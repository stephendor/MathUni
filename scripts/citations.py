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

DO NOT read a corpus-wide failure count as a defect count; sample before
acting on one. The largest contaminant is not in this script at all — it is the
unit's `resources:` line, which is what picks the book to check against. an2-01
named Oxford lecture notes and Abbott while its lesson is written from
Lindström, so this gate resolved it to Abbott and reported 25 of 31 citations
wrong; pointed at Lindström the same file reports 5. Six other an2 units named
only a source that resolves to nothing, so `book_for_unit` returned None and
the gate could not run at all — 156 citations no check in the repository ever
looked at. `scripts/check_resources.py` is the gate for that, and the syllabus
is repaired on the `s1-syllabus-audit` branch.

(An earlier version of this paragraph blamed the folio fit — "Lindström fits
-12 globally where --folio measures -13". That was wrong: Lindström's global
fit is a single plateau at -13 over PDF 15-382 and agrees with the local
measurement. The two PDF candidates in the failure line were Abbott's, one for
the text and one for its bound-in solutions manual, which is what gave the
wrong book away. Recorded because a plausible diagnosis that survives one
reading is exactly what this gate exists to make impossible.)

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
#
# The number may also be a bare INTEGER. Axler and Lindström number exercises
# that way ("Exercise 10", "Exercise 3" of a section), and requiring a dot meant
# 237 such citations inside citation spans matched nothing at all and left the
# denominator silently — including every Axler exercise in the `la` sets. The
# dotted alternative is written first so that alternation prefers it: "6.11"
# must be captured whole and never as "6".
NUM = r"\d+(?:\.\d+)+[a-z]?|\d+[a-z]?"
RESULT = re.compile(r"\b(%s)\s+(%s)(?!\d)(?!\.\d)" % ("|".join(KINDS), NUM))
# The plural/range form: "Exercises 6.6-6.9", "Theorems 1.1 and 1.2",
# "Definitions 8.3, 8.5". See results_in().
NUMBER = re.compile(r"(?:%s)(?!\d)(?!\.\d)" % NUM)
PLURALS = {"Theorem": "Theorems", "Lemma": "Lemmas", "Proposition": "Propositions",
           "Definition": "Definitions", "Corollary": "Corollaries",
           "Example": "Examples", "Exercise": "Exercises", "Fact": "Facts",
           "Axiom": "Axioms", "Remark": "Remarks"}
SINGULAR = {p.lower(): s for s, p in PLURALS.items()}
PLURAL = re.compile(
    r"\b(%s)\s+(%s(?:\s*(?:[-–—,]|and)\s*%s)+)"
    % ("|".join(PLURALS.values()), NUMBER.pattern, NUMBER.pattern))
# "p. 225", "pp. 41-42", "pp. 220–221" (hyphen or en dash) — and this repo's own
# "printed 394" / "printed **268–274**" form, which is what the lab and an2
# source blocks use. Accepting only `p.` left 1084 occurrences of `printed NNN`
# unparsed, so those spans produced results and no pages and check_file skipped
# them entirely: the largest silent-absence hole this gate has had. The
# emphasis markers are stripped from spans before matching, so the `**` form
# arrives here bare.
PAGES = re.compile(
    r"(?:\bpp?\.|\bprinted)\s*[*_]*\s*(\d+)[*_]*"
    r"(?:\s*[-–—]\s*[*_]*(\d+))?", re.I)

SPAN_PATTERNS = (
    re.compile(r'<span class="cite">(.*?)</span>', re.S),
    re.compile(r'<p class="cite">(.*?)</p>', re.S),
    re.compile(r"^\*\*Sources:\*\*(.*?)(?=\n\n)", re.S | re.M),
    re.compile(r"^<footer>(.*?)</footer>", re.S | re.M),
    # `[^)]` stopped the parenthetical span at the FIRST close paren, so a
    # citation naming an exercise part — "Exercise 8.28(d), p. 280" — was cut
    # off before its page reference and the whole span went unrecognised. Not
    # a wrong verdict: no verdict, silently, and the citation simply dropped
    # out of the denominator. Cummings letters its exercise parts, so pw-03's
    # set lost four citations that way. One level of nesting is enough for
    # every form in the corpus.
    re.compile(r"\*\(((?:[^()]|\([^()]*\))*?\bpp?\.\s*\d+(?:[^()]|\([^()]*\))*?)\)\*",
               re.S),
)


class Unreadable(Exception):
    """An input this gate was asked to read could not be read. Verdict 2."""


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
    """Every result id a span cites, plural and range forms included.

    RESULT only matches the singular-and-separate form, so `Exercises 6.6-6.9`
    and `Theorems 1.1 and 1.2` matched NOTHING: not a wrong verdict, no verdict,
    with the citations dropping silently out of the denominator. There are 190
    such citations in the corpus — more than every defect this gate has found
    put together. check_lesson_coverage.py solved exactly this in its own
    REF_PATTERN (its Obs 153); the fix was never carried across to the sibling
    script, which is the same "fixed the instance, not the class" mistake as
    gate.py's `data-type` and mission.py's `data-class`.

    Only the numbers actually written are expanded — `Exercises 6.6-6.9` gives
    6.6 and 6.9, never the interior — because inferring 6.7 and 6.8 would
    invent citations the author did not make and then hold them to a page.
    """
    ids = {"%s %s" % (m.group(1), m.group(2)) for m in RESULT.finditer(span)}
    for kinds, numbers in PLURAL.findall(span):
        kind = SINGULAR[kinds.lower()]
        ids.update("%s %s" % (kind, n) for n in NUMBER.findall(numbers))
    return sorted(ids)


def clauses(span):
    """A span's semicolon-separated assertions, as [(text, pages)].

    Leniency WITHIN one assertion is deliberate (see the module docstring): a
    parenthetical naming four results and a page range asserts only that they
    live in there. Leniency ACROSS assertions is not, and a Sources line is
    several assertions sharing a line:

        §4.1-4.2 (Principle 4.1, Propositions 4.2-4.3), pp. 107-115;
        §4.3 (Theorem 4.8, Proposition 4.10), pp. 124-133;
        §4 Exercises (4.1, 4.7, 4.12), pp. 143-145

    Taking the union gave every result in that line a 22-page target, so
    `Theorem 4.8 on printed p. 107,…,145` passed. pw-02's header did pass,
    with its exercise pages wrong by five, while the gate built to catch
    exactly that said ok. A check whose target grows with the number of things
    being checked is nearly unfalsifiable where citations are densest.

    A clause carrying no page reference of its own falls back to the span's
    pages, so `(Cummings §4.3, Theorem 4.8, pp. 125-127)` stays one assertion
    however it is punctuated.
    """
    whole = printed_pages_in(span)
    parts = [c for c in span.split(";") if c.strip()]
    if len(parts) < 2:
        return [(span, whole)]
    return [(c, printed_pages_in(c) or whole) for c in parts]


def book_named_in(text, names):
    """The bookmap key this text names, or None.

    A key matches when every word of it appears in the text, so "Cummings"
    matches `Cummings, *Proofs*` while "Cummings Real Analysis" matches only
    the clause that also says Real Analysis. The most specific match wins,
    which is what separates the two Cummings volumes and the two Aluffis.
    """
    best = None
    for name in names:
        words = name.split()
        if all(re.search(r"\b%s\b" % re.escape(w), text, re.I) for w in words):
            if best is None or len(words) > len(best.split()):
                best = name
    return best


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

    Its EXERCISES are barer still: printed as `1 Prove that -(-v) = v ...`,
    with no kind word and no heading markup at all. Once integer-only result
    numbers were parsed, every `Axler §1.B, Exercise 1, p. 17` in the `la` sets
    turned into a hard FAIL — each of them correct about the page. A plain
    numbered item at the start of a line is therefore a label too, which puts
    these back where they belong: WARN, "right about where, loose about what it
    is called", never a wrong page. (Codex review of PR #21.)
    """
    m = re.search(r"^#{1,6}\s*\**\s*%s\**\s+(.+)$" % re.escape(num), raw, re.M)
    if m:
        return re.sub(r"[*#$]", "", m.group(1)).strip()[:60]
    m = re.search(r"^\*\*%s\**\s+(.+)$" % re.escape(num), raw, re.M)
    if m:
        return re.sub(r"[*#$]", "", m.group(1)).strip()[:60]
    # A bare numbered item: the number at the start of a line, then a space,
    # then prose. Anchored and requiring a following word so that a page
    # number or a stray figure caption does not qualify.
    m = re.search(r"^\s*%s\s+([A-Za-z$\\][^\n]*)$" % re.escape(num), raw, re.M)
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
    # A SUBSTRING test approved a citation to any result whose number extends
    # the cited one: "Theorem 1.13" matched a page printing only Theorem 1.130,
    # "Exercise 2.5" matched Exercise 2.50, "Lemma 1.3.7" matched Lemma 1.3.70.
    # A false PASS in the worst place — the sibling result is exactly what a
    # mistyped citation lands on. The number must end where the citation ends,
    # so nothing that continues it as a digit or a further dotted level counts.
    # (Codex review of PR #21.)
    for n in {num, stem}:
        pat = r"(?:%s\s+%s|%s\s+%s)(?!\d)(?!\.\d)" % (
            re.escape(k), re.escape(n), re.escape(n), re.escape(k))
        if re.search(pat, hay):
            return "exact"
    if raw is not None:
        for n in {num, stem}:
            if book_label_for(n, raw) is not None:
                return "number-only"
    return None


def split_at_books(text, names):
    """[(part, book_or_None)] — text cut at every point a book is named.

    The first part carries None (it belongs to whatever was current), and each
    later part carries the book whose name begins it. A name is only a cut
    point if it starts a part: `see also Abbott` mid-sentence cuts there too,
    which is the conservative reading — a citation after a book's name is
    about that book.
    """
    hits = []
    for name in names:
        words = name.split()
        for m in re.finditer(r"\b%s\b" % re.escape(words[0]), text, re.I):
            if all(re.search(r"\b%s\b" % re.escape(w), text[m.start():], re.I)
                   for w in words[1:]):
                hits.append((m.start(), len(words), name))
    if not hits:
        return [(text, None)]
    # At one position, the most specific name wins ("Cummings Real Analysis"
    # over "Cummings"); positions are then taken in order.
    best = {}
    for pos, spec, name in hits:
        if pos not in best or spec > best[pos][0]:
            best[pos] = (spec, name)
    cuts = sorted(best)
    out = []
    if cuts[0] > 0:
        out.append((text[:cuts[0]], None))
    for i, pos in enumerate(cuts):
        end = cuts[i + 1] if i + 1 < len(cuts) else len(text)
        out.append((text[pos:end], best[pos][1]))
    return out


def attribute(text, primary, names):
    """Assertions with the book each one is actually about.

    A Sources line that names two books had EVERY citation in it checked
    against the unit's primary book. tda1-01 cites six Oudot results and was
    told all six were missing from Edelsbrunner — six loud failures, none of
    them about the citation. Across the corpus that mechanism produced most of
    the failing rows, so the gate's own verdict could not be read.

    Attribution is sticky and left-to-right, and it splits at each book NAME
    rather than only at clause boundaries: everything from one book's name up
    to the next book's name is about that book, and text before any name
    continues the last one named — which is how these Sources blocks are
    actually written (`Oudot, ... — Chapter 2 ... (p. 29); Definition 2.1 of a
    filtration ...`). Nothing named yet means the unit's primary book.

    Splitting on the name and not on the clause matters because authors
    separate two books with a full stop, not a semicolon, and a full stop
    cannot be used as a separator here — `p. 39` and `§2.2` both contain one.
    pw-04's own footer named Abbott first and Cummings Real Analysis second in
    one clause; the most-specific-match rule then attributed Abbott's two
    citations to Cummings and failed both.
    """
    out = []
    for whole_span, line in spans(text):
        current = primary
        for span, pages in clauses(whole_span):
            for part, named in split_at_books(span, names):
                if named is not None:
                    current = named
                out.append((part, printed_pages_in(part) or pages, line, current))
    return out


def check_file(path, book, verbose=False, books=None, all_names=None):
    """Returns (failures, checked, unavailable). Prints a row per failure.

    `unavailable` is the set of books a clause was actually about and that are
    not on this machine. Those citations are NOT counted wrong: the gate could
    not look, and this script's whole exit-code contract is that a check which
    did not run must not look like a check that failed.
    """
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        # Exit 2, not 1. An unreadable input is an absence of analysis, and
        # letting OSError escape gave a traceback and process exit 1 — the code
        # reserved for "a citation was compared and was wrong".
        # (Codex review of PR #21.)
        raise Unreadable("%s: %s" % (path, e)) from e
    failures, warnings, checked = [], [], 0
    books = books if books is not None else {book.name: book}
    unavailable = set()
    # Attribution is offered EVERY bookmap name, not only the ones whose page
    # trees are here. Passing `sorted(books)` meant a clause naming a book we
    # do not hold could not be recognised as being about that book at all: it
    # stayed attributed to the primary and its citations were reported wrong,
    # which is the one verdict the docstring promises never to give for a check
    # that could not run. (Codex review of PR #21.)
    for span, pages, line, name in attribute(text, book.name,
                                             all_names or sorted(books)):
        results = results_in(span)
        if not pages or not results:
            continue
        if name not in books:
            unavailable.add(name)
            continue
        book = books[name]
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
                    "line %d: %s is not on %s printed p. %s (PDF %s)"
                    % (line, r, book.name, ",".join(str(p) for p in sorted(pages)),
                       ",".join(str(n) for n in pdf_pages)))
            elif status == "number-only":
                num = r.partition(" ")[2]
                warnings.append(
                    "line %d: %s is on printed p. %s, but the book heads it %r"
                    % (line, r, ",".join(str(p) for p in sorted(pages)),
                       book_label_for(re.sub(r"[a-z]$", "", num), raw)))
            elif verbose:
                print("  ok  %s on %s printed p. %s"
                      % (r, book.name, ",".join(str(p) for p in sorted(pages))))
    for w in warnings:
        print("WARN %s" % w)
    for f_ in failures:
        print("FAIL %s" % f_)
    for name in sorted(unavailable):
        print("NOVERDICT citations attributed to %s were not checked: its page"
              " tree is not on this machine" % name)
    return failures, checked, unavailable


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
              == ["Definition 2.2", "Proposition 2.4", "Proposition 2.6"])
    # These two controls used to assert the OPPOSITE — that a plural citation
    # yields nothing — on the reasoning that a known limit pinned by a control
    # cannot regress into a false PASS. It cannot; but pinning it also made it
    # permanent, and the limit was quietly excusing 190 citations across the
    # corpus. A control over a gap keeps the gap honest, not acceptable.
    check_one("a plural citation expands to one id per number",
              results_in("Propositions 2.4, 2.6")
              == ["Proposition 2.4", "Proposition 2.6"])
    check_one("a range expands to its ENDS only, never its interior",
              results_in("Exercises 6.6-6.9") == ["Exercise 6.6", "Exercise 6.9"])
    check_one("'and' joins a plural citation too",
              results_in("Theorems 1.1 and 1.2") == ["Theorem 1.1", "Theorem 1.2"])
    check_one("a singular keyword is unaffected",
              results_in("Theorem 1.1 and Theorem 1.2")
              == ["Theorem 1.1", "Theorem 1.2"])
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

    # -- one assertion per verdict, and spans that contain parentheses -------
    sources = ("§4.1-4.2 (Proposition 4.2), pp. 107-115; "
               "§4.3 (Theorem 4.8), pp. 124-133; "
               "§4 Exercises (Exercise 4.1), pp. 148-149")
    by_clause = {r: pages for text, pages in clauses(sources)
                 for r in results_in(text)}
    check_one("a Sources line is split into one assertion per clause",
              by_clause["Theorem 4.8"] == set(range(124, 134))
              and by_clause["Exercise 4.1"] == {148, 149})
    check_one("...so no result inherits the whole line's pages",
              by_clause["Proposition 4.2"] == set(range(107, 116)))
    check_one("a clause with no page of its own falls back to the span",
              clauses("Theorem 7.6; proved there, pp. 225-226")[0][1] == {225, 226})
    check_one("an unpunctuated span is still one assertion, as before",
              [p for _, p in clauses("Cummings §4.3, Theorem 4.8, pp. 125-127")]
              == [{125, 126, 127}])
    check_one("a parenthetical span survives a parenthesised exercise part",
              spans("*(Cummings, Exercise 8.28(d), p. 280)*")
              and results_in(spans("*(Cummings, Exercise 8.28(d), p. 280)*")[0][0])
              == ["Exercise 8.28"])
    check_one("...and its page reference is still read",
              printed_pages_in(spans("*(Cummings, Exercise 8.28(d), p. 280)*")[0][0])
              == {280})

    # -- Codex review of PR #21 --------------------------------------------
    check_one("a cited number does not match a longer sibling",
              found_on_page("Theorem 1.13", "theorem 1.130 statement") is None
              and found_on_page("Exercise 2.5", "exercise 2.50 do this") is None
              and found_on_page("Lemma 1.3.7", "lemma 1.3.70 x") is None)
    check_one("...while the number itself still matches",
              found_on_page("Theorem 1.13", "theorem 1.13 statement") == "exact")
    check_one("a trailing sentence period is not a further level",
              found_on_page("Exercise 2.5a", "exercise 2.5. with parts") == "exact")
    check_one("an integer-only result number is parsed",
              results_in("Axler Exercise 10, p. 24") == ["Exercise 10"])
    check_one("...and does not match a longer integer",
              found_on_page("Exercise 10", "exercise 100 blah") is None
              and found_on_page("Exercise 10", "exercise 10. blah") == "exact")
    check_one("a dotted number is still captured whole, never as its first part",
              results_in("Theorem 6.11.") == ["Theorem 6.11"])
    check_one("an integer-only plural expands too",
              results_in("Exercises 1, 2") == ["Exercise 1", "Exercise 2"])
    check_one("the repo's own 'printed NNN' page form is read",
              printed_pages_in("Theorem 13.1, printed 394") == {394})
    check_one("...including its emphasised range form",
              printed_pages_in("printed **268-274**") == set(range(268, 275)))
    check_one("...and 'p.' still works",
              printed_pages_in("pp. 41-42") == {41, 42})

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

    # Every book on this machine is available for attribution, not only the
    # unit's primary one: a Sources block that switches books mid-line is the
    # normal case, not the exception. A book whose page tree is absent is
    # skipped here and reported by name when a clause actually needs it.
    books, absent = {}, []
    for name in sorted(load_bookmap()):
        try:
            books[name] = Book(name)
        except RuntimeError:
            absent.append(name)
    if book_name not in books:
        print("ERROR pages tree for %r is not on this machine" % book_name)
        print("This gate needs the per-page markdown tree and cannot run here.")
        return 2
    book = books[book_name]
    if absent:
        print("NOTE %d book(s) have no page tree here and cannot be checked "
              "against: %s" % (len(absent), ", ".join(absent)))

    all_names = sorted(load_bookmap())
    rc, total, blocked = 0, 0, False
    for p in paths:
        print("=== %s  (primary %s)" % (p, book.name))
        try:
            failures, checked, unavailable = check_file(
                p, book, a.verbose, books, all_names)
        except Unreadable as e:
            # Exit 2, never 1: an input that could not be read is an absence of
            # analysis, and this script promises those never look alike.
            print("ERROR could not read %s" % e)
            blocked = True
            continue
        total += checked
        if failures:
            rc = 1
        if unavailable:
            blocked = True
        print("%s %d citation(s) checked, %d wrong%s"
              % ("FAIL" if failures else "PASS", checked, len(failures),
                 "" if not unavailable else
                 "; %d book(s) unavailable, so some citations got no verdict"
                 % len(unavailable)))
    # A real wrong citation outranks a check that could not run: exit 1 says
    # "something is wrong", exit 2 says "I could not tell", and 1 is the more
    # actionable of the two when both are true.
    return rc or (2 if blocked else 0)


if __name__ == "__main__":
    sys.exit(main())
