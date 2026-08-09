"""drift_bundle.py — assemble an ISOLATED drift-test bundle for a lesson unit.

The drift test is offline QA, not a college action. This tool keeps it entirely
outside the runtime: nothing is written inside the repo, the real lesson is never
moved (so the slash commands never see it "missing"), and the held-out reference
is read straight from git (so scoring compares against the canonical committed
lesson, not a working-tree edit). See docs/lesson-generation-handoff.md.

  python scripts/drift_bundle.py <unit>                 # build the bundle + pull the reference
  python scripts/drift_bundle.py <unit> --exemplar an-05
  python scripts/drift_bundle.py <unit> --check         # free pre-filter on the candidates

Layout (default workspace is a SIBLING of the repo, <repo>-drift/, never inside it):

  <repo>-drift/
    inbox/<unit>/     generator inputs  (LESSON-GUIDE, RUBRIC, template, exemplar,
                      syllabus entry, problem set, SOURCE-EXTRACT, PROMPT) — NO answer
    candidates/       each generator writes <unit>.candidate.html here; RENAME between
                      runs (<unit>.m1.html, ...) or the next one overwrites it. --check
                      globs <unit>*.html, so any suffix works.
    reference/        the held-out gold, pulled from git (scorer's eyes only)
    scorecards/       rubric verdicts
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

for _stream in (sys.stdout, sys.stderr):  # UTF-8 console I/O, cp1252-safe (cf. srs/scheduler.py)
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lesson_lint  # noqa: E402  — sibling script: render-fidelity + structure lint

SPEC_FILES = [  # copied from the working tree: the current standard under test
    ("curriculum/LESSON-GUIDE.md", "LESSON-GUIDE.md"),
    ("curriculum/LESSON-RUBRIC.md", "LESSON-RUBRIC.md"),
    ("lessons/_template.html", "_template.html"),
]
EXTERNAL_REQUEST = re.compile(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//""", re.I)


def repo_root():
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def git_show_bytes(repo, ref_path):
    """Return the exact committed bytes of ref_path (e.g. 'main:lessons/aa/aa-01.html'),
    or None if it does not exist. Byte-faithful — never decodes/re-encodes."""
    r = subprocess.run(["git", "-C", str(repo), "show", ref_path], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def load_units(repo):
    with open(repo / "curriculum/syllabus.yaml", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    return doc, {u["id"]: u for u in doc.get("units", [])}, \
        {m["id"]: m for m in doc.get("modules", [])}


def resolve_source(resources, bookmap):
    """Map each resource string to its book (longest-prefix in bookmap) or mark it
    a non-book source. Returns [(resource, key_or_None, entry_or_None, section)]."""
    keys = sorted(bookmap, key=len, reverse=True)
    out = []
    for res in resources:
        hit = next((k for k in keys if res.startswith(k)), None)
        section = res[len(hit):].strip() if hit else ""
        out.append((res, hit, bookmap.get(hit), section))
    return out


def workspace_for(args, repo):
    if args.workspace:
        return Path(args.workspace)
    return repo.parent / (repo.name + "-drift")


# ----------------------------------------------------------------- build

def build(args):
    repo = repo_root()
    _, units, mods = load_units(repo)
    unit = args.unit
    if unit not in units:
        sys.exit(f"ERROR: unit {unit!r} not in syllabus.yaml")
    if args.exemplar == unit:
        sys.exit("ERROR: exemplar must differ from the target unit (would leak the answer)")
    if args.exemplar not in units:
        sys.exit(f"ERROR: exemplar {args.exemplar!r} not in syllabus.yaml")

    module = units[unit]["module"]
    ex_module = units[args.exemplar]["module"]
    ws = workspace_for(args, repo)
    inbox = ws / "inbox" / unit
    for d in (inbox, ws / "candidates", ws / "reference", ws / "scorecards"):
        d.mkdir(parents=True, exist_ok=True)

    notes = []

    # 1. held-out reference (scorer only) — canonical committed bytes, not working tree
    ref_bytes = git_show_bytes(repo, f"{args.ref}:lessons/{module}/{unit}.html")
    if ref_bytes:
        (ws / "reference" / f"{unit}.reference.html").write_bytes(ref_bytes)
        notes.append(f"reference: pulled lessons/{module}/{unit}.html from {args.ref}")
    else:
        notes.append(f"reference: NONE committed on {args.ref} — score absolute vs the rubric "
                     f"(no head-to-head delta for this unit)")

    # 2. exemplar (few-shot gold, DIFFERENT content) — canonical committed bytes
    ex_bytes = git_show_bytes(repo, f"{args.ref}:lessons/{ex_module}/{args.exemplar}.html")
    if ex_bytes:
        (inbox / f"exemplar-{args.exemplar}.html").write_bytes(ex_bytes)
    else:
        sys.exit(f"ERROR: exemplar lessons/{ex_module}/{args.exemplar}.html not committed on {args.ref}")

    # 3. spec files (current standard under test) — from the working tree
    for src, dst in SPEC_FILES:
        p = repo / src
        if p.exists():
            shutil.copy(p, inbox / dst)
        else:
            notes.append(f"MISSING spec file: {src}")

    # 4. the unit's syllabus entry + its module block
    (inbox / f"{unit}.syllabus.yaml").write_text(
        yaml.safe_dump({"module": mods.get(module), "unit": units[unit]},
                       sort_keys=False, allow_unicode=True), encoding="utf-8")

    # 5. problem set (drives the coverage gate) — copy if present
    pset = repo / "problems/sets" / f"{unit}.md"
    if pset.exists():
        shutil.copy(pset, inbox / f"{unit}.problems.md")
    else:
        notes.append(f"problem set problems/sets/{unit}.md ABSENT — per the handoff, "
                     f"generate the problem set FIRST, then the lesson")

    # 6. source pointer (resolve resources; do not slice — point precisely)
    bookmap = {}
    bm = repo / "resources/bookmap.json"
    if bm.exists():
        import json
        bookmap = json.loads(bm.read_text(encoding="utf-8"))
    src_lines = ["# Source text — paste the named sections into the bundle before generating\n",
                 f"Unit **{unit}** cites these resources. Book sections are NOT auto-sliced "
                 "(section formats differ per book); grab each from the path below.\n"]
    for res, key, entry, section in resolve_source(units[unit].get("resources", []), bookmap):
        if entry:
            src_lines.append(f"\n## {res}\n- book: {entry.get('title', key)}\n"
                             f"- section to extract: **{section or '(whole)'}**\n"
                             f"- markdown: `{entry.get('md','')}`\n"
                             f"- per-page: `{entry.get('pages','')}`")
        else:
            src_lines.append(f"\n## {res}\n- non-book source (see resources/RESOURCES.md); "
                             "paste the relevant notes/docs.")
    (inbox / "SOURCE-POINTER.md").write_text("\n".join(src_lines) + "\n", encoding="utf-8")

    # 7. generation prompt. Model-neutral by design: no vendor named, no
    # reasoning directives (they would advantage models with those features and
    # confound a reasoning-effort arm), and a fixed output contract.
    # One canonical candidate path, built with pathlib so the separator is the
    # platform's. It goes into the generator prompt AND the next-step print, so
    # the file the generator is told to write is the file --check globs for.
    candidate_path = ws / "candidates" / f"{unit}.candidate.html"
    (inbox / "PROMPT.md").write_text(
        PROMPT_TEMPLATE.format(unit=unit, exemplar=args.exemplar, inbox=inbox,
                               candidate_path=candidate_path),
        encoding="utf-8")

    # manifest
    print(f"Bundle built for {unit} (module {module}) at:\n  {inbox}")
    for n in notes:
        print("  -", n)
    print("\nInbox contents (hand THIS folder to the generator):")
    for p in sorted(inbox.iterdir()):
        print("   ", p.name)
    print("\nNEXT:")
    print("  1. Extract the sections named in SOURCE-POINTER.md into")
    print(f"     {inbox / 'SOURCE-EXTRACT.md'}  (the one manual step; PROMPT.md reads it as")
    print("     the sole source for this unit's own mathematics).")
    print("  2. Point each generator at the inbox folder and PROMPT.md. Same bytes to")
    print("     every generator, one turn each, no repair prompts.")
    print(f"  3. Each writes {candidate_path} — RENAME IT")
    print("     before the next run, or the next generator overwrites it.")
    print(f"  4. python scripts/drift_bundle.py {unit} --check")
    print("  5. Bring the surviving candidates to Claude to score against the rubric.")
    print("\nDo NOT put reference/ or the working-tree lesson in the generator's input.")


# ----------------------------------------------------------------- check

def _self_contained(html):
    hits = sorted(set(m.group(0) for m in EXTERNAL_REQUEST.finditer(html)))
    return hits


def _parses(html):
    from html.parser import HTMLParser
    try:
        HTMLParser().feed(html)
        return True, ""
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def check(args):
    repo = repo_root()
    ws = workspace_for(args, repo)
    unit = args.unit
    cands = sorted((ws / "candidates").glob(f"{unit}*.html"))
    if not cands:
        sys.exit(f"no candidates at {ws / 'candidates' / (unit + '*.html')} -- generate them first")
    pset = repo / "problems/sets" / f"{unit}.md"
    any_fail = False
    for c in cands:
        html = c.read_text(encoding="utf-8", errors="replace")
        # coverage
        if pset.exists():
            r = subprocess.run([sys.executable, str(repo / "scripts/check_lesson_coverage.py"),
                                str(pset), str(c)], capture_output=True, text=True)
            report = r.stdout.strip()
            cov = report if r.returncode in {0, 1} and report else \
                  ("ERROR " + r.stderr.strip()).strip()
        else:
            cov = "SKIP (no problem set)"
        source_gap_disposition = getattr(args, "source_gap_disposition", None)
        unchecked = cov.startswith("UNCHECKED")
        source_gap_ok = not unchecked or source_gap_disposition == "accept-no-checkable-refs"
        source_gap = source_gap_disposition or "SOURCE GAP UNDISPOSITIONED"
        # parse
        ok, err = _parses(html)
        parse = "PASS" if ok else f"FAIL {err}"
        # self-contained
        ext = _self_contained(html)
        selfc = "PASS" if not ext else f"FAIL external: {', '.join(ext[:3])}"
        # A candidate that declares "NOT IN SOURCE: ..." is being honest about the
        # extract: a datum to read at Gate 2, not a bounce. Committed lessons are
        # linted by the same function and DO fail on a gap — the exemption is this
        # caller's policy, so it drops that one row by name rather than asking
        # lesson_lint to soften.
        lint_results = lesson_lint.lint(html)
        gaps = lesson_lint.gap_markers(html)
        lfails = [(nm, d) for nm, ok, d in lint_results
                  if not ok and nm != lesson_lint.GAP_CHECK]
        # The gap row is a datum, not a check: exclude it from the count too, or a
        # candidate with declared gaps reports one more "render+structure" check
        # than one without.
        structural = [r for r in lint_results if r[0] != lesson_lint.GAP_CHECK]
        failed = (cov.startswith(("FAIL", "ERROR")) or not source_gap_ok
                  or parse.startswith("FAIL") or selfc.startswith("FAIL") or bool(lfails))
        any_fail = any_fail or failed
        print(f"\n{c.name}  [{'BOUNCE' if failed else 'ready to score'}]")
        print(f"  coverage        : {cov}")
        if unchecked:
            print(f"  source gap      : {source_gap}")
        print(f"  html parses     : {parse}")
        print(f"  self-contained  : {selfc}")
        print(f"  declared gaps   : {len(gaps)}"
              + ("  <- read these before scoring" if gaps else
                 "  (none — check this is completeness, not silent invention)"))
        for g in gaps:
            print(f"      NOT IN SOURCE: {g.strip()[:100]}")
        if lfails:
            for nm, d in lfails:
                print(f"  {nm} : FAIL{(': ' + d) if d else ''}")
        else:
            print(f"  render+structure: PASS ({len(structural)} checks)")
    print("\n" + ("Some candidates failed the free gate — fix/regenerate before scoring."
                  if any_fail else "All candidates passed the free gate — bring them to Claude to score."))
    sys.exit(1 if any_fail else 0)


PROMPT_TEMPLATE = """# Generation task

Write one self-contained HTML lesson for a mathematics self-study system.

## Where the inputs are

Read every file in this folder:

```
{inbox}
```

In order of authority:

1. `LESSON-GUIDE.md` — binding. Its **Structure** list is in order and every item
   is required. Its **Register** section defines the voice.
2. `LESSON-RUBRIC.md` — how the output will be scored.
3. `_template.html` — the file skeleton to fill.
4. `SOURCE-EXTRACT.md` — the mathematical source for this unit.
5. `{unit}.syllabus.yaml` — the unit's id, title, prereqs, hook, mission_link and
   pinned sections.
6. `{unit}.problems.md` — the problem set this lesson must prepare the learner for.
7. `exemplar-{exemplar}.html` — a completed lesson on different, easier content.

Ignore `SOURCE-POINTER.md`; it is a build record, not input.

## Where the output goes

Write the finished lesson as a real file at exactly:

```
{candidate_path}
```

One file. Do not print the HTML into the conversation, do not wrap it in a code
fence, and do not create, move or modify any other file anywhere.

## What the exemplar is and is not

The exemplar shows **format, markup conventions, register and scaffolding
technique**. It is on much easier material than your target unit. Do **not**
calibrate mathematical depth to it, and do not reuse its mathematics. Depth is
set by `SOURCE-EXTRACT.md` and by the sections named in the syllabus entry.

## Source discipline (this is graded)

`SOURCE-EXTRACT.md` is the sole source for **this unit's own mathematics** — the
definitions, theorems and proofs of the sections it pins. Do not restate those
from recollection of the textbook, and do not consult anything outside this
folder. Every definition, theorem statement and proof of the unit's material must
be traceable to the extract, cited by book, section and page in the footer.

**Prerequisite results are a different matter and you should use them freely.**
The learner has already completed the earlier units of this curriculum, so
standard facts they have met — the homology of a connected space, of spheres,
surfaces and projective spaces, cellular and singular homology, the universal
coefficient theorem, ordinary linear algebra — are available even when the
extract does not restate them. Use them, and attribute them to the earlier unit
rather than to the extract. The extract is a boundary on **what this unit
teaches**, not on what the learner already knows.

If something the lesson genuinely needs is missing — a result of *this unit's*
material that the extract does not contain, and that is not prerequisite
knowledge — do not supply it from memory and do not quietly work around it.
State it in place, in this exact form, and carry on:

```html
<p class="gap">NOT IN SOURCE: the proof that the cover is good</p>
```

A lesson with an honest gap marker scores better than one with an unsupported
claim. Do not use the marker for a prerequisite you could simply state, and do
not invent a theorem number or a page citation for a result you are supplying
yourself: if you need an auxiliary lemma, give it your own name, prove it, and
say which cited result it follows from. Hypotheses matter — state them where the
source states them.

## Output contract

- Exactly one HTML document in the file named above.
- First characters `<!DOCTYPE html>`, last characters `</html>`.
- Fully self-contained: no external requests of any kind — no CDN, no remote
  fonts, stylesheets, images or scripts. All CSS and JS inline.
- Use literal Unicode characters for mathematics (ℤ, ℝ, ⊗, ≅, ∂, ε). Do **not**
  invent HTML entities: only the five standard named entities
  (`&amp; &lt; &gt; &quot; &apos;`) and numeric entities are valid. Anything like
  `&mathbb;`, `&left;`, `&dots;` renders as literal text and fails admission.
- Label self-checks literally as `Self-check 1`, `Self-check 2`, … so they can be
  counted.

## Constraints on process

Work at whatever internal depth you need; nothing about your reasoning is being
measured and no reasoning trace should appear in the file. Only the delivered
HTML is scored.

Target unit: **{unit}**.
"""


def main():
    ap = argparse.ArgumentParser(description="Assemble an isolated drift-test bundle for a unit.")
    ap.add_argument("unit", help="target unit id, e.g. aa-01")
    ap.add_argument("--exemplar", default="an-03", help="few-shot exemplar unit (different content; default an-03)")
    ap.add_argument("--ref", default="main", help="git ref for the held-out reference & exemplar (default main)")
    ap.add_argument("--workspace", default=None, help="override workspace dir (default <repo>-drift/)")
    ap.add_argument("--check", action="store_true", help="run the free pre-filter on candidates instead of building")
    ap.add_argument(
        "--source-gap-disposition",
        choices=("accept-no-checkable-refs", "block-for-source-repair"),
        help="required decision when coverage reports UNCHECKED",
    )
    args = ap.parse_args()
    (check if args.check else build)(args)


if __name__ == "__main__":
    main()
