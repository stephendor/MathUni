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
  5. NO EXTERNAL REQUESTS. http(s)://, <link, src=, cdn, @import — the file
     must render offline (rubric Gate 0.3).
  6. INLINE SCRIPTS PARSE. node --check each <script> body (rubric Gate 0.4 is
     "zero console errors"; a syntax error is the loudest of those).

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

# HTML permits these end tags to be omitted, and a start tag for a block
# element implicitly closes an open <p>. A strict stack therefore reports
# spec-legal markup as an error and — worse — desynchronises on it, so every
# tag after the first <p> is misattributed. lesson_lint.py made the same
# carve-out for the same reason ("``p`` is deliberately excluded because HTML
# permits its end tag to be omitted"); the two gates agree on purpose.
OPTIONAL_END = {"p", "li", "dt", "dd", "option", "thead", "tbody", "tfoot",
                "tr", "td", "th"}

# `xmlns="http://www.w3.org/2000/svg"` is an XML *namespace identifier*, not a
# URL the browser ever fetches — inline SVG carrying it renders identically
# with the network unplugged. Scanning raw lines flagged it anyway, failing
# an-02, pw-01 and pw-03 while the 76 S2-S4 lessons passed purely because
# their authors happened to omit the attribute. The population, not the
# sample, is the thing to fix: strip namespace declarations before scanning.
# Nothing else is exempted — `src=`, `<link`, `@import` and any other
# http(s):// all still fire.
XMLNS_DECL = re.compile(r"""\bxmlns(?::[A-Za-z_][\w.-]*)?\s*=\s*("[^"]*"|'[^']*')""")
EXTERNAL = re.compile(r"https?://|<link\b|\bsrc\s*=|\bcdn\b|@import", re.I)


class Balance(HTMLParser):
    """Stack-based tag-ordering check that does not cascade.

    The scratchpad version popped the stack on every end tag, matching or not.
    One stray ``</p>`` in aa-00 therefore consumed the open ``<div>`` and every
    subsequent close was misattributed: four error lines, of which one was
    real and three were wreckage from the first. An error list a reader cannot
    trust past its first entry is a gate that reports its own confusion. Here
    an end tag with no matching start is reported and *not* popped, and one
    that matches deeper in the stack unwinds exactly to it.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.open_optional = {}
        self.errors = []

    def _governed(self, tag):
        return tag not in VOID and tag not in OPTIONAL_END

    def handle_starttag(self, tag, attrs):
        if tag in OPTIONAL_END:
            self.open_optional[tag] = self.open_optional.get(tag, 0) + 1
        elif self._governed(tag):
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        pass  # <br/>, <svg .../> — self-closing, nothing to balance

    def handle_endtag(self, tag):
        # An optional end tag may be OMITTED; one that is PRESENT with nothing
        # open is still malformed, and parsers drop it silently. Counting
        # rather than stacking is what the optionality permits — an implicit
        # close (<p>a<div>) leaves the count high and raises nothing — while
        # still catching the surplus. aa-00 and aa-01 each ship one of these.
        if tag in OPTIONAL_END:
            if self.open_optional.get(tag, 0) > 0:
                self.open_optional[tag] -= 1
            else:
                self.errors.append("line %d: </%s> with no matching <%s>"
                                   % (self.getpos()[0], tag, tag))
            return
        if not self._governed(tag):
            return
        depth = next((i for i in range(len(self.stack) - 1, -1, -1)
                      if self.stack[i][0] == tag), None)
        if depth is None:
            self.errors.append("line %d: </%s> with no matching <%s>"
                               % (self.getpos()[0], tag, tag))
            return
        for orphan, line in reversed(self.stack[depth + 1:]):
            self.errors.append("line %d: <%s> not closed before </%s> at line %d"
                               % (line, orphan, tag, self.getpos()[0]))
        del self.stack[depth:]

    def close(self):
        super().close()
        for tag, line in reversed(self.stack):
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


def script_bodies(html):
    return [s for s in re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.I | re.S)
            if s.strip()]


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

    bad, checked = script_errors(script_bodies(html))
    print("%s inline scripts parse (%d checked)%s"
          % ("PASS" if not bad else "FAIL", checked,
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

    check_one("clean lesson has no tag errors", not tag_errors(clean))
    check_one("fires on crossed tags",
              any("</sub>" in e or "not closed" in e
                  for e in tag_errors("<div><sup>x</sub></div>")))
    check_one("fires on a genuinely crossed pair with balanced counts",
              bool(tag_errors("<div><em><strong>x</em></strong></div>")))
    check_one("fires on an unclosed div", bool(tag_errors("<div><span>x</span>")))
    check_one("fires on a stray end tag",
              any("no matching" in e for e in tag_errors("<div>x</div></section>")))

    # The cascade control: one stray </p> must produce exactly one error, not
    # a chain of misattributions through every enclosing element.
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
    check_one("omitted </td>/</tr> in a table are not errors",
              tag_errors("<table><tr><td>a<td>b</tr></table>") == [])
    check_one("a surplus </td> IS an error",
              any("</td> with no matching" in e
                  for e in tag_errors("<table><tr><td>a</td></td></tr></table>")))
    check_one("an unclosed div inside a list is still caught, one error only",
              len(tag_errors("<ul><li><div>x</li></ul>")) == 1)

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

    check_one("finds inline script bodies", len(script_bodies(clean)) == 1)
    check_one("empty script bodies are not counted",
              script_bodies("<script></script><script>  </script>") == [])
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
        except RuntimeError as e:
            print("ERROR %s" % e)
            return 2
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
