---
name: review
description: Run a spaced-repetition retrieval session from the SRS deck. Use for /review, "quiz me", "flashcards", or the /today warm-up.
---

# /review — retrieval session

There are two ways to run this, and the page is the default.

## The page (zero tokens, works during a usage limit)

If the local server is up, send Stephen to `http://127.0.0.1:8787/review`. It
shows one front at a time, reveals the back, takes 1-4 on click or keypress, and
POSTs each rating straight into `srs.scheduler.apply_rating` — the same function
the CLI uses. The queue is capped at 15, oldest-due first, and the page states
what it is holding back. A rating that fails to save stops the session and says
so rather than advancing.

Nothing about retrieval needed a model: the deck already carries the back of
every card, and Stephen's own rating has always been the one that counts.

Start the server with `python scripts/serve.py` if it is not running.

## The conversation (Tier 1 — when reteaching is the point)

Use this when Stephen asks for it, or when he is getting things wrong and wants
the explanation rather than the drill. It costs tokens and it is worth them for
exactly that.

1. From repo root (verify cwd): `python srs/scheduler.py due` → due cards.
   If none due: say so, offer 5 random cards as a bonus round, or exit
   gracefully. Never invent unscheduled obligations.
2. Quickfire format (learner-confirmed effective): present ONE card front at a
   time, conversationally. Stephen answers in his own words.
3. Judge the answer against the back honestly: correct / partially / missed.
   Ask Stephen to self-rate: again(1) hard(2) good(3) easy(4) — his rating wins
   over yours unless he under-rates a clean answer, and then say so.
4. `python srs/scheduler.py rate <id> <rating>` after EACH card (state-first).
5. On misses: 20-second reteach with the citation, not a lecture. If the same
   card lapses 3+ times, note it in `learning-records/<unit>.md` as a sticking
   point and suggest revisiting the lesson segment.
6. Cap: 15 cards or ~10 minutes, whichever first; then stop — retention lives in
   the schedule, not in marathon sessions. Close with count + one encouraging,
   specific observation.
7. If `scheduler.py` prints an `[engram] …` notice on **stderr** (it fires once
   the deck passes 50 logged reviews), relay that one line to Stephen at the
   close — it means the FSRS-4.5 scheduler swap is now worthwhile
   (`docs/engram-fsrs-swap.md`). Never let it interrupt the retrieval flow.
   The page relays the same notice at the top of the queue.
