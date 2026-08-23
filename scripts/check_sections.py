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
INDEX = os.path.join(REPO, "resources", "sections.json")

# A citation's section label, then the text up to the next citation, the next
# tag, or the end of the sentence. Stopping at the sentence boundary matters:
# pages named in a FOLLOWING sentence belong to whatever that sentence cites,
# and letting the tail run on reports them against this label.
#
# The length cap is a safety net, not the primary stop, and it must never cut
# inside a number. A Sources line reading "§3.F (Definitions ...), pp. 101-114"
# is one long sentence: the cap landed in the middle of "101", the tail ended
# "pp. 1", and a correct citation was reported as naming printed page 1. A cap
# that silently shortens a page number is worse than no cap at all, because it
# can turn a wrong page into a plausible one just as easily as it turned a
# right one into an absurd one. The trailing \d* runs the tail on to the end of
# whatever digit run it stopped in.
CITE = re.compile(r"§(\d+(?:\.[A-Z])?)((?:(?!\.\s+[A-Z])[^§<]){0,400}\d*)")
# "pp. 28-38" names two pages, not one. Matching only the first let a range
# whose FAR end lands in the next section pass unexamined, which is the
# likeliest place for a footer's label to be wrong. Only the numbers actually
# written are taken; the interior of a range is never invented.
PAGES = re.compile(r"\bpp?\.\s*(\d+(?:\s*(?:[-–—,]|and)\s*\d+)*)")
_NUM = re.compile(r"\d+")


def pages_in(tail):
    """Every printed page number written under a p./pp. marker in `tail`."""
    return [int(n) for m in PAGES.finditer(tail)
            for n in _NUM.findall(m.group(1))]

# The section heading as the books print it: "## 3.B Null Spaces and Ranges".
HEADING = re.compile(r"^#{1,6}\s*\**\s*(\d+\.[A-F])\**\s+(.{2,60})", re.M)


class NoVerdict(Exception):
    """The check could not run. Exit 2 — never a silent pass."""


def load_index(path=INDEX):
    """{book: [[label, first_printed_page], ...]} sorted by page."""
    try:
        with io.open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise NoVerdict("cannot read section index %s: %s" % (path, exc))
    if not data or not any(data.values()):
        raise NoVerdict("section index %s names no section" % path)
    return {book: sorted((int(p), lab) for lab, p in rows.items())
            for book, rows in data.items()}


def section_of(page, rows):
    """The label of the last section that has started by printed `page`.

    None only for a page before the first section of the book.

    The index records where each section STARTS, not where it ends, so a page
    in the gap between a chapter's last section and the next chapter's first
    — Axler's chapter-opening pages, which carry Notation 3.1 and its
    siblings — is attributed to the section that precedes the gap. The verdict
    is still right in that case (the cited label does not match, and it should
    not have been a section label at all), but the "is in §X" hint names the
    section before the gap rather than saying "no section". Reported as a
    known limit rather than papered over: widening it would need the index to
    record chapter openings too.
    """
    found = None
    for start, label in rows:
        if page >= start:
            found = label
        else:
            break
    return found


def check_text(text, rows):
    """[(label, page, actual)] for every citation whose label is wrong."""
    wrong = []
    for m in CITE.finditer(text):
        label, tail = m.group(1), m.group(2)
        if "." not in label:          # a bare chapter number, e.g. "§4"
            continue
        for page in pages_in(tail):
            actual = section_of(page, rows)
            if actual != label:
                wrong.append((label, page, actual))
    return wrong


def refresh(book, out=INDEX):
    """Regenerate the index for one book from its page tree."""
    sys.path.insert(0, REPO)
    from scripts.pull import (all_pages, fit_offsets,  # noqa: E402
                              folio_candidates, page_text, pages_dir)

    d = pages_dir(book)
    _, plateaus = fit_offsets([(n, folio_candidates(page_text(d, n) or ""))
                               for n in all_pages(d)])

    def printed(n):
        for off, lo, hi, _cnt in plateaus:
            if lo <= n <= hi:
                return n + off
        return None

    found = {}
    for n in all_pages(d):
        p = printed(n)
        if p is None:
            continue
        for m in HEADING.finditer(page_text(d, n) or ""):
            # A section starts once. A later page mentioning the label in a
            # running head or a table of contents must not move the boundary,
            # so the FIRST page carrying the heading wins.
            found.setdefault(m.group(1), p)
    if not found:
        raise NoVerdict("no section headings found for %r" % book)

    data = {}
    if os.path.exists(out):
        with io.open(out, encoding="utf-8") as fh:
            data = json.load(fh)
    data[book] = found
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    return found


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

    # The length cap must not cut a page number in half.
    long_tail = ("Axler §2.A (" + "Theorem 2.7, " * 40 + "), pp. 28-38.")
    one("a page number straddling the length cap is read whole",
        check_text(long_tail, rows) == [])
    one("...and the number it would have been cut to is not reported",
        all(page not in (2, 3) for _lab, page, _act
            in check_text("Axler §9.9 (" + "x" * 398 + "), pp. 28-38.", rows)))

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
            found = refresh(args.refresh)
            print("%s: %d section(s) indexed" % (args.refresh, len(found)))
            for label, page in sorted(found.items(), key=lambda kv: kv[1]):
                print("  §%-5s printed %d" % (label, page))
            return 0

        index = load_index()
    except NoVerdict as exc:
        print("NO VERDICT: %s" % exc, file=sys.stderr)
        return 2

    if not args.paths:
        ap.error("give at least one path, or --refresh BOOK, or --selftest")

    # Every file in this repo cites one book, named in its Sources line. The
    # index is keyed by book so a second primary text cannot be checked
    # against the first one's page numbers.
    total = bad = 0
    for path in args.paths:
        try:
            text = io.open(path, encoding="utf-8").read()
        except OSError as exc:
            print("NO VERDICT: cannot read %s: %s" % (path, exc),
                  file=sys.stderr)
            return 2
        book = next((b for b in index if b.lower() in text.lower()), None)
        if book is None:
            print("SKIP %s — names no indexed book" % path)
            continue
        wrong = check_text(text, index[book])
        total += 1
        for label, page, actual in wrong:
            bad += 1
            print("FAIL %s: cited §%s, but printed p. %d is in %s"
                  % (path, label, page,
                     ("§" + actual) if actual else "no section (before §"
                      + index[book][0][1] + ")"))
    if not total:
        print("NO VERDICT: no file named an indexed book", file=sys.stderr)
        return 2
    print("%s %d file(s) checked, %d wrong label(s)"
          % ("FAIL" if bad else "PASS", total, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
