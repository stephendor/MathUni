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

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console (cf. srs/scheduler.py)
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

_NAMED = re.compile(r"&([a-zA-Z][a-zA-Z0-9]*);")   # &name;  (numeric &#...; is always valid)
_LATEX = re.compile(r"\\(?:left|right|frac|mathbb|mathbf|mathcal|cdot|times|sqrt"
                    r"|begin|end|leq|geq|neq|infty|sum|int|forall|exists)\b"
                    r"|\\\(|\\\)|\\\[|\\\]|\$\$")   # LaTeX that leaked as text


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


def structure(html):
    html = _strip_code(html)  # count rendered markup only, not <script>/<style> string contents
    def count(pat):
        return len(re.findall(pat, html))
    return {
        "self_checks": count(r"Self-check\s*\d"),
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


def lint(html):
    """Return [(check_name, ok, detail)] — render fidelity first, then structure."""
    out = []
    bad = invalid_entities(html)
    out.append(("render: no invalid entities", not bad,
                "" if not bad else "%d: %s" % (sum(bad.values()),
                    ", ".join("%s x%d" % (k, v) for k, v in bad.most_common(6)))))
    leaks = latex_leaks(html)
    out.append(("render: no LaTeX leak", not leaks,
                "" if not leaks else ", ".join("%s x%d" % (k, v) for k, v in leaks.most_common(6))))
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
