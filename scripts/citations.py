"""citations.py — does the page a lesson cites actually contain the result?

The last self-attested step in the authoring loop. Gate 1
(check_lesson_coverage.py) checks that an id named in a problem set appears in
its lesson; gate 8 checks the mission strip against the syllabus. Nothing
checked the thing the whole source discipline rests on: that "Theorem 7.6,
p. 225" is a page where Theorem 7.6 is actually printed.

It needed building. A read-back of pw-01 by hand on 2026-08-21 found SIX wrong
citations in one unit — a printed page that held an unrelated definition, two
exercises attributed to a section they are not in, a theorem placed one section
early, and a proposition marked "composed" that is Proposition 7.2 verbatim.
None of it was catchable by any existing gate, and all of it is mechanical.

  python scripts/citations.py problems/sets/pw-01.md lessons/pw/pw-01.html
  python scripts/citations.py --unit pw-01
  python scripts/citations.py --selftest

A citation SPAN is a parenthetical aside, a `<span class="cite">`, a
`<p class="cite">` or a Sources line. Within one span, every result id must be
findable on at least one of the printed pages that span names. That is the
semantics the authors were writing to, and it is deliberately lenient: a span
listing four results and a page range asserts only that they live in there.

Requires the per-page markdown tree from resources/bookmap.json, so this runs
locally and NOT in CI, exactly like gate 9's re-execution half. It says so
loudly rather than passing vacuously when the tree is absent.

Exit 0 all citations check out, 1 if any fails, 2 if it could not run.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.pull import (all_pages, fit_offsets, folio_candidates,  # noqa: E402
                          load_bookmap, page_text, pages_dir)

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KINDS = ("Theorem", "Lemma", "Proposition", "Definition", "Corollary",
         "Example", "Exercise", "Fact", "Axiom", "Remark")
# Multi-level numbers must be captured WHOLE. Abbott numbers three deep —
# "Lemma 1.3.7", "Theorem 2.4.2" — and a pattern stopping at two components
# truncates that to "Lemma 1.3", which then matches a page carrying Lemma 1.3.9
# just as happily. That is a false PASS, and it would have applied to all 14
# `an` units. `+` not `?` on the repeated group.
RESULT = re.compile(r"\b(%s)\s+(\d+(?:\.\d+)+[a-z]?)" % "|".join(KINDS))
# "p. 225", "pp. 41-42", "pp. 220–221" (hyphen or en dash)
PAGES = re.compile(r"\bpp?\.\s*(\d+)(?:\s*[-–—]\s*(\d+))?")

SPAN_PATTERNS = (
    re.compile(r'<span class="cite">(.*?)</span>', re.S),
    re.compile(r'<p class="cite">(.*?)</p>', re.S),
    re.compile(r"^\*\*Sources:\*\*(.*?)(?=\n\n)", re.S | re.M),
    re.compile(r"^<footer>(.*?)</footer>", re.S | re.M),
    re.compile(r"\*\(([^)]*?\bpp?\.\s*\d+[^)]*?)\)\*", re.S),
)


def strip_tags(text):
    return re.sub(r"<[^>]+>", " ", text)


def spans(text):
    """Citation spans, as (span_text, line_number)."""
    out = []
    for pat in SPAN_PATTERNS:
        for m in pat.finditer(text):
            out.append((strip_tags(m.group(1)), text[:m.start()].count("\n") + 1))
    return out


def printed_pages_in(span):
    pages = set()
    for m in PAGES.finditer(span):
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        if hi < lo or hi - lo > 60:      # a malformed or absurd range
            pages.add(lo)
            continue
        pages.update(range(lo, hi + 1))
    return pages


def results_in(span):
    return sorted({"%s %s" % (m.group(1), m.group(2)) for m in RESULT.finditer(span)})


class Book:
    """A book's printed-folio -> PDF-page map, fitted once."""

    def __init__(self, name):
        self.name = name
        self.dir = pages_dir(name)
        if not os.path.isdir(self.dir):
            raise RuntimeError("pages tree for %r is not on this machine: %s"
                               % (name, self.dir))
        pages = [(n, folio_candidates(page_text(self.dir, n) or ""))
                 for n in all_pages(self.dir)]
        rows, plateaus = fit_offsets(pages)
        # Only substantial plateaus define pagination; a lone disagreeing page
        # is a chapter number or an index reference (see pull.fit_offsets).
        self.plateaus = [p for p in plateaus if p[3] > 1]

    def pdf_pages_for(self, printed):
        """Every PDF page that could carry this printed folio.

        A book with drifting offsets (Axler: -17, -16, -15) can in principle
        map one printed page from more than one plateau, and a book with a
        bound-in solutions manual (Abbott, from PDF 270) certainly does. All
        candidates are returned and the caller accepts a hit on any — the
        alternative is picking one and being confidently wrong.
        """
        out = []
        for off, lo, hi, _ in self.plateaus:
            n = printed - off
            if lo <= n <= hi:
                out.append(n)
        return out

    def text_of(self, pdf_page):
        return page_text(self.dir, pdf_page) or ""


def normalise_for_search(text):
    """Collapse whitespace and drop markdown emphasis so "**Theorem 7.6.**"
    and "Theorem\\n7.6" both match "Theorem 7.6"."""
    return re.sub(r"\s+", " ", text.replace("*", "").replace("$", ""))


def book_label_for(num, raw):
    """The book's own header line for result `num`, or None.

    Axler numbers results without naming a kind: "1.34 Conditions for a
    subspace", "1.13 Commutativity of addition in F^n". Only its Definitions
    and Examples carry a kind word at all. So a citation reading "Theorem 1.34"
    can be perfectly correct about the page and still find no string
    "Theorem 1.34" anywhere in the book. Requiring the kind word marked all 19
    of la-01's and la-02's theorem citations wrong while every one of them
    pointed at the right page.
    """
    m = re.search(r"^#{1,6}\s*\**\s*%s\**\s+(.+)$" % re.escape(num), raw, re.M)
    if m:
        return re.sub(r"[*#$]", "", m.group(1)).strip()[:60]
    m = re.search(r"^\*\*%s\**\s+(.+)$" % re.escape(num), raw, re.M)
    return re.sub(r"[*#$]", "", m.group(1)).strip()[:60] if m else None


def found_on_page(result, blob, raw=None):
    """Locate a cited result. Returns "exact", "number-only", or None.

    "exact"       — the book prints this kind and this number together.
    "number-only" — the book prints this number as a result header, under a
                    different kind word or none. The citation is right about
                    WHERE and loose about WHAT it is called; reported as a
                    warning, never as a wrong page.
    None          — the number is not a result header on the cited page.

    Both word orders are accepted, because books disagree: Cummings and Abbott
    print "Definition 2.2", Axler prints "1.8 Definition". Matching is
    case-insensitive because Aluffi sets headers in small caps —
    "DEFINITION 1.1", "LEMMA 1.2". Each of those three conventions, taken
    alone, inverted this gate across a whole module while the citations under
    it were correct.

    "Exercise 2.5(a)" is printed as "Exercise 2.5." with an (a) item under it,
    so a trailing item letter is stripped before matching.
    """
    kind, _, num = result.partition(" ")
    stem = re.sub(r"[a-z]$", "", num)
    hay = blob.lower()
    k = kind.lower()
    for n in {num, stem}:
        if "%s %s" % (k, n) in hay or "%s %s" % (n, k) in hay:
            return "exact"
    if raw is not None:
        for n in {num, stem}:
            if book_label_for(n, raw) is not None:
                return "number-only"
    return None


def check_file(path, book, verbose=False):
    """Returns (failures, checked). Prints a row per failing citation."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    failures, warnings, checked = [], [], 0
    for span, line in spans(text):
        pages = printed_pages_in(span)
        results = results_in(span)
        if not pages or not results:
            continue
        pdf_pages = sorted({n for p in pages for n in book.pdf_pages_for(p)})
        if not pdf_pages:
            failures.append("line %d: printed page(s) %s are not in %s"
                            % (line, ",".join(str(p) for p in sorted(pages)), book.name))
            continue
        raw = "\n".join(book.text_of(n) for n in pdf_pages)
        blob = normalise_for_search(raw)
        for r in results:
            checked += 1
            status = found_on_page(r, blob, raw)
            if status is None:
                failures.append(
                    "line %d: %s is not on printed p. %s (PDF %s)"
                    % (line, r, ",".join(str(p) for p in sorted(pages)),
                       ",".join(str(n) for n in pdf_pages)))
            elif status == "number-only":
                num = r.partition(" ")[2]
                warnings.append(
                    "line %d: %s is on printed p. %s, but the book heads it %r"
                    % (line, r, ",".join(str(p) for p in sorted(pages)),
                       book_label_for(re.sub(r"[a-z]$", "", num), raw)))
            elif verbose:
                print("  ok  %s on printed p. %s"
                      % (r, ",".join(str(p) for p in sorted(pages))))
    for w in warnings:
        print("WARN %s" % w)
    for f_ in failures:
        print("FAIL %s" % f_)
    return failures, checked


def book_for_unit(uid):
    """The unit's primary book, from the syllabus resource line."""
    import yaml
    with open(os.path.join(REPO, "curriculum", "syllabus.yaml"), encoding="utf-8") as f:
        syl = yaml.safe_load(f)
    bm = load_bookmap()
    unit = next((u for u in syl["units"] if u["id"] == uid), None)
    if unit is None:
        return None
    for res in unit.get("resources", []):
        for name in sorted(bm, key=len, reverse=True):
            if res.lower().startswith(name.lower()):
                return name
    return None


def selftest():
    total, fails = [0], []

    def check_one(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    check_one("finds a result id and a single page",
              results_in("Cummings §7.4, Theorem 7.6, p. 225") == ["Theorem 7.6"]
              and printed_pages_in("p. 225") == {225})
    check_one("expands an en-dash page range",
              printed_pages_in("pp. 220–221") == {220, 221})
    check_one("expands a hyphen page range",
              printed_pages_in("pp. 41-42") == {41, 42})
    check_one("collects several results from one span",
              results_in("Definition 2.2, p. 36; Propositions 2.4, 2.6, pp. 37-38")
              == ["Definition 2.2"])
    check_one("plural 'Propositions 2.4, 2.6' is NOT silently read as two ids",
              # A known limit, asserted so it cannot regress into a false PASS:
              # only the first is matched, because "2.6" carries no keyword.
              results_in("Propositions 2.4, 2.6") == [])
    check_one("an absurd range does not expand to thousands of pages",
              printed_pages_in("pp. 12-9000") == {12})
    check_one("a span with no page reference yields nothing to check",
              printed_pages_in("Cummings §7.4, Theorem 7.6") == set())
    check_one("markdown emphasis does not hide a result",
              "Theorem 7.6" in normalise_for_search("**Theorem 7.6.** The number"))
    check_one("a line break inside a result id does not hide it",
              "Theorem 7.6" in normalise_for_search("Theorem\n7.6. The number"))
    check_one("a cite span is extracted from HTML",
              spans('<span class="cite">— Cummings §7.4, p. 224</span>')[0][0].strip()
              .startswith("— Cummings"))
    check_one("a markdown parenthetical aside is extracted",
              any("Exercise 2.6" in s for s, _ in
                  spans("*(Cummings, Exercise 2.6, p. 69)*")))
    check_one("a parenthetical with no page is not treated as a citation span",
              not any("Theorem 9.9" in s for s, _ in spans("*(see Theorem 9.9)*")))

    # The book-order controls. Axler and Aluffi print the number first; matching
    # only the citation's own order inverted this gate on 21 of 21 la-01 lines.
    check_one("kind-first printing is matched (Cummings, Abbott)",
              found_on_page("Definition 2.2", "An integer n is even. Definition 2.2 says"))
    check_one("number-first printing is matched (Axler, Aluffi)",
              found_on_page("Definition 1.8", "1.8 Definition list, length Suppose n"))
    check_one("an item letter is stripped (Exercise 2.5(a) prints as Exercise 2.5)",
              found_on_page("Exercise 2.5a", "Exercise 2.5. Prove the following. (a)"))
    check_one("a DIFFERENT result on the page is not accepted (no false pass)",
              not found_on_page("Definition 1.8", "1.9 Definition something else"))
    check_one("a near-miss number is not accepted",
              not found_on_page("Theorem 1.13", "1.130 Theorem and 1.1 Theorem"))
    check_one("small-caps printing is matched (Aluffi)",
              found_on_page("Definition 1.1", "DEFINITION 1.1 Let a, b be in Z"))
    check_one("small caps with the kind first is matched too",
              found_on_page("Lemma 1.2", "LEMMA 1.2 If b divides a"))
    check_one("case-insensitivity does not make a wrong number pass",
              not found_on_page("Lemma 1.9", "LEMMA 1.2 If b divides a"))

    # Axler heads results with a number and a descriptive title and no kind
    # word at all. Location is right; the kind word is ours. WARN, not FAIL.
    axler = "### 1.34 Conditions for a subspace\n\nA subset U of V is..."
    check_one("a number-only book header is located, not called wrong",
              found_on_page("Theorem 1.34", normalise_for_search(axler), axler)
              == "number-only")
    check_one("...and the book's own wording is recovered for the warning",
              book_label_for("1.34", axler) == "Conditions for a subspace")
    check_one("an exact kind+number match outranks the number-only path",
              found_on_page("Definition 1.32",
                            normalise_for_search("### 1.32 Definition subspace"),
                            "### 1.32 Definition subspace") == "exact")
    check_one("a number that is NOT a header on the page is still a failure",
              found_on_page("Theorem 9.9", "we mention 9.9 in passing here",
                            "we mention 9.9 in passing here") is None)
    check_one("a bare number in prose does not count as a header",
              book_label_for("9.9", "as shown in 9.9 above, the result") is None)

    # Abbott numbers three deep. Truncating to two components turns a wrong
    # citation into a passing one.
    check_one("a three-level number is captured whole (Abbott)",
              results_in("Lemma 1.3.7, p. 16") == ["Lemma 1.3.7"])
    check_one("a three-level citation does NOT match a sibling result",
              not found_on_page("Lemma 1.3.7", "lemma 1.3.9 assume s is an upper bound",
                                "**Lemma 1.3.9** Assume s"))
    check_one("a three-level citation matches its own result",
              found_on_page("Lemma 1.3.7", "lemma 1.3.7 assume s is an upper bound",
                            "**Lemma 1.3.7** Assume s") == "exact")
    check_one("two-level numbering still works (Cummings, Axler, Aluffi)",
              results_in("Theorem 7.6, p. 225") == ["Theorem 7.6"])

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--unit", help="check both files of a unit")
    ap.add_argument("--book", help="override the book chosen from the syllabus")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    paths = list(a.paths)
    book_name = a.book
    if a.unit:
        mod = a.unit.rsplit("-", 1)[0]
        for p in (os.path.join(REPO, "problems", "sets", a.unit + ".md"),
                  os.path.join(REPO, "lessons", mod, a.unit + ".html")):
            if os.path.exists(p):
                paths.append(p)
        book_name = book_name or book_for_unit(a.unit)
    if not paths:
        ap.error("give paths or --unit")
    if not book_name:
        uid = os.path.splitext(os.path.basename(paths[0]))[0]
        book_name = book_for_unit(uid)
    if not book_name:
        print("ERROR could not tell which book to check against; pass --book")
        return 2

    try:
        book = Book(book_name)
    except RuntimeError as e:
        print("ERROR %s" % e)
        print("This gate needs the per-page markdown tree and cannot run here.")
        return 2

    rc, total = 0, 0
    for p in paths:
        print("=== %s  (against %s)" % (p, book.name))
        failures, checked = check_file(p, book, a.verbose)
        total += checked
        if failures:
            rc = 1
        print("%s %d citation(s) checked, %d wrong"
              % ("FAIL" if failures else "PASS", checked, len(failures)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
