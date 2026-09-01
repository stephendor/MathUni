---
name: morning
description: Rebuild today's study day by hand. The scheduled task already does this every day without a model; use this when it has not run, or to force a fresh plan.
---

# /morning — rebuild today (no model in the path)

The 06:30 routine is no longer a model call. `scripts/daily.py` builds the day
from `syllabus.yaml`, `progress.json` and the SRS deck with stdlib only, and the
`NexusCollege Daily` scheduled task runs it at logon and again at 06:30. This
skill is the manual handle on that same script — it is not a second
implementation, and you must not rebuild the plan yourself.

The old version of this skill called a model at 06:30 and wrote a hook line to
`state/NUDGE.txt` for "the interactive session" to surface. No reader for that
file ever existed, and the model call 404'd on a retired model id every study
morning from 2026-07-11 to 2026-08-31 while the task reported `Status: Ready`.
Both are gone. See `docs/plans/2026-08-31-deterministic-daily-loop.md`.

1. Verify cwd is `C:\Users\steph\MathUni`.
2. `python scripts/daily.py --force`
   On success it prints one JSON line — outcome, date, units, due count —
   and exits 0. Relay it. With `--force` the outcome is `built` on a study
   day and `rest` otherwise; `already-built` only appears on an unforced run
   that found today's plan already on disk.
   On failure it prints nothing on stdout, writes the reason to stderr, and
   exits 2, having recorded a heartbeat with outcome `failed`. Report that
   rather than treating a silent run as success.
3. Optionally post the toast:
   `powershell -ExecutionPolicy Bypass -File scripts\notify.ps1`
   It exits 0 even when it fails — the toast is best-effort, the page is the
   contract.
4. If Stephen wants to look at it, the home surface is `http://127.0.0.1:8787/`
   when the server is up, and `dashboard/today.html` on disk when it is not.

Never hand-write `state/today.json`, `state/sessions/<date>.md`, or
`state/last-daily-run.json`. They are machine-written, and a hand-written
heartbeat is a lie about whether the automation is alive.
