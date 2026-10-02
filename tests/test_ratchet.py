"""Controls for scripts/ratchet.py, the one allowlist ratchet.

The helper holds three rules: a listed entry that passes is stale, a listed
entry whose subject is gone is stale, and an entry ADDED since the base ref
fails. Each has a control that violates it in the forbidden direction, and a
positive control that proves the check is quiet when nothing is wrong.
"""
import pytest

from scripts.ratchet import (Ratchet, Unreadable, Usage, additions_against,
                             load_known_failing)


def _ratchet(tmp_path, base, current):
    listfile = tmp_path / "list.txt"
    if current is not None:
        listfile.write_text("\n".join(current) + "\n", encoding="utf-8")
    argv = ["--known-failing", str(listfile)]
    if base is not None:
        baseline = tmp_path / "base.txt"
        baseline.write_text("\n".join(base) + "\n", encoding="utf-8")
        argv += ["--baseline", str(baseline)]
    ratchet, rest = Ratchet.from_argv(argv + ["x"], label="test list",
                                      remedy="Fix it.", subject="thing")
    assert rest == ["x"]
    return ratchet


def _run(ratchet, verdicts, exists=lambda uid: True):
    lines = []
    rc = ratchet.check(verdicts, exists=exists, out=lines.append,
                       note=lines.append)
    return rc, "\n".join(lines)


def test_a_grown_list_fails(tmp_path):
    rc, out = _run(_ratchet(tmp_path, ["a"], ["a", "b"]), {"a": 1, "b": 1})
    assert rc == 1 and "GREW b" in out


def test_a_swap_that_keeps_the_count_fails(tmp_path):
    rc, out = _run(_ratchet(tmp_path, ["a"], ["b"]), {"b": 1})
    assert rc == 1 and "GREW b" in out


def test_a_stale_entry_that_now_passes_fails(tmp_path):
    rc, out = _run(_ratchet(tmp_path, ["a", "b"], ["a", "b"]), {"a": 1, "b": 0})
    assert rc == 1 and "STALE b passes now" in out


def test_a_stale_entry_whose_subject_is_gone_fails(tmp_path):
    rc, out = _run(_ratchet(tmp_path, ["a", "b"], ["a", "b"]), {"a": 1},
                   exists=lambda uid: uid != "b")
    assert rc == 1 and "STALE b is listed" in out and "has no thing" in out


def test_a_shrunk_list_whose_entries_still_fail_passes(tmp_path):
    """Positive control: without it, a check returning 1 for everything would pass the above."""
    rc, out = _run(_ratchet(tmp_path, ["a", "b"], ["a"]), {"a": 1})
    assert rc == 0 and "no additions" in out


def test_an_unjudged_entry_that_still_exists_is_not_accused(tmp_path):
    """Running on one subject must not call every other entry stale."""
    rc, _ = _run(_ratchet(tmp_path, ["a", "b"], ["a", "b"]), {"a": 1})
    assert rc == 0


def test_a_deleted_list_is_refused_when_the_baseline_had_one(tmp_path):
    rc, out = _run(_ratchet(tmp_path, ["a"], None), {})
    assert rc == 1 and "DELETED" in out


def test_no_baseline_file_is_the_introducing_commit(tmp_path):
    ratchet = _ratchet(tmp_path, None, ["a"])
    ratchet.baseline = str(tmp_path / "missing-base.txt")
    rc, out = _run(ratchet, {"a": 1})
    assert rc == 0 and "introduces the list" in out


def test_growth_and_stale_cannot_be_adopted_separately(tmp_path):
    """check() has no way to run one rule: the stale rules' inputs are required."""
    ratchet = _ratchet(tmp_path, ["a"], ["a"])
    with pytest.raises(TypeError):
        ratchet.check({"a": 1})
    with pytest.raises(TypeError):
        ratchet.check(exists=lambda uid: True)


def test_baseline_without_a_list_is_a_usage_error():
    with pytest.raises(Usage):
        Ratchet.from_argv(["--baseline", "b.txt"], label="l", remedy="r")


def test_an_unreadable_list_or_baseline_raises_unreadable(tmp_path):
    with pytest.raises(Unreadable):
        load_known_failing(str(tmp_path))
    with pytest.raises(Unreadable):
        additions_against(str(tmp_path), {"a"})


def test_comments_and_blanks_are_ignored(tmp_path):
    f = tmp_path / "l.txt"
    f.write_text("# c\n\naa-00\npw-03  # t\n", encoding="utf-8")
    assert load_known_failing(str(f)) == {"aa-00", "pw-03"}
