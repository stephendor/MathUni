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
