"""daily.py — Tier 0 day builder: assemble today's study day with no model.

Everything /morning used a model for is a lookup. Every unit in the syllabus
already carries its own `hook` string; picking the day's units is a sort over
state/progress.json; the due count is a filter over srs/deck.json. So this
script imports nothing outside the stdlib and the repo, opens no socket, and
spawns no subprocess. It cannot fail because a provider is rate-limited, and it
cannot rot because a model id was retired underneath it — which is what killed
the scheduled morning routine between 2026-07-11 and 2026-08-31 while
`schtasks /Query` went on reporting `Status: Ready`.

Three artifacts, all written atomically:

  state/sessions/YYYY-MM-DD.md   the day plan a human (and /today) reads
  state/today.json               the same plan, machine-readable
  state/last-daily-run.json      the heartbeat

The heartbeat is the point. A rest day writes one too, with outcome "rest", so
that "did not run" and "ran, nothing to do" cannot look alike — indistinguishable
success and silent absence is exactly the confusion that let seven weeks of
failure pass unnoticed. Whatever reads this file must treat a stale date as a
failure, not as an absence of news (scripts/check_daily_liveness.py, Phase 5).

This script is READ-ONLY over state/progress.json. It never changes a unit's
status: /lecture moves unlocked -> in-progress when a lesson actually opens, and
scripts/update_unlocks.py remains the only path to "mastered".

  python scripts/daily.py [--force] [--date YYYY-MM-DD]

Exit 0 when the day was built, was already built, or is a rest day. Exit 2 when
the plan could not be built at all (wrong cwd, unreadable state) — a run that
could not reach a verdict must not look like a run that had nothing to do.
"""
import argparse
import json
import os
import sys
from datetime import date, datetime

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.home import (StaticLinks, build_view, render_home,
                          render_unbuilt_page)
from srs.scheduler import due_cards, load_deck

# scripts.validate_syllabus is NOT imported here, and the omission is the point.
# It is the only thing in this file's reach that needs PyYAML, so it is the only
# import that can fail because an interpreter's environment changed underneath
# it -- which is what happened during install, when a conda python without
# pyyaml was registered and this script died at import, before main() had a
# handler to write a "failed" heartbeat with. The task then reported success,
# because the notification action that runs afterwards exits 0 by design.
#
# The installer proves the interpreter can import this module, but it proves it
# once, at registration. Importing inside the guarded path means a dependency
# that breaks later still produces a heartbeat that says so.

PLAN_HEADING = "## Plan (pre-built)"

# Weekday abbreviations as a fixed table rather than strftime("%a"). strftime is
# locale-dependent: under a non-English Windows locale it returns "Mo"/"Di"/...,
# no entry in schedule.json would ever match, and every day would silently
# become a rest day. A scheduling bug that only reproduces on someone else's
# machine is not worth the two saved lines.
DAY_ABBR = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

# Warm-up cap. The deck stands at 66 of 66 due after the loop stalled, and
# presenting a 66-card wall on the first day back is how a re-entry fails. 15
# matches the cap already stated in .claude/skills/review/SKILL.md; the backlog
# drains oldest-due-first across sessions instead.
REVIEW_CAP = 15

STUDIABLE = ("unlocked", "in-progress")
MASTERY_GATE = 0.8


def is_study_day(schedule, today):
    """True when `today` (ISO date string) falls on a configured study day."""
    weekday = DAY_ABBR[date.fromisoformat(today).weekday()]
    return weekday in schedule.get("study_days", [])


def pick_units(units, progress, limit=2):
    """Choose today's lecture units. Deterministic; does not mutate `progress`.

    Ranked `unlocked` before `in-progress` — a fresh unit beats a stalled one —
    then by syllabus order, which is the DAG's own topological order.

    Status IS the DAG projection here: update_unlocks.recompute only marks a
    unit `unlocked` once every prereq is mastered, so filtering on status is
    already prereq-respecting. Re-deriving prereq logic in this file would give
    the repo a second opinion about the DAG that could drift from the first.

    Prefers units from different modules (variety within a session), but falls
    back to a same-module pair rather than returning a short day: early on, and
    again at the end of a semester, one module is legitimately all there is.
    """
    ranked = []
    for order, unit in enumerate(units):
        status = progress.get(unit["id"], {}).get("status", "locked")
        if status in STUDIABLE:
            ranked.append((STUDIABLE.index(status), order, unit))
    ranked.sort(key=lambda row: (row[0], row[1]))

    picked, modules = [], set()
    for _, _, unit in ranked:
        if len(picked) >= limit:
            break
        if unit["module"] not in modules:
            picked.append(unit)
            modules.add(unit["module"])
    if len(picked) < limit:  # top up from what is left, module repeats allowed
        chosen = {u["id"] for u in picked}
        for _, _, unit in ranked:
            if len(picked) >= limit:
                break
            if unit["id"] not in chosen:
                picked.append(unit)
    return picked


def problem_candidates(units, progress, mastery, available_sets):
    """Unit ids that have a problem set and are worth working, best first.

    Every studiable unit with a set on disk qualifies, not only today's two
    lecture units. Units below the mastery gate (or never attempted) sort ahead
    of ones already passed, so revisiting a solved set is always a deliberate
    choice rather than the default offer.
    """
    out = []
    for order, unit in enumerate(units):
        uid = unit["id"]
        if uid not in available_sets:
            continue
        if progress.get(uid, {}).get("status", "locked") not in STUDIABLE:
            continue
        passed = mastery.get(uid, {}).get("score", 0) >= MASTERY_GATE
        out.append((passed, order, uid))
    out.sort(key=lambda row: (row[0], row[1]))
    return [uid for _, _, uid in out]


def build_plan(syllabus, progress, stats, today, streaks, available_sets,
               schedule=None, mastery=None):
    """Assemble the machine-readable day plan.

    `schedule` is optional: pass it to have the rest-day decision made here,
    or omit it when the caller has already established that today is a study
    day. `stats` carries at least `due_today`; `available_sets` is the set of
    unit ids with a file under problems/sets/; `mastery` is state/mastery.json,
    without which problem_candidates cannot tell a passed set from an
    unattempted one and the "unmastered first" promise is vacuous.
    """
    rest = schedule is not None and not is_study_day(schedule, today)
    units = syllabus.get("units", [])
    mod_titles = {m["id"]: m.get("title", m["id"]) for m in syllabus.get("modules", [])}
    due = stats.get("due_today", 0)

    lectures = []
    if not rest:
        for unit in pick_units(units, progress):
            lectures.append({
                "id": unit["id"],
                "module": unit["module"],
                "module_title": mod_titles.get(unit["module"], unit["module"]),
                "title": unit["title"],
                # Verbatim from the syllabus. This string is the notification
                # text and the lesson's opening line; it is never paraphrased.
                "hook": unit["hook"],
                "status": progress.get(unit["id"], {}).get("status", "locked"),
                "lesson_path": "lessons/%s/%s.html" % (unit["module"], unit["id"]),
            })

    return {
        "date": today,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "rest_day": rest,
        "due_count": due,
        "deck_total": stats.get("total", 0),
        "review_target": min(due, REVIEW_CAP),
        "review_cap": REVIEW_CAP,
        "streak": {"current": streaks.get("current", 0),
                   "best": streaks.get("best", 0)},
        "lectures": lectures,
        "problem_candidates": [] if rest else problem_candidates(
            units, progress, mastery or {}, available_sets),
    }


def _cell(text):
    """Markdown table cells: a pipe in a hook would otherwise split the row."""
    return str(text).replace("|", "\\|")


def render_session_md(plan):
    """The day plan as markdown — hook first, never a definition first."""
    if plan["rest_day"]:
        return ("# Rest day — %s\n\n"
                "Not a study day per state/schedule.json. Nothing planned.\n"
                "Built by scripts/daily.py.\n" % plan["date"])

    lines = ["# Study Day — %s" % plan["date"], "",
             "**Status:** PLANNED",
             "**Streak:** %d (best %d)" % (plan["streak"]["current"],
                                           plan["streak"]["best"]),
             "", PLAN_HEADING, ""]
    if plan["lectures"]:
        lines += ["> %s" % plan["lectures"][0]["hook"], ""]

    due, target = plan["due_count"], plan["review_target"]
    warmup = ("SRS review: %d cards" % due if due <= target
              else "SRS review: %d of %d due (oldest first)" % (target, due))
    rows = [("Warm-up (~10 min)", warmup)]
    for n, lec in enumerate(plan["lectures"], 1):
        rows.append(("Lecture %d" % n, "%s — %s (%s)"
                     % (lec["id"], lec["title"], lec["module_title"])))
    if plan["problem_candidates"]:
        rows.append(("Problems (~25 min)", ", ".join(plan["problem_candidates"][:4])))

    lines += ["| Segment | Content | Status |", "|---------|---------|--------|"]
    lines += ["| %s | %s | pending |" % (_cell(a), _cell(b)) for a, b in rows]
    lines += ["", "Built by scripts/daily.py — no model involved.", ""]
    return "\n".join(lines)


def write_atomic(path, text):
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # newline="\n" because the repo is eol=lf (.gitattributes); text mode
    # on Windows would otherwise emit CRLF into machine-written state.
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def read_json(path, default=None):
    if not os.path.exists(path):
        return {} if default is None else default
    # encoding is explicit everywhere: Python 3.13 on Windows still defaults
    # open() to cp1252, and srs/deck.json carries maths Unicode that cp1252
    # cannot decode.
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_required_json(path):
    """Like read_json, but absence is an error rather than an empty default."""
    if not os.path.exists(path):
        raise OSError("%s is missing; run scripts/init_state.py" % path)
    with open(path, encoding="utf-8") as f:
        loaded = json.load(f)
    if not isinstance(loaded, dict):
        raise ValueError("%s does not contain an object" % path)
    return loaded


def plan_is_usable(obj, today):
    """True when a persisted plan can stand in for a rebuild.

    The date alone is not enough. `already-built` publishes the persisted
    object verbatim -- to the heartbeat, the static page and the server -- so
    `{"date": today}` and nothing else would suppress the rebuild and then
    publish an empty day through all three, permanently: the next run finds the
    same date and does the same thing. A plan that cannot be published is the
    strongest possible argument for building a new one.

    Deliberately a shape check, not a schema: it asks for what the page and the
    heartbeat actually read, so a plan gaining a field does not fail here.
    """
    if not isinstance(obj, dict) or obj.get("date") != today:
        return False
    if not isinstance(obj.get("lectures"), list):
        return False
    if not all(isinstance(lec, dict) and lec.get("id") for lec in obj["lectures"]):
        return False
    if not isinstance(obj.get("problem_candidates"), list):
        return False
    if not isinstance(obj.get("rest_day"), bool):
        return False
    # A study day with no lectures is not a plan, it is an empty file with
    # today's date on it. A rest day with none is exactly right.
    return bool(obj["lectures"]) or obj["rest_day"]


def _clean_mastery(raw):
    """mastery.json reduced to the shape problem_candidates can read.

    It is hand-edited and model-written, so `["x"]` or `{"aa-01": []}` are both
    reachable, and `.get` on either raises AttributeError deep inside the
    build. That crash is caught and turns into a "failed" heartbeat, but it
    takes the whole day with it -- over a file that only decides the ORDER of
    the problem candidates. Unreadable entries are treated as unattempted,
    which is what they were before anyone recorded a score.
    """
    if not isinstance(raw, dict):
        return {}
    return {uid: rec for uid, rec in raw.items() if isinstance(rec, dict)}


def available_problem_sets(root="problems/sets"):
    if not os.path.isdir(root):
        return set()
    return {n[:-3] for n in os.listdir(root) if n.endswith(".md")}


def _build(argv=None):
    ap = argparse.ArgumentParser(description="Build today's study day (no model).")
    ap.add_argument("--force", action="store_true",
                    help="rebuild even if today's plan already exists")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="ISO date to build for (default: today)")
    args = ap.parse_args(argv)
    today = args.date

    if not os.path.exists("curriculum/syllabus.yaml"):
        print("daily.py: run from the repo root (curriculum/syllabus.yaml not found)",
              file=sys.stderr)
        return 2

    try:
        from scripts.validate_syllabus import load_syllabus

        syllabus = load_syllabus("curriculum/syllabus.yaml")
        # schedule.json and progress.json are tracked, load-bearing, and have
        # no defensible default. An absent schedule made every date a rest day;
        # an absent progress file produced a day with no lectures. Both wrote a
        # healthy heartbeat, so the liveness check reported success while the
        # learner was silently assigned nothing -- a plausible empty day is
        # worse than a loud failure, and is the failure mode this loop exists
        # to remove. Missing means broken, not empty.
        schedule = read_required_json("state/schedule.json")
        progress = read_required_json("state/progress.json")
        # These two are genuinely optional: streaks are cosmetic, and mastery
        # only orders the problem candidates.
        streaks = read_json("state/streaks.json")
        mastery = _clean_mastery(read_json("state/mastery.json"))
        deck = load_deck()
        stats = {"due_today": len(due_cards(deck, today)),
                 "total": len(deck.get("cards", []))}
    except (OSError, ValueError, KeyError) as exc:
        # Re-raised rather than returned. main() is the only place that writes
        # a "failed" heartbeat and retracts the stale static page, and under
        # pythonw.exe this message goes nowhere -- returning 2 here left the
        # scheduled run with no trace at all, which is the shape of failure
        # this whole loop exists to make impossible. Exit 2 still: main()
        # returns 2, so a run that reached no verdict still cannot look like a
        # run that had nothing to do.
        raise RuntimeError("could not read state — %s" % exc) from exc

    plan_path = "state/sessions/%s.md" % today
    plan = build_plan(syllabus, progress, stats, today, streaks,
                      available_problem_sets(), schedule=schedule,
                      mastery=mastery)

    # A session file on disk is not proof the plan is on disk. state/today.json
    # is gitignored while state/sessions/ is tracked, so a fresh checkout has
    # the markdown and not the JSON; a crash between the two writes leaves the
    # same split. Reporting "already-built" then leaves the server and /today
    # reading an empty plan forever, because nothing ever rebuilds it.
    # A malformed today.json is "not current", not a crash: the whole point of
    # this check is to decide whether to rebuild, and an unreadable plan is the
    # strongest possible reason to.
    try:
        persisted = read_json("state/today.json")
    except ValueError:
        persisted = {}
    plan_current = plan_is_usable(persisted, today)
    session_exists = os.path.exists(plan_path)

    if plan["rest_day"]:
        # A rest day the learner studied anyway has a real session log. Do not
        # overwrite it with the generic rest-day text just because the logon
        # trigger fired again after a reboot.
        outcome = "already-built" if (session_exists and plan_current
                                      and not args.force) else "rest"
    elif session_exists and plan_current and not args.force:
        outcome = "already-built"
    else:
        outcome = "built"

    # When the run happened, which is not when the plan it publishes was made.
    ran_at = plan["generated"]

    if outcome == "already-built":
        # Publish what is ON DISK, not the recomputation that was just discarded.
        # Opening lecture 1 moves it unlocked -> in-progress, so a same-day rerun
        # (the logon trigger after a reboot) recomputes DIFFERENT units; rendering
        # those into the static page and the heartbeat would leave three files
        # disagreeing about what today is.
        plan = persisted

    heartbeat = {
        "date": today,
        "outcome": outcome,
        "generated": ran_at,
        "plan_path": plan_path,
        "units": [lec["id"] for lec in plan.get("lectures", [])],
        "due_count": plan.get("due_count", 0),
    }

    if outcome in ("built", "rest"):
        write_atomic(plan_path, render_session_md(plan))
        write_atomic("state/today.json", json.dumps(plan, indent=2) + "\n")

    # The static front door. Written every run, including "already-built", so
    # that a machine whose server is down still has a current page to open:
    # the plan's rule is that the page is the contract, and a contract that
    # only holds while a process is up is not one. Rendered against the
    # heartbeat this run is about to write, so it never reports itself stale.
    write_atomic("dashboard/today.html", render_home(
        build_view(plan, progress, syllabus, streaks, heartbeat, today),
        StaticLinks()))

    write_atomic("state/last-daily-run.json",
                 json.dumps(heartbeat, indent=2) + "\n")

    print(json.dumps({"outcome": outcome, "date": today,
                      "units": [lec["id"] for lec in plan.get("lectures", [])],
                      "due": plan.get("due_count", 0)}))
    return 0


def main(argv=None):
    """Run the build, and make a crash visible instead of silent.

    The scheduled task runs this under pythonw.exe, which has no console and
    discards stderr, so an unhandled exception would leave no trace anywhere
    -- the exact silent-death shape that hid the previous automation's
    failure for seven weeks. The heartbeat is the one channel guaranteed to
    be read, so a crash writes its own heartbeat with outcome "failed", and
    check_daily_liveness.py treats any outcome outside HEALTHY_OUTCOMES as
    stale. A heartbeat dated today is not on its own evidence of health.
    """
    try:
        return _build(argv)
    except Exception as exc:  # noqa: BLE001 - the point is to catch everything
        try:
            write_atomic("state/last-daily-run.json", json.dumps({
                "date": date.today().isoformat(),
                "outcome": "failed",
                "generated": datetime.now().isoformat(timespec="seconds"),
                "error": "%s: %s" % (type(exc).__name__, exc),
                "units": [],
                "due_count": 0,
            }, indent=2) + "\n")
        except OSError:
            pass    # nothing left to do; the missing heartbeat still reads stale
        try:
            # Retract the static page too. Left alone it is yesterday's, and it
            # carries yesterday's healthy banner, so the offline front door
            # would keep offering yesterday's lectures as today's work while
            # the heartbeat next to it said "failed".
            write_atomic("dashboard/today.html", render_unbuilt_page(
                date.today().isoformat(),
                "The builder ran and failed: %s: %s."
                % (type(exc).__name__, exc)))
        except OSError:
            pass
        print("daily.py: build failed - %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
