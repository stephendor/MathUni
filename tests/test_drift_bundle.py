from types import SimpleNamespace

import pytest

from scripts import drift_bundle


def test_coverage_error_bounces_candidate(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    workspace = tmp_path / "drift"
    (repo / "problems/sets").mkdir(parents=True)
    (repo / "problems/sets/aa-01.md").write_text("problem", encoding="utf-8")
    (workspace / "candidates").mkdir(parents=True)
    (workspace / "candidates/aa-01.html").write_text(
        "<html></html>", encoding="utf-8")
    monkeypatch.setattr(drift_bundle, "repo_root", lambda: repo)
    monkeypatch.setattr(
        drift_bundle.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="boom"),
    )
    monkeypatch.setattr(drift_bundle.lesson_lint, "lint", lambda html: [])

    args = SimpleNamespace(unit="aa-01", workspace=str(workspace))
    with pytest.raises(SystemExit) as exc:
        drift_bundle.check(args)
    assert exc.value.code == 1


def test_zero_ref_coverage_is_visible_as_unchecked_without_bouncing(tmp_path, monkeypatch, capsys):
    repo = tmp_path / "repo"
    workspace = tmp_path / "drift"
    (repo / "problems/sets").mkdir(parents=True)
    (repo / "problems/sets/aa-01.md").write_text("problem", encoding="utf-8")
    (workspace / "candidates").mkdir(parents=True)
    (workspace / "candidates/aa-01.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(drift_bundle, "repo_root", lambda: repo)
    monkeypatch.setattr(
        drift_bundle.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="UNCHECKED checked 0 refs - nothing to verify\n",
            stderr="",
        ),
    )
    monkeypatch.setattr(drift_bundle.lesson_lint, "lint", lambda html: [])

    args = SimpleNamespace(unit="aa-01", workspace=str(workspace))
    with pytest.raises(SystemExit) as exc:
        drift_bundle.check(args)
    assert exc.value.code == 0
    assert "coverage        : UNCHECKED checked 0 refs" in capsys.readouterr().out
