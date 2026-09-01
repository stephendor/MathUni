import json
from datetime import date

from scripts import open_today


def built_today(root):
    """A heartbeat vouching for today, plus the page that run would have left.

    Without this, target() correctly refuses to present the artifact as today
    and overwrites it, so a fixture that only touches today.html is testing the
    retraction path rather than the one it names.
    """
    (root / "state").mkdir(exist_ok=True)
    (root / "state" / "last-daily-run.json").write_text(
        json.dumps({"date": date.today().isoformat(), "outcome": "built"}),
        encoding="utf-8")
    (root / "dashboard").mkdir(exist_ok=True)
    (root / "dashboard" / "today.html").write_text("x", encoding="utf-8")


def test_static_page_is_used_when_no_server_state_exists(tmp_path):
    built_today(tmp_path)
    url = open_today.target(str(tmp_path))
    assert url.startswith("file:///")
    assert url.endswith("dashboard/today.html")


def test_a_stale_server_json_does_not_win_over_the_page(tmp_path, monkeypatch):
    """A dead process leaves state/server.json behind, so its existence proves
    nothing. Only /healthz answering does."""
    built_today(tmp_path)
    (tmp_path / "state" / "server.json").write_text(
        json.dumps({"port": 65530, "token": "x", "pid": 1}), encoding="utf-8")
    monkeypatch.setattr(open_today, "server_url", lambda root, timeout=1.0: None)
    assert open_today.target(str(tmp_path)).startswith("file:///")


def test_the_live_server_wins_when_it_answers(tmp_path, monkeypatch):
    built_today(tmp_path)
    monkeypatch.setattr(open_today, "server_url",
                        lambda root, timeout=1.0: "http://127.0.0.1:8787/")
    assert open_today.target(str(tmp_path)) == "http://127.0.0.1:8787/"


def test_an_empty_repo_gets_an_honest_page_rather_than_nothing(tmp_path):
    """Nothing built and no server: the shortcut still opens something, and
    what it opens says what to run. A shortcut that does nothing visible is
    indistinguishable from a shortcut that is broken."""
    url = open_today.target(str(tmp_path))
    assert url.startswith("file:///")
    page = (tmp_path / "dashboard" / "today.html").read_text(encoding="utf-8")
    assert "No day has been built" in page
    assert "scripts/daily.py" in page


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


# --- review findings --------------------------------------------------------

def test_a_non_integer_port_returns_none_rather_than_raising(tmp_path):
    """`%d` on a string raises TypeError outside the try, so a corrupt file
    crashed instead of falling back to the static page."""
    (tmp_path / "state").mkdir()
    for bad in ('"x"', "null", "true", "0", "70000", "-1"):
        (tmp_path / "state" / "server.json").write_text(
            '{"port": %s}' % bad, encoding="utf-8")
        assert open_today.server_url(str(tmp_path), timeout=0.05) is None, bad


def test_a_foreign_responder_on_the_port_is_not_treated_as_the_college(monkeypatch,
                                                                      tmp_path):
    """A stale server.json plus a reused port would otherwise open an unrelated
    local app. serve.py names itself in the Server header; require it."""
    class FakeResp:
        status = 200
        headers = {"Server": "SomeOtherApp/1.0"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "server.json").write_text('{"port": 8787}', encoding="utf-8")
    monkeypatch.setattr(open_today, "urlopen", lambda *a, **k: FakeResp())
    assert open_today.server_url(str(tmp_path)) is None


def test_our_own_server_is_accepted(monkeypatch, tmp_path):
    class FakeResp:
        status = 200
        headers = {"Server": "NexusCollege Python/3.13"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "server.json").write_text('{"port": 8787}', encoding="utf-8")
    monkeypatch.setattr(open_today, "urlopen", lambda *a, **k: FakeResp())
    assert open_today.server_url(str(tmp_path)) == "http://127.0.0.1:8787/"


def test_a_non_object_server_json_returns_none_rather_than_raising(tmp_path):
    """`[]`, `null` and `1` are valid JSON; subscripting them raises TypeError,
    which was not in the caught tuple, so the fallback never ran."""
    (tmp_path / "state").mkdir()
    for content in ("[]", "null", "1", '"a string"', "{}"):
        (tmp_path / "state" / "server.json").write_text(content, encoding="utf-8")
        assert open_today.server_url(str(tmp_path), timeout=0.05) is None, content


def test_yesterdays_page_is_retracted_not_opened(tmp_path):
    """The whole finding: nothing rewrites dashboard/today.html when the task
    never fires, so yesterday's complete, plausible page -- carrying the
    healthy banner it rendered yesterday -- would be opened as today's."""
    built_today(tmp_path)
    (tmp_path / "state" / "last-daily-run.json").write_text(
        json.dumps({"date": "2020-01-01", "outcome": "built"}), encoding="utf-8")
    (tmp_path / "dashboard" / "today.html").write_text(
        "<h1>Yesterday</h1>", encoding="utf-8")

    url = open_today.target(str(tmp_path))

    page = (tmp_path / "dashboard" / "today.html").read_text(encoding="utf-8")
    assert url.startswith("file:///")
    assert "Yesterday" not in page
    assert "2020-01-01" in page, "say when it last ran"


def test_a_failed_run_today_is_not_treated_as_a_built_day():
    """A heartbeat dated today is not evidence of health; the outcome is."""
    import tempfile
    import pathlib as pl

    with tempfile.TemporaryDirectory() as tmp:
        root = pl.Path(tmp)
        built_today(root)
        (root / "state" / "last-daily-run.json").write_text(
            json.dumps({"date": date.today().isoformat(), "outcome": "failed"}),
            encoding="utf-8")
        healthy, detail = open_today.heartbeat_verdict(
            str(root), date.today().isoformat())
        assert healthy is False
        assert "failed" in detail


def test_a_non_object_heartbeat_does_not_crash_the_opener():
    import tempfile
    import pathlib as pl

    with tempfile.TemporaryDirectory() as tmp:
        root = pl.Path(tmp)
        (root / "state").mkdir()
        (root / "state" / "last-daily-run.json").write_text("[]", encoding="utf-8")
        healthy, detail = open_today.heartbeat_verdict(
            str(root), date.today().isoformat())
        assert healthy is False and detail


def test_a_repo_path_containing_a_hash_produces_a_usable_url(tmp_path):
    r"""'C:\Work\Math#Stats' is a valid Windows path. Concatenating it after
    'file:///' makes everything from the '#' a fragment, so the browser opens
    the parent folder instead of the page."""
    root = tmp_path / "Math#Stats"
    root.mkdir()
    built_today(root)
    url = open_today.target(str(root))
    assert "%23" in url
    assert url.endswith("today.html")
