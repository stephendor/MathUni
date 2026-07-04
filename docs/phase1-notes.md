# Notes for Phase 1 (from Phase 0 final review, 2026-07-04)

1. **Resource resolution scheme must be defined early.** `syllabus.yaml`
   `resources` entries are prose ("Axler 1A-1B"). `/lecture` needs a
   deterministic way to resolve these to files in
   `NexusCollege Core Texts\md\<book>\markdown.md` (+ `pages\` for
   citations). Decide the scheme (book-slug map in resources/inventory.json
   recommended) before generating the first lesson, or citations will drift.

2. **`state/progress.json` status enum will be extended, not just read.**
   Phase 0 seeds only `locked`/`unlocked`; spec §4 defines the full enum
   `locked/unlocked/in-progress/mastered`. Phase 1 skills own the
   transitions; add validator coverage when the enum grows.

3. Consider a `.gitattributes` (e.g. `* text=auto`) before any non-Windows
   contributor/agent touches the repo (current files are uniformly CRLF —
   harmless, but mixed-EOL diffs would appear if autocrlf settings differ).

4. Open user-side items: correct YouTube links for Axler's LADR course and
   the Cummings Proofs companion (currently duplicates of the Francis Su
   link — flagged in resources/RESOURCES.md); optional cleanup of stray
   build/ + checks.json in Core Texts pdf\ folder.
