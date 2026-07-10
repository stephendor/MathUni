---
name: status
description: Refresh and show the visual dashboard — kanban, streaks, module progress, what's unlocked. Use for /status, "where am I", "show progress".
---

# /status — the college noticeboard

1. Run `python scripts/build_dashboard.py` (repo root; verify cwd).
2. Open dashboard/index.html via PowerShell `Start-Process` with the
   **absolute** path, e.g.
   `Start-Process "C:\Users\steph\MathUni\dashboard\index.html"`
   (relative paths via `cmd /c start` from the bash shell are unreliable).
3. Say, in ≤6 lines: current streak; units in-progress; units newly
   unlocked (with their hooks — sell them); next mastery gates ahead
   (Phase 2 note if grading not yet built); one-line encouragement tied to
   actual data (never generic, never guilt).
4. If any unit has sat `in-progress` >7 days, gently offer a 15-minute
   "close it out" mini-session as an option, not an obligation.
