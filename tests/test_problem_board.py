"""The problem board: a join over four files that must not contradict them."""
import pathlib

from scripts.home import StaticLinks
from scripts.problem_board import build_board, lane, render_board, summarise

UNITS = [
    {"id": "pw-01", "module": "pw", "title": "Direct proof"},
    {"id": "pw-02", "module": "pw", "title": "Induction"},
    {"id": "la-02", "module": "la", "title": "Subspaces"},
    {"id": "top-99", "module": "top", "title": "Way ahead"},
    {"id": "no-set", "module": "pw", "title": "Never authored"},
]

PROGRESS = {
    "pw-01": {"status": "mastered"},
    "pw-02": {"status": "in-progress"},
    "la-02": {"status": "unlocked"},
    "top-99": {"status": "locked"},
    "no-set": {"status": "unlocked"},
}

MASTERY = {"pw-01": {"score": 0.86, "attempts": 1, "last": "2026-07-10"}}
TITLES = {"pw": "Proof Workshop", "la": "Linear Algebra", "top": "Topology"}


def fake_repo(tmp_path, sets=("pw-01", "pw-02", "la-02", "top-99"),
              solutions=(), records=()):
    for name, files in (("problems/sets", sets),
                        ("problems/solutions", solutions),
                        ("learning-records", records)):
        d = tmp_path / name
        d.mkdir(parents=True, exist_ok=True)
        for uid in files:
            (d / ("%s.md" % uid)).write_text("x", encoding="utf-8")
    return tmp_path


def board(tmp_path, progress=None, mastery=None, **kw):
    fake_repo(tmp_path, **kw)
    return build_board(UNITS, PROGRESS if progress is None else progress,
                       MASTERY if mastery is None else mastery, TITLES,
                       root=str(tmp_path))


# --- the lanes must partition, or the header lies ---------------------------

def test_the_three_lanes_partition_every_row(tmp_path):
    rows = board(tmp_path)
    s = summarise(rows)
    assert s["pending"] + s["passed"] + s["locked"] == s["total"]


def test_a_mastered_unit_is_passed_not_locked(tmp_path):
    """It has left unlocked/in-progress entirely, so a rule that asks
    "studiable?" first files every finished unit under `locked` -- and then
    counts it under `passed` as well, reporting 145 sets as 148."""
    rows = {r["id"]: r for r in board(tmp_path)}
    assert rows["pw-01"]["passed"] is True
    assert lane(rows["pw-01"]) == "passed"


def test_a_mastered_unit_with_no_score_still_reads_as_done(tmp_path):
    """update_unlocks owns "mastered"; mastery.json is a separate record and
    may simply not have one."""
    rows = {r["id"]: r for r in board(tmp_path, mastery={})}
    assert lane(rows["pw-01"]) == "passed"
    assert rows["pw-01"]["score"] is None


def test_a_score_at_the_gate_passes_without_the_status(tmp_path):
    rows = {r["id"]: r for r in board(
        tmp_path, mastery={"la-02": {"score": 0.8}})}
    assert lane(rows["la-02"]) == "passed"


def test_a_score_below_the_gate_is_still_outstanding(tmp_path):
    rows = {r["id"]: r for r in board(
        tmp_path, mastery={"la-02": {"score": 0.79}})}
    assert lane(rows["la-02"]) == "pending"
    assert rows["la-02"]["attempted"] is True, "attempted, just not passed"


def test_studiable_and_unpassed_is_the_outstanding_lane(tmp_path):
    rows = {r["id"]: r for r in board(tmp_path)}
    assert lane(rows["pw-02"]) == "pending"
    assert lane(rows["la-02"]) == "pending"


def test_a_locked_unit_is_listed_but_lands_in_its_own_lane(tmp_path):
    """Listed, because the board is also how you see what is coming; its own
    lane, because the default filter should not offer it as work."""
    rows = {r["id"]: r for r in board(tmp_path)}
    assert lane(rows["top-99"]) == "locked"


def test_summarise_cannot_disagree_with_the_lanes(tmp_path):
    rows = board(tmp_path)
    s = summarise(rows)
    for name in ("pending", "passed", "locked"):
        assert s[name] == sum(1 for r in rows if lane(r) == name), name


# --- the join itself --------------------------------------------------------

def test_a_unit_with_no_authored_set_is_omitted(tmp_path):
    """A board padded with rows that are not files teaches you to distrust it."""
    assert "no-set" not in {r["id"] for r in board(tmp_path)}


def test_mastery_details_are_carried_through(tmp_path):
    row = {r["id"]: r for r in board(tmp_path)}["pw-01"]
    assert row["score"] == 0.86 and row["attempts"] == 1
    assert row["last"] == "2026-07-10"


def test_solutions_and_records_are_detected(tmp_path):
    rows = {r["id"]: r for r in board(tmp_path, solutions=("pw-01",),
                                      records=("pw-02",))}
    assert rows["pw-01"]["has_solutions"] and not rows["pw-01"]["has_record"]
    assert rows["pw-02"]["has_record"] and not rows["pw-02"]["has_solutions"]


def test_a_malformed_mastery_record_is_treated_as_unattempted(tmp_path):
    """mastery.json is hand-edited. Losing the board over one bad entry would
    trade an ordering detail for the whole page."""
    for bad in ([], "x", None, {"score": "high"}, {"score": True}):
        rows = {r["id"]: r for r in board(tmp_path, mastery={"la-02": bad})}
        assert rows["la-02"]["score"] is None, bad
        assert rows["la-02"]["attempted"] is False, bad


def test_a_unit_missing_from_progress_defaults_to_locked(tmp_path):
    """Absent from progress.json is not a fourth state; it reads as locked,
    the same default daily.py uses."""
    rows = {r["id"]: r for r in board(tmp_path, progress={}, mastery={})}
    assert rows["la-02"]["status"] == "locked"
    assert lane(rows["la-02"]) == "locked"


def test_a_passing_score_outranks_an_absent_progress_entry(tmp_path):
    """The two sources are consulted independently, so a unit with a recorded
    score is done even if progress.json has lost track of it."""
    rows = {r["id"]: r for r in board(tmp_path, progress={})}
    assert lane(rows["pw-01"]) == "passed"


def test_rows_follow_syllabus_order(tmp_path):
    assert [r["id"] for r in board(tmp_path)] == ["pw-01", "pw-02", "la-02", "top-99"]


# --- the page ---------------------------------------------------------------

def test_the_header_states_the_counts(tmp_path):
    rows = board(tmp_path)
    html = render_board(rows, StaticLinks())
    s = summarise(rows)
    assert "%d outstanding" % s["pending"] in html
    assert "%d passed" % s["passed"] in html
    assert "%d authored in all" % s["total"] in html


def test_every_row_is_a_working_link(tmp_path):
    html = render_board(board(tmp_path), StaticLinks())
    for uid in ("pw-01", "pw-02", "la-02", "top-99"):
        assert "../problems/sets/%s.md" % uid in html


def test_modules_are_grouped_with_their_titles(tmp_path):
    html = render_board(board(tmp_path), StaticLinks())
    assert "Proof Workshop" in html and "Linear Algebra" in html
    assert html.index("Proof Workshop") < html.index("Linear Algebra")


def test_a_mastered_row_says_so_rather_than_showing_nothing(tmp_path):
    html = render_board(board(tmp_path, mastery={}), StaticLinks())
    assert "mastered" in html


def test_a_score_is_shown_as_a_percentage_with_its_attempts(tmp_path):
    html = render_board(board(tmp_path), StaticLinks())
    assert "86%" in html and "1 attempt<" in html


def test_the_default_filter_is_outstanding(tmp_path):
    """The question the board exists to answer, and 135 of the 145 real rows
    are locked -- opening on all of them buries the seven that matter."""
    html = render_board(board(tmp_path), StaticLinks())
    assert "data-lane='pending' aria-pressed='true'" in html
    assert "var lane = 'pending'" in html


def test_titles_are_escaped(tmp_path):
    units = [{"id": "pw-01", "module": "pw", "title": "<script>alert(1)</script>"}]
    fake_repo(tmp_path)
    html = render_board(build_board(units, PROGRESS, {}, TITLES,
                                    root=str(tmp_path)), StaticLinks())
    assert "<script>alert(1)" not in html
    assert "&lt;script&gt;" in html


def test_the_real_corpus_produces_a_board():
    """146 sets on disk; 145 map to syllabus units."""
    import json

    import yaml

    root = pathlib.Path(__file__).resolve().parents[1]
    syllabus = yaml.safe_load(
        (root / "curriculum" / "syllabus.yaml").read_text(encoding="utf-8"))
    progress = json.loads(
        (root / "state" / "progress.json").read_text(encoding="utf-8-sig"))
    mastery = json.loads(
        (root / "state" / "mastery.json").read_text(encoding="utf-8-sig"))
    rows = build_board(syllabus["units"], progress, mastery, root=str(root))
    s = summarise(rows)
    assert s["total"] > 140
    assert s["pending"] + s["passed"] + s["locked"] == s["total"]


# --- state that is valid JSON but the wrong shape ---------------------------

def test_a_non_object_mastery_file_does_not_500_the_board(tmp_path):
    """/problems returned HTTP 500 over a file that decides nothing but which
    lane a row lands in. daily.py already normalises the same input.

    build_board directly, not the helper: the helper reads None as "use the
    default fixture", which is exactly the value under test here."""
    fake_repo(tmp_path)
    for bad in (None, [], "x", 3):
        rows = build_board(UNITS, PROGRESS, bad, TITLES, root=str(tmp_path))
        assert len(rows) == 4, bad
        assert all(r["score"] is None for r in rows), bad
        assert "</html>" in render_board(rows, StaticLinks()), bad


def test_a_non_object_progress_file_is_survivable(tmp_path):
    fake_repo(tmp_path)
    for bad in (None, [], "x", 3):
        rows = build_board(UNITS, bad, {}, TITLES, root=str(tmp_path))
        assert all(r["status"] == "locked" for r in rows), bad
        assert all(lane(r) == "locked" for r in rows), bad


def test_a_non_numeric_attempt_count_never_reaches_the_formatter(tmp_path):
    """_tags formats attempts with %d, and {"attempts": "one"} is a thing a
    hand-edited file can say."""
    for bad in ("one", [], {}, -1, True, None):
        rows = board(tmp_path,
                     mastery={"la-02": {"score": 0.5, "attempts": bad}})
        html = render_board(rows, StaticLinks())
        assert "</html>" in html
        assert "attempt" not in html or "1 attempt" not in html


def test_a_real_attempt_count_is_shown(tmp_path):
    rows = board(tmp_path, mastery={"la-02": {"score": 0.5, "attempts": 3}})
    assert "3 attempts" in render_board(rows, StaticLinks())


def test_a_non_finite_score_is_not_a_score(tmp_path):
    """round(nan * 100) raises in _tags, and inf would silently pass the gate
    for every unit it touched."""
    for bad in (float("nan"), float("inf"), float("-inf")):
        rows = {r["id"]: r for r in board(tmp_path, mastery={"la-02": {"score": bad}})}
        assert rows["la-02"]["score"] is None, bad
        assert lane(rows["la-02"]) == "pending", bad
