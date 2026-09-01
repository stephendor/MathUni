from scripts.home import (
    ServerLinks,
    StaticLinks,
    build_view,
    render_home,
)

TODAY = "2026-08-31"

SYL = {"modules": [{"id": "pw", "title": "Proof Workshop"},
                   {"id": "la", "title": "Linear Algebra"},
                   {"id": "top", "title": "Topology"}],
       "units": [
           {"id": "pw-01", "module": "pw", "title": "Direct proof", "prereqs": [],
            "hook": "h", "mission_link": "m", "resources": []},
           {"id": "pw-02", "module": "pw", "title": "Induction", "prereqs": [],
            "hook": "Dominoes, infinitely.", "mission_link": "m", "resources": []},
           {"id": "la-02", "module": "la", "title": "Subspaces", "prereqs": [],
            "hook": "h", "mission_link": "m", "resources": []},
           {"id": "top-01", "module": "top", "title": "Open sets", "prereqs": [],
            "hook": "h", "mission_link": "m", "resources": []}]}

PLAN = {"date": TODAY, "rest_day": False, "due_count": 66, "review_target": 15,
        "streak": {"current": 3, "best": 5},
        "lectures": [{"id": "pw-02", "module": "pw", "module_title": "Proof Workshop",
                      "title": "Induction", "hook": "Dominoes, infinitely.",
                      "status": "unlocked", "lesson_path": "lessons/pw/pw-02.html"},
                     {"id": "la-02", "module": "la", "module_title": "Linear Algebra",
                      "title": "Subspaces", "hook": "Hook la.",
                      "status": "unlocked", "lesson_path": "lessons/la/la-02.html"}],
        "problem_candidates": ["pw-02", "la-02"]}

PROGRESS = {"pw-01": {"status": "mastered", "last_studied": "2026-07-07"},
            "pw-02": {"status": "unlocked"},
            "la-02": {"status": "unlocked"},
            "top-01": {"status": "in-progress", "last_studied": "2026-07-20"}}

STREAKS = {"current": 3, "best": 5}
BEAT = {"date": TODAY, "outcome": "built"}


def view(plan=PLAN, progress=None, beat=BEAT, today=TODAY):
    return build_view(plan, PROGRESS if progress is None else progress,
                      SYL, STREAKS, beat, today)


# --- build_view -------------------------------------------------------------

def test_hook_is_the_headline():
    assert view()["hook"] == "Dominoes, infinitely."


def test_backlog_is_reported_as_target_of_total():
    v = view()
    assert v["review"] == {"due": 66, "target": 15}


def test_stale_in_progress_units_are_surfaced_with_their_age():
    stale = view()["stale"]
    assert [s["id"] for s in stale] == ["top-01"]
    assert stale[0]["days"] == 42


def test_a_recently_studied_in_progress_unit_is_not_stale():
    progress = dict(PROGRESS, **{"top-01": {"status": "in-progress",
                                            "last_studied": "2026-08-30"}})
    assert view(progress=progress)["stale"] == []


def test_only_modules_with_progress_get_a_bar():
    """30 empty bars is noise, not a progress display."""
    mods = view()["modules"]
    assert [m["id"] for m in mods] == ["pw"]
    assert mods[0]["done"] == 1 and mods[0]["total"] == 2


def test_liveness_is_fresh_when_the_heartbeat_is_today():
    assert view()["liveness"]["stale"] is False


def test_liveness_is_stale_when_the_heartbeat_is_old():
    live = view(beat={"date": "2026-08-24", "outcome": "built"})["liveness"]
    assert live["stale"] is True and live["days"] == 7


def test_liveness_is_stale_when_there_is_no_heartbeat_at_all():
    """Absence and staleness must both register; only one of them has a date."""
    live = view(beat={})["liveness"]
    assert live["stale"] is True and live["last"] is None


def test_rest_day_view_carries_no_lectures():
    v = view(plan={"date": TODAY, "rest_day": True, "due_count": 4,
                   "review_target": 4, "lectures": [], "problem_candidates": [],
                   "streak": {"current": 3, "best": 5}})
    assert v["rest_day"] is True and v["lectures"] == []


# --- render_home ------------------------------------------------------------

def html(v=None, links=None):
    return render_home(v or view(), links or ServerLinks("TOK"))


def test_page_is_a_document_with_the_hook_in_it():
    out = html()
    assert out.startswith("<!DOCTYPE html>") and "</html>" in out
    assert "Dominoes, infinitely." in out


def test_server_links_carry_the_token_and_go_through_open():
    out = html()
    assert '/open/pw-02?t=TOK' in out
    assert '/open/la-02?t=TOK' in out


def test_static_links_point_at_the_lesson_files_directly():
    out = html(links=StaticLinks())
    assert "../lessons/pw/pw-02.html" in out
    assert "/open/" not in out, "a dead server must not be linked as if live"


def test_static_page_says_review_needs_the_server_rather_than_dead_linking():
    out = html(links=StaticLinks())
    assert "needs the local server" in out
    assert 'href="/review"' not in out


def test_stale_banner_appears_only_when_the_builder_has_not_run():
    assert "has not run today" not in html()
    stale = view(beat={"date": "2026-08-20", "outcome": "built"})
    assert "has not run today" in html(stale)


def test_rest_day_page_offers_without_obliging():
    v = view(plan={"date": TODAY, "rest_day": True, "due_count": 4,
                   "review_target": 4, "lectures": [], "problem_candidates": [],
                   "streak": {"current": 3, "best": 5}})
    out = html(v)
    assert "Rest day" in out
    assert "nothing is owed" in out


def test_hooks_and_titles_are_escaped():
    """Unit text is authored in YAML and reaches the page as markup otherwise."""
    plan = dict(PLAN)
    plan["lectures"] = [dict(PLAN["lectures"][0],
                             hook="<script>alert(1)</script> & co",
                             title="a <b>bold</b> title")]
    out = html(view(plan=plan))
    assert "<script>alert(1)</script>" not in out
    assert "&lt;script&gt;" in out and "&amp; co" in out
    assert "<b>bold</b>" not in out


def test_no_external_requests_from_the_home_page():
    """Same rule gate.py enforces on lessons: the page must render offline."""
    out = html()
    for probe in ("http://", "https://", "//cdn", "@import", "<link"):
        assert probe not in out, probe


def test_empty_plan_renders_a_page_rather_than_crashing():
    """A first run, or a wiped state dir, must still produce a front door."""
    out = render_home(view(plan={}), ServerLinks("TOK"))
    assert "<!DOCTYPE html>" in out
    assert "No units are waiting" in out or "has not run today" in out


def test_the_warm_up_button_shows_the_capped_target_not_the_whole_backlog():
    """66 on the button rebuilds the wall the cap exists to take down."""
    out = html()
    assert "Warm up · 15 cards" in out
    assert "Warm up · 66 cards" not in out


def test_a_small_queue_is_shown_whole():
    v = view(plan=dict(PLAN, due_count=4, review_target=4))
    out = html(v)
    assert "Warm up · 4 cards" in out
    assert "of 4 due" not in out, "no 'x of y' framing when there is no backlog"

def test_a_crashed_build_shows_the_banner_even_though_it_is_dated_today():
    """The page and scripts/check_daily_liveness.py must agree; the rule is
    imported from one place rather than restated in two."""
    v = view(beat={"date": TODAY, "outcome": "failed", "error": "boom"})
    assert v["liveness"]["stale"] is True
    out = html(v)
    assert "has not run today" in out
    assert "did not finish" in out


def test_a_rest_day_heartbeat_is_not_a_stale_banner():
    v = view(beat={"date": TODAY, "outcome": "rest"})
    assert v["liveness"]["stale"] is False
    assert "has not run today" not in html(v)

# --- review findings: the served page must not contradict the live state ----

def test_live_due_overrides_the_morning_snapshot():
    """After a review session the plan still says 66; the page must not."""
    v = build_view(PLAN, PROGRESS, SYL, STREAKS, BEAT, TODAY, live_due=51)
    assert v["review"]["due"] == 51
    assert v["review"]["target"] == 15, "still capped"


def test_live_due_below_the_cap_is_shown_whole():
    v = build_view(PLAN, PROGRESS, SYL, STREAKS, BEAT, TODAY, live_due=4)
    assert v["review"] == {"due": 4, "target": 4}


def test_no_live_due_keeps_the_snapshot_for_the_static_page():
    """dashboard/today.html cannot know the live count and must not invent one."""
    v = build_view(PLAN, PROGRESS, SYL, STREAKS, BEAT, TODAY)
    assert v["review"] == {"due": 66, "target": 15}


def test_streaks_file_wins_over_the_plans_copy():
    """Closing a day rewrites streaks.json but not the plan."""
    v = build_view(PLAN, PROGRESS, SYL, {"current": 9, "best": 12}, BEAT, TODAY)
    assert v["streak"] == {"current": 9, "best": 12}


def test_plan_streak_is_the_fallback_when_there_is_no_streaks_file():
    v = build_view(PLAN, PROGRESS, SYL, {}, BEAT, TODAY)
    assert v["streak"] == {"current": 3, "best": 5}


# --- the problem chips were spans wired to nothing ---------------------------

def test_problem_chips_are_links_not_inert_spans():
    """They were <span class="chip">: styled like links, doing nothing. A
    control that reads as clickable and is not is worse than no control."""
    out = html()
    assert '<a class="chip" href="/problems/pw-02"' in out
    assert '<span class="chip"' not in out


def test_problem_chips_carry_the_unit_title_as_a_tooltip():
    assert 'title="Induction"' in html()


def test_static_page_chips_point_at_the_markdown_on_disk():
    out = html(links=StaticLinks())
    assert '../problems/sets/pw-02.md' in out
    assert "/problems/pw-02" not in out


def test_problem_set_page_shows_the_source_verbatim():
    from scripts.home import render_problem_set

    body = "# pw-03" + chr(10) + "Let $f: A " + chr(92) + "to B$ be given."
    out = render_problem_set("pw-03", "Sets and functions", body)
    assert out.startswith("<!DOCTYPE html>")
    assert "$f: A" in out, "LaTeX is shown as written; nothing renders it"
    assert "Sets and functions" in out


def test_problem_set_page_escapes_the_markdown():
    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "<script>alert(1)</script> & co")
    assert "<script>alert(1)</script>" not in out
    assert "&lt;script&gt;" in out and "&amp; co" in out


def test_problem_set_page_makes_no_external_requests():
    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "body")
    for probe in ("http://", "https://", "//cdn", "@import", "<link"):
        assert probe not in out, probe
