"""A unit's resources line is what picks the book its citations are checked
against, so a line naming a source that is not on the machine points the
verification gate at the wrong book — or at no book, in which case the gate
cannot run and reports nothing at all."""
import json

import yaml

from scripts.check_resources import (book_named_in, chapter_present, check,
                                     parts_named, section_present, selftest)

NAMES = ["Abbott", "Cummings", "Cummings Real Analysis", "Carter", "Hatcher",
         "Lindstrom", "Aluffi Chapter 0", "Aluffi Underground"]
BOOKS = {n: {} for n in NAMES}


# --- check 1: does the resource name anything readable? --------------------

def test_the_defect_this_gate_was_built_for_fires():
    """an2-02's line was ["Oxford M2 Metric Spaces notes"] and nothing else, so
    the unit resolved to no book and citations.py checked zero of its twenty
    citations. Six an2 units were in that state."""
    unit = [{"id": "an2-02", "module": "an2",
             "resources": ["Oxford M2 Metric Spaces notes"]}]
    failures, checked, _ = check(unit, BOOKS, deep=False)
    assert checked == 1
    assert len(failures) == 1
    assert "an2-02" in failures[0] and "no book" in failures[0]


def test_the_repaired_line_passes():
    unit = [{"id": "an2-02", "module": "an2",
             "resources": ["Lindstrom 3.4", "Lindstrom 3.7"]}]
    failures, checked, _ = check(unit, BOOKS, deep=False)
    assert (failures, checked) == ([], 2)


def test_a_non_book_class_is_scoped_to_its_module():
    """"self-directed" is the whole pedagogy of cap and would mean "no source
    was ever identified" in la. The classes are per-module for that reason."""
    ok = [{"id": "cap-01", "module": "cap", "resources": ["self-directed"]}]
    bad = [{"id": "la-01", "module": "la", "resources": ["self-directed"]}]
    assert check(ok, BOOKS, deep=False)[0] == []
    assert len(check(bad, BOOKS, deep=False)[0]) == 1


def test_cap_does_not_inherit_labs_software_class():
    unit = [{"id": "cap-02", "module": "cap", "resources": ["GUDHI install docs"]}]
    assert len(check(unit, BOOKS, deep=False)[0]) == 1


# --- resolving a book name -------------------------------------------------

def test_the_more_specific_volume_wins():
    """pw-04 cites Cummings's Real Analysis and pw-03 cites his Proofs. A
    prefix match on "Cummings" alone would send one unit's citations to the
    other's book."""
    assert book_named_in("Cummings Real Analysis ch. 6", NAMES) \
        == "Cummings Real Analysis"
    assert book_named_in("Cummings ch. 3, 8", NAMES) == "Cummings"


def test_a_longer_word_is_not_a_match():
    assert book_named_in("Abbottsford lecture notes", NAMES) is None


# --- check 2: do the parts named exist? ------------------------------------

def test_a_range_names_its_ends_never_its_interior():
    """"ch. 1-9" asserts 1 and 9 exist and says nothing about 5 — inferring the
    interior would invent claims the author did not make."""
    assert parts_named("Carter ch. 1-3") == ([1, 3], [])
    assert parts_named("Abbott 1.5-1.6") == ([], ["1.5", "1.6"])


def test_one_keyword_can_head_a_list():
    """"Cummings ch. 3, 8" names two chapters. Matching only the number
    adjacent to the keyword silently dropped the 8."""
    assert parts_named("Cummings ch. 3, 8") == ([3, 8], [])
    assert parts_named("Carter chapters 2 and 5") == ([2, 5], [])


def test_a_section_does_not_also_report_its_chapter():
    assert parts_named("Hatcher 1.1") == ([], ["1.1"])


def test_a_section_number_is_not_matched_by_a_longer_one():
    assert not section_present("see 1.15 below", "1.1")
    assert section_present("## 1.1. Proofs", "1.1")


def test_an_absent_chapter_is_reported():
    assert not chapter_present("Chapter 1\nChapter 2\n", 7)
    assert chapter_present("# Chapter 7: Contradiction\n", 7)


# --- the live syllabus -----------------------------------------------------

def test_the_committed_syllabus_passes_check_one(repo_root=None):
    """The enforcing run. Check 2 is local-only (it needs the page trees), so
    this is the half CI can also run."""
    import os
    repo = repo_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(repo, "curriculum", "syllabus.yaml"), encoding="utf-8") as f:
        units = yaml.safe_load(f)["units"]
    with open(os.path.join(repo, "resources", "bookmap.json"), encoding="utf-8") as f:
        books = json.load(f)
    failures, checked, _ = check(units, books, deep=False)
    assert failures == [], failures
    assert checked > 200, "the denominator collapsed; the syllabus is not being read"


def test_selftest_passes(capsys):
    assert selftest() == 0
    assert "checks passed" in capsys.readouterr().out
