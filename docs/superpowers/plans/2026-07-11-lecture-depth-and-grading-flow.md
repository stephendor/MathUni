# Lecture Depth, Grading Hand-off, and Problem Access Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen future-generated lessons, auto-hand-off from lesson end to grading, and remove the "only today's two lecture units" restriction on working problem sets.

**Architecture:** Three independent, additive changes to markdown skill/guide files plus one small pure-Python coverage-check script. No changes to `state/*.json` schemas, no changes to `/grade`'s marking logic, no retrofitting of existing lessons.

**Tech Stack:** Markdown skill files (Claude Code `.claude/skills/*/SKILL.md`), Python 3 (stdlib only, `re`), pytest (existing test style in `tests/`).

## Global Constraints

- New standard applies to lessons generated from now on only — do not modify `lessons/la/la-01.html` or any existing generated lesson.
- No changes to `state/progress.json`, `state/mastery.json`, or `state/streaks.json` schemas.
- No changes to `/grade`'s marking stance, rubric format, or `.claude/skills/grade/SKILL.md`.
- Follow existing script style: a pure, unit-testable function plus a thin `if __name__ == "__main__"` CLI wrapper (see `scripts/update_unlocks.py`, `scripts/validate_syllabus.py`).
- Follow existing test style: plain functions, no fixtures/classes needed, import the pure function directly (see `tests/test_update_unlocks.py`).
- British English, markdown skill files match the tone/format already used in `.claude/skills/lecture/SKILL.md`, `.claude/skills/today/SKILL.md`, `.claude/skills/grade/SKILL.md`.

---

### Task 1: Deepen `curriculum/LESSON-GUIDE.md`

**Files:**
- Modify: `curriculum/LESSON-GUIDE.md`

**Interfaces:**
- Produces: new checklist lines that Task 2's coverage script and Task 3's lecture-skill edit both reference by name ("coverage cross-check", "intermediate lemma", "guided proof").

- [ ] **Step 1: Add the four new requirements to the guide**

Open `curriculum/LESSON-GUIDE.md` and make these edits:

Replace item 4 (faded worked examples) — after the existing bullet text, add a new sentence:

```markdown
4. **Faded worked examples** within segments: first example fully worked
   (`.worked`), second partially completed (`.worked.fade`, gaps marked
   "⟨your step⟩"), then a `.you-try` block the learner does solo. Every
   technique the unit's `problems/sets/<unit>.md` uses must be demonstrated
   by at least one worked or faded example — read the problem set before
   drafting examples, not after.
```

Insert a new item 5 (renumbering the old 5–8 to 6–9), between the current items 4 and 5:

```markdown
5. **Intermediate lemmas.** Any lemma-style fact the unit's problem set
   relies on that isn't a named theorem in the primary text (e.g. "a·0=0"
   as a sub-step, not itself Axler's Theorem 1.29) must be explicitly
   stated and proved in the lesson body — never left for the learner to
   invent cold during grading.
```

Renumber the old item 5 (Self-checks) to item 6, and immediately after its bullet, insert a new item 7 (renumbering old 6/7/8 to 8/9/10):

```markdown
7. **Guided proof.** At least one point per lesson, after the self-checks
   and distinct from them: a free-response prompt where the learner writes
   a short proof inline, followed by a revealed model answer for
   self-comparison. Not multiple choice — this is deliberate proof-writing
   practice, not recognition.
```

Renumber remaining items (old 6 Visual element → 8, old 7 Blank-page ending → 9, old 8 Footer citations → 10) — keep their text unchanged, only update the leading numeral.

- [ ] **Step 2: Add the coverage cross-check to the pre-commit checklist**

At the end of the "Checklist before committing a lesson" section, before the final `html.parser` line, add:

```markdown
`python scripts/check_lesson_coverage.py <problem-set-path> <lesson-html-path>`
reports no missing theorem/definition references ✓ ·
```

- [ ] **Step 3: Verify the renumbering is internally consistent**

Run:
```bash
grep -n "^[0-9]\." curriculum/LESSON-GUIDE.md
```
Expected: a clean sequence `1.` through `10.` with no gaps or repeats.

- [ ] **Step 4: Commit**

```bash
git add curriculum/LESSON-GUIDE.md
git commit -m "Deepen LESSON-GUIDE: full technique coverage, intermediate lemmas, guided proof practice"
```

---

### Task 2: `scripts/check_lesson_coverage.py` coverage cross-check

**Files:**
- Create: `scripts/check_lesson_coverage.py`
- Test: `tests/test_check_lesson_coverage.py`

**Interfaces:**
- Produces: `find_missing_refs(problem_set_text: str, lesson_html_text: str) -> list[str]` — pure function, returns a sorted list of theorem/definition references (e.g. `"Theorem 1.29"`, `"Definition 1.19"`) that appear in the problem set text but not in the lesson HTML text. Empty list means fully covered.
- CLI: `python scripts/check_lesson_coverage.py <problem_set_path> <lesson_html_path>` prints the missing refs (one per line) and exits 1 if any are missing, exits 0 with no output if none.
- Consumed by: Task 3's `/lecture` generation step.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_check_lesson_coverage.py`:

```python
from scripts.check_lesson_coverage import find_missing_refs


def test_no_refs_in_problem_set_means_nothing_missing():
    assert find_missing_refs("Solve for x.", "<html>anything</html>") == []


def test_ref_present_in_lesson_is_not_missing():
    problem_set = "Use Theorem 1.29 to show av=0."
    lesson = "<p>Theorem 1.29 states that 0v=0 for all v.</p>"
    assert find_missing_refs(problem_set, lesson) == []


def test_ref_absent_from_lesson_is_reported():
    problem_set = "Use Theorem 1.29 and Definition 1.19."
    lesson = "<p>Definition 1.19 defines a vector space.</p>"
    assert find_missing_refs(problem_set, lesson) == ["Theorem 1.29"]


def test_multiple_missing_refs_sorted():
    problem_set = "See Theorem 1.34, Theorem 1.29, Definition 1.20."
    lesson = "<p>No theorems mentioned here.</p>"
    assert find_missing_refs(problem_set, lesson) == [
        "Definition 1.20", "Theorem 1.29", "Theorem 1.34",
    ]


def test_duplicate_refs_in_problem_set_reported_once():
    problem_set = "Theorem 1.29 and again Theorem 1.29."
    lesson = "<p>nothing</p>"
    assert find_missing_refs(problem_set, lesson) == ["Theorem 1.29"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_check_lesson_coverage.py -v`
Expected: `ModuleNotFoundError: No module named 'scripts.check_lesson_coverage'` (or collection error) for all 5 tests.

- [ ] **Step 3: Write the implementation**

Create `scripts/check_lesson_coverage.py`:

```python
"""Cross-check that a lesson HTML file covers every theorem/definition
reference its problem set relies on. Used as a pre-commit gate for newly
generated lessons (curriculum/LESSON-GUIDE.md)."""
import re
import sys

REF_PATTERN = re.compile(r"(Theorem|Definition|Lemma|Corollary)\s+\d+[A-Za-z]?(?:\.\d+)*")


def find_missing_refs(problem_set_text, lesson_html_text):
    refs = sorted(set(REF_PATTERN.findall_ref(problem_set_text)))
    return [r for r in refs if r not in lesson_html_text]


def main():
    if len(sys.argv) != 3:
        print("usage: check_lesson_coverage.py <problem_set_path> <lesson_html_path>")
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        problem_set_text = f.read()
    with open(sys.argv[2], encoding="utf-8") as f:
        lesson_html_text = f.read()
    missing = find_missing_refs(problem_set_text, lesson_html_text)
    for ref in missing:
        print(ref)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests, fix the regex-extraction bug, verify pass**

Run: `python -m pytest tests/test_check_lesson_coverage.py -v`
Expected: `AttributeError: 're.Pattern' object has no attribute 'findall_ref'` — `REF_PATTERN.findall_ref` isn't a real method; it should be `REF_PATTERN.findall`, but `findall` on a pattern with one group returns just the group captures, not the full match. Fix `find_missing_refs`:

```python
def find_missing_refs(problem_set_text, lesson_html_text):
    refs = sorted({m.group(0) for m in REF_PATTERN.finditer(problem_set_text)})
    return [r for r in refs if r not in lesson_html_text]
```

Run again: `python -m pytest tests/test_check_lesson_coverage.py -v`
Expected: all 5 tests PASS.

- [ ] **Step 5: Manual CLI smoke test against the real la-01 files**

Run:
```bash
python scripts/check_lesson_coverage.py problems/sets/la-01.md lessons/la/la-01.html
echo "exit code: $?"
```
Expected: prints whatever refs (if any) `problems/sets/la-01.md` names that aren't in the existing la-01 lesson HTML — this is informational only (la-01 predates this gate and is out of scope for retrofitting), just confirms the script runs cleanly end-to-end without crashing.

- [ ] **Step 6: Commit**

```bash
git add scripts/check_lesson_coverage.py tests/test_check_lesson_coverage.py
git commit -m "Add scripts/check_lesson_coverage.py: theorem/definition coverage gate for new lessons"
```

---

### Task 3: `/lecture` — generation-time coverage gate + post-minute-paper hand-off

**Files:**
- Modify: `.claude/skills/lecture/SKILL.md`

**Interfaces:**
- Consumes: `scripts/check_lesson_coverage.py` CLI from Task 2 (must exist before this task is applied).
- Consumes: `problems/sets/<unit>.md` / `problems/solutions/<unit>.md` naming convention already used by `/grade`.

- [ ] **Step 1: Add the coverage gate to the "Serve or generate" step**

In `.claude/skills/lecture/SKILL.md`, find step 4:

```markdown
4. **Serve or generate**:
   - If lessons/<module>/<unit>.html exists: open it via PowerShell
     `Start-Process` with the **absolute** path, e.g.
     `Start-Process "C:\Users\steph\MathUni\lessons\<module>\<unit>.html"`
     (relative paths via `cmd /c start` from the bash shell are unreliable —
     use the absolute-path PowerShell form every time), and run the live layer.
   - If missing: generate it FIRST, following curriculum/LESSON-GUIDE.md
     exactly (template lessons/_template.html; sources via
     resources/bookmap.json, read the md, cite pages), commit it, then open.
```

Replace the "If missing" bullet with:

```markdown
   - If missing: generate it FIRST, following curriculum/LESSON-GUIDE.md
     exactly (template lessons/_template.html; sources via
     resources/bookmap.json, read the md, cite pages). Before committing,
     if problems/sets/<unit>.md exists, run
     `python scripts/check_lesson_coverage.py problems/sets/<unit>.md lessons/<module>/<unit>.html`
     — it must report no missing references; if it reports any, add the
     missing theorem/definition/lemma to the lesson body (per
     LESSON-GUIDE.md item 5) before committing. Then commit, then open.
```

- [ ] **Step 2: Add the post-minute-paper hand-off step**

Find step 5 (live layer) and step 6 (state updates):

```markdown
5. **Live layer** (the part a file can't do): after Stephen reads each
   segment, ask one Socratic question about it; answer questions with
   citations into the source; at lesson end pose the unit's "minute paper" —
   one-sentence summary in Stephen's own words + muddiest point. Record both
   in learning-records/<unit>.md (create; append if exists).
6. **State updates** (atomic): set unit status `unlocked` → `in-progress` in
   state/progress.json when the lesson opens. Append to today's session log.
7. **Never** mark `mastered` — that is /grade (Phase 2).
```

Insert a new step 6 between the current 5 and 6, renumbering the old 6/7 to 7/8:

```markdown
6. **Hand off to grading**: after the minute paper is recorded, check
   whether problems/sets/<unit>.md exists. If not, generate it now
   (following the same rubric-authoring process /grade expects, alongside
   problems/solutions/<unit>.md) so Stephen is never left without a
   problem set for a unit just lectured. Open/display the problem set and
   ask: "Want to attempt this now, or later via /grade <unit>?" If Stephen
   says later, change nothing else — /grade <unit> continues to work
   standalone.
```

- [ ] **Step 3: Verify the full file reads coherently**

Run: `cat .claude/skills/lecture/SKILL.md` (or Read the file) and confirm steps are numbered 1, 4, 5, 6, 7, 8 in sequence with no duplicate numbers (the file already skips 2/3 before this edit — preserve that existing numbering quirk, just don't introduce a new gap or collision from this edit).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/lecture/SKILL.md
git commit -m "lecture: gate new-lesson commits on coverage check, hand off to grading after minute paper"
```

---

### Task 4: `/today` — broaden the problem segment beyond the day's two lecture units

**Files:**
- Modify: `.claude/skills/today/SKILL.md`

**Interfaces:**
- Consumes: `state/progress.json` (`status` field), `state/mastery.json` (`score` field), existence of `problems/sets/<unit>.md`.

- [ ] **Step 1: Replace the problem segment bullet**

In `.claude/skills/today/SKILL.md`, find within step 3:

```markdown
   - Problem segment (~25 min): 2-3 problems from the current units'
     primary-text exercises (resolve via resources/bookmap.json), worked
     interactively with the hint ladder: nudge → strategy → partial → worked.
```

Replace with:

```markdown
   - Problem segment (~25 min): candidates are every unit with status
     `unlocked` or `in-progress` in state/progress.json that has a
     problems/sets/<unit>.md — not only today's two lecture units.
     Prioritize units not yet mastered (mastery.json score < 0.8, or no
     entry at all) over units already passed. If more than one candidate
     qualifies, offer Stephen the choice (ADHD: choice within structure) —
     don't silently pick. Work 2-3 problems from the chosen unit's set,
     interactively with the hint ladder: nudge → strategy → partial → worked.
```

- [ ] **Step 2: Verify no other step references "current units" for problems**

Run: `grep -n "current units" .claude/skills/today/SKILL.md`
Expected: no matches (the phrase was only in the bullet just replaced).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/today/SKILL.md
git commit -m "today: broaden problem segment to all unlocked/in-progress units, not just today's two lectures"
```

---

### Task 5: New standalone `/problems <unit-id>` skill

**Files:**
- Create: `.claude/skills/problems/SKILL.md`

**Interfaces:**
- Consumes: `state/progress.json`, `problems/sets/<unit>.md`, the hint-ladder pattern already described in `.claude/skills/today/SKILL.md`.
- Produces: entry point Stephen invokes as `/problems <unit-id>`, ending by pointing at `/grade <unit>`.

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/problems/SKILL.md`:

```markdown
---
name: problems
description: Work any unlocked/in-progress unit's problem set on demand, outside the structured /today flow. Use for /problems <unit-id>, "let me do some problems", "work on <unit>'s problem set".
---

# /problems <unit-id> — on-demand problem set

1. **Resolve the unit** in curriculum/syllabus.yaml (fuzzy-match titles if
   given a topic, confirm with Stephen). Check state/progress.json: the
   unit must be `unlocked` or `in-progress` — if `locked`, say what's
   missing (unmastered prereqs) rather than proceeding; if already
   `mastered`, ask whether Stephen wants extra practice anyway rather than
   refusing.
2. **Load the problem set**: problems/sets/<unit>.md. If it doesn't exist,
   say so and suggest running /lecture <unit-id> first (lesson generation
   now creates the problem set alongside the lesson).
3. **Work interactively**, same hint ladder as /today's problem segment:
   nudge → strategy → partial → worked, one problem at a time, letting
   Stephen attempt before offering the next hint level.
4. **No grading here** — this skill is for practice/attempts only. When
   Stephen is ready to submit for a score, point at `/grade <unit-id>`;
   don't invoke /grade automatically.
```

- [ ] **Step 2: Verify the frontmatter matches the existing pattern**

Run: `head -5 .claude/skills/today/SKILL.md .claude/skills/problems/SKILL.md`
Expected: both files show a `---` frontmatter block with `name:` and `description:` fields in the same style.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/problems/SKILL.md
git commit -m "Add /problems skill: on-demand problem-set access for any unlocked/in-progress unit"
```

---

## Self-review notes (for the implementer to re-check after all tasks land)

- Spec Part 1 (depth) → Task 1 (guide) + Task 2 (automated gate).
- Spec Part 2 (hand-off) → Task 3.
- Spec Part 3 (broadened access) → Task 4 (`/today`) + Task 5 (`/problems`).
- Out-of-scope items from the spec (retrofitting existing lessons, DAG
  restructuring, `/grade` changes) — confirm no task above touches
  `lessons/la/la-01.html`, `curriculum/syllabus.yaml` prereqs, or
  `.claude/skills/grade/SKILL.md`.
