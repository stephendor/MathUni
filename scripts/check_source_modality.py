"""Validate the unit-to-source modality record."""
import json
import sys

ALLOWED = {"proves", "states", "sets-as-exercise", "disclaims", "applies"}


def errors(records, books):
    out = []
    for unit, rows in records.items():
        for index, row in enumerate(rows, 1):
            label = "%s[%d]" % (unit, index)
            for field in ("claim", "source", "section", "page", "modality"):
                if row.get(field) in (None, ""):
                    out.append("%s lacks %s" % (label, field))
            if row.get("source") not in books:
                out.append("%s names unknown source %r" % (label, row.get("source")))
            if row.get("modality") not in ALLOWED:
                out.append("%s has invalid modality %r" % (label, row.get("modality")))
    return out


def main():
    with open("curriculum/source-modality.json", encoding="utf-8") as f:
        records = json.load(f)
    with open("resources/bookmap.json", encoding="utf-8") as f:
        books = json.load(f)
    found = errors(records, books)
    for error in found:
        print("FAIL " + error)
    print("%s %d modality record error(s)" % (
        "FAIL" if found else "PASS", len(found)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
