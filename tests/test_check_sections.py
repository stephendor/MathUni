"""A citation asserts three things — a section, a result, and a page — and
citations.py verifies only the last two. Twenty-two citations in la-06 named
section 3.A while pointing at pages 59 to 67, which are section 3.B, and every
one of them was PASS: the result numbers were right and the folios were right.
This gate is the third assertion."""
import json

import pytest

from scripts.check_sections import (NoVerdict, check_text, load_index, main,
                                    pages_in, section_of, selftest)

ROWS = [(2, "1.A"), (12, "1.B"), (18, "1.C"), (28, "2.A"), (39, "2.B"),
        (44, "2.C"), (52, "3.A"), (59, "3.B")]


# --- the defect the gate was built for -------------------------------------

def test_the_defect_this_gate_was_built_for_fires():
    """la-06's citations, verbatim in shape: correct result, correct folio,
    wrong section."""
    cite = '<span class="cite">— Axler §3.A, Definition 3.12, p. 59</span>'
    assert check_text(cite, ROWS) == [("3.A", 59, "3.B")]


def test_the_repaired_citation_passes():
    cite = '<span class="cite">— Axler §3.B, Definition 3.12, p. 59</span>'
    assert check_text(cite, ROWS) == []


# --- boundaries ------------------------------------------------------------

def test_a_section_owns_its_own_first_page():
    assert section_of(39, ROWS) == "2.B"
    assert section_of(38, ROWS) == "2.A"


def test_a_page_before_the_first_section_is_unplaceable():
    assert section_of(1, ROWS) is None


def test_a_chapter_opening_page_is_still_reported_as_wrong():
    """Axler's Notation 3.1 sits on printed 51, the chapter-3 opening page,
    which belongs to no section — §2.C's exercises have ended and §3.A does
    not begin until 52. The citation "§3.A ... p. 51" is therefore wrong and
    is reported. The index knows only where sections START, so the hint names
    §2.C rather than "no section"; that limit is documented in section_of and
    does not affect the verdict."""
    assert check_text("Axler §3.A, Notation 3.1, p. 51", ROWS) == [
        ("3.A", 51, "2.C")]


def test_a_range_is_checked_at_both_ends():
    """la-01's set claimed §1.B, pp. 12-18. Section 1.C begins at 18, so the
    far end of the range was in the wrong section while the near end was
    right — and matching only the first number never saw it."""
    assert check_text("Axler §1.B, pp. 12–18", ROWS) == [("1.B", 18, "1.C")]
    assert check_text("Axler §1.B, pp. 12–17", ROWS) == []


def test_a_following_sentence_is_not_charged_to_this_label():
    """la-04's footer names §2.A p. 35 in one sentence and 2.C results with
    pp. 44-46 in the next. Letting the tail run past the full stop reports the
    second sentence's pages against the first sentence's section."""
    text = ("Theorem 2.23 is Axler §2.A, p. 35. That result drives Theorems "
            "2.35 and 2.39 above, pp. 44–46.")
    assert check_text(text, ROWS) == []


def test_a_bare_chapter_number_is_not_judged():
    """"§4" claims a chapter, not a section, so there is nothing to compare."""
    assert check_text("Axler §4, p. 30", ROWS) == []


def test_a_number_without_a_page_marker_is_not_a_page():
    assert pages_in("Theorem 2.23, and 40 more like it") == []
    assert pages_in("p. 35") == [35]


# --- absence must not look like cleanliness --------------------------------

def test_a_missing_index_gives_no_verdict_not_a_pass():
    with pytest.raises(NoVerdict):
        load_index("resources/definitely-not-here.json")


def test_an_empty_index_gives_no_verdict(tmp_path):
    p = tmp_path / "sections.json"
    p.write_text(json.dumps({"Axler": {}}), encoding="utf-8")
    with pytest.raises(NoVerdict):
        load_index(str(p))


def test_a_file_naming_no_indexed_book_is_skipped_not_passed(tmp_path, capsys):
    """A file citing a book the index does not cover must not be counted as
    checked. If NO file names an indexed book the run has no verdict at
    all — exit 2, never 0."""
    p = tmp_path / "unit.md"
    p.write_text("Sources: Hatcher, Algebraic Topology, p. 30", encoding="utf-8")
    assert main([str(p)]) == 2
    assert "SKIP" in capsys.readouterr().out


# --- the committed index ---------------------------------------------------

def test_the_committed_index_is_readable_and_ordered():
    index = load_index()
    assert "Axler" in index
    rows = index["Axler"]
    assert rows == sorted(rows)
    starts = {lab: p for p, lab in rows}
    assert starts["3.B"] == 59
    assert starts["2.B"] == 39


def test_selftest_passes():
    assert selftest() == 0
