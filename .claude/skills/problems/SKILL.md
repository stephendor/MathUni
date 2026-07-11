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