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

## What was copied

| Path | Purpose |
|---|---|
| `katex.min.css` | layout and the `@font-face` rules |
| `katex.min.js` | the renderer |
| `contrib/auto-render.min.js` | finds `$…$` / `$$…$$` in the DOM |
| `fonts/*.woff2` | 20 files, the complete KaTeX 0.16 woff2 set |
| `LICENSE` | upstream MIT licence, unmodified |

**woff2 only.** The upstream `dist/fonts` also carries `.woff` and `.ttf` of
every face — three times the files for formats no browser this runs on will
ask for, because the `@font-face` `src` lists woff2 first and every supported
browser stops there. 547 KB total instead of roughly 1.6 MB.

Nothing here is modified. To update, replace the files from an upstream
`dist/` of the same shape and change the version above.

## How it is served

`scripts/serve.py` exposes `GET /katex/<path>` through `read_asset`, which
resolves the real path and requires it to sit under the real vendor root — so
a `../` or a symlink cannot escape — and then requires the extension to be on
a five-entry whitelist. That route can serve executable JavaScript, so both
gates matter: without the second one it could serve `state/` or a `.py` file.
