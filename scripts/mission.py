"""mission.py — gate 8: each lesson quotes its unit's mission_link verbatim.

The mission strip is the one place a lesson makes a claim on behalf of the
curriculum rather than the textbook, so it is quoted from syllabus.yaml and
not paraphrased. Where the syllabus strip is wrong, LESSON-GUIDE requires the
lesson to quote it anyway and refute it in the body; softening the quotation
to make it true is what this gate exists to prevent.

Promoted into the repo 2026-08-21 from scratchpad, with the defect the S2 plan
recorded against it repaired:

  > The script derives the unit id from the filename with `([a-z0-9]+-\\d+)\\.html$`;
  > `mission_negctl.html` does not match, so `re.search(...)` returns `None` and
  > the script raises `AttributeError` at line 7 **before the mission strip is
  > ever compared**. Exit 1 came from a traceback, not a verdict.

A non-zero exit is not a watched failure. Every path that cannot reach a
verdict now says so and exits 2; exit 1 means a strip was compared and differed.

  python scripts/mission.py <lesson_html_path> [...]
  python scripts/mission.py --known-failing curriculum/mission-drift.txt <path> [...]
  python scripts/mission.py --selftest

Exit 0 clean, 1 on a real mismatch, 2 when no verdict could be reached.

--known-failing is a RATCHET, not a suppression list. Run over the corpus for
the first time, this gate failed 15 of 81 lessons; wiring it non-blocking until
those are repaired is how the promotion of these scripts came to be deferred
three times already. So the listed units are excused from failing, and a listed
unit that starts PASSING fails the run until it is struck off. The list can
only shrink, and it cannot rot quietly: the state "repaired but still listed"
is the one an ordinary allowlist hides, and it is the state that turns an
allowlist into permanent silence.
"""
import html as html_mod
import os
import re
import sys

import yaml

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console (cf. srs/scheduler.py)
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYLLABUS = os.path.join(REPO, "curriculum", "syllabus.yaml")

UNIT_ID = re.compile(r"([a-z]+\d*-\d+)\.html$")
MISSION_P = re.compile(r'<p class="mission">(.*?)</p>', re.S)
PREFIX = re.compile(r"^Why this matters for the mission:\s*")


def normalise(text):
    """Whitespace-normalise so the lesson's line wrapping cannot fail the gate.

    Wrapping sensitivity is a defect this project has already paid for once, in
    check_lesson_coverage.py's REF_PATTERN: the citation was well formed and it
    was the comparison that broke on a newline. Same repair here — normalise
    both sides, compare the content.
    """
    return re.sub(r"\s+", " ", text).strip()


def unit_id_for(path):
    """Unit id from the lesson filename, or None. Never raises — a filename
    that does not name a unit is a usage error with a message, not a traceback
    that a caller could mistake for a verdict."""
    m = UNIT_ID.search(path.replace("\\", "/"))
    return m.group(1) if m else None


def strip_of(doc):
    """The lesson's mission strip, tags removed, prefix removed, normalised.
    None means the lesson has no `<p class="mission">` at all — a different
    finding from a strip that is present and wrong, and reported as such."""
    m = MISSION_P.search(doc)
    if not m:
        return None
    text = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
    return normalise(PREFIX.sub("", text.strip()))


def lesson_path(uid):
    """Where a unit's lesson lives: lessons/<module>/<uid>.html."""
    return os.path.join(REPO, "lessons", uid.rsplit("-", 1)[0], uid + ".html")


def load_units(path=SYLLABUS):
    with open(path, encoding="utf-8") as f:
        return {u["id"]: u for u in yaml.safe_load(f)["units"]}


def check(path, units):
    """Print one verdict row. Returns 0 pass, 1 fail, 2 no verdict possible."""
    uid = unit_id_for(path)
    if uid is None:
        print("ERROR %s: filename does not name a unit (expected <module>-<nn>.html)"
              % os.path.basename(path))
        return 2
    if uid not in units:
        print("ERROR %s: no unit %r in %s" % (os.path.basename(path), uid, SYLLABUS))
        return 2
    if "mission_link" not in units[uid]:
        print("ERROR %s: unit %r has no mission_link in the syllabus" % (path, uid))
        return 2

    want = normalise(units[uid]["mission_link"])
    with open(path, encoding="utf-8") as f:
        got = strip_of(f.read())

    if got is None:
        print("FAIL %s mission strip verbatim" % uid)
        print("  want: %r" % want)
        print("  got : <no <p class=\"mission\"> in the lesson>")
        return 1
    if got != want:
        print("FAIL %s mission strip verbatim" % uid)
        print("  want: %r" % want)
        print("  got : %r" % got)
        return 1
    print("PASS %s mission strip verbatim" % uid)
    return 0


def selftest():
    """Watched failures, built on synthetic strips so the control does not
    depend on any unit's current syllabus text."""
    total = [0]
    fails = []

    def check_one(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    # The repaired defect: a filename that names no unit must reach a verdict
    # path that SAYS so, not raise before the comparison.
    check_one("a filename that names no unit returns None, does not raise",
              unit_id_for("mission_negctl.html") is None)
    check_one("a normal lesson filename is parsed",
              unit_id_for(r"lessons\aa\aa-01.html") == "aa-01")
    check_one("a module with digits in its name is parsed (an2, tda1, at2)",
              unit_id_for("lessons/tda1/tda1-09.html") == "tda1-09")

    body = '<p class="mission">Why this matters for the mission: %s</p>'
    check_one("the prefix is stripped",
              strip_of(body % "Persistent homology needs this.")
              == "Persistent homology needs this.")
    check_one("tags inside the strip are removed",
              strip_of('<p class="mission">a <em>b</em> c</p>') == "a b c")
    check_one("entities are unescaped",
              strip_of('<p class="mission">R&nbsp;&amp;&nbsp;D</p>')
              == normalise("R\xa0&\xa0D"))
    check_one("line wrapping in the lesson does not change the strip",
              strip_of('<p class="mission">one\n   two</p>') == "one two")
    check_one("a lesson with no mission strip yields None, distinctly from ''",
              strip_of("<p>no strip here</p>") is None)

    # The watched failure the S2 plan built by hand: a shipped strip with four
    # words appended must be reported as a mismatch, not tolerated.
    want = "Persistent homology needs this."
    check_one("four words appended to the strip is a mismatch",
              strip_of(body % (want + " and a bit more")) != normalise(want))
    check_one("an exactly-quoted strip matches",
              strip_of(body % want) == normalise(want))
    check_one("a strip differing only in whitespace still matches",
              strip_of(body % "Persistent   homology\tneeds this.") == normalise(want))
    check_one("a strip differing by one character is a mismatch",
              strip_of(body % "Persistent homology needs these.") != normalise(want))

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def load_known_failing(path):
    """Unit ids excused from failing, one per line; '#' starts a comment."""
    ids = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                ids.add(line)
    return ids


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()

    known, listfile = set(), None
    if len(argv) >= 2 and argv[0] == "--known-failing":
        listfile = argv[1]
        known = load_known_failing(listfile)
        argv = argv[2:]

    if not argv:
        print("usage: mission.py [--known-failing <file>] <lesson_html_path> [...]"
              " | --selftest")
        return 2

    units = load_units()
    rc = 0
    seen = set()
    for path in argv:
        uid = unit_id_for(path)
        if uid in known:
            # Suppress the verdict row's effect on rc, but still run it, so the
            # stale case below is decided by a real comparison.
            r = check(path, units)
            seen.add(uid)
            if r == 0:
                print("STALE %s passes now — strike it from %s" % (uid, listfile))
                rc = 1
            elif r == 2:
                return 2
            else:
                print("KNOWN-FAIL %s (listed in %s)" % (uid, listfile))
            continue
        r = check(path, units)
        if r == 2:
            return 2
        rc = rc or r

    # A listed unit whose lesson no longer exists is the same rot in another
    # form: the entry outlives the thing it excused. Resolved against disk
    # rather than against this invocation's arguments, so running the gate on
    # one lesson does not accuse every other entry of being stale.
    for uid in sorted(known - seen):
        if not os.path.exists(lesson_path(uid)):
            print("STALE %s is listed in %s but has no lesson at %s"
                  % (uid, listfile, lesson_path(uid)))
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
