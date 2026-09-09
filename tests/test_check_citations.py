"""The citation SWEEP: what status does each citation get, and is the
denominator visible?

Synthetic throughout — CI has no access to the book drive, so every test here
builds a fake book whose "pages" are strings.

The two negative controls Observation 2026-08-09 asked for are
`test_a_page_one_off_is_not_found_on_page` and
`test_a_label_absent_from_the_book_is_not_found_on_page`. They are the reason
this file exists: without them the reporter could print RESOLVED for everything
and nobody could tell the difference between a corpus that is right and a
sweep that never looked.
"""
import pytest

import scripts.check_citations as S


class FakeBook:
    """Printed folio n lives on PDF page n + 100. Two pages of content."""

    name = "Fake"

    PAGES = {
        110: "**Theorem 2.3.** Every widget is a gadget.\n",
        111: "**Lemma 2.4.** Gadgets compose.\n",
        # Axler's number-first style: a result headed by number and no kind.
        112: "2.5 Conditions for a widget\n\nSuppose W is a widget.\n",
    }

    def pdf_pages_for(self, printed):
        n = printed + 100
        return [n] if n in self.PAGES else []

    def text_of(self, pdf_page):
        return self.PAGES.get(pdf_page)

    def find_result(self, result):
        return any(result in t for t in self.PAGES.values())


def sweep(tmp_path, body, name="unit.md"):
    src = tmp_path / name
    src.write_text(body, encoding="utf-8")
    return S.classify_file(str(src), "Fake", {"Fake": FakeBook()}, ["Fake"],
                           {"Fake": "Fake Book"})


def statuses(cites):
    return [(c.result, c.status) for c in cites]


# --- the positive signal ----------------------------------------------------

def test_a_correct_citation_resolves(tmp_path):
    got = sweep(tmp_path, "*(Fake §2, Theorem 2.3, p. 10)*\n")
    assert statuses(got) == [("Theorem 2.3", S.RESOLVED)]


def test_the_summary_prints_the_resolved_count_even_when_nothing_failed(capsys,
                                                                       tmp_path):
    """A gate that only speaks when it is unhappy cannot be distinguished from
    a gate that never ran. The count is the liveness signal."""
    counts = S.report(sweep(tmp_path, "*(Fake, Theorem 2.3, p. 10)*\n"),
                      set(S.ORDER))
    out = capsys.readouterr().out
    assert "1 citation(s) compared against a page; 1 resolved" in out
    assert counts[S.RESOLVED] == 1


# --- negative controls (Observation 2026-08-09) -----------------------------

def test_a_page_one_off_is_not_found_on_page(tmp_path):
    """Control one. Theorem 2.3 is on printed 10; the citation says 11. The
    page IS in the book and IS readable, so nothing excuses the sweep from
    giving a verdict — and the verdict must not be RESOLVED."""
    got = sweep(tmp_path, "*(Fake §2, Theorem 2.3, p. 11)*\n")
    assert statuses(got) == [("Theorem 2.3", S.NOT_FOUND)]


def test_a_label_absent_from_the_book_is_not_found_on_page(tmp_path):
    """Control two. Theorem 9.9 is in no page of this book. A citation naming
    a real-looking result at a real page is exactly the tda2-10 shape."""
    got = sweep(tmp_path, "*(Fake §9, Theorem 9.9, p. 10)*\n")
    assert statuses(got) == [("Theorem 9.9", S.NOT_FOUND)]


def test_a_folio_outside_the_book_is_page_not_in_book(tmp_path):
    """tda2-10's own defect: pp. 261-277 for a section printed 180-189. The
    folio maps to no PDF page at all, which is a different and louder failure
    than "the result is not on that page"."""
    got = sweep(tmp_path, "*(Fake §9, Theorem 2.3, p. 900)*\n")
    assert statuses(got) == [("Theorem 2.3", S.NOT_IN_BOOK)]


def test_a_bare_page_pointer_is_unverifiable_not_resolved(tmp_path):
    """1980 of the corpus's page claims name no result. They cannot be wrong
    about a label they never gave — but they must not be counted as resolved
    either, or the denominator lies."""
    got = sweep(tmp_path, "*(Fake §2, the widget construction, pp. 10-11)*\n")
    assert [c.status for c in got] == [S.NO_RESULT]


def test_noverdict_is_never_counted_as_resolved_or_as_wrong(tmp_path):
    got = S.classify_file(
        str(_write(tmp_path, "*(Absent §2, Theorem 2.3, p. 10)*\n")),
        "Fake", {"Fake": FakeBook()}, ["Fake", "Absent"],
        {"Fake": "Fake Book", "Absent": "Absent Book"})
    assert [c.status for c in got] == [S.NOVERDICT]
    assert S.NOVERDICT not in S.COMPARED


def _write(tmp_path, body):
    src = tmp_path / "unit.md"
    src.write_text(body, encoding="utf-8")
    return src


# --- the loose bucket -------------------------------------------------------

def test_a_number_only_hit_is_resolved_loose_not_resolved(tmp_path):
    """Axler heads results with no kind word. "Proposition 2.5" on the page
    that heads it "2.5 Conditions for a widget" is right about WHERE and loose
    about WHAT — a third thing, and collapsing it into either neighbour loses
    information."""
    got = sweep(tmp_path, "*(Fake §2, Proposition 2.5, p. 12)*\n")
    assert statuses(got) == [("Proposition 2.5", S.LOOSE)]


# --- exit-code contract -----------------------------------------------------

def test_the_reporter_does_not_fail_the_build_by_default(tmp_path, monkeypatch,
                                                         capsys):
    """Report-first is the whole point: the corpus is swept before the check
    becomes blocking, so a NOT-FOUND row must not stop a run that asked for a
    report."""
    src = _write(tmp_path, "*(Fake §2, Theorem 2.3, p. 11)*\n")
    monkeypatch.setattr(S, "load_books", lambda: ({"Fake": FakeBook()}, []))
    monkeypatch.setattr(S.C, "load_bookmap", lambda: {"Fake": {"title": "Fake Book"}})
    monkeypatch.setattr(S, "primary_for", lambda *a: "Fake")
    assert S.main([str(src)]) == 0
    assert "NOT-FOUND-ON-PAGE" in capsys.readouterr().out
    assert S.main([str(src), "--strict"]) == 1


def test_an_unknown_status_filter_is_rejected(tmp_path):
    with pytest.raises(SystemExit):
        S.main(["--only", "PROBABLY-FINE"])
