"""Cross-check that a lesson covers every numbered result its problem set cites.

The command always reports its denominator. A zero-reference source is
``UNCHECKED`` rather than a vacuous ``PASS``; ``--min-refs`` turns an expected
non-zero denominator into an enforcing authoring gate.
"""
import argparse
import re
import sys

REF_PATTERN = re.compile(r"(Theorem|Definition|Lemma|Corollary)\s+\d+[A-Za-z]?(?:\.\d+)*")

# Obs 153: REF_PATTERN only matches the singular-and-separate citation form
# ("Definition 11.9"). A plural keyword with a comma/dash-joined list
# ("Definitions 11.8-11.9, p. 328", "Theorems 3, 4 and 5") cites each number
# just as validly, but never matches this pattern at all (the keyword is
# plural) — so a lesson that correctly teaches the content but cites it as a
# range reads as an untaught miss, and a problem set citing that way has its
# references skipped by the denominator entirely. Expand such citations into
# their individual singular refs before checking coverage.
_KEYWORD = r"Theorems?|Definitions?|Lemmas?|Corollar(?:y|ies)"
_NUMBER = r"\d+[A-Za-z]?(?:\.\d+)*"
_RANGE_PATTERN = re.compile(rf"({_KEYWORD})\s+({_NUMBER}(?:\s*(?:[-–—,]|and)\s*{_NUMBER})+)")
_SINGULAR_KEYWORD = {
    "theorem": "Theorem",
    "theorems": "Theorem",
    "definition": "Definition",
    "definitions": "Definition",
    "lemma": "Lemma",
    "lemmas": "Lemma",
    "corollary": "Corollary",
    "corollaries": "Corollary",
}


def _expand_range_refs(text):
    """Return the set of singular 'Keyword Number' refs a range/list citation covers.

    Only the numbers written down are expanded, not the interior of a span:
    "Definitions 12.1-12.5" yields 12.1 and 12.5, not 12.2 to 12.4. Inferring
    the interior would invent references the author never wrote.
    """
    expanded = set()
    for keyword_text, number_list in _RANGE_PATTERN.findall(text):
        keyword = _SINGULAR_KEYWORD.get(keyword_text.lower())
        if keyword is None:
            continue
        for n in re.findall(_NUMBER, number_list):
            expanded.add("%s %s" % (keyword, n))
    return expanded


def find_refs(problem_set_text):
    refs = {m.group(0) for m in REF_PATTERN.finditer(problem_set_text)}
    refs |= _expand_range_refs(problem_set_text)
    return sorted(refs)


def find_missing_refs(problem_set_text, lesson_html_text):
    refs = find_refs(problem_set_text)
    # A lesson may teach the same reference under a range/list citation rather
    # than the singular-and-separate form the check searches for; canonicalise
    # the lesson side the same way so a range-cited result reads as covered
    # rather than as a false miss.
    lesson_expanded = lesson_html_text + " " + " ".join(_expand_range_refs(lesson_html_text))
    missing = []
    for r in refs:
        boundary_pattern = re.compile(re.escape(r) + r"(?!\d)(?!\.\d)")
        if not boundary_pattern.search(lesson_expanded):
            missing.append(r)
    return missing


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-refs", type=int, default=0)
    parser.add_argument("problem_set_path")
    parser.add_argument("lesson_html_path")
    args = parser.parse_args(argv)
    if args.min_refs < 0:
        parser.error("--min-refs must be non-negative")
    with open(args.problem_set_path, encoding="utf-8") as f:
        problem_set_text = f.read()
    with open(args.lesson_html_path, encoding="utf-8") as f:
        lesson_html_text = f.read()
    refs = find_refs(problem_set_text)
    missing = find_missing_refs(problem_set_text, lesson_html_text)
    if len(refs) < args.min_refs:
        print("FAIL checked %d refs; minimum required is %d" % (len(refs), args.min_refs))
        return 1
    if not refs:
        print("UNCHECKED checked 0 refs - nothing to verify")
        return 0
    print("%s checked %d refs, %d missing" % (
        "FAIL" if missing else "PASS", len(refs), len(missing)))
    for ref in missing:
        print(ref)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
