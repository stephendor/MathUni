"""Cross-check that a lesson HTML file covers every theorem/definition
reference its problem set relies on. Used as a pre-commit gate for newly
generated lessons (curriculum/LESSON-GUIDE.md)."""
import re
import sys

REF_PATTERN = re.compile(r"(Theorem|Definition|Lemma|Corollary)\s+\d+[A-Za-z]?(?:\.\d+)*")


def find_missing_refs(problem_set_text, lesson_html_text):
    refs = sorted({m.group(0) for m in REF_PATTERN.finditer(problem_set_text)})
    missing = []
    for r in refs:
        boundary_pattern = re.compile(re.escape(r) + r"(?!\d)(?!\.\d)")
        if not boundary_pattern.search(lesson_html_text):
            missing.append(r)
    return missing


def main():
    if len(sys.argv) != 3:
        print("usage: check_lesson_coverage.py <problem_set_path> <lesson_html_path>")
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        problem_set_text = f.read()
    with open(sys.argv[2], encoding="utf-8") as f:
        lesson_html_text = f.read()
    missing = find_missing_refs(problem_set_text, lesson_html_text)
    for ref in missing:
        print(ref)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
