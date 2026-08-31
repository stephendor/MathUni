import json

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

def _import_roots(source):
    """Top-level module names imported by a Python source string."""
    import ast
    roots = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


ALLOWED_IMPORTS = {"argparse", "json", "os", "sys", "datetime",  # stdlib
                   "scripts", "srs"}                             # repo
BANNED_IMPORTS = {"urllib", "http", "socket", "requests", "httpx", "subprocess",
                  "anthropic", "openai", "ollama"}


def _tier0_violations(source):
    roots = _import_roots(source)
    return (roots & BANNED_IMPORTS) | (roots - ALLOWED_IMPORTS)


def test_daily_imports_nothing_that_could_call_a_model_or_a_network():
    """daily.py must stay Tier 0: stdlib + repo only.

    The module docstring claims no model and no network. A claim in a docstring
    is self-attestation; this is the check that makes it a property. If someone
    later reaches for `requests`, `urllib`, or a subprocess to a provider CLI,
    the day builder stops being the thing that still works when a provider is
    down, and this is what says so.
    """
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "daily.py"
    assert _tier0_violations(src.read_text(encoding="utf-8")) == set()


def test_tier0_import_guard_actually_fires():
    """Negative control for the check above.

    A gate nobody has watched fail is a gate nobody knows is wired. These are
    the three shapes the real regression would take: a provider SDK, a hand-
    rolled HTTP call, and shelling out to a provider CLI.
    """
    assert _tier0_violations("import anthropic") == {"anthropic"}
    assert _tier0_violations("from urllib import request") == {"urllib"}
    assert _tier0_violations("import subprocess") == {"subprocess"}
    clean = "import json" + chr(10) + "import os" + chr(10)
    assert _tier0_violations(clean) == set()
