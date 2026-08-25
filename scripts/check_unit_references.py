"""Check that cross-unit references resolve to both governed artifacts."""
import argparse
import os
import re
import sys


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIT_REF = re.compile(r"(?<![A-Za-z0-9])([a-z][a-z0-9]*-\d{2})(?![A-Za-z0-9])")
RETIRED_MODULES = {"gt"}


def governed_modules(repo=REPO):
    module_dir = os.path.join(repo, "curriculum", "modules")
    if os.path.isdir(module_dir):
        current = {os.path.splitext(name)[0] for name in os.listdir(module_dir)
                   if name.endswith(".md")}
    else:
        lesson_dir = os.path.join(repo, "lessons")
        current = set(os.listdir(lesson_dir)) if os.path.isdir(lesson_dir) else set()
        set_dir = os.path.join(repo, "problems", "sets")
        if os.path.isdir(set_dir):
            current.update(name.rsplit("-", 1)[0]
                           for name in os.listdir(set_dir) if name.endswith(".md"))
    return current | RETIRED_MODULES


def unit_refs(text, repo=REPO):
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text,
                  flags=re.I | re.S)
    modules = governed_modules(repo)
    return sorted({uid for uid in UNIT_REF.findall(text)
                   if uid.rsplit("-", 1)[0] in modules})


def missing_references(text, repo=REPO):
    missing = []
    for uid in unit_refs(text, repo=repo):
        module = uid.rsplit("-", 1)[0]
        expected = (
            os.path.join("problems", "sets", uid + ".md"),
            os.path.join("lessons", module, uid + ".html"),
        )
        absent = [path for path in expected
                  if not os.path.isfile(os.path.join(repo, path))]
        if absent:
            missing.append((uid, absent))
    return missing


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)
    failed = False
    checked = 0
    for path in args.paths:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        refs = unit_refs(text)
        checked += len(refs)
        for uid, absent in missing_references(text):
            failed = True
            print("FAIL %s references %s, missing %s" % (
                path, uid, ", ".join(absent)))
    print("%s checked %d cross-unit reference(s)" % (
        "FAIL" if failed else "PASS", checked))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
