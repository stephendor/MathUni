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

    def start_unit(uid):
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
    real_read, real_write = srv.read_json, srv.write_atomic
    srv.read_json = lambda path, default=None: dict(progress)
    srv.write_atomic = lambda path, text: written.update(json.loads(text))
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
