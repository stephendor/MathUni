"""open_today.py — open today's study day, wherever it currently lives.

This exists for two reasons, and the second one is not obvious.

The obvious one: clicking "Nexus College" in the Start Menu should open today,
and "today" is the live server when it is up and the static page when it is not.
That decision needs three lines of logic, which a shortcut cannot carry.

The second one: the Start Menu shortcut carries the toast AppUserModelID, and
a shortcut wants a real executable to point at. This script is what makes
pythonw.exe an honest target rather than a decoy chosen only to satisfy the
registration.

That shortcut was, for several rounds, blamed for missing toast banners. It was
not the cause — Do Not Disturb was — and the banners work now. What remains
true, and unexplained, is that this shortcut does not appear in Get-StartApps
and the Start Menu cannot find it by name, while sitting in the same folder as
shortcuts that do. That costs nothing but the convenience of the shortcut
itself.

  python scripts/open_today.py [--print]
"""
import argparse
import json
import os
import pathlib
import sys
import tempfile
import webbrowser
from datetime import date
from http.client import HTTPException
from urllib.error import URLError
from urllib.request import urlopen

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.check_daily_liveness import HEALTHY_OUTCOMES
from scripts.home import render_unbuilt_page

SERVER_STATE = "state/server.json"
STATIC_PAGE = "dashboard/today.html"
HEARTBEAT = "state/last-daily-run.json"


def server_url(repo_root, timeout=1.0):
    """The live server's URL, or None. Asks it, rather than trusting the file.

    A dead process leaves state/server.json behind, so its existence proves
    nothing; /healthz answering is what proves something.
    """
    path = os.path.join(repo_root, SERVER_STATE)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8-sig") as f:
            record = json.load(f)
    except (OSError, ValueError):
        return None
    # `[]`, `null` and `1` are all valid JSON. Indexing them raises TypeError,
    # which is not in the tuple above, so the record's shape is checked before
    # it is subscripted rather than after.
    if not isinstance(record, dict):
        return None
    port = record.get("port")
    # A string port would raise TypeError on the %d below, which is outside the
    # try above, so a corrupt file would crash rather than fall back to the page.
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        return None
    base = "http://127.0.0.1:%d" % port
    try:
        with urlopen(base + "/healthz", timeout=timeout) as resp:
            # 200 alone is not enough. The port may have been reused by an
            # unrelated local process since this file was written, and opening
            # someone else's app is worse than falling back to the page.
            # serve.py names itself in the Server header; ask for that.
            if resp.status == 200 and "NexusCollege" in resp.headers.get("Server", ""):
                return base + "/"
    except (URLError, OSError, HTTPException):
        # HTTPException is NOT an OSError. A reused port answering with a
        # malformed status line raises BadStatusLine, which without this
        # would crash the Start Menu shortcut instead of falling back to
        # the offline page -- the one job this function has.
        pass
    return None


def heartbeat_verdict(repo_root, today):
    """(is today's build healthy, why not) — read straight from the heartbeat.

    Kept local rather than calling check_daily_liveness so that this stays a
    file read and a comparison. This runs from a Start Menu shortcut under
    pythonw.exe with no console; the fewer moving parts between the click and
    a page, the better.
    """
    try:
        with open(os.path.join(repo_root, HEARTBEAT), encoding="utf-8-sig") as f:
            beat = json.load(f)
    except (OSError, ValueError):
        return False, "No heartbeat has been written at all."
    if not isinstance(beat, dict):
        return False, "The heartbeat file does not contain a record."
    if beat.get("date") != today:
        return False, ("The last recorded run was %s."
                       % (beat.get("date") or "never"))
    if beat.get("outcome") not in HEALTHY_OUTCOMES:
        return False, ("It ran today and reported outcome %s."
                       % (beat.get("outcome") or "nothing"))
    return True, ""


def _write(path, text):
    """Atomic enough: write beside the target, then replace."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline=chr(10)) as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def target(repo_root, today=None):
    """Where 'today' is right now: the server if live, else the page on disk.

    The page on disk is only today's page if a run today wrote it. Nothing
    rewrites dashboard/today.html when the scheduled task never fires, so
    "the file exists" is not the question -- yesterday's page is complete,
    plausible, and carries the healthy banner it rendered yesterday. Opening
    that would offer yesterday's lectures as today's work, which is the exact
    silent-wrong-answer this loop exists to remove.

    So: when the heartbeat does not vouch for today, the stale artifact is
    replaced with a page that says so. That is a write from what is otherwise
    a read-only opener, including under --print, and it is deliberate --
    printing a URL that leads somewhere dishonest is not an improvement.
    """
    live = server_url(repo_root)
    if live:
        return live

    static = os.path.join(repo_root, STATIC_PAGE)
    healthy, detail = heartbeat_verdict(repo_root, today or date.today().isoformat())
    if not healthy:
        try:
            _write(static, render_unbuilt_page(
                today or date.today().isoformat(), detail))
        except OSError:
            # Could not retract it. An honest stale page beats no page, but
            # only just; say so on stderr for whoever is watching.
            sys.stderr.write("open_today: could not rewrite %s; the page it "
                             "opens may be out of date%s" % (STATIC_PAGE, chr(10)))
    if os.path.exists(static):
        # as_uri(), not "file:///" + path: a repo under a directory containing
        # '#' or '%' produces a URL whose tail the browser reads as a fragment,
        # and the fallback opens the parent folder instead of the page.
        return pathlib.Path(static).resolve().as_uri()
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Open today's study day.")
    ap.add_argument("--print", dest="show", action="store_true",
                    help="print the URL instead of opening it")
    args = ap.parse_args(argv)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url = target(repo_root)
    if url is None:
        # Nothing to open is not a crash, but it is not success either.
        sys.stderr.write("open_today: no server and no dashboard/today.html; "
                         "run `python scripts/daily.py` first\n")
        return 2
    if args.show:
        print(url)
        return 0
    webbrowser.open(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
