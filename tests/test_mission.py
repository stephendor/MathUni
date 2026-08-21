"""Gate 8, and the ratchet that lets it be a hard gate while 15 units still fail."""
import os

import pytest

from scripts.mission import (load_known_failing, main, normalise, strip_of,
                             unit_id_for)


# --- the recorded defect: a crash is not a verdict -------------------------

def test_a_filename_that_names_no_unit_does_not_raise():
    """The S2 plan found the inherited negative control was not a control:
    mission_negctl.html failed the filename regex, so re.search(...).group(1)
    raised AttributeError before the strip was ever compared. Exit 1 came from
    a traceback. This is that repair."""
    assert unit_id_for("mission_negctl.html") is None
    assert unit_id_for("negctl.html") is None


def test_a_filename_that_names_no_unit_exits_2_not_1(tmp_path, capsys):
    """2 means no verdict was reached; 1 means a strip was compared and
    differed. Collapsing them is how a crash gets counted as a caught defect."""
    p = tmp_path / "mission_negctl.html"
    p.write_text('<p class="mission">anything</p>', encoding="utf-8")
    assert main([str(p)]) == 2
    assert "does not name a unit" in capsys.readouterr().out


def test_lesson_filenames_are_parsed_including_modules_with_digits():
    assert unit_id_for(r"lessons\aa\aa-01.html") == "aa-01"
    assert unit_id_for("lessons/tda1/tda1-09.html") == "tda1-09"
    assert unit_id_for("lessons/an2/an2-03.html") == "an2-03"


# --- the comparison --------------------------------------------------------

def test_prefix_and_tags_are_stripped():
    assert strip_of('<p class="mission">Why this matters for the mission: '
                    "A <em>b</em> c.</p>") == "A b c."


def test_line_wrapping_does_not_change_the_verdict():
    """The wrapping-sensitivity defect already paid for once in
    check_lesson_coverage.py's REF_PATTERN. Normalise, then compare."""
    assert strip_of('<p class="mission">one\n    two</p>') == "one two"


def test_a_missing_strip_is_distinct_from_an_empty_one():
    assert strip_of("<p>no strip</p>") is None
    assert strip_of('<p class="mission"></p>') == ""


def test_four_words_appended_is_a_mismatch():
    """The watched failure the S2 plan built by hand, as a test."""
    want = normalise("Persistent homology needs this.")
    body = '<p class="mission">%s</p>'
    assert strip_of(body % want) == want
    assert strip_of(body % (want + " and a bit more")) != want
    assert strip_of(body % "Persistent homology needs these.") != want


# --- the ratchet -----------------------------------------------------------

def test_known_failing_list_ignores_comments_and_blanks(tmp_path):
    f = tmp_path / "drift.txt"
    f.write_text("# a comment\n\naa-00\npw-03  # trailing\n", encoding="utf-8")
    assert load_known_failing(str(f)) == {"aa-00", "pw-03"}


def test_a_listed_unit_that_fails_does_not_fail_the_run(capsys):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    drift = os.path.join(repo, "curriculum", "mission-drift.txt")
    lesson = os.path.join(repo, "lessons", "aa", "aa-00.html")
    assert main(["--known-failing", drift, lesson]) == 0
    assert "KNOWN-FAIL aa-00" in capsys.readouterr().out


def test_a_listed_unit_that_passes_FAILS_the_run(tmp_path, capsys):
    """The ratchet. An ordinary allowlist is silent in exactly the state that
    matters — repaired but still listed — and that silence is what turns it
    into permanent suppression. Here the list can only shrink."""
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    passing = os.path.join(repo, "lessons", "at1", "at1-03.html")
    f = tmp_path / "drift.txt"
    f.write_text("at1-03\n", encoding="utf-8")
    assert main(["--known-failing", str(f), passing]) == 1
    assert "STALE at1-03 passes now" in capsys.readouterr().out


def test_an_entry_whose_lesson_no_longer_exists_FAILS_the_run(tmp_path, capsys):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    real = os.path.join(repo, "lessons", "aa", "aa-00.html")
    f = tmp_path / "drift.txt"
    f.write_text("aa-00\nzz-99\n", encoding="utf-8")
    assert main(["--known-failing", str(f), real]) == 1
    assert "STALE zz-99" in capsys.readouterr().out


def test_checking_one_lesson_does_not_accuse_other_entries_of_being_stale(capsys):
    """Resolved against disk, not against this invocation's arguments —
    otherwise the gate is unusable on a single file during authoring."""
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    drift = os.path.join(repo, "curriculum", "mission-drift.txt")
    lesson = os.path.join(repo, "lessons", "aa", "aa-00.html")
    main(["--known-failing", drift, lesson])
    out = capsys.readouterr().out
    assert "STALE" not in out


def test_every_listed_unit_still_exists_and_still_fails():
    """Binds the checked-in list to reality, so it cannot rot between runs."""
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    drift = os.path.join(repo, "curriculum", "mission-drift.txt")
    listed = sorted(load_known_failing(drift))
    assert listed, "the drift list is empty — if gate 8 is clean, delete the file"
    for uid in listed:
        path = os.path.join(repo, "lessons", uid.rsplit("-", 1)[0], uid + ".html")
        assert os.path.exists(path), "%s is listed but has no lesson" % uid


# --- Codex review of PR #20 ------------------------------------------------

def test_a_valid_unit_with_no_lesson_file_exits_2_not_1(capsys):
    """pw-04 is a real syllabus unit whose lesson is not written yet. The
    unguarded open() raised FileNotFoundError, and the traceback exited 1 —
    the code reserved for "a strip was compared and differed". A filesystem
    failure must never be readable as a gate verdict."""
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert main([os.path.join(repo, "lessons", "pw", "pw-04.html")]) == 2
    assert "cannot read" in capsys.readouterr().out


def test_an_unchanged_or_shrunk_drift_list_has_no_additions(tmp_path):
    from scripts.mission import additions_against
    base = tmp_path / "base.txt"
    base.write_text("# header\naa-00\npw-03\ntda2-02\n", encoding="utf-8")
    assert additions_against(str(base), {"aa-00", "pw-03", "tda2-02"}) == (set(), True)
    assert additions_against(str(base), {"aa-00"}) == (set(), True)
    assert additions_against(str(base), set()) == (set(), True)


def test_a_grown_drift_list_is_caught():
    """The ratchet's whole claim. The two stale checks only ever let the list
    SHRINK; nothing stopped a branch adding a freshly-drifted unit and going
    green. Verified before the fix: a lesson broken on purpose, then listed,
    exited 0."""
    from scripts.mission import additions_against
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "base.txt")
        with open(base, "w", encoding="utf-8") as f:
            f.write("aa-00\npw-03\n")
        assert additions_against(base, {"aa-00", "pw-03", "an-03"}) == ({"an-03"}, True)
        # A swap keeps the count identical and must still be caught.
        assert additions_against(base, {"aa-00", "an-03"}) == ({"an-03"}, True)


def test_a_missing_baseline_is_reported_as_missing_not_as_empty(tmp_path):
    """Treating an absent baseline as the empty set would make every entry an
    addition on the commit that introduces the list — and, worse, would make a
    lost baseline look like a clean comparison."""
    from scripts.mission import additions_against
    added, existed = additions_against(str(tmp_path / "nope.txt"), {"aa-00"})
    assert (added, existed) == (set(), False)


def test_growth_check_end_to_end_fails_the_run(tmp_path, capsys):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = tmp_path / "base.txt"
    base.write_text("aa-00\n", encoding="utf-8")
    grown = tmp_path / "grown.txt"
    grown.write_text("aa-00\npw-03\n", encoding="utf-8")
    rc = main(["--known-failing", str(grown), "--baseline", str(base),
               os.path.join(repo, "lessons", "aa", "aa-00.html")])
    assert rc == 1
    assert "GREW pw-03" in capsys.readouterr().out
