# Nexus College Phase 1 — Teaching Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the college teachable: `/today`, `/lecture`, `/status` commands, the lesson template + pedagogy guide, resource-path resolution, a visual dashboard, and the first 8 interactive lessons (weeks 1–2 of Semester 1).

**Architecture:** Skills are markdown instruction files in `.claude/skills/` that read/write the Phase 0 data files (`curriculum/syllabus.yaml`, `state/*.json`). Lessons are self-contained HTML generated once and reused. The only new Python is `scripts/build_dashboard.py`. Resource strings resolve through `resources/bookmap.json`.

**Tech Stack:** Python 3.11 (pyyaml, pytest, stdlib html), vanilla HTML/CSS/JS lessons (no build step), Claude Code skills (markdown).

## Global Constraints

- Repo root: `C:\Users\steph\MathUni`, branch `main`. Verify cwd before every write/commit.
- Commits: `git commit -F <tempfile>` (scratchpad tempfile), never here-strings; trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Spec: `docs/specs/2026-07-03-nexus-college-design.md`; handover: `docs/phase1-notes.md`.
- Progress status enum (full, from spec §4): `locked | unlocked | in-progress | mastered`. Phase 1 skills may set `in-progress`; `mastered` is Phase 2's (`/grade`).
- State writes are atomic (write `.tmp`, `os.replace`) and continuous — never only at session end.
- Lesson files: `lessons/<module>/<unit>.html`, self-contained (inline CSS/JS, no external requests), open the hook FIRST — never "Definition 1.1" first.
- Citations cite book + section + PDF page, resolvable via `resources/bookmap.json`.
- Timeboxes: lessons are structured as 2–3 segments of 25–30 min each, visibly labeled.
- Core Texts folder: `D:\OneDrive - The Open University\NexusCollege Core Texts\` (`md\<book-folder>\markdown.md` preferred; `pages\` for page-precise citation; `pdf\` fallback).
- No Obsidian. Test output pristine.

---

### Task 1: Resource resolution — bookmap.json

**Files:**
- Create: `resources/bookmap.json`
- Modify: `resources/RESOURCES.md` (append resolution-rule section)

**Interfaces:**
- Produces: `resources/bookmap.json` — object keyed by **slug** (the first word(s) of a `resources` string in syllabus.yaml, e.g. `"Axler"`, `"Abbott"`, `"Cummings"`, `"Carter"`, `"Aluffi Underground"`). Each value: `{"title": str, "md": str (absolute path to markdown.md), "pages": str (absolute path to pages dir), "pdf": str (absolute path)}`. Later tasks and `/lecture` look up: longest slug that prefixes the resource string wins; remainder (e.g. `"1A-1B"`) is the section reference.

- [ ] **Step 1: Inventory the Core Texts folder**

Run: `ls "/d/OneDrive - The Open University/NexusCollege Core Texts/md"` and same for `pdf`. Every book folder found gets a bookmap entry; the five below are REQUIRED (fail the task if missing).

- [ ] **Step 2: Write `resources/bookmap.json`**

Required entries (verify exact folder names against the ls output — the Aluffi folder name contains a space before `.pdf`):

```json
{
  "Axler": {
    "title": "Linear Algebra Done Right (Axler)",
    "md": "D:\\OneDrive - The Open University\\NexusCollege Core Texts\\md\\Linear Algebra Done Right (Undergraduate Texts in Mathematics) (Axler, Sheldon) (z-lib.org).pdf\\markdown.md",
    "pages": "D:\\OneDrive - The Open University\\NexusCollege Core Texts\\md\\Linear Algebra Done Right (Undergraduate Texts in Mathematics) (Axler, Sheldon) (z-lib.org).pdf\\pages",
    "pdf": "D:\\OneDrive - The Open University\\NexusCollege Core Texts\\pdf\\Linear Algebra Done Right (Undergraduate Texts in Mathematics) (Axler, Sheldon) (z-lib.org).pdf"
  },
  "Abbott": { "title": "Understanding Analysis (Abbott)", "md": "...same pattern...", "pages": "...", "pdf": "..." },
  "Cummings": { "title": "Proofs (Cummings)", "md": "...", "pages": "...", "pdf": "..." },
  "Carter": { "title": "Visual Group Theory (Carter)", "md": "...", "pages": "...", "pdf": "..." },
  "Aluffi Underground": { "title": "Algebra: Notes from the Underground (Aluffi)", "md": "...", "pages": "...", "pdf": "..." }
}
```

("...same pattern..." = fill with the real absolute paths from Step 1's output — no literal ellipses may remain in the committed file.) Add entries for any other book folders present (e.g. Cummings Real Analysis, Munkres, Hatcher) using the same slug convention (surname, or surname + distinguishing word). Validate with `python -c "import json; d=json.load(open('resources/bookmap.json')); import os; missing=[k for k,v in d.items() if not os.path.exists(v['md'])]; print('missing md:', missing); assert not missing"`.

- [ ] **Step 3: Append the resolution rule to `resources/RESOURCES.md`**

```markdown
## Resource resolution rule (Phase 1)

`syllabus.yaml` resource strings resolve via `bookmap.json`: the longest slug
that is a prefix of the string names the book; the remainder is the section
reference (e.g. "Axler 1A-1B" → bookmap["Axler"], sections 1A-1B). Non-book
resources (video playlists, folder names like "Oxford M1 Groups") are not in
bookmap and resolve via the tables above. Lesson generators quote from `md`,
cite pages via `pages\` filenames, and fall back to `pdf` on conversion damage.
```

- [ ] **Step 4: Commit** — `feat: bookmap resource resolution (phase1-notes item 1)`

---

### Task 2: Dashboard generator (TDD)

**Files:**
- Create: `scripts/build_dashboard.py`
- Test: `tests/test_build_dashboard.py`
- Generates: `dashboard/index.html` (committed)

**Interfaces:**
- Consumes: `load_syllabus(path)` from `scripts/validate_syllabus.py`; `state/progress.json`, `state/streaks.json`.
- Produces: `render(syllabus: dict, progress: dict, streaks: dict) -> str` (full HTML document) and CLI `python scripts/build_dashboard.py` writing `dashboard/index.html` atomically. `/status` runs this CLI.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_build_dashboard.py
from scripts.build_dashboard import render

SYL = {"semesters": [{"id": "s1", "title": "T"}],
       "modules": [{"id": "la", "title": "Linear Algebra", "semester": "s1"}],
       "units": [
           {"id": "la-01", "module": "la", "title": "Vector spaces", "prereqs": [],
            "resources": [], "hook": "h", "mission_link": "m"},
           {"id": "la-02", "module": "la", "title": "Subspaces", "prereqs": ["la-01"],
            "resources": [], "hook": "h", "mission_link": "m"}]}
PROG = {"la-01": {"status": "in-progress"}, "la-02": {"status": "locked"}}
STREAKS = {"current": 3, "best": 5, "study_days": ["2026-07-06"]}

def test_render_returns_html_document():
    html = render(SYL, PROG, STREAKS)
    assert html.startswith("<!DOCTYPE html>") and "</html>" in html

def test_units_appear_in_status_columns():
    html = render(SYL, PROG, STREAKS)
    assert "Vector spaces" in html and "Subspaces" in html
    assert 'data-status="in-progress"' in html and 'data-status="locked"' in html

def test_streak_and_module_progress_shown():
    html = render(SYL, PROG, STREAKS)
    assert "3" in html and "Linear Algebra" in html
    assert "0/2" in html  # mastered count / total for module la

def test_unknown_unit_status_defaults_locked():
    html = render(SYL, {}, STREAKS)
    assert html.count('data-status="locked"') == 2
```

- [ ] **Step 2: Run to verify FAIL** — `python -m pytest tests/test_build_dashboard.py -v` → import error.

- [ ] **Step 3: Implement `scripts/build_dashboard.py`**

```python
"""Render dashboard/index.html: kanban by status, module progress, streaks.
Pure stdlib + repo data; /status runs this CLI."""
import json
import os
import sys
from html import escape

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.validate_syllabus import load_syllabus

COLUMNS = ["unlocked", "in-progress", "mastered", "locked"]
LABELS = {"unlocked": "Unlocked", "in-progress": "In progress",
          "mastered": "Mastered", "locked": "Locked"}

CSS = """body{font-family:Segoe UI,system-ui,sans-serif;background:#101418;color:#e8e8e8;margin:2rem}
h1{font-weight:600}.streak{font-size:1.1rem;margin-bottom:1.5rem}
.board{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.col{background:#1a2027;border-radius:10px;padding:.8rem}.col h2{font-size:.95rem;text-transform:uppercase;letter-spacing:.05em;color:#8ab4f8}
.card{background:#232b34;border-radius:8px;padding:.6rem .8rem;margin:.5rem 0;font-size:.9rem}
.card small{color:#9aa5b1;display:block}
.mods{margin-top:2rem}.bar{background:#232b34;border-radius:6px;height:14px;overflow:hidden;margin:.3rem 0 1rem}
.fill{background:#4caf82;height:100%}"""


def render(syllabus, progress, streaks):
    units = syllabus.get("units", [])
    mods = {m["id"]: m for m in syllabus.get("modules", [])}
    status = {u["id"]: progress.get(u["id"], {}).get("status", "locked") for u in units}
    cols = []
    for c in COLUMNS:
        cards = "".join(
            f'<div class="card" data-status="{c}"><b>{escape(u["title"])}</b>'
            f'<small>{u["id"]} · {escape(mods.get(u["module"], {}).get("title", u["module"]))}</small></div>'
            for u in units if status[u["id"]] == c)
        cols.append(f'<div class="col"><h2>{LABELS[c]} ({sum(1 for u in units if status[u["id"]]==c)})</h2>{cards}</div>')
    modbars = []
    for mid, m in mods.items():
        mu = [u for u in units if u["module"] == mid]
        if not mu:
            continue
        done = sum(1 for u in mu if status[u["id"]] == "mastered")
        pct = int(100 * done / len(mu))
        modbars.append(f'<div><b>{escape(m["title"])}</b> {done}/{len(mu)}'
                       f'<div class="bar"><div class="fill" style="width:{pct}%"></div></div></div>')
    return ("<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>Nexus College</title>"
            f"<style>{CSS}</style></head><body><h1>Nexus College</h1>"
            f'<div class="streak">🔥 Streak: {streaks.get("current", 0)} (best {streaks.get("best", 0)}) · '
            f'{len(streaks.get("study_days", []))} study days total</div>'
            f'<div class="board">{"".join(cols)}</div>'
            f'<div class="mods"><h2>Module progress (mastered)</h2>{"".join(modbars)}</div>'
            "</body></html>")


def main():
    syllabus = load_syllabus("curriculum/syllabus.yaml")
    with open("state/progress.json", encoding="utf-8") as f:
        progress = json.load(f)
    with open("state/streaks.json", encoding="utf-8") as f:
        streaks = json.load(f)
    os.makedirs("dashboard", exist_ok=True)
    tmp = "dashboard/index.html.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(render(syllabus, progress, streaks))
    os.replace(tmp, "dashboard/index.html")
    print("dashboard/index.html written")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests (expect 4 pass, suite total 15), then run CLI** — `python scripts/build_dashboard.py` → `dashboard/index.html written`; open count: 4 unlocked / 42 locked.

- [ ] **Step 5: Commit** — `feat: dashboard generator (kanban, streaks, module bars)` including `dashboard/index.html`.

---

### Task 3: Lesson template + pedagogy guide

**Files:**
- Create: `lessons/_template.html`, `curriculum/LESSON-GUIDE.md`

**Interfaces:**
- Produces: the template every lesson task copies, and the guide that binds lesson generators. Placeholder tokens in template: `{{UNIT_ID}} {{TITLE}} {{MODULE_TITLE}} {{HOOK_HEADLINE}} {{MISSION_LINK}} {{SEGMENTS}} {{CITATIONS}}`.

- [ ] **Step 1: Write `lessons/_template.html`**

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{UNIT_ID}} — {{TITLE}}</title>
<style>
:root{--bg:#101418;--panel:#1a2027;--ink:#e8e8e8;--dim:#9aa5b1;--acc:#8ab4f8;--good:#4caf82;--bad:#e06c75}
body{font-family:Georgia,serif;background:var(--bg);color:var(--ink);max-width:46rem;margin:2rem auto;padding:0 1.2rem;line-height:1.65;font-size:1.05rem}
h1,h2,h3{font-family:Segoe UI,system-ui,sans-serif}
.hook{background:linear-gradient(135deg,#1a2340,#1a2027);border-left:4px solid var(--acc);padding:1.2rem;border-radius:10px;font-size:1.15rem;margin:1.4rem 0}
.mission{color:var(--dim);font-style:italic;border-top:1px solid #2a333d;border-bottom:1px solid #2a333d;padding:.6rem 0;margin:1rem 0}
.segment{margin:2.2rem 0}.timebox{display:inline-block;background:#26313c;color:var(--acc);border-radius:999px;padding:.15rem .8rem;font-size:.8rem;font-family:Segoe UI,sans-serif}
.theorem,.definition{background:var(--panel);border-radius:10px;padding:1rem 1.2rem;margin:1.2rem 0}
.definition{border-left:4px solid var(--good)}.theorem{border-left:4px solid var(--acc)}
.worked{background:#151b21;border:1px dashed #2a333d;border-radius:10px;padding:1rem 1.2rem;margin:1.2rem 0}
.fade{opacity:.92}.you-try{border-left:4px solid #d8a657;background:#1d1c16;border-radius:10px;padding:1rem 1.2rem;margin:1.2rem 0}
canvas{display:block;margin:1rem auto;background:#0c1013;border-radius:10px}
.selfcheck{background:var(--panel);border-radius:10px;padding:1rem 1.2rem;margin:1.6rem 0}
.selfcheck button{background:#26313c;color:var(--ink);border:1px solid #2a333d;border-radius:8px;padding:.45rem .9rem;margin:.25rem;cursor:pointer;font-size:.95rem}
.selfcheck button.correct{background:var(--good);color:#08130d}.selfcheck button.wrong{background:var(--bad);color:#1b0c0e}
.explain{display:none;color:var(--dim);margin-top:.6rem}.selfcheck.answered .explain{display:block}
.cite{color:var(--dim);font-size:.85rem}footer{margin:3rem 0 2rem;color:var(--dim);font-size:.9rem;border-top:1px solid #2a333d;padding-top:1rem}
.break{background:#14231b;border-radius:10px;text-align:center;padding:.8rem;margin:2rem 0;color:var(--good)}
</style></head><body>
<p class="cite">{{MODULE_TITLE}} · Nexus College</p>
<h1>{{TITLE}} <span class="cite">({{UNIT_ID}})</span></h1>
<div class="hook">{{HOOK_HEADLINE}}</div>
<p class="mission">Why this matters for the mission: {{MISSION_LINK}}</p>
{{SEGMENTS}}
<footer>Sources: {{CITATIONS}}</footer>
<script>
function check(btn,ok){const sc=btn.closest('.selfcheck');if(sc.classList.contains('answered'))return;
btn.classList.add(ok?'correct':'wrong');if(!ok){const c=sc.querySelector('button[data-ok]');if(c)c.classList.add('correct');}
sc.classList.add('answered');
try{const done=document.querySelectorAll('.selfcheck.answered').length,total=document.querySelectorAll('.selfcheck').length;
localStorage.setItem('nexus-'+document.title,JSON.stringify({done:done,total:total,ts:Date.now()}));}catch(e){}}
</script></body></html>
```

- [ ] **Step 2: Write `curriculum/LESSON-GUIDE.md`**

```markdown
# Lesson Generation Guide (binding for every lesson)

A lesson serves ONE unit of syllabus.yaml and is a single self-contained
HTML file at `lessons/<module>/<unit>.html`, built from `lessons/_template.html`.

## Structure (in order, non-negotiable)
1. **Hook first.** `{{HOOK_HEADLINE}}` expands the unit's `hook` into 2-4
   sentences with a concrete, fun instance. Never open with a definition.
2. **Mission strip** — the unit's `mission_link`, one sentence.
3. **2–3 segments**, each wrapped in `<div class="segment">` opening with
   `<span class="timebox">Segment N · ~25 min</span>` and a title. Between
   segments insert `<div class="break">☕ Break — stand up, 5 minutes.</div>`.
4. **Faded worked examples** within segments: first example fully worked
   (`.worked`), second partially completed (`.worked.fade`, gaps marked
   "⟨your step⟩"), then a `.you-try` block the learner does solo.
5. **Self-checks**: 2–3 per segment (`.selfcheck` with 3-4 answer buttons,
   `onclick="check(this,true|false)"`, `data-ok` on the correct one, plus a
   `.explain` div giving WHY). Instant feedback, no page reload.
6. **Visual element**: at least one per lesson — a `<canvas>` with a short
   inline JS animation/diagram (≤60 lines) OR an inline SVG diagram where
   animation adds nothing. Geometry over decoration.
7. **Footer citations**: every definition/theorem cites book + section +
   PDF page(s), e.g. `Axler §1A, pp. 2–5`. Resolve paths via
   resources/bookmap.json; verify quotes against the book's markdown.md.

## Register
- Definitions verbatim-faithful to the primary text (cite); narration in
  your own voice: vivid, precise, never breathless. Aluffi/Stillwell is the
  style bar. British English.
- Content depth = the primary text's sections named in the unit's
  `resources`, scoped to ONE lecture-equivalent (the DAG's next units take
  the rest). State explicitly what is deferred and to which unit.
- MathML or Unicode maths (no external LaTeX/JS libraries; file must render
  offline).

## Checklist before committing a lesson
hook-first ✓ · mission strip ✓ · 2-3 timeboxed segments ✓ · break card ✓ ·
faded examples ✓ · ≥4 self-checks with explanations ✓ · visual ✓ ·
citations with pages ✓ · self-contained (zero external requests) ✓ ·
`python -c "from html.parser import HTMLParser; HTMLParser().feed(open(PATH,encoding='utf-8').read())"` runs clean ✓
```

- [ ] **Step 3: Commit** — `feat: lesson template and binding pedagogy guide`

---

### Task 4: The /today, /lecture, /status skills

**Files:**
- Create: `.claude/skills/today/SKILL.md`, `.claude/skills/lecture/SKILL.md`, `.claude/skills/status/SKILL.md`

**Interfaces:**
- Consumes: bookmap (T1), dashboard CLI (T2), LESSON-GUIDE + template (T3), Phase 0 state/curriculum files.
- Produces: the user-facing commands. Session logs: `state/sessions/YYYY-MM-DD.md` (append-only). Handoff: `state/SESSION-HANDOFF.md` (overwrite).

- [ ] **Step 1: Write `.claude/skills/today/SKILL.md`**

```markdown
---
name: today
description: Assemble and run today's study day — warm-up, two lectures, problem segment. Use when Stephen says /today, "start today", or "what's on today".
---

# /today — run a study day

Work from the repo root (verify cwd = MathUni). All state writes atomic
(temp file + os.replace via python -c, or write-then-move).

1. **Load state**: state/progress.json, state/streaks.json,
   state/SESSION-HANDOFF.md, curriculum/syllabus.yaml.
2. **Resume check**: if SESSION-HANDOFF.md shows an unfinished day for
   today's date, resume it at the recorded step instead of building a new day.
3. **Build the day** (write plan to state/sessions/YYYY-MM-DD.md before
   starting):
   - Warm-up (~10 min): 3-5 quick recall questions from `in-progress`/
     recently touched units (improvise from lesson self-check topics until
     the Phase 2 SRS exists — note "SRS pending Phase 2" in the log).
   - Lecture 1 and Lecture 2: pick two units, DIFFERENT modules, status
     `unlocked` first, else `in-progress`. Respect DAG order. Offer Stephen
     the choice when >2 candidates (ADHD: choice within structure).
   - Problem segment (~25 min): 2-3 problems from the current units'
     primary-text exercises (resolve via resources/bookmap.json), worked
     interactively with the hint ladder: nudge → strategy → partial → worked.
4. **Run each lecture** by following .claude/skills/lecture/SKILL.md for
   that unit (including its state updates).
5. **Log continuously**: append each completed step to the day's session
   file THE MOMENT it finishes; update SESSION-HANDOFF.md (today's date,
   day plan, current step) so a dead session resumes losslessly.
6. **Close the day**: update streaks.json (append today to study_days once,
   recompute current/best on consecutive study-date logic — dates on the
   4-day/week schedule count as consecutive if within 3 days); run
   `python scripts/build_dashboard.py`; give a 3-line summary + one
   genuinely interesting teaser for next session (hook of the next unlocked
   unit).

Tone: engaging, hook-led, never guilt. Timebox: announce segment starts/ends;
suggest the break card's 5-minute break between lectures.
```

- [ ] **Step 2: Write `.claude/skills/lecture/SKILL.md`**

```markdown
---
name: lecture
description: Open or generate the interactive lesson for a syllabus unit. Use for /lecture <unit-id>, "teach me <topic>", or when /today reaches a lecture slot.
---

# /lecture <unit-id> — deliver one lesson

1. **Resolve the unit** in curriculum/syllabus.yaml (fuzzy-match titles if
   given a topic, confirm with Stephen). Check prereqs in
   state/progress.json: if any prereq is `locked`/`unlocked` (i.e. not yet
   studied), warn and offer it instead — never hard-block (ADHD: gentle).
4. **Serve or generate**:
   - If lessons/<module>/<unit>.html exists: open it
     (`start lessons\<module>\<unit>.html` via cmd) and run the live layer.
   - If missing: generate it FIRST, following curriculum/LESSON-GUIDE.md
     exactly (template lessons/_template.html; sources via
     resources/bookmap.json — read the md, cite pages), commit it, then open.
5. **Live layer** (the part a file can't do): after Stephen reads each
   segment, ask one Socratic question about it; answer questions with
   citations into the source; at lesson end pose the unit's "minute paper" —
   one-sentence summary in Stephen's own words + muddiest point. Record both
   in learning-records/<unit>.md (create; append if exists).
6. **State updates** (atomic): set unit status `unlocked` → `in-progress` in
   state/progress.json when the lesson opens. Append to today's session log.
7. **Never** mark `mastered` — that is /grade (Phase 2).

Model note: generation quality gate — if generating, the lesson must pass
the LESSON-GUIDE checklist before commit; run its html.parser check.
```

- [ ] **Step 3: Write `.claude/skills/status/SKILL.md`**

```markdown
---
name: status
description: Refresh and show the visual dashboard — kanban, streaks, module progress, what's unlocked. Use for /status, "where am I", "show progress".
---

# /status — the college noticeboard

1. Run `python scripts/build_dashboard.py` (repo root; verify cwd).
2. Open dashboard/index.html (`start dashboard\index.html`).
3. Say, in ≤6 lines: current streak; units in-progress; units newly
   unlocked (with their hooks — sell them); next mastery gates ahead
   (Phase 2 note if grading not yet built); one-line encouragement tied to
   actual data (never generic, never guilt).
4. If any unit has sat `in-progress` >7 days, gently offer a 15-minute
   "close it out" mini-session as an option, not an obligation.
```

- [ ] **Step 4: Sanity-check frontmatter** — each SKILL.md has `name` + `description`; names don't collide with global skills.

- [ ] **Step 5: Commit** — `feat: today/lecture/status skills (teaching loop)`

---

### Task 5: Exemplar lesson — pw-01

**Files:**
- Create: `lessons/pw/pw-01.html`

**Interfaces:**
- Consumes: template + guide (T3), bookmap (T1). Syllabus unit pw-01: "Direct proof, contrapositive, contradiction", resources Cummings ch. 4-6, hook "Three ways to corner a truth — and how mathematicians pick locks.", mission_link "Every TDA paper you'll verify is built from these moves."
- Produces: the quality bar all later lessons are reviewed against.

- [ ] **Step 1: Read the source** — bookmap "Cummings" → markdown.md, chapters 4–6 (direct proof, contrapositive, contradiction). Extract: chapter framing, 2 worked proofs per technique, the definitions/statements to cite, PDF page numbers via `pages\`.
- [ ] **Step 2: Author `lessons/pw/pw-01.html`** per LESSON-GUIDE: Segment 1 direct proof (hook expansion: lock-picking metaphor — three different attacks on "n² even ⇒ n even"); Segment 2 contrapositive + contradiction (include √2 irrationality as the show-piece, faded); you-try: one short proof solo. Visual: inline SVG "three doors to the same room" diagram of the three proof shapes (implication arrows). ≥4 self-checks (e.g. "which technique does this proof skeleton use?").
- [ ] **Step 3: Validate** — html.parser check clean; LESSON-GUIDE checklist all ✓; no external URLs (`grep -E 'https?://' allowed only inside citations as plain text, no <script src>/<link href>`).
- [ ] **Step 4: Commit** — `feat: lesson pw-01 (exemplar)`

---

### Task 6: Lessons la-01, la-02 (Axler)

**Files:** Create `lessons/la/la-01.html`, `lessons/la/la-02.html`

Same procedure as Task 5. Sources: bookmap "Axler". la-01 "Vector spaces" (Axler 1A-1B; hook: "Polynomials, sequences, and functions are all secretly the same thing."): Segment 1 = ℝⁿ/ℂⁿ and the field axioms lightly (1A), Segment 2 = vector space definition + the zoo of examples incl. function spaces (1B), canvas visual: vector addition/scaling in the plane. Defer subspaces to la-02 explicitly. la-02 "Subspaces, sums, direct sums" (Axler 1C; hook: plane-plus-line jigsaw): Segment 1 subspace test + examples/counterexamples, Segment 2 sums and direct sums with the jigsaw metaphor; visual: canvas showing a plane and line through origin summing to ℝ³ (rotating wireframe or layered 2D projection). Each lesson: guide checklist + parser check + commit separately (`feat: lesson la-01`, `feat: lesson la-02`).

### Task 7: Lessons an-01, an-02, pw-02 (Abbott + Cummings)

**Files:** Create `lessons/an/an-01.html`, `lessons/an/an-02.html`, `lessons/pw/pw-02.html`

Sources: bookmap "Abbott" (an), "Cummings" (pw). an-01 "Reals, completeness, sup and inf" (Abbott 1.1-1.4; hook: √2 punches a hole in ℚ): Segment 1 = the √2 wound + ℚ's inadequacy (1.1), Segment 2 = axiom of completeness, sup/inf with worked sup computations (1.3-1.4, cardinality deferred to an-02); visual: number-line canvas animating nested rational approximations closing on √2. an-02 "Cardinality and Cantor's diagonal" (Abbott 1.5-1.6; hook: some infinities are bigger): Segment 1 = 1-1 correspondence, countability of ℚ (1.5), Segment 2 = diagonal argument as a game (1.6); visual: SVG diagonal-array walk. pw-02 "Induction, strong induction, well-ordering" (Cummings ch. 7; hook: infinite dominoes): Segment 1 = induction mechanics + one faded example, Segment 2 = strong induction + well-ordering equivalence sketch; visual: canvas domino cascade. Checklist + parser + separate commits.

### Task 8: Lessons gt-01, gt-02 (Carter + Aluffi)

**Files:** Create `lessons/gt/gt-01.html`, `lessons/gt/gt-02.html`

Sources: bookmap "Carter" (gt-01 primary), "Aluffi Underground" (gt-02 primary). gt-01 "Symmetry: groups before the definition" (Carter ch. 1-2; hook: rectangle/light-switch/dance-move walk into a bar): Segment 1 = symmetries as actions, the rectangle's four moves (Carter ch. 1), Segment 2 = rules of the game: closure/identity/inverses discovered informally (Carter ch. 2) — NO formal axioms yet (that's gt-02); visual: canvas rectangle flipping/rotating through its four symmetries on click; embed link-as-text to Macauley VGT lecture 1 in citations. gt-02 "Groups: definition and first properties" (Aluffi Underground ch. 1; hook: four axioms that generate a universe): Segment 1 = the definition, matched against gt-01's discovered rules, first examples (ℤ, ℤ/nℤ, symmetries), Segment 2 = uniqueness of identity/inverses proved (faded), order of an element; visual: Cayley-table SVG for ℤ/4ℤ vs Klein four, spot-the-difference self-check. Checklist + parser + separate commits.

---

### Task 9: Wire-up verification + handover

**Files:**
- Modify: `state/SESSION-HANDOFF.md`, `docs/phase1-notes.md` (mark items 1-2 resolved), `README.md` (add "Daily use" section)

- [ ] **Step 1: End-to-end dry check** — full pytest suite green (15 tests); `python scripts/build_dashboard.py` runs; every lessons/*/*.html passes the parser check; every syllabus resource string for units pw-01..gt-02 resolves through bookmap or RESOURCES.md tables.
- [ ] **Step 2: README "Daily use"**

```markdown
## Daily use
- `/today` — run a study day (warm-up → two lectures → problems)
- `/lecture <unit>` — one lesson (generates it if missing)
- `/status` — dashboard: kanban, streaks, unlocked units
Lessons live in `lessons/`, open in any browser, work offline.
```

- [ ] **Step 3: Update SESSION-HANDOFF.md** — "Phase 1 complete; 8 lessons ready (pw-01/02, la-01/02, an-01/02, gt-01/02); start with /today. Phase 2 next: SRS + /grade + problem sets."
- [ ] **Step 4: Mark phase1-notes items 1-2 resolved** (bookmap; enum transitions implemented in skills).
- [ ] **Step 5: Commit** — `chore: phase 1 wire-up, handover, daily-use docs`

---

## Self-Review (completed)

- **Spec coverage:** §5 commands /today, /lecture, /status ✓ (T4); /resume deferred to Phase 3 per spec §9 (SESSION-HANDOFF resume logic included in /today step 2 as interim) ✓; §6 learning-science requirements embedded in LESSON-GUIDE (hooks, faded examples, self-checks, timeboxes) ✓; §9 Phase 1 "first two weeks of lessons" = 8 lessons ✓; phase1-notes items 1 (bookmap, T1) and 2 (enum, T4 skills + Global Constraints) ✓. SRS and /grade correctly absent (Phase 2).
- **Placeholder scan:** Task 1 JSON contains "...same pattern..." markers — these are explicitly instructed to be replaced from Step 1's ls output and the task fails if literal ellipses remain; acceptable as the values are machine-discoverable, not design decisions. No TBDs elsewhere.
- **Type consistency:** `render(syllabus, progress, streaks) -> str` consistent between T2 test and implementation; template tokens listed in T3 match those the guide references; skills reference only files created in T1-T3 or Phase 0; status enum strings match Phase 0's (`unlocked`/`locked`) plus spec's `in-progress`/`mastered` (dashboard COLUMNS covers all four).
