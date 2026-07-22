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
7. If `scheduler.py` prints an `[engram] …` notice on **stderr** (it fires
   once the deck passes 50 logged reviews), relay that one line to Stephen at
   the close — it means the FSRS-4.5 scheduler swap is now worthwhile
   (`docs/engram-fsrs-swap.md`). Never let it interrupt the retrieval flow.
