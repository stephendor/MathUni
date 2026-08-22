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
    matched nothing at all. Only the numbers written are expanded — never the
    interior of a range, which would invent citations the author never made."""
    from scripts.citations import results_in
    assert results_in("Propositions 2.4, 2.6") == ["Proposition 2.4",
                                                   "Proposition 2.6"]
    assert results_in("Exercises 6.6-6.9") == ["Exercise 6.6", "Exercise 6.9"]
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
