"""Cross-check that a lesson covers every numbered result its problem set cites.

The command always reports its denominator. A zero-reference source is
``UNCHECKED`` rather than a vacuous ``PASS``; ``--min-refs`` turns an expected
non-zero denominator into an enforcing authoring gate.
"""
import argparse
import re
import sys

REF_PATTERN = re.compile(r"(Theorem|Definition|Lemma|Corollary)\s+\d+[A-Za-z]?(?:\.\d+)*")


def find_refs(problem_set_text):
    return sorted({m.group(0) for m in REF_PATTERN.finditer(problem_set_text)})


def find_missing_refs(problem_set_text, lesson_html_text):
    refs = find_refs(problem_set_text)
    missing = []
    for r in refs:
        boundary_pattern = re.compile(re.escape(r) + r"(?!\d)(?!\.\d)")
        if not boundary_pattern.search(lesson_html_text):
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
