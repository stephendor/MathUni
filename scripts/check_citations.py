"""Report every citation's resolution status against the book it names.

`citations.py` is a GATE: it answers "is any citation in this file wrong?" with
an exit code, and it is deliberately silent about the ones that are right. That
shape cannot answer the question Observation 2026-08-09 actually asked, which
is a corpus question: *how many* of our citations were ever compared to a page
at all, and what does the residue look like. tda2-10 shipped with page numbers
that resolved under no convention because nothing read the source; the fix for
that class is not another pass/fail row but a sweep whose denominator is
visible.

So this is a REPORTER, not a gate. Every citation gets exactly one status and
the run exits 0 whatever they are (`--strict` opts into the gate contract, for
when the corpus is clean enough to hold the line):

  RESOLVED           the named page carries the named result, kind word and all
  RESOLVED-LOOSE     the page heads that number under a different kind word, or
                     none - right about WHERE, loose about WHAT it is called
  NOT-FOUND-ON-PAGE  the page was read and does not head that result
  PAGE-NOT-IN-BOOK   the printed folio maps to no PDF page - tda2-10's defect
  NO-RESULT-CITED    a page pointer naming no numbered result, so there is
                     nothing to look for on it - unverifiable, not wrong
  ANCHORED-POINTER   a page pointer that names no numbered result but quotes a
                     phrase of three or more words from the page, so a reader
                     can find what it points at (LESSON-RUBRIC Gate 1.12)
  UNPARSEABLE        a citation-shaped span this parser could not turn into a
                     (book, result, page) triple
  NOVERDICT          the book's page tree is not on this machine

NOVERDICT is kept apart from every other status on purpose: a check that could
not run must never be counted with checks that ran and passed, and must never
be counted with checks that ran and failed.

The page mapping, the parsing and the on-page matching all come from
`citations.py`. Reimplementing any of them here would give the corpus sweep a
second, silently diverging opinion about what a citation resolves to.
"""
import argparse
import glob
import html
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# `python scripts/check_citations.py` puts scripts/ on sys.path, not the repo
# root, so `from scripts import ...` died with ImportError before a single
# citation was read: the documented entry point could not run at all, and the
# test suite never noticed because pytest imports from the root. (Codex review
# of PR #32.)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from scripts import citations as C  # noqa: E402
from scripts.ratchet import Ratchet, Unreadable, Usage  # noqa: E402

RESOLVED = "RESOLVED"
LOOSE = "RESOLVED-LOOSE"
NOT_FOUND = "NOT-FOUND-ON-PAGE"
NOT_IN_BOOK = "PAGE-NOT-IN-BOOK"
NO_RESULT = "NO-RESULT-CITED"
UNPARSEABLE = "UNPARSEABLE"
NOVERDICT = "NOVERDICT"
ANCHORED = "ANCHORED-POINTER"

# Report order: worst first, so a long sweep's tail is the interesting end.
ORDER = (NOT_IN_BOOK, NOT_FOUND, UNPARSEABLE, NO_RESULT, LOOSE, RESOLVED,
         ANCHORED, NOVERDICT)

#: statuses that mean "a page was actually read and compared".
#: PAGE-NOT-IN-BOOK is deliberately absent: it is assigned exactly when the
#: folio maps to no PDF page, so nothing was read. Counting it here made the
#: summary say those citations were "compared against a page" -- inflating the
#: one denominator this reporter exists to make trustworthy. It is still
#: reported, on its own line, and still fails --strict. (Codex review of PR #32.)
COMPARED = (RESOLVED, LOOSE, NOT_FOUND)


class Citation:
    """One (book, result, printed page(s)) claim and what became of it."""

    def __init__(self, path, line, book, result, pages, status, detail=""):
        """Store one citation claim and its resolution outcome."""
        self.path, self.line, self.book = path, line, book
        self.result, self.pages = result, pages
        self.status, self.detail = status, detail

    def row(self):
        """Format this citation as one human-readable report row."""
        where = ",".join(str(p) for p in sorted(self.pages)) or "-"
        try:
            shown = os.path.relpath(self.path, REPO).replace("\\", "/")
        except ValueError:          # a different drive on Windows
            shown = self.path
        return "%-17s %s:%d  %s, %s p. %s%s" % (
            self.status, shown, self.line, self.book, self.result, where,
            "  (%s)" % self.detail if self.detail else "")


QUOTED = re.compile(r"[“\"]([^”\"]+)[”\"]")
ANCHOR_WORDS = 3


def has_anchor_phrase(span):
    """Whether a span quotes a phrase of at least ANCHOR_WORDS words.

    A page number alone names a place, not a thing: 1,980 pointers in the
    corpus pointed at pages and said nothing about what is on them, which is
    why nothing could ever check them. Gate 1.12 now requires a result id or a
    quoted phrase of three or more words, so that a reader (or a script with
    the page text) has something to look for.
    """
    return any(len(re.findall(r"\w+", m)) >= ANCHOR_WORDS
               for m in QUOTED.findall(html.unescape(span)))


def _has_page_marker(span):
    """Return whether a citation span contains an explicit page marker."""
    return C.PAGES.search(span) is not None


def classify_file(path, primary, books, all_names, titles):
    """Every citation in one file, as Citation records.

    Mirrors `citations.check_file`'s traversal exactly - same `attribute`, same
    `unspanned_citations`, same `pdf_pages_for`, same `found_on_page` - and
    differs only in recording a status for the spans that check_file passes
    over in silence. If the two ever disagree about a file, this walk is what
    is wrong, because the gate's verdict is the one under review.
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    out = []
    try:
        attributed = C.attribute(text, primary, all_names, titles)
    except C.Unreadable as e:
        return [Citation(path, 0, primary, "-", set(), UNPARSEABLE, str(e))]
    try:
        attributed.extend(C.unspanned_citations(text, attributed, primary,
                                                all_names, titles))
    except C.Unreadable as e:
        # The ambiguous result/page binding check. That is precisely an
        # unparseable citation, and it is a finding, not a crash -- but it is
        # ONE finding. Returning early here replaced every explicitly marked
        # citation in the file with a single UNPARSEABLE row, shrinking the
        # per-status totals and the corpus denominator for the sake of one
        # prose sentence. The explicit spans are kept and classified below;
        # the ambiguity is recorded beside them. (Codex review of PR #32.)
        #
        # Stated limit: unspanned_citations raises mid-walk, so unmarked prose
        # references it had already collected before the ambiguous sentence are
        # not recorded. They were not recorded before this change either.
        out.append(Citation(path, 0, primary, "-", set(), UNPARSEABLE, str(e)))

    for span, pages, line, name in attributed:
        results = C.results_in(span)
        if not results:
            # A page claim with nothing to look for. Only report it when the
            # span names a page EXPLICITLY: `pages` is inherited from the
            # enclosing clause, so a bare fragment carrying a sibling's folio
            # is not a citation this file made.
            if pages and _has_page_marker(span):
                if has_anchor_phrase(span):
                    out.append(Citation(path, line, name, "-", pages, ANCHORED,
                                        "page cited with a quoted phrase"))
                else:
                    out.append(Citation(path, line, name, "-", pages,
                                        NO_RESULT,
                                        "page cited with no result "
                                        "identifier"))
            continue
        if not pages:
            # Pageless references are name-checked by the gate, not located.
            # They are not citations for this report's purposes and must not
            # inflate the denominator.
            continue
        if name not in books:
            for r in results:
                out.append(Citation(path, line, name, r, pages, NOVERDICT,
                                    "no page tree on this machine"))
            continue
        book = books[name]
        pdf_pages = sorted({n for p in pages for n in book.pdf_pages_for(p)})
        if not pdf_pages:
            for r in results:
                out.append(Citation(path, line, name, r, pages, NOT_IN_BOOK,
                                    "printed folio maps to no page in the book"))
            continue
        texts = [(n, book.text_of(n)) for n in pdf_pages]
        present = [(n, t) for n, t in texts if t is not None]
        missing = [n for n, t in texts if t is None]
        if not present:
            for r in results:
                out.append(Citation(path, line, name, r, pages, NOVERDICT,
                                    "cited page(s) could not be read"))
            continue
        for r in results:
            status, hit_raw = None, None
            for _n, t in present:
                st = C.found_on_page(r, C.normalise_for_search(t), t)
                if st == "exact":
                    status, hit_raw = st, t
                    break
                if st == "number-only" and status is None:
                    status, hit_raw = st, t
            if status == "exact":
                out.append(Citation(path, line, name, r, pages, RESOLVED))
            elif status == "number-only":
                num = re.sub(r"[a-z]$", "", r.partition(" ")[2])
                out.append(Citation(path, line, name, r, pages, LOOSE,
                                    "book heads it %r"
                                    % C.book_label_for(num, hit_raw)))
            elif missing:
                # Some candidate page was unreadable, so "not found" on the
                # others is not a verdict about this citation.
                out.append(Citation(path, line, name, r, pages, NOVERDICT,
                                    "a candidate page could not be read"))
            else:
                out.append(Citation(path, line, name, r, pages, NOT_FOUND,
                                    "PDF %s"
                                    % ",".join(str(n) for n in pdf_pages)))
    return out


def corpus_paths():
    """Every lesson and problem set, in a stable order."""
    found = sorted(glob.glob(os.path.join(REPO, "lessons", "*", "*.html")))
    found += sorted(glob.glob(os.path.join(REPO, "problems", "sets", "*.md")))
    return [p for p in found if not os.path.basename(p).startswith("_")]


def primary_for(path, all_names, titles):
    """This file's default book name, or None. Same rule as the gate's."""
    uid = os.path.splitext(os.path.basename(path))[0]
    try:
        name = C.book_for_unit(uid)
    except C.Unreadable:
        name = None
    if name:
        return name
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except OSError:
        return None
    return C.inferred_citation_book(raw, all_names, titles)


def load_books():
    """Load available book page trees and list the books absent locally."""
    books, absent = {}, []
    for name in sorted(C.load_bookmap()):
        try:
            books[name] = C.Book(name)
        except RuntimeError:
            absent.append(name)
    return books, absent


def report(cites, show):
    """Print selected citation rows and return counts for every status."""
    counts = {s: 0 for s in ORDER}
    for c in cites:
        counts[c.status] = counts.get(c.status, 0) + 1
    for status in ORDER:
        if status not in show:
            continue
        for c in cites:
            if c.status == status:
                print(c.row())
    print("")
    compared = sum(counts.get(s, 0) for s in COMPARED)
    # The positive signal the observation asked for: a count of citations that
    # were actually resolved, printed whether or not anything failed. A gate
    # that only speaks when it is unhappy cannot be distinguished from a gate
    # that never ran.
    print("%d citation(s) compared against a page; %d resolved (%d exactly, "
          "%d under a different label)"
          % (compared, counts[RESOLVED] + counts[LOOSE], counts[RESOLVED],
             counts[LOOSE]))
    for status in ORDER:
        if status in (RESOLVED, LOOSE):
            continue
        if counts.get(status):
            print("%-17s %d" % (status, counts[status]))
    return counts


def pointer_id(cite, occurrence, repo=None):
    """A stable id for one bare pointer: file, book, pages, and which occurrence.

    Not the line number: editing prose above a pointer must not turn it into a
    "new" one. Editing the pointer itself (its book or pages) does, which is
    the point: an edited citation is held to the new convention.
    """
    rel = os.path.relpath(cite.path, repo or REPO).replace("\\", "/")
    pages = ",".join(str(n) for n in sorted(cite.pages))
    return "%s|%s|p.%s|%d" % (rel, cite.book, pages, occurrence)


def bare_pointers(paths, primary_of, all_names, titles):
    """Every NO-RESULT-CITED pointer in `paths`, as (id, Citation), in file order.

    Classified with no page trees: whether a pointer names a result or quotes a
    phrase is a fact about the source text, so this gate runs identically on a
    machine with the books and in CI without them. Raises OSError on an
    unreadable file; a file with no attributable book makes no pointer claim.
    """
    found = []
    for path in paths:
        primary = primary_of(path)
        if primary is None:
            continue
        seen = {}
        for c in classify_file(path, primary, {}, all_names, titles):
            if c.status != NO_RESULT:
                continue
            key = (c.book, tuple(sorted(c.pages)))
            seen[key] = seen.get(key, 0) + 1
            found.append((pointer_id(c, seen[key]), c))
    return found


def pointer_gate(paths, ratchet, primary_of, all_names, titles):
    """The page-pointer convention as a shrink-only ratchet. Exit 0, 1 or 2.

    A bare pointer not on the baseline list fails (NEW). A listed pointer that
    is gone from its file, or now carries a result or a quoted phrase, is stale
    and fails until struck off; a list that grew since the base ref fails. The
    last two come from `scripts/ratchet.py`, with the same rules as every other
    drift list.
    """
    try:
        found = bare_pointers(paths, primary_of, all_names, titles)
    except OSError as e:
        print("ERROR could not read a lesson: %s" % e)
        return 2
    current = dict(found)
    rc = 0
    for uid in sorted(set(current) - ratchet.entries):
        c = current[uid]
        print("NEW-BARE-POINTER %s  (%s) -- name a result id or quote a phrase "
              "of three or more words from the page" % (c.row(), uid))
        rc = 1
    swept = {os.path.relpath(p, REPO).replace("\\", "/") for p in paths}
    verdicts = {}
    for uid in ratchet.entries:
        if uid.split("|", 1)[0] in swept and os.path.exists(
                os.path.join(REPO, uid.split("|", 1)[0])):
            verdicts[uid] = 1 if uid in current else 0
    rc = ratchet.check(verdicts, exists=lambda uid: os.path.exists(
        os.path.join(REPO, uid.split("|", 1)[0]))) or rc
    print("%d bare page pointer(s) in %d file(s); %d on the baseline list; "
          "%d new" % (len(current), len(swept), len(ratchet.entries),
                      len(set(current) - ratchet.entries)))
    return rc


def main(argv=None):
    """Sweep requested files or the corpus and report citation outcomes."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="files to sweep (default: corpus)")
    ap.add_argument("--book", help="override the primary book for every path")
    ap.add_argument("--only", default=",".join(ORDER),
                    help="comma-separated statuses to list (default: all)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any citation failed to resolve on its "
                         "page, or could not be parsed into one")
    ap.add_argument("--pointers", action="store_true",
                    help="gate bare page pointers (no result id, no quoted "
                         "phrase) against --known-failing as a shrink-only "
                         "ratchet; needs no page trees")
    ap.add_argument("--known-failing", metavar="LIST",
                    help="with --pointers: the baseline list of existing "
                         "bare pointers")
    ap.add_argument("--baseline", metavar="LIST",
                    help="with --pointers: the base ref's copy of the list; "
                         "fails if the list has grown")
    a = ap.parse_args(argv)

    show = {s.strip().upper() for s in a.only.split(",") if s.strip()}
    unknown = show - set(ORDER)
    if unknown:
        ap.error("unknown status(es): %s" % ", ".join(sorted(unknown)))

    if a.pointers:
        if not a.known_failing:
            ap.error("--pointers needs --known-failing")
        flags = ["--known-failing", a.known_failing]
        if a.baseline:
            flags += ["--baseline", a.baseline]
        try:
            ratchet, _ = Ratchet.from_argv(
                flags, label="page-pointer baseline list",
                remedy="Name a result id or quote a phrase of three or more "
                       "words instead.", subject="pointer's file")
            bm = C.load_bookmap()
            names = sorted(bm)
            titles = {k: v.get("title") for k, v in bm.items()}
            paths = [os.path.abspath(p) for p in a.paths] or corpus_paths()
            return pointer_gate(
                paths, ratchet,
                lambda path: a.book or primary_for(path, names, titles),
                names, titles)
        except Unreadable as e:
            print("ERROR could not read %s -- no verdict about the pointer "
                  "list" % e)
            return 2
        except Usage as e:
            print("ERROR %s" % e)
            return 2

    books, absent = load_books()
    if not books:
        print("ERROR no book on this machine has a page tree")
        print("This sweep needs the per-page markdown trees and cannot run "
              "here.")
        return 2
    if absent:
        print("NOTE %d book(s) have no page tree here: %s"
              % (len(absent), ", ".join(absent)))

    bm = C.load_bookmap()
    all_names, titles = sorted(bm), {k: v.get("title") for k, v in bm.items()}
    paths = [os.path.abspath(p) for p in a.paths] or corpus_paths()

    cites, unreadable = [], 0
    for p in paths:
        primary = a.book or primary_for(p, all_names, titles)
        if primary is None:
            # No syllabus book and the file names none. If it makes no
            # page-bearing claim there is nothing here to resolve; if it does,
            # that is an unparseable citation and must be visible.
            try:
                with open(p, encoding="utf-8") as f:
                    raw = f.read()
            except OSError as e:
                print("ERROR could not read %s: %s" % (p, e))
                unreadable += 1
                continue
            if C.has_page_result_claim(raw):
                cites.append(Citation(p, 0, "?", "-", set(), UNPARSEABLE,
                                      "no book could be attributed to this "
                                      "file"))
            continue
        try:
            cites.extend(classify_file(p, primary, books, all_names, titles))
        except OSError as e:
            print("ERROR could not read %s: %s" % (p, e))
            unreadable += 1

    print("=== %d file(s) swept" % len(paths))
    counts = report(cites, show)
    if unreadable:
        print("ERROR %d file(s) could not be read" % unreadable)
        return 2
    # UNPARSEABLE fails strict mode too. `Theorem 2.3 and Lemma 2.4, pp. 10-11`
    # cannot be bound to pages, so it was never checked -- and strict is the
    # opt-in gate contract, under which "could not be parsed" passing is
    # exactly the silent state a gate must not have. (Codex review of PR #32.)
    if a.strict and (counts[NOT_FOUND] or counts[NOT_IN_BOOK]
                     or counts[UNPARSEABLE]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
