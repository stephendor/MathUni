# Engram FSRS-4.5 swap — staged, trigger wired

**Status (2026-07-22):** staged and armed. The default scheduler is still SM-2;
FSRS-4.5 is vendored and dormant behind a config flag, and a trip-wire prompts the
swap once enough reviews exist. Deferred originally in [phase1-notes.md](phase1-notes.md) item 5.

## What was actually swapped (and what was not)

engram (`F:/Projects/engram/scripts/engram.py`) is a whole **concept-graph learning
engine** — nodes with claims/probes/edges, a receipts evidence log, a learner model,
calibration, misconceptions — with state in `~/.claude/learning`, outside any repo.
MathUni's SRS is a **flat flashcard deck** (`srs/deck.json`) scheduled repo-locally.
They are different paradigms, and phase1-notes said plainly: *swap `srs/scheduler.py`*,
and *do NOT run engram as a parallel plugin* (two queues fragment the spacing data).

So only engram's **FSRS-4.5 scheduling core** was vendored, into
[`srs/fsrs.py`](../srs/fsrs.py): the stability/difficulty/retrievability maths, the
interval function, and the coarse per-user `refit` multiplier. The flat deck, the
`/review` flow, and repo-local state are all unchanged.

## How it is wired

- **`srs/config.json`** — `{"scheduler": "sm2"|"fsrs", "engram_threshold": 50}`. The
  flag selects the engine; SM-2 is the default and behaves exactly as before.
- **Trip-wire** — `scheduler.py` prints a one-line `[engram] …` banner **to stderr**
  (stdout stays pure JSON for the skills) on the `due`/`rate` path when the deck has
  ≥ `engram_threshold` cumulative reps *and* we are still on SM-2. It self-silences
  after the swap. `stats` also reports `engram.ready` for the morning routine.
- **Surfacing** — `/review` relays the stderr notice once; `/morning` adds one nudge
  line when `stats` reports `engram.ready`. The trigger fires at the point of use,
  not in a doc.

## Flipping (one command, when the trip-wire fires)

```
python srs/scheduler.py swap-to-fsrs
```

This migrates every card (`migrate_deck`) and sets `config.scheduler = "fsrs"`. From
then on `rate` uses FSRS and appends a prediction record to `srs/reviews.jsonl`.

**Migration semantics (mechanical, lossless for schedule continuity):** each card's
SM-2 `ease`/`interval` are shed; **stability is seeded from the current interval**
(exact, since `interval_for(s, 0.9) == s`), difficulty is seeded neutral, and
`reps`/`lapses`/`due` are preserved. Unseen cards (interval 0) initialise on their
first FSRS review.

## Refit (later)

FSRS only beats SM-2 once it can fit the learner. After ~50 **further** FSRS reviews
(each logged with the retrievability the model predicted), run:

```
python srs/scheduler.py refit         # guarded; --force to override the threshold
```

It compares observed recall to predicted and rescales intervals via a single
`interval_multiplier` stored in `deck.memory`. Guarded below 50 records.

## Rollback

Set `"scheduler": "sm2"` in `srs/config.json`. FSRS fields on cards are inert under
SM-2 (which reads `ease`/`interval`) — but note migration shed those, so a clean
rollback means restoring the pre-swap `deck.json` from git. Do the swap on a branch.

## Tests

`python srs/fsrs.py selftest` — 25 checks: FSRS core identities, the card round-trip,
migration (preserves reps/lapses/due, seeds stability), and the refit guard +
direction (negative control on the 50-review threshold).
