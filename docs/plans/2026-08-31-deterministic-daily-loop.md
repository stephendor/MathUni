# Deterministic Daily Loop — replacing the LLM-triggered morning routine

**Goal:** Make the daily study loop run without a model in the path. The trigger,
the day plan, the notification, the flashcards, and the home surface all become
deterministic local artifacts. A model is only ever invoked by something Stephen
deliberately started, so a usage limit or a provider outage can no longer cause a
silently missing study day.

**Status:** Phases 1–3 complete. Phases 4–5 specified, not started.

---

## Why

The scheduled `NexusCollege Morning` task has been failing continuously since
approximately 2026-07-11 while reporting healthy. Evidence gathered 2026-08-31:

- `state/streaks.json` last records a study day of **2026-07-10**; `state/sessions/`
  ends at 2026-07-18.
- `schtasks /Query /TN "NexusCollege Morning" /V` reports `Status: Ready`,
  `Last Run Time: 31/08/2026 06:30:00`, `Last Result: -1073741510` (0xC000013A,
  process terminated) — a run that wrote **nothing at all** to its log.
- `state/morning.log` holds five identical lines:
  `API Error: 404 ... "model: claude-sonnet-4-20250514"` — a model id that was
  retired underneath the automation.

Five independent failure modes, any one of which is sufficient:

1. **Model-ID rot.** The scheduled `claude -p "/morning"` resolved to a retired model.
2. **Silent death.** The current failure writes no log line, so even reactive
   diagnosis has nothing to read.
3. **Interactive-only, no battery.** The task carries `Logon Mode: Interactive only`
   and `Stop On Battery Mode, No Start On Batteries`. It cannot fire on a laptop on
   battery, or when nobody is logged in at 06:30.
4. **The notification goes nowhere.** `.claude/skills/morning/SKILL.md` step 4 falls
   back to writing `state/NUDGE.txt`, described as something "the interactive session
   surfaces". Grep finds `NUDGE` in four places — two skill mirrors, a plan doc, an
   SDD brief. **No reader exists.** The file has never been created.
5. **Usage-limit collision.** The whole entry point is one LLM call.

The deeper problem is that none of the work required a model. Every unit in
`curriculum/syllabus.yaml` already carries a `hook` string; unit selection is a
sort over `state/progress.json` respecting the DAG; the due count comes from
`srs/scheduler.py stats`, which is pure stdlib. The model was reading a string out
of a YAML file.

The repo already states the governing principle in its own authoring gates —
`scripts/gate.py`: *"absence of a check is not a pass"*; `scripts/mission.py`:
*"A non-zero exit is not a watched failure."* That discipline was never applied to
the scheduling layer.

## Architecture — the Tier 0 / Tier 1 split

| Tier | Rule | Contents |
|------|------|----------|
| **Tier 0** | No model, no network, must never fail | Pick the day, build the plan, notify, serve the home surface, open lessons, run SRS, update streaks and dashboard |
| **Tier 1** | Needs a model, **always user-initiated, never scheduled** | Grading proofs, problem hint ladder, generating a missing lesson, reteaching a lapsed card |

Provider-agnosticism is a consequence, not a separate mechanism: nothing scheduled
has a provider. A usage limit can only ever interrupt something Stephen chose to
start, where it reads as "try later" rather than as a day that did not happen.

## Tech stack

Python 3.13 stdlib only (no new dependencies), Windows PowerShell 5.1 for the toast,
Task Scheduler XML for the trigger, pytest for tests.

**Verified before planning (2026-08-31):**

- `[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications,
  ContentType=WindowsRuntime]` loads under PowerShell 5.1. BurntToast is **not**
  installed and `pwsh` 7 is absent; neither is needed.
- Because a local server is in scope, toast buttons use `activationType="protocol"`
  with `http://127.0.0.1:<port>/…` URLs. This avoids registering a COM activator,
  which is otherwise the hard part of actionable Windows toasts.
- `%APPDATA%\Microsoft\Windows\Start Menu\Programs` is writable, so an
  AppUserModelID can be registered via a shortcut.
- **Python 3.13 on Windows still defaults `open()` to cp1252.**
  `json.load(open('srs/deck.json'))` raises `UnicodeDecodeError` on the maths
  Unicode in the deck. Every file handle in new code passes `encoding="utf-8"`
  explicitly. This is why `srs/scheduler.py` carries its `reconfigure` block.
- `srs/deck.json` holds 66 cards, **all 66 currently due** (nothing rated since
  2026-07-11). Re-entry policy is a requirement, not a refinement.

## Global constraints

- Repo root `C:\Users\steph\MathUni`, branch `feat/deterministic-daily-loop` off
  `main`. Verify cwd and branch before any write or commit.
- Commits via `git commit -F <tempfile>`, never here-strings. Trailer
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- State writes atomic (`.tmp` + `os.replace`), matching `scripts/build_dashboard.py`.
- Dates ISO `YYYY-MM-DD`, local time.
- Status enum `locked | unlocked | in-progress | mastered`. `scripts/update_unlocks.py`
  remains the **only** path to `mastered`; nothing in this plan writes it.
- All new file I/O passes `encoding="utf-8"`.
- Every new gate ships a negative control proving it can fire.
- Skills are edited in `.agents/skills/` (authoring source) and mirrored to
  `.claude/skills/` in the same change.
- CI already ends on `python -m pytest -q`, so new tests are enforced on merge
  without touching `.github/workflows/quality-gates.yml`.

---

## Phase 1 — `scripts/daily.py`, the Tier-0 day builder *(done)*

**Files:** create `scripts/daily.py`, `tests/test_daily.py`.

**Interfaces**

- `pick_units(units, progress, today) -> list[dict]` — two candidates, different
  modules, `unlocked` before `in-progress`, DAG-respecting, deterministic tie-break
  by syllabus order.
- `build_plan(syllabus, progress, stats, today) -> dict` — the `today.json` payload.
- `is_study_day(schedule, today) -> bool`
- `render_session_md(plan) -> str` — the `state/sessions/YYYY-MM-DD.md` shape that
  `/today` step 2 already resumes from.
- CLI: `python scripts/daily.py [--force] [--date YYYY-MM-DD]`

**Writes** (all atomic):

- `state/sessions/YYYY-MM-DD.md` — human-readable day plan
- `state/today.json` — machine-readable plan: unit ids, hooks, titles, due count,
  problem candidates, generated timestamp
- `state/last-daily-run.json` — the heartbeat: `{date, outcome, plan_path, units,
  due_count}` where `outcome` ∈ `built | rest | already-built`

**Rules**

- Idempotent: re-running on a day whose plan exists is a no-op recording
  `outcome: "already-built"`, unless `--force`.
- On a rest day it still writes the heartbeat with `outcome: "rest"`, so *"did not
  run"* and *"ran, nothing to do"* cannot look alike. This is the specific defect
  that let seven weeks pass unnoticed.
- Never writes `mastered`; never changes unit status at all (that is `/lecture`'s
  job when a lesson is actually opened).
- No network, no subprocess to any model, no imports outside stdlib + repo modules.

- [x] Step 1: failing tests for `pick_units`, `is_study_day`, idempotency, and the
      rest-day heartbeat
- [x] Step 2: implement `scripts/daily.py`
- [x] Step 3: full suite green, run against real repo state, inspect artifacts

## Phase 2 — `scripts/serve.py`, the persistent local server *(done)*

**Files:** create `scripts/serve.py`, `tests/test_serve.py`.

`ThreadingHTTPServer` bound to `127.0.0.1` only. Port and a per-run token written to
`state/server.json`. **Mutating routes require the token** — this is an
unauthenticated local write API, and without a token any page open in the browser
can POST to it.

| Route | Purpose |
|-------|---------|
| `GET /` | Home surface (Phase 3) |
| `GET /lesson/<unit>` | Serve the existing lesson HTML; mark `unlocked` → `in-progress` |
| `GET /review` | Flashcard UI (Phase 4) |
| `POST /api/rate` | `scheduler.rate_card` writeback; token required |
| `GET /api/state` | Plan + progress + streak JSON |
| `GET /dashboard` | Existing `build_dashboard.py` output |

Runs persistently under its own logon-triggered task (Phase 5), so the toast always
has a live target.

## Phase 3 — the home surface *(done)*

`GET /` is the real front door, not a stub: today's hook as the headline, the two
lecture buttons, due-card count, problem-set candidates, streak, units sitting
`in-progress` too long, dashboard content inline, and the liveness banner from
Phase 5. Rendered server-side from `state/today.json` + `state/progress.json`.

Single renderer shared with a static fallback write, so a dead server still leaves
a readable page on disk.

## Phase 4 — `review.html`, offline flashcards with writeback

`srs/deck.json` already carries fronts and backs. The page renders cards, Stephen
self-rates 1–4, `POST /api/rate` calls `scheduler.rate_card` directly. The full SRS
loop with no model judging anything.

**Re-entry policy** (required — the deck is at 66/66 due): cap the session queue at
15, oldest-due first, so the backlog drains across sessions instead of presenting as
a wall. 15 matches the existing `/review` cap in the skill.

## Phase 5 — trigger, toast, liveness, skill rewiring

- `scripts/notify.ps1` — WinRT toast, text = lecture-1's `hook` verbatim, buttons
  protocol-linked to the server.
- Start Menu shortcut registering AppUserModelID `NexusCollege.Daily`.
- `scripts/register_daily_task.ps1` — replaces `scripts/register_morning_task.ps1`,
  using `schtasks /Create /XML` rather than the CLI form so **one task carries two
  triggers**: logon (delayed) and a daily time trigger. The CLI can only express one,
  which is part of why the current task misses so much. Sets `StartWhenAvailable=true`,
  `DisallowStartIfOnBatteries=false`, `RunOnlyIfIdle=false`, directly fixing failure
  mode 3. Registers the server's logon task. Deletes the `NexusCollege Morning` entry.
- `scripts/check_daily_liveness.py` — exits non-zero on a stale heartbeat, **with a
  negative-control test proving it fires**. Surfaces in the home surface banner,
  `/status`, and `/resume`.
- Skills: `/today` reads the pre-built plan rather than rebuilding it and keeps only
  the live Socratic layer; `/morning` becomes a thin `python scripts/daily.py --force`
  wrapper; the `NUDGE.txt` prose is removed. `.agents/` and `.claude/` both.

**The toast is best-effort; the page is the contract.** If the notification stack
fails entirely, the day was still built and the home surface is still there.

---

## Decisions taken

| Decision | Choice | Date |
|---|---|---|
| Trigger mechanism | Toast **and** home page, page load-bearing | 2026-08-31 |
| Local server | In scope | 2026-08-31 |
| Server lifetime | Persistent, own logon task | 2026-08-31 |
| Home surface scope | Full front door, not a minimal stub | 2026-08-31 |

## Out of scope

- Multi-provider fallback chains for Tier 1 (`claude → codex → ollama`). Only worth
  considering once Tier 0 is solid; Tier 1 work is user-initiated, so a limit is
  visible rather than silent.
- Changes to the content-authoring gate suite, which works and is not implicated.
