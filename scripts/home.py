"""home.py — the front door: today's plan as a page.

One renderer, two link modes. The server calls it for `GET /` and gets
`/open/<unit>?t=…` links that mark a unit in-progress on the way through;
daily.py calls it each morning and writes `dashboard/today.html`, which links
straight at the lesson files so the page still works when the server is down.
That fallback is the point of splitting this out of serve.py: the plan doc's
rule is that the toast is best-effort and the page is the contract, and a
contract that only holds while a process is up is not one.

It lives in its own module rather than inside serve.py because daily.py must
be able to import it, and daily.py may not import `http` — see the Tier-0
import guard in tests/test_daily.py, which walks this file too.

Rendering is split from deciding: `build_view` computes what the page says
(segments, stale units, module bars, liveness) and is what the tests assert
against; `render_home` only turns that into HTML.

Palette and type match lessons/*.html and dashboard/index.html deliberately —
this is the same college, and a front door in a different visual language
reads as a different application.
"""
from datetime import date
from html import escape

from scripts import mathdoc

from scripts.check_daily_liveness import HEALTHY_OUTCOMES

STALE_DAYS = 7          # an in-progress unit older than this gets a gentle offer
REVIEW_CAP = 15         # fallback when the plan predates the capped queue

# The one place the college's colours are written down. review.py imports it
# rather than restating it: two pages of the same application quietly drifting
# apart in palette is the cheapest kind of divergence to prevent.
PALETTE = """
:root{--bg:#101418;--panel:#1a2027;--ink:#e8e8e8;--dim:#9aa5b1;--acc:#8ab4f8;
--good:#4caf82;--warm:#d8a657;--bad:#e06c75;--line:#2a333d}
"""

CSS = PALETTE + """
*{box-sizing:border-box}
body{font-family:Georgia,serif;background:var(--bg);color:var(--ink);
max-width:54rem;margin:0 auto;padding:2rem 1.2rem 4rem;line-height:1.6;font-size:1.02rem}
h1,h2,h3,.ui{font-family:Segoe UI,system-ui,sans-serif}
a{color:var(--acc)}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:.9rem;
border-bottom:1px solid var(--line);padding-bottom:.9rem;margin-bottom:1.6rem}
header h1{font-size:1.35rem;margin:0;font-weight:600}
header .meta{color:var(--dim);font-size:.9rem;font-family:Segoe UI,system-ui,sans-serif}
header .streak{margin-left:auto;font-family:Segoe UI,system-ui,sans-serif;font-size:.9rem}
.banner{background:#2a1d1d;border-left:4px solid var(--bad);border-radius:10px;
padding:.9rem 1.1rem;margin-bottom:1.6rem;font-family:Segoe UI,system-ui,sans-serif;font-size:.92rem}
.banner b{color:var(--bad)}
.hook{background:linear-gradient(135deg,#1a2340,#1a2027);border-left:4px solid var(--acc);
padding:1.4rem 1.5rem;border-radius:12px;font-size:1.2rem;margin:0 0 1.2rem}
.hook .lead{color:var(--dim);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;
font-family:Segoe UI,system-ui,sans-serif;margin-bottom:.5rem}
.btn{display:inline-block;background:var(--acc);color:#0c1013;text-decoration:none;
font-family:Segoe UI,system-ui,sans-serif;font-weight:600;font-size:.95rem;
border-radius:8px;padding:.6rem 1.1rem;margin:.9rem .5rem 0 0}
.btn.ghost{background:transparent;color:var(--acc);border:1px solid #33414f}
h2{font-size:.82rem;text-transform:uppercase;letter-spacing:.07em;color:var(--acc);
margin:2.2rem 0 .8rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:.9rem}
.card{background:var(--panel);border-radius:12px;padding:1rem 1.1rem;
border:1px solid transparent}
.card .kind{font-family:Segoe UI,system-ui,sans-serif;font-size:.72rem;letter-spacing:.08em;
text-transform:uppercase;color:var(--dim)}
.card .title{font-weight:600;margin:.35rem 0 .3rem}
.card .note{color:var(--dim);font-size:.9rem}
.card.lecture{border-color:#25334a}.card.review{border-color:#24382c}
.card.problems{border-color:#3a3220}
.card a.go{display:inline-block;margin-top:.7rem;font-family:Segoe UI,system-ui,sans-serif;
font-size:.9rem;text-decoration:none}
.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.5rem}
.chip{background:#26313c;border-radius:999px;padding:.2rem .7rem;font-size:.82rem;
font-family:Segoe UI,system-ui,sans-serif;color:var(--ink);text-decoration:none}
.stale{background:#1d1c16;border-left:4px solid var(--warm);border-radius:10px;
padding:.9rem 1.1rem;font-size:.93rem}
.mods{display:grid;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));gap:.7rem 1.4rem}
.mod{font-family:Segoe UI,system-ui,sans-serif;font-size:.88rem}
.bar{background:#232b34;border-radius:6px;height:8px;overflow:hidden;margin-top:.35rem}
.fill{background:var(--good);height:100%}
footer{margin-top:3rem;border-top:1px solid var(--line);padding-top:1rem;
color:var(--dim);font-size:.85rem;font-family:Segoe UI,system-ui,sans-serif}
footer .nav{margin-top:.5rem}
footer .nav a{margin-right:1.1rem}
.rest{background:var(--panel);border-radius:12px;padding:1.3rem 1.4rem;color:var(--dim)}
.rest b{color:var(--ink);font-family:Segoe UI,system-ui,sans-serif}
"""


class ServerLinks:
    """Links for the live server: opening a lesson records that it opened."""

    live = True

    def __init__(self, token):
        # token_urlsafe output needs no percent-encoding, which is why this
        # module can stay clear of urllib (daily.py imports it).
        self.token = token

    def lesson(self, lec):
        return "/open/%s?t=%s" % (lec["id"], self.token)

    def review(self):
        return "/review"

    def problems(self, unit_id):
        return "/problems/%s" % unit_id

    def dashboard(self):
        return "/dashboard"

    def home(self):
        return "/"

    def board(self):
        return "/problems"

    def reference(self):
        return "/reference"

    def nav(self):
        return _nav(self)


class StaticLinks:
    """Links for dashboard/today.html, written to disk and opened as a file.

    Lessons open directly. Nothing that needs a writeback is offered as a live
    link, because it would silently do nothing — the page says so instead.
    """

    live = False

    def lesson(self, lec):
        return "../lessons/%s/%s.html" % (lec["module"], lec["id"])

    def review(self):
        return None

    def problems(self, unit_id):
        # The raw markdown, straight off disk. Browsers show it as plain text;
        # that is what a problem set is, and the server-rendered view is only a
        # nicer frame around the same file.
        return "../problems/sets/%s.md" % unit_id

    def dashboard(self):
        return "index.html"

    def home(self):
        return "today.html"

    def board(self):
        return "problems.html"

    def reference(self):
        return "reference.html"

    def nav(self):
        return _nav(self)


def _nav(links):
    """The footer that makes every surface reachable from every other.

    Written once and shared, because the boards exist precisely so that nothing
    disappears when the day's plan happens to be empty. A rest day owes no work;
    it should not also hide the material.
    """
    items = [("Today", links.home()), ("Problems", links.board()),
             ("Reference", links.reference()), ("Full board", links.dashboard())]
    if links.review():
        items.insert(3, ("Review", links.review()))
    return "".join('<a href="%s">%s</a>' % (escape(href), label)
                   for label, href in items if href)


def _days_since(iso, today):
    if not iso:
        return None
    try:
        return (date.fromisoformat(today) - date.fromisoformat(iso)).days
    except ValueError:
        return None


def build_view(plan, progress, syllabus, streaks, heartbeat, today,
               live_due=None):
    """Everything the page states, decided here so it can be asserted on.

    `live_due` is the CURRENT number of due cards. The plan is a morning
    snapshot: rating cards rewrites srs/deck.json and closing a day rewrites
    state/streaks.json, but neither rewrites the plan, so a served page that
    reads only the snapshot keeps insisting every card you just reviewed is
    still due. The server passes the live count; the static fallback cannot
    know it and passes None, which keeps the snapshot.
    """
    units = {u["id"]: u for u in syllabus.get("units", [])}
    mod_titles = {m["id"]: m.get("title", m["id"]) for m in syllabus.get("modules", [])}
    # `plan or {}` kept a truthy list or string, and the very next line calls
    # .get on it. The server turns that AttributeError into a 500, so a
    # malformed today.json took down the page whose entire job is to still be
    # standing when the state underneath it is wrong.
    plan = plan if isinstance(plan, dict) else {}
    progress = progress if isinstance(progress, dict) else {}
    streaks = streaks if isinstance(streaks, dict) else {}

    # A plan from another day is worse than no plan. state/today.json is only
    # rewritten by a successful build, so when today's build fails yesterday's
    # object is still on disk and the server hands it straight to this
    # function. Rendering it puts yesterday's lectures under today's date, as
    # live links: the liveness banner would warn while the page below it stayed
    # confidently actionable. Discard it and let the page say it has nothing.
    stale_plan = bool(plan) and plan.get("date") != today
    if stale_plan:
        plan = {}

    stale = []
    for uid, rec in sorted(progress.items()):
        if rec.get("status") != "in-progress":
            continue
        days = _days_since(rec.get("last_studied"), today)
        if days is not None and days >= STALE_DAYS:
            stale.append({"id": uid, "days": days,
                          "title": units.get(uid, {}).get("title", uid),
                          "module": units.get(uid, {}).get("module", "")})
    stale.sort(key=lambda s: -s["days"])

    mods = []
    for mid, title in mod_titles.items():
        member = [u for u in units.values() if u["module"] == mid]
        if not member:
            continue
        done = sum(1 for u in member
                   if progress.get(u["id"], {}).get("status") == "mastered")
        if done:  # only modules actually under way; 30 empty bars is noise
            mods.append({"id": mid, "title": title, "done": done,
                         "total": len(member),
                         "pct": int(100 * done / len(member))})
    mods.sort(key=lambda m: (-m["pct"], m["title"]))

    problems = [{"id": uid, "title": units.get(uid, {}).get("title", uid)}
                for uid in plan.get("problem_candidates", [])]

    # Same rule the liveness script applies, imported rather than restated: a
    # heartbeat dated today whose outcome is "failed" is not a healthy day.
    beat = heartbeat if isinstance(heartbeat, dict) else {}
    hb_date = beat.get("date")
    liveness = {"stale": hb_date != today
                         or beat.get("outcome") not in HEALTHY_OUTCOMES,
                "last": hb_date,
                "outcome": beat.get("outcome"),
                "days": _days_since(hb_date, today)}

    # streaks.json is live state, so it wins over the plan's copy of it. The
    # plan's value is only the fallback for a caller that has no streaks file.
    streak = ({"current": streaks.get("current", 0), "best": streaks.get("best", 0)}
              if streaks else plan.get("streak") or {"current": 0, "best": 0})

    due = plan.get("due_count", 0) if live_due is None else live_due
    cap = plan.get("review_cap") or REVIEW_CAP
    target = plan.get("review_target", 0) if live_due is None else min(due, cap)

    return {
        "date": today,
        "rest_day": bool(plan.get("rest_day")),
        "has_plan": bool(plan),
        "hook": (plan.get("lectures") or [{}])[0].get("hook", ""),
        "lectures": plan.get("lectures", []),
        "review": {"due": due, "target": target},
        "problems": problems,
        "streak": streak,
        "stale": stale,
        "modules": mods,
        "liveness": liveness,
        "stale_plan": stale_plan,
        "mastered_total": sum(1 for r in progress.values()
                              if r.get("status") == "mastered"),
        "unit_total": len(units),
    }


def _pretty_date(iso):
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        return iso
    days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday")
    months = ("January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December")
    return "%s %d %s" % (days[d.weekday()], d.day, months[d.month - 1])


def _liveness_banner(view):
    live = view["liveness"]
    if not live["stale"]:
        # A healthy heartbeat with a plan from another day should not happen --
        # daily.py writes both -- but silence is the wrong response if it does.
        if view.get("stale_plan"):
            return ('<div class="banner"><b>Today\'s plan is missing.</b> The '
                    'heartbeat is healthy but the plan on disk is from an '
                    'earlier day, so it has been set aside. Run '
                    '<code>python scripts/daily.py --force</code>.</div>')
        return ""
    if not live["last"]:
        detail = "No day has ever been built."
    elif live["days"] == 0:
        detail = ("It ran today and did not finish (outcome: %s)."
                  % escape(str(live.get("outcome"))))
    elif live["days"] is None:
        # _days_since returns None for an unparseable date, deliberately. This
        # branch used to format that with %d and raise, which took the whole
        # page to a 500 -- the one surface whose job is to survive bad state.
        detail = ("Its last run is dated %s, which is not a date."
                  % escape(str(live["last"])))
    else:
        detail = "Last built %s (%d days ago)." % (escape(live["last"]), live["days"])
    extra = ""
    if view.get("stale_plan"):
        extra = (' The plan still on disk is from an earlier day and has been '
                 'set aside rather than shown, so this page is thin on purpose.')
    return ('<div class="banner"><b>The day builder has not run today.</b> %s%s '
            'Run <code>python scripts/daily.py</code>, or check the scheduled '
            'task.</div>' % (detail, extra))


def _hero(view, links):
    if view["rest_day"]:
        # A rest day owes no work, so problem_candidates is empty and the
        # segment cards below are gone. That is right about the day and wrong
        # about the material: nothing should become unreachable because today
        # happens to be a Wednesday. The boards are named here explicitly.
        return ('<div class="rest"><b>Rest day.</b> Nothing is scheduled, and '
                'nothing is owed. If you want something anyway, it is all still '
                'there: %s, the <a href="%s">problem board</a>, or the '
                '<a href="%s">definitions and theorems</a>.</div>'
                % (_review_link(links, "a few cards"),
                   escape(links.board()), escape(links.reference())))
    if not view["lectures"]:
        return ('<div class="rest"><b>No units are waiting.</b> Everything '
                'unlocked has been studied — grade what is in progress to open '
                'the next layer of the DAG. The <a href="%s">problem board</a> '
                'lists every set either way.</div>' % escape(links.board()))
    first = view["lectures"][0]
    return ('<div class="hook"><div class="lead">Today opens with</div>%s'
            '<div><a class="btn" href="%s">Start %s</a>%s</div></div>'
            % (escape(view["hook"]), links.lesson(first), escape(first["id"]),
               _review_button(view, links)))


def _review_link(links, label):
    href = links.review()
    if href is None:
        return '<span class="note">%s (needs the local server)</span>' % escape(label)
    return '<a href="%s">%s</a>' % (href, escape(label))


def _review_button(view, links):
    # The target, not the raw due count. Showing 66 here would rebuild on the
    # button the exact wall the cap exists to take down.
    href, target = links.review(), view["review"]["target"]
    if href is None or not target:
        return ""
    return '<a class="btn ghost" href="%s">Warm up · %d cards</a>' % (href, target)


def _segment_cards(view, links):
    cards = []
    due, target = view["review"]["due"], view["review"]["target"]
    if due:
        note = ("%d due" % due if due <= target
                else "%d of %d due — oldest first, the rest keep" % (target, due))
        cards.append(
            '<div class="card review"><div class="kind">Warm-up · ~10 min</div>'
            '<div class="title">Retrieval</div><div class="note">%s</div>%s</div>'
            % (note, _go(links.review(), "Start review")))
    for n, lec in enumerate(view["lectures"], 1):
        cards.append(
            '<div class="card lecture"><div class="kind">Lecture %d · %s</div>'
            '<div class="title">%s</div><div class="note">%s</div>%s</div>'
            % (n, escape(lec.get("module_title", "")), escape(lec["title"]),
               escape(lec.get("hook", "")), _go(links.lesson(lec), "Open " + lec["id"])))
    if view["problems"]:
        # These were <span>s: they looked clickable and did nothing. A control
        # that reads as a link and is inert is worse than no control at all.
        chips = "".join(
            '<a class="chip" href="%s" title="%s">%s</a>'
            % (links.problems(p["id"]), escape(p["title"]), escape(p["id"]))
            for p in view["problems"][:6])
        cards.append(
            '<div class="card problems"><div class="kind">Problems · ~25 min</div>'
            '<div class="title">Pick one</div>'
            '<div class="note">Unmastered sets first.</div>'
            '<div class="chips">%s</div></div>' % chips)
    return '<div class="cards">%s</div>' % "".join(cards) if cards else ""


def _go(href, label):
    if href is None:
        return '<div class="note">needs the local server</div>'
    return '<a class="go" href="%s">%s →</a>' % (href, escape(label))


def _stale_block(view):
    if not view["stale"]:
        return ""
    items = ", ".join("%s (%d days)" % (escape(s["id"]), s["days"])
                      for s in view["stale"][:4])
    return ('<h2>Still open</h2><div class="stale">%s. Fifteen minutes would '
            'close any one of them — an option, not a debt.</div>' % items)


def _modules_block(view):
    if not view["modules"]:
        return ""
    bars = "".join(
        '<div class="mod">%s <span style="color:var(--dim)">%d/%d</span>'
        '<div class="bar"><div class="fill" style="width:%d%%"></div></div></div>'
        % (escape(m["title"]), m["done"], m["total"], m["pct"])
        for m in view["modules"])
    return '<h2>Module progress</h2><div class="mods">%s</div>' % bars


def render_unbuilt_page(today, detail):
    """The static page when there is no day to show, and saying so is the job.

    dashboard/today.html is only rewritten by a run that got that far, so a
    build that crashes -- or a scheduled task that never fires -- leaves
    yesterday's page in place, complete with the healthy banner it rendered
    yesterday. Clicking the shortcut then produces a confident page offering
    yesterday's lectures under no date at all. That is the precise failure this
    whole loop exists to remove, reintroduced by an artifact nobody rewrote.

    Deliberately self-contained: no syllabus, no plan, no PyYAML. It is written
    from a crash handler and from a Start Menu shortcut, and both must work
    when the thing that failed is exactly the state this would otherwise read.
    """
    return (
        "<!DOCTYPE html>\n<html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Nexus College — no day built</title><style>%s"
        "body{font-family:Georgia,serif;background:var(--bg);color:var(--ink);"
        "max-width:44rem;margin:0 auto;padding:3rem 1.2rem;line-height:1.7}"
        "h1{font-family:Segoe UI,system-ui,sans-serif;font-size:1.3rem}"
        "code{background:#26313c;border-radius:5px;padding:.1rem .35rem;"
        "font-family:Consolas,monospace;font-size:.9em}"
        ".banner{background:#2a1f1f;border-left:4px solid var(--bad);"
        "border-radius:10px;padding:1rem 1.2rem;margin:1.5rem 0}"
        "</style></head><body>"
        "<h1>Nexus College</h1>"
        "<div class='banner'><b>No day has been built for %s.</b> %s</div>"
        "<p>Nothing here is lost — the plan is rebuilt from state, so running "
        "the builder again is the whole recovery:</p>"
        "<p><code>python scripts/daily.py</code></p>"
        "<p>If that succeeds and this page persists, the scheduled task is not "
        "firing; <code>python scripts/check_daily_liveness.py</code> says which "
        "of the two it is.</p>"
        "<p>The previous day's page was deliberately not shown. It would have "
        "offered yesterday's units as though they were today's.</p>"
        "</body></html>\n" % (PALETTE, escape(today), escape(detail)))


def render_home(view, links):
    streak = view["streak"]
    return (
        "<!DOCTYPE html>\n<html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Nexus College — %s</title><style>%s</style></head><body>"
        "<header><h1>Nexus College</h1>"
        "<span class='meta'>%s</span>"
        "<span class='streak'>%d day streak · best %d · %d/%d units mastered</span>"
        "</header>%s%s<h2>Today</h2>%s%s%s"
        "<footer>Built by <code>scripts/daily.py</code> — no model involved. "
        "<div class='nav'>%s</div></footer></body></html>\n"
        % (escape(view["date"]), CSS, escape(_pretty_date(view["date"])),
           streak.get("current", 0), streak.get("best", 0),
           view["mastered_total"], view["unit_total"],
           _liveness_banner(view), _hero(view, links),
           _segment_cards(view, links), _stale_block(view),
           _modules_block(view), links.nav()))


PROBLEM_CSS = PALETTE + """
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);margin:0;padding:2rem 1.2rem 4rem;
font-family:Georgia,serif;line-height:1.7}
main{max-width:52rem;margin:0 auto}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:.8rem;
border-bottom:1px solid var(--line);padding-bottom:.8rem;margin-bottom:1.4rem;
font-family:Segoe UI,system-ui,sans-serif}
header h1{font-size:1.1rem;margin:0;font-weight:600}
header a{margin-left:auto;color:var(--acc);font-size:.9rem}
h1,h2,h3,h4{font-family:Segoe UI,system-ui,sans-serif;line-height:1.3}
main h1{font-size:1.35rem;margin:2rem 0 .6rem}
main h2{font-size:1.05rem;margin:2.2rem 0 .5rem;color:var(--acc)}
main h3{font-size:.95rem;margin:1.6rem 0 .4rem}
hr{border:0;border-top:1px solid var(--line);margin:2rem 0}
code{background:#26313c;border-radius:5px;padding:.1rem .35rem;font-size:.9em;
font-family:Consolas,"DejaVu Sans Mono",monospace}
blockquote{border-left:3px solid var(--warm);margin:1.2rem 0;padding:.2rem 0 .2rem 1rem;
color:var(--dim)}
li{margin:.3rem 0}
pre{background:#0c1116;border:1px solid var(--line);border-radius:8px;
padding:.9rem 1rem;overflow-x:auto;line-height:1.45;margin:1.1rem 0}
pre code{background:none;padding:0;font-size:.86rem;white-space:pre}
/* The six sets with tables use them for fill-in grids, so an empty cell has to
   keep its box: collapsed borders and a min-height rather than nothing. */
table{border-collapse:collapse;width:100%;margin:1.2rem 0;font-size:.92rem;
display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:.45rem .6rem;text-align:left;
vertical-align:top;min-width:4.5rem;height:1.9rem}
th{background:var(--panel);font-family:Segoe UI,system-ui,sans-serif;
font-size:.85rem;color:var(--acc)}
.note{background:var(--panel);border-left:4px solid var(--warm);border-radius:10px;
padding:.8rem 1rem;margin-bottom:1.6rem;font-size:.9rem;color:var(--dim);
font-family:Segoe UI,system-ui,sans-serif;line-height:1.55}
/* KaTeX is used in MathML-only mode, so these two rules replace everything the
   KaTeX stylesheet used to provide: its own sizing, and keeping a long display
   formula scrollable instead of letting it push the page sideways. */
.katex{font-size:1.12em}
.katex-display{display:block;text-align:center;margin:1.1rem 0;
overflow-x:auto;overflow-y:hidden;padding:.2rem 0}
math{font-size:1.05em}
"""


def render_problem_set(unit_id, title, markdown):
    """A problem set as a readable page, with its LaTeX actually rendered.

    KaTeX is vendored under vendor/katex and served by this server from
    /katex/. It is NOT loaded from a CDN: the college works offline by rule
    (scripts/gate.py forbids external requests in lessons, and a problem set
    that needs the internet to be legible would be a worse artifact than one
    that does not). Everything here is same-origin.

    It runs in `output: 'mathml'` mode, which is why no stylesheet and no fonts
    are loaded: the browser's own maths engine does the layout. KaTeX's default
    htmlAndMathml emits BOTH a visual HTML rendering and a hidden MathML copy,
    which is fine alone and breaks badly next to anything that also acts on
    maths -- a Native MathML extension unhides the MathML while KaTeX's CSS is
    still clipping it, and every formula on the page goes blank. MathML-only
    emits one thing, so there is nothing to disagree about.

    The <annotation encoding="application/x-tex"> KaTeX embeds carries the
    original source, so copy-the-LaTeX tooling keeps working.

    Server-only: the static dashboard/today.html links chips straight at the
    .md on disk, because a page written to disk cannot serve fonts.
    """
    # The header is a breadcrumb, not a title: every set opens with its own
    # `# unit — title` heading, and printing the same words twice, three lines
    # apart, just looks like a bug.
    heading = "Problem set · " + escape(unit_id)
    return (
        "<!DOCTYPE html>" + chr(10) +
        "<html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Problem set " + escape(unit_id) + "</title>"
        "<style>" + PROBLEM_CSS + "</style></head><body><main>"
        "<header><h1>" + heading + "</h1>"
        "<a href='/'>Back to today</a></header>"
        "<div class='note'>Work it with <code>/problems " + escape(unit_id) +
        "</code> for the hint ladder, or submit written solutions with "
        "<code>/grade " + escape(unit_id) + "</code> — both need a model, "
        "so both are things you start rather than things that happen to you."
        "</div>" + mathdoc.to_html(markdown) + "</main>"
        "<script src='/katex/katex.min.js'></script>"
        "<script src='/katex/contrib/auto-render.min.js'></script>"
        "<script>renderMathInElement(document.querySelector('main'),{"
        "delimiters:["
        "{left:'$$',right:'$$',display:true},"
        "{left:'$',right:'$',display:false}"
        "],output:'mathml',throwOnError:false});</script>"
        "</body></html>" + chr(10))
