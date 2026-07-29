import json

import yaml

from scripts.check_id_consistency import find_orphans


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _fixture(tmp_path):
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "curriculum/syllabus.yaml").write_text(
        yaml.safe_dump({"units": [{"id": "aa-01", "module": "aa"}]}),
        encoding="utf-8")
    _write_json(tmp_path / "state/progress.json", {"aa-01": {"status": "locked"}})
    _write_json(tmp_path / "srs/deck.json", {"cards": []})
    _write_json(tmp_path / "srs/seed-batch-01.json", [])
    return tmp_path


def test_clean_id_spaces_pass(tmp_path):
    assert find_orphans(_fixture(tmp_path)) == []


def test_orphan_srs_card_fails(tmp_path):
    root = _fixture(tmp_path)
    _write_json(root / "srs/deck.json", {"cards": [{"unit": "gt-99"}]})
    assert any("srs/deck.json" in error and "gt-99" in error
               for error in find_orphans(root))


def test_orphan_lesson_fails(tmp_path):
    root = _fixture(tmp_path)
    lesson = root / "lessons/gt/gt-99.html"
    lesson.parent.mkdir(parents=True)
    lesson.write_text("<html></html>", encoding="utf-8")
    assert any("lessons/gt/gt-99.html" in error
               for error in find_orphans(root))


def test_in_progress_unit_requires_expected_artifacts(tmp_path):
    root = _fixture(tmp_path)
    _write_json(root / "state/progress.json", {
        "aa-01": {"status": "in-progress"},
    })
    errors = find_orphans(root)
    assert any("lessons/aa/aa-01.html" in error for error in errors)
    assert any("learning-records/aa-01.md" in error for error in errors)
