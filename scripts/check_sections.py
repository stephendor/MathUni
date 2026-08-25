"""Check that a citation's section label agrees with the folio it names.

`scripts/citations.py` verifies two of the three things a citation asserts:
that the result number exists, and that it sits on the printed page named.
It never looks at the section label. So

    <span class="cite">— Axler §3.A, Definition 3.12, p. 59</span>

passes that gate in full — Definition 3.12 really is on printed 59 — while
naming the wrong section, because printed 59 is where §3.B begins. Twenty-two
citations in one lesson carried that error, and every one of them was PASS.

This check closes that gap. For each ``§LABEL ... p. N`` citation it looks up
which section contains printed page N and compares.

The section index lives in ``resources/sections.json`` and is generated from
the book's own page tree by ``--refresh``, never hand-written: a hand-kept
table of page numbers is exactly the sort of binding that rots without
anything reporting it. ``--refresh`` requires the book drive; the check itself
does not, so it runs in CI against the committed index.

Exit codes follow the repo contract: 0 clean, 1 at least one label wrong,
2 no verdict reachable (no index, or an index that names no section).
"""
import argparse
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from scripts.citations import printed_pages_in, sentence_end  # noqa: E402
INDEX = os.path.join(REPO, "resources", "sections.json")

# A citation's section label, then the text up to the next citation, the next
# tag, or the end of the sentence. Stopping at the sentence boundary matters:
# pages named in a FOLLOWING sentence belong to whatever that sentence cites,
# and letting the tail run on reports them against this label.
#
# The cap is a safety net, not the primary stop, and the first version of it
# was itself a defect twice over. A Sources line reading "§3.F (Definitions
# ...), pp. 101-114" is one long sentence: a 220-character cap landed in the
# middle of "101", the tail ended "pp. 1", and a correct citation was reported
# as naming printed page 1. Raising the cap and making it digit-safe fixed the
# loud direction and left the quiet one: when the cap lands BEFORE the page
# marker, the tail carries no page at all, pages_in returns nothing, and the
# citation is silently accepted however wrong its label is. Silence is the
# failure mode this whole script exists to remove, so truncation is now
# detected and reported as NO VERDICT rather than absorbed. The cap is also
# large enough that reaching it means something is malformed, not long.
CAP = 2000
_SECTION = r"\d+\.(?:[A-Z]|\d{1,2})"
_CHAPTER = r"\d+"
_DASH = r"\s*[–—-]\s*"
# A Sources line names a RANGE of sections at least as often as a single one,
# and the range is part of the label, not text following it. Reading only the
# first half of "§1.2-1.5" and then testing every page in the clause against
# it reported four correct citations in one unit as wrong, each of them naming
# a page in the later half of its own range.
#
# The two ends must have the SAME SHAPE — both sectioned, or both bare chapter
# numbers. The first version allowed any number after the dash, so ordinary
# prose reading "§1.4 — 4 rules, p. 6" parsed as the label "1.4 — 4", which
# span() cannot resolve, and a correct citation was reported wrong. The
# negative control written alongside it used "§1.4 - the rules" and passed,
# because a word after the dash was never the risk: a NUMBER after the dash
# was, and the control had no way to fire. (Codex, PR #26.)
CITE = re.compile(r"§(%s(?:%s%s)?|%s(?:%s%s)?)"
                  % (_SECTION, _DASH, _SECTION, _CHAPTER, _DASH, _CHAPTER))
def tails(text):
    """(label, tail, truncated) for each §LABEL in `text`, in order."""
    # Sentence boundaries are a shared corpus-reading contract. Import the
    # citation gate's abbreviation-aware rule rather than re-deriving it here.
    out = []
    for m in CITE.finditer(text):
        rest = text[m.end():]
        structural = re.search(r"[§<]", rest)
        structural_end = structural.start() if structural else len(rest)
        end = min(structural_end, sentence_end(rest))
        truncated = end > CAP
        out.append((m.group(1), rest[:min(end, CAP)], truncated))
    return out
# "pp. 28-38" names two pages, not one. Matching only the first let a range
# whose FAR end lands in the next section pass unexamined, which is the
# likeliest place for a footer's label to be wrong. Only the numbers actually
# written are taken; the interior of a range is never invented.
def pages_in(tail):
    """Every written page member, using the shared citation-page grammar.

    Unlike the folio gate, this gate deliberately does not expand interiors:
    section claims are tested at the page members the author actually wrote,
    especially the far endpoint where a boundary error becomes visible.
    """
    return sorted(printed_pages_in(tail, expand_ranges=False))

# The section heading as the books print it. Two shapes so far: Axler letters
# its sections ("## 3.B Null Spaces and Ranges") and Abbott numbers them
# ("## 1.3 The Axiom of Completeness"). A book that labels sections some third
# way is not silently unsupported — refresh raises NoVerdict when it finds no
# heading at all.
_HEAD = r"^#{1,6}\s*\**\s*(\d+\.%s)\**\s+(.{2,60})"
LETTERED = re.compile(_HEAD % "[A-F]", re.M)
NUMBERED = re.compile(_HEAD % r"\d{1,2}", re.M)
# Which shape a book uses is read off the book, not configured. The numbered
# pattern alone would be a disaster on Axler, whose RESULTS are headed "10.58
# Definition"; run over Axler it invented sections 10.58 and 10.59 out of two
# of them. So the lettered pattern is tried first over the whole book and
# wins outright if it finds anything, because no book labels sections both
# ways and no book numbers a result with a letter.
HEADING = LETTERED   # the default, and what the selftest's fixtures use
# A chapter opening: "CHAPTER" alone above its number (Axler), or a markdown
# heading carrying the word and the number (Abbott's "# Chapter 1"). The page
# belongs to no section, and neither does anything after it until that
# chapter's first section heading.
CHAPTER_OPEN = re.compile(r"^#{0,6}\s*CHAPTER\s*\d{0,2}\s*$", re.I)


class NoVerdict(Exception):
    """The check could not run. Exit 2 — never a silent pass."""


def main_text_plateaus(plateaus):
    """(kept, dropped) — plateaus whose printed range repeats an earlier one.

    Abbott's PDF carries the Instructor's Solutions Manual bound in behind the
    book: PDF 13-269 is printed 1-257, and PDF 277-429 starts again at printed
    1. Printed page 100 therefore exists twice in one file. For the section
    index that is not an ambiguity to be resolved page by page — the second
    document is a different document, its headings are not this book's
    sections, and indexing it would move section boundaries to pages the book
    does not have. A plateau whose printed span overlaps one already accepted
    is dropped, and the caller says so rather than deciding quietly.
    """
    kept, dropped, spans = [], [], []
    for off, lo, hi, cnt in plateaus:
        a, b = lo + off, hi + off
        if any(a <= y and x <= b for x, y in spans):
            dropped.append((off, lo, hi, cnt))
        else:
            spans.append((a, b))
            kept.append((off, lo, hi, cnt))
    return kept, dropped


def extend_first_plateau(plateaus, blanks):
    """Extend the first plateau down over the folio-less pages above it.

    ``fit_offsets`` skips a page whose folio nothing could read, so a blank
    page in the MIDDLE of a plateau is still covered by the range around it.
    A run of them at the lower EDGE is not: those pages fall outside every
    plateau, ``printed()`` answers None, and any section heading standing
    there is dropped from the index without a word. Aluffi's chapter-1
    opening page is exactly that page — it carries no folio, it sits one page
    below the first folio the fit could read, and §1.1 went missing from a
    75-section index in silence, which then made the CORRECT citation
    "§1.1, p. 3" the thing that failed.

    Only the first plateau is extended, and only while the offset keeps the
    printed page at 1 or above. Both halves of that are the point. A book's
    main text starts at printed 1, so the guard stops the walk exactly where
    the book does — front matter numbered in roman reads as folio-less too,
    and without it a plateau would swallow the introduction and hand it
    printed page 0 and below. A blank run BETWEEN two plateaus has no such
    pin: either neighbour's offset could be the right one, the choice is not
    determinable from the page tree, and refresh reports those pages instead
    of guessing at them.
    """
    out = []
    for i, (off, lo, hi, cnt) in enumerate(plateaus):
        if i == 0:
            while lo - 1 in blanks and lo - 1 + off >= 1:
                lo -= 1
        out.append((off, lo, hi, cnt))
    return out


def uncovered(plateaus):
    """Pages between two kept plateaus that neither one covers.

    These are the folio-less runs `extend_first_plateau` deliberately leaves
    alone. A heading on one of them would be missing from the index, so the
    pages are reported rather than left for someone to find through a FAIL on
    a citation that was right.
    """
    out = []
    for (_o, _lo, hi, _c), (_o2, lo2, _h2, _c2) in zip(plateaus,
                                                       plateaus[1:]):
        out.extend(range(hi + 1, lo2))
    return out


def load_index(path=INDEX):
    """{book: (rows, shared)} — rows sorted by page, shared a set of pages.

    A row with label None marks a page from which no section is in force. The
    older flat format carried no such rows, so it is refused rather than read:
    an index that cannot express a gap would answer gap questions wrongly, and
    a wrong answer here is worse than no answer.
    """
    try:
        with io.open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise NoVerdict("cannot read section index %s: %s" % (path, exc))
    if not data or not any(data.values()):
        raise NoVerdict("section index %s names no section" % path)
    out = {}
    for book, entry in data.items():
        if not isinstance(entry, dict) or "sections" not in entry:
            raise NoVerdict(
                "section index %s is in the pre-gap format for %r; re-run "
                "--refresh %s" % (path, book, book))
        rows = [(int(p), lab) for lab, p in entry["sections"].items()]
        rows += [(int(p), None) for p in entry.get("gaps", [])]
        # A gap and a section starting on the same page: the section wins,
        # so it must sort last.
        out[book] = (sorted(rows, key=lambda r: (r[0], r[1] is not None)),
                     set(entry.get("shared", [])))
    return out


def section_of(page, rows):
    """The label of the last section that has started by printed `page`.

    None for a page before the first section of the book, and None for a page
    in a gap between sections — a chapter-opening page, or the whole of an
    unsectioned chapter such as Axler's chapter 4.

    Gaps are why the index records chapter openings alongside section starts.
    Without them the last section of the previous chapter runs on through the
    gap, and a citation naming a gap page under that section's label is
    accepted: "§2.C, ..., p. 51" passed, though printed 51 is the chapter-3
    opening page and belongs to no section at all. A gap is recorded as a row
    whose label is None, so the same "last row at or before this page" rule
    answers "no section" without a special case.
    """
    found = None
    for start, label in rows:
        if page >= start:
            found = label
        else:
            break
    return found


# How much text before a section's heading counts as the previous section
# still running. Running heads and bare folios are dropped first, so this is
# body text or nothing; the threshold only has to separate "nothing" from "a
# page of exercises".
SHARE_MIN = 120


def admissible(page, rows, shared=()):
    """Every section label a citation of `page` may legitimately name.

    Usually one. A page that carries the tail of one section above the heading
    of the next carries two, and both are right: Abbott prints Exercise 1.4.13
    at the top of printed 29 and opens §1.5 below it, so "§1.4, Exercise
    1.4.13, p. 29" is a correct citation that the one-label rule would fail.

    The second label is admitted only where the book actually shares the page,
    which --refresh decides by looking for body text above the heading. Axler's
    printed 59 opens §3.B at the top with nothing above it but the running
    head, so 59 admits §3.B alone — which is what makes the defect this gate
    was built for still fire.

    A page carrying a GAP row never admits the earlier label, whatever the
    index says about sharing. A gap is the statement that nothing from before
    is in force here, so the two claims contradict each other and the gap
    wins. Abbott's printed 213 is exactly this case: the chapter-8 opening
    page, carrying the chapter title and epigraph above the §8.1 heading.
    That text is long enough to read as a previous section running on, so
    --refresh marked 213 shared and `§7.7, p. 213` passed — though §7.7 ended
    before the chapter break, which is the one thing gap rows exist to say.
    (Codex review of PR #25.) The guard is here as well as at refresh time
    because the index is a committed artifact and can be stale.
    """
    here = section_of(page, rows)
    if page not in shared:
        return [here]
    if any(start == page and label is None for start, label in rows):
        return [here]
    before = None
    for start, label in rows:
        if start >= page:
            break
        if label != here:
            before = label
    return [here, before] if before else [here]


def span(label, rows):
    """Every section a label covers — one, or the whole run of a range.

    A range is checked against the index rather than expanded arithmetically.
    Sections do not always run 1, 2, 3: a book may stop at §3.3 and go to
    §4.1, and "§3.1-3.6" would then name three sections that do not exist and
    admit pages that belong to the next chapter. Reading the run off the index
    admits exactly the sections the book has between the two ends, and a range
    naming an end the book does not have is left as-is, to fail loudly rather
    than resolve to something plausible.
    """
    parts = re.split(r"\s*[–—-]\s*", label)
    if len(parts) != 2:
        return [label]
    order = [lab for _p, lab in rows if lab is not None]
    if parts[0] not in order or parts[1] not in order:
        return [label]
    i, j = order.index(parts[0]), order.index(parts[1])
    return order[i:j + 1] if i <= j else [label]


def check_text(text, rows, shared=()):
    """[(label, page, actual)] for every citation whose label is wrong."""
    wrong = []
    for label, tail, _cut in tails(text):
        if "." not in label:          # a bare chapter number, e.g. "§4"
            continue
        named = span(label, rows)
        for page in pages_in(tail):
            ok = admissible(page, rows, shared)
            if not set(named) & set(ok):
                wrong.append((label, page, ok[0]))
    return wrong


def unreadable(text):
    """[label] for each citation whose tail was cut off by the cap.

    These are not passes and not failures: the check could not be performed on
    them, which is exit 2 and must be said out loud.

    Every capped citation counts, not only one that retained no page at all.
    The first version asked `not pages_in(tail)`, which still lost the case
    that matters most: a citation naming a correct page BEFORE the cut and a
    wrong one after it read as fully checked, and the page past the cut was
    skipped in silence. A tail that was cut has an unknown remainder, and an
    unknown remainder cannot be called clean.
    """
    return [label for label, _tail, cut in tails(text) if cut and "." in label]


def _attribution():
    """(names, titles, split_at_books) for attributing citations to books.

    Borrowed from citations.py rather than re-derived. That module already
    pays for the hard parts -- de-accenting so "Lindstrom" matches
    "Lindstrom" with its o-umlaut, requiring a name to appear as a
    CONSECUTIVE phrase so "Cummings Real Analysis" wins over "Cummings", and
    treating any book name as a cut point -- and every one of those was a
    reported failure before it was a rule. A second implementation here would
    be a second place for them to come back.

    Nothing in this reaches the book drive: bookmap.json is in the repo, so
    the section gate still runs anywhere.
    """
    try:
        sys.path.insert(0, REPO)
        from scripts.citations import (load_bookmap,  # noqa: E402
                                       split_at_books)
    except ImportError as exc:
        raise NoVerdict("cannot import citation attribution: %s" % exc)
    bm = load_bookmap()
    return (sorted(bm), {k: v.get("title") for k, v in bm.items()},
            split_at_books)


def _primary(path):
    """The unit's primary book, or None — the same one citations.py uses.

    Attribution here started at None and waited to be told a book. That is
    right for the FIRST gate a citation meets and wrong for this one, because
    the two gates then disagree about the same file: a lesson writing "Aluffi
    §1.1, p. 5" throughout passes citations.py — bare "Aluffi" names no book,
    so the clause stays with the unit's primary, which is Aluffi Underground
    — and was SKIPPED entirely here as naming no indexed book. Thirteen
    citations, one gate saying PASS and the other saying nothing at all.

    Reading the primary from the syllabus makes the two agree by construction.
    A unit with no syllabus record, or a syllabus that cannot be read, gets
    None and the old behaviour: attribution waits to be told.
    """
    try:
        sys.path.insert(0, REPO)
        from scripts.citations import book_for_unit  # noqa: E402
        return book_for_unit(os.path.splitext(os.path.basename(path))[0])
    except Exception:
        return None


def refresh(book, out=INDEX):
    """Regenerate the index for one book from its page tree."""
    sys.path.insert(0, REPO)
    from scripts.pull import (all_pages, fit_offsets,  # noqa: E402
                              folio_candidates, page_text, pages_dir)

    d = pages_dir(book)
    rows_off, plateaus = fit_offsets(
        [(n, folio_candidates(page_text(d, n) or "")) for n in all_pages(d)])
    plateaus, dropped = main_text_plateaus(plateaus)
    blanks = set(n for n, _f, _w, off, _s in rows_off if off is None)
    plateaus = extend_first_plateau(plateaus, blanks)
    orphans = uncovered(plateaus)

    def printed(n):
        for off, lo, hi, _cnt in plateaus:
            if lo <= n <= hi:
                return n + off
        return None

    lettered = sum(len(LETTERED.findall(page_text(d, n) or ""))
                   for n in all_pages(d))
    heading = LETTERED if lettered else NUMBERED

    found = {}
    gaps = []
    shared = set()
    for n in all_pages(d):
        p = printed(n)
        if p is None:
            continue
        text = page_text(d, n) or ""
        for m in heading.finditer(text):
            # A section starts once. A later page mentioning the label in a
            # running head or a table of contents must not move the boundary,
            # so the FIRST page carrying the heading wins.
            if m.group(1) in found:
                continue
            found[m.group(1)] = p
            # Does the previous section still occupy the top of this page?
            # Drop bare folios and running heads before deciding: they are
            # short and they are on every page.
            kept = [ln.strip() for ln in text[:m.start()].splitlines()
                    if ln.strip() and not ln.strip().isdigit()
                    and len(ln.strip()) >= 60]
            if sum(len(ln) for ln in kept) >= SHARE_MIN:
                shared.add(p)
        # A chapter's opening page carries the word CHAPTER alone on its first
        # line, above the chapter number; a running head puts the folio and
        # the chapter title on the same line. The opening page belongs to no
        # section, and neither does anything after it until the chapter's
        # first section heading — which for an unsectioned chapter (Axler's
        # chapter 4) is the whole chapter.
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        if CHAPTER_OPEN.match(first):
            gaps.append(p)
    # A gap page is never a shared page. The two rows say opposite things —
    # "nothing from before is in force here" against "the previous section
    # runs on into this page" — and the gap is the one read off the book's
    # structure rather than off a character count. The count is what misfires:
    # on a chapter-opening page the text above the first section heading is
    # the chapter title and epigraph, which is new matter, not the tail of the
    # previous section. Abbott's printed 213 was recorded as both.
    shared -= set(gaps)
    if not found:
        raise NoVerdict("no section headings found for %r — neither the "
                        "lettered nor the numbered shape matched anything, so "
                        "this book labels its sections some third way" % book)

    data = {}
    if os.path.exists(out):
        with io.open(out, encoding="utf-8") as fh:
            data = json.load(fh)
    if dropped:
        print("  note: %d plateau(s) ignored as a bound-in second document: %s"
              % (len(dropped),
                 ", ".join("PDF %d-%d (printed %d-%d)"
                           % (lo, hi, lo + off, hi + off)
                           for off, lo, hi, _c in dropped)))
    if orphans:
        print("  note: %d page(s) covered by no plateau, so a section "
              "heading on one of them is not in this index: PDF %s"
              % (len(orphans), ", ".join(str(n) for n in orphans)))
    data[book] = {"sections": found, "gaps": sorted(gaps),
                  "shared": sorted(shared)}
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    return found, sorted(gaps), sorted(shared)


def selftest():
    rows = [(2, "1.A"), (12, "1.B"), (28, "2.A"), (39, "2.B"), (59, "3.B")]
    checks = []

    def one(name, ok):
        checks.append(ok)
        print("%s %s" % ("PASS" if ok else "FAIL", name))

    one("a page inside a section resolves to that section",
        section_of(30, rows) == "2.A")
    one("the first page of a section belongs to it, not the one before",
        section_of(39, rows) == "2.B")
    one("the last page before a section still belongs to the earlier one",
        section_of(38, rows) == "2.A")
    one("a page before every section is unplaceable, not the first section",
        section_of(1, rows) is None)

    # The defect this check exists for: right folio, right result, wrong label.
    good = '<span class="cite">— Axler §3.B, Definition 3.12, p. 59</span>'
    bad = '<span class="cite">— Axler §3.A, Definition 3.12, p. 59</span>'
    one("a correct label passes", check_text(good, rows) == [])
    one("the label citations.py cannot see is caught",
        check_text(bad, rows) == [("3.A", 59, "3.B")])

    # Pages named in the NEXT sentence belong to the next sentence's citation.
    two = ("Builds on la-03, whose Theorem 2.23 is Axler §2.A, p. 35. That "
           "result drives Theorems 2.35 and 2.39 above, pp. 44–46.")
    one("a following sentence's pages are not charged to this label",
        check_text(two, [(28, "2.A"), (44, "2.C")]) == [])

    # A page range writes only its endpoints; both are checked.
    one("both ends of a range are checked",
        check_text("Axler §2.A, pp. 28–39", rows) == [("2.A", 39, "2.B")])
    one("...and a range wholly inside its section is clean",
        check_text("Axler §2.A, pp. 28–38", rows) == [])
    one("...and a comma list is read as a list of pages",
        pages_in("pp. 28, 30 and 39") == [28, 30, 39])
    one("a number with no page marker is not read as a page",
        pages_in("Theorem 2.23 in section 2") == [])

    # A bare chapter number is not a section claim and must not be judged.
    one("a bare chapter label is skipped, not guessed at",
        check_text("Axler §4, p. 30", rows) == [])

    # A numbered book's labels must actually reach check_text. CITE read only
    # "§N" and "§N.LETTER", so Abbott's "§1.4" parsed as the bare chapter
    # "1" and every one of its citations was skipped as a non-claim -- 476 of
    # them in the `an` module alone, all reported as a clean pass. Adding the
    # numbered HEADING pattern indexed the book without ever checking it.
    # (Codex review of PR #25.) These two are the negative control.
    num = [(29, "1.4"), (36, "1.5")]
    one("a numbered section label is parsed, not read as a chapter",
        [lab for lab, _t, _c in tails("Abbott §1.4, p. 29")] == ["1.4"])
    one("...and a wrong numbered label fails",
        check_text("Abbott §9.9, p. 36", num) == [("9.9", 36, "1.5")])
    one("...while a bare chapter still is not judged",
        check_text("Abbott §1, p. 36", num) == [])

    # The length cap must not cut a page number in half.
    long_tail = ("Axler §2.A (" + "Theorem 2.7, " * 40 + "), pp. 28-38.")
    one("a page number straddling the length cap is read whole",
        check_text(long_tail, rows) == [])
    one("...and the number it would have been cut to is not reported",
        all(page not in (2, 3) for _lab, page, _act
            in check_text("Axler §9.9 (" + "x" * 398 + "), pp. 28-38.", rows)))

    # A page in a chapter gap belongs to no section, and the label that ran on
    # through the gap must not be accepted. Printed 51 is Axler's chapter-3
    # opening page: §2.C has ended and §3.A has not begun.
    gapped = [(44, "2.C"), (51, None), (52, "3.A")]
    one("a chapter-opening page is in no section",
        section_of(51, gapped) is None)
    one("...and a label that ran on through the gap is caught",
        check_text("Axler §2.C, Notation 3.1, p. 51", gapped)
        == [("2.C", 51, None)])
    one("...while the section after the gap is unaffected",
        check_text("Axler §3.A, p. 52", gapped) == [])
    one("a section starting on a gap page still wins",
        section_of(51, [(51, None), (51, "3.A")]) == "3.A")

    # Truncation must produce NO VERDICT, never a pass. The quiet direction of
    # the old cap: cut before the page marker, pages_in finds nothing, and a
    # wrong label is accepted in silence.
    runaway = "Axler §2.A " + "y" * (CAP + 50) + " pp. 59"
    one("a citation cut off before its page marker is reported unreadable",
        unreadable(runaway) == ["2.A"])
    one("...and a citation that reaches its pages is not",
        unreadable("Axler §2.A, pp. 28-38.") == [])
    one("...and a short wrong citation is still judged, not deferred",
        check_text("Axler §2.A, p. 59", rows) == [("2.A", 59, "3.B")])

    # Two books, two heading shapes, and the discriminator between them.
    one("Abbott's numbered section heading is read",
        NUMBERED.search("## 1.3 The Axiom of Completeness").group(1) == "1.3")
    one("...and the lettered pattern does not see it",
        LETTERED.search("## 1.3 The Axiom of Completeness") is None)
    one("Axler's lettered section heading is read",
        LETTERED.search("### 3.B Null Spaces and Ranges").group(1) == "3.B")
    one("a numbered RESULT heading is why the shape is not guessed per page",
        NUMBERED.search("### 10.58 **Definition**").group(1) == "10.58"
        and LETTERED.search("### 10.58 **Definition**") is None)
    one("a three-part result number is not a section heading",
        NUMBERED.search("### 1.3.6 Example") is None)

    # A bound-in solutions manual repeats the book's printed numbers.
    keep, drop = main_text_plateaus([(-12, 13, 269, 254), (-276, 277, 429, 150)])
    one("a plateau that repeats an earlier printed range is dropped",
        len(keep) == 1 and drop == [(-276, 277, 429, 150)])
    one("...while a book with drifting offsets keeps all of them",
        len(main_text_plateaus([(-17, 18, 66, 49), (-16, 67, 177, 111),
                                (-15, 178, 346, 169)])[0]) == 3)

    # A section range names every section between its ends.
    RANGE = [(3, "1.1"), (4, "1.2"), (5, "1.3"), (6, "1.4"), (7, "1.5")]
    one("a range covers the sections between its ends",
        span("1.2–1.5", RANGE) == ["1.2", "1.3", "1.4", "1.5"])
    one("...so a page in the later half of a range is right",
        check_text("Carter §1.2–1.5, pp. 4–7", RANGE) == [])
    one("...and a page outside the range is still wrong",
        check_text("Carter §1.2–1.3, p. 7", RANGE)
        == [("1.2–1.3", 7, "1.5")])
    one("a range whose end the book does not have is not resolved",
        span("1.2–1.9", RANGE) == ["1.2–1.9"])
    one("a hyphen before a word is not a range",
        [lab for lab, _t, _c in tails("Carter §1.4 - the rules, p. 6")]
        == ["1.4"])
    one("...nor is a hyphen before a bare COUNT",
        [lab for lab, _t, _c in tails("Carter §1.4 — 4 rules, p. 6")]
        == ["1.4"])
    one("...and that citation still passes",
        check_text("Carter §1.4 — 4 rules, p. 6", RANGE) == [])

    # A folio-less run at the lower edge of the first plateau is main text.
    one("the first plateau reaches down over folio-less pages",
        extend_first_plateau([(-18, 22, 384, 350)], {19, 20, 21})
        == [(-18, 19, 384, 350)])
    one("...and stops where the printed page would fall below 1",
        extend_first_plateau([(-18, 22, 384, 350)],
                             set(range(1, 22)))[0][1] == 19)
    one("...and does not reach over a page whose folio was read",
        extend_first_plateau([(-18, 22, 384, 350)], {19, 20})
        == [(-18, 22, 384, 350)])
    one("a later plateau is left alone, and its orphans are reported",
        extend_first_plateau([(-17, 18, 66, 49), (-16, 70, 177, 111)],
                             {67, 68, 69}) == [(-17, 18, 66, 49),
                                               (-16, 70, 177, 111)]
        and uncovered([(-17, 18, 66, 49), (-16, 70, 177, 111)])
        == [67, 68, 69])
    one("a book whose plateaus abut has no orphans",
        uncovered([(-17, 18, 66, 49), (-16, 67, 177, 111)]) == [])

    # Truncation is unreadable even when a page survived the cut.
    both = "Axler §2.A, p. 28 " + "y" * (CAP + 50) + " pp. 59"
    one("a capped citation is unreadable even if an early page survived",
        unreadable(both) == ["2.A"])

    # A page carrying the tail of one section above the heading of the next
    # admits both labels -- but only where the book actually shares it.
    share_rows = [(18, "1.4"), (29, "1.5")]
    one("a shared page admits the section above the heading",
        check_text("Abbott §1.4, Exercise 1.4.13, p. 29", share_rows, {29}) == [])
    one("...and the section below it",
        check_text("Abbott §1.5, Theorem 1.5.1, p. 29", share_rows, {29}) == [])
    one("...while an unshared start page admits only its own section",
        check_text("Axler §3.A, Definition 3.12, p. 59", rows) == [("3.A", 59, "3.B")])
    one("admissible names the page's own section first",
        admissible(29, share_rows, {29}) == ["1.5", "1.4"])

    # A gap page is never shared, even if the index says it is. Abbott's
    # printed 213 opens chapter 8: the chapter title and epigraph above the
    # §8.1 heading read as a previous section running on, so refresh marked
    # it shared, and §7.7 -- which ended before the chapter break -- was
    # admitted there. The gap row is the book's own statement that nothing
    # from before is in force, and it wins. (Codex review of PR #25.)
    gap_share = [(210, "7.7"), (213, None), (213, "8.1")]
    one("a gap page does not admit the label from before the gap",
        admissible(213, gap_share, {213}) == ["8.1"])
    one("...so a label that ran on through the gap is still caught",
        check_text("Abbott §7.7, p. 213", gap_share, {213})
        == [("7.7", 213, "8.1")])
    one("...while the section starting on that page is fine",
        check_text("Abbott §8.1, p. 213", gap_share, {213}) == [])
    one("the committed index records no page as both a gap and shared",
        all(not (set(v["shared"]) & set(v["gaps"]))
            for v in json.load(io.open(INDEX, encoding="utf-8")).values()))

    # The pre-gap index format cannot express a gap, so it is refused.
    import tempfile
    fd, tmp = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump({"Axler": {"1.A": 2}}, fh)
    try:
        load_index(tmp)
        one("the pre-gap index format is refused, not read", False)
    except NoVerdict:
        one("the pre-gap index format is refused, not read", True)
    finally:
        os.unlink(tmp)

    # Absence must never look like cleanliness.
    try:
        load_index(os.path.join(REPO, "resources", "no-such-file.json"))
        one("a missing index raises NoVerdict rather than passing", False)
    except NoVerdict:
        one("a missing index raises NoVerdict rather than passing", True)

    print("\n%d/%d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--refresh", metavar="BOOK",
                    help="regenerate the section index for BOOK from its "
                         "page tree (needs the book drive)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    try:
        if args.refresh:
            found, gaps, shared = refresh(args.refresh)
            print("%s: %d section(s) indexed, %d chapter gap(s)"
                  % (args.refresh, len(found), len(gaps)))
            for label, page in sorted(found.items(), key=lambda kv: kv[1]):
                print("  §%-5s printed %d" % (label, page))
            print("  gaps (no section in force from): %s"
                  % ", ".join(str(g) for g in gaps))
            print("  shared (two sections on one page): %s"
                  % (", ".join(str(x) for x in shared) or "none"))
            return 0

        index = load_index()
    except NoVerdict as exc:
        print("NO VERDICT: %s" % exc, file=sys.stderr)
        return 2

    if not args.paths:
        ap.error("give at least one path, or --refresh BOOK, or --selftest")

    # A file does NOT cite one book. pw-04 cites Abbott and Cummings in one
    # Sources line; an2 cites Lindstrom. Taking the first indexed name in the
    # file and checking every citation against it is the exact mechanism
    # citations.py already had to remove (see its attribute() docstring, which
    # names pw-04): it reported 60 wrong labels the moment numeric labels
    # started being parsed at all, and not one of them was about a citation.
    # Attribution here is the same rule -- sticky, left to right, cut at each
    # book NAME -- and a span belonging to a book with no index is counted and
    # reported as unchecked rather than measured against the wrong book.
    try:
        names, titles, split_at_books = _attribution()
    except NoVerdict as exc:
        print("NO VERDICT: %s" % exc, file=sys.stderr)
        return 2
    total = bad = 0
    parsed_citations = checked_citations = 0
    unindexed = {}
    unattributed = 0
    for path in args.paths:
        try:
            text = io.open(path, encoding="utf-8").read()
        except OSError as exc:
            print("NO VERDICT: cannot read %s: %s" % (path, exc),
                  file=sys.stderr)
            return 2
        cut = unreadable(text)
        if cut:
            print("NO VERDICT: %s: citation of §%s runs past %d characters "
                  "with no page marker — cannot be checked"
                  % (path, cut[0], CAP), file=sys.stderr)
            return 2
        # The denominator is derived before attribution can skip anything.
        # The checked and unchecked counters below must partition this raw
        # parse exactly; otherwise the gate has no verdict on its own coverage.
        parsed_citations += len([1 for lab, _t, _c in tails(text)
                                 if "." in lab])
        # Split BEFORE deciding whether this file is worth looking at. The
        # skip used to come first, so a file citing only Lindstrom was printed
        # as SKIP and its citations were never counted -- and the NOTE line
        # below, which exists precisely to be the honest denominator for the
        # PASS line, reported 195 when the true figure across the corpus was
        # 1432 in 112 files. A count that is itself silently short is worse
        # than no count, because it looks like the answer.
        # (CodeRabbit review of PR #25.)
        checked_here = False
        current = _primary(path)
        for part, named in split_at_books(text, names, titles):
            if named is not None:
                current = named
            if current is None or current not in index:
                n = len([1 for lab, _t, _c in tails(part) if "." in lab])
                if n:
                    if current is None:
                        unattributed += n
                    else:
                        unindexed[current] = unindexed.get(current, 0) + n
                continue
            checked_citations += len([1 for lab, _t, _c in tails(part)
                                      if "." in lab])
            checked_here = True
            rows, shared = index[current]
            for label, page, actual in check_text(part, rows, shared):
                bad += 1
                print("FAIL %s: cited §%s of %s, but printed p. %d is in %s"
                      % (path, label, current, page,
                         ("§" + actual) if actual
                         else "no section (a chapter opening, or an "
                              "unsectioned chapter)"))
        if checked_here:
            total += 1
        else:
            print("SKIP %s — names no indexed book" % path)
    unchecked_citations = sum(unindexed.values()) + unattributed
    if checked_citations + unchecked_citations != parsed_citations:
        print("NO VERDICT: citation partition mismatch: %d checked + %d "
              "unchecked != %d parsed"
              % (checked_citations, unchecked_citations, parsed_citations),
              file=sys.stderr)
        return 2
    if not total:
        print("NO VERDICT: no file named an indexed book", file=sys.stderr)
        return 2
    if unindexed:
        # A number, not a wall of lines, and never silence: these citations
        # were parsed and then not checked, and the report says how many.
        print("NOTE %d citation(s) name a book with no section index and were "
              "not checked: %s"
              % (sum(unindexed.values()),
                 ", ".join("%s %d" % kv for kv in sorted(unindexed.items()))))
    if unattributed:
        print("NOTE %d citation(s) name no book at all and were not checked"
              % unattributed)
    print("%s %d file(s) checked, %d citation(s) checked, %d unchecked, "
          "%d wrong label(s)"
          % ("FAIL" if bad else "PASS", total, checked_citations,
             unchecked_citations, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
