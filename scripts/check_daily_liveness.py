"""check_daily_liveness.py — has the day builder actually run?

The `NexusCollege Morning` task failed every study morning from roughly
2026-07-11 to 2026-08-31 while `schtasks /Query` reported `Status: Ready` and
`Last Run Time` ticked forward. Nothing anywhere asserted "a day was built
today", so seven weeks of failure produced no signal at all. This is the
assertion that was missing.

It reads the heartbeat `scripts/daily.py` writes and turns it into an exit
code, so a scheduler, a shell prompt, or a person can ask the question:

  0  fresh   — a day was built (or a rest day recorded) within the window
  1  STALE   — the builder has not run; this is a verdict, act on it
  2  unknown — the check could not run at all (wrong cwd, unreadable file)

**A missing heartbeat is exit 1, not exit 2.** Absence is the finding here, not
an inability to reach one: a builder that has never run and a builder that has
stopped running are the same problem wearing different clothes. Conflating
"nothing to report" with "nothing happened" is precisely what let the original
failure hide, and `scripts/gate.py` states the same rule for lessons — absence
of a check is not a pass.

A rest day still counts as fresh. The builder runs every day; what a rest day
changes is that the plan it writes is empty, not that it skipped.

  python scripts/check_daily_liveness.py [--max-age-days N] [--json] [--date D]
"""
import argparse
import json
import os
import sys
from datetime import date

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HEARTBEAT = "state/last-daily-run.json"

FRESH, STALE, UNKNOWN = 0, 1, 2

# Outcomes daily.py writes when it actually completed. Anything else -- most
# importantly "failed", which it writes from its own top-level handler -- is
# a heartbeat dated today that must NOT read as healthy. A run that crashed
# still touched the file, so date alone cannot tell the two apart.
HEALTHY_OUTCOMES = ("built", "already-built", "rest")


def verdict(heartbeat, today, max_age_days=0):
    """(exit_code, message, age_in_days_or_None) for a heartbeat dict.

    `heartbeat` is whatever was on disk: {} for a missing file.
    """
    if heartbeat is None or not heartbeat:
        return (STALE, "no heartbeat at all — the day builder has never run "
                       "here, or state/last-daily-run.json was removed", None)

    stamped = heartbeat.get("date")
    if not stamped:
        return (STALE, "heartbeat has no date field; treating as never run", None)

    try:
        age = (date.fromisoformat(today) - date.fromisoformat(stamped)).days
    except (TypeError, ValueError):
        # An unparseable date is a broken check, not a broken builder.
        return (UNKNOWN, "heartbeat date %r is not an ISO date" % (stamped,), None)

    if age < 0:
        return (UNKNOWN, "heartbeat is dated %s, in the future relative to %s"
                % (stamped, today), age)

    outcome = heartbeat.get("outcome", "?")
    if outcome not in HEALTHY_OUTCOMES:
        return (STALE, "the builder ran on %s and did not finish (outcome: %s)"
                % (stamped, outcome), age)

    if age <= max_age_days:
        return (FRESH, "built %s (outcome: %s)" % (stamped, outcome), age)

    return (STALE, "last built %s — %d day%s ago; the day builder is not running"
            % (stamped, age, "" if age == 1 else "s"), age)


def load_heartbeat(path=HEARTBEAT):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Assert the day builder has run.")
    ap.add_argument("--max-age-days", type=int, default=0,
                    help="days of tolerance before the heartbeat reads stale")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not os.path.exists("curriculum/syllabus.yaml"):
        print("check_daily_liveness.py: run from the repo root", file=sys.stderr)
        return UNKNOWN

    try:
        beat = load_heartbeat()
    except (OSError, ValueError) as exc:
        print("check_daily_liveness.py: heartbeat unreadable — %s" % exc,
              file=sys.stderr)
        return UNKNOWN

    code, message, age = verdict(beat, args.date, args.max_age_days)
    label = {FRESH: "fresh", STALE: "STALE", UNKNOWN: "unknown"}[code]
    if args.json:
        print(json.dumps({"status": label, "message": message, "age_days": age,
                          "checked": args.date}, indent=1))
    else:
        print("%s: %s" % (label, message), file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
