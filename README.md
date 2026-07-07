# Nexus College

A two-year, AT/TDA-specialised university mathematics curriculum, run by
Claude Code. Spec: [docs/specs/2026-07-03-nexus-college-design.md](docs/specs/2026-07-03-nexus-college-design.md).

## Layout
- `MISSION.md` / `NOTES.md` — learner mission and preferences (Pocock format)
- `curriculum/` — `syllabus.yaml` (unit DAG) + `modules/*.md` (module specs)
- `lessons/` — generated interactive HTML lessons
- `problems/` — problem sets, solutions, graded submissions
- `srs/` — spaced-repetition deck and local scheduler
- `state/` — progress, mastery, streaks, session logs (machine-written)
- `scripts/` — validator and state tooling
- `dashboard/` — generated HTML dashboard

## Daily use
- `/today` — run a study day (warm-up → two lectures → problems)
- `/lecture <unit>` — one lesson (generates it if missing)
- `/status` — dashboard: kanban, streaks, unlocked units
Lessons live in `lessons/`, open in any browser, work offline.

## Rules
- `state/` is machine-written; never hand-edit.
- `curriculum/syllabus.yaml` must pass `python scripts/validate_syllabus.py` before commit.
- Sessions resume from files alone: see `state/SESSION-HANDOFF.md`.
