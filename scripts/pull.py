"""pull.py — source-text extractor and folio checker for lesson authoring.

Reads the per-PDF-page markdown under bookmap[<book>]["pages"], so every
extract carries the PDF page number a citation needs, and every citation can be
checked against the folio actually printed on that page.

  python scripts/pull.py --list                       # known books
  python scripts/pull.py Abbott --find "Cauchy Criterion"
  python scripts/pull.py Abbott --pages 166-170 [--out x.md]
  python scripts/pull.py Abbott --folio 160-170       # printed folio + offset

Promoted into the repo 2026-08-21. Two things were recovered in the process.

FIRST, the copy chain lost a feature. Two lineages of this script exist in the
scratchpads: an argparse version with --find and --pages (2026-08-08), and a
positional-argument rewrite (2026-08-11) that kept only the page dump. The
later, smaller one is what the S1 handoff pointed at, so the page-search
capability had silently disappeared from the toolchain with nothing recording
that it ever existed. That is the cost of a tool living in a temp directory:
a regression with no diff, no review, and no way to notice.

SECOND, --folio is new here, and mechanises a discipline that had been prose.
LESSON-GUIDE requires the printed folio to be read off the page cited, with the
offset verified on consecutive pages AND on a page in a distant chapter. The S4
plan asserted a constant Ghrist offset that was false — it drifted, because
unnumbered chapter-opener pages are counted by the PDF and not by the book. A
prose rule caught none of that. This prints the folio it can actually see, says
NO FOLIO when it sees none, and refuses to average the two: a page with no
folio proves nothing, and must not silently contribute to an offset.
"""
import argparse
import json
import os
import re
import sys

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console (cf. srs/scheduler.py)
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKMAP = os.path.join(REPO, "resources", "bookmap.json")

# A folio is a line that is nothing but a page number, at the very top or very
# bottom of the page's text. Anything else — a numbered equation, a year, a
# theorem number — is not a folio, and guessing at one is worse than reporting
# none, because the whole point is to catch a pagination scheme changing.
FOLIO_LINE = re.compile(r"^\**\s*(\d{1,4})\s*\**$")
EDGE_LINES = 2  # how far from each edge a folio may sit

_LIST_FAMILIES = (
    ("roman", re.compile(r"^\s*\((i{1,3}|iv|v|vi{0,3}|ix|x)\)\s+", re.I | re.M), "i"),
    ("lettered", re.compile(r"^\s*\(([a-z])\)\s+", re.I | re.M), "a"),
    ("numbered", re.compile(r"^\s*(\d+)\.\s+", re.M), "1"),
)
_EQUIVALENT = re.compile(r"the following are equivalent\s*:", re.I)
_EXTRACT_BOUNDARY = re.compile(r"(?m)^(?:=== p\.\d+.*===|#{1,6}\s+.*)$")
_PAGE_BOUNDARY = re.compile(r"^=== p\.\d+.*===")


def _marker_value(name, marker):
    if name == "numbered":
        return int(marker)
    if name == "lettered":
        return ord(marker.lower()) - ord("a") + 1
    roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
             "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10}
    return roman[marker.lower()]


def _list_regions(text):
    """Split an extraction where a new page or Markdown heading starts."""
    starts = [0] + [match.start() for match in _EXTRACT_BOUNDARY.finditer(text)]
    starts = sorted(set(starts))
    return [text[start:end] for start, end in
            zip(starts, starts[1:] + [len(text)]) if text[start:end].strip()]


def extract_integrity_errors(text):
    """Structural signs that a page extraction silently dropped list items."""
    errors = []
    previous_last = {}
    for region_number, region in enumerate(_list_regions(text), 1):
        page_continuation = bool(_PAGE_BOUNDARY.match(region))
        roman_positions = {
            m.start() for m in _LIST_FAMILIES[0][1].finditer(region)}
        for name, pattern, first in _LIST_FAMILIES:
            matches = list(pattern.finditer(region))
            if name == "lettered":
                matches = [m for m in matches if m.start() not in roman_positions]
            first_value = (_marker_value(name, matches[0].group(1))
                           if matches else None)
            continues = (page_continuation and name in previous_last
                         and first_value == previous_last[name] + 1)
            if matches and matches[0].group(1).lower() != first and not continues:
                errors.append("%s list begins at %s, not %s (region %d)"
                              % (name, matches[0].group(1), first,
                                 region_number))
            values = [_marker_value(name, match.group(1)) for match in matches]
            for index, (left, right) in enumerate(zip(values, values[1:])):
                # Returning to the first marker starts a new list. Requiring a
                # particular amount of intervening prose made extraction
                # integrity depend on an author's paragraph formatting and
                # rejected intact pages containing consecutive exercises.
                restarted = right == 1
                if restarted:
                    continue
                if right != left + 1:
                    errors.append("%s list jumps from %s to %s (region %d)" % (
                        name, left, right, region_number))
            if matches:
                previous_last[name] = _marker_value(name, matches[-1].group(1))
            elif not page_continuation:
                previous_last.pop(name, None)
    for match in _EQUIVALENT.finditer(text):
        tail = text[match.end():match.end() + 2000]
        labelled = max((len(pattern.findall(tail))
                        for _name, pattern, _first in _LIST_FAMILIES), default=0)
        if labelled < 2:
            errors.append("'the following are equivalent' is followed by fewer "
                          "than two labelled clauses")
    return errors


def load_bookmap(path=BOOKMAP):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pages_dir(book, bookmap=None):
    bm = bookmap if bookmap is not None else load_bookmap()
    if book not in bm:
        sys.exit("unknown book %r; known: %s" % (book, ", ".join(sorted(bm))))
    return bm[book]["pages"]


def page_text(d, n):
    p = os.path.join(d, "page-%d" % n, "markdown.md")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def all_pages(d):
    return sorted(int(m.group(1)) for m in
                  (re.fullmatch(r"page-(\d+)", name) for name in os.listdir(d)) if m)


def folio_candidates(text):
    """Every bare number at either edge, as [(value, 'head'|'tail')].

    Both edges are returned rather than the first match, because preferring one
    edge picks the wrong number on exactly the pages that matter most. Axler's
    chapter openers carry 'CHAPTER' / '2' at the head and the real folio at the
    tail: a head-first reader calls PDF 44 page 2 and computes an offset of
    -42. Nine of Axler's twelve chapter openers do this, and the resulting
    phantom offsets are what a range fit has to see through. Which edge a
    number came from is kept because it is evidence in its own right.
    """
    lines = [ln for ln in text.split("\n") if ln.strip()]
    # The two slices must not overlap. On a page short enough that head[:2] and
    # lines[-2:] intersect, the same number is otherwise returned as both a
    # head and a tail candidate, and fit_offsets counts its vote twice.
    n = len(lines)
    spans = (("head", range(0, min(EDGE_LINES, n))),
             ("tail", range(max(EDGE_LINES, n - EDGE_LINES), n)))
    out = []
    for where, span in spans:
        for i in span:
            m = FOLIO_LINE.match(lines[i].strip())
            if m:
                out.append((int(m.group(1)), where))
    return out


def folio_of(text):
    """Single best-guess (folio, where) for one page in isolation, or (None, None).

    Kept for callers with one page and no range to fit against; it prefers the
    tail, since a head number competing with a tail number is the chapter-opener
    signature. Range work should use fit_offsets, which does not have to guess.
    """
    cands = folio_candidates(text)
    if not cands:
        return None, None
    tail = [c for c in cands if c[1] == "tail"]
    return (tail or cands)[0]


def fit_offsets(pages):
    """Fit offset plateaus over [(page, [(folio, where), ...]), ...].

    Returns (rows, plateaus) where rows is [(page, folio, where, offset, status)]
    and plateaus is [(offset, first_page, last_page, count)].

    The offset is a property of a RANGE, not of a page, so it is fitted rather
    than read: seed with the commonest offset across the range, then walk,
    keeping the candidate that agrees with the plateau in progress and starting
    a new plateau only when nothing agrees. A single page that disagrees with
    its neighbours on both sides is reported SUSPECT and kept out of the drift
    verdict — that is what a chapter number and an index page-reference both
    look like, and neither is a pagination change.
    """
    votes = {}
    for n, cands in pages:
        for f, _ in cands:
            votes[f - n] = votes.get(f - n, 0) + 1
    current = max(votes, key=lambda o: (votes[o], -abs(o))) if votes else None

    rows = []
    for n, cands in pages:
        if not cands:
            rows.append((n, None, None, None, "NO FOLIO"))
            continue
        agree = next((c for c in cands if c[0] - n == current), None)
        if agree is None:
            f, where = sorted(cands, key=lambda c: c[1] != "tail")[0]
            current = f - n
            rows.append((n, f, where, current, "NEW"))
        else:
            rows.append((n, agree[0], agree[1], current, "OK"))

    plateaus = []
    for n, f, where, off, status in rows:
        if off is None:
            continue
        if plateaus and plateaus[-1][0] == off:
            plateaus[-1][2], plateaus[-1][3] = n, plateaus[-1][3] + 1
        else:
            plateaus.append([off, n, n, 1])

    # A singleton plateau is SUSPECT only when it is INTERIOR and the plateaus
    # on either side of it agree with each other — that is what "disagrees with
    # both neighbours" actually requires, and a chapter number or an index
    # page-reference is exactly that shape.
    #
    # A singleton at the FIRST or LAST position has evidence on one side only,
    # so it cannot be shown to disagree with both. Excluding it anyway is how
    # `--folio 66-70` came to report "Consistent offset -16, exit 0" across
    # Axler's documented -17/-16 transition at 66/67: the last page of the -17
    # run was the range's first row, got called suspect, and the verdict lost
    # the boundary it was asked about. A false "consistent" over a real
    # transition is the Ghrist failure this whole subcommand exists to prevent.
    # (Codex review of PR #20, second round.)
    #
    # Suspects are also identified by POSITION, not by offset value: keying on
    # the offset marked every row sharing that number, including rows in a
    # substantial plateau elsewhere in the range.
    suspect_spans = [(p[1], p[2]) for p in suspect_plateaus(plateaus)]
    rows = [(n, f, w, o,
             "SUSPECT" if status != "NO FOLIO"
             and any(a <= n <= b for a, b in suspect_spans) else status)
            for n, f, w, o, status in rows]
    return rows, [tuple(p) for p in plateaus]


def suspect_plateaus(plateaus):
    """The plateaus that are a stray reading rather than a pagination change.

    One rule, used both to label rows and to decide the verdict — they were
    two rules once, and the verdict's version ("any plateau of one page")
    silently discarded a real boundary.
    """
    out = []
    for i, p in enumerate(plateaus):
        interior = 0 < i < len(plateaus) - 1
        if p[3] == 1 and interior and plateaus[i - 1][0] == plateaus[i + 1][0]:
            out.append(p)
    return out


def parse_range(spec):
    lo, _, hi = spec.partition("-")
    return int(lo), int(hi or lo)


def cmd_find(d, book, pattern):
    pat = re.compile(pattern, re.I)
    hits = [n for n in all_pages(d) if pat.search(page_text(d, n) or "")]
    print("%s: %d page(s) match %r" % (book, len(hits), pattern))
    print(" ".join(str(n) for n in hits))
    return 0


def cmd_pages(d, spec, out):
    lo, hi = parse_range(spec)
    chunks = []
    for n in range(lo, hi + 1):
        t = page_text(d, n)
        chunks.append("\n=== p.%d (NO SUCH PAGE) ===\n" % n if t is None
                      else "\n=== p.%d ===\n" % n + t)
    blob = "".join(chunks)
    integrity = extract_integrity_errors(blob)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(blob)
        print("wrote %s (%d chars, pp. %d-%d)" % (out, len(blob), lo, hi))
    else:
        print(blob)
    for error in integrity:
        print("EXTRACT INTEGRITY FAIL: %s — inspect the PDF page directly" % error,
              file=sys.stderr)
    return 1 if integrity else 0


def cmd_folio(d, book, spec):
    """Print printed-folio and implied offset per PDF page; flag any drift.

    Sign convention: printed = PDF + offset, so every offset here is negative.
    """
    lo, hi = parse_range(spec)
    pages = []
    absent = []
    for n in range(lo, hi + 1):
        t = page_text(d, n)
        if t is None:
            # A page whose markdown file is not there was never analysed. The
            # first version folded it into the empty-candidate list, which made
            # it indistinguishable from a real page carrying no folio — so a
            # range with only its endpoints extracted could report a consistent
            # offset and exit 0 while every page between them was unavailable.
            # That is the silent-absence failure mode exactly, and it was a
            # regression: the earlier positional version printed NO SUCH PAGE.
            # (Codex review of PR #20.)
            absent.append(n)
        pages.append((n, [] if t is None else folio_candidates(t)))

    rows, plateaus = fit_offsets(pages)
    print("%s — printed = PDF + offset" % book)
    for n, folio, where, off, status in rows:
        if n in absent:
            print("  PDF %4d  NO SUCH PAGE — not extracted, nothing was read" % n)
        elif folio is None:
            print("  PDF %4d  NO FOLIO — proves nothing about the offset" % n)
        elif status == "SUSPECT":
            print("  PDF %4d  printed %4d  offset %+d  (%s)  SUSPECT — disagrees with"
                  " both neighbours; a chapter number or an index reference reads"
                  " like this" % (n, folio, off, where))
        else:
            print("  PDF %4d  printed %4d  offset %+d  (%s)%s"
                  % (n, folio, off, where, "  <- offset changes here"
                     if status == "NEW" and n != rows[0][0] else ""))

    # A plateau counts toward the verdict unless it is a stray reading.
    # Counting only plateaus longer than one page discarded a genuine
    # boundary whenever the range began or ended on one.
    suspect = suspect_plateaus(plateaus)
    real = [p for p in plateaus if p not in suspect]
    nofolio = [n for n, f, _, _, _ in rows if f is None and n not in absent]
    if absent:
        print("\n%d of %d page(s) in %d-%d were NOT EXTRACTED: %s"
              % (len(absent), hi - lo + 1, lo, hi,
                 " ".join(str(n) for n in absent)))
        print("No verdict: an offset fitted over a range that was only "
              "partly read is not evidence about the range.")
        return 2
    if not plateaus:
        print("\nNo folio found on any page in %d-%d." % (lo, hi))
        return 1

    # The verdict is about DISTINCT offsets, not plateau count. A single
    # suspect page between two runs of the same real offset splits them into
    # two plateaus, and counting plateaus then announced "OFFSET IS NOT
    # CONSTANT" over a range with one offset in it — crying drift on exactly
    # the case SUSPECT exists to absorb. (Codex review of PR #20.)
    distinct = sorted({p[0] for p in real})
    suspect_pages = [n for n, f, _, _, s in rows if s == "SUSPECT"]

    # One folio in the whole range is not a fit. With every neighbour reading
    # NO FOLIO there is nothing for SUSPECT to disagree with, so a chapter
    # number or an index reference — the two things that read exactly like a
    # folio and that the suspect rule exists to reject — sails through as the
    # offset, and the range exits 0 announcing "Consistent offset across 1
    # page". The guide's requirement is agreement over consecutive pages, and
    # a single observation cannot express agreement with anything.
    # (Codex review of PR #20, sixth round.)
    supporting = sum(p[3] for p in real)
    if supporting < 2:
        print("\nOnly %d page(s) in %d-%d carried a usable folio. No verdict:"
              " an offset needs agreement across pages, and one reading cannot"
              " be told apart from a chapter number or an index reference."
              % (supporting, lo, hi))
        return 2

    if len(distinct) <= 1:
        off = distinct[0] if distinct else plateaus[0][0]
        print("\nConsistent offset %+d across %d page(s) with a folio."
              % (off, sum(p[3] for p in plateaus if p[0] == off)))
        if nofolio:
            print("%d page(s) carried no folio and were excluded: %s"
                  % (len(nofolio), " ".join(str(m) for m in nofolio)))
        if suspect_pages:
            print("%d page(s) SUSPECT and excluded: %s"
                  % (len(suspect_pages), " ".join(str(m) for m in suspect_pages)))
        print("A local run establishes the offset; check a distant chapter "
              "before relying on it.")
        return 0
    print("\nOFFSET IS NOT CONSTANT over %d-%d — %d distinct offsets:"
          % (lo, hi, len(distinct)))
    for off, a, b, count in real:
        print("  %+d on PDF %d-%d (%d pages)" % (off, a, b, count))
    print("Do not cite a printed page in this range from a single offset.")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("book", nargs="?")
    ap.add_argument("--list", action="store_true", help="list known books and exit")
    ap.add_argument("--find", metavar="REGEX", help="which pages mention this")
    ap.add_argument("--pages", metavar="LO-HI", help="dump these PDF pages")
    ap.add_argument("--folio", metavar="LO-HI", help="printed folio and offset per page")
    ap.add_argument("--out", metavar="PATH", help="write --pages output here")
    a = ap.parse_args(argv)

    bm = load_bookmap()
    if a.list:
        for name in sorted(bm):
            print("%-22s %s" % (name, bm[name]["title"]))
        return 0
    if not a.book:
        ap.error("give a book (or --list)")

    d = pages_dir(a.book, bm)
    if not os.path.isdir(d):
        sys.exit("pages tree for %r is not on this machine: %s" % (a.book, d))

    if a.find:
        return cmd_find(d, a.book, a.find)
    if a.folio:
        return cmd_folio(d, a.book, a.folio)
    if a.pages:
        return cmd_pages(d, a.pages, a.out)
    ap.error("give --find, --pages or --folio")


if __name__ == "__main__":
    sys.exit(main())
