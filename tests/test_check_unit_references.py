from pathlib import Path

from scripts.check_unit_references import missing_references, unit_refs


def make_pair(root, uid):
    module = uid.rsplit("-", 1)[0]
    (root / "problems" / "sets").mkdir(parents=True, exist_ok=True)
    (root / "lessons" / module).mkdir(parents=True, exist_ok=True)
    (root / "problems" / "sets" / (uid + ".md")).write_text("set")
    (root / "lessons" / module / (uid + ".html")).write_text("lesson")


def test_resolved_reference_requires_both_artifacts(tmp_path):
    make_pair(tmp_path, "lab-05")
    assert missing_references("See lab-05.", str(tmp_path)) == []


def test_missing_sibling_is_reported(tmp_path):
    (tmp_path / "problems" / "sets").mkdir(parents=True)
    (tmp_path / "problems" / "sets" / "lab-05.md").write_text("set")
    assert missing_references("See lab-05.", str(tmp_path)) == [
        ("lab-05", [str(Path("lessons") / "lab" / "lab-05.html")])]


def test_version_like_text_is_not_a_unit_reference(tmp_path):
    assert missing_references("encoded as utf-8", str(tmp_path)) == []


def test_unknown_module_reference_is_not_filtered_out(tmp_path):
    assert unit_refs("See cta-04.", str(tmp_path)) == ["cta-04"]
    assert missing_references("See cta-04.", str(tmp_path))


def test_unknown_module_after_corpus_cross_reference_wording_is_retained(tmp_path):
    assert unit_refs("Deferred to cta-04.", str(tmp_path)) == ["cta-04"]
    assert unit_refs("This is developed in cta-04.", str(tmp_path)) == ["cta-04"]
