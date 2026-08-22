"""The folio fitter. Synthetic pages throughout — CI has no access to the
book drive, and a check that silently does nothing when its input is missing
is the silent-absence failure mode this project keeps paying for."""
from scripts.pull import fit_offsets, folio_candidates, folio_of, parse_range


def page(head="", tail=""):
    """A page with a body long enough that its head and tail are distinct."""
    parts = ([head] if head else []) + ["prose"] * 6 + ([tail] if tail else [])
    return "\n\n".join(parts)


# --- reading a folio off one page ------------------------------------------

def test_a_bare_number_at_either_edge_is_a_candidate():
    assert folio_candidates(page(head="154")) == [(154, "head")]
    assert folio_candidates(page(tail="27")) == [(27, "tail")]


def test_a_chapter_opener_offers_both_the_chapter_number_and_the_folio():
    """Axler PDF 44: 'CHAPTER' / '2' at the head, the real folio 27 at the tail.
    Nine of its twelve chapter openers do this. A head-first reader calls the
    page 'printed 2' and computes an offset of -42."""
    text = "CHAPTER\n\n2\n\n## Finite-Dimensional Vector Spaces\n\nbody\n\n27"
    assert folio_candidates(text) == [(2, "head"), (27, "tail")]
    assert folio_of(text) == (27, "tail")   # one page in isolation: prefer the tail


def test_numbers_in_the_body_are_not_folios():
    body = "\n\n".join(["Chapter 6. Sequences", "prose", "prose", "42",
                        "prose", "prose", "prose", "closing line"])
    assert folio_candidates(body) == []


def test_head_and_tail_spans_do_not_overlap_on_a_short_page():
    """A two-line page would otherwise return its single number as both a head
    and a tail candidate, and fit_offsets would count that vote twice."""
    assert folio_candidates("154\n\ntext") == [(154, "head")]


def test_a_page_with_no_number_yields_nothing_rather_than_a_guess():
    assert folio_candidates(page(head="Chapter 6. Sequences", tail="see below")) == []
    assert folio_of("no numbers here") == (None, None)


# --- fitting an offset over a range ----------------------------------------

def _pages(spec):
    return [(n, cands) for n, cands in spec]


def test_a_constant_offset_is_reported_as_one_plateau():
    pages = _pages([(n, [(n - 12, "head")]) for n in range(164, 171)])
    rows, plateaus = fit_offsets(pages)
    assert plateaus == [(-12, 164, 170, 7)]
    assert all(r[4] == "OK" for r in rows)


def test_a_chapter_opener_does_not_break_the_run():
    """The regression this fitter exists for. PDF 44 offers 2 (head) and 27
    (tail); the fit must take the candidate that agrees with its neighbours."""
    pages = _pages(
        [(n, [(n - 17, "head")]) for n in (42, 43)]
        + [(44, [(2, "head"), (27, "tail")])]
        + [(n, [(n - 17, "head")]) for n in (45, 46)]
    )
    rows, plateaus = fit_offsets(pages)
    assert plateaus == [(-17, 42, 46, 5)]
    assert rows[2] == (44, 27, "tail", -17, "OK")


def test_a_genuine_drift_is_reported_as_two_plateaus():
    """Axler really does move: -17, then -16, then -15. Two substantial
    plateaus is drift, and must not be smoothed away by the mode."""
    pages = _pages([(n, [(n - 17, "head")]) for n in range(60, 67)]
                   + [(n, [(n - 16, "head")]) for n in range(67, 74)])
    _rows, plateaus = fit_offsets(pages)
    assert [(p[0], p[3]) for p in plateaus] == [(-17, 7), (-16, 7)]


def test_a_lone_disagreeing_page_is_SUSPECT_not_a_drift():
    """An index page-reference or a stray number reads exactly like a one-page
    plateau. Calling that a pagination change would cry wolf on every book."""
    pages = _pages([(n, [(n - 15, "head")]) for n in (250, 252, 254)]
                   + [(256, [(8, "head")])]
                   + [(n, [(n - 15, "head")]) for n in (258, 260)])
    rows, plateaus = fit_offsets(pages)
    assert [r[4] for r in rows if r[0] == 256] == ["SUSPECT"]
    assert [p for p in plateaus if p[3] > 1] == [(-15, 250, 254, 3),
                                                 (-15, 258, 260, 2)]


def test_pages_with_no_folio_do_not_contribute_to_the_offset():
    """'A page with no folio proves nothing.' It must not be averaged in, and
    it must not be reported as a change either."""
    pages = _pages([(30, [(13, "head")]), (31, []), (32, []),
                    (33, []), (34, [(17, "head")])])
    rows, plateaus = fit_offsets(pages)
    assert [r[4] for r in rows] == ["OK", "NO FOLIO", "NO FOLIO", "NO FOLIO", "OK"]
    assert plateaus == [(-17, 30, 34, 2)]


def test_an_empty_range_does_not_invent_an_offset():
    rows, plateaus = fit_offsets([(1, []), (2, [])])
    assert plateaus == []
    assert all(r[3] is None for r in rows)


def test_range_parsing():
    assert parse_range("166-170") == (166, 170)
    assert parse_range("166") == (166, 166)


# --- Codex review of PR #20 ------------------------------------------------

def test_equal_plateaus_split_by_a_suspect_are_one_offset_not_drift():
    """A single stray folio between two runs of the SAME offset splits them
    into two plateaus. Deciding the verdict on plateau count then announced
    "OFFSET IS NOT CONSTANT" over a range with exactly one offset in it —
    crying drift on precisely the case SUSPECT exists to absorb. The verdict
    is about DISTINCT offsets."""
    pages = _pages([(n, [(n - 15, "head")]) for n in (250, 252, 254)]
                   + [(256, [(8, "head")])]
                   + [(n, [(n - 15, "head")]) for n in (258, 260)])
    _rows, plateaus = fit_offsets(pages)
    real = [p for p in plateaus if p[3] > 1]
    assert len(real) == 2                      # still two plateaus...
    assert {p[0] for p in real} == {-15}       # ...but one offset, so no drift


def test_genuine_drift_still_has_two_distinct_offsets():
    """The regression guard for the fix above: Axler really does move."""
    pages = _pages([(n, [(n - 17, "head")]) for n in range(60, 67)]
                   + [(n, [(n - 16, "head")]) for n in range(67, 74)])
    _rows, plateaus = fit_offsets(pages)
    real = [p for p in plateaus if p[3] > 1]
    assert {p[0] for p in real} == {-17, -16}


# --- Codex review of PR #20, second round ----------------------------------

def test_a_singleton_at_the_range_edge_is_not_suspect():
    """A singleton is suspect only when it is INTERIOR and both sides agree —
    that is what "disagrees with both neighbours" requires. At the first or
    last row there is evidence on one side only. Excluding it anyway made
    `--folio 66-70` report "Consistent offset -16", exit 0, straight across
    Axler's real -17/-16 transition at 66/67."""
    from scripts.pull import suspect_plateaus
    pages = _pages([(66, [(49, "head")])]
                   + [(n, [(n - 16, "head")]) for n in (67, 68, 69, 70)])
    _rows, plateaus = fit_offsets(pages)
    assert suspect_plateaus(plateaus) == []
    real = [p for p in plateaus if p not in suspect_plateaus(plateaus)]
    assert {p[0] for p in real} == {-17, -16}


def test_an_interior_singleton_between_agreeing_sides_is_still_suspect():
    from scripts.pull import suspect_plateaus
    pages = _pages([(n, [(n - 15, "head")]) for n in (250, 252, 254)]
                   + [(256, [(8, "head")])]
                   + [(n, [(n - 15, "head")]) for n in (258, 260)])
    rows, plateaus = fit_offsets(pages)
    assert [p[1] for p in suspect_plateaus(plateaus)] == [256]
    assert [r[4] for r in rows if r[0] == 256] == ["SUSPECT"]


def test_an_interior_singleton_between_DISAGREEING_sides_is_not_suspect():
    """Two real transitions in a row is drift, not a stray reading."""
    from scripts.pull import suspect_plateaus
    pages = _pages([(n, [(n - 17, "head")]) for n in (60, 61)]
                   + [(62, [(62 - 16, "head")])]
                   + [(n, [(n - 15, "head")]) for n in (63, 64)])
    _rows, plateaus = fit_offsets(pages)
    assert suspect_plateaus(plateaus) == []


def test_two_conflicting_endpoint_singletons_are_both_evidence():
    """A two-page range whose pages disagree has no interior at all, so
    neither reading can be dismissed. Marking both SUSPECT would leave no real
    plateau and produce a false consistent verdict on a range that is nothing
    but a disagreement."""
    from scripts.pull import suspect_plateaus
    _rows, plateaus = fit_offsets(_pages([(100, [(80, "head")]),
                                          (101, [(82, "head")])]))
    assert suspect_plateaus(plateaus) == []
    real = [p for p in plateaus if p not in suspect_plateaus(plateaus)]
    assert sorted({p[0] for p in real}) == [-20, -19]


def test_a_suspect_singleton_does_not_taint_a_real_run_of_the_same_offset():
    """SUSPECT is a property of a PLATEAU, not of an offset value. Keying on
    the offset marked every row carrying that number, including a substantial
    plateau elsewhere in the same range."""
    from scripts.pull import suspect_plateaus
    spec = ([(n, [(n - 16, "head")]) for n in (10, 11)]
            + [(12, [(12 - 15, "head")])]
            + [(n, [(n - 16, "head")]) for n in (13, 14)]
            + [(n, [(n - 15, "head")]) for n in (20, 21, 22)])
    rows, plateaus = fit_offsets(_pages(spec))
    assert [p[1] for p in suspect_plateaus(plateaus)] == [12]
    assert [r[0] for r in rows if r[4] == "SUSPECT"] == [12]


def _corpus(tmp_path, pages):
    """pages: {pdf_page: text or None}. None means the page was never extracted."""
    for n, text in pages.items():
        if text is None:
            continue
        d = tmp_path / ("page-%d" % n)
        d.mkdir()
        (d / "markdown.md").write_text(text, encoding="utf-8")
    return str(tmp_path)


def test_one_lone_folio_in_a_range_is_no_verdict_not_a_consistent_offset(tmp_path):
    """One observation cannot agree with anything, so it cannot be told apart
    from a chapter number or an index reference — the two readings SUSPECT
    exists to reject. It used to exit 0 with 'Consistent offset across 1 page'.
    (Codex review of PR #20, sixth round.)"""
    from scripts.pull import cmd_folio
    d = _corpus(tmp_path, {10: "no number here\nplain prose\n",
                           11: "84\nsome prose on the page\n",
                           12: "still nothing numeric to read\n"})
    assert cmd_folio(d, "book", "10-12") == 2


def test_two_agreeing_folios_do_reach_a_verdict(tmp_path):
    from scripts.pull import cmd_folio
    d = _corpus(tmp_path, {10: "84\nprose\n", 11: "85\nprose\n"})
    assert cmd_folio(d, "book", "10-11") == 0
