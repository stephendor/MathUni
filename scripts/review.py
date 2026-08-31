"""review.py — the retrieval session as a page, with no model in it.

`/review` used to need a model to judge free-text answers. It does not: the
deck already carries the back of every card, and the rating that actually moves
the schedule has always been Stephen's own (the skill says his rating wins).
What a model added was conversation, and conversation is Tier 1 — something you
start deliberately, not something a usage limit can take out from under you at
06:30.

So this is the whole SRS loop, offline: the page shows a front, reveals the
back, takes 1-4, and POSTs each rating straight through `/api/rate` into
`srs.scheduler.apply_rating` — the same function the CLI uses.

Two decisions worth naming.

The queue is capped and drained oldest-first. The deck stood at 66 of 66 due
when this was written, and a 66-card wall is how a re-entry fails; 15 matches
the cap already stated in the review skill. The page says what it is holding
back, because a silently truncated queue is its own kind of lie.

A rating that fails to save stops the session on that card and says so. The
alternative — advancing and losing it — is the exact failure this whole piece
of work exists to remove: an action that reports success while nothing was
written.
"""
import json

from scripts.home import PALETTE

REVIEW_CAP = 15

CSS = PALETTE + """
*{box-sizing:border-box}
body{font-family:Georgia,serif;background:var(--bg);color:var(--ink);
max-width:44rem;margin:0 auto;padding:2rem 1.2rem 4rem;line-height:1.6}
h1,.ui{font-family:Segoe UI,system-ui,sans-serif}
a{color:var(--acc)}
header{display:flex;align-items:baseline;gap:.8rem;border-bottom:1px solid var(--line);
padding-bottom:.8rem;margin-bottom:1.8rem;font-family:Segoe UI,system-ui,sans-serif}
header h1{font-size:1.15rem;margin:0;font-weight:600}
header .count{margin-left:auto;color:var(--dim);font-size:.9rem}
.progress{background:#232b34;border-radius:6px;height:6px;overflow:hidden;margin-bottom:2rem}
.progress i{display:block;background:var(--good);height:100%;width:0;transition:width .2s}
.card{background:var(--panel);border-radius:14px;padding:1.8rem;min-height:11rem;
display:flex;flex-direction:column;justify-content:center}
.unit{font-family:Segoe UI,system-ui,sans-serif;font-size:.72rem;letter-spacing:.08em;
text-transform:uppercase;color:var(--dim);margin-bottom:.9rem}
.front{font-size:1.18rem}
.back{border-top:1px solid var(--line);margin-top:1.3rem;padding-top:1.3rem;color:#cfd6dd}
.controls{margin-top:1.4rem;display:flex;flex-wrap:wrap;gap:.5rem}
button{font-family:Segoe UI,system-ui,sans-serif;font-size:.95rem;font-weight:600;
border:0;border-radius:9px;padding:.7rem 1.15rem;cursor:pointer;background:#26313c;color:var(--ink)}
button.primary{background:var(--acc);color:#0c1013}
button.r1{background:#3a2226;color:#f3c2c7}button.r2{background:#3a3222;color:#f0dcb0}
button.r3{background:#22331f;color:#c9e6bd}button.r4{background:#1f3330;color:#b6e6d8}
button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.hint{color:var(--dim);font-size:.84rem;font-family:Segoe UI,system-ui,sans-serif;margin-top:.9rem}
.err{background:#2a1d1d;border-left:4px solid var(--bad);border-radius:10px;padding:.9rem 1.1rem;
margin-top:1.2rem;font-family:Segoe UI,system-ui,sans-serif;font-size:.92rem;display:none}
.err b{color:var(--bad)}
.note{background:#1d1c16;border-left:4px solid var(--warm);border-radius:10px;
padding:.8rem 1rem;margin-bottom:1.5rem;font-size:.88rem;
font-family:Segoe UI,system-ui,sans-serif;color:var(--dim)}
.done{background:var(--panel);border-radius:14px;padding:1.8rem;text-align:center}
.done h2{font-family:Segoe UI,system-ui,sans-serif;font-size:1.1rem;margin:0 0 .6rem}
.tally{color:var(--dim);font-family:Segoe UI,system-ui,sans-serif;font-size:.92rem}
.empty{background:var(--panel);border-radius:14px;padding:1.8rem;color:var(--dim)}
.empty b{color:var(--ink);font-family:Segoe UI,system-ui,sans-serif}
"""

# `</script>` inside card text would end the block early and drop the rest of
# the deck into the document as markup. Escaping the sequence is what makes
# embedding JSON in a script element safe; the cards carry maths prose, not
# markup, but "no card has ever contained that" is not a property.
_JSON_SAFE = (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"))


def embed_json(obj):
    out = json.dumps(obj, ensure_ascii=False)
    for raw, esc in _JSON_SAFE:
        out = out.replace(raw, esc)
    return out


def build_queue(due, cap=REVIEW_CAP):
    """The session's cards: oldest due first, capped.

    `due` arrives from srs.scheduler.due_cards, which already sorts by due
    date; the sort is repeated here so the cap means "oldest" regardless of
    what the caller passed.
    """
    return sorted(due, key=lambda c: (c.get("due", ""), c.get("id", "")))[:cap]


def render_review(queue, token, total_due, engram_notice=None):
    """The retrieval page. `token` is required for the writeback to work."""
    if not queue:
        return _shell("Nothing due", (
            '<div class="empty"><b>Nothing is due.</b> The schedule is the '
            'point — cards come back when they are worth seeing again, and '
            'inventing extra ones now would only make that worse. '
            '<a href="/">Back to today</a>.</div>'))

    held = total_due - len(queue)
    sub = ("%d of %d due — the other %d keep their place in the queue"
           % (len(queue), total_due, held)) if held > 0 else "%d due" % total_due
    notice = '<div class="note">%s</div>' % engram_notice if engram_notice else ""

    body = (
        '%s<div class="progress"><i id="bar"></i></div>'
        '<div id="stage"></div>'
        '<div class="err" id="err"><b>That rating did not save.</b> '
        '<span id="errdetail"></span> The card is still due; nothing was lost. '
        'Check the local server and reload.</div>'
        '<script type="application/json" id="deck">%s</script>'
        '<script>%s</script>'
        % (notice, embed_json(queue), _SCRIPT.replace("__TOKEN__", token)))
    return _shell("Review", body, sub=sub, count=len(queue))


def _shell(title, body, sub="", count=0):
    return (
        "<!DOCTYPE html>\n<html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Nexus College — %s</title><style>%s</style></head><body>"
        "<header><h1>Retrieval</h1><span class='count'>%s</span></header>"
        "%s</body></html>\n" % (title, CSS, sub, body))


_SCRIPT = """
(function(){
  var CARDS = JSON.parse(document.getElementById('deck').textContent);
  var RATE = '/api/rate?t=' + '__TOKEN__';
  var LABELS = {1:'Again',2:'Hard',3:'Good',4:'Easy'};
  var i = 0, tally = {1:0,2:0,3:0,4:0}, revealed = false, busy = false;
  var stage = document.getElementById('stage');
  var bar = document.getElementById('bar');
  var err = document.getElementById('err');

  function esc(s){ var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  function draw(){
    bar.style.width = (100 * i / CARDS.length) + '%';
    if (i >= CARDS.length) return finish();
    var c = CARDS[i];
    var html = '<div class="card"><div class="unit">' + esc(c.unit || '') + ' \\u00b7 ' +
               esc(c.type || 'card') + ' \\u00b7 ' + (i+1) + ' of ' + CARDS.length +
               '</div><div class="front">' + esc(c.front) + '</div>';
    if (revealed) html += '<div class="back">' + esc(c.back) + '</div>';
    html += '</div><div class="controls">';
    if (revealed) {
      for (var r = 1; r <= 4; r++) {
        html += '<button class="r' + r + '" data-rate="' + r + '">' + r + ' \\u00b7 ' +
                LABELS[r] + '</button>';
      }
    } else {
      html += '<button class="primary" data-reveal="1">Show answer</button>';
    }
    html += '</div><div class="hint">' +
            (revealed ? 'Keys 1-4. Your rating wins.' : 'Space or Enter to reveal.') +
            '</div>';
    stage.innerHTML = html;
  }

  function finish(){
    var parts = [];
    for (var r = 1; r <= 4; r++) { if (tally[r]) parts.push(tally[r] + ' ' + LABELS[r].toLowerCase()); }
    stage.innerHTML = '<div class="done"><h2>Done \\u2014 ' + CARDS.length + ' cards</h2>' +
      '<div class="tally">' + (parts.join(' \\u00b7 ') || 'nothing rated') + '</div>' +
      '<div class="controls" style="justify-content:center">' +
      '<a href="/"><button class="primary">Back to today</button></a></div></div>';
  }

  function rate(r){
    if (busy) return;
    busy = true;
    fetch(RATE, {method:'POST', headers:{'Content-Type':'application/json'},
                 body: JSON.stringify({card: CARDS[i].id, rating: r})})
      .then(function(resp){
        if (!resp.ok) throw new Error('server said ' + resp.status);
        return resp.json();
      })
      .then(function(){
        tally[r]++; i++; revealed = false; busy = false; draw();
      })
      .catch(function(e){
        // Stop here rather than advancing. A rating that vanished while the
        // session marched on is the failure mode this project exists to remove.
        busy = false;
        document.getElementById('errdetail').textContent = String(e.message || e);
        err.style.display = 'block';
      });
  }

  stage.addEventListener('click', function(ev){
    var b = ev.target.closest('button'); if (!b) return;
    if (b.dataset.reveal) { revealed = true; draw(); }
    else if (b.dataset.rate) { rate(parseInt(b.dataset.rate, 10)); }
  });

  document.addEventListener('keydown', function(ev){
    if (i >= CARDS.length) return;
    if (!revealed && (ev.key === ' ' || ev.key === 'Enter')) {
      ev.preventDefault(); revealed = true; draw();
    } else if (revealed && ev.key >= '1' && ev.key <= '4') {
      rate(parseInt(ev.key, 10));
    }
  });

  draw();
})();
"""
