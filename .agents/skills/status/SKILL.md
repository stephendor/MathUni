---
name: status
description: Refresh and show the visual dashboard — kanban, streaks, module progress, what's unlocked. Use for /status, "where am I", "show progress".
---

# /status — the college noticeboard

1. `python scripts/check_daily_liveness.py`. If it exits non-zero, say so first:
   a progress display that looks healthy while the automation is dead is the
   exact failure this college spent seven weeks inside.
2. Open the surface Stephen actually uses:
   - Server up (`state/server.json` and `http://127.0.0.1:8787/healthz` answers)
     → `Start-Process "http://127.0.0.1:8787/"`. The home page carries today's
     hook, the lecture and review buttons, stale units and module bars.
   - Server down → `python scripts/daily.py` (refreshes `dashboard/today.html`)
     then `Start-Process "C:\Users\steph\MathUni\dashboard\today.html"`.
     Mention that the server can be started with `python scripts/serve.py` if
     he wants the review page and the writeback.
3. For the full kanban across all 145 units, `python scripts/build_dashboard.py`
   then `Start-Process "C:\Users\steph\MathUni\dashboard\index.html"` — use the
   **absolute** path via PowerShell `Start-Process` (relative paths through
   `cmd /c start` from the bash shell are unreliable).
4. Say, in ≤6 lines: current streak; units in-progress; units newly unlocked
   (with their hooks — sell them); next mastery gates ahead; one line of
   encouragement tied to actual data, never generic, never guilt.
5. If any unit has sat `in-progress` >7 days, gently offer a 15-minute
   "close it out" mini-session as an option, not an obligation. The home page
   already lists these under "Still open"; don't restate more than the top two.
