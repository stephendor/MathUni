"""check_resources.py — every unit's resources name something that can be read.

A unit's `resources:` line is not decoration. It is what `citations.py` uses to
decide which book a citation is checked against, so a line naming a source that
is not on the machine does not merely misdescribe the unit — it points the
verification gate at the wrong book, or at no book. an2-01 is the worked case:
its line reads ["Oxford M2 Metric Spaces notes", "Abbott 8.2 (or equiv.)"] while
its lesson is written from Lindström, so the gate resolved the unit to Abbott
and reported 25 of 31 citations wrong. Pointed at Lindström the same file
reports 5. Twenty of those failures were the syllabus, not the citations.

Two checks:

  1. RESOLVES. Every resource names a book in resources/bookmap.json, or is a
     member of a declared non-book class (software documentation, a named
     paper, self-directed project work). The classes are listed per MODULE
     below, not globally, because "self-directed" is correct for cap and would
     be a defect in la.

  2. PARTS EXIST. Where a resource names chapters or sections of a book that is
     on this machine, those chapters exist in it. This catches a reference to
     Ch. 12 of an eleven-chapter book. It cannot catch a reference to the wrong
     chapter of the right book — pw-04's "Cummings Real Analysis ch. 1-2", for
     material that is in Ch. 3 and Ch. 6 — because both chapters exist. That
     defect is only visible to a reader, or downstream to citations.py once the
     book is right.

  python scripts/check_resources.py
  python scripts/check_resources.py --selftest

Exit 0 clean, 1 if any unit fails, 2 if the check could not run. Check 2 needs
the per-page markdown tree and is SKIPPED with a printed count where the tree is
absent, never silently passed — so this runs in CI for check 1 alone.
"""
import argparse
import json
import os
import re
import sys

import yaml

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYLLABUS = os.path.join(REPO, "curriculum", "syllabus.yaml")
BOOKMAP = os.path.join(REPO, "resources", "bookmap.json")

# Non-book resources, by module. A class is legitimate for the modules listed
# and a defect anywhere else. Keeping this per-module is the point: it is what
# stops "self-directed" spreading from cap, where it is the whole pedagogy,
# into a module where it would mean "no source was ever identified".
NON_BOOK = {
    # module -> (regex, why it is legitimate there)
    "lab": (re.compile(r"giotto-tda|GUDHI|Ripser|persim|scikit|Kepler-Mapper"
                       r"|self-directed|docs\b|tutorials?\b|gallery"
                       r"|Otter et al\.|Singh-Memoli-Carlsson", re.I),
            "a computational module: its sources are library documentation and"
            " the papers those libraries implement"),
    "cap": (re.compile(r"self-directed|tdlbook\.org", re.I),
            "a capstone: the student chooses the sources"),
}


def load_syllabus(path=SYLLABUS):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["units"]


def load_books(path=BOOKMAP):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def book_named_in(resource, names):
    """The bookmap key this resource names, or None.

    Every word of the key must appear, so "Cummings" matches `Cummings ch. 3`
    while "Cummings Real Analysis" matches only a resource that also says Real
    Analysis. The most specific match wins, which is what separates the two
    Cummings volumes and the two Aluffis.
    """
    best = None
    for name in names:
        words = name.split()
        if all(re.search(r"\b%s\b" % re.escape(w), resource, re.I) for w in words):
            if best is None or len(words) > len(best.split()):
                best = name
    return best


# "ch. 3, 8", "ch. 1-9", "chapters 2 and 5" — one keyword can head a LIST, so
# the keyword is matched once and the whole number list after it is taken.
# Matching only the first number silently dropped the 8 of "Cummings ch. 3, 8".
CHAPTERS = re.compile(
    r"\bch(?:\.|apter)?s?\s*(\d+(?:\s*(?:[-–—,]|and)\s*\d+)*)", re.I)
SECTIONS = re.compile(r"(?<![\w.])\d+\.\d+")
NUMBER = re.compile(r"\d+")


def parts_named(resource):
    """(chapters, sections) a resource names, as sorted lists of ints/strings.

    A range names its ENDS, never its interior: "ch. 1-9" asserts that 1 and 9
    exist and says nothing about 5. Inferring the interior would invent claims
    the author did not make — the same rule citations.py uses for page ranges.
    """
    sections = set(SECTIONS.findall(resource))
    stripped = SECTIONS.sub(" ", resource)   # so "1.5-1.6" is not read as ch. 1
    chapters = set()
    for m in CHAPTERS.finditer(stripped):
        chapters.update(int(n) for n in NUMBER.findall(m.group(1)))
    # A section reference implies its chapter; do not double-report.
    chapters -= {int(x.split(".")[0]) for x in sections}
    return sorted(chapters), sorted(sections)


def book_text(name):
    """All of a book's extracted text, or None if the tree is not here."""
    from scripts.pull import all_pages, page_text, pages_dir
    d = pages_dir(name)
    if not os.path.isdir(d):
        return None
    return "\n".join(page_text(d, n) or "" for n in all_pages(d))


def chapter_present(blob, n):
    return re.search(r"\bchapter\s+%d\b" % n, blob, re.I) is not None


def section_present(blob, sec):
    return re.search(r"(?<![\w.])%s(?![\d])" % re.escape(sec), blob) is not None


def check(units, books, deep=True):
    """Returns (failures, checked, skipped_books). Prints a row per failure."""
    names = sorted(books)
    failures, checked, skipped = [], 0, set()
    blobs = {}
    for u in units:
        mod = u.get("module", "")
        pattern = NON_BOOK.get(mod, (None, ""))[0]
        for r in u.get("resources", []):
            checked += 1
            name = book_named_in(r, names)
            if name is None:
                if pattern is not None and pattern.search(r):
                    continue
                failures.append(
                    "%s: %r names no book in bookmap.json%s"
                    % (u["id"], r,
                       "" if pattern is None else
                       " and no %s resource" % mod))
                continue
            if not deep:
                continue
            if name not in blobs:
                blobs[name] = book_text(name)
            blob = blobs[name]
            if blob is None:
                skipped.add(name)
                continue
            chapters, sections = parts_named(r)
            for n in chapters:
                if not chapter_present(blob, n):
                    failures.append("%s: %r — %s has no Chapter %d"
                                    % (u["id"], r, name, n))
            for sec in sections:
                if not section_present(blob, sec):
                    failures.append("%s: %r — %s has no section %s"
                                    % (u["id"], r, name, sec))
    return failures, checked, skipped


def selftest():
    total, fails = [0], []

    def check_one(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    names = ["Abbott", "Cummings", "Cummings Real Analysis", "Carter",
             "Aluffi Chapter 0", "Aluffi Underground"]
    check_one("a bare author name resolves",
              book_named_in("Abbott 1.1-1.4", names) == "Abbott")
    check_one("the more specific of two volumes wins",
              book_named_in("Cummings Real Analysis ch. 3", names)
              == "Cummings Real Analysis")
    check_one("...and the less specific one is still reachable",
              book_named_in("Cummings ch. 3, 8", names) == "Cummings")
    check_one("the two Aluffis are told apart",
              book_named_in("Aluffi Underground 11.1", names) == "Aluffi Underground"
              and book_named_in("Aluffi Chapter 0 II.1", names) == "Aluffi Chapter 0")
    check_one("a phantom source resolves to nothing",
              book_named_in("Oxford M2 Metric Spaces notes", names) is None)
    check_one("a substring of an author's name does not match",
              book_named_in("Abbottsford lecture notes", names) is None)

    check_one("a chapter range names its ends, not its interior",
              parts_named("Carter ch. 1-3") == ([1, 3], []))
    check_one("a section range names both its ends",
              parts_named("Abbott 1.5-1.6") == ([], ["1.5", "1.6"]))
    check_one("a section does not also report its chapter",
              parts_named("Hatcher 1.1") == ([], ["1.1"]))
    check_one("one keyword can head a list of chapters",
              parts_named("Cummings ch. 3, 8") == ([3, 8], []))
    check_one("...including one joined by 'and'",
              parts_named("Carter chapters 2 and 5") == ([2, 5], []))
    check_one("a resource naming no parts reports none",
              parts_named("self-directed") == ([], []))

    # Negative controls for the two checks: each must FAIL on a planted defect.
    books = {n: {} for n in names}
    bad = [{"id": "x-01", "module": "la", "resources": ["Oxford M2 notes"]}]
    f, _, _ = check(bad, books, deep=False)
    check_one("check 1 fires on a resource naming no book", len(f) == 1)

    ok = [{"id": "x-02", "module": "la", "resources": ["Abbott 1.1"]}]
    f, _, _ = check(ok, books, deep=False)
    check_one("check 1 is quiet on a resource that resolves", f == [])

    lab = [{"id": "lab-01", "module": "lab", "resources": ["GUDHI install docs"]}]
    f, _, _ = check(lab, books, deep=False)
    check_one("a lab's software docs are legitimate", f == [])

    notlab = [{"id": "la-01", "module": "la", "resources": ["GUDHI install docs"]}]
    f, _, _ = check(notlab, books, deep=False)
    check_one("...and the same string in another module is a defect",
              len(f) == 1)

    cap = [{"id": "cap-01", "module": "cap", "resources": ["self-directed"]}]
    f, _, _ = check(cap, books, deep=False)
    check_one("a capstone's self-directed work is legitimate", f == [])

    capsoft = [{"id": "cap-01", "module": "cap", "resources": ["GUDHI docs"]}]
    f, _, _ = check(capsoft, books, deep=False)
    check_one("...but cap does not inherit lab's software class", len(f) == 1)

    check_one("a chapter that is absent is reported",
              not chapter_present("Chapter 1\nChapter 2\n", 7))
    check_one("...and one that is present is not",
              chapter_present("some text\n# Chapter 7: Contradiction\n", 7))
    check_one("a section number is not matched by a longer one",
              not section_present("see 1.15 below", "1.1"))
    check_one("...while the section itself matches",
              section_present("## 1.1. Proofs", "1.1"))

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--shallow", action="store_true",
                    help="check 1 only; do not open the page trees")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    sys.path.insert(0, REPO)
    units = load_syllabus()
    books = load_books()
    failures, checked, skipped = check(units, books, deep=not a.shallow)
    for f in failures:
        print("FAIL %s" % f)
    if skipped:
        print("NOTE %d book(s) have no page tree here, so their chapter and "
              "section references were NOT checked: %s"
              % (len(skipped), ", ".join(sorted(skipped))))
    print("%s %d unit(s), %d resource reference(s) checked, %d wrong"
          % ("FAIL" if failures else "PASS", len(units), checked, len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
