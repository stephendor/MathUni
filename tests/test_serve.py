import json

from scripts.serve import Context, route, valid_host

UNITS = [
    {"id": "pw-02", "module": "pw", "title": "Induction", "prereqs": [],
     "hook": "Dominoes.", "mission_link": "m", "resources": []},
    {"id": "la-02", "module": "la", "title": "Subspaces", "prereqs": [],
     "hook": "Hook la.", "mission_link": "m", "resources": []},
]

TOKEN = "test-token-abc"
PLAN = {"date": "2026-08-31", "rest_day": False, "due_count": 12,
        "review_target": 12, "streak": {"current": 3, "best": 3},
        "lectures": [{"id": "pw-02", "module": "pw", "title": "Induction",
                      "module_title": "Proof", "hook": "Dominoes.",
                      "status": "unlocked",
                      "lesson_path": "lessons/pw/pw-02.html"}],
        "problem_candidates": ["pw-02"]}


def ctx(**over):
    calls = {"started": [], "rated": []}

    def start_unit(uid, module=None):
        calls["started"].append(uid)
        return True

    def rate_card(cid, rating):
        calls["rated"].append((cid, rating))
        return {"id": cid, "due": "2026-09-05"}

    base = dict(
        token=TOKEN, port=8787, units=UNITS,
        load_plan=lambda: PLAN,
        load_progress=lambda: {"pw-02": {"status": "unlocked"}},
        load_heartbeat=lambda: {"date": "2026-08-31", "outcome": "built"},
        read_lesson=lambda path: b"<html>lesson</html>",
        start_unit=start_unit,
        rate_card=rate_card,
        build_dashboard=lambda: b"<html>dash</html>",
        home_page=lambda: b"<html>home</html>",
        review_page=lambda: b"<html>review</html>",
    )
    base.update(over)
    c = Context(**base)
    c.calls = calls
    return c


def get(path, query=None, c=None, method="GET", body=None):
    return route(method, path, query or {}, body, c or ctx())


# --- Host header ------------------------------------------------------------

def test_localhost_hosts_accepted():
    for host in ("127.0.0.1:8787", "localhost:8787", "127.0.0.1", "[::1]:8787"):
        assert valid_host(host, 8787) is True, host


def test_foreign_host_header_rejected():
    """DNS rebinding: a page on evil.com resolving to 127.0.0.1 would otherwise
    reach this server with the browser happily attaching to localhost."""
    for host in ("evil.com", "evil.com:8787", "192.168.1.9:8787", ""):
        assert valid_host(host, 8787) is False, host


# --- basic routing ----------------------------------------------------------

def test_healthz_reports_ok():
    r = get("/healthz")
    assert r.status == 200
    assert json.loads(r.body)["ok"] is True


def test_unknown_path_is_404():
    assert get("/nope").status == 404


def test_api_state_returns_plan_and_heartbeat():
    r = get("/api/state")
    assert r.status == 200
    payload = json.loads(r.body)
    assert payload["plan"]["date"] == "2026-08-31"
    assert payload["heartbeat"]["outcome"] == "built"


# --- lesson serving is read-only and whitelisted ----------------------------

def test_known_lesson_is_served():
    r = get("/lesson/pw-02")
    assert r.status == 200 and b"lesson" in r.body


def test_unknown_unit_is_404_not_a_file_read():
    reads = []
    c = ctx(read_lesson=lambda p: reads.append(p) or b"x")
    assert get("/lesson/nope-99", c=c).status == 404
    assert reads == [], "an unknown unit must never reach the filesystem"


def test_path_traversal_cannot_escape_the_lesson_tree():
    """Unit ids are matched against the syllabus, never joined into a path.

    A whitelist is the reason traversal is impossible here; there is no
    sanitising step that could be got wrong.
    """
    reads = []
    c = ctx(read_lesson=lambda p: reads.append(p) or b"x")
    for evil in ("../../etc/passwd", "..%2f..%2fsecrets", "pw-02/../../../x",
                 "....//pw-02"):
        assert get("/lesson/" + evil, c=c).status == 404, evil
    assert reads == []


def test_serving_a_lesson_does_not_change_state():
    c = ctx()
    get("/lesson/pw-02", c=c)
    assert c.calls["started"] == [], "GET /lesson must be read-only"


# --- /open mutates, so it is token-guarded ----------------------------------

def test_open_without_token_is_403():
    c = ctx()
    assert get("/open/pw-02", c=c).status == 403
    assert c.calls["started"] == []


def test_open_with_wrong_token_is_403():
    c = ctx()
    assert get("/open/pw-02", {"t": ["wrong"]}, c=c).status == 403
    assert c.calls["started"] == []


def test_open_with_token_marks_in_progress_and_redirects():
    c = ctx()
    r = get("/open/pw-02", {"t": [TOKEN]}, c=c)
    assert r.status == 302
    assert r.headers["Location"] == "/lesson/pw-02"
    assert c.calls["started"] == ["pw-02"]


def test_open_unknown_unit_is_404_even_with_a_valid_token():
    c = ctx()
    assert get("/open/nope-99", {"t": [TOKEN]}, c=c).status == 404
    assert c.calls["started"] == []


# --- SRS writeback ----------------------------------------------------------

def test_rate_requires_the_token():
    c = ctx()
    r = get("/api/rate", method="POST", c=c,
            body=json.dumps({"card": "pw-01-c01", "rating": 3}).encode())
    assert r.status == 403
    assert c.calls["rated"] == []


def test_rate_with_token_writes_through_to_the_scheduler():
    c = ctx()
    r = get("/api/rate", {"t": [TOKEN]}, method="POST", c=c,
            body=json.dumps({"card": "pw-01-c01", "rating": 3}).encode())
    assert r.status == 200
    assert c.calls["rated"] == [("pw-01-c01", 3)]


def test_rate_rejects_ratings_outside_one_to_four():
    c = ctx()
    for bad in (0, 5, -1, "three", None):
        r = get("/api/rate", {"t": [TOKEN]}, method="POST", c=c,
                body=json.dumps({"card": "x", "rating": bad}).encode())
        assert r.status == 400, bad
    assert c.calls["rated"] == []


def test_rate_rejects_a_malformed_body():
    c = ctx()
    r = get("/api/rate", {"t": [TOKEN]}, method="POST", c=c, body=b"not json")
    assert r.status == 400


def test_rate_is_not_reachable_by_get():
    """A mutating route reachable by GET is one <img src> away from firing."""
    assert get("/api/rate", {"t": [TOKEN]}).status == 405


# --- the no-model property --------------------------------------------------

def test_serve_never_imports_a_model_client():
    """The server opens a socket, so it is not import-identical to daily.py.
    It must still be unable to reach a provider.
    """
    import pathlib

    from tests.test_daily import _import_roots

    src = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "serve.py"
    roots = _import_roots(src.read_text(encoding="utf-8"))
    banned = {"anthropic", "openai", "ollama", "requests", "httpx", "subprocess"}
    assert not (roots & banned)


def test_serve_binds_loopback_only():
    """The bind address is a literal in the source, not a configurable."""
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1] / "scripts" / "serve.py"
           ).read_text(encoding="utf-8")
    assert '"127.0.0.1"' in src
    assert '"0.0.0.0"' not in src


# --- start_unit: the only state this server writes to progress.json ---------

def _run_start_unit(uid, progress):
    """Call start_unit against in-memory progress; return what it would write."""
    import scripts.serve as srv

    written = {}

    def capture(path, text):
        # start_unit also writes learning-records/<unit>.md, which is markdown.
        # Only progress.json is JSON, so only that one is parsed.
        if path.endswith("progress.json"):
            written.update(json.loads(text))

    real_read, real_write = srv.read_json, srv.write_atomic
    srv.read_json = lambda path, default=None: dict(progress)
    srv.write_atomic = capture
    try:
        srv.start_unit(uid)
    finally:
        srv.read_json, srv.write_atomic = real_read, real_write
    return written


def test_opening_an_unlocked_unit_marks_it_in_progress():
    out = _run_start_unit("pw-02", {"pw-02": {"status": "unlocked"}})
    assert out["pw-02"]["status"] == "in-progress"
    assert out["pw-02"]["last_studied"]


def test_in_progress_is_not_disturbed():
    out = _run_start_unit("pw-02", {"pw-02": {"status": "in-progress"}})
    assert out["pw-02"]["status"] == "in-progress"


def test_a_mastered_unit_is_never_demoted_by_reopening_its_lesson():
    """update_unlocks.py owns `mastered`. Re-reading a lesson must not undo it."""
    out = _run_start_unit("pw-01", {"pw-01": {"status": "mastered"}})
    assert out["pw-01"]["status"] == "mastered"


def test_opening_a_locked_unit_neither_unlocks_it_nor_records_study():
    out = _run_start_unit("top-99", {"top-99": {"status": "locked"}})
    assert out["top-99"]["status"] == "locked"
    assert "last_studied" not in out["top-99"], "peeking is not studying"


def test_start_unit_never_writes_the_mastered_status_itself():
    for status in ("locked", "unlocked", "in-progress"):
        out = _run_start_unit("u", {"u": {"status": status}})
        assert out["u"]["status"] != "mastered"


def test_other_units_survive_the_write():
    out = _run_start_unit("pw-02", {"pw-02": {"status": "unlocked"},
                                    "la-02": {"status": "unlocked"}})
    assert out["la-02"] == {"status": "unlocked"}

# --- port occupancy, which binding does not reliably report on Windows ------

def test_port_in_use_sees_a_real_listener():
    """HTTPServer sets SO_REUSEADDR, and on Windows that lets a second process
    bind a port another process is already listening on. Two servers on one
    port -- the newer silently serving stale code from the older -- was an
    observed state, not a hypothetical. Connecting is the test that works.
    """
    import socket

    from scripts.serve import port_in_use

    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]
    try:
        assert port_in_use(port) is True
    finally:
        srv.close()
    # Once closed, the same port must read as free again.
    assert port_in_use(port) is False


def test_port_in_use_is_false_for_a_port_with_nothing_on_it():
    import socket

    from scripts.serve import port_in_use

    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()          # bound then released: nothing is listening
    assert port_in_use(port) is False

# --- the two rendered pages are wired, not placeholders ---------------------

def test_root_serves_the_home_page():
    r = get("/")
    assert r.status == 200 and b"home" in r.body


def test_review_route_serves_the_review_page():
    r = get("/review")
    assert r.status == 200 and b"review" in r.body


def test_neither_page_route_requires_a_token():
    """Reading is not mutating; the token guards writes, not the front door."""
    for path in ("/", "/review"):
        assert get(path).status == 200

# --- surviving pythonw, which hands the process no stdio at all -------------

def test_request_logging_survives_stderr_being_none():
    """The logon task runs serve.py under pythonw.exe, where sys.stderr is None.
    BaseHTTPRequestHandler calls log_request on every send_response, so an
    unguarded write raised inside the handler thread and the server answered
    every request by closing the connection -- listening, and serving nothing.
    """
    import sys

    from scripts.serve import Handler

    class Bare(Handler):
        def __init__(self):           # no socket, no request; only the logger
            pass

    real = sys.stderr
    sys.stderr = None
    try:
        Bare().log_message("%s", "no console here")   # must not raise
    finally:
        sys.stderr = real


def test_attach_stdio_is_a_noop_when_a_console_exists(tmp_path):
    from scripts.serve import _attach_stdio

    target = tmp_path / "server.log"
    _attach_stdio(str(target))
    assert not target.exists(), "must not create a log when stdio already works"


def test_attach_stdio_gives_a_windowless_run_somewhere_to_write(tmp_path):
    import sys

    from scripts.serve import _attach_stdio

    target = tmp_path / "nested" / "server.log"
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = None
    try:
        _attach_stdio(str(target))
        assert sys.stdout is not None and sys.stderr is not None
        sys.stdout.write("hello from pythonw")
        sys.stdout.flush()
    finally:
        try:
            if sys.stdout is not None:
                sys.stdout.close()
        except (OSError, ValueError):
            pass
        sys.stdout, sys.stderr = real_out, real_err
    assert "hello from pythonw" in target.read_text(encoding="utf-8")


# --- the repo invariant CI caught this server breaking ----------------------

def test_marking_in_progress_creates_the_learning_record(tmp_path, monkeypatch):
    """check_id_consistency.py requires learning-records/<unit>.md for every
    in-progress unit. /lecture created it; the server did not, so one toast
    click put the repo in a state its own CI rejects."""
    import scripts.serve as srv

    monkeypatch.chdir(tmp_path)
    (tmp_path / "learning-records").mkdir()
    written = {}
    monkeypatch.setattr(srv, "read_json",
                        lambda path, default=None: {"pw-02": {"status": "unlocked"}})
    real_write = srv.write_atomic
    monkeypatch.setattr(srv, "write_atomic",
                        lambda path, text: written.__setitem__(path, text))
    srv.start_unit("pw-02")
    assert "learning-records/pw-02.md" in written
    assert "No minute paper yet" in written["learning-records/pw-02.md"]
    srv.write_atomic = real_write


def test_no_learning_record_is_created_for_a_locked_unit(tmp_path, monkeypatch):
    """Opening a locked lesson does not make it in-progress, so it must not
    manufacture a record either."""
    import scripts.serve as srv

    monkeypatch.chdir(tmp_path)
    written = {}
    monkeypatch.setattr(srv, "read_json",
                        lambda path, default=None: {"top-99": {"status": "locked"}})
    monkeypatch.setattr(srv, "write_atomic",
                        lambda path, text: written.__setitem__(path, text))
    srv.start_unit("top-99")
    assert not any(k.startswith("learning-records/") for k in written)


def test_an_existing_learning_record_is_never_overwritten(tmp_path, monkeypatch):
    import scripts.serve as srv

    monkeypatch.chdir(tmp_path)
    (tmp_path / "learning-records").mkdir()
    existing = tmp_path / "learning-records" / "pw-02.md"
    existing.write_text("# real minute paper", encoding="utf-8")
    written = {}
    monkeypatch.setattr(srv, "write_atomic",
                        lambda path, text: written.__setitem__(path, text))
    srv.ensure_learning_record("pw-02")
    assert written == {}, "a real record must survive"

# --- the server promotes only what it can keep CI-valid ---------------------

def test_a_unit_without_authored_solutions_is_not_promoted(tmp_path, monkeypatch):
    """check_id_consistency.py requires a lesson, problem set, solutions file AND
    learning record for every in-progress unit. Only 9 of 145 units have the
    first three; the server cannot author solutions and must not invent them, so
    it must not create the state that demands them.
    """
    import scripts.serve as srv

    monkeypatch.chdir(tmp_path)
    written = {}
    monkeypatch.setattr(srv, "read_json",
                        lambda path, default=None: {"pw-03": {"status": "unlocked"}})
    monkeypatch.setattr(srv, "write_atomic",
                        lambda path, text: written.__setitem__(path, text))
    rec = srv.start_unit("pw-03", "pw")
    assert rec["status"] == "unlocked", "must not claim a unit is under way"
    assert written == {}, "and must not write anything at all"


def test_a_fully_authored_unit_is_promoted(tmp_path, monkeypatch):
    import scripts.serve as srv

    monkeypatch.chdir(tmp_path)
    for rel in ("lessons/pw", "problems/sets", "problems/solutions",
                "learning-records"):
        (tmp_path / rel).mkdir(parents=True, exist_ok=True)
    (tmp_path / "lessons" / "pw" / "pw-03.html").write_text("x", encoding="utf-8")
    (tmp_path / "problems" / "sets" / "pw-03.md").write_text("x", encoding="utf-8")
    (tmp_path / "problems" / "solutions" / "pw-03.md").write_text("x", encoding="utf-8")

    written = {}

    def capture(path, text):
        if path.endswith("progress.json"):
            written.update(json.loads(text))

    monkeypatch.setattr(srv, "read_json",
                        lambda path, default=None: {"pw-03": {"status": "unlocked"}})
    monkeypatch.setattr(srv, "write_atomic", capture)
    rec = srv.start_unit("pw-03", "pw")
    assert rec["status"] == "in-progress"
    assert written["pw-03"]["status"] == "in-progress"


def test_missing_artifacts_names_exactly_what_is_absent(tmp_path, monkeypatch):
    import scripts.serve as srv

    monkeypatch.chdir(tmp_path)
    (tmp_path / "lessons" / "pw").mkdir(parents=True)
    (tmp_path / "lessons" / "pw" / "pw-03.html").write_text("x", encoding="utf-8")
    gaps = srv.missing_artifacts("pw-03", "pw")
    assert gaps == ["problems/sets/pw-03.md", "problems/solutions/pw-03.md"]
