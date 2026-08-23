"""A citation asserts three things — a section, a result, and a page — and
citations.py verifies only the last two. Twenty-two citations in la-06 named
section 3.A while pointing at pages 59 to 67, which are section 3.B, and every
one of them was PASS: the result numbers were right and the folios were right.
This gate is the third assertion."""
import json

import pytest

from scripts.check_sections import (CAP, LETTERED, NUMBERED, NoVerdict,
                                    admissible, check_text, load_index, main,
                                    main_text_plateaus, pages_in, section_of,
                                    selftest, tails, unreadable)

# A None label is a gap: a chapter-opening page, or an unsectioned chapter.
# Printed 27 opens Axler's chapter 2 and printed 51 opens chapter 3.
ROWS = [(2, "1.A"), (12, "1.B"), (18, "1.C"), (27, None), (28, "2.A"),
        (39, "2.B"), (44, "2.C"), (51, None), (52, "3.A"), (59, "3.B")]


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


def test_a_chapter_opening_page_belongs_to_no_section():
    """Axler's Notation 3.1 sits on printed 51, the chapter-3 opening page:
    §2.C's exercises have ended and §3.A does not begin until 52. Citing it
    under either neighbour is wrong, and the hint says "no section"."""
    assert section_of(51, ROWS) is None
    assert check_text("Axler §3.A, Notation 3.1, p. 51", ROWS) == [
        ("3.A", 51, None)]


def test_the_label_that_runs_on_through_a_gap_is_caught():
    """Without gap rows the previous section runs on through the chapter
    opening, and a citation naming the gap page under THAT label is accepted
    — a silent pass on a page that is in no section at all."""
    no_gaps = [(44, "2.C"), (52, "3.A")]
    assert check_text("Axler §2.C, Notation 3.1, p. 51", no_gaps) == []
    assert check_text("Axler §2.C, Notation 3.1, p. 51", ROWS) == [
        ("2.C", 51, None)]


def test_an_unsectioned_chapter_is_a_gap_throughout():
    """Axler's chapter 4 has no sections. Every page of it must resolve to no
    section, not to §3.F running on from the chapter before."""
    index, _shared = load_index()["Axler"]
    assert section_of(101, index) == "3.F"
    for page in (117, 120, 131):
        assert section_of(page, index) is None
    assert section_of(132, index) == "5.A"


def test_a_section_starting_on_a_gap_page_still_wins():
    assert section_of(51, [(51, None), (51, "3.A")]) == "3.A"


def test_the_pre_gap_index_format_is_refused(tmp_path):
    """An index that cannot express a gap would answer gap questions wrongly.
    Wrong is worse than absent, so the old format is NoVerdict."""
    p = tmp_path / "old.json"
    p.write_text(json.dumps({"Axler": {"1.A": 2, "1.B": 12}}), encoding="utf-8")
    with pytest.raises(NoVerdict):
        load_index(str(p))


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
    rows, _shared = index["Axler"]
    assert rows == sorted(rows)
    starts = {lab: p for p, lab in rows}
    assert starts["3.B"] == 59
    assert starts["2.B"] == 39


def test_selftest_passes():
    assert selftest() == 0


def test_the_length_cap_never_cuts_a_page_number_in_half():
    """la-10's Sources line is one long sentence ending "pp. 101-114". The cap
    landed inside "101", the tail ended "pp. 1", and a correct citation was
    reported as naming printed page 1. A cap that silently shortens a page
    number can turn a wrong page into a plausible one just as easily."""
    long_tail = "Axler §2.A (" + "Theorem 2.7, " * 40 + "), pp. 28-38."
    assert len(long_tail) > 400
    assert check_text(long_tail, ROWS) == []
    assert 1 not in pages_in(long_tail[long_tail.index("§"):])


def test_a_citation_cut_off_before_its_page_marker_gives_no_verdict():
    """The quiet direction of the length cap. When the cap lands before the
    page marker the tail carries no page, pages_in returns nothing, and the
    citation is accepted however wrong its label is — a pass manufactured by
    not looking. Truncation is now reported instead."""
    runaway = "Axler §2.A " + "y" * (CAP + 50) + " pp. 59"
    assert check_text(runaway, ROWS) == []      # nothing to judge...
    assert unreadable(runaway) == ["2.A"]       # ...and it says so


def test_a_citation_that_reaches_its_pages_is_not_reported_unreadable():
    assert unreadable("Axler §2.A, pp. 28-38.") == []
    assert unreadable("Axler §2.A (" + "Theorem 2.7, " * 40 + "), pp. 28-38.") == []


def test_a_truncated_citation_makes_main_exit_two(tmp_path, capsys):
    """Exit 2, not 0: the check could not be performed."""
    f = tmp_path / "runaway.html"
    f.write_text("Axler §2.A " + "y" * (CAP + 50) + " pp. 59",
                 encoding="utf-8")
    assert main([str(f)]) == 2


def test_a_capped_citation_is_unreadable_even_when_a_page_survived():
    """The case the first truncation fix still lost: a correct page before the
    cut and a wrong one after it read as fully checked, and the page past the
    cut was skipped in silence."""
    both = "Axler §2.A, p. 28 " + "y" * (CAP + 50) + " pp. 59"
    assert check_text(both, ROWS) == []      # 28 is right, 59 never seen
    assert unreadable(both) == ["2.A"]


def test_the_two_heading_shapes_do_not_overlap():
    """Abbott numbers its sections and Axler letters them. Running the numbered
    pattern over Axler invents sections out of result headings — it read 10.58
    and 10.59, which are a Definition and a Theorem."""
    assert NUMBERED.search("## 1.3 The Axiom of Completeness").group(1) == "1.3"
    assert LETTERED.search("## 1.3 The Axiom of Completeness") is None
    assert LETTERED.search("### 3.B Null Spaces and Ranges").group(1) == "3.B"
    assert NUMBERED.search("### 10.58 **Definition**").group(1) == "10.58"
    assert LETTERED.search("### 10.58 **Definition**") is None
    assert NUMBERED.search("### 1.3.6 Example") is None


def test_a_bound_in_second_document_is_not_indexed():
    """Abbott's PDF carries the Instructor's Solutions Manual behind the book,
    restarting at printed 1, so printed 100 exists twice in one file. Indexing
    the second copy would move section boundaries onto pages the book has."""
    keep, drop = main_text_plateaus([(-12, 13, 269, 254), (-276, 277, 429, 150)])
    assert keep == [(-12, 13, 269, 254)]
    assert drop == [(-276, 277, 429, 150)]


def test_a_book_with_drifting_offsets_keeps_every_plateau():
    """The negative control for the rule above: Axler's three plateaus run
    forward, never repeating a printed page, and all three are kept."""
    keep, drop = main_text_plateaus([(-17, 18, 66, 49), (-16, 67, 177, 111),
                                     (-15, 178, 346, 169)])
    assert len(keep) == 3 and drop == []


def test_the_committed_abbott_index_is_the_book_not_the_manual():
    index, _shared = load_index()["Abbott"]
    starts = {lab: p for p, lab in index if lab}
    assert starts["1.3"] == 13      # The Axiom of Completeness
    assert starts["3.3"] == 84      # Compact Sets
    assert starts["8.2"] == 222     # Metric Spaces
    assert max(p for p, _lab in index) < 258


def test_a_page_shared_by_two_sections_admits_both():
    """Abbott prints Exercise 1.4.13 at the top of printed 29 and opens §1.5
    below it, so "§1.4, Exercise 1.4.13, p. 29" is a correct citation. The
    one-label rule failed it."""
    rows = [(18, "1.4"), (29, "1.5")]
    assert admissible(29, rows, shared={29}) == ["1.5", "1.4"]
    assert check_text("Abbott §1.4, Exercise 1.4.13, p. 29", rows, {29}) == []
    assert check_text("Abbott §1.5, Theorem 1.5.1, p. 29", rows, {29}) == []


def test_an_unshared_start_page_still_admits_only_its_own_section():
    """The negative control, and the gate's founding case: Axler opens §3.B at
    the top of printed 59 with nothing above it but the running head, so the
    la-06 citation "§3.A ... p. 59" must still fail."""
    rows = [(52, "3.A"), (59, "3.B")]
    assert admissible(59, rows, shared=set()) == ["3.B"]
    assert check_text("Axler §3.A, Definition 3.12, p. 59", rows) == [
        ("3.A", 59, "3.B")]


def test_the_two_books_share_pages_differently():
    """Abbott runs sections on down the page; Axler starts each on a fresh one.
    The index is generated from the books, so it says so."""
    _rows_a, shared_abbott = load_index()["Abbott"]
    _rows_x, shared_axler = load_index()["Axler"]
    assert 29 in shared_abbott and len(shared_abbott) > 20
    assert shared_axler == set()


# --- a numbered book must actually be checked, not merely indexed ----------

NUM = [(29, "1.4"), (36, "1.5"), (44, "1.6")]


def test_a_numbered_section_label_is_parsed_whole():
    """CITE read only "§N" and "§N.LETTER". Abbott's "§1.4" therefore parsed
    as the bare chapter "1", check_text skipped it as a non-claim, and every
    numbered citation in the corpus passed without being looked at — 476 of
    them in `an` alone. Indexing the book was not the same as checking it.
    (Codex review of PR #25.)"""
    assert [lab for lab, _t, _c in tails("Abbott §1.4, p. 29")] == ["1.4"]


def test_a_wrong_numbered_label_fails():
    """The negative control for the line above: if this ever passes, the
    numbered half of the gate has gone quiet again."""
    assert check_text("Abbott §9.9, p. 36", NUM) == [("9.9", 36, "1.5")]


def test_a_bare_chapter_is_still_not_judged_in_a_numbered_book():
    """Widening the label must not turn "§1" into a claim about §1.5."""
    assert check_text("Abbott §1, p. 36", NUM) == []


def test_a_two_digit_numbered_label_is_read_whole():
    assert [lab for lab, _t, _c in tails("Abbott §4.11, p. 44")] == ["4.11"]


def test_the_corpus_numbered_citations_are_actually_checked():
    """Not a tautology: this counts the citations the parser now hands to
    check_text, so a regression in CITE shows up as a collapse in the count
    rather than as a still-green PASS line."""
    labels = [lab for lab, _t, _c in
              tails("Abbott §1.3, p. 16. Abbott §2.4, pp. 59, 60.")
              if "." in lab]
    assert labels == ["1.3", "2.4"]


# --- one book per file was never true --------------------------------------

def test_a_second_book_in_one_file_is_not_checked_against_the_first(
        tmp_path, capsys):
    """pw-04 cites Abbott and Cummings in one Sources line. Attributing the
    whole file to the first indexed name it happened to contain reported all
    four Cummings citations as wrong labels in Abbott — the same mechanism
    citations.py's attribute() was written to remove. Cummings has no section
    index, so its citations are counted as unchecked and said out loud."""
    p = tmp_path / "unit.md"
    p.write_text(
        "Sources: Abbott, Understanding Analysis — §1.3, p. 16. "
        "Cummings, Real Analysis: A Long-Form Mathematics Textbook — "
        "§6.3, Definition 6.8 p. 226.", encoding="utf-8")
    assert main([str(p)]) == 0
    out = capsys.readouterr().out
    assert "FAIL" not in out
    assert "not checked" in out and "Cummings Real Analysis 1" in out


def test_an_unindexed_book_is_counted_not_silently_dropped(tmp_path, capsys):
    """Silence is the failure mode this script exists to remove. A citation
    that was parsed and then not checked is neither a pass nor a failure, and
    the report gives its count."""
    p = tmp_path / "unit.md"
    p.write_text(
        "Sources: Abbott, Understanding Analysis — §1.3, p. 16. "
        "Lindstrom, Spaces — §3.1, p. 43; §3.2, p. 48.", encoding="utf-8")
    assert main([str(p)]) == 0
    assert "Lindstrom 2" in capsys.readouterr().out


def test_the_first_book_named_still_wins_before_any_name():
    """Attribution is sticky and left to right. Text before any book name
    belongs to nothing yet and must not be charged to a book chosen by
    alphabetical accident."""
    from scripts.check_sections import _attribution
    names, titles, split = _attribution()
    parts = split("§1.3, p. 16. Abbott — §1.4, p. 29", names, titles)
    assert parts[0][1] is None
    assert parts[-1][1] == "Abbott"


# --- the heading shape is chosen by one match, not two ---------------------

def test_one_lettered_heading_selects_the_lettered_shape():
    """`lettered >= 2` contradicted the rule stated beside it — the lettered
    pattern wins outright if it finds ANYTHING. A book with a single lettered
    section fell through to NUMBERED, matched nothing, and raised NoVerdict.
    (CodeRabbit review of PR #25.)"""
    one = "## 3.B Null Spaces and Ranges\n"
    assert len(LETTERED.findall(one)) == 1
    assert NUMBERED.findall(one) == []
