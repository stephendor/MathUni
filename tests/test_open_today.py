import json

from scripts import open_today


def test_static_page_is_used_when_no_server_state_exists(tmp_path):
    (tmp_path / "dashboard").mkdir()
    (tmp_path / "dashboard" / "today.html").write_text("x", encoding="utf-8")
    url = open_today.target(str(tmp_path))
    assert url.startswith("file:///")
    assert url.endswith("dashboard/today.html")


def test_a_stale_server_json_does_not_win_over_the_page(tmp_path, monkeypatch):
    """A dead process leaves state/server.json behind, so its existence proves
    nothing. Only /healthz answering does."""
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "server.json").write_text(
        json.dumps({"port": 65530, "token": "x", "pid": 1}), encoding="utf-8")
    (tmp_path / "dashboard").mkdir()
    (tmp_path / "dashboard" / "today.html").write_text("x", encoding="utf-8")
    monkeypatch.setattr(open_today, "server_url", lambda root, timeout=1.0: None)
    assert open_today.target(str(tmp_path)).startswith("file:///")


def test_the_live_server_wins_when_it_answers(tmp_path, monkeypatch):
    (tmp_path / "dashboard").mkdir()
    (tmp_path / "dashboard" / "today.html").write_text("x", encoding="utf-8")
    monkeypatch.setattr(open_today, "server_url",
                        lambda root, timeout=1.0: "http://127.0.0.1:8787/")
    assert open_today.target(str(tmp_path)) == "http://127.0.0.1:8787/"


def test_nothing_to_open_is_reported_rather_than_guessed(tmp_path):
    assert open_today.target(str(tmp_path)) is None


def test_missing_everything_exits_non_zero(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(open_today, "target", lambda root: None)
    assert open_today.main([]) == 2
    assert "run `python scripts/daily.py` first" in capsys.readouterr().err


def test_print_mode_does_not_open_a_browser(tmp_path, monkeypatch, capsys):
    opened = []
    monkeypatch.setattr(open_today, "target", lambda root: "http://x/")
    monkeypatch.setattr(open_today.webbrowser, "open", lambda u: opened.append(u))
    assert open_today.main(["--print"]) == 0
    assert opened == []
    assert capsys.readouterr().out.strip() == "http://x/"


def test_server_url_tolerates_a_bom_in_server_json(tmp_path):
    """Same Windows hazard as the heartbeat: anything that hand-edits this file
    with PowerShell adds a BOM."""
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "server.json").write_text(
        json.dumps({"port": 1}), encoding="utf-8-sig")
    # Port 1 will not answer; the point is that it parsed far enough to try.
    assert open_today.server_url(str(tmp_path), timeout=0.05) is None


def test_server_url_survives_a_corrupt_server_json(tmp_path):
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "server.json").write_text("not json", encoding="utf-8")
    assert open_today.server_url(str(tmp_path), timeout=0.05) is None
