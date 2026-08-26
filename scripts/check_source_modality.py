"""Validate the unit-to-source modality record."""
import json
import sys
import yaml

ALLOWED = {"proves", "states", "sets-as-exercise", "disclaims", "applies"}


def errors(records, books, units=None):
    out = []
    if not any(records.values()):
        out.append("no modality records were provided")
    for unit, rows in records.items():
        if units is not None and unit not in units:
            out.append("unknown unit %r" % unit)
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
    with open("curriculum/syllabus.yaml", encoding="utf-8") as f:
        units = {row["id"] for row in yaml.safe_load(f)["units"]}
    found = errors(records, books, units)
    for error in found:
        print("FAIL " + error)
    count = sum(len(rows) for rows in records.values())
    print("%s checked %d modality record(s); %d error(s)" % (
        "FAIL" if found else "PASS", count, len(found)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
