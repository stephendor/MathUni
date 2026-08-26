import json
import os
from pathlib import Path

from scripts.check_unit import commands_for_unit, discovered_units, unit_context


ROOT = Path(__file__).resolve().parents[1]


def test_unit_context_maps_both_artifacts():
    assert unit_context("aa-07") == {
        "unit": "aa-07", "module": "aa",
        "problem": os.path.join("problems", "sets", "aa-07.md"),
        "lesson": os.path.join("lessons", "aa", "aa-07.html")}


def test_manifest_applies_module_specific_gates():
    aa = [name for name, _command in commands_for_unit("aa-07", ci=True)]
    lab = [name for name, _command in commands_for_unit("lab-02", ci=True)]
    assert "sections" in aa and "lab-outputs" not in aa
    assert "lab-outputs" in lab and "sections" in lab
    assert "--allow-no-indexed" in dict(
        commands_for_unit("pw-04", ci=True))["sections"]


def test_zero_ref_disposition_reaches_the_coverage_command():
    command = dict(commands_for_unit("lab-02", ci=True))["coverage"]
    assert "--expect-zero-refs" in command


def test_workflow_consumes_the_manifest_runner():
    workflow = (ROOT / ".github" / "workflows" / "quality-gates.yml").read_text(
        encoding="utf-8")
    assert "python scripts/check_unit.py --all --ci" in workflow
    manifest = json.loads((ROOT / "curriculum" / "unit-gates.json").read_text(
        encoding="utf-8"))
    assert {gate["id"] for gate in manifest["gates"]} == {
        "lesson-lint", "html-js", "mission", "coverage",
        "hypothesis-parity", "cross-unit-refs", "visual-claims",
        "source-heading", "sections", "lab-outputs"}


def test_discovery_names_the_governed_unit_population():
    units = discovered_units()
    assert "aa-07" in units and "lab-02" in units


def test_discovery_keeps_incomplete_pairs_visible(monkeypatch):
    monkeypatch.setattr("scripts.check_unit.load_syllabus_units",
                        lambda: {"aa-07", "future-99"})
    assert "future-99" in discovered_units()
