import copy
import subprocess
import sys

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

def test_duplicate_with_conflicting_prereqs_reports_duplicate_not_crash():
    doc = copy.deepcopy(VALID)
    conflicting = dict(doc["units"][0])
    conflicting["prereqs"] = ["la-02"]
    doc["units"].append(conflicting)
    errors = validate(doc)
    assert any("duplicate" in e for e in errors)

def test_cli_missing_file_clean_error():
    result = subprocess.run(
        [sys.executable, "scripts/validate_syllabus.py", "nonexistent.yaml"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert result.stdout.startswith("ERROR:") or result.stderr.startswith("ERROR:")
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined

def test_declared_primary_resource_must_lead():
    doc = copy.deepcopy(VALID)
    doc["modules"][0]["primary_resource"] = "Axler"
    doc["units"][0]["resources"] = ["Oxford notes"]
    assert any("does not match" in e for e in validate(doc))

def test_declared_primary_resource_requires_section_locator():
    doc = copy.deepcopy(VALID)
    doc["modules"][0]["primary_resource"] = "Axler"
    doc["units"][0]["resources"] = ["Axler ch. 1-2"]
    assert any("section-level locator" in e for e in validate(doc))
