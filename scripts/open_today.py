"""open_today.py — open today's study day, wherever it currently lives.

This exists for two reasons, and the second one is not obvious.

The obvious one: clicking "Nexus College" in the Start Menu should open today,
and "today" is the live server when it is up and the static page when it is not.
That decision needs three lines of logic, which a shortcut cannot carry.

The non-obvious one: the Start Menu shortcut is what registers the toast
AppUserModelID with Windows, and Windows only indexes a shortcut as an app when
it points at an ordinary executable. Pointing it at the HTML page failed (a
document is not an app). Pointing it at explorer.exe failed too — Windows
excludes its own shell binaries from the app list. Both times the AUMID never
resolved, and a toast from an unresolved AUMID is filed into the Action Center
WITHOUT a banner: delivered, recorded, and invisible. So the shortcut needs a
real executable to name, and this script is what makes pythonw.exe the honest
answer rather than a decoy.

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
            port = json.load(f)["port"]
    except (OSError, ValueError, KeyError):
        return None
    base = "http://127.0.0.1:%d" % port
    try:
        with urlopen(base + "/healthz", timeout=timeout) as resp:
            if resp.status == 200:
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
