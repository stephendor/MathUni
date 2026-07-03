import copy
from scripts.validate_syllabus import validate

VALID = {
    "version": 1,
    "semesters": [{"id": "s1", "title": "Rigour and machinery"}],
    "modules": [{"id": "la", "title": "Linear Algebra", "semester": "s1"}],
    "units": [
        {"id": "la-01", "module": "la", "title": "Vector spaces",
         "prereqs": [], "resources": ["Axler 1A-1B"],
         "hook": "Why polynomials are secretly vectors.",
         "mission_link": "Homology groups are vector spaces first."},
        {"id": "la-02", "module": "la", "title": "Subspaces",
         "prereqs": ["la-01"], "resources": ["Axler 1C"],
         "hook": "Planes through the origin.",
         "mission_link": "Cycles and boundaries are subspaces."},
    ],
}

def test_valid_doc_passes():
    assert validate(copy.deepcopy(VALID)) == []

def test_duplicate_unit_id_fails():
    doc = copy.deepcopy(VALID)
    doc["units"].append(dict(doc["units"][0]))
    assert any("duplicate" in e for e in validate(doc))

def test_unknown_prereq_fails():
    doc = copy.deepcopy(VALID)
    doc["units"][1]["prereqs"] = ["zz-99"]
    assert any("zz-99" in e for e in validate(doc))

def test_cycle_fails():
    doc = copy.deepcopy(VALID)
    doc["units"][0]["prereqs"] = ["la-02"]
    assert any("cycle" in e.lower() for e in validate(doc))

def test_unknown_module_fails():
    doc = copy.deepcopy(VALID)
    doc["units"][0]["module"] = "nope"
    assert any("nope" in e for e in validate(doc))

def test_missing_hook_fails():
    doc = copy.deepcopy(VALID)
    del doc["units"][0]["hook"]
    assert any("hook" in e for e in validate(doc))
