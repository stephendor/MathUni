from scripts.build_dashboard import render

SYL = {"semesters": [{"id": "s1", "title": "T"}],
       "modules": [{"id": "la", "title": "Linear Algebra", "semester": "s1"}],
       "units": [
           {"id": "la-01", "module": "la", "title": "Vector spaces", "prereqs": [],
            "resources": [], "hook": "h", "mission_link": "m"},
           {"id": "la-02", "module": "la", "title": "Subspaces", "prereqs": ["la-01"],
            "resources": [], "hook": "h", "mission_link": "m"}]}
PROG = {"la-01": {"status": "in-progress"}, "la-02": {"status": "locked"}}
STREAKS = {"current": 3, "best": 5, "study_days": ["2026-07-06"]}

def test_render_returns_html_document():
    html = render(SYL, PROG, STREAKS)
    assert html.startswith("<!DOCTYPE html>") and "</html>" in html

def test_units_appear_in_status_columns():
    html = render(SYL, PROG, STREAKS)
    assert "Vector spaces" in html and "Subspaces" in html
    assert 'data-status="in-progress"' in html and 'data-status="locked"' in html

def test_streak_and_module_progress_shown():
    html = render(SYL, PROG, STREAKS)
    assert "3" in html and "Linear Algebra" in html
    assert "0/2" in html  # mastered count / total for module la

def test_unknown_unit_status_defaults_locked():
    html = render(SYL, {}, STREAKS)
    assert html.count('data-status="locked"') == 2
