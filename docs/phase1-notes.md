# Notes for Phase 1 (from Phase 0 final review, 2026-07-04)

1. **RESOLVED.** Resource resolution scheme implemented via `resources/bookmap.json`
   (longest-prefix match) with non-book resources (video playlists, folder
   names) documented in `resources/RESOURCES.md`; verified end-to-end for all
   8 Phase 1 units.

2. **RESOLVED.** `state/progress.json` status enum extended to the full
   `locked/unlocked/in-progress/mastered` set, with transitions owned by
   Phase 1 skills as designed.

3. Consider a `.gitattributes` (e.g. `* text=auto`) before any non-Windows
   contributor/agent touches the repo (current files are uniformly CRLF —
   harmless, but mixed-EOL diffs would appear if autocrlf settings differ).

4. Open user-side items: all video links now resolved and verified
   (2026-07-04); optional cleanup of stray build/ + checks.json in
   Core Texts pdf\ folder remains.

Phases 2+3 (2026-07-07): SRS, mastery gating, problem sets, resume, morning routine delivered; item 3 (.gitattributes) still open.

5. **Scheduler upgrade candidate (2026-07-07).** `F:\Projects\engram\scripts\engram.py`
   contains a clean, stdlib-only FSRS-4.5 implementation with a 33-check
   selftest. FSRS fits per-learner memory parameters and outperforms SM-2,
   but only once review history exists — revisit swapping `srs/scheduler.py`
   after ~50 logged reviews (engram's own `refit` guard uses the same
   threshold). Deck format is JSON either way; migration is mechanical.
   Do NOT run engram as a parallel plugin for maths content — two review
   queues over one curriculum fragments the spacing data.
