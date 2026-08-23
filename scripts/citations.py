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
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.pull import (all_pages, fit_offsets, folio_candidates,  # noqa: E402
                          load_bookmap, page_text, pages_dir, suspect_plateaus)

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KINDS = ("Theorem", "Lemma", "Proposition", "Definition", "Corollary",
         "Example", "Exercise", "Fact", "Axiom", "Remark", "Principle",
         # Axler heads several numbered items "Notation": Notation 3.3 names
         # L(V, W), Notation 3.39 names F^{m,n}, Notation 3.44 names the rows
         # and columns of a matrix. Each is a numbered result on a specific
         # page and the la lessons cite them as such. Without the kind word
         # here the citation produced no id at all, so the folio was never
         # checked and the denominator never moved -- the absence looked
         # exactly like a file with nothing to check.
         "Notation")
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
#
# The first component may be an APPENDIX LETTER. Hatcher numbers its appendix
# results A.1, A.17, and requiring a leading digit meant those citations
# produced no id at all, so a wrong page for one could not affect the verdict.
# The letter form must be dotted — a bare "A" is not a result number, it is a
# word — and it is upper case, which keeps it clear of the trailing item letter
# in "2.5a". (Codex review of PR #21.)
NUM = r"\d+(?:\.\d+)+[a-z]?|[A-Z](?:\.\d+)+[a-z]?|\d+[a-z]?"
RESULT = re.compile(r"\b(%s)\s+(%s)(?!\d)(?!\.\d)" % ("|".join(KINDS), NUM))
# The plural/range form: "Exercises 6.6-6.9", "Theorems 1.1 and 1.2",
# "Definitions 8.3, 8.5". See results_in().
NUMBER = re.compile(r"(?:%s)(?!\d)(?!\.\d)" % NUM)
PLURALS = {"Theorem": "Theorems", "Lemma": "Lemmas", "Proposition": "Propositions",
           "Definition": "Definitions", "Corollary": "Corollaries",
           "Example": "Examples", "Exercise": "Exercises", "Fact": "Facts",
           "Axiom": "Axioms", "Remark": "Remarks",
           # Cummings states induction and strong induction as PRINCIPLES, and
           # pw-02 cites Principle 4.1 and Principle 4.7. Omitting the kind
           # meant both citations were skipped without touching the
           # denominator. (CodeRabbit review of PR #21.)
           "Principle": "Principles", "Notation": "Notations"}
SINGULAR = {p.lower(): s for s, p in PLURALS.items()}
# A member of a plural list may carry a PART: `Exercises 8(a) and 8(b)`. The
# part interrupted the separator pattern, so the whole list matched nothing and
# both exercises left the denominator — top-02 cites exactly that. The part is
# matched here and dropped when the ids are built, since found_on_page already
# strips a trailing item marker. (Codex review of PR #21.)
_PART = r"(?:\s*\([a-z]\))?"
_PNUM = NUMBER.pattern + _PART
PLURAL = re.compile(
    r"\b(%s)\s+(%s(?:\s*(?:[-–—,/]|and|to)\s*%s)+)"
    % ("|".join(PLURALS.values()), _PNUM, _PNUM))
# "p. 225", "pp. 41-42", "pp. 220–221" (hyphen or en dash) — and this repo's own
# "printed 394" / "printed **268–274**" form, which is what the lab and an2
# source blocks use. Accepting only `p.` left 1084 occurrences of `printed NNN`
# unparsed, so those spans produced results and no pages and check_file skipped
# them entirely: the largest silent-absence hole this gate has had. The
# emphasis markers are stripped from spans before matching, so the `**` form
# arrives here bare.
#
# One keyword can also head a LIST: `pp. 326 and 328`, `pp. 262, 265`. Reading
# only the first meant the other pages were never searched, so a result printed
# on the second was reported wrong. The list is matched whole and then split;
# a dash between two of its members is still a range.
_PGNUM = r"[*_]*\s*\d+\s*[*_]*"
PAGES = re.compile(
    r"(?:\bpp?\.|\bprinted)\s*(%s(?:\s*(?:[-–—,]|and)\s*%s)*)" % (_PGNUM, _PGNUM),
    re.I)
_PGRANGE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)")

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
    # The plain parenthetical, without the markdown emphasis. Lessons write
    # `Definition 6.4.1 (Abbott, printed 167)` inline — 955 of them across the
    # corpus — and none was a span. The result was found later in the footer
    # instead, so changing the LOCAL page to any value at all could not affect
    # the verdict: the citation nearest the mathematics was the one nothing
    # checked. (Codex review of PR #21.)
    # The span reaches BACK over the text just before the bracket, because that
    # is where the result id sits: `Definition 6.4.1 (Abbott, printed 167)`
    # puts the number outside the parenthesis and the page inside, and a span
    # holding only the bracket has a page and nothing to check against it.
    re.compile(r"([^<>()\n]{0,90}\((?:[^()]|\([^()]*\))*?"
               r"(?:\bpp?\.|\bprinted)\s*\d+(?:[^()]|\([^()]*\))*?\))", re.S),
)


class Unreadable(Exception):
    """An input this gate was asked to read could not be read. Verdict 2."""


def strip_tags(text):
    return re.sub(r"<[^>]+>", " ", text)


def spans(text):
    """Citation spans, as (span_text, line_number)."""
    out, seen = [], set()
    for pat in SPAN_PATTERNS:
        for m in pat.finditer(text):
            body = strip_tags(m.group(1))
            line = text[:m.start()].count("\n") + 1
            # The markdown and plain parenthetical patterns overlap on the
            # `*(...)*` form in the problem sets. The same assertion twice is
            # harmless to the verdict but doubles the denominator, so dedupe on
            # what was said and where.
            key = (line, " ".join(body.split()).strip("*()  ").strip())
            if key in seen:
                continue
            seen.add(key)
            out.append((body, line))
    return out


def printed_pages_in(span):
    pages = set()
    for m in PAGES.finditer(span):
        rest = re.sub(r"[*_]", "", m.group(1))
        # Walk the list left to right so a dashed pair is consumed as a RANGE
        # and every other number counts on its own. Adding all the numbers
        # unconditionally would resurrect the absurd-range case: `pp. 12-9000`
        # must yield {12}, not {12, 9000}.
        prev, pos = None, 0
        for tok in re.finditer(r"\d+", rest):
            n = int(tok.group(0))
            joiner = rest[pos:tok.start()]
            if prev is not None and re.fullmatch(r"\s*[-–—]\s*", joiner):
                if n >= prev and n - prev <= 60:   # else malformed or absurd
                    pages.update(range(prev, n + 1))
            else:
                pages.add(n)
            prev, pos = n, tok.end()
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

    A RANGE is expanded; a LIST is not. `Exercises 1.3.1-1.3.9` cites all nine,
    which is what a range means, and taking only its ends left the seven
    interior ones out of the denominator so a wrong page for any of them could
    not affect the verdict — an-01's source block is written that way. But
    `Definitions 8.3, 8.5` cites exactly two, and inventing 8.4 would hold the
    author to a citation never made. The separator decides: a dash or "to"
    expands, a comma or "and" does not.

    An earlier version of this docstring stated the ends-only rule as a
    principle. It was right about lists and wrong about ranges, and the
    justification — "inferring the interior invents citations" — is true only
    when the interior was not cited. (Codex review of PR #21.)
    """
    ids = {"%s %s" % (m.group(1), m.group(2)) for m in RESULT.finditer(span)}
    for kinds, numbers in PLURAL.findall(span):
        kind = SINGULAR[kinds.lower()]
        ids.update("%s %s" % (kind, n) for n in expand_members(numbers))
    return sorted(ids)


_RANGE_SEP = re.compile(r"\s*(?:[-–—]|to)\s*")
_MEMBER = re.compile(r"(%s)%s" % (NUMBER.pattern, _PART))


def expand_members(numbers):
    """The result numbers a plural list denotes, ranges expanded.

    Only a dash- or `to`-joined pair of COMMENSURABLE numbers expands: same
    leading components, numeric final component, ascending, and no more than
    MAX_RANGE members. Anything else contributes its written members only, so
    a malformed or absurd range degrades to the two numbers actually there
    rather than to hundreds of invented ones.
    """
    MAX_RANGE = 40
    out, tokens = set(), []
    pos = 0
    for m in _MEMBER.finditer(numbers):
        tokens.append((numbers[pos:m.start()], m.group(1)))
        pos = m.end()
    prev = None
    for joiner, n in tokens:
        out.add(n)
        if prev is not None and _RANGE_SEP.fullmatch(joiner or ""):
            out.update(_between(prev, n, MAX_RANGE))
        prev = n
    return sorted(out)


def _between(a, b, cap):
    """The numbers strictly between two commensurable result numbers."""
    pa, pb = a.split("."), b.split(".")
    if len(pa) != len(pb) or pa[:-1] != pb[:-1]:
        return []
    if not (pa[-1].isdigit() and pb[-1].isdigit()):
        return []
    lo, hi = int(pa[-1]), int(pb[-1])
    if hi <= lo or hi - lo > cap:
        return []
    head = pa[:-1]
    return [".".join(head + [str(i)]) for i in range(lo + 1, hi)]


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
    parts = [c for c in _split_assertions(span) if c.strip()]
    if len(parts) < 2:
        return [(span, whole)]
    return [(c, printed_pages_in(c) or whole) for c in parts]


# Abbreviations whose full stop is not a sentence end. `p.` and `pp.` are the
# ones that matter — a source block is made of them — and the rest are here so
# the rule does not have to be rediscovered per book.
_ABBREV = {"p", "pp", "ch", "chap", "ed", "eds", "vol", "no", "nos", "cf",
           "eq", "eqn", "fig", "sec", "art", "trans", "repr", "i.e", "e.g"}
_SENTENCE = re.compile(r"(?<=[a-z0-9)\]’\"])\.\s+(?=[A-Z§])")


def _split_assertions(span):
    """A span's assertions: semicolon-separated, and sentence-separated.

    Splitting on ';' alone still unioned unrelated page claims wherever a
    Sources block is written as sentences — an2-06's footer cites Theorem 6.5.1
    on printed 170 in a sentence whose pages then merged with 166-174 and
    181-182, so a wrong local page could pass because the theorem occurs
    somewhere in the accumulated set. (Codex review of PR #21.)

    A full stop only ends an assertion when it is not part of an abbreviation
    or a result number: `p. 46`, `pp. 41-42`, `§2.2` and `Lemma 1.3.7` all
    contain one and none of them ends anything. The lookbehind requires a
    letter or a closing bracket, and the word before the stop must not be a
    known abbreviation.
    """
    out, start = [], 0
    for m in _SENTENCE.finditer(span):
        word = re.search(r"([A-Za-z.]+)$", span[:m.start()])
        if word and word.group(1).rstrip(".").lower() in _ABBREV:
            continue
        out.append(span[start:m.start()])
        start = m.end()
    out.append(span[start:])
    return [c for part in out for c in part.split(";")]


def deaccent(text):
    """Strip combining marks so a displayed name matches its bookmap key.

    The corpus writes Lindström with the umlaut — 275 times across the nine
    an2 files — while the bookmap key is ASCII "Lindstrom". A literal match saw
    none of them, so every an2 clause that DID name its book was attributed to
    the unit's other source and its citations were reported wrong. I had put
    those failures down to spans that omit the book name; the spans name it,
    and the matcher could not read it. (Codex review of PR #21.)

    Length-preserving, one character in for one character out, because
    split_at_books slices the ORIGINAL text at the match offsets: dropping a
    combining mark outright would shift every position after it.
    """
    out = []
    for c in text:
        d = unicodedata.normalize("NFKD", c)
        out.append(d[0] if d and not unicodedata.combining(d[0]) else c)
    return "".join(out)


def name_pattern(name):
    """A regex matching a bookmap key as a CONSECUTIVE phrase.

    The words must appear in order and adjacent, with only punctuation,
    whitespace or markdown emphasis allowed between them — so `Cummings, *Real
    Analysis*` matches "Cummings Real Analysis" and `Cummings, *Proofs* … later
    … Real Analysis` does not.

    Testing the words INDEPENDENTLY was the defect: a Sources block naming
    Cummings's Proofs first and his Real Analysis later made the first
    "Cummings" satisfy the three-word key, because "Real" and "Analysis"
    appeared somewhere after it. The most-specific-match rule then attributed
    the Proofs citations to Real Analysis. (CodeRabbit review of PR #21.)
    """
    gap = r"[\s,:;*_\-–—'\"()]*"
    return re.compile(
        r"\b" + gap.join(re.escape(w) for w in deaccent(name).split()) + r"\b",
        re.I)


def display_forms(name, title):
    """The phrases that name this book: its key, and its author-plus-title.

    Authors write the displayed title, not the bookmap key: cat-05's block says
    `Aluffi, *Algebra: Chapter 0*`, and the key "Aluffi Chapter 0" does not
    match it because "Algebra" sits between the two words. The Aluffi
    citations there were therefore left attributed to Spivak, the unit's
    primary book, and reported wrong. (Codex review of PR #21.)

    The alias is the author's surname followed by the title as printed, up to
    the first comma — enough to keep `Algebra: Chapter 0` apart from `Algebra:
    Notes from the Underground`, and short enough not to depend on edition
    text. Both forms still have to appear as consecutive phrases, so this does
    not reopen the scattered-words defect: only the vocabulary widens.
    """
    forms = [name]
    m = re.match(r"^(.*?)\s*\(([^)]*)\)", title or "")
    if m:
        lead = re.split(r",", m.group(1))[0].strip()
        surname = re.split(r"[,&]| and ", m.group(2))[0].strip().split()
        if lead and surname:
            alias = "%s %s" % (surname[-1], lead)
            if alias.lower() != name.lower():
                forms.append(alias)
    return forms


def name_patterns(name, title=None):
    """Every pattern that names this book. See display_forms()."""
    return [name_pattern(f) for f in display_forms(name, title)]


def book_named_in(text, names, titles=None):
    """The bookmap key this text names, or None.

    "Cummings" matches `Cummings, *Proofs*`; "Cummings Real Analysis" matches
    only text that says both, adjacently. The most specific match wins, which
    is what separates the two Cummings volumes and the two Aluffis.
    """
    best = None
    flat = deaccent(text)
    titles = titles or {}
    for name in names:
        if any(p.search(flat) for p in name_patterns(name, titles.get(name))):
            if best is None or len(name.split()) > len(best.split()):
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
        # A lone disagreeing page is usually a chapter number or an index
        # reference — but "usually" is the whole difficulty, and dropping EVERY
        # single-page plateau also drops a genuine one-page pagination run, so
        # a citation to a folio inside it cannot be mapped and is reported as
        # a page that is not in the book.
        #
        # pull.suspect_plateaus is the rule that distinguishes them, and its
        # own docstring records that the blanket version "silently discarded a
        # real boundary". This reimplemented the discarded rule rather than
        # calling the one next door. Only INTERIOR singletons bracketed by the
        # same offset on both sides are strays. (Codex review of PR #21.)
        suspect = suspect_plateaus(plateaus)
        self.plateaus = [p for p in plateaus if p not in suspect]
        # A tree that exists but yields no usable plateau — empty directory, or
        # no page in it carrying a detectable folio — cannot map any printed
        # page. Constructing a Book from it made the book look AVAILABLE, and
        # every citation attributed to it then came back "printed page(s) are
        # not in <book>" with exit 1: a wrong-citation verdict for a comparison
        # that never ran. An unusable tree is an absent tree.
        # (Codex review of PR #21.)
        if not self.plateaus:
            raise RuntimeError(
                "pages tree for %r has no usable folio map (%d page(s) read, "
                "no pagination plateau): %s"
                % (name, len(pages), self.dir))

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
    # A bare numbered item: the number at the start of a line, an optional
    # "." or ")", then prose. Anchored and requiring a following word so that a
    # page number or a stray figure caption does not qualify. Axler writes
    # "1 Prove that ..." and Lindström writes "1. Let f, g ..." — one
    # punctuation mark apart, and omitting it turned every Lindström exercise
    # citation in the an2 sets into a hard FAIL.
    #
    # An exercise whose first part is lettered opens with the item marker
    # rather than a word — Axler's 2.A.5 is printed "5 (a) Show that if we
    # think of C as a vector space over R ...". Demanding a letter immediately
    # after the number reported that citation as a wrong page while it named
    # the right one. The marker is admitted, but only in bracketed item form
    # and still followed by prose, so a displayed formula opening "5 (x + y)"
    # is not promoted to a header.
    #
    # The converter sometimes reads an exercise block as a markdown ordered
    # list and emits its own marker in front of the book's number, so Axler's
    # exercise 1 on printed 88 arrives as "1. 1 Suppose T in L(U, V)". The
    # number then sits where the guard demanded a word, the exercise had no
    # label, and a citation naming its correct page was reported wrong.
    #
    # The marker need not agree with the book's number. On printed 189 the
    # converter counted part (b) of exercise 1 as an item of its own, so every
    # later marker is one ahead: exercise 3 arrives as "4. 3 Suppose T in
    # L(R^3)". Requiring the marker to repeat the number therefore still
    # reported a correct citation as wrong.
    #
    # Any leading integer marker is admitted, because the number being looked
    # for is anchored AFTER it and so can never be confused with it. That is
    # what keeps the relaxation safe: on the same page, "3. 2 Suppose e_1" is
    # exercise 2, and a citation of exercise 3 matches neither branch — not
    # the marker branch, where the number after the marker is 2, nor the
    # bare branch, where a digit sits where prose is required.
    m = re.search(
        r"^\s*(?:\d{1,3}[.)]\s+)?%s[.)]?\s+"
        r"(?:\((?:[a-z]|[ivx]{1,4}|\d{1,2})\)\s*)?"
        r"([A-Za-z$\\][^\n]*)$" % re.escape(num), raw, re.M)
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
    # Boundaries on BOTH sides. The trailing guard alone still let a citation
    # match a longer number that ENDS with it: "Definition 1.3" was found in
    # "11.3 definition", and "Exercise 10" in "110 exercise". That is the same
    # sibling-result false PASS from the other end, and it bites hardest in
    # Axler's number-first format. (Codex review of PR #21.)
    for n in {num.lower(), stem.lower()}:
        # `hay` is lower-cased, so the number must be too — Hatcher's appendix
        # numbers carry a capital ("A.17") and matching them raw found nothing.
        pat = r"(?:%s\s+(?<![\d.])%s|(?<![\d.])%s\s+%s)(?!\d)(?!\.\d)" % (
            re.escape(k), re.escape(n), re.escape(n), re.escape(k))
        if re.search(pat, hay):
            return "exact"
    if raw is not None:
        for n in {num, stem}:
            if book_label_for(n, raw) is not None:
                return "number-only"
    return None


def split_at_books(text, names, titles=None):
    """[(part, book_or_None)] — text cut at every point a book is named.

    The first part carries None (it belongs to whatever was current), and each
    later part carries the book whose name begins it. A name is only a cut
    point if it starts a part: `see also Abbott` mid-sentence cuts there too,
    which is the conservative reading — a citation after a book's name is
    about that book.
    """
    # The name must appear as a CONSECUTIVE phrase, not as its words scattered
    # anywhere after the first: matching them independently let a span that
    # names Cummings's Proofs and later his Real Analysis cut at the FIRST
    # "Cummings" as though it were the three-word key, sending the Proofs
    # citations to the wrong volume. (CodeRabbit review of PR #21.)
    hits = []
    flat = deaccent(text)          # same length as text, so offsets carry over
    titles = titles or {}
    for name in names:
        for pat in name_patterns(name, titles.get(name)):
            for m in pat.finditer(flat):
                hits.append((m.start(), len(name.split()), name))
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


def attribute(text, primary, names, titles=None):
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
            for part, named in split_at_books(span, names, titles):
                if named is not None:
                    current = named
                out.append((part, printed_pages_in(part) or pages, line, current))
    return out


def check_file(path, book, verbose=False, books=None, all_names=None,
               titles=None):
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
                                             all_names or sorted(books),
                                             titles):
        results = results_in(span)
        if not pages or not results:
            continue
        if name not in books:
            unavailable.add(name)
            continue
        book = books[name]
        pdf_pages = sorted({n for p in pages for n in book.pdf_pages_for(p)})
        if not pdf_pages:
            # One failure PER RESULT, and each one counted. Recording a single
            # failure and skipping the increment produced output that
            # contradicted itself — "0 citation(s) checked, 1 wrong" — and
            # understated how many citations the bad folio affected. This is a
            # real wrong-page verdict, so it belongs in both numbers.
            # (Codex review of PR #21.)
            for r in results:
                checked += 1
                failures.append(
                    "line %d: %s cites printed p. %s, which is not in %s"
                    % (line, r, ",".join(str(p) for p in sorted(pages)),
                       book.name))
            continue
        # Each candidate page is searched SEPARATELY. Joining them first let a
        # match be assembled across a page boundary: one page ending "Theorem"
        # and the next beginning "7.6" collapsed — the newline becoming a space
        # under normalisation — into a "Theorem 7.6" that neither page carries.
        # (Codex review of PR #21.)
        texts = [(n, book.text_of(n)) for n in pdf_pages]
        missing = [n for n, t in texts if t is None]
        present = [(n, t) for n, t in texts if t is not None]
        if not present:
            unavailable.add(book.name)
            continue
        for r in results:
            checked += 1
            status, hit_raw = None, None
            for _n, t in present:
                st = found_on_page(r, normalise_for_search(t), t)
                if st == "exact":
                    status, hit_raw = st, t
                    break
                if st == "number-only" and status is None:
                    status, hit_raw = st, t
            if status is None and missing:
                # A cited page could not be read, so "not found" is not a
                # verdict about this citation.
                checked -= 1
                unavailable.add(book.name)
            elif status is None:
                failures.append(
                    "line %d: %s is not on %s printed p. %s (PDF %s)"
                    % (line, r, book.name, ",".join(str(p) for p in sorted(pages)),
                       ",".join(str(n) for n in pdf_pages)))
            elif status == "number-only":
                num = r.partition(" ")[2]
                warnings.append(
                    "line %d: %s is on printed p. %s, but the book heads it %r"
                    % (line, r, ",".join(str(p) for p in sorted(pages)),
                       book_label_for(re.sub(r"[a-z]$", "", num), hit_raw)))
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


def unit_paths(uid):
    """Both halves of a unit, present or not.

    Filtering these through exists() meant a unit whose lesson had never been
    written reported the verdict of its problem set alone and looked fully
    checked — exactly the state --unit is supposed to expose. A missing half
    now reaches the unreadable-input path and returns 2.
    (Codex review of PR #21.)
    """
    mod = uid.rsplit("-", 1)[0]
    return [os.path.join(REPO, "problems", "sets", uid + ".md"),
            os.path.join(REPO, "lessons", mod, uid + ".html")]


def book_for_unit(uid):
    """The unit's primary book, from the syllabus resource line.

    An unreadable or malformed syllabus is Unreadable, not a traceback: the
    same exit-code contract as every other input this gate depends on. Found by
    sweeping for the class after the third instance of it was reported.
    """
    import yaml
    path = os.path.join(REPO, "curriculum", "syllabus.yaml")
    try:
        with open(path, encoding="utf-8") as f:
            syl = yaml.safe_load(f)
        # The lookup and the resource walk are INSIDE the guard. A previous
        # version guarded only the read, so a unit record that is not a mapping,
        # or one without an id, raised out of the function and exited 1 — the
        # status reserved for a checked, wrong citation. Guarding the open() and
        # not the parse is guarding the easy half. (Codex review of PR #21.)
        unit = next((u for u in syl["units"] if u["id"] == uid), None)
        if unit is None:
            return None
        resources = unit.get("resources", [])
    except (OSError, yaml.YAMLError, KeyError, TypeError, AttributeError) as e:
        raise Unreadable("%s: %s" % (path, e)) from e
    bm = load_bookmap()
    for res in resources:
        for name in sorted(bm, key=len, reverse=True):
            if res.lower().startswith(name.lower()):
                return name
    return None


ALUFFI = ["Aluffi Chapter 0", "Aluffi Underground", "Spivak"]
ALUFFI_TITLES = {"Aluffi Chapter 0": "Algebra: Chapter 0 (Aluffi)",
                 "Aluffi Underground": "Algebra: Notes from the Underground (Aluffi)",
                 "Spivak": "Seven Sketches in Compositionality (Fong, Spivak)"}


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
    check_one("a RANGE expands to every member it denotes",
              results_in("Exercises 6.6-6.9")
              == ["Exercise 6.%d" % i for i in range(6, 10)])
    check_one("...while a LIST contributes only what is written",
              results_in("Definitions 8.3, 8.5")
              == ["Definition 8.3", "Definition 8.5"])
    check_one("an absurd or incommensurable range degrades to its ends",
              results_in("Theorems 1.1-99.9") == ["Theorem 1.1", "Theorem 99.9"]
              and results_in("Lemmas 1.2-3.4.5")
              == ["Lemma 1.2", "Lemma 3.4.5"])
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

    # Axler prints a lettered exercise as "5 (a) Show that ...". The item
    # marker sits where the guard demanded a word, so the exercise had no
    # label and a correct citation to it was reported as a wrong page.
    # A markdown ordered-list marker in front of the book's own number.
    check_one("a doubled list marker does not hide the exercise",
              book_label_for("1", "1. 1 Suppose T in L(U, V) and S in L(V, W)")
              == "Suppose T in L(U, V) and S in L(V, W)")
    # On printed 189 the converter counted a part (b) as its own item, so
    # every later marker runs one ahead of the book's number.
    check_one("...and a marker one ahead of the number still finds it",
              book_label_for("3", "4. 3 Suppose T in L(R^3) has an upper")
              == "Suppose T in L(R^3) has an upper")
    check_one("...while the MARKER is never mistaken for the number",
              book_label_for("3", "3. 2 Suppose e_1 is an orthonormal list")
              is None)
    check_one("...and the marker is still required to precede prose",
              book_label_for("1", "1. 1 2 3 4") is None)

    check_one("a lettered exercise item is a header despite the (a) marker",
              book_label_for("5", "5 (a) Show that if we think of C as a vector")
              == "Show that if we think of C as a vector")
    check_one("...and the marker does not admit a displayed formula",
              book_label_for("5", "5 (x + y) = 5x + 5y for all x, y") is None)
    check_one("...nor a bare marker with no prose after it",
              book_label_for("5", "5 (a)") is None)

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

    # -- CodeRabbit review of PR #21 ---------------------------------------
    check_one("Principle is a result kind",
              results_in("Cummings §4.1, Principle 4.1, p. 108")
              == ["Principle 4.1"]
              and results_in("Principles 4.1, 4.7")
              == ["Principle 4.1", "Principle 4.7"])
    check_one("a book name matches only as a consecutive phrase",
              book_named_in("Cummings, *Proofs*, Ch. 8 — cf. Real Analysis",
                            ["Cummings", "Cummings Real Analysis"]) == "Cummings")
    check_one("...while the real phrase still matches through punctuation",
              book_named_in("Cummings, *Real Analysis*, Ch. 6",
                            ["Cummings", "Cummings Real Analysis"])
              == "Cummings Real Analysis")
    check_one("a mixed-volume span is cut at each volume, in order",
              [n for _p, n in split_at_books(
                  "Cummings, *Proofs*, p. 46. Cummings, *Real Analysis*, p. 226.",
                  ["Cummings", "Cummings Real Analysis"])]
              == ["Cummings", "Cummings Real Analysis"])
    check_one("the number-first word order rejects a longer sibling too",
              found_on_page("Definition 1.3", "1.3.7 definition of x") is None
              and found_on_page("Definition 1.8", "1.8 definition subspace")
              == "exact")
    check_one("a non-contiguous page list names every page in it",
              printed_pages_in("pp. 326 and 328") == {326, 328}
              and printed_pages_in("pp. 262, 265") == {262, 265})
    check_one("...and a dash inside such a list is still a range",
              printed_pages_in("pp. 41-42") == {41, 42}
              and printed_pages_in("pp. 10-12, 20") == {10, 11, 12, 20})
    check_one("an appendix-lettered result number is parsed and matched",
              results_in("Hatcher, Proposition A.17, p. 520") == ["Proposition A.17"]
              and found_on_page("Proposition A.17", "proposition a.17 states")
              == "exact")
    check_one("...and its siblings are still rejected, and a bare letter is not a number",
              found_on_page("Proposition A.1", "proposition a.17 states") is None
              and results_in("Theorem A states that") == [])
    check_one("a leading digit is a boundary too",
              found_on_page("Definition 1.3", "11.3 definition unrelated") is None
              and found_on_page("Exercise 10", "110 exercise unrelated") is None
              and found_on_page("Definition 1.3", "1.3 definition of x") == "exact")
    check_one("a plain HTML parenthetical is a span, with its result",
              [(results_in(b), sorted(printed_pages_in(b))) for b, _l in
               spans("<strong>Definition 6.4.1 (Abbott, printed 167).</strong>")]
              == [(["Definition 6.4.1"], [167])])
    check_one("...and the markdown form is not counted twice",
              len(spans("*(Cummings, Exercise 8.28(d), p. 280)*")) == 1)
    check_one("a sentence ends an assertion; an abbreviation does not",
              [sorted(pg) for _c, pg in clauses(
                  "Abbott, printed 167-168. Lindstrom, printed 92.")]
              == [[167, 168], [92]]
              and [sorted(pg) for _c, pg in clauses(
                  "Cummings 2nd ed. §4.3, Theorem 4.8, pp. 125-126")]
              == [[125, 126]])
    # Axler heads L(V, W), F^{m,n} and the row/column notation as numbered
    # "Notation" items. Without the kind word the citation made no id, so the
    # page went unchecked and the denominator never moved.
    check_one("a Notation citation produces an id like any other result",
              results_in("Axler 3.C, Notation 3.39, p. 73") == ["Notation 3.39"])
    check_one("...and it is located on the page the book prints it on",
              found_on_page("Notation 3.39",
                            normalise_for_search("### 3.39 Notation F^{m,n}"),
                            "### 3.39 Notation F^{m,n}") == "exact")
    check_one("...and the plural form expands too",
              results_in("Notations 3.39 and 3.44, p. 76")
              == ["Notation 3.39", "Notation 3.44"])

    check_one("a plural list survives a parenthesised part",
              results_in("Exercises 8(a) and 8(b), pp. 83-84") == ["Exercise 8"])
    check_one("...and parts on distinct numbers still give distinct ids",
              results_in("Exercises 8(a) and 9(b)")
              == ["Exercise 8", "Exercise 9"])
    check_one("a displayed title names the book too",
              book_named_in("Aluffi, *Algebra: Chapter 0* — §I.5", ALUFFI,
                            ALUFFI_TITLES) == "Aluffi Chapter 0")
    check_one("...and the two Aluffi volumes stay apart under it",
              book_named_in("Aluffi, *Algebra: Notes from the Underground*",
                            ALUFFI, ALUFFI_TITLES) == "Aluffi Underground")
    check_one("...while the alias does not reopen scattered-word matching",
              book_named_in("Cummings, *Proofs*, Ch. 8 — cf. Real Analysis",
                            ["Cummings", "Cummings Real Analysis"]) == "Cummings")
    check_one("an accented display name matches its ASCII bookmap key",
              book_named_in("Lindström, Definition 3.1.1, p. 44",
                            ["Abbott", "Lindstrom"]) == "Lindstrom")
    check_one("...and de-accenting preserves offsets, so slicing still works",
              len(deaccent("Lindström")) == len("Lindström")
              and [n for _p, n in split_at_books(
                  "Abbott, p. 223; Lindström, p. 44",
                  ["Abbott", "Lindstrom"])] == ["Abbott", "Lindstrom"])
    check_one("'to' joins a plural citation, and expands it",
              results_in("Definitions 12.1 to 12.5")
              == ["Definition 12.%d" % i for i in range(1, 6)])
    check_one("'/' joins a plural citation as a LIST, not a range",
              results_in("Definitions 12.1/12.5")
              == ["Definition 12.1", "Definition 12.5"])

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
    try:
        if a.unit:
            paths.extend(unit_paths(a.unit))
            book_name = book_name or book_for_unit(a.unit)
        if not paths:
            ap.error("give paths or --unit")
        if not book_name:
            uid = os.path.splitext(os.path.basename(paths[0]))[0]
            book_name = book_for_unit(uid)
    except Unreadable as e:
        print("ERROR could not read %s" % e)
        return 2
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

    bm = load_bookmap()
    all_names = sorted(bm)
    titles = {k: v.get("title") for k, v in bm.items()}
    rc, total, blocked = 0, 0, False

    def per_path_book(path):
        """This file's own primary book, or None with the reason printed."""
        uid = os.path.splitext(os.path.basename(path))[0]
        try:
            name = book_for_unit(uid) or book_name
        except Unreadable as e:
            print("=== %s" % path)
            print("ERROR could not read %s" % e)
            return None
        if name not in books:
            print("=== %s" % path)
            print("ERROR pages tree for %r is not on this machine" % name)
            return None
        return books[name]

    for p in paths:
        # The primary book is a property of the UNIT, not of the run. It was
        # read once from paths[0] and reused for every path behind it, so a
        # run spanning two books checked the second book's folios against the
        # first book's pagination — silently, because a wrong pagination still
        # resolves to real pages and some of them still carry the result
        # named. aa-01 cites Aluffi throughout, was checked against Carter
        # because aa-00 came first on the command line, and five of its eight
        # citations PASSED. Single-book modules never exposed it. --book is
        # still an override for the whole run, since that is what it is for.
        book = per_path_book(p) if not a.book else books[book_name]
        if book is None:
            blocked = True
            continue
        print("=== %s  (primary %s)" % (p, book.name))
        try:
            failures, checked, unavailable = check_file(
                p, book, a.verbose, books, all_names, titles)
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
