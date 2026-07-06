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
