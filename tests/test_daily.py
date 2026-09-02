import ast
import json
import pathlib

from scripts.daily import (
    PLAN_HEADING,
    build_plan,
    is_study_day,
    pick_units,
    problem_candidates,
    render_session_md,
)

SCHEDULE = {"study_days": ["Mon", "Tue", "Thu", "Fri"]}

UNITS = [
    {"id": "pw-01", "module": "pw", "title": "Direct proof", "prereqs": [],
     "hook": "Hook pw-one.", "mission_link": "m", "resources": []},
    {"id": "pw-02", "module": "pw", "title": "Induction", "prereqs": ["pw-01"],
     "hook": "Dominoes, but the row is infinite.", "mission_link": "m", "resources": []},
    {"id": "la-02", "module": "la", "title": "Subspaces", "prereqs": ["la-01"],
     "hook": "Hook la-two.", "mission_link": "m", "resources": []},
    {"id": "an-02", "module": "an", "title": "Sequences", "prereqs": ["an-01"],
     "hook": "Hook an-two.", "mission_link": "m", "resources": []},
    {"id": "top-99", "module": "top", "title": "Way ahead", "prereqs": ["an-02"],
     "hook": "Hook locked.", "mission_link": "m", "resources": []},
]

SYL = {"modules": [{"id": "pw", "title": "Proof"}, {"id": "la", "title": "Linear Algebra"},
                   {"id": "an", "title": "Analysis"}, {"id": "top", "title": "Topology"}],
       "units": UNITS}

PROGRESS = {
    "pw-01": {"status": "mastered"},
    "pw-02": {"status": "unlocked"},
    "la-02": {"status": "unlocked"},
    "an-02": {"status": "in-progress"},
    "top-99": {"status": "locked"},
}

STATS = {"due_today": 12, "total": 66}
STREAKS = {"current": 3, "best": 3, "study_days": ["2026-07-10"]}

# 2026-08-31 is a Monday; 2026-09-02 is a Wednesday.
MONDAY = "2026-08-31"
WEDNESDAY = "2026-09-02"


# --- is_study_day -----------------------------------------------------------

def test_study_day_true_on_listed_weekday():
    assert is_study_day(SCHEDULE, MONDAY) is True


def test_study_day_false_on_unlisted_weekday():
    assert is_study_day(SCHEDULE, WEDNESDAY) is False


def test_study_day_does_not_use_locale_dependent_names():
    """Weekday abbreviations are a fixed table, not strftime('%a').

    strftime is locale-dependent; under a non-English Windows locale it would
    return e.g. 'Mo' and every day would silently become a rest day.
    """
    assert is_study_day({"study_days": ["Mon"]}, MONDAY) is True
    assert is_study_day({"study_days": []}, MONDAY) is False


# --- pick_units -------------------------------------------------------------

def test_picks_two_units_from_different_modules():
    picked = pick_units(UNITS, PROGRESS)
    assert len(picked) == 2
    assert len({u["module"] for u in picked}) == 2


def test_unlocked_preferred_over_in_progress():
    picked = pick_units(UNITS, PROGRESS)
    assert picked[0]["id"] in ("pw-02", "la-02")


def test_locked_units_never_picked():
    picked = pick_units(UNITS, PROGRESS)
    assert all(u["id"] != "top-99" for u in picked)


def test_falls_back_to_same_module_when_only_one_module_available():
    units = [UNITS[1], {"id": "pw-03", "module": "pw", "title": "Contradiction",
                        "prereqs": [], "hook": "h", "mission_link": "m", "resources": []}]
    progress = {"pw-02": {"status": "unlocked"}, "pw-03": {"status": "unlocked"}}
    picked = pick_units(units, progress)
    assert len(picked) == 2, "one available module must still yield a full day"


def test_returns_what_exists_when_fewer_than_two_candidates():
    picked = pick_units(UNITS, {"pw-02": {"status": "unlocked"}})
    assert len(picked) == 1


def test_returns_empty_when_nothing_studiable():
    assert pick_units(UNITS, {"top-99": {"status": "locked"}}) == []


def test_selection_is_deterministic():
    assert [u["id"] for u in pick_units(UNITS, PROGRESS)] == \
           [u["id"] for u in pick_units(UNITS, PROGRESS)]


def test_pick_units_does_not_mutate_progress():
    before = json.dumps(PROGRESS, sort_keys=True)
    pick_units(UNITS, PROGRESS)
    assert json.dumps(PROGRESS, sort_keys=True) == before


# --- problem_candidates -----------------------------------------------------

def test_problem_candidates_require_an_existing_set():
    got = problem_candidates(UNITS, PROGRESS, {}, available_sets={"pw-02"})
    assert got == ["pw-02"]


def test_unmastered_units_sort_before_passed_ones():
    mastery = {"pw-02": {"score": 0.9}}
    got = problem_candidates(UNITS, PROGRESS, mastery,
                             available_sets={"pw-02", "la-02", "an-02"})
    assert got.index("la-02") < got.index("pw-02")
    assert got.index("an-02") < got.index("pw-02")


def test_locked_units_are_not_problem_candidates():
    got = problem_candidates(UNITS, PROGRESS, {}, available_sets={"top-99", "pw-02"})
    assert "top-99" not in got


# --- build_plan -------------------------------------------------------------

def test_plan_carries_hook_verbatim_from_syllabus():
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS, available_sets={"pw-02"})
    hooks = [lec["hook"] for lec in plan["lectures"]]
    assert "Dominoes, but the row is infinite." in hooks


def test_plan_records_due_count_and_date():
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS, available_sets=set())
    assert plan["date"] == MONDAY
    assert plan["due_count"] == 12


def test_plan_on_rest_day_is_marked_rest():
    plan = build_plan(SYL, PROGRESS, STATS, WEDNESDAY, STREAKS, available_sets=set(),
                      schedule=SCHEDULE)
    assert plan["rest_day"] is True
    assert plan["lectures"] == []


def test_plan_never_reports_a_status_it_could_change():
    """daily.py is read-only over progress; update_unlocks owns status."""
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS, available_sets={"pw-02"})
    assert all(lec["status"] in ("unlocked", "in-progress") for lec in plan["lectures"])


# --- render_session_md ------------------------------------------------------

def test_session_md_uses_the_heading_today_resumes_from():
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS, available_sets={"pw-02"})
    md = render_session_md(plan)
    assert PLAN_HEADING in md


def test_session_md_leads_with_the_hook_not_a_definition():
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS, available_sets={"pw-02"})
    md = render_session_md(plan)
    assert plan["lectures"][0]["hook"] in md


def test_session_md_names_every_planned_unit():
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS, available_sets={"pw-02"})
    md = render_session_md(plan)
    for lec in plan["lectures"]:
        assert lec["id"] in md


def test_session_md_on_rest_day_says_so_without_inventing_work():
    plan = build_plan(SYL, PROGRESS, STATS, WEDNESDAY, STREAKS, available_sets=set(),
                      schedule=SCHEDULE)
    md = render_session_md(plan)
    assert "Rest day" in md
    assert "Lecture 1" not in md
# --- the Tier-0 property, enforced rather than asserted ---------------------

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_PACKAGES = ("scripts", "srs")

ALLOWED_IMPORTS = {"argparse", "json", "os", "sys", "datetime",  # stdlib
                   "scripts", "srs"}                             # repo
BANNED_IMPORTS = {"urllib", "http", "socket", "requests", "httpx", "subprocess",
                  "anthropic", "openai", "ollama"}


def _import_names(source):
    """Full dotted module names imported by a Python source string."""
    names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
            if node.module in REPO_PACKAGES:
                # `from srs import fsrs` names a module, not a symbol.
                names.update(node.module + "." + a.name for a in node.names)
    return names


def _import_roots(source):
    """Top-level module names only, which is what the ban is written against."""
    return {n.split(".")[0] for n in _import_names(source)}


def _import_closure(entry):
    """Every repo file reachable from `entry` by import, `entry` included.

    Checking daily.py alone would be a guard with a hole in it: daily.py
    imports scripts.home, so a network call added to home.py would put the
    day builder on the network while the direct check still passed. The
    property is about what daily.py can reach, so the walk has to be too.
    """
    seen, queue, out = set(), [entry], []
    while queue:
        path = queue.pop()
        if path in seen or not path.exists():
            continue
        seen.add(path)
        out.append(path)
        for name in _import_names(path.read_text(encoding="utf-8")):
            parts = name.split(".")
            if parts[0] in REPO_PACKAGES and len(parts) > 1:
                queue.append(ROOT.joinpath(*parts).with_suffix(".py"))
    return out


def _tier0_violations(source):
    roots = _import_roots(source)
    return (roots & BANNED_IMPORTS) | (roots - ALLOWED_IMPORTS)


def test_daily_imports_nothing_that_could_call_a_model_or_a_network():
    """daily.py must stay Tier 0: stdlib + repo only.

    The module docstring claims no model and no network. A claim in a
    docstring is self-attestation; this is the check that makes it a
    property. If someone later reaches for `requests`, `urllib`, or a
    subprocess to a provider CLI, the day builder stops being the thing that
    still works when a provider is down, and this is what says so.
    """
    src = ROOT / "scripts" / "daily.py"
    assert _tier0_violations(src.read_text(encoding="utf-8")) == set()


def test_nothing_daily_imports_can_reach_a_model_or_the_network_either():
    """The ban follows the import closure, not just the entry file."""
    closure = _import_closure(ROOT / "scripts" / "daily.py")
    offenders = {}
    for path in closure:
        bad = _import_roots(path.read_text(encoding="utf-8")) & BANNED_IMPORTS
        if bad:
            offenders[path.name] = sorted(bad)
    assert offenders == {}, offenders


def test_the_closure_walk_actually_reaches_the_modules_it_should():
    """Negative control for the walk: a walk that finds nothing bans nothing."""
    found = {p.name for p in _import_closure(ROOT / "scripts" / "daily.py")}
    for expected in ("daily.py", "home.py", "validate_syllabus.py", "scheduler.py"):
        assert expected in found, (expected, sorted(found))


def test_tier0_import_guard_actually_fires():
    """Negative control for the check itself.

    A gate nobody has watched fail is a gate nobody knows is wired. These are
    the three shapes the real regression would take: a provider SDK, a hand-
    rolled HTTP call, and shelling out to a provider CLI.
    """
    assert _tier0_violations("import anthropic") == {"anthropic"}
    assert _tier0_violations("from urllib import request") == {"urllib"}
    assert _tier0_violations("import subprocess") == {"subprocess"}
    clean = "import json" + chr(10) + "import os" + chr(10)
    assert _tier0_violations(clean) == set()

# --- review findings: the plan must survive a half-written state dir --------

def test_mastery_reaches_problem_ordering_through_build_plan():
    """build_plan passed {} for mastery, so a passed set could never be
    recognised and "unmastered first" was vacuous in production."""
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS,
                      available_sets={"pw-02", "la-02", "an-02"},
                      mastery={"pw-02": {"score": 0.95}})
    got = plan["problem_candidates"]
    assert got.index("la-02") < got.index("pw-02")
    assert got.index("an-02") < got.index("pw-02")


def test_without_mastery_the_ordering_is_syllabus_order():
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS,
                      available_sets={"pw-02", "la-02"})
    assert plan["problem_candidates"] == ["pw-02", "la-02"]


def test_rest_day_plan_still_has_no_lectures_with_mastery_supplied():
    plan = build_plan(SYL, PROGRESS, STATS, WEDNESDAY, STREAKS,
                      available_sets={"pw-02"}, schedule=SCHEDULE,
                      mastery={"pw-02": {"score": 0.95}})
    assert plan["rest_day"] is True and plan["problem_candidates"] == []


def test_a_session_file_without_a_plan_is_rebuilt_not_reported_already_built(tmp_path,
                                                                            monkeypatch):
    """state/sessions/ is tracked and state/today.json is gitignored, so a fresh
    checkout has one and not the other. Reporting "already-built" there left the
    server and /today reading an empty plan with nothing ever rebuilding it.
    """
    import os

    import scripts.daily as d

    monkeypatch.chdir(tmp_path)
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "curriculum" / "syllabus.yaml").write_text("x", encoding="utf-8")
    (tmp_path / "state" / "sessions").mkdir(parents=True)
    (tmp_path / "state" / "sessions" / "2026-08-31.md").write_text("old", encoding="utf-8")

    # load_syllabus is imported inside _build, not at module scope, so that a
    # broken PyYAML produces a "failed" heartbeat instead of dying at import.
    # That means it is patched where it is defined.
    monkeypatch.setattr("scripts.validate_syllabus.load_syllabus", lambda p: SYL)
    monkeypatch.setattr(d, "load_deck", lambda: {"cards": []})
    monkeypatch.setattr(d, "due_cards", lambda deck, today: [])
    monkeypatch.setattr(d, "read_required_json", lambda path: {
        "state/schedule.json": SCHEDULE,
        "state/progress.json": PROGRESS,
    }[path])
    monkeypatch.setattr(d, "read_json", lambda path, default=None: {})
    monkeypatch.setattr(d, "render_home", lambda view, links: "<html></html>")

    assert d._build(["--date", MONDAY]) == 0
    beat = json.loads((tmp_path / "state" / "last-daily-run.json").read_text(
        encoding="utf-8"))
    assert beat["outcome"] == "built", "a missing plan must be rebuilt"
    assert os.path.exists(tmp_path / "state" / "today.json")


def test_an_already_built_day_publishes_the_plan_on_disk_not_a_recomputation(
        tmp_path, monkeypatch):
    """Opening lecture 1 moves it unlocked -> in-progress, so a same-day rerun
    picks DIFFERENT units. Publishing that recomputation would leave the static
    page and the heartbeat disagreeing with the session file and today.json.
    """
    import scripts.daily as d

    monkeypatch.chdir(tmp_path)
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "curriculum" / "syllabus.yaml").write_text("x", encoding="utf-8")
    (tmp_path / "state" / "sessions").mkdir(parents=True)
    (tmp_path / "state" / "sessions" / ("%s.md" % MONDAY)).write_text("kept",
                                                                     encoding="utf-8")
    persisted = {"date": MONDAY, "rest_day": False, "due_count": 7,
                 "review_target": 7, "streak": {"current": 1, "best": 1},
                 "lectures": [{"id": "pw-02", "module": "pw",
                               "module_title": "Proof", "title": "Induction",
                               "hook": "h", "status": "in-progress",
                               "lesson_path": "lessons/pw/pw-02.html"}],
                 "problem_candidates": []}

    # pw-02 is now in-progress, so a fresh pick would prefer the unlocked la-02.
    progress = dict(PROGRESS, **{"pw-02": {"status": "in-progress"}})
    monkeypatch.setattr("scripts.validate_syllabus.load_syllabus", lambda p: SYL)
    monkeypatch.setattr(d, "load_deck", lambda: {"cards": []})
    monkeypatch.setattr(d, "due_cards", lambda deck, today: [])
    monkeypatch.setattr(d, "read_required_json", lambda path: {
        "state/schedule.json": SCHEDULE,
        "state/progress.json": progress,
    }[path])
    monkeypatch.setattr(d, "read_json", lambda path, default=None: {
        "state/today.json": persisted,
    }.get(path, {}))
    monkeypatch.setattr(d, "render_home", lambda view, links: "<html></html>")

    assert d._build(["--date", MONDAY]) == 0
    beat = json.loads((tmp_path / "state" / "last-daily-run.json").read_text(
        encoding="utf-8"))
    assert beat["outcome"] == "already-built"
    assert beat["units"] == ["pw-02"], "the heartbeat must match what is on disk"
    assert beat["due_count"] == 7, "not the recomputed count"
    assert (tmp_path / "state" / "sessions" / ("%s.md" % MONDAY)).read_text(
        encoding="utf-8") == "kept"


# --- state that is missing, not empty ---------------------------------------

def test_a_missing_schedule_is_an_error_not_a_rest_day(tmp_path, monkeypatch):
    """The default made every date a rest day and still wrote a healthy
    heartbeat, so the liveness check reported success while the learner was
    assigned nothing. A plausible empty day is worse than a loud failure."""
    import scripts.daily as d

    monkeypatch.chdir(tmp_path)
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "curriculum" / "syllabus.yaml").write_text("x", encoding="utf-8")
    monkeypatch.setattr("scripts.validate_syllabus.load_syllabus", lambda p: SYL)
    monkeypatch.setattr(d, "load_deck", lambda: {"cards": []})
    monkeypatch.setattr(d, "due_cards", lambda deck, today: [])

    assert d.main(["--date", MONDAY]) == 2
    beat = json.loads((tmp_path / "state" / "last-daily-run.json").read_text(
        encoding="utf-8"))
    assert beat["outcome"] == "failed"
    assert "schedule.json" in beat["error"]


def test_a_failed_build_retracts_yesterdays_static_page(tmp_path, monkeypatch):
    """dashboard/today.html is only rewritten by a run that got that far, so a
    crash leaves yesterday's page complete and carrying yesterday's healthy
    banner. The offline front door would keep offering yesterday's lectures."""
    import scripts.daily as d

    monkeypatch.chdir(tmp_path)
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "curriculum" / "syllabus.yaml").write_text("x", encoding="utf-8")
    (tmp_path / "dashboard").mkdir()
    (tmp_path / "dashboard" / "today.html").write_text(
        "<h1>Yesterday, and it looks fine</h1>", encoding="utf-8")
    monkeypatch.setattr("scripts.validate_syllabus.load_syllabus", lambda p: SYL)
    monkeypatch.setattr(d, "load_deck", lambda: {"cards": []})
    monkeypatch.setattr(d, "due_cards", lambda deck, today: [])

    assert d.main(["--date", MONDAY]) == 2
    page = (tmp_path / "dashboard" / "today.html").read_text(encoding="utf-8")
    assert "Yesterday" not in page
    assert "No day has been built" in page


def test_a_non_object_progress_file_is_an_error(tmp_path, monkeypatch):
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "progress.json").write_text("[]", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    import scripts.daily as d

    try:
        d.read_required_json("state/progress.json")
    except ValueError as exc:
        assert "object" in str(exc)
    else:
        raise AssertionError("a list is not a progress file")


# --- mastery.json is hand-edited, so it can be any shape --------------------

def test_malformed_mastery_does_not_take_the_day_with_it():
    """It only decides the ORDER of the problem candidates; losing the whole
    build over it trades a cosmetic defect for a failed day."""
    from scripts.daily import _clean_mastery

    assert _clean_mastery(["x"]) == {}
    assert _clean_mastery(None) == {}
    assert _clean_mastery({"aa-01": []}) == {}
    assert _clean_mastery({"aa-01": {"score": 0.9}, "aa-02": 3}) == {
        "aa-01": {"score": 0.9}}


def test_a_unit_with_an_unreadable_record_sorts_as_unattempted():
    from scripts.daily import _clean_mastery

    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, STREAKS,
                      available_sets={"pw-02", "la-02"},
                      mastery=_clean_mastery({"pw-02": [], "la-02": {"score": 0.99}}))
    assert plan["problem_candidates"][0] == "pw-02", "unattempted comes first"


# --- a persisted plan has to be publishable, not merely dated ---------------

def test_a_date_only_plan_is_not_treated_as_already_built():
    """already-built publishes the persisted object verbatim to the heartbeat,
    the static page and the server. `{"date": today}` would suppress the
    rebuild and then publish an empty day through all three, for ever."""
    from scripts.daily import plan_is_usable

    assert plan_is_usable({"date": MONDAY}, MONDAY) is False


def test_a_plan_for_another_day_is_not_current():
    from scripts.daily import plan_is_usable

    assert plan_is_usable({"date": "2020-01-01", "rest_day": False,
                           "lectures": [{"id": "pw-02"}],
                           "problem_candidates": []}, MONDAY) is False


def test_a_study_day_with_no_lectures_is_still_a_plan():
    """Once everything studiable is mastered this is the CORRECT plan, and
    home.py has a "No units are waiting" state for it. Rejecting it made every
    rerun that day report "built" again and rewrite state/sessions/<today>.md,
    discarding review notes appended earlier in the day."""
    from scripts.daily import plan_is_usable

    assert plan_is_usable({"date": MONDAY, "rest_day": False, "lectures": [],
                           "problem_candidates": []}, MONDAY) is True


def test_a_rest_day_with_no_lectures_is_exactly_right():
    from scripts.daily import plan_is_usable

    assert plan_is_usable({"date": MONDAY, "rest_day": True, "lectures": [],
                           "problem_candidates": []}, MONDAY) is True


def test_lectures_must_carry_ids_because_the_heartbeat_reads_them():
    from scripts.daily import plan_is_usable

    assert plan_is_usable({"date": MONDAY, "rest_day": False,
                           "lectures": [{"title": "no id"}],
                           "problem_candidates": []}, MONDAY) is False
    assert plan_is_usable({"date": MONDAY, "rest_day": False,
                           "lectures": ["pw-02"],
                           "problem_candidates": []}, MONDAY) is False


def test_a_plan_gaining_a_field_still_passes():
    """A shape check, not a schema: new fields must not fail the old check."""
    from scripts.daily import plan_is_usable

    assert plan_is_usable({"date": MONDAY, "rest_day": False,
                           "lectures": [{"id": "pw-02"}],
                           "problem_candidates": [], "something_new": 1},
                          MONDAY) is True


def test_malformed_streak_state_does_not_prevent_the_day(tmp_path, monkeypatch):
    """streaks.json is a cosmetic display counter. Letting its shape decide
    whether lectures, review and the fallback page get built at all inverts
    every priority this file has."""
    from scripts.daily import _as_mapping

    for bad in (None, [], "x", 3):
        assert _as_mapping(bad) == {}
    assert _as_mapping({"current": 3}) == {"current": 3}


def test_a_plan_builds_with_unreadable_streaks():
    plan = build_plan(SYL, PROGRESS, STATS, MONDAY, {}, available_sets={"pw-02"})
    assert plan["lectures"], "the day survives a missing display counter"
    assert plan["streak"] == {"current": 0, "best": 0}


def test_an_opened_but_unpromotable_unit_yields_to_an_untouched_one():
    """The server records `last_opened` on a unit it cannot mark in-progress
    (its solutions file is unwritten). Without reading it here, that unit is
    indistinguishable from one nobody has touched and, being first in syllabus
    order, is chosen again tomorrow and the day after."""
    units = [{"id": "pw-03", "module": "pw", "title": "a"},
             {"id": "la-02", "module": "la", "title": "b"}]
    fresh = {"pw-03": {"status": "unlocked"}, "la-02": {"status": "unlocked"}}
    assert pick_units(units, fresh, limit=1)[0]["id"] == "pw-03"

    opened = {"pw-03": {"status": "unlocked", "last_opened": "2026-09-02"},
              "la-02": {"status": "unlocked"}}
    assert pick_units(units, opened, limit=1)[0]["id"] == "la-02"


def test_an_opened_unlocked_unit_still_outranks_a_stalled_one():
    """It has been read, not worked. That is still fresher than a unit sitting
    half-finished, so the unlocked-before-in-progress rule holds."""
    units = [{"id": "pw-03", "module": "pw", "title": "a"},
             {"id": "la-02", "module": "la", "title": "b"}]
    progress = {"pw-03": {"status": "unlocked", "last_opened": "2026-09-02"},
                "la-02": {"status": "in-progress"}}
    assert pick_units(units, progress, limit=1)[0]["id"] == "pw-03"


def test_last_opened_does_not_disturb_the_ordinary_ranking():
    assert [u["id"] for u in pick_units(UNITS, PROGRESS)] == \
           [u["id"] for u in pick_units(UNITS, PROGRESS)]
