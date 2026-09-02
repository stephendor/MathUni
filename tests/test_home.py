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
    assert "$f: A" in out, "the LaTeX reaches the page for KaTeX to render"
    assert "Problem set · pw-03" in out


def test_problem_set_page_escapes_the_markdown():
    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "<script>alert(1)</script> & co")
    assert "<script>alert(1)</script>" not in out
    assert "&lt;script&gt;" in out and "&amp; co" in out


def test_problem_set_page_makes_no_external_requests():
    """It DOES load stylesheets, scripts and fonts -- all same-origin, from the
    vendored KaTeX. The rule was never "no requests"; it is "nothing off this
    machine", which is what keeps the college working offline.
    """
    import re

    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "body")
    for probe in ("http://", "https://", "//cdn", "@import"):
        assert probe not in out, probe
    pattern = (r'(?:src|href)=' + '[' + "'" + '"' + ']'
               + r'([^' + "'" + '"' + r']+)'
               + '[' + "'" + '"' + ']')
    refs = re.findall(pattern, out)
    assert refs, "the page should reference the vendored assets"
    for ref in refs:
        assert ref.startswith("/"), "off-origin reference: %s" % ref
        assert not ref.startswith("//"), "protocol-relative: %s" % ref


def test_problem_set_page_loads_katex_from_the_vendored_copy():
    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "$x$")
    assert "/katex/katex.min.js" in out
    assert "/katex/contrib/auto-render.min.js" in out
    assert "renderMathInElement" in out


def test_katex_runs_in_mathml_only_mode():
    """The default htmlAndMathml emits a visual rendering AND a hidden MathML
    copy. Beside a Native MathML browser extension the two fight and every
    formula goes blank -- observed, not hypothetical. One representation only.
    """
    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "$x$")
    assert "output:'mathml'" in out


def test_no_stylesheet_or_font_is_loaded():
    """MathML is laid out by the browser, so the KaTeX CSS and its 20 web fonts
    are not vendored at all. A <link> here would 404."""
    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "$x$")
    assert "katex.min.css" not in out
    assert "<link" not in out
    assert ".woff" not in out


def test_problem_set_page_renders_markdown_structure():
    from scripts.home import render_problem_set

    out = render_problem_set("x-01", "t", "## Problem 1" + chr(10) * 2 + "**Bold** text")
    assert "<h2>Problem 1</h2>" in out
    assert "<strong>Bold</strong>" in out


def test_the_header_does_not_repeat_the_documents_own_title():
    """Every set opens with `# unit — title`; printing it again three lines
    above just reads as a bug."""
    from scripts.home import render_problem_set

    out = render_problem_set("pw-03", "Sets and functions",
                             "# pw-03 - Sets and functions")
    assert out.count("Sets and functions") == 1


# --- a plan from another day is worse than no plan --------------------------

def test_yesterdays_plan_is_not_rendered_under_todays_date():
    """state/today.json is only rewritten by a successful build, so a failed
    build leaves yesterday's object on disk and the server hands it straight
    to build_view. Rendering it puts yesterday's lectures under today's date,
    as live links, with the banner above them warning about nothing useful."""
    stale = dict(PLAN, date="2020-01-01")
    v = build_view(stale, PROGRESS, SYL, STREAKS,
                   {"date": "2020-01-01", "outcome": "built"}, TODAY)
    assert v["stale_plan"] is True
    assert v["lectures"] == []
    assert v["problems"] == []
    assert v["hook"] == ""


def test_todays_plan_is_not_flagged_stale():
    assert view()["stale_plan"] is False


def test_an_absent_plan_is_not_a_stale_one():
    """No plan at all is a different condition, and says so differently."""
    v = build_view({}, PROGRESS, SYL, STREAKS, BEAT, TODAY)
    assert v["stale_plan"] is False and v["has_plan"] is False


def test_the_banner_explains_why_the_page_is_thin():
    stale = dict(PLAN, date="2020-01-01")
    html = render_home(build_view(stale, PROGRESS, SYL, STREAKS,
                                  {"date": "2020-01-01", "outcome": "built"},
                                  TODAY), StaticLinks())
    assert "set aside" in html
    assert "Dominoes, infinitely." not in html, "no stale hook may survive"


def test_a_healthy_heartbeat_with_a_stale_plan_still_says_something():
    """Should not happen -- daily.py writes both -- but silence is the wrong
    response to two files disagreeing about what day it is."""
    stale = dict(PLAN, date="2020-01-01")
    html = render_home(build_view(stale, PROGRESS, SYL, STREAKS, BEAT, TODAY),
                       StaticLinks())
    assert "Today's plan is missing" in html


# --- the liveness banner is the page's last line of defence -----------------

def test_an_unparseable_heartbeat_date_does_not_take_the_page_down():
    """_days_since returns None for a date it cannot read, deliberately. That
    branch formatted it with %d and raised, turning the one surface whose job
    is to survive bad state into an HTTP 500."""
    html = render_home(view(beat={"date": "not-a-date", "outcome": "built"}),
                       StaticLinks())
    assert "not a date" in html
    assert "scripts/daily.py" in html


def test_a_heartbeat_that_is_not_a_record_is_survivable():
    for beat in ({}, None):
        html = render_home(view(beat=beat), StaticLinks())
        assert "day builder has not run" in html


# --- the rendered vocabulary the problem pages now need ---------------------

def test_problem_css_styles_the_blocks_mathdoc_emits():
    from scripts.home import PROBLEM_CSS

    assert "pre{" in PROBLEM_CSS, "fenced code needs a scroll box"
    assert "table{" in PROBLEM_CSS and "th,td{" in PROBLEM_CSS
    assert "overflow-x:auto" in PROBLEM_CSS


# --- the page written when there is no day to show --------------------------

def test_the_unbuilt_page_says_what_to_run():
    from scripts.home import render_unbuilt_page

    page = render_unbuilt_page(TODAY, "The last recorded run was 2020-01-01.")
    assert "No day has been built" in page and TODAY in page
    assert "2020-01-01" in page
    assert "python scripts/daily.py" in page
    assert "check_daily_liveness" in page


def test_the_unbuilt_page_escapes_what_it_is_told():
    from scripts.home import render_unbuilt_page

    page = render_unbuilt_page(TODAY, "<script>alert(1)</script>")
    assert "<script>alert(1)" not in page and "&lt;script&gt;" in page


def test_the_unbuilt_page_needs_no_state_to_render():
    """It is written from a crash handler and from a Start Menu shortcut, and
    both must work when the thing that failed is the state it would read."""
    import ast
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1]
           / "scripts" / "home.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "render_unbuilt_page")
    called = {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert called <= {"escape"}, called


# --- nothing disappears because the day is empty ----------------------------

def test_a_rest_day_still_names_both_boards():
    """The complaint that started this: on a rest day build_plan empties
    problem_candidates -- correctly, a rest day owes no work -- and the sets
    vanished from the only surface that listed them."""
    html = render_home(view(plan=dict(PLAN, rest_day=True, lectures=[],
                                      problem_candidates=[])), StaticLinks())
    assert "Rest day" in html
    assert "problems.html" in html, "the board must be reachable"
    assert "reference.html" in html


def test_a_day_with_nothing_unlocked_still_offers_the_board():
    html = render_home(view(plan=dict(PLAN, lectures=[],
                                      problem_candidates=[])), StaticLinks())
    assert "No units are waiting" in html and "problems.html" in html


def test_every_page_carries_the_same_footer_nav():
    html = render_home(view(), StaticLinks())
    for href in ("today.html", "problems.html", "reference.html", "index.html"):
        assert href in html, href


def test_the_static_nav_omits_review_because_it_cannot_work():
    """StaticLinks.review() is None by design: a writeback link opened from a
    file:// page would silently do nothing."""
    from scripts.home import ServerLinks

    assert "review" not in StaticLinks().nav().lower()
    assert "/review" in ServerLinks("tok").nav()


def test_the_server_nav_reaches_every_surface():
    from scripts.home import ServerLinks

    nav = ServerLinks("tok").nav()
    for href in ("/", "/problems", "/reference", "/review", "/dashboard"):
        assert 'href="%s"' % href in nav, href


# --- state that is valid JSON but the wrong shape ---------------------------

def test_a_non_object_plan_does_not_take_the_page_down():
    """`plan or {}` kept a truthy list, and the next line called .get on it.
    The server turns that AttributeError into a 500, so a malformed today.json
    took down the page whose whole job is to survive bad state."""
    for bad in ([1, 2], "text", 7):
        v = build_view(bad, PROGRESS, SYL, STREAKS, BEAT, TODAY)
        assert v["has_plan"] is False
        assert "Nexus College" in render_home(v, StaticLinks())


def test_non_object_progress_and_streaks_are_survivable():
    for bad in ([], "x", None):
        html = render_home(
            build_view(PLAN, bad if bad is not None else {}, SYL, bad, BEAT, TODAY),
            StaticLinks())
        assert "</html>" in html


def test_a_non_object_heartbeat_reads_as_never_run():
    v = build_view(PLAN, PROGRESS, SYL, STREAKS, ["nonsense"], TODAY)
    assert v["liveness"]["stale"] is True
    assert "day builder has not run" in render_home(v, StaticLinks())
