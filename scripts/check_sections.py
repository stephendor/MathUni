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
CITE = re.compile(r"§(\d+(?:\.[A-Z])?)")
# The tail runs to the next citation, the next tag, or the end of the sentence.
# Stopping at the sentence boundary matters: pages named in a FOLLOWING
# sentence belong to whatever that sentence cites, and letting the tail run on
# reports them against this label.
_STOP = re.compile(r"[§<]|\.\s+[A-Z]")


def tails(text):
    """(label, tail, truncated) for each §LABEL in `text`, in order."""
    out = []
    for m in CITE.finditer(text):
        rest = text[m.end():]
        stop = _STOP.search(rest)
        end = stop.start() if stop else len(rest)
        truncated = end > CAP
        out.append((m.group(1), rest[:min(end, CAP)], truncated))
    return out
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
    """{book: [(printed_page, label_or_None), ...]} sorted by page.

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
        out[book] = sorted(rows, key=lambda r: (r[0], r[1] is not None))
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


def check_text(text, rows):
    """[(label, page, actual)] for every citation whose label is wrong."""
    wrong = []
    for label, tail, _cut in tails(text):
        if "." not in label:          # a bare chapter number, e.g. "§4"
            continue
        for page in pages_in(tail):
            actual = section_of(page, rows)
            if actual != label:
                wrong.append((label, page, actual))
    return wrong


def unreadable(text):
    """[label] for each citation whose tail hit the cap before any page.

    These are not passes and not failures: the check could not be performed on
    them, which is exit 2 and must be said out loud.
    """
    return [label for label, tail, cut in tails(text)
            if cut and "." in label and not pages_in(tail)]


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
    gaps = []
    for n in all_pages(d):
        p = printed(n)
        if p is None:
            continue
        text = page_text(d, n) or ""
        for m in HEADING.finditer(text):
            # A section starts once. A later page mentioning the label in a
            # running head or a table of contents must not move the boundary,
            # so the FIRST page carrying the heading wins.
            found.setdefault(m.group(1), p)
        # A chapter's opening page carries the word CHAPTER alone on its first
        # line, above the chapter number; a running head puts the folio and
        # the chapter title on the same line. The opening page belongs to no
        # section, and neither does anything after it until the chapter's
        # first section heading — which for an unsectioned chapter (Axler's
        # chapter 4) is the whole chapter.
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        if first.upper().startswith("CHAPTER") and len(first) <= 12:
            gaps.append(p)
    if not found:
        raise NoVerdict("no section headings found for %r" % book)

    data = {}
    if os.path.exists(out):
        with io.open(out, encoding="utf-8") as fh:
            data = json.load(fh)
    data[book] = {"sections": found, "gaps": sorted(gaps)}
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    return found, sorted(gaps)


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
            found, gaps = refresh(args.refresh)
            print("%s: %d section(s) indexed, %d chapter gap(s)"
                  % (args.refresh, len(found), len(gaps)))
            for label, page in sorted(found.items(), key=lambda kv: kv[1]):
                print("  §%-5s printed %d" % (label, page))
            print("  gaps (no section in force from): %s"
                  % ", ".join(str(g) for g in gaps))
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
        cut = unreadable(text)
        if cut:
            print("NO VERDICT: %s: citation of §%s runs past %d characters "
                  "with no page marker — cannot be checked"
                  % (path, cut[0], CAP), file=sys.stderr)
            return 2
        wrong = check_text(text, index[book])
        total += 1
        for label, page, actual in wrong:
            bad += 1
            print("FAIL %s: cited §%s, but printed p. %d is in %s"
                  % (path, label, page,
                     ("§" + actual) if actual
                     else "no section (a chapter opening, or an "
                          "unsectioned chapter)"))
    if not total:
        print("NO VERDICT: no file named an indexed book", file=sys.stderr)
        return 2
    print("%s %d file(s) checked, %d wrong label(s)"
          % ("FAIL" if bad else "PASS", total, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
