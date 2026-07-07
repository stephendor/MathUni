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
