"""A canvas figure asserts the same fact in four places.

The drawing script, the aria-label, the HTML caption, and any text the script
paints. lab-09's caption said the two thresholds "both cut the barcode after
the third bar" while the null threshold cuts after the fifth; two reviewers
caught that. Neither found the third instance — a footer string inside the
drawing code, left over from a superseded version of the figure and false under
the corrected numbers. It was found only by opening the drawing code, because a
painted string is invisible to a text search of the prose, to a reviewer reading
the caption's diff, and to a screen reader.

Two checks answer that, at different rungs:

  * `lesson_lint.CANVAS_CHECK` names the aria-label CANONICAL and requires every
    decimal number the script paints to appear in it. Structural, no rendering.
  * `check_canvas_render.py --check-fixture` compares a live headless render
    against a committed read-back, so gate 7's manual canvas read-back leaves an
    execution signal instead of being purely manual.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.lesson_lint import (CANVAS_CHECK, canvas_labels, lint,
                                 canvas_ratchet_errors, painted_literals,
                                 undescribed_canvas_numbers, unit_id_for)

ROOT = Path(__file__).resolve().parents[1]
DRIFT = ROOT / "curriculum" / "canvas-label-drift.txt"


def canvas_page(label, script):
    return ('<canvas id="fig" aria-label="%s"></canvas>'
            '<script>%s</script>' % (label, script))


# --- what the script paints ------------------------------------------------

def test_a_pure_string_literal_is_read():
    assert painted_literals(
        "<script>g.fillText('null max = 0.5012', 4, 8);</script>"
    ) == ["null max = 0.5012"]


def test_a_computed_argument_is_not_read():
    """`t.toFixed(1)` and `'H1 #' + (i+1)` are produced at draw time. The check
    says nothing about them — a stated limit, not a silent omission."""
    assert painted_literals(
        "<script>g.fillText(t.toFixed(1), 0, 0);"
        "g.fillText('H1 #' + (i + 1), 62, 10);</script>") == []


def test_both_quote_styles_and_an_escaped_quote_survive():
    assert painted_literals(
        '<script>g.fillText("a 1.5 b", 0, 0);'
        r"g.fillText('it\'s 2.5', 0, 0);</script>") == ["a 1.5 b", r"it\'s 2.5"]


def test_labels_are_pooled_across_a_lessons_canvases():
    html = ('<canvas aria-label="first 1.5"></canvas>'
            '<canvas aria-label="second 2.5"></canvas>')
    assert "1.5" in canvas_labels(html) and "2.5" in canvas_labels(html)


# --- the check itself ------------------------------------------------------

def test_a_painted_number_missing_from_the_label_is_reported():
    """The defect. The figure paints 0.5012 and nothing describes it."""
    page = canvas_page("A barcode with bars in green.",
                       "g.fillText('null max = 0.5012', 4, 8);")
    assert undescribed_canvas_numbers(page) == [
        ("0.5012", "null max = 0.5012")]


def test_a_painted_number_present_in_the_label_is_quiet():
    """The positive control: without it, a check that returned [] always would
    pass the negative above."""
    page = canvas_page("A dashed line marks the null threshold at 0.5012.",
                       "g.fillText('null max = 0.5012', 4, 8);")
    assert undescribed_canvas_numbers(page) == []


def test_an_integer_is_not_required_verbatim():
    """A good aria-label spells small counts out ("five bars extend past the
    null line"), so demanding "5" would be noisy against correct prose."""
    page = canvas_page("Three bars extend past the stability line.",
                       "g.fillText('4 delta keeps 3, the null keeps 5.', 0, 0);")
    assert undescribed_canvas_numbers(page) == []


def test_a_result_number_is_a_citation_not_figure_data():
    """"Theorem 11.1" painted on a canvas is checked against the book by
    citations.py. Demanding it in the aria-label would be this check reaching
    outside its own claim."""
    for painted in ("Theorem 11.1: one operation", "Lemma 1.17 — stated",
                    "(Example 3.3)", "see §31.2 for the counterexample",
                    "Corollary 3.6", "Definition 2.4"):
        page = canvas_page("A commutative square.",
                           "g.fillText('%s', 0, 0);" % painted)
        assert undescribed_canvas_numbers(page) == [], painted


def test_a_result_number_does_not_excuse_data_in_the_same_string():
    """The exclusion is scoped to the numeral, not to the line — a sentence
    carrying both a citation and a measurement is still checked for the
    measurement."""
    page = canvas_page("A commutative square.",
                       "g.fillText('by Theorem 11.1 the gap is 0.368', 0, 0);")
    assert [n for n, _lit in undescribed_canvas_numbers(page)] == ["0.368"]


def test_each_numeral_is_reported_once():
    page = canvas_page("nothing",
                       "g.fillText('gap 0.368', 0, 0);"
                       "g.fillText('still 0.368', 0, 0);")
    assert len(undescribed_canvas_numbers(page)) == 1


def test_the_row_reaches_the_lint_report():
    page = canvas_page("A barcode.", "g.fillText('max = 0.5012', 0, 0);")
    row = [r for r in lint(page) if r[0] == CANVAS_CHECK]
    assert len(row) == 1 and row[0][1] is False
    assert "0.5012" in row[0][2]


# --- the ratchet -----------------------------------------------------------

def test_lab_09_the_figure_that_prompted_this_describes_its_numbers():
    """lab-09 is deliberately absent from the drift list: it was repaired in
    the same change, so the check has a real passing case in the corpus and
    "no failures" is not just the drift list swallowing them all."""
    html = (ROOT / "lessons" / "lab" / "lab-09.html").read_text(encoding="utf-8")
    assert undescribed_canvas_numbers(html) == []
    assert "lab-09" not in DRIFT.read_text(encoding="utf-8").split("\n\n")[-1]


def test_a_listed_unit_that_now_passes_fails_the_run():
    """The ratchet rule, and the only thing separating this list from a
    suppression list."""
    errors = canvas_ratchet_errors({"lab-09"}, str(DRIFT))
    assert len(errors) == 1 and "strike it" in errors[0]


def test_a_listed_unit_whose_lesson_is_gone_fails_the_run():
    errors = canvas_ratchet_errors({"zz-99"}, str(DRIFT))
    assert len(errors) == 1 and "has no lesson" in errors[0]


def test_a_listed_unit_that_still_fails_is_quiet():
    """Positive control for the ratchet itself."""
    assert canvas_ratchet_errors({"an2-06"}, str(DRIFT)) == []


def test_the_committed_drift_list_has_no_stale_entries():
    from scripts.mission import load_known_failing
    listed = load_known_failing(str(DRIFT))
    assert listed, "an empty list would make the ratchet test vacuous"
    assert canvas_ratchet_errors(listed, str(DRIFT)) == []


def test_the_drift_list_is_the_measured_backlog_not_a_guess():
    """G15: the known gap ships with its magnitude. 134 lessons carry a canvas
    and 10 painted a number no label described; lab-09 was repaired, so nine
    are listed."""
    from scripts.mission import load_known_failing
    assert len(load_known_failing(str(DRIFT))) == 9


def test_an_unreadable_drift_list_is_verdict_2_not_1():
    """Exit 1 is reserved for a lesson that failed a check. A ratchet input
    that exists but cannot be read is an absence of analysis and must not look
    like one — the rule mission.py already holds itself to."""
    from scripts.lesson_lint import main
    assert main(["--known-failing", str(ROOT / "scripts"),
                 str(ROOT / "lessons" / "lab" / "lab-09.html")]) == 2


def test_an_excused_lesson_exits_zero_and_says_why(capsys):
    from scripts.lesson_lint import main
    rc = main(["--known-failing", str(DRIFT),
               str(ROOT / "lessons" / "an2" / "an2-06.html")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "KNOWN-FAIL" in out and "an2-06" in out


def test_unit_id_is_anchored_to_the_whole_basename():
    """The defect mission.py records: end-anchoring alone let `draft-aa-01.html`
    be treated as unit aa-01."""
    assert unit_id_for("lessons/lab/lab-09.html") == "lab-09"
    assert unit_id_for("lessons/lab/draft-lab-09.html") is None


def test_the_manifest_runs_the_lint_against_the_ratchet():
    from scripts.check_unit import commands_for_unit
    command = dict(commands_for_unit("lab-09", ci=True))["lesson-lint"]
    assert "--known-failing" in command
    assert "curriculum/canvas-label-drift.txt" in command


# --- the read-back fixture -------------------------------------------------

FIXTURE = ROOT / "curriculum" / "canvas-fixtures" / "lab-09.json"
STATES = {"fig@initial", "fig@after-canvas-left", "fig@after-canvas-centre",
          "fig@after-canvas-right"}


def _fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_the_lab_09_fixture_is_committed_and_records_geometry_only():
    """Gate 7's execution signal. Four canvas states, each with the figure's
    structural GEOMETRY: the green bars, the grey bars, the axis and threshold
    strokes, the amber gap arrow. The `_text` marker records that it was taken
    with text suppressed."""
    data = _fixture()
    assert data["_text"] == "suppressed"
    assert set(data) - {"_text"} == STATES
    initial = data["fig@initial"]
    colours = {row["colour"] for row in initial["ink"]}
    assert "64,160,128" in colours, "the green bars the gap rule keeps"
    assert "64,64,64" in colours, "the grey bars"
    for row in initial["ink"]:
        assert len(row["bbox"]) == 4 and row["n"] > 0


def test_the_fixture_records_no_glyph_ink():
    """The first fixture recorded text, passed on the Windows machine that took
    it, and failed every Linux CI run with identical numbers: the footer text
    colour and the amber annotation colour vanished and dark anti-aliasing rose
    218 px, while both bar colours matched. `sans-serif` is a different font
    there. The footer text colour is painted by nothing but text, so its
    absence -- and every bbox stopping above the footer's text row -- is the
    evidence text was excluded."""
    for key in STATES:
        ink = _fixture()[key]["ink"]
        assert "224,224,224" not in {row["colour"] for row in ink}
        assert all(row["bbox"][3] < 291 for row in ink), key


def test_the_fixture_holds_no_anti_aliasing_fringe_rows():
    """The floor exists so the fixture pins structure, not the rasteriser."""
    for key in STATES:
        state = _fixture()[key]
        floor = max(24, round(state["painted"] * 0.02))
        for row in state["ink"]:
            assert row["n"] >= floor


def test_a_moved_bar_end_is_caught_by_the_comparison():
    """The watched failure, replayed without a browser. Run for real against
    the text-suppressed fixture: lab-09's last bar moved from 0.4950 to 0.7950,
    past the null threshold, and the read-back reported the grey bar ink
    EXTENDING from x=290 to x=345, grey coverage up to 8340 px from 7320, and
    the amber gap arrow gone. The text-bearing fixture had only ever reported
    coverage; this one sees the bar end itself. Stored numbers keep the negative
    control alive where CI has no Chrome."""
    from scripts.check_canvas_render import _compare_ink
    fixture = _fixture()["fig@initial"]
    perturbed = [dict(row) for row in fixture["ink"]
                 if row["colour"] != "224,160,96"]
    for row in perturbed:
        if row["colour"] == "64,64,64":
            row["n"] = 8340
            row["bbox"] = [120, 142, 345, 237]
    errors = _compare_ink("fig@initial", fixture["ink"], perturbed)
    assert any("64,64,64 extends to [120, 142, 345, 237]" in e for e in errors)
    assert any("64,64,64 covers 8340" in e for e in errors)
    assert any("224,160,96 is gone" in e for e in errors)


def test_the_comparison_is_quiet_on_the_fixture_itself():
    """Positive control: a check that reported differences for every input
    would pass the negative above."""
    from scripts.check_canvas_render import _compare_ink
    fixture = _fixture()["fig@initial"]
    assert _compare_ink("fig@initial", fixture["ink"], fixture["ink"]) == []


def test_a_within_tolerance_wobble_does_not_fail():
    """Anti-aliasing moves a boundary by a pixel between Chrome builds. A gate
    that fires on that is a gate nobody keeps."""
    from scripts.check_canvas_render import _compare_ink
    fixture = _fixture()["fig@initial"]
    wobbled = []
    for row in fixture["ink"]:
        moved = dict(row)
        moved["bbox"] = [row["bbox"][0] + 1, row["bbox"][1] - 1,
                         row["bbox"][2] + 2, row["bbox"][3]]
        moved["n"] = row["n"] + max(4, int(row["n"] * 0.03))
        wobbled.append(moved)
    assert _compare_ink("fig@initial", fixture["ink"], wobbled) == []


def test_the_harness_suppresses_text_only_when_asked():
    from scripts.check_canvas_render import harness
    lesson = [str(ROOT / "lessons" / "lab" / "lab-09.html")]
    assert "const suppressText=true;" in harness(lesson, suppress_text=True)
    assert "const suppressText=false;" in harness(lesson)


def test_fixtures_are_recorded_and_checked_with_text_suppressed(monkeypatch):
    import scripts.check_canvas_render as R
    seen = {}

    def fake(paths, browser=None, suppress_text=False):
        seen["suppress_text"] = suppress_text
        return []
    monkeypatch.setattr(R, "render_results", fake)
    assert R.fixture_for(["x.html"]) == {"_text": "suppressed"}
    assert seen["suppress_text"] is True


def test_the_blank_and_clipped_render_check_still_renders_text(monkeypatch,
                                                                tmp_path):
    """Suppression is for fixtures only. A figure whose only ink is text must
    still count as painted for the blank-canvas gate."""
    import scripts.check_canvas_render as R
    seen = {}

    def fake(paths, browser=None, suppress_text=False):
        seen["suppress_text"] = suppress_text
        return []
    monkeypatch.setattr(R, "render_results", fake)
    exceptions = tmp_path / "exceptions.json"
    exceptions.write_text("{}", encoding="utf-8")
    R.render_errors(["x.html"], exceptions_path=str(exceptions))
    assert seen["suppress_text"] is False


def test_a_fixture_recorded_with_text_is_refused_not_compared(monkeypatch,
                                                              tmp_path):
    """G13: a text-bearing fixture differs by platform, so comparing it would
    report the platform as a defect. It gets an explicit outcome instead."""
    import scripts.check_canvas_render as R
    (tmp_path / "lab-09.json").write_text(
        json.dumps({"fig@initial": {"painted": 1, "bbox": [0, 0, 1, 1],
                                    "ink": []}}), encoding="utf-8")
    monkeypatch.setattr(R, "FIXTURES", str(tmp_path))
    monkeypatch.setattr(R, "fixture_for", lambda *a, **k: pytest.fail(
        "an unmarked fixture must be refused before any render"))
    errors, checked = R.fixture_errors([str(ROOT / "lessons" / "lab" /
                                            "lab-09.html")])
    assert checked == 0
    assert len(errors) == 1 and "not recorded with text suppressed" in errors[0]


def test_a_missing_fixture_is_reported_not_skipped():
    """G13: an absent input has an explicit outcome. A lesson with no fixture
    must not look like a lesson that passed one."""
    from scripts.check_canvas_render import fixture_errors
    errors, checked = fixture_errors([str(ROOT / "lessons" / "top" / "top-05.html")])
    assert checked == 0
    assert len(errors) == 1 and "no read-back fixture" in errors[0]


def test_record_and_check_fixture_are_exclusive():
    result = subprocess.run(
        [sys.executable, "scripts/check_canvas_render.py", "--record-fixture",
         "--check-fixture", "lessons/lab/lab-09.html"],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert "exclusive" in (result.stderr + result.stdout)


def test_the_workflow_runs_the_read_back():
    workflow = (ROOT / ".github" / "workflows" / "quality-gates.yml").read_text(
        encoding="utf-8")
    assert "--check-fixture" in workflow


# --- Codex review of PR #32 -------------------------------------------------

def test_a_label_value_that_merely_contains_the_numeral_does_not_vouch():
    """A substring test let 0.25 or 10.2 in the label excuse a painted 0.2."""
    for label in ("The ratio is 0.25.", "The mean is 10.2.", "Version 1.0.2."):
        page = canvas_page(label, "g.fillText('short by 0.2%', 0, 0);")
        assert [n for n, _l in undescribed_canvas_numbers(page)] == ["0.2"], label


def test_a_sentence_final_decimal_in_the_label_still_counts():
    page = canvas_page("The bar ends short by 0.2.",
                       "g.fillText('short by 0.2%', 0, 0);")
    assert undescribed_canvas_numbers(page) == []


def test_the_corpus_backlog_is_unchanged_by_token_matching():
    """The stricter match found no new undescribed number in any lesson: the
    same nine are listed and lab-09 still passes."""
    import glob
    from scripts.mission import load_known_failing
    failing = set()
    for path in glob.glob(str(ROOT / "lessons" / "*" / "*.html")):
        if undescribed_canvas_numbers(Path(path).read_text(encoding="utf-8")):
            failing.add(unit_id_for(path))
    assert failing == load_known_failing(str(DRIFT))


def _lists(tmp_path, base_ids, current_ids):
    base = tmp_path / "base.txt"
    current = tmp_path / "current.txt"
    if base_ids is not None:
        base.write_text("\n".join(base_ids) + "\n", encoding="utf-8")
    if current_ids is not None:
        current.write_text("\n".join(current_ids) + "\n", encoding="utf-8")
    return str(base), str(current)


def test_a_drift_list_that_grew_fails_the_run(tmp_path, capsys):
    """The forbidden direction. Listing a freshly undescribed figure used to
    make it a known failure and leave CI green."""
    from scripts.lesson_lint import main
    base, current = _lists(tmp_path, ["an-01"], ["an-01", "an-03"])
    assert main(["--known-failing", current, "--baseline", base]) == 1
    assert "GREW an-03" in capsys.readouterr().out


def test_a_swap_that_keeps_the_count_is_still_caught(tmp_path):
    from scripts.lesson_lint import main
    base, current = _lists(tmp_path, ["an-01"], ["an-03"])
    assert main(["--known-failing", current, "--baseline", base]) == 1


def test_a_drift_list_that_shrank_or_held_passes(tmp_path, capsys):
    """Positive control for the growth check."""
    from scripts.lesson_lint import main
    base, current = _lists(tmp_path, ["an-01", "an-03"], ["an-01"])
    assert main(["--known-failing", current, "--baseline", base]) == 0
    assert "no additions" in capsys.readouterr().out


def test_deleting_the_drift_list_fails_rather_than_reopening_it(tmp_path):
    from scripts.lesson_lint import main
    base, current = _lists(tmp_path, ["an-01"], None)
    assert main(["--known-failing", current, "--baseline", base]) == 1


def test_no_baseline_is_reported_as_the_introducing_commit(tmp_path, capsys):
    from scripts.lesson_lint import main
    base, current = _lists(tmp_path, None, ["an-01"])
    assert main(["--known-failing", current, "--baseline", base]) == 0
    assert "introduces the list" in capsys.readouterr().out


def test_baseline_without_a_list_is_a_usage_error(tmp_path):
    from scripts.lesson_lint import main
    base, _current = _lists(tmp_path, ["an-01"], None)
    assert main(["--baseline", base]) == 2


def test_an_unreadable_baseline_is_verdict_2(tmp_path):
    from scripts.lesson_lint import main
    _base, current = _lists(tmp_path, None, ["an-01"])
    assert main(["--known-failing", current, "--baseline", str(tmp_path)]) == 2


def test_the_workflow_runs_the_canvas_drift_growth_check():
    workflow = (ROOT / ".github" / "workflows" / "quality-gates.yml").read_text(
        encoding="utf-8")
    assert "--baseline /tmp/canvas-drift-baseline.txt" in workflow
    assert "canvas-label-drift.txt" in workflow
