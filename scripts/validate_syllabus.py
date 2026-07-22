"""Validate curriculum/syllabus.yaml: ids unique, prereqs exist, DAG acyclic,
modules/semesters consistent, required unit fields present, every resource
resolves to a known source, and no prereq points forward into a later semester.

  python scripts/validate_syllabus.py             # validate the real file
  python scripts/validate_syllabus.py --selftest  # prove the new gates can fire
"""
import json
import sys
from graphlib import TopologicalSorter, CycleError

import yaml

REQUIRED_UNIT_FIELDS = ("id", "module", "title", "prereqs", "resources",
                        "hook", "mission_link")

BOOKMAP = "resources/bookmap.json"
SOURCES = "resources/resource_sources.json"


def load_syllabus(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return None


def resource_resolves(res, book_keys, source_prefixes):
    """A resource string resolves if a bookmap key or a registered non-book
    source prefix is a prefix of it (the longest-prefix rule, RESOURCES.md)."""
    r = res.strip()
    return (any(r.startswith(k) for k in book_keys)
            or any(r.startswith(s) for s in source_prefixes))


def validate(doc, book_keys=(), source_prefixes=()):
    """Return a list of error strings. `book_keys`/`source_prefixes` enable the
    resource-resolvability check; pass them empty to skip it (e.g. no registry)."""
    errors = []
    sem_ids = {s["id"] for s in doc.get("semesters", [])}
    sem_order = {s["id"]: i for i, s in enumerate(doc.get("semesters", []))}
    mod_ids = set()
    mod_sem = {}
    for m in doc.get("modules", []):
        if m["id"] in mod_ids:
            errors.append(f"duplicate module id: {m['id']}")
        mod_ids.add(m["id"])
        mod_sem[m["id"]] = m.get("semester")
        if m.get("semester") not in sem_ids:
            errors.append(f"module {m['id']}: unknown semester {m.get('semester')}")

    unit_ids = set()
    unit_mod = {}
    for u in doc.get("units", []):
        uid = u.get("id", "<missing>")
        for field in REQUIRED_UNIT_FIELDS:
            if field not in u or u[field] in (None, ""):
                errors.append(f"unit {uid}: missing field '{field}'")
        if uid in unit_ids:
            errors.append(f"duplicate unit id: {uid}")
        unit_ids.add(uid)
        unit_mod[uid] = u.get("module")
        if u.get("module") not in mod_ids:
            errors.append(f"unit {uid}: unknown module {u.get('module')}")
        if book_keys or source_prefixes:
            for res in u.get("resources", []) or []:
                if not resource_resolves(res, book_keys, source_prefixes):
                    errors.append(
                        f"unit {uid}: unresolvable resource {res!r} — register "
                        f"the book in {BOOKMAP} or the source in {SOURCES}")

    def sem_of(uid):
        return sem_order.get(mod_sem.get(unit_mod.get(uid)))

    for u in doc.get("units", []):
        uid = u.get("id", "<missing>")
        for p in u.get("prereqs", []):
            if p not in unit_ids:
                errors.append(f"unit {uid}: unknown prereq {p}")
                continue
            su, sp = sem_of(uid), sem_of(p)
            if su is not None and sp is not None and sp > su:
                errors.append(
                    f"unit {uid} ({mod_sem.get(unit_mod.get(uid))}): prereq {p} is "
                    f"in a later semester ({mod_sem.get(unit_mod.get(p))}) — likely mis-wired")

    # Skip cycle detection when duplicate unit ids were found: the dict
    # comprehension below would let one duplicate's prereqs silently
    # overwrite another's, corrupting the graph. Duplicates are already
    # reported as errors above, so there's nothing useful to add here.
    if not any("duplicate unit id" in e for e in errors):
        try:
            ts = TopologicalSorter(
                {u["id"]: set(u.get("prereqs", [])) & unit_ids
                 for u in doc.get("units", [])})
            ts.prepare()
        except CycleError as e:
            errors.append(f"prerequisite cycle detected: {e.args[1]}")
    return errors


def selftest():
    """Negative controls: prove each new gate fires and that clean data passes."""
    books = ["Munkres", "Abbott"]
    srcs = ["Oxford", "giotto-tda"]
    ok = {
        "semesters": [{"id": "s1"}, {"id": "s2"}],
        "modules": [{"id": "an", "semester": "s1"}, {"id": "top", "semester": "s2"}],
        "units": [
            {"id": "an-01", "module": "an", "title": "t", "prereqs": [],
             "resources": ["Abbott 1.1"], "hook": "h", "mission_link": "m"},
            {"id": "top-01", "module": "top", "title": "t", "prereqs": ["an-01"],
             "resources": ["Munkres §12", "Oxford notes"], "hook": "h", "mission_link": "m"},
        ],
    }
    total = [0]
    fails = []

    def check(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    check("clean doc passes both new gates", validate(ok, books, srcs) == [])

    bad_res = json.loads(json.dumps(ok))
    bad_res["units"][1]["resources"] = ["Bogus Source 3.1"]
    check("fires on unresolvable resource",
          any("unresolvable resource" in e for e in validate(bad_res, books, srcs)))

    check("resource check is skipped when no registry is loaded",
          not any("unresolvable" in e for e in validate(bad_res, (), ())))

    fwd = json.loads(json.dumps(ok))
    fwd["units"].append({"id": "an-02", "module": "an", "title": "t",
                         "prereqs": ["top-01"], "resources": ["Abbott 2.1"],
                         "hook": "h", "mission_link": "m"})  # s1 <- s2, no cycle
    check("fires on forward-semester prereq",
          any("later semester" in e for e in validate(fwd, books, srcs)))

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def main(path="curriculum/syllabus.yaml"):
    try:
        doc = load_syllabus(path)
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    bookmap = _load_json(BOOKMAP) or {}
    sources = _load_json(SOURCES) or {}
    book_keys = sorted(bookmap.keys(), key=len, reverse=True)
    source_prefixes = sources.get("non_book_sources", [])
    if not book_keys and not source_prefixes:
        print("WARNING: no resolver registry found — resource checks skipped")
    errors = validate(doc, book_keys, source_prefixes)
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        sys.exit(1)
    print("syllabus OK")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        sys.exit(selftest())
    main(*args[:1])
