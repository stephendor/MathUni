---
name: resume
description: Cold-restart the college from disk state after an interruption or usage-limit reset. Use for /resume, "where were we", "pick up where we left off".
---

# /resume — cold start from files only

Trust files, not memory. From repo root (verify cwd):

1. **Ask whether the automation is alive** — before anything else:
   `python scripts/check_daily_liveness.py`
   Exit 0 is fresh — which includes `rest` and `already-built`, so it means
   "a day was accounted for today", not "the builder is running right now".
   **Exit 1 is STALE** — a date older than today, or an outcome of `failed` —
   and must be surfaced in the first line, not buried. Exit 2 is `unknown`:
   an unparseable or future date, a heartbeat that is not an object, or an
   unreadable file. That is a broken check, not a broken builder, and should
   be reported as such rather than as a missed day.
   This step exists because the previous automation failed silently for seven
   weeks while every surface reported healthy. A stale heartbeat is news.
2. Read `state/SESSION-HANDOFF.md` → last session date, day plan, current step.
3. Read `state/sessions/<latest>.md` → what actually completed.
4. `python srs/scheduler.py stats`, `state/progress.json`, `state/mastery.json`,
   `state/streaks.json` → the numbers.
5. Report in ≤6 lines: whether the builder is running, where we stopped, what's
   due, what's in-progress, the next concrete action. Offer: continue the
   interrupted day, or start fresh with /today. If the handoff shows an
   unfinished graded submission or unclosed lesson, surface it first.
6. Never guilt about the gap. If >3 days since the last study day, re-hook with
   the most interesting waiting unit's hook — one line, quoted from the
   syllabus.

If the liveness check reported stale, offer the fix rather than only the
diagnosis: `python scripts/daily.py` rebuilds today immediately, and
`schtasks /Query /TN "NexusCollege Daily" /V /FO LIST` says what the scheduled
task thinks it is doing.
