"""A citation asserts three things — a section, a result, and a page — and
citations.py verifies only the last two. Twenty-two citations in la-06 named
section 3.A while pointing at pages 59 to 67, which are section 3.B, and every
one of them was PASS: the result numbers were right and the folios were right.
This gate is the third assertion."""
import json

import pytest

from scripts.check_sections import (ALUFFI_LOCAL_SECTION, ALUFFI_SUBSECTION,
                                    BARE_SECTION, CAP, LETTERED, NUMBERED,
                                    HIERARCHICAL_SECTION, NUMBERED_SECTION, ROMAN_SECTION,
                                    RUNNING_SECTION, NoVerdict,
                                    _primary, admissible, check_text,
                                    extend_first_plateau, load_index, main,
                                    main_text_plateaus, pages_in, section_of,
                                    selftest, span, tails, uncovered,
                                    unreadable)

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


def test_refresh_heading_shapes_cover_trailing_dots_and_running_heads():
    assert NUMBERED_SECTION.search(
        "## 3.1. Definitions and examples").group(1) == "3.1"
    assert RUNNING_SECTION.search("Section 1.1").group(1) == "1.1"
    assert ROMAN_SECTION.search("### III.1 Simplicial Complexes").group(1) == "III.1"
    assert BARE_SECTION.search("## §46 Pointwise Convergence").group(1) == "46"
    assert HIERARCHICAL_SECTION.search(
        "### 11.1.1 Persistence modules").group(1) == "11.1.1"
    assert ALUFFI_LOCAL_SECTION.search("## 5. Universal properties").group(1) == "5"
    assert ALUFFI_SUBSECTION.search(
        "**1.3. When are two categories equivalent?**").group(1) == "1.3"


def test_refresh_safe_numbered_shape_rejects_result_headings():
    assert NUMBERED.search("### 10.58 **Definition**").group(1) == "10.58"
    assert NUMBERED_SECTION.search("### 10.58 **Definition**") is None
    assert ROMAN_SECTION.search("### III.1.16 **Remark**") is None


def test_a_bare_label_is_judged_when_the_book_indexes_bare_sections():
    rows = [(1, "45"), (10, "46")]
    assert check_text("Munkres §45, p. 10", rows) == [("45", 10, "46")]


def test_a_unique_chapter_qualified_suffix_resolves_local_section_notation():
    rows = [(1, "I.3.2"), (10, "VIII.1.3")]
    assert check_text("Aluffi §3.2, p. 1", rows) == []
    assert check_text("Aluffi §1.3, p. 10", rows) == []


def test_chapter_qualified_range_inherits_abbreviated_far_endpoint():
    rows = [(483, "VIII.1.1"), (485, "VIII.1.2"), (487, "VIII.1.3")]
    assert check_text("Aluffi §VIII.1.1–1.3, pp. 484–487", rows) == []


def test_a_new_chapter_reference_ends_the_previous_section_citation():
    parsed = tails("Cummings §2.2, p. 41; ch. 6 opener, p. 198")
    assert pages_in(parsed[0][1]) == [41]


def test_hierarchical_and_roman_chapter_section_labels_are_parsed_whole():
    assert [x[0] for x in tails("Oudot §2.1.1, p. 29")] == ["2.1.1"]
    assert [x[0] for x in tails("Aluffi §VIII.1.3, p. 492")] == ["VIII.1.3"]


def test_source_specific_heading_grammars_do_not_treat_axler_results_as_sections():
    from scripts.check_sections import BOOK_SECTION_HEADINGS, HIERARCHICAL_SECTION

    axler = "### 1.3 Description of vector spaces\n## 1.B Definition of vector space"
    assert [m.group(1) for pattern in BOOK_SECTION_HEADINGS["Axler"]
            for m in pattern.finditer(axler)] == ["1.B"]
    assert HIERARCHICAL_SECTION.search("#### 3.3.2 Functors").group(1) == "3.3.2"


def test_underground_accepts_a_section_title_beginning_with_definition():
    from scripts.check_sections import BOOK_SECTION_HEADINGS

    text = "## 3.1 Definition and Examples"
    matches = [m.group(1) for pattern in BOOK_SECTION_HEADINGS["Aluffi Underground"]
               for m in pattern.finditer(text)]
    assert matches == ["3.1"]


def test_a_parent_section_citation_covers_its_numbered_subsections():
    rows = [(1, "4.3"), (2, "4.3.1"), (5, "4.3.2")]
    assert check_text("Dey §4.3, p. 5", rows) == []


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


def test_sentence_boundary_contract_ignores_book_abbreviations():
    """`ed.` is not an excuse to drop the later page from the denominator."""
    text = "Axler §1.B, Cummings 2nd ed. Theorem 2.3, p. 20."
    assert check_text(text, ROWS) == [("1.B", 20, "1.C")]


def test_a_bare_chapter_number_is_not_judged():
    """"§4" claims a chapter, not a section, so there is nothing to compare."""
    assert check_text("Axler §4, p. 30", ROWS) == []


def test_a_number_without_a_page_marker_is_not_a_page():
    assert pages_in("Theorem 2.23, and 40 more like it") == []
    assert pages_in("p. 35") == [35]
    assert pages_in("printed **35–37**") == [35, 37]


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


def test_unpaged_section_does_not_absorb_the_next_paragraph_pages():
    text = "Problem 2 to §3.5 asks for a proof.\n\n*(Lindstrom p. 63.)*"
    assert pages_in(tails(text)[0][1]) == []


def test_section_tail_stops_at_the_next_lettered_problem_part():
    text = "Use §14, p. 84.\n(d) Read Exercise 19 (p. 102)."
    assert pages_in(tails(text)[0][1]) == [84]


def test_terminal_section_label_does_not_absorb_the_next_sentence_pages():
    text = "Compare §3.7. Lindstrom restates it on printed 107."
    assert pages_in(tails(text)[0][1]) == []


def test_section_does_not_absorb_pages_after_a_named_source_switch():
    import re

    text = "See §4.8 (next unit); Abbott's Definition is on printed 224."
    abbott = re.compile(r"\bAbbott\b", re.I)
    assert pages_in(tails(text, [abbott])[0][1]) == []


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


def test_pageless_section_mention_is_not_in_the_checked_denominator(
        tmp_path, capsys):
    p = tmp_path / "unit.md"
    p.write_text("Abbott §1.3 discusses completeness.", encoding="utf-8")
    assert main([str(p)]) == 2
    assert "citation(s) checked" not in capsys.readouterr().out


# --- one book per file was never true --------------------------------------

def without_index(monkeypatch, book):
    """Keep unindexed-source behavior tests independent of corpus growth."""
    import scripts.check_sections as sections
    real = sections.load_index

    def load():
        index = real()
        index.pop(book, None)
        return index

    monkeypatch.setattr(sections, "load_index", load)


def test_a_second_book_in_one_file_is_not_checked_against_the_first(
        tmp_path, monkeypatch, capsys):
    """pw-04 cites Abbott and Cummings in one Sources line. Attributing the
    whole file to the first indexed name it happened to contain reported all
    four Cummings citations as wrong labels in Abbott — the same mechanism
    citations.py's attribute() was written to remove. Cummings has no section
    index, so its citations are counted as unchecked and said out loud."""
    without_index(monkeypatch, "Cummings Real Analysis")
    p = tmp_path / "unit.md"
    p.write_text(
        "Sources: Abbott, Understanding Analysis — §1.3, p. 16. "
        "Cummings, Real Analysis: A Long-Form Mathematics Textbook — "
        "§6.3, Definition 6.8 p. 226.", encoding="utf-8")
    assert main([str(p)]) == 0
    out = capsys.readouterr().out
    assert "FAIL" not in out
    assert "not checked" in out and "Cummings Real Analysis 1" in out


def test_an_unindexed_book_is_counted_not_silently_dropped(
        tmp_path, monkeypatch, capsys):
    """Silence is the failure mode this script exists to remove. A citation
    that was parsed and then not checked is neither a pass nor a failure, and
    the report gives its count."""
    without_index(monkeypatch, "Lindstrom")
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


# --- a gap page is never a shared page -------------------------------------

# Abbott's printed 213 as the committed index recorded it: the chapter-8
# opening page, which is both a gap and a section start, and which refresh
# also marked shared because the chapter title and epigraph sit above the
# heading and look like a previous section running on.
GAP_SHARE = [(210, "7.7"), (213, None), (213, "8.1")]


def test_a_gap_page_does_not_admit_the_label_from_before_the_gap():
    """Sharing and a gap say opposite things about the same page — "the
    previous section runs on into this" against "nothing from before is in
    force here". The gap is read off the book's structure, the sharing off a
    character count, and the character count is the one that misfires on a
    chapter opening. (Codex review of PR #25.)"""
    assert admissible(213, GAP_SHARE, {213}) == ["8.1"]


def test_the_label_that_ran_on_through_a_gap_is_caught_even_when_shared():
    """The negative control. This gate's whole purpose is that a section does
    not run on past its end; `shared` must not be able to buy that back."""
    assert (check_text("Abbott §7.7, p. 213", GAP_SHARE, {213})
            == [("7.7", 213, "8.1")])


def test_a_section_starting_on_a_gap_page_is_still_citable_there():
    """The other direction: the guard must not cost the page its own label."""
    assert check_text("Abbott §8.1, p. 213", GAP_SHARE, {213}) == []


def test_a_genuinely_shared_page_still_admits_both():
    """Printed 29 is shared and is not a gap, so the relaxation still applies
    and Abbott's `§1.4, Exercise 1.4.13, p. 29` still passes."""
    rows, shared = load_index()["Abbott"]
    assert check_text("Abbott §1.4, Exercise 1.4.13, p. 29", rows, shared) == []


def test_two_sections_starting_on_a_shared_page_are_both_admissible():
    rows = [(31, "I.5.1"), (33, "I.5.2"), (33, "I.5.3")]
    assert admissible(33, rows, {33}) == ["I.5.3", "I.5.2"]


def test_the_committed_index_marks_no_page_both_gap_and_shared():
    """Belt and braces: `admissible` guards against a stale index, and refresh
    no longer produces one. If this fails, the index was regenerated by a
    build that lost the `shared -= set(gaps)` line."""
    index = json.loads(open("resources/sections.json", encoding="utf-8").read())
    for book, v in index.items():
        assert not (set(v["shared"]) & set(v["gaps"])), book


# --- the unchecked count must not itself be short --------------------------

def test_a_file_citing_only_an_unindexed_book_still_counts_its_citations(
        tmp_path, monkeypatch, capsys):
    """The skip used to happen before the split, so a file citing only an
    unindexed book was printed as SKIP and its citations vanished from the
    NOTE line -- which exists precisely to be the honest denominator for the
    PASS line above it. Corpus-wide it reported 195 when the true figure was
    1432 in 112 files. (CodeRabbit review of PR #25.)"""
    without_index(monkeypatch, "Lindstrom")
    only = tmp_path / "only.md"
    only.write_text("Sources: Lindstrom, Spaces — §3.1, p. 43; §3.2, p. 48.",
                    encoding="utf-8")
    indexed = tmp_path / "indexed.md"
    indexed.write_text("Sources: Abbott — §1.3, p. 16.", encoding="utf-8")
    assert main([str(only), str(indexed)]) == 0
    out = capsys.readouterr().out
    assert "SKIP" in out                 # still reported as unchecked...
    assert "Lindstrom 2" in out          # ...and still counted
    assert "1 file(s) checked" in out    # but not counted as checked
    assert "1 citation(s) checked, 2 unchecked" in out


def test_a_broken_attribution_splitter_cannot_drop_the_independent_parse(
        tmp_path, monkeypatch, capsys):
    """Parsed citations survive even if attribution returns no segments."""
    import scripts.check_sections as sections

    p = tmp_path / "unit.md"
    p.write_text("Abbott — §1.3, p. 16.", encoding="utf-8")
    monkeypatch.setattr(
        sections, "_attribution",
        lambda: (["Abbott"], {"Abbott": "Abbott"}, lambda *_args: []))
    assert sections.main([str(p)]) == 2
    out = capsys.readouterr()
    assert "citation partition mismatch" not in out.err
    assert "no file named an indexed book" in out.err


def test_a_citation_naming_no_book_is_counted_separately(tmp_path, capsys):
    """A citation before any book name belongs to nothing. It is neither
    checked nor attributable, and saying so is not the same as saying it names
    an unindexed book."""
    p = tmp_path / "unit.md"
    p.write_text("§9.9, p. 400. Abbott — §1.3, p. 16.", encoding="utf-8")
    assert main([str(p)]) == 0
    out = capsys.readouterr().out
    assert "1 citation(s) name no book at all" in out


def test_no_checkable_file_is_still_no_verdict(tmp_path, monkeypatch, capsys):
    """Counting a file's citations must not make it look checked. Two files
    naming only an unindexed book are both SKIPped and the run has no verdict
    at all -- exit 2, never a PASS over an empty set."""
    without_index(monkeypatch, "Hatcher")
    for name in ("a.md", "b.md"):
        (tmp_path / name).write_text(
            "Sources: Hatcher — §1.1, p. 30; §1.2, p. 40.", encoding="utf-8")
    assert main([str(tmp_path / "a.md"), str(tmp_path / "b.md")]) == 2
    out = capsys.readouterr().out
    assert out.count("SKIP") == 2
    assert "PASS" not in out


# --- a section range is one label naming several sections -------------------

RANGE = [(3, "1.1"), (4, "1.2"), (5, "1.3"), (6, "1.4"), (7, "1.5")]


def test_a_range_covers_every_section_between_its_ends():
    assert span("1.2–1.5", RANGE) == ["1.2", "1.3", "1.4", "1.5"]


def test_a_page_in_the_later_half_of_a_range_is_right():
    """Carter's Sources line names §1.2–1.5 over printed 4–7. Read as the
    single label §1.2, printed 7 -- which is §1.5 -- was reported wrong, and
    four citations failed in one unit with nothing wrong with any of them."""
    assert check_text("Carter §1.2–1.5, pp. 4–7", RANGE) == []


def test_a_page_outside_the_range_is_still_wrong():
    """The negative control. A range must not become a way of naming every
    section at once: printed 7 is outside §1.2–1.3 and still fails."""
    assert check_text("Carter §1.2–1.3, p. 7", RANGE) == [("1.2–1.3", 7, "1.5")]


def test_a_range_end_the_book_does_not_have_is_not_resolved():
    """Sections do not always run consecutively, so the run is read off the
    index rather than counted out. An end that is not in the index leaves the
    label alone, to fail loudly rather than resolve to something plausible."""
    assert span("1.2–1.9", RANGE) == ["1.2–1.9"]
    assert check_text("Carter §1.2–1.9, p. 4", RANGE) != []


def test_a_dash_before_a_word_is_not_a_range():
    assert [lab for lab, _t, _c in tails("Carter §1.4 - the rules, p. 6")] \
        == ["1.4"]


# --- the folio-less run at the lower edge of the first plateau --------------

def test_the_first_plateau_reaches_down_over_folio_less_pages():
    """Aluffi's chapter-1 opening page carries §1.1 and no folio, and it sits
    one page below the first folio the fit could read. §1.1 was missing from a
    76-section index in silence, and the correct citation "§1.1, p. 3" was the
    thing that failed."""
    assert extend_first_plateau([(-18, 22, 384, 350)], {19, 20, 21}) \
        == [(-18, 19, 384, 350)]


def test_the_extension_stops_where_printed_page_1_would():
    """Front matter numbered in roman also reads as folio-less. Without the
    guard a plateau swallows the introduction and hands it printed page 0."""
    assert extend_first_plateau([(-18, 22, 384, 350)],
                                set(range(1, 22)))[0][1] == 19


def test_the_extension_does_not_cross_a_page_whose_folio_was_read():
    """The negative control: page 21 is not blank, so nothing moves."""
    assert extend_first_plateau([(-18, 22, 384, 350)], {19, 20}) \
        == [(-18, 22, 384, 350)]


def test_a_later_plateau_is_left_alone_and_its_orphans_are_reported():
    """A blank run between two plateaus could belong to either offset, and
    the page tree does not say which. Those pages are reported, not guessed
    at -- a heading on one of them is absent from the index."""
    ps = [(-17, 18, 66, 49), (-16, 70, 177, 111)]
    assert extend_first_plateau(ps, {67, 68, 69}) == ps
    assert uncovered(ps) == [67, 68, 69]


def test_abutting_plateaus_have_no_orphans():
    assert uncovered([(-17, 18, 66, 49), (-16, 67, 177, 111)]) == []


# --- the two gates now agree on which book a file is about ------------------

def test_the_primary_book_comes_from_the_syllabus():
    """citations.py reads the unit's primary book from the syllabus resource
    line and lets an unnamed clause stay with it; this gate started at None
    and waited to be told. A lesson writing "Aluffi §1.1, p. 5" throughout
    therefore passed one gate and was SKIPped whole by the other."""
    assert _primary("lessons/aa/aa-01.html") == "Aluffi Underground"
    assert _primary("problems/sets/aa-01.md") == "Aluffi Underground"


def test_a_file_that_is_no_unit_still_has_no_primary():
    """The negative control: nothing invents a book for a file the syllabus
    does not know."""
    assert _primary("notes/scratch.md") is None


def test_a_bare_count_after_a_dash_is_not_a_range_endpoint():
    """The first range grammar allowed any number after the dash, so prose
    reading "§1.4 — 4 rules" parsed as the label "1.4 — 4", span() could not
    resolve it, and a correct citation was reported wrong. The negative
    control written alongside it used a WORD after the dash and could never
    have fired. Both ends of a range must now have the same shape.
    (Codex, PR #26.)"""
    assert [lab for lab, _t, _c in tails("Carter §1.4 — 4 rules, p. 6")] \
        == ["1.4"]
    assert check_text("Carter §1.4 — 4 rules, p. 6", RANGE) == []
    # ...while a genuine range is still read as one.
    assert [lab for lab, _t, _c in tails("Carter §1.2–1.5, pp. 4–7")] \
        == ["1.2–1.5"]
