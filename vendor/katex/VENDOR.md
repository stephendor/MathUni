# KaTeX, vendored

**Version:** 0.16.47 · **Licence:** MIT (see `LICENSE`) · **Upstream:** https://katex.org

## Why it is here and not on a CDN

139 of the 146 problem sets are markdown carrying LaTeX, 78 of them with
display math. Something has to render it, and the college is offline by rule:
`scripts/gate.py` check 5 forbids external requests in lessons, and a problem
set that needs the internet to be legible would be the worse artifact. So KaTeX
ships in the repository and is served same-origin from `/katex/` by
`scripts/serve.py`.

The lessons do not use this. Zero of the 145 lesson files contain `$...$`;
their maths is Unicode written into the HTML by hand. Only the problem sets
took the LaTeX convention, so only the problem-set page loads KaTeX.

## What was copied, and what was not

| Path | Purpose |
|---|---|
| `katex.min.js` | the parser and renderer |
| `contrib/auto-render.min.js` | finds `$…$` / `$$…$$` in the DOM |
| `LICENSE` | upstream MIT licence, unmodified |

**No stylesheet and no fonts**, which is the whole point of the configuration
below: 272 KB instead of 547 KB, and 4 files instead of 24.

## MathML-only, deliberately

`scripts/home.py` calls `renderMathInElement` with `output: 'mathml'`. KaTeX's
default is `htmlAndMathml`, which emits a visual HTML rendering *and* a hidden
MathML copy of every formula. That is fine on its own and fails badly beside
anything else that acts on maths: with a Native MathML browser extension
installed, the extension unhides the MathML while KaTeX's stylesheet is still
clipping it, and every formula on the page renders as a blank space. That was
observed, not imagined.

MathML-only emits one representation, so there is nothing to disagree about.
It also means the browser's own maths engine does the layout — hence no
stylesheet and no web fonts, and one less thing that can fail to load. Two CSS
rules in `PROBLEM_CSS` replace everything the KaTeX stylesheet provided here.

MathML is supported natively by every browser this runs on. The
`<annotation encoding="application/x-tex">` KaTeX embeds carries the original
source, so copy-the-LaTeX tooling still works.

To go back to visual HTML rendering, re-vendor `katex.min.css` and
`fonts/*.woff2` from an upstream `dist/` and drop the `output` option.

## How it is served

`scripts/serve.py` exposes `GET /katex/<path>` through `read_asset`, which
resolves the real path and requires it to sit under the real vendor root — so
a `../` or a symlink cannot escape — and then requires the extension to be on
a small whitelist. That route serves executable JavaScript, so both gates
matter: without the second it could serve `state/` or a `.py` file.
