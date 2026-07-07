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
