"""Validate curriculum/syllabus.yaml: ids unique, prereqs exist, DAG acyclic,
modules/semesters consistent, required unit fields present."""
import sys
from graphlib import TopologicalSorter, CycleError

import yaml

REQUIRED_UNIT_FIELDS = ("id", "module", "title", "prereqs", "resources",
                        "hook", "mission_link")


def load_syllabus(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(doc):
    errors = []
    sem_ids = {s["id"] for s in doc.get("semesters", [])}
    mod_ids = set()
    for m in doc.get("modules", []):
        if m["id"] in mod_ids:
            errors.append(f"duplicate module id: {m['id']}")
        mod_ids.add(m["id"])
        if m.get("semester") not in sem_ids:
            errors.append(f"module {m['id']}: unknown semester {m.get('semester')}")

    unit_ids = set()
    for u in doc.get("units", []):
        uid = u.get("id", "<missing>")
        for field in REQUIRED_UNIT_FIELDS:
            if field not in u or u[field] in (None, ""):
                errors.append(f"unit {uid}: missing field '{field}'")
        if uid in unit_ids:
            errors.append(f"duplicate unit id: {uid}")
        unit_ids.add(uid)
        if u.get("module") not in mod_ids:
            errors.append(f"unit {uid}: unknown module {u.get('module')}")

    for u in doc.get("units", []):
        for p in u.get("prereqs", []):
            if p not in unit_ids:
                errors.append(f"unit {u['id']}: unknown prereq {p}")

    try:
        ts = TopologicalSorter(
            {u["id"]: set(u.get("prereqs", [])) & unit_ids
             for u in doc.get("units", [])})
        ts.prepare()
    except CycleError as e:
        errors.append(f"prerequisite cycle detected: {e.args[1]}")
    return errors


def main(path="curriculum/syllabus.yaml"):
    errors = validate(load_syllabus(path))
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        sys.exit(1)
    print("syllabus OK")


if __name__ == "__main__":
    main(*sys.argv[1:2])
