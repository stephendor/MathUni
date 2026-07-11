# Lecture depth, grading hand-off, and problem access — design

Date: 2026-07-11
Status: approved, pending implementation plan

## Problem statement

Three related gaps surfaced while grading la-01's remedial set:

1. **Lecture depth is insufficient for grading questions.** Lessons lack enough
   worked examples, skip intermediate lemmas that problem sets assume (e.g.
   `a·0=0` in la-01), don't give Stephen practice writing proofs before being
   graded on one, and sometimes have thinner topic coverage than their own
   problem set requires (the la-01 Problem 5 curriculum bug: a problem
   required la-02 machinery the la-01 lesson never taught). Expected to recur
   in the Analysis and Group Theory tracks, not just Linear Algebra.
2. **No hand-off from a lesson's end-of-lecture self-checks into grading.**
   `/lecture` ends at the minute paper; Stephen has to separately know a
   problem set exists and invoke `/grade` cold.
3. **Problem-set access is restricted to the day's two lecture units.**
   `/today`'s problem segment only pulls from the units picked for that day's
   two lectures, so a unit's problem set is inaccessible on days it isn't one
   of those two picks.

## Scope decision: retrofit vs. going-forward

Applies to **lessons generated from now on only**. Already-mastered lessons
(la-01, pw-01) are not rewritten — they've already passed grading. Currently
in-progress lessons (an-01, gt-01) are also left as-is; the new standard
applies the next time a lesson is generated fresh, not retroactively to units
mid-flight. (If an-01/gt-01 later fail grading and need remediation, the new
depth standard naturally applies to any *new* material added at that point,
but existing lesson content isn't forcibly rewritten.)

## Part 1: Lecture depth — richer LESSON-GUIDE.md + generation-time cross-check

Rejected alternative: splitting each syllabus unit into two lessons (doubling
DAG granularity). This would touch `state/progress.json` schema, unlock
logic, and mastery tracking for every module — much larger blast radius than
the actual problem (thin content, not wrong unit boundaries).

Chosen approach: keep one lesson per unit, strengthen `curriculum/LESSON-GUIDE.md`
and the generation step in `.claude/skills/lecture/SKILL.md`:

- **Worked examples**: minimum count is no longer a flat number — it must
  cover every technique the unit's `problems/sets/<unit>.md` actually uses.
  Generation reads the problem set first, extracts the techniques/theorems
  each problem needs, and ensures a worked (or faded) example demonstrates
  each one before the lesson can be marked complete.
- **Intermediate lemmas**: any lemma-style fact a problem set relies on that
  isn't a named theorem in the primary text (e.g. `a·0=0`, used as a Problem 3
  sub-step in la-01) must be explicitly stated and proved in the lesson body.
  LESSON-GUIDE.md gets a new checklist line for this.
- **Guided proof practice**: a new lesson component, distinct from the
  existing MCQ-style `.selfcheck`: at least one point per lesson where Stephen
  writes a short proof inline (free response, not multiple choice) and the
  lesson reveals a model answer immediately after for self-comparison. Placed
  before the minute paper, after the self-checks.
- **Coverage cross-check (generation-time gate)**: before a newly generated
  lesson can be committed, a script parses `problems/sets/<unit>.md` for
  theorem/definition references and confirms each appears in the lesson body.
  Mismatches block commit with a clear message (same enforcement style as the
  existing html.parser structural check) — this is the automated version of
  the check that caught the la-01 Problem 5 bug manually.

Net effect: new lessons get materially longer and deeper, but through richer
requirements + an automated cross-check, not a DAG/schema change.

## Part 2: Lesson → grading hand-off

`.claude/skills/lecture/SKILL.md` gets a new step after the minute paper is
recorded:

- Check whether `problems/sets/<unit>.md` exists; if the unit doesn't have one
  yet, generate it (following the same rubric-authoring process `/grade`
  already expects, via `problems/solutions/<unit>.md`).
- Open/display the problem set and ask Stephen: "Want to attempt this now, or
  later via `/grade <unit>`?"
- If "later," nothing else changes — `/grade <unit>` continues to work
  standalone exactly as today.

No state schema changes. `/grade` itself is untouched.

## Part 3: Problem access — broaden `/today` + new `/problems` command

- **`/today`'s problem segment** (`.claude/skills/today/SKILL.md`, step 3's
  problem segment): instead of pulling only from the day's two lecture units,
  it considers all units with status `unlocked` or `in-progress` that have a
  `problems/sets/<unit>.md`, prioritizing units not yet mastered (mastery
  score < 0.8 or no attempt recorded). When more than one candidate qualifies,
  offer Stephen the choice (same "choice within structure" pattern already
  used for picking lecture units) rather than silently picking one.
- **New `/problems <unit-id>` skill** (`.claude/skills/problems/SKILL.md`):
  standalone, on-demand entry point to work any unlocked/in-progress unit's
  problem set outside the structured `/today` flow. Same interactive hint
  ladder (nudge → strategy → partial → worked) already used in `/today`'s
  problem segment. Ends by pointing at `/grade <unit>` once Stephen is ready
  to submit, mirroring Part 2's hand-off language.

This removes the "only today's two lecture units" restriction two ways:
`/today` itself widens, and `/problems` provides always-available ad hoc
access.

## Out of scope

- Retrofitting already-generated lessons (la-01, pw-01, an-01, gt-01) to the
  new depth standard.
- Restructuring the syllabus DAG (splitting units, changing prereqs).
- Changes to `/grade`'s marking stance or rubric format — grading itself is
  unaffected; only what feeds into it changes.

## Files touched (for the implementation plan)

- `curriculum/LESSON-GUIDE.md` — new checklist requirements.
- `.claude/skills/lecture/SKILL.md` — generation-time coverage cross-check,
  new post-minute-paper hand-off step.
- `.claude/skills/today/SKILL.md` — broadened problem-segment picker.
- New `.claude/skills/problems/SKILL.md`.
- Possibly a new `scripts/check_lesson_coverage.py` for the cross-check gate.
