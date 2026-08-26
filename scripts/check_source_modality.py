"""Validate the unit-to-source modality record."""
import json
import sys
import yaml

ALLOWED = {"proves", "states", "sets-as-exercise", "disclaims", "applies"}


def errors(records, books, units=None, unit_sources=None):
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
            elif unit_sources is not None and unit in unit_sources \
                    and row.get("source") not in unit_sources[unit]:
                out.append("%s source %r is not a resource for %s" % (
                    label, row.get("source"), unit))
            if row.get("modality") not in ALLOWED:
                out.append("%s has invalid modality %r" % (label, row.get("modality")))
    return out


def main():
    with open("curriculum/source-modality.json", encoding="utf-8") as f:
        records = json.load(f)
    with open("resources/bookmap.json", encoding="utf-8") as f:
        books = json.load(f)
    with open("curriculum/syllabus.yaml", encoding="utf-8") as f:
        syllabus = yaml.safe_load(f)["units"]
    from check_resources import book_named_in
    units = {row["id"] for row in syllabus}
    unit_sources = {
        row["id"]: {name for resource in row.get("resources", [])
                    for name in [book_named_in(resource, books)] if name}
        for row in syllabus
    }
    found = errors(records, books, units, unit_sources)
    for error in found:
        print("FAIL " + error)
    count = sum(len(rows) for rows in records.values())
    print("%s checked %d modality record(s); %d error(s)" % (
        "FAIL" if found else "PASS", count, len(found)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
