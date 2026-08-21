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
  python scripts/mission.py --known-failing <list> --baseline <base-ref-copy> <path>...
  python scripts/mission.py --selftest

Exit 0 clean, 1 on a real mismatch, 2 when no verdict could be reached.

--known-failing is a RATCHET, not a suppression list. Run over the corpus for
the first time, this gate failed 15 of 81 lessons; wiring it non-blocking until
those are repaired is how the promotion of these scripts came to be deferred
three times already. So the listed units are excused from failing, and:

  * a listed unit that starts PASSING fails the run until it is struck off —
    "repaired but still listed" is the state an ordinary allowlist hides, and
    the one that turns an allowlist into permanent silence;
  * a listed unit whose lesson no longer exists fails the run;
  * and, with --baseline, a unit ADDED to the list since the base ref fails the
    run. Without that third rule the first two only ever let the list shrink
    while nothing stopped it growing, so "the list can only shrink" was a claim
    about author discipline rather than a property of the gate. It is now the
    property it was described as.
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

# Anchored to the WHOLE basename. End-anchoring alone let `draft-aa-01.html`
# and `copy-of-pw-01.html` be treated as units aa-01 and pw-01 and pass gate 8,
# while check_id_consistency.py skips a nonconforming stem rather than calling
# it an orphan — so a stray extra lesson could clear every integrity check the
# workflow runs. (Codex review of PR #20, second round.)
UNIT_ID = re.compile(r"^([a-z]+\d*-\d+)\.html$")
MISSION_P = re.compile(r'<p class="mission">(.*?)</p>', re.S)
PREFIX = re.compile(r"^Why this matters for the mission:\s*")
# A commented-out strip renders nothing, but a raw regex still finds it, so
# gate 8 reported PASS on a lesson displaying no mission paragraph at all.
# lesson_lint.py could not close it either — its structure counter scans
# comments as raw text too, so the lesson cleared both hard checks.
# (Codex review of PR #20, fourth round.)
COMMENT = re.compile(r"<!--.*?-->", re.S)


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
    m = UNIT_ID.match(os.path.basename(path.replace("\\", "/")))
    return m.group(1) if m else None


def strips_of(doc):
    """EVERY mission strip in the lesson, cleaned and normalised.

    All of them, not the first. Comparing only the first let a lesson keep an
    exact strip at the top and carry a second, divergent mission claim further
    down while gate 8 exited 0 — and lesson_lint.py only requires the count to
    be at least one, so nothing else closed it. A duplicated section is the
    obvious way to end up in that state by accident.
    (Codex review of PR #20, second round.)
    """
    out = []
    for m in MISSION_P.finditer(COMMENT.sub("", doc)):
        text = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        out.append(normalise(PREFIX.sub("", text.strip())))
    return out


def strip_of(doc):
    """The lesson's single mission strip, or None if it has none.

    Raises nothing on a duplicate — check() reports that as its own finding,
    since "two strips" and "one wrong strip" are different defects.
    """
    strips = strips_of(doc)
    return strips[0] if strips else None


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
    try:
        with open(path, encoding="utf-8") as f:
            strips = strips_of(f.read())
        got = strips[0] if strips else None
    except OSError as e:
        # A missing or unreadable file is NOT a verdict. Letting OSError escape
        # gave a traceback and process exit 1 — the code this script reserves
        # for "a strip was compared and differed" — so an authoring wrapper
        # could read a filesystem failure as a caught defect. `pw-04` is a real
        # syllabus unit with no lesson yet, and it exited 1.
        # (Codex review of PR #20.)
        print("ERROR %s: cannot read %s: %s" % (uid, path, e))
        return 2

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
    if len(strips) > 1:
        # The first strip is exact, and there is another one. A second strip is
        # a second claim on behalf of the curriculum, and the gate exists to
        # stop exactly that being made unchecked.
        print("FAIL %s mission strip verbatim" % uid)
        print("  the lesson carries %d mission strips; there must be one."
              % len(strips))
        for i, s in enumerate(strips[1:], 2):
            print("  strip %d: %r" % (i, s))
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
    # Codex round 2: end-anchoring alone let a stray file borrow a unit id.
    check_one("a prefixed filename is NOT read as a unit id",
              unit_id_for("lessons/aa/draft-aa-01.html") is None)
    check_one("...nor is a copy",
              unit_id_for("lessons/pw/copy-of-pw-01.html") is None)
    check_one("a real lesson path still parses after anchoring",
              unit_id_for("lessons/aa/aa-01.html") == "aa-01")

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
    # Codex round 2: comparing only the FIRST strip let a lesson keep an exact
    # one at the top and a divergent second claim further down.
    check_one("every mission strip is collected, not just the first",
              strips_of('<p class="mission">one</p><p class="mission">two</p>')
              == ["one", "two"])
    check_one("a single strip still yields exactly one",
              strips_of('<p class="mission">only</p>') == ["only"])
    # Codex round 4: a commented-out strip renders nothing.
    check_one("a commented-out strip does not count",
              strips_of('<!-- <p class="mission">hidden</p> -->') == [])
    check_one("a real strip beside a commented one is still found",
              strips_of('<p class="mission">real</p>'
                        '<!-- <p class="mission">hidden</p> -->') == ["real"])

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

    # The ratchet's growth rule. Codex review of PR #20 found that the two
    # stale checks only ever let the list shrink while nothing stopped it
    # growing: a lesson broken on purpose and then listed exited 0.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as d:
        base = os.path.join(d, "base.txt")
        with open(base, "w", encoding="utf-8") as f:
            f.write("# comment\naa-00\npw-03\n")
        check_one("an unchanged list has no additions",
                  additions_against(base, {"aa-00", "pw-03"}) == (set(), True))
        check_one("a SHRUNK list has no additions",
                  additions_against(base, {"aa-00"}) == (set(), True))
        check_one("a GROWN list is caught, and names what was added",
                  additions_against(base, {"aa-00", "pw-03", "an-03"})
                  == ({"an-03"}, True))
        check_one("a swap that keeps the count is still caught",
                  additions_against(base, {"aa-00", "an-03"}) == ({"an-03"}, True))
    check_one("a missing baseline is reported as missing, not as empty",
              additions_against(os.path.join(REPO, "no-such-baseline.txt"),
                                {"aa-00"}) == (set(), False))

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def load_known_failing(path):
    """Unit ids excused from failing, one per line; '#' starts a comment.

    A missing file is an EMPTY list, not an error, so the finished state can be
    reached at all — an earlier version raised FileNotFoundError before a single
    lesson was compared, which made the ratchet's own success state impossible
    to pass CI. A list that is absent excuses nothing, so the gate gets strictly
    stricter, and deleting the file cannot be used to escape it.

    But the file is nonetheless PERMANENT: the zero state is an empty list, not
    a deleted one. Deleting it would make the base ref lack the path, and
    "base has no list" is the one condition under which the growth check stands
    down — so a later branch could reintroduce the file alongside fresh
    mismatches and have them excused. main() refuses a deletion for exactly
    that reason. (Codex review of PR #20, rounds two and four.)
    """
    ids = set()
    if not os.path.exists(path):
        return ids
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                ids.add(line)
    return ids


def additions_against(baseline_path, current):
    """Ids in the current drift list that the baseline did not have.

    Without this the ratchet was a claim, not a mechanism. The stale checks
    catch a listed unit that starts passing and one whose lesson is gone — both
    of which make the list SHRINK — but nothing stopped a branch from adding a
    freshly-drifted unit to the list and going green. Verified: a lesson broken
    on purpose, then listed, exited 0. "The list can only shrink" was asserted
    in the commit message, the plan and the CI comment, and enforced nowhere.
    (Codex review of PR #20.)

    Returns (additions, baseline_existed). A baseline that does not exist is
    reported as such rather than silently treated as empty — on the commit that
    introduces the list there is nothing to compare against, and that must be
    visible instead of looking like a clean comparison.
    """
    if not os.path.exists(baseline_path):
        return set(), False
    return current - load_known_failing(baseline_path), True


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()

    known, listfile, baseline = set(), None, None
    while len(argv) >= 2 and argv[0] in ("--known-failing", "--baseline"):
        if argv[0] == "--known-failing":
            listfile = argv[1]
            known = load_known_failing(listfile)
        else:
            baseline = argv[1]
        argv = argv[2:]

    if baseline is not None:
        if listfile is None:
            print("ERROR --baseline needs --known-failing")
            return 2
        added, existed = additions_against(baseline, known)
        if existed and not os.path.exists(listfile):
            # The base ref has a list and this ref does not. Deleting it is the
            # one move that reopens the ratchet: with the path gone, every
            # later base also lacks it, "base has no list" stops meaning "the
            # introducing commit", and a branch can reintroduce the file with
            # fresh mismatches and have them excused.
            print("DELETED %s existed at the baseline and is gone here. The"
                  " drift list is permanent — empty it, do not delete it, or"
                  " the growth check can never distinguish a reintroduction"
                  " from the original rollout." % listfile)
            return 1
        if not existed:
            print("NOTE no baseline at %s — this is the commit that introduces"
                  " the list, so there is nothing it could have grown from"
                  % baseline)
        elif added:
            for uid in sorted(added):
                print("GREW %s was added to %s; the drift list is a ratchet and"
                      " may only shrink. Repair the lesson instead."
                      % (uid, listfile))
            return 1
        else:
            print("PASS drift list has no additions against %s" % baseline)

    if not argv:
        print("usage: mission.py [--known-failing <file>] [--baseline <file>]"
              " <lesson_html_path> [...] | --selftest")
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
