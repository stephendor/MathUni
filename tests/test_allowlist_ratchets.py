"""Every allowlist in the repo detects its own stale entries.

`scripts/mission.py --known-failing` established the shape: a listed unit that
starts PASSING fails the run until it is struck off, and a listed unit whose
artifact is gone fails too. The rule is one line and it is the whole difference
between a ratchet and a suppression list, because "repaired but still excused"
is the one state an ordinary allowlist is silent about — so absence of a signal
cannot be read as absence of a backlog.

These tests hold the three allowlists that lacked that rule to it:

  * `check_resources.NON_BOOK`            — per-module non-book resource classes
  * `curriculum/coverage-zero-refs.json`  — units excused from the coverage floor
  * `check_unit_references.RETIRED_MODULES` — module ids kept recognisable

Each gets a control that violates the "may only shrink" claim in the forbidden
direction (GATE-AUTHORING-CHECKLIST G8), plus a positive control proving the
check is quiet when the entry is genuinely still doing work (G7) — without
which "no stale entries" would also be the answer a vacuous check gives.
`canvas-render-exceptions.json` already ratchets in `check_canvas_render.py`
and is covered by `tests/test_check_canvas_render.py`; `mission-drift.txt` by
`tests/test_mission.py`.
"""
import json
from pathlib import Path

import pytest

from scripts.check_resources import stale_non_book_classes
from scripts.check_unit import (load_json, load_syllabus_units,
                                stale_zero_refs, MANIFEST, ZERO_REFS)
from scripts.check_unit_references import (RETIRED_MODULES, audit_retired,
                                           stale_retired_modules)

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {n: {} for n in ["Abbott", "Carter", "Hatcher"]}


# --- check_resources.NON_BOOK ----------------------------------------------

def test_a_non_book_class_still_excusing_something_is_not_stale():
    """The positive control. Without it, a check that returned [] for every
    input would pass every negative below."""
    units = [{"id": "lab-01", "module": "lab", "resources": ["GUDHI docs"]},
             {"id": "cap-01", "module": "cap", "resources": ["self-directed"]}]
    assert stale_non_book_classes(units, BOOKS) == []


def test_a_non_book_class_whose_resources_were_all_repaired_is_stale():
    """The forbidden direction: every lab resource now names a real book, so
    the exemption excuses nothing and must not stay silently listed."""
    units = [{"id": "lab-01", "module": "lab", "resources": ["Carter ch. 1"]},
             {"id": "cap-01", "module": "cap", "resources": ["self-directed"]}]
    stale = stale_non_book_classes(units, BOOKS)
    assert [module for module, _why in stale] == ["lab"]
    assert "excuses nothing" in stale[0][1]


def test_a_non_book_class_for_a_module_with_no_units_is_stale():
    """The entry outliving the thing it excused — the second of mission.py's
    two stale shapes."""
    units = [{"id": "cap-01", "module": "cap", "resources": ["self-directed"]}]
    stale = stale_non_book_classes(units, BOOKS)
    assert [module for module, _why in stale] == ["lab"]
    assert "no unit in the syllabus" in stale[0][1]


def test_the_live_syllabus_has_no_stale_non_book_classes():
    """Corpus liveness: both entries are doing work today, so this passing is
    a real verdict rather than an empty population."""
    import yaml
    from scripts.check_resources import load_books
    units = yaml.safe_load(
        (ROOT / "curriculum" / "syllabus.yaml").read_text(encoding="utf-8"))["units"]
    assert stale_non_book_classes(units, load_books()) == []


# --- curriculum/coverage-zero-refs.json ------------------------------------

def test_a_zero_ref_entry_for_a_unit_the_syllabus_dropped_is_stale():
    manifest, zero_refs = load_json(MANIFEST), load_json(ZERO_REFS)
    stale = stale_zero_refs(manifest, dict(zero_refs, **{"zz-99": "why"}),
                            load_syllabus_units())
    assert [uid for uid, _why in stale] == ["zz-99"]
    assert "no unit zz-99 in the syllabus" in stale[0][1]


def test_a_zero_ref_entry_no_coverage_gate_can_read_is_stale():
    """An exemption the gate never reads cannot fire in either direction, so
    it is silence with no subject — the state this rule exists to name."""
    manifest = {"gates": [{"id": "lesson-lint", "argv": ["x"], "ci": True}]}
    stale = stale_zero_refs(manifest, {"lab-02": "why"}, {"lab-02"})
    assert [uid for uid, _why in stale] == ["lab-02"]
    assert "never read" in stale[0][1]


def test_the_live_zero_ref_list_has_no_stale_entries():
    """Positive control on real data: all three entries are governed by a
    coverage gate and still in the syllabus."""
    zero_refs = load_json(ZERO_REFS)
    assert zero_refs, "an empty list would make the check vacuous"
    assert stale_zero_refs(load_json(MANIFEST), zero_refs,
                           load_syllabus_units()) == []


def test_the_other_half_of_the_zero_ref_ratchet_is_the_gate_itself():
    """'Listed and passing' is caught by check_lesson_coverage.py, which FAILS
    when --expect-zero-refs is given and refs are in fact found. This test
    pins that the disposition still reaches the command, so the two halves
    cannot drift apart."""
    from scripts.check_unit import commands_for_unit
    assert "--expect-zero-refs" in dict(commands_for_unit("lab-02", ci=True))["coverage"]


# --- check_unit_references.RETIRED_MODULES ---------------------------------

def test_a_retired_module_that_came_back_is_stale(tmp_path, monkeypatch):
    import scripts.check_unit_references as mod
    (tmp_path / "curriculum" / "modules").mkdir(parents=True)
    (tmp_path / "curriculum" / "modules" / "gt.md").write_text("live again")
    (tmp_path / "curriculum" / "syllabus.yaml").write_text("units: []")
    monkeypatch.setattr(mod, "RETIRED_MODULES", {"gt"})
    stale, scanned, _missing = mod.stale_retired_modules(str(tmp_path))
    assert [m for m, _why in stale] == ["gt"]
    assert "live again" in stale[0][1]
    assert scanned == 0


def test_a_retired_module_nothing_references_any_more_is_stale(tmp_path, monkeypatch):
    import scripts.check_unit_references as mod
    (tmp_path / "curriculum").mkdir(parents=True)
    (tmp_path / "curriculum" / "syllabus.yaml").write_text(
        "units:\n  - id: lab-01\n")
    (tmp_path / "problems" / "sets").mkdir(parents=True)
    (tmp_path / "problems" / "sets" / "lab-01.md").write_text("no refs here")
    (tmp_path / "lessons" / "lab").mkdir(parents=True)
    (tmp_path / "lessons" / "lab" / "lab-01.html").write_text("<p>none</p>")
    monkeypatch.setattr(mod, "RETIRED_MODULES", {"gt"})
    stale, scanned, _missing = mod.stale_retired_modules(str(tmp_path))
    assert [m for m, _why in stale] == ["gt"]
    assert scanned == 2


def test_a_retired_module_still_referenced_is_not_stale(tmp_path, monkeypatch):
    """The positive control. It also pins the reading boundary: the reference
    is found in rendered prose."""
    import scripts.check_unit_references as mod
    (tmp_path / "curriculum").mkdir(parents=True)
    (tmp_path / "curriculum" / "syllabus.yaml").write_text(
        "units:\n  - id: lab-01\n")
    (tmp_path / "problems" / "sets").mkdir(parents=True)
    (tmp_path / "problems" / "sets" / "lab-01.md").write_text("see gt-04")
    (tmp_path / "lessons" / "lab").mkdir(parents=True)
    (tmp_path / "lessons" / "lab" / "lab-01.html").write_text("<p>x</p>")
    monkeypatch.setattr(mod, "RETIRED_MODULES", {"gt"})
    stale, _scanned, _missing = mod.stale_retired_modules(str(tmp_path))
    assert stale == []


def test_a_reference_only_inside_a_script_does_not_keep_an_entry_alive(tmp_path,
                                                                      monkeypatch):
    """The stripper is shared with unit_refs (one parser, not two), so a unit
    id no reader ever sees does not count as a live reference here either."""
    import scripts.check_unit_references as mod
    (tmp_path / "curriculum").mkdir(parents=True)
    (tmp_path / "curriculum" / "syllabus.yaml").write_text(
        "units:\n  - id: lab-01\n")
    (tmp_path / "problems" / "sets").mkdir(parents=True)
    (tmp_path / "problems" / "sets" / "lab-01.md").write_text("nothing")
    (tmp_path / "lessons" / "lab").mkdir(parents=True)
    (tmp_path / "lessons" / "lab" / "lab-01.html").write_text(
        "<script>var a = 'gt-04';</script><!-- gt-04 -->")
    monkeypatch.setattr(mod, "RETIRED_MODULES", {"gt"})
    stale, _scanned, _missing = mod.stale_retired_modules(str(tmp_path))
    assert [m for m, _why in stale] == ["gt"]


def test_a_missing_governed_artifact_is_reported_not_silently_dropped(tmp_path,
                                                                     monkeypatch):
    """G14: the denominator is reported with the verdict, so a corpus that
    shrank cannot look like a clean audit."""
    import scripts.check_unit_references as mod
    (tmp_path / "curriculum").mkdir(parents=True)
    (tmp_path / "curriculum" / "syllabus.yaml").write_text(
        "units:\n  - id: lab-01\n")
    monkeypatch.setattr(mod, "RETIRED_MODULES", set())
    _stale, scanned, missing = mod.stale_retired_modules(str(tmp_path))
    assert scanned == 0 and len(missing) == 2


def test_the_gt_entry_the_ratchet_found_is_struck():
    """The watched failure, preserved. Run for the first time on 2026-09-09 the
    audit reported `gt` stale — nothing in 290 governed files had named a gt-NN
    unit — and the entry was struck. Reintroducing it without a reference must
    fail the audit again, so this pins the finished state."""
    assert RETIRED_MODULES == set()


def test_the_live_corpus_passes_the_retired_module_audit(capsys):
    assert audit_retired() == 0
    out = capsys.readouterr().out
    assert "PASS retired-module audit" in out
    assert "governed file(s)" in out


def test_audit_retired_refuses_a_caller_supplied_population():
    """G3: the population is derived, never passed in — a caller that named
    its own files could make any entry look unreferenced."""
    from scripts.check_unit_references import main
    with pytest.raises(SystemExit):
        main(["--audit-retired", "lessons/lab/lab-09.html"])


def test_the_workflow_runs_the_retired_module_audit():
    """G19: wired into the corpus loop in the same change, not left to a
    future one."""
    workflow = (ROOT / ".github" / "workflows" / "quality-gates.yml").read_text(
        encoding="utf-8")
    assert "check_unit_references.py --audit-retired" in workflow


def test_every_allowlist_in_the_repo_is_accounted_for():
    """The completeness claim this file makes. A new suppression list added
    without a ratchet should break this test rather than pass unnoticed."""
    known = {
        "curriculum/mission-drift.txt",          # scripts/mission.py
        "curriculum/coverage-zero-refs.json",    # scripts/check_unit.py
        "curriculum/canvas-render-exceptions.json",  # check_canvas_render.py
    }
    on_disk = {
        "curriculum/" + p.name
        for p in (ROOT / "curriculum").iterdir()
        if p.name in {"mission-drift.txt", "coverage-zero-refs.json",
                      "canvas-render-exceptions.json"}}
    assert on_disk == known
    # And the two in-code lists, which have no file to enumerate.
    from scripts.check_resources import NON_BOOK
    assert set(NON_BOOK) == {"lab", "cap"}
    assert json.loads(
        (ROOT / "curriculum" / "canvas-render-exceptions.json").read_text(
            encoding="utf-8"))
