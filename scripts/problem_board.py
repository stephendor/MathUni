"""problem_board.py — every problem set, and where you got to with it.

The home page offers `problem_candidates`: today's suggestion, unmastered
first, capped at six. That is the right thing for a study day and the wrong
thing for everything else. On a rest day `build_plan` empties it — correctly,
because a rest day owes no work — and the sets vanish from the only surface
that lists them. There was no way to ask "what is still outstanding" or "what
did I do on la-02 back in July", which are not day-plan questions at all.

So: a board, alongside the day rather than inside it. It is a join over four
things already on disk, and it invents nothing.

  problems/sets/*.md        146 authored sets
  state/progress.json       whether the unit is locked, open, or done
  state/mastery.json        score, attempts, date — for the 3 with a score
  learning-records/*.md     whether a session was ever logged against it

The status vocabulary here is the repo's, not a new one. "Passed" means a
mastery score at or above the gate scripts/daily.py already uses; it is not a
second opinion about what mastery means, it is the same number read twice.
"""
import os
import sys
from html import escape

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.daily import MASTERY_GATE, STUDIABLE
from scripts.home import PALETTE

SETS = "problems/sets"
SOLUTIONS = "problems/solutions"
RECORDS = "learning-records"


def build_board(units, progress, mastery, mod_titles=None, root="."):
    """One row per authored set, in syllabus order, grouped by module.

    A unit with no set on disk is omitted rather than listed as empty: 146 of
    the 146 rows here are real files, and a board padded with things that do
    not exist teaches you to distrust it.
    """
    mod_titles = mod_titles or {}
    rows = []
    for unit in units:
        uid = unit["id"]
        if not os.path.exists(os.path.join(root, SETS, "%s.md" % uid)):
            continue
        status = progress.get(uid, {}).get("status", "locked")
        record = mastery.get(uid) if isinstance(mastery.get(uid), dict) else {}
        score = record.get("score")
        scored = isinstance(score, (int, float)) and not isinstance(score, bool)
        rows.append({
            "id": uid,
            "title": unit.get("title", uid),
            "module": unit["module"],
            "module_title": mod_titles.get(unit["module"], unit["module"]),
            "status": status,
            "score": score if scored else None,
            "attempts": record.get("attempts"),
            "last": record.get("last"),
            # Two ways to be done with a set, and both count. A unit reaches
            # "mastered" through scripts/update_unlocks.py, which is the repo's
            # own verdict; a score at or above the gate is daily.py's. Reading
            # only the score called every mastered unit outstanding.
            "passed": status == "mastered" or (scored and score >= MASTERY_GATE),
            "attempted": scored,
            "studiable": status in STUDIABLE,
            "has_solutions": os.path.exists(
                os.path.join(root, SOLUTIONS, "%s.md" % uid)),
            "has_record": os.path.exists(
                os.path.join(root, RECORDS, "%s.md" % uid)),
        })
    return rows


def lane(row):
    """Which of the three filters a row answers to. Exactly one, always.

    Order matters: a mastered unit is not "studiable" — it has left the
    unlocked/in-progress states entirely — so a rule that asked "studiable?"
    first would file every finished unit under `locked`.
    """
    if row["passed"]:
        return "passed"
    if row["studiable"]:
        return "pending"
    return "locked"


def summarise(rows):
    """The counts the header states, derived from `lane` rather than restated.

    The first version asked its own questions -- pending as "studiable and not
    passed", locked as "not studiable" -- and a mastered unit answered yes to
    both `passed` and `locked`, so 145 sets were reported as 148. Counting the
    lanes makes the total an identity instead of a coincidence.
    """
    counts = {"pending": 0, "passed": 0, "locked": 0}
    for row in rows:
        counts[lane(row)] += 1
    counts["total"] = len(rows)
    counts["attempted"] = sum(1 for r in rows if r["attempted"])
    return counts


CSS = PALETTE + """
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);margin:0;padding:1.6rem 1.2rem 4rem;
font-family:Georgia,serif;line-height:1.6}
main{max-width:56rem;margin:0 auto}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:.8rem;
border-bottom:1px solid var(--line);padding-bottom:.8rem;margin-bottom:1rem;
font-family:Segoe UI,system-ui,sans-serif}
header h1{font-size:1.1rem;margin:0;font-weight:600}
header .meta{color:var(--dim);font-size:.85rem}
header a{margin-left:auto;color:var(--acc);font-size:.9rem}
.tools{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:0 0 1.2rem;
font-family:Segoe UI,system-ui,sans-serif;font-size:.85rem}
input[type=search]{flex:1;min-width:14rem;background:var(--panel);color:var(--ink);
border:1px solid var(--line);border-radius:8px;padding:.5rem .7rem;font:inherit}
button{background:var(--panel);color:var(--dim);border:1px solid var(--line);
border-radius:999px;padding:.35rem .8rem;font:inherit;cursor:pointer}
button[aria-pressed=true]{background:var(--acc);color:#101418;border-color:var(--acc);
font-weight:600}
.mod{margin:1.6rem 0 .4rem;font-family:Segoe UI,system-ui,sans-serif;font-size:.9rem;
color:var(--acc);border-bottom:1px solid var(--line);padding-bottom:.3rem}
.r{display:flex;flex-wrap:wrap;align-items:baseline;gap:.5rem;background:var(--panel);
border-left:3px solid var(--line);border-radius:8px;padding:.55rem .8rem;margin:.35rem 0}
.r.pending{border-left-color:var(--warm)}
.r.passed{border-left-color:var(--good)}
.r.locked{opacity:.55}
.r a.uid{font-family:Consolas,"DejaVu Sans Mono",monospace;font-size:.88rem;
color:var(--acc);text-decoration:none;font-weight:600}
.r a.uid:hover{text-decoration:underline}
.r .t{flex:1;min-width:12rem}
.tag{font-family:Segoe UI,system-ui,sans-serif;font-size:.72rem;letter-spacing:.04em;
text-transform:uppercase;color:var(--dim);border:1px solid var(--line);
border-radius:999px;padding:.05rem .5rem;white-space:nowrap}
.tag.score{color:var(--good);border-color:var(--good)}
.tag.open{color:var(--warm);border-color:var(--warm)}
.tag.rec{color:var(--dim)}
#empty{color:var(--dim);padding:2rem 0;display:none}
footer{margin-top:3rem;border-top:1px solid var(--line);padding-top:.8rem;
color:var(--dim);font-size:.82rem;font-family:Segoe UI,system-ui,sans-serif}
footer a{color:var(--acc);margin-right:1rem}
"""

_SCRIPT = """
(function(){
  var q = document.getElementById('q');
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-lane]'));
  var rows = Array.prototype.slice.call(document.querySelectorAll('.r'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.g'));
  var empty = document.getElementById('empty');
  // Pending by default: the question the board exists to answer. 'all' is the
  // only lane that shows locked units, so the sequencing stays visible without
  // being hidden.
  var lane = 'pending';

  function apply(){
    var needle = q.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function(el){
      var okLane = lane === 'all' || el.classList.contains(lane);
      var okText = !needle || el.dataset.t.indexOf(needle) !== -1;
      var on = okLane && okText;
      el.hidden = !on;
      if (on) shown++;
    });
    groups.forEach(function(g){
      g.hidden = !g.querySelectorAll('.r:not([hidden])').length;
    });
    empty.style.display = shown ? 'none' : 'block';
  }

  buttons.forEach(function(b){
    b.addEventListener('click', function(){
      lane = b.dataset.lane;
      buttons.forEach(function(o){ o.setAttribute('aria-pressed', o === b); });
      apply();
    });
  });
  q.addEventListener('input', apply);
  document.addEventListener('keydown', function(ev){
    if (ev.key === '/' && document.activeElement !== q){ ev.preventDefault(); q.focus(); }
    if (ev.key === 'Escape'){ q.value = ''; apply(); }
  });
  apply();
})();
"""


def _tags(row):
    out = []
    if row["score"] is not None:
        out.append('<span class="tag score">%d%%%s</span>'
                   % (round(row["score"] * 100),
                      " &middot; %d attempt%s" % (row["attempts"],
                                                  "" if row["attempts"] == 1 else "s")
                      if row["attempts"] else ""))
    if row["status"] == "mastered":
        # Said explicitly: a mastered unit with no recorded score would
        # otherwise sit in the Passed lane wearing no tag at all, looking
        # identical to a row the board had nothing to say about.
        out.append('<span class="tag score">mastered</span>')
    elif row["status"] == "in-progress":
        out.append('<span class="tag open">open</span>')
    elif row["status"] == "locked":
        out.append('<span class="tag">locked</span>')
    if row["last"]:
        out.append('<span class="tag">%s</span>' % escape(str(row["last"])))
    if row["has_record"]:
        out.append('<span class="tag rec">notes</span>')
    return "".join(out)


def render_board(rows, links, summary=None):
    """The board as one page, filtered in the browser.

    Same shape as the reference index and for the same reason: 146 rows is a
    page, and a page that filters itself keeps working with no server.
    """
    summary = summary or summarise(rows)
    out = []
    current = None
    for row in rows:
        if row["module"] != current:
            if current is not None:
                out.append("</div>")
            current = row["module"]
            out.append('<div class="g"><div class="mod">%s</div>'
                       % escape(row["module_title"]))
        haystack = " ".join(str(x) for x in
                            (row["id"], row["title"], row["status"])).lower()
        out.append(
            '<div class="r %s" data-t="%s">'
            '<a class="uid" href="%s">%s</a><span class="t">%s</span>%s</div>'
            % (lane(row), escape(haystack), escape(links.problems(row["id"])),
               escape(row["id"]), escape(row["title"]), _tags(row)))
    if current is not None:
        out.append("</div>")

    return (
        "<!DOCTYPE html>\n<html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Nexus College — problem sets</title>"
        "<style>%s</style></head><body><main>"
        "<header><h1>Problem sets</h1>"
        "<span class='meta'>%d outstanding &middot; %d passed &middot; %d "
        "authored in all</span>"
        "<a href='%s'>Back to today</a></header>"
        "<div class='tools'>"
        "<input type='search' id='q' placeholder='Search unit or title "
        "&mdash; press /' autocomplete='off'>"
        "<button data-lane='pending' aria-pressed='true'>Outstanding</button>"
        "<button data-lane='passed' aria-pressed='false'>Passed</button>"
        "<button data-lane='all' aria-pressed='false'>All</button>"
        "</div>"
        "%s"
        "<div id='empty'>Nothing matches that.</div>"
        "<footer>Every authored set, joined against progress and mastery by "
        "<code>scripts/problem_board.py</code> — no model involved. Work one "
        "with <code>/problems &lt;unit&gt;</code> for the hint ladder. %s</footer>"
        "</main><script>%s</script></body></html>\n"
        % (CSS, summary["pending"], summary["passed"], summary["total"],
           escape(links.home() or "/"), "".join(out), links.nav(), _SCRIPT))


def main(argv=None):
    from scripts.daily import read_json
    from scripts.home import StaticLinks
    from scripts.validate_syllabus import load_syllabus

    if not os.path.exists("curriculum/syllabus.yaml"):
        print("problem_board.py: run from the repo root", file=sys.stderr)
        return 2
    syllabus = load_syllabus("curriculum/syllabus.yaml")
    units = syllabus.get("units", [])
    mod_titles = {m["id"]: m.get("title", m["id"])
                  for m in syllabus.get("modules", [])}
    rows = build_board(units, read_json("state/progress.json"),
                       read_json("state/mastery.json"), mod_titles)

    os.makedirs("dashboard", exist_ok=True)
    with open("dashboard/problems.html", "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(render_board(rows, StaticLinks()))
    summary = summarise(rows)
    print("problem_board.py: %d sets — %d outstanding, %d passed, %d locked"
          % (summary["total"], summary["pending"], summary["passed"],
             summary["locked"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
