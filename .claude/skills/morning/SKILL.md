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
