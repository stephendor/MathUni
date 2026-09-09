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


def test_the_lab_09_fixture_is_committed_and_records_real_structure():
    """Gate 7's execution signal. Four canvas states, each with the figure's
    structural ink: the green bar colour, the grey bar and label colour, the
    near-black axis colour, the amber annotation, the light-grey footer."""
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert set(data) == {"fig@initial", "fig@after-canvas-left",
                         "fig@after-canvas-centre", "fig@after-canvas-right"}
    initial = data["fig@initial"]
    assert initial["painted"] > 20000
    assert len(initial["ink"]) == 5
    colours = {row["colour"] for row in initial["ink"]}
    assert "64,160,128" in colours, "the green the gap rule keeps"
    assert "224,160,96" in colours, "the amber annotation"
    for row in initial["ink"]:
        assert len(row["bbox"]) == 4 and row["n"] > 0


def test_the_fixture_holds_no_anti_aliasing_fringe_rows():
    """The floor exists so the fixture pins structure, not the rasteriser: a
    blend colour that appears on the next Chrome release must not be able to
    fail the gate."""
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for state in data.values():
        floor = max(24, round(state["painted"] * 0.02))
        for row in state["ink"]:
            assert row["n"] >= floor


def test_a_moved_bar_end_is_caught_by_the_comparison():
    """The watched failure, replayed against the committed fixture without a
    browser: lab-09's last bar was moved from 0.4950 to 0.7950 — past the null
    threshold, changing what the figure claims — and the read-back reported the
    footer's light grey gone and the grey coverage up by 1005 px. Preserved as
    stored numbers so the negative control survives without Chrome, which the
    live check needs and CI may not always have."""
    from scripts.check_canvas_render import _compare_ink
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fig@initial"]
    perturbed = [dict(row) for row in fixture["ink"]
                 if row["colour"] != "224,224,224"]
    for row in perturbed:
        if row["colour"] == "64,64,64":
            row["n"] = 8698
    errors = _compare_ink("fig@initial", fixture["ink"], perturbed)
    assert any("224,224,224 is gone" in e for e in errors)
    assert any("64,64,64 covers 8698" in e for e in errors)


def test_the_comparison_is_quiet_on_the_fixture_itself():
    """Positive control: a check that reported differences for every input
    would pass the negative above."""
    from scripts.check_canvas_render import _compare_ink
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fig@initial"]
    assert _compare_ink("fig@initial", fixture["ink"], fixture["ink"]) == []


def test_a_within_tolerance_wobble_does_not_fail():
    """Anti-aliasing moves a boundary by a pixel between Chrome builds. A gate
    that fires on that is a gate nobody keeps."""
    from scripts.check_canvas_render import _compare_ink
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fig@initial"]
    wobbled = []
    for row in fixture["ink"]:
        moved = dict(row)
        moved["bbox"] = [row["bbox"][0] + 1, row["bbox"][1] - 1,
                         row["bbox"][2] + 2, row["bbox"][3]]
        moved["n"] = row["n"] + max(4, int(row["n"] * 0.03))
        wobbled.append(moved)
    assert _compare_ink("fig@initial", fixture["ink"], wobbled) == []


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
