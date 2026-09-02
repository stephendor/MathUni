from scripts.check_daily_liveness import (
    FRESH,
    HEALTHY_OUTCOMES,
    STALE,
    UNKNOWN,
    verdict,
)

TODAY = "2026-08-31"


def code(beat, today=TODAY, max_age=0):
    return verdict(beat, today, max_age)[0]


def message(beat, today=TODAY, max_age=0):
    return verdict(beat, today, max_age)[1]


# --- the fresh case ---------------------------------------------------------

def test_a_heartbeat_from_today_is_fresh():
    assert code({"date": TODAY, "outcome": "built"}) == FRESH


def test_a_rest_day_counts_as_fresh():
    """The builder runs every day; a rest day changes what it writes, not
    whether it ran. Treating rest as stale would cry wolf twice a week."""
    assert code({"date": TODAY, "outcome": "rest"}) == FRESH


def test_already_built_counts_as_fresh():
    assert code({"date": TODAY, "outcome": "already-built"}) == FRESH


# --- the stale case, which is the whole point -------------------------------

def test_yesterdays_heartbeat_is_stale_by_default():
    assert code({"date": "2026-08-30", "outcome": "built"}) == STALE


def test_the_seven_week_outage_would_have_been_caught():
    """The real failure: last real activity 2026-07-10, discovered 2026-08-31."""
    assert code({"date": "2026-07-10", "outcome": "built"}) == STALE
    assert "52 days ago" in message({"date": "2026-07-10", "outcome": "built"})


def test_a_missing_heartbeat_is_stale_not_unknown():
    """Absence IS the finding. A builder that never ran and one that stopped
    running are the same problem; reporting 'unknown' for the first is exactly
    how the original failure stayed invisible."""
    assert code({}) == STALE
    assert code(None) == STALE


def test_a_heartbeat_without_a_date_is_stale():
    assert code({"outcome": "built"}) == STALE


def test_tolerance_can_be_widened_but_defaults_to_strict():
    beat = {"date": "2026-08-29", "outcome": "built"}
    assert code(beat) == STALE
    assert code(beat, max_age=2) == FRESH
    assert code(beat, max_age=1) == STALE


def test_singular_day_reads_correctly():
    assert "1 day ago" in message({"date": "2026-08-30", "outcome": "built"})


# --- unknown is reserved for "the check could not run" ----------------------

def test_an_unparseable_date_is_unknown_not_stale():
    """A broken check must not masquerade as a broken builder."""
    assert code({"date": "not-a-date"}) == UNKNOWN
    assert code({"date": 20260831}) == UNKNOWN


def test_a_future_heartbeat_is_unknown():
    """Clock skew or a bad --date; either way the check cannot judge."""
    assert code({"date": "2026-09-05", "outcome": "built"}) == UNKNOWN


# --- negative control -------------------------------------------------------

def test_the_check_distinguishes_all_three_verdicts():
    """A liveness check that cannot return every one of its codes is a check
    with a branch nobody has watched execute.
    """
    seen = {
        code({"date": TODAY, "outcome": "built"}),
        code({"date": "2026-01-01", "outcome": "built"}),
        code({"date": "nonsense"}),
    }
    assert seen == {FRESH, STALE, UNKNOWN}


def test_exit_codes_are_distinct_and_zero_means_only_fresh():
    assert len({FRESH, STALE, UNKNOWN}) == 3
    assert FRESH == 0, "only a fresh heartbeat may exit 0"
    assert STALE and UNKNOWN, "every failure code must be non-zero"


# --- a heartbeat dated today is not on its own evidence of health -----------

def test_a_crashed_build_is_stale_even_though_it_is_dated_today():
    """daily.py runs under pythonw, which discards stderr, so it writes its own
    failure heartbeat. If the check looked only at the date, a build that
    crashed every morning would read fresh every morning -- the original
    failure again, one layer down.
    """
    assert code({"date": TODAY, "outcome": "failed", "error": "boom"}) == STALE


def test_an_unrecognised_outcome_is_stale_rather_than_assumed_good():
    assert code({"date": TODAY, "outcome": "who-knows"}) == STALE
    assert code({"date": TODAY}) == STALE, "a missing outcome is not a good one"


def test_the_healthy_outcomes_are_exactly_what_daily_py_writes():
    """Drift here is silent: a new outcome string in daily.py that nobody adds
    to this tuple turns every run stale, and one wrongly added hides crashes.
    """
    import pathlib
    src = (pathlib.Path(__file__).resolve().parents[1] / "scripts" / "daily.py"
           ).read_text(encoding="utf-8")
    written = {o for o in ("built", "already-built", "rest", "failed")
               if '"%s"' % o in src}
    assert written == {"built", "already-built", "rest", "failed"}
    assert set(HEALTHY_OUTCOMES) == written - {"failed"}

def test_a_heartbeat_with_a_windows_bom_still_reads(tmp_path):
    """PowerShell's Set-Content -Encoding UTF8 writes a BOM. Without utf-8-sig
    a hand-edited heartbeat reports "unreadable" and the check goes blind.
    """
    from scripts.check_daily_liveness import load_heartbeat

    path = tmp_path / "hb.json"
    path.write_text('{"date": "2026-09-01", "outcome": "built"}',
                    encoding="utf-8-sig")
    assert load_heartbeat(str(path))["date"] == "2026-09-01"


def test_a_plain_utf8_heartbeat_is_unaffected(tmp_path):
    from scripts.check_daily_liveness import load_heartbeat

    path = tmp_path / "hb.json"
    path.write_text('{"date": "2026-09-01", "outcome": "rest"}', encoding="utf-8")
    assert load_heartbeat(str(path))["outcome"] == "rest"


def test_a_non_object_heartbeat_is_unknown_not_a_traceback():
    """Valid JSON that is not an object has no .get; without this the
    check dies with an AttributeError instead of returning a verdict."""
    for shape in ([1, 2], "a string", 42, True):
        assert code(shape) == UNKNOWN, shape


def test_the_non_object_message_names_the_shape():
    assert "list" in message([1, 2])

