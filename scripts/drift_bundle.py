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
                      syllabus entry, problem set, source pointer, PROMPT) — NO answer
    candidates/       you save Gemini output here as <unit>.flash.html / <unit>.pro.html
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

    # 7. generation prompt
    (inbox / "PROMPT.md").write_text(PROMPT_TEMPLATE.format(unit=unit, exemplar=args.exemplar),
                                     encoding="utf-8")

    # manifest
    print(f"Bundle built for {unit} (module {module}) at:\n  {inbox}")
    for n in notes:
        print("  -", n)
    print("\nInbox contents (hand THIS folder to the generator):")
    for p in sorted(inbox.iterdir()):
        print("   ", p.name)
    print("\nNEXT:")
    print("  1. Paste the source sections named in SOURCE-POINTER.md into the inbox.")
    print("  2. Run the inbox + PROMPT.md through Gemini Flash AND Pro.")
    print(f"  3. Save outputs as  {ws / 'candidates'}\\{unit}.flash.html  and  {unit}.pro.html")
    print(f"  4. python scripts/drift_bundle.py {unit} --check")
    print("  5. Bring the surviving candidates to Claude to score vs the reference.")
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
        sys.exit(f"no candidates at {ws / 'candidates'}\\{unit}*.html -- generate them first")
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
        lint_results = lesson_lint.lint(html)
        lfails = [(nm, d) for nm, ok, d in lint_results if not ok]
        failed = (cov.startswith(("FAIL", "ERROR")) or not source_gap_ok
                  or parse.startswith("FAIL") or selfc.startswith("FAIL") or bool(lfails))
        any_fail = any_fail or failed
        print(f"\n{c.name}  [{'BOUNCE' if failed else 'ready to score'}]")
        print(f"  coverage        : {cov}")
        if unchecked:
            print(f"  source gap      : {source_gap}")
        print(f"  html parses     : {parse}")
        print(f"  self-contained  : {selfc}")
        if lfails:
            for nm, d in lfails:
                print(f"  {nm} : FAIL{(': ' + d) if d else ''}")
        else:
            print(f"  render+structure: PASS ({len(lint_results)} checks)")
    print("\n" + ("Some candidates failed the free gate — fix/regenerate before scoring."
                  if any_fail else "All candidates passed the free gate — bring them to Claude to score."))
    sys.exit(1 if any_fail else 0)


PROMPT_TEMPLATE = """You are writing one self-contained HTML lesson for a mathematics self-study
system. Follow LESSON-GUIDE.md exactly — every item in its Structure list is
non-negotiable and in order. You will be graded against LESSON-RUBRIC.md; a single
mathematical error fails the lesson outright, so verify every statement and proof
against the attached source text and cite book + section + page in the footer.
Match the depth, register (British English), and scaffolding of the attached
exemplar lesson (exemplar-{exemplar}.html), which is on DIFFERENT content — do not
copy its mathematics. Fill _template.html. Demonstrate every technique the attached
problem set uses, and ensure every theorem/definition it names appears in your
lesson. Output only the complete HTML file for unit {unit}.

Attached: LESSON-GUIDE.md, LESSON-RUBRIC.md, _template.html, exemplar-{exemplar}.html,
{unit}.syllabus.yaml, {unit}.problems.md, and the source sections from SOURCE-POINTER.md.
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
