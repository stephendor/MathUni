"""lesson_lint.py — mechanical lesson checks the coverage/parse gates miss.

Two blind spots the aa-01 Gemini drift test exposed (skill-observations Obs 109):

  * RENDER FIDELITY — invalid HTML entities (`&mathbb;`) and LaTeX leak (`\\frac`,
    `&left;`/`&right;`) render as LITERAL TEXT in the browser yet raise no parse
    or console error, so they sail through Gate 0. Flash shipped 49 of them.
  * STRUCTURAL COUNTS — a component being PRESENT is not the same as ENOUGH of it.
    Pro shipped 3 self-checks where the rubric requires >=4; nothing checked.

Complements check_lesson_coverage.py. Both run in the drift-test pre-filter
(drift_bundle.py --check) and back Gate 0.5 of curriculum/LESSON-RUBRIC.md.

  python scripts/lesson_lint.py <lesson_html_path>
  python scripts/lesson_lint.py --selftest

Exit 0 if clean, 1 if any check fails (prints them), 2 on usage error.
"""
import re
import sys
from collections import Counter
from html.entities import html5
from html.parser import HTMLParser

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console (cf. srs/scheduler.py)
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

_NAMED = re.compile(r"&([a-zA-Z][a-zA-Z0-9]*);")   # &name;  (numeric &#...; is always valid)
_LATEX = re.compile(r"\\(?:left|right|frac|mathbb|mathbf|mathcal|cdot|times|sqrt"
                    r"|begin|end|leq|geq|neq|infty|sum|int|forall|exists)\b"
                    r"|\\\(|\\\)|\\\[|\\\]|\$\$")   # LaTeX that leaked as text
_MARKDOWN = re.compile(
    r"\*\*[^*\n]+\*\*"   # **bold** — same failure mode as LaTeX leak: source
    r"|__[^_\n]+__"      # __bold__   syntax that renders as literal text with
    r"|`[^`\n]+`"        # `code`     no parse/console error (Obs 151; la-01
)                        #            shipped `**R**` inside an <h2>).
_GAP = re.compile(r"NOT IN SOURCE:\s*([^<\n]*)")   # LESSON-GUIDE 'Source discipline'
_SELF_CHECK_DATA_OK = re.compile(r"\bdata-ok\b")
_SELF_CHECK_CLASS = re.compile(r'class="[^"]*\bselfcheck\b[^"]*"', re.I)
_SELF_CHECK_PROSE = re.compile(r"Self-check\s*\d")
_BALANCED_TAGS = {
    "sup", "sub", "em", "strong", "div", "details", "summary", "table",
    "tr", "td", "th", "ol", "ul", "li", "span", "footer", "textarea",
    "canvas", "svg", "h1", "h2", "h3", "button",
}


def _strip_code(html):
    """Entities inside <script>/<style> are raw text, not HTML entities — exclude them."""
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.I | re.S)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.I | re.S)
    return html


def invalid_entities(html):
    """Named &entity; refs absent from the HTML5 table — they render as literal text."""
    body = _strip_code(html)
    return Counter(m.group(0) for m in _NAMED.finditer(body)
                   if (m.group(1) + ";") not in html5)


def latex_leaks(html):
    return Counter(_LATEX.findall(_strip_code(html)))


def markdown_leaks(html):
    """Markdown source syntax leaked into rendered HTML (Obs 151).

    Same failure mode as latex_leaks: renders as literal text with no parse
    or console error. la-01 shipped `<h2>Warm-up geometry: **R**<sup>n</sup></h2>`
    — a generator emitting source syntax into a rendered target, just a
    different dialect than LaTeX.
    """
    return Counter(_MARKDOWN.findall(_strip_code(html)))


def _self_check_count(html):
    """Count self-checks by semantic markup, not the literal prose label.

    Obs 152: the rest of structure() is explicitly "keyed on robust semantic
    signals, not one lesson's class names" — every other item honours that,
    but this one counted the literal string "Self-check \\d", which a
    structurally-complete candidate can simply head differently ("Check 1"
    rather than "Self-check 1") and go uncounted. `data-ok` and
    `class="...selfcheck..."` are the markup rubric 1.8 actually asks for
    (3-4 buttons, one `data-ok`, one `.explain` per self-check); the prose
    match is kept only as a fallback for lessons using neither marker.
    """
    semantic = max(
        len(_SELF_CHECK_DATA_OK.findall(html)),
        len(_SELF_CHECK_CLASS.findall(html)),
    )
    if semantic:
        return semantic
    return len(_SELF_CHECK_PROSE.findall(html))


def tag_imbalances(html):
    """Return explicit open/close mismatches for governed non-void tags.

    ``p`` is deliberately excluded because HTML permits its end tag to be
    omitted. Browser recovery and ``HTMLParser.feed`` do not prove balance.
    """
    counts = {tag: [0, 0] for tag in _BALANCED_TAGS}

    class CounterParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag in counts:
                counts[tag][0] += 1

        def handle_endtag(self, tag):
            if tag in counts:
                counts[tag][1] += 1

    CounterParser(convert_charrefs=False).feed(_strip_code(html))
    return {
        tag: tuple(value)
        for tag, value in sorted(counts.items())
        if value[0] != value[1]
    }


def structure(html):
    html = _strip_code(html)  # count rendered markup only, not <script>/<style> string contents
    def count(pat):
        return len(re.findall(pat, html))
    return {
        "self_checks": _self_check_count(html),
        # Keyed on robust semantic signals, not one lesson's class names: the
        # reference and generated candidates mark these components differently
        # (e.g. "Predict before we start" vs "Prediction Gate"; class="blankpage"
        # vs "blank-page"; <textarea> vs class="guided-proof").
        "prediction_gate": len(re.findall(r"predict", html, re.I)),
        "segments": count(r'class="[^"]*\bsegment\b'),
        "breaks": count(r'class="[^"]*\bbreak\b'),
        "faded": count(r'class="[^"]*\bfade\b'),
        "guided_proof": len(re.findall(r"<textarea\b", html, re.I)),
        "visual": len(re.findall(r"<canvas\b|<svg\b", html, re.I)),
        "blank_page": len(re.findall(r"blank-?page|reconstruct", html, re.I)),
        "mission": count(r'class="[^"]*\bmission\b'),
        "footer": len(re.findall(r"<footer\b", html, re.I)),
    }


def gap_markers(html):
    """Author-declared source gaps (LESSON-GUIDE 'Source discipline'). A committed
    lesson must carry none; a drift candidate that carries one is being HONEST —
    hence the allow_gaps escape hatch in lint()."""
    return _GAP.findall(_strip_code(html))


GAP_CHECK = "source: no unresolved gap markers"


def lint(html):
    """Return [(check_name, ok, detail)] — render fidelity first, then structure.

    The GAP_CHECK row always fails when a gap marker is present: that is the right
    answer for a lesson about to be committed. A caller for whom a declared gap is
    a datum rather than a defect (drift_bundle scoring candidates) filters that one
    row out by name — the policy lives with the caller, not in a flag here."""
    out = []
    gaps = gap_markers(html)
    out.append((GAP_CHECK, not gaps,
                "" if not gaps else "%d declared: %s" % (
                    len(gaps), "; ".join(g.strip()[:60] for g in gaps[:3]))))
    bad = invalid_entities(html)
    out.append(("render: no invalid entities", not bad,
                "" if not bad else "%d: %s" % (sum(bad.values()),
                    ", ".join("%s x%d" % (k, v) for k, v in bad.most_common(6)))))
    leaks = latex_leaks(html)
    out.append(("render: no LaTeX leak", not leaks,
                "" if not leaks else ", ".join("%s x%d" % (k, v) for k, v in leaks.most_common(6))))
    md_leaks = markdown_leaks(html)
    out.append(("render: no Markdown leak", not md_leaks,
                "" if not md_leaks else ", ".join("%s x%d" % (k, v) for k, v in md_leaks.most_common(6))))
    imbalances = tag_imbalances(html)
    out.append(("render: tags balanced", not imbalances,
                "" if not imbalances else ", ".join(
                    "%s open=%d close=%d" % (tag, value[0], value[1])
                    for tag, value in imbalances.items())))
    c = structure(html)
    out += [
        ("structure: >=4 self-checks", c["self_checks"] >= 4, "found %d" % c["self_checks"]),
        ("structure: prediction gate", c["prediction_gate"] >= 1, "found %d" % c["prediction_gate"]),
        ("structure: 2-3 segments", 2 <= c["segments"] <= 3, "found %d" % c["segments"]),
        ("structure: break card(s)", c["breaks"] >= 1, "found %d" % c["breaks"]),
        ("structure: >=1 faded example", c["faded"] >= 1, "found %d" % c["faded"]),
        ("structure: guided proof", c["guided_proof"] >= 1, "found %d" % c["guided_proof"]),
        ("structure: visual (canvas/svg)", c["visual"] >= 1, "found %d" % c["visual"]),
        ("structure: blank-page ending", c["blank_page"] >= 1, "found %d" % c["blank_page"]),
        ("structure: mission strip", c["mission"] >= 1, "found %d" % c["mission"]),
        ("structure: footer citations", c["footer"] >= 1, "found %d" % c["footer"]),
    ]
    return out


def run(path):
    with open(path, encoding="utf-8") as f:
        results = lint(f.read())
    fails = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, (": " + detail) if detail else ""))
    print("\n%d/%d checks passed" % (len(results) - len(fails), len(results)))
    return 1 if fails else 0


def selftest():
    good = ('<div class="mission">m</div><p>Prediction Gate: ?</p>'
            + '<div class="segment"><span class="timebox">t</span></div>' * 2
            + '<div class="break">b</div><div class="worked fade">f</div>'
            + '<div class="guided-proof"><textarea></textarea></div><canvas></canvas>'
            + '<div class="blank-page">reconstruct</div><footer>c</footer>'
            + ''.join('<p><strong>Self-check %d.</strong></p>' % i for i in range(1, 5))
            + '<p>&isin; &ell; &Zopf; &#8484; &amp;</p>')
    total = [0]
    fails = []

    def check(name, cond):
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    def fired(html, needle):
        return any((not ok) and needle in nm for nm, ok, _ in lint(html))

    check("clean lesson passes every check", all(ok for _, ok, _ in lint(good)))
    check("fires on invalid entity", fired(good + "&mathbb;Z", "invalid entities"))
    check("fires on LaTeX leak", fired(good + r"\frac{a}{b}", "LaTeX"))
    check("fires on <4 self-checks",
          fired(good.replace('<strong>Self-check 4.</strong>', ''), "self-checks"))
    check("fires on missing guided proof",
          fired(good.replace('<textarea></textarea>', ''), "guided proof"))
    check("valid entities are NOT flagged (no false positive)",
          not fired(good, "invalid entities"))
    check("entity inside <script> is ignored",
          not fired(good + "<script>var s='&mathbb;';</script>", "invalid entities"))
    check("structure signal inside <script> is ignored",
          fired(good.replace('<textarea></textarea>', '')
                + "<script>var t='<textarea></textarea>';</script>", "guided proof"))
    check("fires on Markdown leak (bold)", fired(good + "**R**", "Markdown"))
    check("fires on Markdown leak (code span)", fired(good + "use `foo()` here", "Markdown"))
    check("valid text is NOT flagged as Markdown leak (no false positive)",
          not fired(good, "Markdown"))
    check("Markdown-looking text inside <script> is ignored",
          not fired(good + "<script>var s='**not markdown**';</script>", "Markdown"))

    # Obs 152: the self-check counter must be label-independent — a lesson
    # using semantic markup (data-ok, class="selfcheck") instead of the
    # literal "Self-check N" prose must still be counted.
    relabelled = good
    for i in range(1, 5):
        relabelled = relabelled.replace(
            '<p><strong>Self-check %d.</strong></p>' % i,
            '<div class="selfcheck"><button data-ok>ok</button>'
            '<button>a</button><button>b</button><div class="explain">e</div></div>',
        )
    check("self-checks counted under a different heading, not just the prose label",
          all(ok for nm, ok, _ in lint(relabelled) if nm == "structure: >=4 self-checks"))
    check("prose label alone still counts as a fallback (regression)",
          all(ok for nm, ok, _ in lint(good) if nm == "structure: >=4 self-checks"))

    gapped = good + '<p class="gap">NOT IN SOURCE: the good-cover hypothesis</p>'
    check("fires on an unresolved gap marker", fired(gapped, "gap markers"))
    check("the gap row names what was declared (drift scoring reads this)",
          any(nm == GAP_CHECK and "good-cover" in d for nm, _, d in lint(gapped)))
    check("a caller can drop the gap row by name and see an otherwise clean lesson",
          all(ok for nm, ok, _ in lint(gapped) if nm != GAP_CHECK))
    check("fires on mismatched sup/sub tags",
          fired(good + "<sup>x</sub>", "tags balanced"))
    check("clean lesson has balanced governed tags",
          not fired(good, "tags balanced"))
    check("optional p end tags are outside the strict balance gate",
          not fired(good + "<p>optional end", "tags balanced"))

    print("\n%d/%d checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    if len(argv) != 1:
        print("usage: lesson_lint.py <lesson_html_path> | --selftest")
        return 2
    return run(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
