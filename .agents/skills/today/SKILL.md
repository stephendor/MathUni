---
name: today
description: Run today's study day — warm-up, two lectures, problem segment. Use when Stephen says /today, "start today", or "what's on today".
---

# /today — run a study day

Work from the repo root (verify cwd = MathUni). All state writes atomic
(temp file + os.replace via python -c, or write-then-move).

**The plan is not yours to invent.** `scripts/daily.py` picks the units, counts
the due cards and writes `state/today.json` deterministically, and the scheduled
task has usually already run it. Reading that file is the difference between a
day that survives a usage limit and one that does not — a model choosing units
is exactly the dependency this loop was rebuilt to remove.

1. **Load the plan**: read `state/today.json`.
   - Missing, or its `date` is not today? Run `python scripts/daily.py` and read
     it again. Do not build a plan by hand.
   - `rest_day: true`? Say so, offer `/review` if cards are due, and stop. Rest
     days are not a failure and carry no debt.
2. **Load state**: `state/progress.json`, `state/streaks.json`,
   `state/SESSION-HANDOFF.md`.
3. **Resume check**: if SESSION-HANDOFF.md shows an unfinished day for today,
   resume it at the recorded step rather than starting over.
4. **Run the day** as `state/sessions/<today>.md` lays it out:
   - **Warm-up (~10 min)** — the SRS session. Prefer the page:
     `<base>/review` — base from `state/server.json`, since the port is not
     always 8787 — runs the whole loop offline and writes each rating straight
     to the deck, at zero token cost. Fall back to the /review
     skill's conversational mode when Stephen wants reteaching on misses.
     The queue is capped at 15, oldest-due first; the backlog drains across
     sessions and is not a debt to clear in one sitting.
   - **Lecture 1 and Lecture 2** — the two units named in the plan. Follow
     .agents/skills/lecture/SKILL.md for each, including its state updates.
     Offer Stephen the order (ADHD: choice within structure).
   - **Problem segment (~25 min)** — from the plan's `problem_candidates`,
     which are already ordered unmastered-first across every unlocked and
     in-progress unit with a set on disk. Offer the choice; don't silently pick.
     Work 2-3 problems with the hint ladder: nudge → strategy → partial → worked.
5. **Log continuously**: append each completed step to `state/sessions/<today>.md`
   the moment it finishes; update SESSION-HANDOFF.md (date, plan, current step)
   so a dead session resumes losslessly.
6. **Close the day**: update streaks.json (append today to study_days once,
   recompute current/best — dates on the 4-day/week schedule count as
   consecutive if within 3 days); run `python scripts/build_dashboard.py`; give
   a 3-line summary plus one genuinely interesting teaser for next session (the
   hook of the next unlocked unit, quoted from the syllabus).

Tone: engaging, hook-led, never guilt. Timebox: announce segment starts/ends;
suggest the break card's 5-minute break between lectures.
