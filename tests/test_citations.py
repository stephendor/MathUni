"""The citation gate: does the page a lesson cites hold the result it names?

Synthetic throughout — CI has no access to the book drive. Four of these tests
exist because the gate was WRONG in that exact way first, each time inverting
a whole module's verdict while the citations under it were correct:

  * Axler prints "1.8 Definition", not "Definition 1.8"      (order)
  * Axler heads most results with no kind word at all        (labelling)
  * Aluffi sets headers in small caps, "DEFINITION 1.1"      (case)
  * Abbott numbers three deep, "Lemma 1.3.7"                 (truncation)

The first three produced false FAILs — 21 of 21 on la-01 at one point. The
fourth produced false PASSes, which is worse, and closing it immediately
surfaced three more real defects in an-01 that truncation had been hiding.
"""
import os

from scripts.citations import (book_label_for, found_on_page, normalise_for_search,
                               printed_pages_in, results_in, selftest, spans)


# --- reading citations out of a file ---------------------------------------

def test_result_and_page_are_extracted():
    assert results_in("Cummings §7.4, Theorem 7.6, p. 225") == ["Theorem 7.6"]
    assert printed_pages_in("p. 225") == {225}


def test_page_ranges_expand_with_either_dash():
    assert printed_pages_in("pp. 220–221") == {220, 221}
    assert printed_pages_in("pp. 41-42") == {41, 42}


def test_an_absurd_range_does_not_expand():
    assert printed_pages_in("pp. 12-9000") == {12}
    assert printed_pages_in("pp. 40-20") == {40}


def test_three_level_numbers_are_captured_whole():
    """Abbott. Truncating to two components turns a wrong citation into a
    passing one — the only false-PASS bug of the four, and the one that was
    hiding three real defects in an-01."""
    assert results_in("Lemma 1.3.7, p. 16") == ["Lemma 1.3.7"]
    assert results_in("Theorem 2.4.2 and Exercise 1.3.6, pp. 40-41") == [
        "Exercise 1.3.6", "Theorem 2.4.2"]


def test_a_span_needs_both_a_result_and_a_page_to_be_checkable():
    assert printed_pages_in("Cummings §7.4, Theorem 7.6") == set()
    assert not any("Theorem 9.9" in s for s, _ in spans("*(see Theorem 9.9)*"))


def test_cite_spans_are_found_in_html_and_markdown():
    assert spans('<span class="cite">— Cummings §7.4, p. 224</span>')
    assert spans("*(Cummings, Exercise 2.6, p. 69)*")


# --- matching a citation against the printed page --------------------------

def test_kind_first_printing_matches():
    """Cummings, Abbott."""
    assert found_on_page("Definition 2.2",
                         "an integer n is even. definition 2.2 says") == "exact"


def test_number_first_printing_matches():
    """Axler, Aluffi. Matching only the citation's own word order called 21 of
    21 la-01 citations wrong while all 21 were right."""
    assert found_on_page("Definition 1.8",
                         "1.8 definition list, length suppose n") == "exact"


def test_small_caps_printing_matches():
    """Aluffi sets result headers in small caps."""
    assert found_on_page("Definition 1.1", "DEFINITION 1.1 Let a, b be in Z".lower()) \
        == "exact"


def test_case_insensitivity_does_not_let_a_wrong_number_pass():
    assert found_on_page("Lemma 1.9", "lemma 1.2 if b divides a") is None


def test_a_sibling_result_is_not_accepted():
    assert found_on_page("Lemma 1.3.7", "lemma 1.3.9 assume s is an upper bound",
                         "**Lemma 1.3.9** Assume s") is None
    assert found_on_page("Theorem 1.13", "1.130 theorem and 1.1 theorem") is None


def test_an_item_letter_is_stripped():
    """"Exercise 2.5(a)" prints as "Exercise 2.5." with an (a) item beneath."""
    assert found_on_page("Exercise 2.5a",
                         "exercise 2.5. prove the following. (a)") == "exact"


# --- location vs labelling --------------------------------------------------

AXLER = "### 1.34 Conditions for a subspace\n\nA subset U of V is a subspace..."


def test_a_result_the_book_does_not_call_a_theorem_is_located_not_failed():
    """Axler heads most results with a number and a descriptive title and no
    kind word. "Theorem 1.34" is right about the page and loose about the name;
    that is a warning, and calling it a wrong page marked 19 correct citations
    across la-01 and la-02 as defects."""
    assert found_on_page("Theorem 1.34", normalise_for_search(AXLER), AXLER) \
        == "number-only"
    assert book_label_for("1.34", AXLER) == "Conditions for a subspace"


def test_an_exact_match_outranks_the_number_only_path():
    src = "### 1.32 Definition subspace"
    assert found_on_page("Definition 1.32", normalise_for_search(src), src) == "exact"


def test_a_number_that_is_not_a_header_is_still_a_failure():
    """The lenient path must not become "any digits on the page will do"."""
    prose = "we mention 9.9 in passing here"
    assert found_on_page("Theorem 9.9", prose, prose) is None
    assert book_label_for("9.9", "as shown in 9.9 above, the result") is None


# --- formatting robustness --------------------------------------------------

def test_markdown_emphasis_and_line_breaks_do_not_hide_a_result():
    assert "Theorem 7.6" in normalise_for_search("**Theorem 7.6.** The number")
    assert "Theorem 7.6" in normalise_for_search("Theorem\n7.6. The number")


def test_selftest_passes():
    assert selftest() == 0


# --- the s1-pw round: four ways a citation went unchecked -------------------

def test_a_sources_line_is_one_assertion_per_clause():
    """Taking the union of every page in a multi-clause Sources line gave each
    result a 20-page target. pw-02's header passed with its exercise pages
    wrong by five."""
    from scripts.citations import clauses, results_in
    line = ("§4.3 (Theorem 4.8), pp. 124-133; "
            "§4 chapter exercises (Exercise 4.1), pp. 148-149")
    by_clause = {r: pages for text, pages in clauses(line)
                 for r in results_in(text)}
    assert by_clause["Theorem 4.8"] == set(range(124, 134))
    assert by_clause["Exercise 4.1"] == {148, 149}


def test_an_unpunctuated_span_stays_one_assertion():
    from scripts.citations import clauses
    assert [p for _, p in clauses("Cummings §4.3, Theorem 4.8, pp. 125-127")] \
        == [{125, 126, 127}]


def test_a_parenthesised_exercise_part_does_not_end_the_span():
    """`[^)]` cut the span at the first ')', so `Exercise 8.28(d), p. 280` lost
    its page reference and the citation left the denominator silently."""
    from scripts.citations import printed_pages_in, results_in, spans
    got = spans("*(Cummings, Exercise 8.28(d), p. 280)*")
    assert got, "the span was not recognised at all"
    assert results_in(got[0][0]) == ["Exercise 8.28"]
    assert printed_pages_in(got[0][0]) == {280}


def test_a_plural_citation_is_expanded_not_skipped():
    """190 citations in the corpus are written in the plural or as a range and
    matched nothing at all. A RANGE expands to every member it denotes; a LIST
    contributes only what is written — see test_a_range_expands_but_a_list_does_not
    for why those are different questions."""
    from scripts.citations import results_in
    assert results_in("Propositions 2.4, 2.6") == ["Proposition 2.4",
                                                   "Proposition 2.6"]
    assert results_in("Exercises 6.6-6.9") ==         ["Exercise 6.%d" % i for i in range(6, 10)]
    assert results_in("Theorems 1.1 and 1.2") == ["Theorem 1.1", "Theorem 1.2"]


def test_a_clause_is_checked_against_the_book_it_names():
    """A Sources line naming two books had every citation checked against the
    unit's primary one; tda1-01's six Oudot results were reported missing from
    Edelsbrunner. Attribution is sticky, so a clause that names no book
    continues the last one named."""
    from scripts.citations import attribute
    names = ["Edelsbrunner", "Oudot", "Cummings", "Cummings Real Analysis"]
    text = ("**Sources:** Edelsbrunner and Harer — §III.1, pp. 62-68;\n"
            "Oudot, *Persistence Theory* — Chapter 2, pp. 29-34;\n"
            "Definition 2.1 of a filtration, p. 29\n\n")
    got = {r: name for span, _pages, _line, name in attribute(text, "Edelsbrunner", names)
           for r in [span]}
    assert any("Definition 2.1" in span and name == "Oudot"
               for span, name in got.items())


def test_the_two_cummings_volumes_are_told_apart():
    from scripts.citations import book_named_in
    names = ["Cummings", "Cummings Real Analysis", "Abbott"]
    assert book_named_in("Cummings, *Proofs*, Ch. 8", names) == "Cummings"
    assert book_named_in("Cummings, *Real Analysis*, Ch. 2", names) \
        == "Cummings Real Analysis"


# --- Codex review of PR #21 ------------------------------------------------

def test_a_cited_number_does_not_match_a_longer_sibling():
    """A substring test approved a citation to any result extending the cited
    number — Theorem 1.13 against a page printing only Theorem 1.130. A false
    PASS in the worst place: the sibling result is what a mistyped citation
    lands on."""
    from scripts.citations import found_on_page
    assert found_on_page("Theorem 1.13", "theorem 1.130 statement") is None
    assert found_on_page("Exercise 2.5", "exercise 2.50 do this") is None
    assert found_on_page("Lemma 1.3.7", "lemma 1.3.70 x") is None
    assert found_on_page("Theorem 1.13", "theorem 1.13 statement") == "exact"


def test_a_trailing_period_is_not_a_further_level():
    """The boundary guard must exclude a further dotted level, not a sentence
    period: Cummings prints "Exercise 2.5." for the exercise cited as 2.5(a)."""
    from scripts.citations import found_on_page, results_in
    assert found_on_page("Exercise 2.5a", "exercise 2.5. with parts") == "exact"
    assert results_in("Theorem 6.11.") == ["Theorem 6.11"]


def test_integer_only_result_numbers_are_parsed():
    """Axler and Lindström number exercises without a dot. Requiring one left
    237 such citations inside citation spans matching nothing at all."""
    from scripts.citations import found_on_page, results_in
    assert results_in("Axler Exercise 10, p. 24") == ["Exercise 10"]
    assert results_in("Exercises 1, 2") == ["Exercise 1", "Exercise 2"]
    assert found_on_page("Exercise 10", "exercise 100 blah") is None
    assert found_on_page("Exercise 10", "exercise 10. blah") == "exact"


def test_a_dotted_number_is_never_captured_as_its_first_part():
    """Allowing bare integers must not let "Theorem 6.11" be read as
    "Theorem 6" — the dotted alternative is tried first."""
    from scripts.citations import results_in
    assert results_in("Theorem 6.11") == ["Theorem 6.11"]
    assert results_in("Lemma 1.3.7") == ["Lemma 1.3.7"]


def test_the_repos_own_printed_page_notation_is_read():
    """1084 occurrences of `printed NNN` were unparsed, so those spans produced
    results and no pages and were skipped entirely."""
    from scripts.citations import printed_pages_in
    assert printed_pages_in("Theorem 13.1, printed 394") == {394}
    assert printed_pages_in("printed **268-274**") == set(range(268, 275))
    assert printed_pages_in("pp. 41-42") == {41, 42}


def test_a_bare_numbered_item_counts_as_a_label():
    """Axler prints exercises as `1 Prove that ...` — no kind word, no heading
    markup. Without this they became hard FAILs while naming the right page;
    they belong in the number-only WARN class."""
    from scripts.citations import book_label_for
    assert book_label_for("1", "17\n\n1 Prove that $-(-v) = v$ for every v.\n")
    assert book_label_for("1", "page 1\n\n1\n") is None


def test_an_unreadable_input_file_is_verdict_2_not_1(tmp_path):
    """Exit 1 is reserved for a citation that was compared and was wrong."""
    import pytest
    from scripts.citations import Unreadable, check_file
    with pytest.raises(Unreadable):
        check_file(str(tmp_path / "no-such-file.md"), object())


def test_a_clause_naming_an_absent_book_is_no_verdict_not_a_failure():
    """Attribution is offered every bookmap name, not only the books whose page
    trees are present. Passing only the present ones left such a clause
    attributed to the primary and reported wrong — the one verdict this script
    promises never to give for a check that could not run."""
    from scripts.citations import attribute
    names = ["Cummings", "Hatcher"]
    text = ("**Sources:** Cummings, Theorem 2.11, p. 46; "
            "Hatcher, Theorem 1.1, p. 30\n\n")
    got = {name for _span, _pages, _line, name in attribute(text, "Cummings", names)}
    assert "Hatcher" in got


# --- CodeRabbit review of PR #21 -------------------------------------------

def test_principle_is_a_result_kind():
    """Cummings states induction and strong induction as Principles, and pw-02
    cites Principle 4.1 and 4.7. Both were skipped without touching the
    denominator — and once counted, one of them was on the wrong page."""
    from scripts.citations import results_in
    assert results_in("Cummings §4.1, Principle 4.1, p. 108") == ["Principle 4.1"]
    assert results_in("Principles 4.1, 4.7") == ["Principle 4.1", "Principle 4.7"]


def test_a_book_name_matches_only_as_a_consecutive_phrase():
    """Testing a key's words independently let a Sources block that names
    Cummings's Proofs first and his Real Analysis later make the FIRST
    "Cummings" satisfy the three-word key, sending the Proofs citations to the
    wrong volume."""
    from scripts.citations import book_named_in, split_at_books
    names = ["Cummings", "Cummings Real Analysis"]
    assert book_named_in("Cummings, *Proofs*, Ch. 8 — cf. Real Analysis",
                         names) == "Cummings"
    assert book_named_in("Cummings, *Real Analysis*, Ch. 6",
                         names) == "Cummings Real Analysis"
    assert [n for _p, n in split_at_books(
        "Cummings, *Proofs*, p. 46. Cummings, *Real Analysis*, p. 226.", names)] \
        == ["Cummings", "Cummings Real Analysis"]


def test_the_number_first_word_order_rejects_a_longer_sibling():
    """Axler prints "1.8 Definition"; that order needs the same boundary."""
    from scripts.citations import found_on_page
    assert found_on_page("Definition 1.3", "1.3.7 definition of x") is None
    assert found_on_page("Definition 1.8", "1.8 definition subspace") == "exact"


def test_a_non_contiguous_page_list_names_every_page():
    """`pp. 326 and 328` captured only 326, so a result printed on the second
    page was reported wrong."""
    from scripts.citations import printed_pages_in
    assert printed_pages_in("pp. 326 and 328") == {326, 328}
    assert printed_pages_in("pp. 262, 265") == {262, 265}
    assert printed_pages_in("pp. 10-12, 20") == {10, 11, 12, 20}


def test_to_and_slash_join_a_plural_citation():
    """tda2-04 writes `Definitions 12.1 to 12.5`; the parser accepted only
    dashes, commas and `and`, so those ids left the denominator silently."""
    from scripts.citations import results_in
    assert results_in("Definitions 12.1 to 12.5") ==         ["Definition 12.%d" % i for i in range(1, 6)]
    # "/" joins a LIST, not a range, so it does not expand.
    assert results_in("Definitions 12.1/12.5") == ["Definition 12.1",
                                                   "Definition 12.5"]


def test_an_accented_display_name_matches_its_ascii_bookmap_key():
    """The corpus writes Lindström with the umlaut 275 times; the bookmap key
    is ASCII. A literal match saw none of them, so every an2 clause that DID
    name its book was attributed to the unit's other source."""
    from scripts.citations import book_named_in, deaccent, split_at_books
    names = ["Abbott", "Lindstrom"]
    assert book_named_in("Lindström, Definition 3.1.1, p. 44", names) \
        == "Lindstrom"
    # Length-preserving, because split_at_books slices the original text.
    assert len(deaccent("Lindström")) == len("Lindström")
    assert [n for _p, n in split_at_books(
        "Abbott, p. 223; Lindström, p. 44", names)] == ["Abbott", "Lindstrom"]


def test_unit_requires_both_halves():
    """Filtering the two paths on exists() meant a unit whose lesson was never
    written reported its problem set's verdict alone and looked checked.

    Asserted on the path list, not by running the gate: the first version of
    this test called main() and matched its stdout, which passed locally and
    failed in CI, where the page trees are absent and the run exits 2 with a
    different message. A control whose verdict depends on the environment is
    testing the environment.

    The id is one the syllabus does not contain and never will -- aa runs to
    aa-30. It was aa-05 until that unit's problem set was written, at which
    point the "must not exist" control started failing on a fixture rather
    than on a defect. A control that a normal week of authoring can turn red
    is pinned to the wrong thing.
    """
    from scripts.citations import unit_paths
    got = unit_paths("aa-99")
    assert len(got) == 2
    assert got[0].endswith(os.path.join("problems", "sets", "aa-99.md"))
    assert got[1].endswith(os.path.join("lessons", "aa", "aa-99.html"))
    assert not any(os.path.exists(p) for p in got), "fixture must name a unit that does not exist"


def test_a_displayed_title_names_the_book():
    """Authors write the displayed title, not the bookmap key: cat-05 says
    `Aluffi, *Algebra: Chapter 0*`, and "Algebra" sitting between the key's two
    words meant the clause stayed attributed to Spivak, the unit's primary
    book, and its citations were reported wrong."""
    from scripts.citations import book_named_in, display_forms
    names = ["Aluffi Chapter 0", "Aluffi Underground", "Spivak"]
    titles = {"Aluffi Chapter 0": "Algebra: Chapter 0 (Aluffi)",
              "Aluffi Underground": "Algebra: Notes from the Underground (Aluffi)",
              "Spivak": "Seven Sketches in Compositionality (Fong, Spivak)"}
    assert book_named_in("Aluffi, *Algebra: Chapter 0* — §I.5", names, titles) \
        == "Aluffi Chapter 0"
    assert book_named_in("Aluffi, *Algebra: Notes from the Underground*",
                         names, titles) == "Aluffi Underground"
    assert display_forms("Aluffi Chapter 0", titles["Aluffi Chapter 0"]) \
        == ["Aluffi Chapter 0", "Aluffi Algebra: Chapter 0"]


def test_the_alias_does_not_reopen_scattered_word_matching():
    from scripts.citations import book_named_in
    assert book_named_in("Cummings, *Proofs*, Ch. 8 — cf. Real Analysis",
                         ["Cummings", "Cummings Real Analysis"]) == "Cummings"


def test_a_genuine_singleton_plateau_is_not_discarded():
    """Dropping every one-page plateau also drops a real one-page pagination
    run, so a citation to a folio inside it cannot be mapped and is reported as
    a page the book does not have. pull.suspect_plateaus is the rule that tells
    the two apart, and its docstring already records that the blanket version
    discarded a real boundary."""
    from scripts.pull import suspect_plateaus
    # An interior singleton bracketed by the same offset either side is a stray.
    stray = [(-4, 10, 14, 5), (-3, 15, 15, 1), (-4, 16, 20, 5)]
    assert suspect_plateaus(stray) == [(-3, 15, 15, 1)]
    # A boundary singleton, and an interior one between DIFFERENT offsets, are
    # both genuine and must survive.
    assert suspect_plateaus([(-3, 15, 15, 1), (-4, 16, 20, 5)]) == []
    assert suspect_plateaus([(-4, 10, 14, 5), (-3, 15, 15, 1),
                             (-5, 16, 20, 5)]) == []


def test_a_plural_list_survives_a_parenthesised_part():
    """`Exercises 8(a) and 8(b)` — the part interrupted the separator pattern,
    so the whole list matched nothing and both exercises left the denominator.
    top-02 cites exactly that."""
    from scripts.citations import results_in
    assert results_in("Exercises 8(a) and 8(b), pp. 83-84") == ["Exercise 8"]
    assert results_in("Exercises 8(a) and 9(b)") == ["Exercise 8", "Exercise 9"]
    assert results_in("Exercises 6.6-6.9") ==         ["Exercise 6.%d" % i for i in range(6, 10)]


def test_a_tree_with_no_usable_folio_map_is_unavailable_not_available(tmp_path,
                                                                      monkeypatch):
    """A tree that exists but yields no plateau cannot map any printed page.
    Constructing a Book from it made the book look available and every citation
    attributed to it came back "printed page(s) are not in <book>" with exit 1
    — a wrong-citation verdict for a comparison that never ran."""
    import pytest

    import scripts.citations as C
    page = tmp_path / "page-1"
    page.mkdir()
    (page / "markdown.md").write_text("prose with no folio at all\n",
                                      encoding="utf-8")
    monkeypatch.setattr(C, "pages_dir", lambda name: str(tmp_path))
    with pytest.raises(RuntimeError, match="no usable folio map"):
        C.Book("Fake")


# --- Codex round seven on PR #21 -------------------------------------------

def test_a_leading_digit_is_a_boundary_too():
    """The trailing guard alone still let a citation match a longer number that
    ENDS with it: "Definition 1.3" found in "11.3 definition", "Exercise 10" in
    "110 exercise". The same sibling false PASS from the other end."""
    from scripts.citations import found_on_page
    assert found_on_page("Definition 1.3", "11.3 definition unrelated") is None
    assert found_on_page("Exercise 10", "110 exercise unrelated") is None
    assert found_on_page("Definition 1.3", "1.3 definition of x") == "exact"


def test_a_plain_html_parenthetical_is_a_span():
    """Lessons write `Definition 6.4.1 (Abbott, printed 167)` inline — 955 of
    them — and none was a span, so the citation nearest the mathematics was the
    one nothing checked. The span reaches back over the result id, which sits
    outside the bracket."""
    from scripts.citations import printed_pages_in, results_in, spans
    got = spans("<strong>Definition 6.4.1 (Abbott, printed 167).</strong>")
    assert [(results_in(b), sorted(printed_pages_in(b))) for b, _l in got] \
        == [(["Definition 6.4.1"], [167])]
    # and the markdown form is not counted twice
    assert len(spans("*(Cummings, Exercise 8.28(d), p. 280)*")) == 1


def test_a_sentence_ends_an_assertion_but_an_abbreviation_does_not():
    """Splitting on ';' alone unioned unrelated page claims wherever a Sources
    block is written as sentences. A full stop after `p.`, `pp.`, `ed.` or
    inside a result number ends nothing."""
    from scripts.citations import clauses
    assert [sorted(pg) for _c, pg in
            clauses("Abbott, printed 167-168. Lindstrom, printed 92.")] \
        == [[167, 168], [92]]
    assert [sorted(pg) for _c, pg in
            clauses("Cummings 2nd ed. §4.3, Theorem 4.8, pp. 125-126")] \
        == [[125, 126]]
    assert [sorted(pg) for _c, pg in clauses("See p. 46. Also Lemma 1.3.7, p. 18.")] \
        == [[46], [18]]


def test_pageless_result_is_a_named_third_outcome(tmp_path, capsys):
    """A missing page cannot silently enter the checked denominator."""
    import scripts.citations as C

    class FakeBook:
        name = "Fake"

        def find_result(self, result):
            return result == "Theorem 5.52"

    src = tmp_path / "unit.md"
    src.write_text("Theorem 5.52 is correct. Theorem 5.20 is not.\n",
                   encoding="utf-8")
    failures, checked, unavailable = C.check_file(str(src), FakeBook())
    output = capsys.readouterr().out
    assert failures == [] and checked == 0 and unavailable == set()
    assert "pageless Theorem 5.20 was not found" in output
    assert "pageless Theorem 5.52 was not found" not in output
    assert "2 pageless result reference(s)" in output


def test_running_prose_page_reference_is_checked_once(tmp_path):
    """A bare result-and-page sentence is a citation, without span markup."""
    import scripts.citations as C

    class FakeBook:
        name = "Fake"

        def pdf_pages_for(self, printed):
            return [10] if printed == 7 else []

        def text_of(self, pdf_page):
            return "Theorem 2.3"

        def find_result(self, result):
            return True

    src = tmp_path / "unit.md"
    src.write_text("That is Fake Theorem 2.3, p. 7.\n", encoding="utf-8")
    failures, checked, unavailable = C.check_file(str(src), FakeBook())
    assert failures == [] and checked == 1 and unavailable == set()

    # The same assertion inside a recognised span must not enter twice.
    src.write_text("**Sources:** Fake, Theorem 2.3, p. 7\n\n", encoding="utf-8")
    failures, checked, unavailable = C.check_file(str(src), FakeBook())
    assert failures == [] and checked == 1 and unavailable == set()


def test_ambiguous_folio_resolution_is_counted(tmp_path, capsys):
    """Accept-any-candidate remains valid, but its weaker proof is visible."""
    import scripts.citations as C

    class FakeBook:
        name = "Fake"

        def pdf_pages_for(self, printed):
            return [10, 110]

        def text_of(self, pdf_page):
            return "Theorem 2.3" if pdf_page == 10 else ""

        def find_result(self, result):
            return True

    src = tmp_path / "unit.md"
    src.write_text("**Sources:** Fake, Theorem 2.3, p. 7\n\n",
                   encoding="utf-8")
    failures, checked, unavailable = C.check_file(str(src), FakeBook())
    output = capsys.readouterr().out
    assert failures == [] and checked == 1 and unavailable == set()
    assert "1 citation(s) resolved to more than one candidate PDF page" in output


def test_a_range_expands_but_a_list_does_not():
    """`Exercises 1.3.1-1.3.9` cites all nine — taking only the ends left seven
    out of the denominator. `Definitions 8.3, 8.5` cites exactly two, and
    inventing 8.4 would hold the author to a citation never made."""
    from scripts.citations import results_in
    assert results_in("Exercises 1.3.1-1.3.9") == \
        ["Exercise 1.3.%d" % i for i in range(1, 10)]
    assert results_in("Definitions 8.3, 8.5") == ["Definition 8.3",
                                                  "Definition 8.5"]
    # A range that is absurd or incommensurable degrades to its ends.
    assert results_in("Theorems 1.1-99.9") == ["Theorem 1.1", "Theorem 99.9"]
    assert results_in("Lemmas 1.2-3.4.5") == ["Lemma 1.2", "Lemma 3.4.5"]


def test_a_match_may_not_be_assembled_across_a_page_boundary(tmp_path,
                                                             monkeypatch):
    """Joining candidate pages before normalising let one page ending "Theorem"
    and the next beginning "7.6" collapse into a result neither page carries."""
    import scripts.citations as C
    # The second page must not START a line with the number either, or it
    # qualifies as a bare numbered item and the verdict is number-only WARN
    # rather than the failure this test is about.
    for n, body in ((10, "40\n\nsome prose ending in Theorem"),
                    (11, "41\n\nand 7.6 continues the sentence")):
        d = tmp_path / ("page-%d" % n)
        d.mkdir()
        (d / "markdown.md").write_text(body, encoding="utf-8")
    monkeypatch.setattr(C, "pages_dir", lambda name: str(tmp_path))
    book = C.Book("Fake")
    src = tmp_path / "unit.md"
    src.write_text("*(Fake, Theorem 7.6, pp. 40-41)*\n", encoding="utf-8")
    failures, checked, _unavailable = C.check_file(str(src), book)
    assert checked == 1
    assert len(failures) == 1, "the split match was accepted across the boundary"


# --- Codex round eight on PR #21 -------------------------------------------

def test_an_appendix_lettered_result_number_is_parsed():
    """Hatcher numbers its appendix results A.1, A.17. Requiring a leading
    digit meant those citations produced no id at all, so a wrong page for one
    could not affect the verdict."""
    from scripts.citations import found_on_page, results_in
    assert results_in("Hatcher, Proposition A.17, p. 520") == ["Proposition A.17"]
    assert found_on_page("Proposition A.17", "proposition a.17 states") == "exact"
    assert found_on_page("Proposition A.1", "proposition a.17 states") is None
    # A bare letter is a word, not a result number.
    assert results_in("Theorem A states that") == []


def test_a_malformed_unit_record_is_no_verdict_not_a_traceback(monkeypatch):
    """The previous fix guarded the syllabus READ and left the parse outside
    the try, so a unit record that is not a mapping, or one without an id,
    still exited 1 — the status reserved for a checked, wrong citation."""
    import pytest
    import yaml

    import scripts.citations as C
    for bad in ({"units": [{"no_id": 1}]}, {"units": ["not a mapping"]},
                {"no_units": []}):
        monkeypatch.setattr(yaml, "safe_load", lambda _f, _b=bad: _b)
        with pytest.raises(C.Unreadable):
            C.book_for_unit("pw-01")


def test_every_citation_on_an_invalid_folio_is_counted(tmp_path, monkeypatch):
    """Recording one failure for the whole clause and skipping the increment
    produced output that contradicted itself — "0 citation(s) checked, 1
    wrong" — and understated how many citations the bad folio affected."""
    import scripts.citations as C
    for n, body in ((10, "40\n\nprose here"), (11, "41\n\nmore prose")):
        d = tmp_path / ("page-%d" % n)
        d.mkdir()
        (d / "markdown.md").write_text(body, encoding="utf-8")
    monkeypatch.setattr(C, "pages_dir", lambda name: str(tmp_path))
    src = tmp_path / "u.md"
    src.write_text("*(Fake, Theorem 7.6 and Lemma 8.1, p. 9000)*\n",
                   encoding="utf-8")
    failures, checked, _unavailable = C.check_file(str(src), C.Book("Fake"))
    assert checked == 2
    assert len(failures) == 2


# --- the primary book is a property of the unit, not of the run -------------

def test_each_path_is_checked_against_its_own_primary_book(tmp_path,
                                                           monkeypatch):
    """The primary book was read once from paths[0] and reused for every path
    behind it, so a run spanning two books measured the second book's folios
    against the first book's pagination. It was silent: a wrong pagination
    still resolves to real pages, and some of them still carry the result
    named. aa-01 cites Aluffi throughout, was checked against Carter because
    aa-00 came first on the command line, and five of its eight citations
    PASSED. Single-book modules never exposed it."""
    import scripts.citations as C
    trees = {"Alpha": (40, "Theorem 1.1"), "Beta": (70, "Theorem 2.2")}
    for name, (first, result) in trees.items():
        root = tmp_path / name
        for k in range(3):
            d = root / ("page-%d" % (10 + k))
            d.mkdir(parents=True)
            body = "%d\n\n%s is stated here.\n" % (first + k, result)
            (d / "markdown.md").write_text(body, encoding="utf-8")
    monkeypatch.setattr(C, "pages_dir", lambda name: str(tmp_path / name))
    monkeypatch.setattr(C, "load_bookmap",
                        lambda: {"Alpha": {"title": "Alpha (A)"},
                                 "Beta": {"title": "Beta (B)"}})
    monkeypatch.setattr(C, "book_for_unit",
                        lambda uid: {"u1": "Alpha", "u2": "Beta"}.get(uid))
    # Neither clause names its book, so each one falls to its unit's primary.
    # That is the whole path the defect lived on.
    (tmp_path / "u1.md").write_text("*(Theorem 1.1, p. 40)*\n",
                                    encoding="utf-8")
    (tmp_path / "u2.md").write_text("*(Theorem 2.2, p. 70)*\n",
                                    encoding="utf-8")
    assert C.main([str(tmp_path / "u1.md"), str(tmp_path / "u2.md")]) == 0
    # The negative control: the same two files in the same run, with u2 now
    # naming a page its own book does not have, must still fail.
    (tmp_path / "u2.md").write_text("*(Theorem 2.2, p. 41)*\n",
                                    encoding="utf-8")
    assert C.main([str(tmp_path / "u1.md"), str(tmp_path / "u2.md")]) == 1


def _two_fake_books(tmp_path, monkeypatch, present=("Alpha", "Beta")):
    """Two book trees on disk, with `present` deciding which are readable."""
    import scripts.citations as C
    trees = {"Alpha": (40, "Theorem 1.1"), "Beta": (70, "Theorem 2.2")}
    for name, (first, result) in trees.items():
        if name not in present:
            continue
        root = tmp_path / name
        for k in range(3):
            d = root / ("page-%d" % (10 + k))
            d.mkdir(parents=True)
            (d / "markdown.md").write_text(
                "%d\n\n%s is stated here.\n" % (first + k, result),
                encoding="utf-8")
    monkeypatch.setattr(C, "pages_dir", lambda name: str(tmp_path / name))
    monkeypatch.setattr(C, "load_bookmap",
                        lambda: {"Alpha": {"title": "Alpha (A)"},
                                 "Beta": {"title": "Beta (B)"}})
    return C


def test_a_path_with_no_syllabus_book_does_not_stop_the_run(tmp_path,
                                                            monkeypatch):
    """main() derived the book from paths[0] and returned 2 before the loop
    when that path had no syllabus record. Putting a scratch file first on the
    command line therefore meant every unit behind it went unchecked, and the
    run still produced a verdict. Only the unresolvable path is blocked now.
    (CodeRabbit, PR #26.)"""
    C = _two_fake_books(tmp_path, monkeypatch)
    monkeypatch.setattr(C, "book_for_unit",
                        lambda uid: {"u2": "Beta"}.get(uid))
    (tmp_path / "scratch.md").write_text("no citations here\n",
                                         encoding="utf-8")
    # Beta has no printed page 41, so this is a wrong citation.
    (tmp_path / "u2.md").write_text("*(Theorem 2.2, p. 41)*\n",
                                    encoding="utf-8")
    assert C.main([str(tmp_path / "scratch.md"),
                   str(tmp_path / "u2.md")]) == 1


def test_a_missing_primary_does_not_blind_the_rest_of_the_file(tmp_path,
                                                               monkeypatch,
                                                               capsys):
    """A file's primary is only the default attribution for a clause naming no
    book of its own. Returning early when the PRIMARY's page tree was absent
    skipped the whole file, so citations naming books that ARE present went
    unchecked. (Codex, PR #26.)"""
    C = _two_fake_books(tmp_path, monkeypatch, present=("Alpha",))
    monkeypatch.setattr(C, "book_for_unit", lambda uid: "Beta")
    (tmp_path / "u3.md").write_text(
        "*(Alpha, Theorem 1.1, p. 99)*\n\n*(Theorem 2.2, p. 70)*\n",
        encoding="utf-8")
    # Alpha is present and printed 99 is not one of its pages, so the wrong
    # citation is reported and the run fails; Beta is absent, and the clause
    # that fell back to it is reported as having had no verdict rather than
    # being counted either way. Both statements have to appear: the file used
    # to produce neither.
    assert C.main([str(tmp_path / "u3.md")]) == 1
    out = capsys.readouterr().out
    assert "Theorem 1.1" in out and "p. 99" in out
    assert "NOVERDICT" in out and "Beta" in out


def test_a_unit_run_whose_primary_is_absent_still_checks_the_rest(tmp_path,
                                                                  monkeypatch,
                                                                  capsys):
    """--unit fills book_name from the syllabus without the caller asserting
    anything, so guarding the early return on book_name rather than on --book
    caught --unit too: a unit whose primary tree is absent aborted the run
    before per_path_book() could see it, losing the checks on its citations
    that named a secondary book which IS present. Only --book aborts now.
    (Codex, PR #26.)"""
    C = _two_fake_books(tmp_path, monkeypatch, present=("Alpha",))
    monkeypatch.setattr(C, "book_for_unit", lambda uid: "Beta")
    monkeypatch.setattr(C, "unit_paths", lambda uid: [str(tmp_path / "u4.md")])
    (tmp_path / "u4.md").write_text("*(Alpha, Theorem 1.1, p. 99)*\n",
                                    encoding="utf-8")
    assert C.main(["--unit", "u4"]) == 1
    out = capsys.readouterr().out
    assert "Theorem 1.1" in out and "p. 99" in out
