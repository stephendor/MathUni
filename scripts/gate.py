"""gate.py — the three lesson checks the coverage/parse/lint gates miss.

Gates 4-6 of the authoring rubric. Promoted into the repo 2026-08-21 after
being carried session-to-session in scratchpad since S3 (the S2 plan records
the promotion as "deferred three times"). A gate that lives in a temp
directory is a gate that only runs when an author remembers it, and the
corpus proves what that is worth: run for the first time over all 81
committed lessons, this found five failures, all five in the S1 units that
predate the S2 conventions, and one of them a defect in the gate itself.

  4. TAG BALANCE. html.parser accepts crossed tags (<sup>x</sub>) without a
     murmur; that shipped once. lesson_lint.py counts open/close pairs, which
     catches an unmatched tag but NOT a crossed one — <em><strong>x</em></strong>
     has balanced counts. Only a stack sees the ordering, so this is the check
     that earns gate.py its place next to the lint.
  5. NO EXTERNAL REQUESTS. http(s)://, protocol-relative //host/…, <link,
     src=, cdn, @import — the file must render offline (rubric Gate 0.3).
  6. INLINE SCRIPTS PARSE. node --check each executable <script> body (rubric
     Gate 0.4 is "zero console errors"; a syntax error is the loudest).

  python scripts/gate.py <lesson_html_path> [...]
  python scripts/gate.py --selftest

Exit 0 if clean, 1 if any check fails, 2 on usage error or when a check could
not be performed. Never exit 0 for a check that did not run: absence of
analysis and absence of defects must not look alike in the output.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console (cf. srs/scheduler.py)
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}

# Elements whose end tag HTML permits to be OMITTED. They are still tracked on
# the stack, in order: omission is not the same as being unordered, and a
# SURPLUS end tag for one of them is still malformed. aa-00 and aa-01 each
# shipped one of those.
#
# The list must be COMPLETE, not merely long enough for this corpus. Gate 4 is
# a hard gate that promises to accept spec-legal omission, and an earlier
# eleven-element version reported three errors on
# `<!doctype html><html><head><title>x</title><body><p>ok` — a document that is
# entirely valid. html, head, body, colgroup, rt and rp were missing.
# (Codex review of PR #20, second round.)
OPTIONAL_END = {"html", "head", "body", "p", "li", "dt", "dd", "option",
                "optgroup", "colgroup", "caption", "thead", "tbody", "tfoot",
                "tr", "td", "th", "rt", "rp"}

# A start tag that implicitly closes an open <p>.
BLOCK = {"address", "article", "aside", "blockquote", "details", "div", "dl",
         "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2",
         "h3", "h4", "h5", "h6", "header", "hr", "main", "nav", "ol", "p",
         "pre", "section", "table", "ul"}

# Which start tags implicitly close which open optional-end element.
# ANY marks an element closed by any following start tag — <colgroup> ends at
# the first non-<col>, <head> at <body>, and so on.
#
# html and body are deliberately ABSENT: their end tags may be omitted at the
# end of the document, but no start tag implicitly closes them. Giving them ANY
# made the first <div> of every lesson close <body>, which then made the
# document's own </body> a surplus end tag — three controls caught it.
ANY = object()
CLOSED_BY = {
    "head": {"body"},
    "p": BLOCK,
    "li": {"li"},
    "dt": {"dt", "dd"},
    "dd": {"dt", "dd"},
    "td": {"td", "th", "tr", "thead", "tbody", "tfoot"},
    "th": {"td", "th", "tr", "thead", "tbody", "tfoot"},
    "tr": {"tr", "thead", "tbody", "tfoot"},
    "caption": {"colgroup", "thead", "tbody", "tfoot", "tr"},
    "colgroup": ANY,          # ends at the first start tag that is not <col>
    "option": {"option", "optgroup"},
    "optgroup": {"optgroup"},
    "thead": {"tbody", "tfoot"},
    "tbody": {"tbody", "tfoot"},
    "tfoot": {"tbody", "thead"},
    "rt": {"rt", "rp"},
    "rp": {"rt", "rp"},
}
# <colgroup> is the one ANY element with an exception: <col> belongs inside it.
KEEPS_OPEN = {"colgroup": {"col"}}

# Inside <svg> and <math> the content is foreign (XML), where <circle/> really
# is self-closing. Everywhere else HTML ignores the slash on a non-void element
# and leaves it OPEN, so <div/> must be treated as an unclosed <div>.
FOREIGN = {"svg", "math"}

# `xmlns="http://www.w3.org/2000/svg"` is an XML *namespace identifier*, not a
# URL the browser ever fetches — inline SVG carrying it renders identically
# with the network unplugged. Scanning raw lines flagged it anyway, failing
# an-02, pw-01 and pw-03 while the 76 S2-S4 lessons passed purely because
# their authors happened to omit the attribute. The population, not the
# sample, is the thing to fix: strip namespace declarations before scanning.
XMLNS_DECL = re.compile(r"""\bxmlns(?::[A-Za-z_][\w.-]*)?\s*=\s*("[^"]*"|'[^']*')""")

# A protocol-relative reference — url(//cdn.example.com/x.png), href="//host/x"
# — is a real network request that neither `https?://` nor `src=` matches
# (Codex review of PR #20). The lookbehind stops `https://` double-matching,
# and the mandatory dot-and-TLD stops `// ordinary comment text` firing.
EXTERNAL = re.compile(
    r"https?://"
    r"|(?<![:/\w])//[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}"
    r"|<link\b|\bsrc\s*=|\bcdn\b|@import", re.I)

# node --check is for JavaScript. A <script type="application/json"> body is
# data, and feeding it to a JS parser fails a valid offline lesson.
#
# Compared on the MIME *essence* — lowercased, parameters stripped — not on the
# raw attribute. `type="text/javascript; charset=utf-8"` is browser-executable
# and an exact-string compare classified it as non-JavaScript and skipped it,
# which is a false PASS for any syntax error inside. Skipping is the dangerous
# direction here, so the classifier has to be the permissive one.
# (Codex review of PR #20, second round.)
JS_TYPES = {"", "module", "text/javascript", "application/javascript",
            "text/ecmascript", "application/ecmascript", "application/x-javascript",
            "text/jsx", "text/babel"}
SCRIPT_TAG = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.I | re.S)
TYPE_ATTR = re.compile(r"""\btype\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)


class Balance(HTMLParser):
    """Stack-based tag-ordering check that does not cascade.

    The scratchpad version popped the stack on every end tag, matching or not.
    One stray ``</p>`` in aa-00 therefore consumed the open ``<div>`` and every
    subsequent close was misattributed: four error lines, of which one was
    real and three were wreckage from the first. An error list a reader cannot
    trust past its first entry is a gate that reports its own confusion.

    Optional-end elements live on the same stack rather than in side counters.
    Counters lose the nesting order, so ``<table><tr><td>x</tr></td></table>``
    came back clean — a crossed pair, which is exactly what gate 4 exists to
    catch and what lesson_lint.py structurally cannot see. Here ``</tr>``
    implicitly closes the open cell and the trailing ``</td>`` is reported as a
    surplus close.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [(tag, line)]
        self.errors = []
        self.foreign = 0         # nesting depth inside <svg>/<math>

    def _implicitly_close(self, starting):
        """Pop open optional-end elements that this start tag terminates."""
        while self.stack:
            top = self.stack[-1][0]
            if top not in OPTIONAL_END:
                return
            rule = CLOSED_BY.get(top, ())
            if rule is ANY:
                if starting in KEEPS_OPEN.get(top, ()):
                    return
            elif starting not in rule:
                return
            self.stack.pop()

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        self._implicitly_close(tag)
        if tag in FOREIGN:
            self.foreign += 1
        self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        # <br/> is void; <circle/> inside <svg> is foreign content and really
        # does self-close; <div/> is neither, and the browser leaves it OPEN
        # to absorb the rest of the document (Codex review of PR #20).
        if tag in VOID or self.foreign:
            return
        self.errors.append(
            "line %d: <%s/> does not self-close in HTML — the browser leaves "
            "<%s> open" % (self.getpos()[0], tag, tag))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        line = self.getpos()[0]
        depth = next((i for i in range(len(self.stack) - 1, -1, -1)
                      if self.stack[i][0] == tag), None)
        if depth is None:
            self.errors.append("line %d: </%s> with no matching <%s>"
                               % (line, tag, tag))
            return
        # Everything above the match closes now. An optional-end element up
        # there was legitimately left open; anything else was not.
        for orphan, oline in reversed(self.stack[depth + 1:]):
            if orphan not in OPTIONAL_END:
                self.errors.append(
                    "line %d: <%s> not closed before </%s> at line %d"
                    % (oline, orphan, tag, line))
        for t, _ in self.stack[depth:]:
            if t in FOREIGN:
                self.foreign = max(0, self.foreign - 1)
        del self.stack[depth:]

    def close(self):
        super().close()
        for tag, line in reversed(self.stack):
            if tag not in OPTIONAL_END:
                self.errors.append("line %d: <%s> never closed" % (line, tag))


def tag_errors(html):
    b = Balance()
    b.feed(html)
    b.close()
    return b.errors


def external_hits(html):
    """Lines requesting a resource off the machine. Namespace decls excluded."""
    hits = []
    for i, line in enumerate(html.split("\n"), 1):
        for m in EXTERNAL.finditer(XMLNS_DECL.sub("", line)):
            hits.append("line %d: %s" % (i, m.group(0)))
    return hits


def mime_essence(value):
    """Lowercased MIME type with parameters and surrounding space removed.

    "text/javascript; charset=utf-8" -> "text/javascript".
    """
    return value.split(";", 1)[0].strip().lower()


def script_blocks(html):
    """[(essence, body)] for every non-empty <script>."""
    out = []
    for m in SCRIPT_TAG.finditer(html):
        if not m.group(2).strip():
            continue
        t = TYPE_ATTR.search(m.group(1))
        raw = ""
        if t:
            raw = t.group(1) or t.group(2) or t.group(3) or ""
        out.append((mime_essence(raw), m.group(2)))
    return out


def script_bodies(html):
    """Executable JavaScript bodies only — the ones node can meaningfully check."""
    return [body for kind, body in script_blocks(html) if kind in JS_TYPES]


def script_errors(bodies):
    """node --check each body. Returns (errors, checked). Raises if node is absent.

    Missing node is raised, never swallowed: a checker that reports PASS for a
    check it could not run manufactures a green result (the `except: continue`
    failure mode this project has paid for before).
    """
    if not shutil.which("node"):
        raise RuntimeError("node not found on PATH — cannot check inline scripts")
    bad = []
    for n, body in enumerate(bodies, 1):
        fd, tmp = tempfile.mkstemp(suffix=".js")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(body)
        try:
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
            if r.returncode:
                first = (r.stderr or r.stdout).strip().split("\n")[0]
                bad.append("script %d: %s" % (n, first))
        finally:
            os.unlink(tmp)
    return bad, len(bodies)


def _row(ok, name, detail_items):
    detail = "" if ok else ": " + "; ".join(detail_items[:6])
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, detail))


def check(path):
    """Print the three rows for one lesson. Returns the list of failures."""
    with open(path, encoding="utf-8") as f:
        html = f.read()
    fails = []

    errs = tag_errors(html)
    _row(not errs, "tags balance", errs)
    fails += errs

    hits = external_hits(html)
    _row(not hits, "no external requests", hits)
    fails += hits

    blocks = script_blocks(html)
    bodies = script_bodies(html)
    skipped = sorted({k or "?" for k, _ in blocks if k not in JS_TYPES})
    bad, checked = script_errors(bodies)
    print("%s inline scripts parse (%d checked%s)%s"
          % ("PASS" if not bad else "FAIL", checked,
             "" if not skipped else ", %d non-JS block(s) skipped: %s"
             % (len(blocks) - len(bodies), ", ".join(skipped)),
             "" if not bad else ": " + "; ".join(bad[:6])))
    fails += bad

    return fails


def selftest():
    """Watched failures. A non-zero exit is not a watched failure — accept a
    control only on the printed FAIL line naming the check (S2 plan, after the
    inherited mission.py control turned out to be an AttributeError)."""
    total = [0]
    fails = []

    def check_one(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    clean = ('<html><body><div class="segment"><p>text<sup>2</sup></p>'
             '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"></svg>'
             '</div><script>var x = 1;</script></body></html>')

    # -- gate 4: ordering --------------------------------------------------
    check_one("clean lesson has no tag errors", not tag_errors(clean))
    check_one("fires on crossed tags", bool(tag_errors("<div><sup>x</sub></div>")))
    check_one("fires on a genuinely crossed pair with balanced counts",
              bool(tag_errors("<div><em><strong>x</em></strong></div>")))
    check_one("fires on an unclosed div", bool(tag_errors("<div><span>x</span>")))
    check_one("fires on a stray end tag",
              any("no matching" in e for e in tag_errors("<div>x</div></section>")))

    cascade = "<html><body><div class='you-try'><strong>x</strong> y</p></div></body></html>"
    errs = tag_errors(cascade)
    check_one("a stray </p> is caught (aa-00, aa-01 each ship one)",
              len(errs) == 1 and "</p> with no matching" in errs[0])
    check_one("...and does not cascade into the enclosing div/body/html",
              len(errs) == 1)
    check_one("an omitted </p> is not an error — the end tag is optional",
              tag_errors("<div><p>one<p>two</p></div>") == [])
    check_one("a <p> implicitly closed by a block start is not an error",
              tag_errors("<div><p>one<div>two</div></div>") == [])
    check_one("an omitted </li> is not an error",
              tag_errors("<ul><li>a<li>b</ul>") == [])
    check_one("omitted </td>/</tr> in a table are not errors",
              tag_errors("<table><tr><td>a<td>b</tr></table>") == [])
    check_one("a surplus </td> IS an error",
              any("</td> with no matching" in e
                  for e in tag_errors("<table><tr><td>a</td></td></tr></table>")))
    # Codex review of PR #20: side counters lose ordering, so this was clean.
    check_one("CROSSED optional-end elements are caught (</tr> before </td>)",
              any("</td> with no matching" in e for e in
                  tag_errors("<table><tr><td>x</tr></td></table>")))
    check_one("an unclosed div inside a list is still caught, one error only",
              len(tag_errors("<ul><li><div>x</li></ul>")) == 1)
    # Codex review of PR #20: HTML ignores the slash on a non-void element.
    check_one("<div/> does not self-close in HTML and is reported",
              any("does not self-close" in e
                  for e in tag_errors("<body><div/></body>")))
    check_one("<br/> is void and is fine", tag_errors("<div>a<br/>b</div>") == [])
    check_one("self-closing children inside <svg> are foreign content, and fine",
              tag_errors('<svg><circle cx="1"/><path d="M0 0"/></svg>') == [])
    check_one("...and a <div/> after the svg closes is still caught",
              any("does not self-close" in e
                  for e in tag_errors("<svg><circle/></svg><div/>")))
    # Codex round 2: the optional-end list has to be COMPLETE, not just long
    # enough for this corpus — gate 4 promises to accept spec-legal omission.
    check_one("a valid minimal document with html/head/body omitted is clean",
              tag_errors("<!doctype html><html><head><title>x</title>"
                         "<body><p>ok") == [])
    check_one("an omitted </colgroup> is clean, and <col> keeps it open",
              tag_errors("<table><colgroup><col><col><tbody><tr><td>a</table>") == [])
    check_one("omitted </rt> and </rp> in ruby are clean",
              tag_errors("<ruby>x<rt>y<rp>)</ruby>") == [])
    check_one("a surplus </body> is still an error",
              any("</body> with no matching" in e
                  for e in tag_errors("<html><body>x</body></body></html>")))

    # -- gate 5: offline ---------------------------------------------------
    check_one("clean lesson requests nothing external", not external_hits(clean))
    check_one("svg xmlns is NOT an external request (no false positive)",
              not external_hits('<svg xmlns="http://www.w3.org/2000/svg"></svg>'))
    check_one("fires on a cdn script src",
              bool(external_hits('<script src="https://cdn.example.com/x.js"></script>')))
    check_one("fires on @import", bool(external_hits("<style>@import url(x);</style>")))
    check_one("fires on http:// outside a namespace declaration",
              bool(external_hits('<a href="http://example.com">x</a>')))
    check_one("a line carrying BOTH xmlns and a real url still fires",
              bool(external_hits('<svg xmlns="http://www.w3.org/2000/svg">'
                                 '<image href="http://example.com/a.png"/></svg>')))
    # Codex review of PR #20: a protocol-relative URL is still a fetch.
    check_one("fires on a protocol-relative url() in CSS",
              bool(external_hits("<style>body{background:url(//example.com/a.png)}</style>")))
    check_one("fires on a protocol-relative attribute",
              bool(external_hits('<video poster="//example.com/a.jpg"></video>')))
    check_one("a // JavaScript comment is NOT an external request",
              not external_hits("<script>// set up the canvas here\nvar x=1;</script>"))
    check_one("a bare ratio a//b is not mistaken for a host",
              not external_hits("<p>the ratio a//b is not a url</p>"))

    # -- gate 6: scripts ---------------------------------------------------
    check_one("finds inline script bodies", len(script_bodies(clean)) == 1)
    check_one("empty script bodies are not counted",
              script_bodies("<script></script><script>  </script>") == [])
    # Codex review of PR #20: JSON data is not JavaScript.
    check_one("a JSON data block is not sent to node",
              script_bodies('<script type="application/json">{"x": 1}</script>') == [])
    check_one("...but it is still counted as a block, so the skip is reported",
              len(script_blocks('<script type="application/json">{"x":1}</script>')) == 1)
    check_one("type=module is JavaScript and IS checked",
              len(script_bodies('<script type="module">let x = 1;</script>')) == 1)
    check_one("an untyped script is JavaScript and IS checked",
              len(script_bodies("<script>var x=1;</script>")) == 1)
    # Codex round 2: an exact-string type compare skipped a browser-executable
    # block, which is a false PASS for any syntax error inside it.
    check_one("a JS type carrying parameters is still checked",
              len(script_bodies('<script type="text/javascript; charset=utf-8">'
                                "var x=1;</script>")) == 1)
    check_one("type matching ignores case and surrounding space",
              len(script_bodies('<script type="  TEXT/JavaScript ">x</script>')) == 1)
    check_one("a JSON type with parameters is still skipped",
              script_bodies('<script type="application/json; charset=utf-8">'
                            '{"x":1}</script>') == [])
    if shutil.which("node"):
        good, _ = script_errors(["var x = 1;"])
        bad, n = script_errors(["var x = ;;)"])
        check_one("clean script parses", not good)
        check_one("fires on a syntax error in an inline script", bool(bad) and n == 1)
    else:
        check_one("node is on PATH so gate 6 can run at all", False)

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    if not argv:
        print("usage: gate.py <lesson_html_path> [...] | --selftest")
        return 2
    rc = 0
    for p in argv:
        print("=== %s" % p)
        try:
            if check(p):
                rc = 1
        except OSError as e:
            print("ERROR cannot read %s: %s" % (p, e))
            return 2
        except RuntimeError as e:
            print("ERROR %s" % e)
            return 2
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
