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
import sys
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SERVER_STATE = "state/server.json"
STATIC_PAGE = "dashboard/today.html"


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
    except (URLError, OSError):
        pass
    return None


def target(repo_root):
    """Where 'today' is right now: the server if live, else the page on disk."""
    live = server_url(repo_root)
    if live:
        return live
    static = os.path.join(repo_root, STATIC_PAGE)
    if os.path.exists(static):
        return "file:///" + static.replace(os.sep, "/")
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
