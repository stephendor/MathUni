"""reference.py — every definition and theorem in the corpus, in one place.

The flashcards drill recall. They are not a reference: 66 cards over 8 units,
each one deliberately a single question, and you cannot look anything up in
them. What was missing is the other half — the thing the Cambridge Dexter notes
split out as `_def` and `_thm` files — a list you scan when you half-remember
that a definition exists and want to see it stated.

That already exists in the repo; it is simply not gathered. The 145 lessons
carry 1054 blocks marked `<div class="definition">` and `<div class="theorem">`,
1048 of them opening with a bold label and 968 carrying a citation. This module
gathers them, and gathers nothing else: every line on the page was written into
a lesson that passed scripts/check_unit.py, so the reference cannot disagree
with what was taught, and no model is involved in producing it. A reference
that could hallucinate a theorem statement would be worse than no reference.

Two extraction details are load-bearing.

**Div matching is balanced, not lazy.** `<div class="theorem">(.*?)</div>` looks
right and truncates every block that contains a nested div, silently, at the
first inner close tag. The corpus has those.

**The label may or may not be wrapped in a <p>.** Two conventions grew in the
corpus -- `<div class="definition"><strong>Definition 1.1` and
`<div class="definition"><p><strong>Definition 11.32` -- and a pattern anchored
to the first shape drops 602 of the 1054 blocks while looking like it works.

  python scripts/reference.py            # write dashboard/reference.html
"""
import os
import re
import sys
from html import escape

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.home import PALETTE

KINDS = ("definition", "theorem")

_OPEN = re.compile(r'<div class="(%s)">' % "|".join(KINDS))
_DIV = re.compile(r"<(/?)div\b")
# Optional <p> because the corpus uses both conventions; see the module docstring.
_LABEL = re.compile(r"^\s*(?:<p>\s*)?<strong>(.*?)</strong>\.?", re.S)
_CITE = re.compile(r'<span class="cite">(.*?)</span>', re.S)
_H2 = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)

# Inline markup that carries meaning in a maths statement, taken from a count
# of what the 1054 blocks actually contain rather than from a guess: 4948 <sub>,
# 4624 <var>, 1184 <sup>. D<sub>2n</sub> and 2<var>k</var> are not decoration --
# dropping <var> turns "n = 2k" into "n = 2 k", which reads as a typo in every
# statement in the corpus. Everything else has its tags removed and its text
# kept, so no attribute from a lesson reaches this page.
#
# <br> is kept and closed as <br> because it is void; the rest are paired.
_KEEP = ("em", "strong", "sub", "sup", "var", "code", "br")
_VOID = ("br",)
_TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")


def _inline_only(html):
    """Drop every tag but a small inline whitelist, keeping the text."""
    def keep(match):
        name = match.group(1).lower()
        if name not in _KEEP:
            # A space, not nothing: </p><p> and </li><li> are word boundaries,
            # and joining across them would run two sentences together.
            return " "
        if name in _VOID:
            return "<%s>" % name
        return "</%s>" % name if match.group(0).startswith("</") else "<%s>" % name
    return re.sub(r"\s{2,}", " ", _TAG.sub(keep, html)).strip()


def blocks(html):
    """(kind, body, opening offset) per definition/theorem div, balanced.

    A lazy `.*?</div>` truncates any block containing a nested div at the first
    inner close tag, which loses the tail of the statement without erroring.

    The offset comes back because the segment a block sits in is decided by the
    nearest <h2> above it, and that is not recoverable from the body alone.
    """
    out = []
    for match in _OPEN.finditer(html):
        kind, start, depth = match.group(1), match.end(), 1
        for tag in _DIV.finditer(html, start):
            depth += -1 if tag.group(1) else 1
            if depth == 0:
                out.append((kind, html[start:tag.start()], match.start()))
                break
    return out


def _segment_for(headings, position):
    """The nearest <h2> above `position` — which segment of the lesson it is in.

    Lessons carry no per-block anchors, so a reference entry cannot deep-link to
    itself. Naming the segment is the next best thing: it tells you where to
    look once the lesson opens.
    """
    last = ""
    for at, text in headings:
        if at > position:
            break
        last = text
    return last


def parse_lesson(html, unit_id, module):
    """Every definition and theorem in one lesson, in document order."""
    entries = []
    headings = [(m.start(), _inline_only(m.group(1))) for m in _H2.finditer(html)]
    for kind, body, at in blocks(html):
        cite = _CITE.search(body)
        stripped = _CITE.sub("", body)
        label = _LABEL.search(stripped)
        statement = _LABEL.sub("", stripped, count=1) if label else stripped
        entries.append({
            "unit": unit_id,
            "module": module,
            "kind": kind,
            # 6 of 1054 blocks open without a label. They are still real
            # statements, so they are kept and named by their kind rather than
            # dropped for failing to match a pattern.
            "label": _inline_only(label.group(1)) if label else kind.title(),
            "statement": _inline_only(statement),
            "cite": _inline_only(cite.group(1)) if cite else "",
            "segment": _segment_for(headings, at),
        })
    return entries


def build_index(units, root="lessons"):
    """Every entry across the corpus, in syllabus order.

    Syllabus order, not filesystem order: the reference reads as the course
    does, so a definition appears after the one it depends on.
    """
    index = []
    for unit in units:
        path = os.path.join(root, unit["module"], "%s.html" % unit["id"])
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            index.extend(parse_lesson(f.read(), unit["id"], unit["module"]))
    return index


def counts(index):
    return {kind: sum(1 for e in index if e["kind"] == kind) for kind in KINDS}


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
.unit{margin:1.6rem 0 .5rem;font-family:Segoe UI,system-ui,sans-serif;
font-size:.9rem;color:var(--acc);border-bottom:1px solid var(--line);
padding-bottom:.3rem}
.unit a{color:inherit}
.e{background:var(--panel);border-left:3px solid var(--line);border-radius:8px;
padding:.7rem .9rem;margin:.5rem 0}
.e.definition{border-left-color:var(--acc)}
.e.theorem{border-left-color:var(--warm)}
.k{font-family:Segoe UI,system-ui,sans-serif;font-size:.7rem;letter-spacing:.08em;
text-transform:uppercase;color:var(--dim)}
.l{font-weight:700}
.s{display:block;margin-top:.2rem}
.c{display:block;margin-top:.35rem;color:var(--dim);font-size:.82rem}
.seg{color:var(--dim);font-size:.82rem}
#empty{color:var(--dim);padding:2rem 0;display:none}
footer{margin-top:3rem;border-top:1px solid var(--line);padding-top:.8rem;
color:var(--dim);font-size:.82rem;font-family:Segoe UI,system-ui,sans-serif}
footer a{color:var(--acc);margin-right:1rem}
"""

_SCRIPT = """
(function(){
  var q = document.getElementById('q');
  var kinds = Array.prototype.slice.call(document.querySelectorAll('[data-kind]'));
  var entries = Array.prototype.slice.call(document.querySelectorAll('.e'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.g'));
  var empty = document.getElementById('empty');
  var kind = 'all';

  function apply(){
    var needle = q.value.trim().toLowerCase();
    var shown = 0;
    entries.forEach(function(el){
      var okKind = kind === 'all' || el.classList.contains(kind);
      var okText = !needle || el.dataset.t.indexOf(needle) !== -1;
      var on = okKind && okText;
      el.hidden = !on;
      if (on) shown++;
    });
    // A unit heading with nothing under it is noise, so it goes too.
    groups.forEach(function(g){
      g.hidden = !g.querySelectorAll('.e:not([hidden])').length;
    });
    empty.style.display = shown ? 'none' : 'block';
  }

  kinds.forEach(function(b){
    b.addEventListener('click', function(){
      kind = b.dataset.kind;
      kinds.forEach(function(o){ o.setAttribute('aria-pressed', o === b); });
      apply();
    });
  });
  q.addEventListener('input', apply);
  // Typing goes to the box wherever the focus is; this page is for scanning.
  document.addEventListener('keydown', function(ev){
    if (ev.key === '/' && document.activeElement !== q){ ev.preventDefault(); q.focus(); }
    if (ev.key === 'Escape'){ q.value = ''; apply(); }
  });
})();
"""


def render_reference(index, links, titles=None):
    """The index as one scannable page, filtered in the browser.

    Everything is in the document and hidden with `hidden`, rather than fetched:
    the whole point is that it works with no server, and 1054 entries is a page,
    not a database.
    """
    titles = titles or {}
    n = counts(index)
    out = []
    current = None
    for entry in index:
        if entry["unit"] != current:
            if current is not None:
                out.append("</div>")
            current = entry["unit"]
            # read_lesson, never lesson(): on the live server the latter is an
            # authenticated /open link that marks the unit in-progress, stamps
            # last_studied and writes a learning record. Consulting a reference
            # is not starting a unit, and must not tell the planner it was.
            href = links.read_lesson(entry["unit"], entry["module"])
            title = titles.get(entry["unit"], "")
            out.append('<div class="g"><div class="unit">'
                       '<a href="%s">%s</a>%s</div>'
                       % (escape(href or ""), escape(entry["unit"]),
                          " &middot; " + escape(title) if title else ""))
        haystack = " ".join((entry["label"], entry["statement"], entry["cite"],
                             entry["unit"])).lower()
        out.append(
            '<div class="e %s" data-t="%s"><span class="k">%s%s</span>'
            '<span class="l">%s</span><span class="s">%s</span>%s</div>'
            % (entry["kind"], escape(re.sub("<[^>]+>", "", haystack)),
               entry["kind"],
               (" &middot; " + escape(entry["segment"])) if entry["segment"] else "",
               entry["label"], entry["statement"],
               ('<span class="c">%s</span>' % entry["cite"]) if entry["cite"] else ""))
    if current is not None:
        out.append("</div>")

    return (
        "<!DOCTYPE html>\n<html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Nexus College — definitions &amp; theorems</title>"
        "<style>%s</style></head><body><main>"
        "<header><h1>Definitions &amp; theorems</h1>"
        "<span class='meta'>%d definitions &middot; %d theorems, from the "
        "lessons themselves</span>"
        "<a href='%s'>Back to today</a></header>"
        "<div class='tools'>"
        "<input type='search' id='q' placeholder='Search statements, labels, "
        "citations &mdash; press /' autocomplete='off'>"
        "<button data-kind='all' aria-pressed='true'>All</button>"
        "<button data-kind='definition' aria-pressed='false'>Definitions</button>"
        "<button data-kind='theorem' aria-pressed='false'>Theorems</button>"
        "</div>"
        "%s"
        "<div id='empty'>Nothing matches that.</div>"
        "<footer>Extracted from the lesson corpus by "
        "<code>scripts/reference.py</code> — no model involved, so nothing here "
        "can say something a lesson does not. %s</footer>"
        "</main><script>%s</script></body></html>\n"
        % (CSS, n["definition"], n["theorem"], escape(links.home() or "/"),
           "".join(out), links.nav(), _SCRIPT))


def main(argv=None):
    from scripts.home import StaticLinks
    from scripts.validate_syllabus import load_syllabus

    if not os.path.exists("curriculum/syllabus.yaml"):
        print("reference.py: run from the repo root", file=sys.stderr)
        return 2
    syllabus = load_syllabus("curriculum/syllabus.yaml")
    units = syllabus.get("units", [])
    index = build_index(units)
    titles = {u["id"]: u.get("title", "") for u in units}
    html = render_reference(index, StaticLinks(), titles)

    os.makedirs("dashboard", exist_ok=True)
    with open("dashboard/reference.html", "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(html)
    n = counts(index)
    print("reference.py: %d definitions, %d theorems from %d units"
          % (n["definition"], n["theorem"], len({e["unit"] for e in index})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
