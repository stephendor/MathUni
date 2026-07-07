# Nexus College Phases 2+3 — Mastery Loop & Automation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the learning loop — a real spaced-repetition engine feeding `/today`'s warm-up, problem sets with `/grade` mastery gating that unlocks the DAG, plus (Phase 3) `/resume` hardening and the scheduled morning agent.

**Architecture:** SRS is a local Python scheduler (zero tokens to schedule; Claude engages only during review conversation). Gating is machine-owned: `/grade` writes `state/mastery.json`, `scripts/update_unlocks.py` recomputes `progress.json`. Skills remain markdown in `.claude/skills/`.

**Tech Stack:** Python 3.11 stdlib + pyyaml + pytest; markdown problem sets; Claude Code skills; CronCreate for the morning routine (controller registers it).

## Global Constraints

- Repo root `C:\Users\steph\MathUni`, branch `main`; verify cwd before writes/commits; commits via `git commit -F <tempfile>` + trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; never here-strings.
- State writes atomic (`.tmp` + `os.replace`). Dates are ISO `YYYY-MM-DD` local.
- Status enum: `locked | unlocked | in-progress | mastered`. Only `/grade` (via update_unlocks) sets `mastered`.
- Mastery gate: score ≥ 0.8 on a unit's problem set. Below gate → targeted remediation, never a full redo.
- ADHD rules: hint ladder (nudge → strategy → partial → worked); one gentle nudge, never guilt; hooks in every notification.
- Learner feedback (2026-07-07, binding): quickfire warm-up starts and embedded reinforcement questions are confirmed effective — preserve both patterns in everything new.
- No Obsidian. Test output pristine. Suite floor entering: 15 tests.

---

### Task 1: SRS scheduler (TDD)

**Files:**
- Create: `srs/scheduler.py`, `srs/__init__.py` (empty)
- Test: `tests/test_scheduler.py`
- Generates: `srs/deck.json` (seeded empty: `{"cards": []}`)

**Interfaces:**
- Produces: card dict schema `{"id": str, "unit": str, "type": "definition"|"theorem"|"proof-sketch", "front": str, "back": str, "ease": float, "interval": int(days), "due": "YYYY-MM-DD", "reps": int, "lapses": int}`.
- Functions: `rate_card(card: dict, rating: int, today: str) -> dict` (rating 1=again 2=hard 3=good 4=easy; returns updated card), `due_cards(deck: dict, today: str) -> list[dict]`, `load_deck(path)`, `save_deck(deck, path)` (atomic).
- CLI: `python srs/scheduler.py due` (JSON list of due cards to stdout), `python srs/scheduler.py rate <card_id> <1-4>`, `python srs/scheduler.py add <json-file>` (appends cards, assigns due=today if absent), `python srs/scheduler.py stats`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_scheduler.py
from srs.scheduler import rate_card, due_cards

def card(**kw):
    c = {"id": "x", "unit": "la-01", "type": "definition", "front": "f",
         "back": "b", "ease": 2.5, "interval": 0, "due": "2026-07-07",
         "reps": 0, "lapses": 0}
    c.update(kw); return c

def test_new_card_good_schedules_one_day():
    c = rate_card(card(), 3, "2026-07-07")
    assert c["interval"] == 1 and c["due"] == "2026-07-08" and c["reps"] == 1

def test_new_card_easy_schedules_three_days():
    c = rate_card(card(), 4, "2026-07-07")
    assert c["interval"] == 3 and c["due"] == "2026-07-10"

def test_good_multiplies_by_ease():
    c = rate_card(card(interval=4, reps=2), 3, "2026-07-07")
    assert c["interval"] == 10  # round(4 * 2.5)

def test_again_resets_and_counts_lapse():
    c = rate_card(card(interval=10, reps=5), 1, "2026-07-07")
    assert c["interval"] == 0 and c["due"] == "2026-07-07" and c["lapses"] == 1
    assert c["ease"] == 2.3

def test_ease_floors_at_1_3():
    c = rate_card(card(ease=1.35), 1, "2026-07-07")
    assert c["ease"] == 1.3

def test_hard_grows_slowly_and_drops_ease():
    c = rate_card(card(interval=10, ease=2.5), 2, "2026-07-07")
    assert c["interval"] == 12 and c["ease"] == 2.35  # round(10*1.2)

def test_due_cards_filters_and_sorts():
    deck = {"cards": [card(id="a", due="2026-07-08"), card(id="b", due="2026-07-06"),
                      card(id="c", due="2026-07-07")]}
    ids = [c["id"] for c in due_cards(deck, "2026-07-07")]
    assert ids == ["b", "c"]
```

- [ ] **Step 2: Run to verify FAIL** — `python -m pytest tests/test_scheduler.py -v` → import error.

- [ ] **Step 3: Implement `srs/scheduler.py`**

```python
"""SM-2-style spaced repetition scheduler. Zero-token: /review shells out here.
Ratings: 1=again 2=hard 3=good 4=easy."""
import json
import os
import sys
from datetime import date, timedelta

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EASE_FLOOR = 1.3
DECK = "srs/deck.json"


def rate_card(card, rating, today):
    c = dict(card)
    d = date.fromisoformat(today)
    if rating == 1:
        c["ease"] = max(EASE_FLOOR, round(c["ease"] - 0.2, 2))
        c["interval"] = 0
        c["lapses"] += 1
        c["due"] = today
    elif rating == 2:
        c["ease"] = max(EASE_FLOOR, round(c["ease"] - 0.15, 2))
        c["interval"] = max(1, round(c["interval"] * 1.2)) if c["interval"] else 1
        c["due"] = (d + timedelta(days=c["interval"])).isoformat()
    elif rating == 3:
        c["interval"] = round(c["interval"] * c["ease"]) if c["interval"] else 1
        c["due"] = (d + timedelta(days=c["interval"])).isoformat()
    else:
        c["ease"] = round(c["ease"] + 0.1, 2)
        c["interval"] = round(c["interval"] * c["ease"] * 1.5) if c["interval"] else 3
        c["due"] = (d + timedelta(days=c["interval"])).isoformat()
    c["reps"] += 1
    return c


def due_cards(deck, today):
    return sorted((c for c in deck["cards"] if c["due"] <= today),
                  key=lambda c: c["due"])


def load_deck(path=DECK):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_deck(deck, path=DECK):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(deck, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def main(argv):
    from srs.scheduler import rate_card as _rc  # self-import safe under both invocations
    today = date.today().isoformat()
    cmd = argv[0] if argv else "due"
    deck = load_deck()
    if cmd == "due":
        print(json.dumps(due_cards(deck, today), ensure_ascii=False, indent=1))
    elif cmd == "rate":
        cid, rating = argv[1], int(argv[2])
        for i, c in enumerate(deck["cards"]):
            if c["id"] == cid:
                deck["cards"][i] = rate_card(c, rating, today)
                save_deck(deck)
                print(json.dumps(deck["cards"][i], ensure_ascii=False))
                return
        print(f"ERROR: no card {cid}"); sys.exit(1)
    elif cmd == "add":
        with open(argv[1], encoding="utf-8") as f:
            new = json.load(f)
        ids = {c["id"] for c in deck["cards"]}
        added = 0
        for c in new:
            if c["id"] in ids:
                continue
            c.setdefault("ease", 2.5); c.setdefault("interval", 0)
            c.setdefault("due", today); c.setdefault("reps", 0); c.setdefault("lapses", 0)
            deck["cards"].append(c); added += 1
        save_deck(deck)
        print(f"added {added} cards ({len(deck['cards'])} total)")
    elif cmd == "stats":
        n = len(deck["cards"]); due = len(due_cards(deck, today))
        by_unit = {}
        for c in deck["cards"]:
            by_unit[c["unit"]] = by_unit.get(c["unit"], 0) + 1
        print(json.dumps({"total": n, "due_today": due, "by_unit": by_unit}, indent=1))
    else:
        print("usage: scheduler.py [due|rate <id> <1-4>|add <file>|stats]"); sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 4: Tests pass (7 new, suite 22); write empty deck** — `srs/deck.json` = `{"cards": []}`; `python srs/scheduler.py stats` → total 0.
- [ ] **Step 5: Commit** — `feat: SRS scheduler (SM-2 style, zero-token CLI)`

---

### Task 2: Unlock recomputation + mastery store (TDD)

**Files:**
- Create: `scripts/update_unlocks.py`
- Test: `tests/test_update_unlocks.py`
- Generates: `state/mastery.json` (seeded `{}`)

**Interfaces:**
- Consumes: `load_syllabus` (Phase 0).
- Produces: `recompute(units: list[dict], progress: dict, mastery: dict) -> dict` (new progress: unit mastered iff mastery score ≥ 0.8; then any non-mastered unit with all prereqs mastered becomes `unlocked` unless already `in-progress`; units with unmastered prereqs stay/become `locked` unless `in-progress` or previously touched). CLI `python scripts/update_unlocks.py` rewrites state/progress.json atomically and prints newly unlocked unit ids. `/grade` runs this after writing mastery.json.

- [ ] **Step 1: Failing tests**

```python
# tests/test_update_unlocks.py
from scripts.update_unlocks import recompute

UNITS = [{"id": "a", "prereqs": []}, {"id": "b", "prereqs": ["a"]},
         {"id": "c", "prereqs": ["a", "b"]}]

def test_mastered_when_gate_met():
    prog = recompute(UNITS, {"a": {"status": "in-progress"}}, {"a": {"score": 0.85}})
    assert prog["a"]["status"] == "mastered"

def test_below_gate_not_mastered():
    prog = recompute(UNITS, {"a": {"status": "in-progress"}}, {"a": {"score": 0.7}})
    assert prog["a"]["status"] == "in-progress"

def test_dependents_unlock():
    prog = recompute(UNITS, {"a": {"status": "in-progress"}, "b": {"status": "locked"},
                             "c": {"status": "locked"}}, {"a": {"score": 0.9}})
    assert prog["b"]["status"] == "unlocked" and prog["c"]["status"] == "locked"

def test_in_progress_never_demoted():
    prog = recompute(UNITS, {"a": {"status": "mastered"}, "b": {"status": "in-progress"},
                             "c": {"status": "locked"}}, {"a": {"score": 0.9}})
    assert prog["b"]["status"] == "in-progress"

def test_roots_stay_unlocked_without_mastery():
    prog = recompute(UNITS, {"a": {"status": "unlocked"}, "b": {"status": "locked"}}, {})
    assert prog["a"]["status"] == "unlocked"
```

- [ ] **Step 2: FAIL run.**
- [ ] **Step 3: Implement**

```python
"""Recompute progress.json from mastery.json + DAG. Only path to 'mastered'."""
import json
import os
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.validate_syllabus import load_syllabus

GATE = 0.8


def recompute(units, progress, mastery):
    prog = {u["id"]: dict(progress.get(u["id"], {"status": "locked"})) for u in units}
    for uid, rec in mastery.items():
        if uid in prog and rec.get("score", 0) >= GATE:
            prog[uid]["status"] = "mastered"
    mastered = {u for u, p in prog.items() if p["status"] == "mastered"}
    for u in units:
        cur = prog[u["id"]]["status"]
        if cur in ("mastered", "in-progress"):
            continue
        if all(p in mastered for p in u["prereqs"]):
            prog[u["id"]]["status"] = "unlocked"
    return prog


def main():
    units = load_syllabus("curriculum/syllabus.yaml")["units"]
    with open("state/progress.json", encoding="utf-8") as f:
        progress = json.load(f)
    mastery = {}
    if os.path.exists("state/mastery.json"):
        with open("state/mastery.json", encoding="utf-8") as f:
            mastery = json.load(f)
    new = recompute(units, progress, mastery)
    newly = [u for u in new if new[u]["status"] == "unlocked"
             and progress.get(u, {}).get("status") == "locked"]
    tmp = "state/progress.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2)
    os.replace(tmp, "state/progress.json")
    print(json.dumps({"newly_unlocked": newly}))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Tests pass (5 new, suite 27); seed `state/mastery.json` = `{}`; CLI run is a no-op print `{"newly_unlocked": []}`.**
- [ ] **Step 5: Commit** — `feat: mastery gate + DAG unlock recomputation`

---

### Task 3: Seed the deck from the 8 lessons (authoring)

**Files:**
- Create: `srs/seed-batch-01.json` (the card source, kept for audit), applied into `srs/deck.json`

Author 6–9 cards per unit for pw-01, pw-02, la-01, la-02, an-01, an-02, gt-01, gt-02 (~55–70 total) by reading each `lessons/<mod>/<unit>.html`. Card mix per unit: 2-3 `definition` (front: "State the definition of X" — back: the cited definition), 2-3 `theorem` (front: statement prompt or "What does Theorem N say?"), 2-3 `proof-sketch` (front: "Outline the proof strategy of X" — back: 3-5 bullet sketch, NOT the full proof). ids: `<unit>-c<nn>` (e.g. `la-01-c03`). Fronts must be answerable without the lesson open; backs cite book+page like the lessons do. Learner feedback says quickfire works — write fronts quickfire-crisp. Apply with `python srs/scheduler.py add srs/seed-batch-01.json` → expect "added N cards". Commit deck + seed file: `feat: SRS deck batch 01 (8 units)`.

---

### Task 4: Problem sets + solutions for the 8 units (authoring)

**Files:**
- Create: `problems/sets/<unit>.md` and `problems/solutions/<unit>.md` for the 8 units

Per unit: 4–6 problems from the primary text's exercise pools (resolve via bookmap; cite exercise numbers/pages), ordered easy→hard, at least one proof problem. Each problem in the SET file carries a 4-rung hint ladder in `<details>` blocks (nudge → strategy → partial → worked start). SOLUTION files: complete model solutions + a grading rubric per problem (criteria + point weights summing to 1.0, with named partial credits, e.g. "correct contrapositive setup 0.3"). Sets must interleave: ≥1 problem per unit explicitly uses an earlier unit's idea (e.g. an-02 set includes one an-01 sup/inf problem — interleaving is a Global Constraint of the pedagogy). Header of each set file: unit id, source citations, "submit via /grade". Commit in two commits (sets, then solutions): `feat: problem sets batch 01` / `feat: solutions + rubrics batch 01`.

---

### Task 5: /review and /grade skills

**Files:**
- Create: `.claude/skills/review/SKILL.md`, `.claude/skills/grade/SKILL.md`

- [ ] **Step 1: Write `.claude/skills/review/SKILL.md`**

```markdown
---
name: review
description: Run a spaced-repetition retrieval session from the SRS deck. Use for /review, "quiz me", "flashcards", or the /today warm-up.
---

# /review — retrieval session

1. From repo root (verify cwd): `python srs/scheduler.py due` → due cards.
   If none due: say so, offer 5 random cards as a bonus round (rate them
   normally), or exit gracefully. Never invent unscheduled obligations.
2. Quickfire format (learner-confirmed effective): present ONE card front at
   a time, conversationally. Stephen answers in his own words.
3. Judge the answer against the back honestly: correct / partially / missed.
   Ask Stephen to self-rate: again(1) hard(2) good(3) easy(4) — his rating
   wins over yours unless he under-rates a clean answer (then say so).
4. `python srs/scheduler.py rate <id> <rating>` after EACH card (state-first).
5. On misses: 20-second reteach with the citation, not a lecture. If the same
   card lapses 3+ times, note it in learning-records/<unit>.md as a sticking
   point and suggest revisiting the lesson segment.
6. Cap: 15 cards or ~10 minutes, whichever first; then stop — retention
   lives in the schedule, not in marathon sessions. Close with count + one
   encouraging, specific observation.
```

- [ ] **Step 2: Write `.claude/skills/grade/SKILL.md`**

```markdown
---
name: grade
description: Grade a problem-set submission with rubric and partial credit; updates mastery and unlocks the DAG. Use for /grade, "mark my work", "check my proofs".
---

# /grade <unit-id> — rigorous marking

MODEL: this skill must run on the most capable model available (Opus/Fable
class). If the session is on a smaller model, say so and ask Stephen to
rerun on the bigger one — grading integrity is the product.

1. Locate submission: problems/submissions/<unit>-<date>.md (or Stephen
   pastes work — save it there first, verbatim).
2. Load problems/solutions/<unit>.md (rubric) and the primary text via
   resources/bookmap.json for authority on definitions.
3. Grade per problem against the rubric: named partial credits, and for
   proofs judge LOGIC not resemblance to the model solution — a different
   valid proof scores full marks; cite the text when ruling an inference
   invalid. Hand-waves named as hand-waves (learner preference), with the
   exact missing step identified.
4. Write feedback to problems/submissions/<unit>-<date>-graded.md:
   per-problem scores + comments, total score (0-1), then two lists:
   "What was genuinely good" and "The gap that matters most".
5. Update state/mastery.json atomically: {"<unit>": {"score": S, "attempts":
   n+1, "last": "YYYY-MM-DD"}} keeping the BEST score.
6. Run `python scripts/update_unlocks.py`; announce newly unlocked units BY
   THEIR HOOKS (sell the next thing). Run `python scripts/build_dashboard.py`.
7. If score < 0.8: build a remediation set of 2-3 problems targeting exactly
   the failed rubric lines (append to problems/sets/<unit>-remedial.md),
   never a full redo. Frame it as "close the gap", never as failure.
8. Log to today's session file + learning-records/<unit>.md (misconceptions
   observed, matched against the module spec's watchlist).
```

- [ ] **Step 3: Commit** — `feat: review and grade skills (mastery loop)`

---

### Task 6: /resume skill + /today warm-up integration (Phase 3)

**Files:**
- Create: `.claude/skills/resume/SKILL.md`
- Modify: `.claude/skills/today/SKILL.md` (warm-up step only)

- [ ] **Step 1: Write `.claude/skills/resume/SKILL.md`**

```markdown
---
name: resume
description: Cold-restart the college from disk state after an interruption or usage-limit reset. Use for /resume, "where were we", "pick up where we left off".
---

# /resume — cold start from files only

Trust files, not memory. From repo root (verify cwd):
1. Read state/SESSION-HANDOFF.md → last session date, day plan, current step.
2. Read state/sessions/<latest>.md → what actually completed.
3. `python srs/scheduler.py stats`, state/progress.json, state/mastery.json,
   state/streaks.json → the numbers.
4. Report in ≤6 lines: where we stopped, what's due (SRS count), what's
   in-progress, the next concrete action. Offer: continue the interrupted
   day, or start fresh with /today. If the handoff shows an unfinished
   graded submission or unclosed lesson, surface it first.
5. Never guilt about the gap; if >3 days since last study_day, re-hook with
   the most interesting waiting unit's hook, one line.
```

- [ ] **Step 2: Edit `.claude/skills/today/SKILL.md`** — replace the warm-up bullet ("Warm-up (~10 min): 3-5 quick recall questions ... note "SRS pending Phase 2" in the log.") with:

```markdown
   - Warm-up (~10 min): run the /review skill (srs/scheduler.py due). If
     fewer than 5 cards are due, top up with quickfire questions improvised
     from in-progress units. Quickfire pace — learner-confirmed effective.
```

- [ ] **Step 3: Commit** — `feat: resume skill + SRS-backed warm-up (phase 3)`

---

### Task 7: Morning routine + schedule config + notes wire-up (Phase 3)

**Files:**
- Create: `.claude/skills/morning/SKILL.md`, `state/schedule.json`
- Modify: `NOTES.md`, `README.md`, `state/SESSION-HANDOFF.md`, `docs/phase1-notes.md` (retitle header line to "Notes for Phase 1+ (living)" is NOT needed — instead append Phase 2/3 completion note)

- [ ] **Step 1: `state/schedule.json`**

```json
{"study_days": ["Mon", "Tue", "Thu", "Fri"], "morning_hour": "06:30",
 "note": "Stephen: edit study_days freely; the morning routine checks this file."}
```

- [ ] **Step 2: `.claude/skills/morning/SKILL.md`**

```markdown
---
name: morning
description: Pre-build today's study day and post the hook notification. Run by the scheduled routine on study days; also manually via /morning.
---

# /morning — the 06:30 routine (cheap, Sonnet-class)

1. From C:\Users\steph\MathUni (verify cwd). Read state/schedule.json —
   if today is not a study day, exit silently (no output, no files).
2. Build the day plan exactly as /today step 3 would (SRS due count via
   `python srs/scheduler.py stats`, two lecture candidates from different
   modules, problem segment) and write it to state/sessions/YYYY-MM-DD.md
   under a "## Plan (pre-built 06:30)" heading. /today step 2's resume
   check picks this up so nothing is rebuilt.
3. Run `python scripts/build_dashboard.py`.
4. Send ONE notification whose text IS the hook: "<hook of lecture-1 unit>
   — that's lecture 1. <n> cards waiting. /today when ready." Use the push
   notification tool if available in the session; else write the line to
   state/NUDGE.txt (the interactive session surfaces it).
5. Missed-day rule: if yesterday was a study day with no session log, add
   ONE line to the notification re-hooking yesterday's lecture-1 unit.
   Never more than one line, never guilt.
```

- [ ] **Step 3: Append to NOTES.md** (under Standing preferences):

```markdown
## Confirmed effective (2026-07-07)
- Quickfire warm-up starts and embedded reinforcement self-checks in lessons
  confirmed by Stephen as strong for focus and retention — keep both in all
  new lessons and reviews.
```

- [ ] **Step 4: README Daily use section** — add `/review`, `/grade <unit>`, `/resume`, `/morning` lines matching their skill descriptions.
- [ ] **Step 5: SESSION-HANDOFF.md** — "Phases 2+3 complete: SRS live (deck batch 01), problem sets + /grade gating live, /resume + morning routine ready. Cron registration: controller step after this task."
- [ ] **Step 6: Append to docs/phase1-notes.md**: "Phases 2+3 (2026-07-07): SRS, mastery gating, problem sets, resume, morning routine delivered; item 3 (.gitattributes) still open."
- [ ] **Step 7: Commit** — `feat: morning routine, schedule config, learner-feedback notes (phase 3)`

**Controller-only follow-up (not this task):** register the cron via CronCreate — 06:30 on Mon/Tue/Thu/Fri, prompt: work in C:\Users\steph\MathUni and follow .claude/skills/morning/SKILL.md. Verify with CronList.

---

## Self-Review (completed)

- **Spec coverage:** §5 /review (T5), /grade (T5, Opus-note embedded), morning agent (T7 + controller cron); §7 gating ≥80% + remediation (T2, T5); §9 Phase 2 = SRS engine (T1), deck (T3), /grade (T5), first problem sets (T4); Phase 3 = /resume (T6), scheduled agent + notifications (T7 + controller). Dashboard already exists (Phase 1) — /grade and /morning refresh it.
- **Placeholder scan:** none; authoring tasks (T3, T4) specify counts, id schemes, formats, and rubric-weight requirements concretely.
- **Type consistency:** card schema identical in T1 code/tests and T3 instructions; `recompute(units, progress, mastery)` matches tests; GATE=0.8 consistent with spec §7 and /grade step 7; scheduler CLI verbs in T5/T6/T7 match T1's implementation.
