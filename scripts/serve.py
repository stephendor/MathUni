"""serve.py — the persistent local surface for the college.

The daily loop needed somewhere to land. A notification can only carry one
line of text, and a `file://` page can read the lesson corpus but cannot write
a single SRS rating back to disk. This server is the missing half: a stdlib
HTTP server, bound to loopback, that turns the state under `state/` and the
146 self-contained lessons under `lessons/` into something clickable, and
accepts the writes that come back.

No model is involved, here or anywhere it calls. It opens a socket, which is
the one thing scripts/daily.py deliberately does not do, so the two are not
import-identical; what they share is that neither can reach a provider and
neither can fail because a provider is unavailable.

Security posture, because this is an unauthenticated write API sitting in a
browser's reach:

  * Bound to 127.0.0.1 only. Never 0.0.0.0 — that would put the college on
    the local network.
  * Host header must name loopback. Without this check, a page on a domain
    the attacker controls can resolve that domain to 127.0.0.1 and drive this
    server from the victim's own browser (DNS rebinding); same-origin policy
    does not help, because to the browser the origin really is that domain.
  * Every route that changes state requires the per-run token from
    state/server.json, compared with secrets.compare_digest. The token is
    what makes a cross-site request unguessable rather than merely awkward.
  * Unit ids are matched against the syllabus, never joined into a path. A
    whitelist is why traversal is impossible here; there is no sanitiser that
    could be got wrong.

The token travels in the query string on /open, which is what lets a Windows
toast button reach it: protocol activation can only issue a GET. That puts the
token in browser history, which is an acceptable trade for a loopback-only
study app and would not be outside one.

  python scripts/serve.py [--port N] [--once]
"""
import argparse
import json
import os
import secrets
import socket
import sys
import urllib.request
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.build_dashboard import render as render_dashboard
from scripts.daily import read_json, write_atomic
from scripts.home import ServerLinks, build_view, render_home
from scripts.review import REVIEW_CAP, build_queue, render_review
from scripts.validate_syllabus import load_syllabus
from srs.scheduler import (
    due_cards,
    engram_banner,
    engram_ready,
    load_config,
    load_deck,
    rate_and_save,
)

BIND = "127.0.0.1"
DEFAULT_PORT = 8787
PORT_SCAN = 20
SERVER_STATE = "state/server.json"
SERVER_LOG = "state/server.log"

LOOPBACK_NAMES = ("127.0.0.1", "localhost", "::1")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    # The review page carries the write token in its own markup, so a page that
    # can frame it can read it. Nothing here is ever meant to be embedded.
    "Content-Security-Policy": "frame-ancestors 'none'",
    "X-Frame-Options": "DENY",
}


class Response:
    def __init__(self, status, body=b"", content_type="text/html; charset=utf-8",
                 headers=None):
        self.status = status
        self.body = body if isinstance(body, bytes) else str(body).encode("utf-8")
        self.content_type = content_type
        self.headers = dict(headers or {})


class Context:
    """Everything a route needs, injected so routing is testable without sockets."""

    def __init__(self, token, port, units, load_plan, load_progress, load_heartbeat,
                 read_lesson, start_unit, rate_card, build_dashboard,
                 home_page=None, review_page=None):
        self.token = token
        self.port = port
        self.units = units
        self.load_plan = load_plan
        self.load_progress = load_progress
        self.load_heartbeat = load_heartbeat
        self.read_lesson = read_lesson
        self.start_unit = start_unit
        self.rate_card = rate_card
        self.build_dashboard = build_dashboard
        self.home_page = home_page or (lambda: b"")
        self.review_page = review_page or (lambda: b"")


def valid_host(host_header, port):
    """True only when the Host header names loopback (and the right port)."""
    if not host_header:
        return False
    h = host_header.strip()
    if h.startswith("["):                       # [::1] or [::1]:8787
        end = h.find("]")
        if end == -1:
            return False
        name, rest = h[1:end], h[end + 1:]
        if rest and not rest.startswith(":"):
            return False
        given_port = rest[1:] if rest else ""
    elif h.count(":") == 1:
        name, given_port = h.rsplit(":", 1)
    elif ":" in h:
        return False                            # bare IPv6, no brackets
    else:
        name, given_port = h, ""
    if name.lower() not in LOOPBACK_NAMES:
        return False
    return not given_port or given_port == str(port)


def lesson_path(unit):
    return "lessons/%s/%s.html" % (unit["module"], unit["id"])


def _json(status, obj):
    return Response(status, json.dumps(obj, ensure_ascii=False, indent=1),
                    "application/json; charset=utf-8")


def _authed(query, ctx):
    given = (query.get("t") or [""])[0] or ""
    return secrets.compare_digest(given, ctx.token)


def _lookup_unit(raw, ctx):
    """Resolve a unit id against the syllabus. Anything unknown is a 404.

    This is the only way a request-supplied string becomes a filesystem path,
    and it cannot: the path is rebuilt from the syllabus entry that matched.
    """
    return next((u for u in ctx.units if u["id"] == raw), None)


def route(method, path, query, body, ctx):
    if path == "/healthz":
        return _json(200, {"ok": True, "date": date.today().isoformat(),
                           "port": ctx.port})

    if path == "/api/state":
        return _json(200, {"plan": ctx.load_plan(),
                           "progress": ctx.load_progress(),
                           "heartbeat": ctx.load_heartbeat()})

    if path == "/api/rate":
        # A mutating route reachable by GET is one <img src> away from firing.
        if method != "POST":
            return _json(405, {"error": "POST only"})
        if not _authed(query, ctx):
            return _json(403, {"error": "bad or missing token"})
        try:
            payload = json.loads((body or b"").decode("utf-8"))
            cid, rating = payload["card"], payload["rating"]
        except (AttributeError, KeyError, UnicodeDecodeError, ValueError):
            return _json(400, {"error": "malformed body"})
        # bool is a subclass of int; True would otherwise pass as rating 1.
        if isinstance(rating, bool) or not isinstance(rating, int) \
                or not 1 <= rating <= 4:
            return _json(400, {"error": "rating must be an integer 1-4"})
        card = ctx.rate_card(cid, rating)
        if card is None:
            return _json(404, {"error": "no such card"})
        return _json(200, {"card": card})

    if path.startswith("/lesson/"):
        unit = _lookup_unit(path[len("/lesson/"):], ctx)
        if unit is None:
            return _json(404, {"error": "unknown unit"})
        return Response(200, ctx.read_lesson(lesson_path(unit)))

    if path.startswith("/open/"):
        if not _authed(query, ctx):
            return _json(403, {"error": "bad or missing token"})
        unit = _lookup_unit(path[len("/open/"):], ctx)
        if unit is None:
            return _json(404, {"error": "unknown unit"})
        ctx.start_unit(unit["id"])
        return Response(302, b"", headers={"Location": "/lesson/%s" % unit["id"]})

    if path == "/dashboard":
        return Response(200, ctx.build_dashboard())

    if path == "/":
        return Response(200, ctx.home_page())

    if path == "/review":
        return Response(200, ctx.review_page())

    return _json(404, {"error": "not found"})


# --- real wiring ------------------------------------------------------------

def start_unit(uid):
    """Mark a unit in-progress when its lesson is actually opened.

    Only unlocked -> in-progress, mirroring .claude/skills/lecture/SKILL.md.
    Never demotes, and never writes `mastered`: scripts/update_unlocks.py is
    the only path to that, and a second writer would be a second opinion.
    """
    progress = read_json("state/progress.json")
    rec = dict(progress.get(uid, {"status": "locked"}))
    status = rec.get("status")
    if status == "unlocked":
        rec["status"] = "in-progress"
    if status in ("unlocked", "in-progress", "mastered"):
        # A locked unit can still be opened (the lecture skill warns rather than
        # blocks), but peeking at one is not studying it and must not be recorded
        # as though it were.
        rec["last_studied"] = date.today().isoformat()
    progress[uid] = rec
    write_atomic("state/progress.json", json.dumps(progress, indent=2) + "\n")
    return rec


def rate_card(cid, rating):
    # rate_and_save, not load_deck + apply_rating: this server is threaded, and
    # two overlapping ratings on separately-loaded snapshots lose one of them
    # while telling both clients it worked.
    return rate_and_save(load_config(), cid, rating, date.today().isoformat())


def read_lesson(path):
    with open(path, "rb") as f:
        return f.read()


def real_context(token, port):
    syllabus = load_syllabus("curriculum/syllabus.yaml")

    def dashboard():
        # The same renderer /status uses, so the two cannot drift.
        return render_dashboard(syllabus, read_json("state/progress.json"),
                                read_json("state/streaks.json")).encode("utf-8")

    def home_page():
        # live_due comes from the deck, not the morning snapshot: after a review
        # session the plan still says every card is due, and a front door that
        # contradicts the page you just used is worse than no counter.
        today = date.today().isoformat()
        try:
            live_due = len(due_cards(load_deck(), today))
        except (OSError, ValueError, KeyError):
            live_due = None     # unreadable deck: fall back to the snapshot
        return render_home(
            build_view(read_json("state/today.json"),
                       read_json("state/progress.json"), syllabus,
                       read_json("state/streaks.json"),
                       read_json("state/last-daily-run.json"),
                       today, live_due=live_due),
            ServerLinks(token)).encode("utf-8")

    def review_page():
        deck, cfg = load_deck(), load_config()
        due = due_cards(deck, date.today().isoformat())
        cap = (read_json("state/today.json") or {}).get("review_cap") or REVIEW_CAP
        # The engram trip-wire fires on the CLI review path via stderr. Routing
        # review through a page would have silently retired it; the review skill
        # says relay one line, so one line is relayed.
        notice = (engram_banner(deck, cfg).split(chr(10))[0]
                  if engram_ready(deck, cfg) else None)
        return render_review(build_queue(due, cap), token, len(due),
                             notice).encode("utf-8")

    return Context(
        token=token, port=port, units=syllabus.get("units", []),
        # Loaded per request, not once at boot: this process is meant to stay
        # up for days, and daily.py rewrites the plan underneath it each morning.
        load_plan=lambda: read_json("state/today.json"),
        load_progress=lambda: read_json("state/progress.json"),
        load_heartbeat=lambda: read_json("state/last-daily-run.json"),
        read_lesson=read_lesson, start_unit=start_unit, rate_card=rate_card,
        build_dashboard=dashboard, home_page=home_page,
        review_page=review_page)


class Handler(BaseHTTPRequestHandler):
    server_version = "NexusCollege"
    ctx = None

    def _dispatch(self, method):
        if not valid_host(self.headers.get("Host", ""), self.ctx.port):
            self._emit(Response(403, b"forbidden", "text/plain; charset=utf-8"))
            return
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        try:
            resp = route(method, parsed.path, parse_qs(parsed.query), body, self.ctx)
        except Exception as exc:                    # noqa: BLE001 - never die on one bad request
            self.log_error("route %s %s: %s", method, parsed.path, exc)
            resp = _json(500, {"error": "internal error"})
        self._emit(resp)

    def _emit(self, resp):
        self.send_response(resp.status)
        self.send_header("Content-Type", resp.content_type)
        self.send_header("Content-Length", str(len(resp.body)))
        for k, v in {**SECURITY_HEADERS, **resp.headers}.items():
            self.send_header(k, v)
        self.end_headers()
        if resp.body:
            self.wfile.write(resp.body)

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def log_message(self, fmt, *args):
        # Under pythonw.exe -- which is how the logon task runs this --
        # sys.stderr is None. BaseHTTPRequestHandler calls log_request on
        # every send_response, so an unguarded write raised inside the handler
        # thread and the server answered every request by closing the
        # connection: it listened, and served nothing.
        stream = sys.stderr
        if stream is None:
            return
        try:
            stream.write("%s %s\n" % (self.log_date_time_string(),
                                              fmt % args))
        except (OSError, ValueError):
            pass


def port_in_use(port, host=BIND, timeout=0.35):
    """True when something is already accepting connections on `port`.

    Binding is not a reliable occupancy test on Windows. HTTPServer sets
    allow_reuse_address, which maps to SO_REUSEADDR, and Windows lets a SECOND
    process bind a port another process is already listening on -- the bind
    succeeds, and connections are then delivered to whichever socket the stack
    picks. Two servers on one port, the newer one silently serving stale code
    from the older, is a state this was observed in during Phase 3.

    Connecting says what binding cannot: is anyone actually there.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def bind_server(port):
    """First genuinely free port from `port` upward."""
    last = None
    for candidate in range(port, port + PORT_SCAN):
        if port_in_use(candidate):
            last = "port %d already has a listener" % candidate
            continue
        try:
            return ThreadingHTTPServer((BIND, candidate), Handler)
        except OSError as exc:
            last = exc
    raise SystemExit("serve.py: no free port in %d-%d (%s)"
                     % (port, port + PORT_SCAN - 1, last))


def _is_our_server(port, host=BIND):
    """Distinguish our own server from an unrelated process on the same port.

    The Server header is set from Handler.server_version, so this asks the
    listener who it is rather than assuming the port implies the program.
    """
    try:
        url = "http://%s:%d/healthz" % (host, port)
        with urllib.request.urlopen(url, timeout=0.5) as resp:
            return "NexusCollege" in resp.headers.get("Server", "")
    except OSError:
        # urllib.error.HTTPError subclasses OSError, so a live-but-unhappy
        # server lands here too, and is correctly treated as not ours.
        return False


def _attach_stdio(path=SERVER_LOG):
    """Point stdout/stderr at a file when there is no console.

    pythonw.exe leaves both as None. Every print in this module would then
    raise, and the failure would be invisible -- the shape of bug this whole
    loop exists to stamp out. A windowless server that cannot be diagnosed
    is only marginally better than one that lies.
    """
    if sys.stdout is not None and sys.stderr is not None:
        return
    handle = None
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        handle = open(path, "a", encoding="utf-8", newline="\n", buffering=1)
    except OSError:
        pass
    if sys.stdout is None:
        sys.stdout = handle
    if sys.stderr is None:
        sys.stderr = handle


def main(argv=None):
    ap = argparse.ArgumentParser(description="Local college surface (no model).")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--once", action="store_true",
                    help="serve a single request and exit (smoke test)")
    args = ap.parse_args(argv)

    if not os.path.exists("curriculum/syllabus.yaml"):
        print("serve.py: run from the repo root", file=sys.stderr)
        return 2

    # A logon-triggered service can fire more than once; starting a second
    # college on top of the first is worse than doing nothing.
    if port_in_use(args.port) and _is_our_server(args.port):
        print("already running on http://%s:%d/" % (BIND, args.port))
        return 0

    _attach_stdio()

    httpd = bind_server(args.port)
    port = httpd.server_address[1]
    token = secrets.token_urlsafe(24)
    Handler.ctx = real_context(token, port)
    write_atomic(SERVER_STATE, json.dumps(
        {"port": port, "token": token, "pid": os.getpid(),
         "started": date.today().isoformat(), "url": "http://%s:%d/" % (BIND, port)},
        indent=2) + "\n")
    print("http://%s:%d/  (token in %s)" % (BIND, port, SERVER_STATE))
    try:
        httpd.handle_request() if args.once else httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
