"""mathdoc.py — problem sets as readable HTML, with the maths left intact.

139 of the 146 problem sets are markdown carrying LaTeX, 78 of them with display
math. Serving that as escaped text in a <pre> made the structure unreadable and
the maths worse than unreadable: `$f^{-1}(\\{0,1,4\\})$` is noise unless
something renders it.

The lessons do not have this problem because they never use LaTeX — 0 of 145
contain `$...$`; their maths is Unicode written into the HTML by hand. The sets
took the other convention, so the sets need a renderer.

Two rules shape what follows.

**Maths is extracted before markdown runs, and restored after.** A subscript
like `x_1` inside `$...$` would otherwise be eaten by the emphasis rule and the
formula silently corrupted — markdown and TeX disagree about `_`, `*` and `\\`,
and the only safe answer is to keep them apart. Every span is replaced by a
placeholder that cannot occur in source text, and put back verbatim.

**Each piece is escaped after its structure is decided, never before.** The
first version escaped the whole document up front, which broke blockquotes: `>`
had already become `&gt;` by the time the rule looked for it. Any block marker
that escapes would fail the same way. So the line's shape is matched on the raw
text, and only the content it contains is escaped. The markup produced here is
a fixed vocabulary of tags; nothing from the file becomes markup by accident.

The markdown subset is deliberately small — headings, rules, emphasis, inline
code, blockquotes, lists, paragraphs, fenced code and tables. That is what the
sets actually use, and the last two are not decoration: the nine lab sets are
261 fences of Python and pinned environments, and six sets use tables as
fill-in grids whose empty cells are the exercise. Both need to survive as
structure, because both are unreadable joined into a paragraph. A
fuller implementation would be more code to be wrong in, and pulling in a real
markdown library for this would add the project's first runtime dependency.
"""
import re
from html import escape

# Delimiters are paired by extract_math's scan, not by a pattern. The regex
# form is genuinely unable to do this job: `$...$` is not a regular language
# once a span may wrap, because deciding where one ends requires knowing which
# `$` opened it, and a pattern applied to the whole document has no such
# memory. See extract_math for what that cost in practice.
#
# What is left here are the two rules that bound a candidate span.
_BLANK_LINE = re.compile(chr(10) + r"[ \t]*" + chr(10))
_WRAP_LIMIT = 4         # formulas wrap once or twice; 4 is slack, not licence

# U+0000 cannot appear in the source files, so a placeholder built from it
# cannot collide with anything an author wrote.
_MARK = "\x00m%d\x00"
_MARK_RE = re.compile("\x00m(\\d+)\x00")

# A fence opens with any info string -- the lab sets write ```python id=env --
# and closes with a bare one. Only the first word is a language.
_FENCE_OPEN = re.compile(r"^\s*```(.*)$")
_FENCE_CLOSE = re.compile(r"^\s*```\s*$")

# A row is a table row only when the NEXT line is a separator. That guard is
# load-bearing: an2-07 line 122 begins `|-1|\,\|\mathbf{v}...` -- a display
# formula broken across two lines, so the inline rule never extracted it -- and
# a shape test on one line alone would render it as a one-cell table.
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_HR = re.compile(r"^\s*(?:---+|\*\*\*+|___+)\s*$")
_ULI = re.compile(r"^\s*[-*+]\s+(.*)$")
_OLI = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")
_QUOTE = re.compile(r"^\s*>\s?(.*)$")

_STRONG = re.compile(r"\*\*(\S(?:.*?\S)?)\*\*")
_EM = re.compile(r"(?<![\w*])\*(\S(?:.*?\S)?)\*(?![\w*])")
_CODE = re.compile(r"`([^`]+)`")

# The sets carry raw HTML, and one piece of it is load-bearing: 2899
# <details>/<summary> pairs across 145 of the 146 files ARE the hint ladder.
# Escaping them does not merely look wrong, it spoils every hint at once by
# printing nudge, strategy, partial and worked answer as plain text.
#
# So a whitelist, and a deliberately narrow one: exact strings, no attribute
# parsing, nothing constructed from the source. `<span class="cite">` is the
# single attribute-bearing form, used six times, and is listed literally rather
# than by allowing attributes on span. Anything else -- an event handler, a
# script, a tag with attributes -- does not match and stays escaped.
_ALLOWED_HTML = (
    "<details>", "</details>", "<summary>", "</summary>",
    "<sub>", "</sub>", "<sup>", "</sup>", "<code>", "</code>",
    '<span class="cite">', "</span>",
)
_UNESCAPE = tuple((escape(tag), tag) for tag in _ALLOWED_HTML)

# <details> and </details> open and close blocks; they must not be wrapped in a
# paragraph, which would be invalid nesting. All 2899 sit on their own line.
_RAW_BLOCK = re.compile(r"^\s*<\/?(?:details|summary)\b")


def _plausible_span(body):
    """True when the text between two `$` is a formula rather than an accident.

    Two guards, and both matter. A blank line ends a paragraph, so a span
    crossing one is a stray `$` that found a later `$`. And a span running over
    more lines than a formula plausibly needs is the same mistake in slower
    motion: "costs $5 today", six lines down "$7", must not become one span
    that eats the text between them.
    """
    return (body
            and not _BLANK_LINE.search(body)
            and body.count(chr(10)) <= _WRAP_LIMIT)


def extract_math(text):
    """(text with placeholders, [math spans]). Display spans keep their $$.

    One left-to-right scan, not a sequence of regex passes, because delimiters
    have to be paired in the order they were written. Two passes -- single-line
    first, then wrapped -- looks equivalent and is not: at1-08's Partial block
    opens a formula on one line and closes it on the next, so the single-line
    rule reached the continuation line first, paired the closing `$` of the
    wrapped formula with the opening `$` of the NEXT one, and took `$, using $`
    as a span. Both real formulas were then left with one delimiter each, the
    `+ ` that began the continuation became a bullet, and the page showed a
    paragraph, a one-item list and half a formula.

    Pairing left to right also removes a subtler hazard for free: this reads
    the source once and never rescans its own output, so a span cannot swallow
    a placeholder written by an earlier pass.
    """
    spans, out, i, n = [], [], 0, len(text)

    def take(raw):
        spans.append(raw)
        return _MARK % (len(spans) - 1)

    while i < n:
        at = text.find("$", i)
        if at == -1:
            out.append(text[i:])
            break
        out.append(text[i:at])

        if text.startswith("$$", at):
            end = text.find("$$", at + 2)
            if end != -1:
                out.append(take(text[at:end + 2]))
                i = end + 2
                continue
            # An unclosed `$$` is a typo, not a licence to eat the document.
            out.append("$")
            i = at + 1
            continue

        end = text.find("$", at + 1)
        if end != -1 and _plausible_span(text[at + 1:end]):
            out.append(take(text[at:end + 1]))
            i = end + 1
            continue
        # No partner, or an implausible one: a literal dollar sign. Resume
        # AFTER it so the rejected closer can still open a span of its own.
        out.append("$")
        i = at + 1

    return "".join(out), spans


def restore_math(html_text, spans):
    """Put the spans back, HTML-escaped.

    Escaped, not raw: a formula may contain `<` or `&`, and KaTeX reads the
    element's text content, so entities arrive at the parser as the characters
    the author wrote.
    """
    return _MARK_RE.sub(lambda m: escape(spans[int(m.group(1))]), html_text)


def _text(raw):
    """Escape, then mark up. Structure is matched on the RAW line before this.

    Doing it the other way round was a bug: `>` becomes `&gt;` when escaped, so
    the blockquote pattern stopped matching its own syntax. Any block rule
    whose marker escapes would have the same problem, so escaping happens per
    piece, after the line's shape has been decided.
    """
    text = escape(raw)
    for escaped, tag in _UNESCAPE:
        text = text.replace(escaped, tag)
    return _inline(text)


def _inline(text):
    """Emphasis and code, on already-escaped text."""
    text = _CODE.sub(lambda m: "<code>%s</code>" % m.group(1), text)
    text = _STRONG.sub(lambda m: "<strong>%s</strong>" % m.group(1), text)
    return _EM.sub(lambda m: "<em>%s</em>" % m.group(1), text)


def _close(out, stack):
    while stack:
        out.append("</%s>" % stack.pop())


def _cells(line):
    """Split a table row on `|`.

    Safe only because maths came out first. Cells routinely contain `|` --
    `$\\|x\\|$`, `$\\{x \\mid P\\}$` -- and splitting the raw line would cut
    formulae in half. By here every span is an opaque placeholder.
    """
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _table(header, rows):
    parts = ["<table><thead><tr>"]
    parts += ["<th>%s</th>" % _text(c) for c in header]
    parts.append("</tr></thead><tbody>")
    for row in rows:
        parts.append("<tr>%s</tr>"
                     % "".join("<td>%s</td>" % _text(c) for c in row))
    parts.append("</tbody></table>")
    return "".join(parts)


def to_html(markdown):
    """The markdown subset the problem sets actually use."""
    protected, spans = extract_math(markdown)
    out, stack, para, item = [], [], [], []

    def flush():
        if para:
            out.append("<p>%s</p>" % _text(" ".join(para)))
            para.clear()

    def flush_item():
        """Emit the list item being accumulated, if any.

        Items are buffered rather than written per physical line because a
        wrapped item is one item. lab-07's numbered source notes each run to
        three or four lines; emitting each line as a complete <li> restarted
        the <ol> at every real item, so the page showed a column of lists all
        numbered 1, and `**bold**` split across two lines lost its pairing and
        printed its own asterisks.
        """
        if item:
            out.append("<li>%s</li>" % _text(" ".join(item)))
            item.clear()

    def close_blocks():
        """Finish the open item, then the open list. Order matters: closing
        </ul> around an unflushed item drops it entirely."""
        flush_item()
        _close(out, stack)

    # An index, not `for`: fences and tables consume more than one line.
    lines = protected.split(chr(10))
    idx = -1
    while idx + 1 < len(lines):
        idx += 1
        line = lines[idx].rstrip()

        if not line.strip():
            flush()
            close_blocks()
            continue

        # Fenced code, verbatim. The nine lab sets are 261 fences of Python,
        # pinned environments and expected output; run through the ordinary
        # rules they lose their indentation, join into one paragraph, and every
        # `#` comment becomes an <h1>. KaTeX ignores <pre>/<code> by default,
        # so a `$` inside a fence stays a dollar sign.
        fence = _FENCE_OPEN.match(line)
        if fence:
            flush()
            close_blocks()
            body = []
            idx += 1
            while idx < len(lines) and not _FENCE_CLOSE.match(lines[idx].rstrip()):
                body.append(lines[idx])
                idx += 1
            lang = fence.group(1).strip().split(" ")[0]
            out.append("<pre><code%s>%s</code></pre>"
                       % (' class="lang-%s"' % escape(lang) if lang else "",
                          escape(chr(10).join(body))))
            continue

        if (_TABLE_ROW.match(line) and idx + 1 < len(lines)
                and _TABLE_SEP.match(lines[idx + 1].rstrip())):
            flush()
            close_blocks()
            header = _cells(line)
            idx += 1                                    # the separator row
            rows = []
            while idx + 1 < len(lines) and _TABLE_ROW.match(lines[idx + 1].rstrip()):
                idx += 1
                rows.append(_cells(lines[idx].rstrip()))
            out.append(_table(header, rows))
            continue

        if _RAW_BLOCK.match(line):
            # A whitelisted block tag: emit it as markup, unwrapped.
            flush()
            close_blocks()
            out.append(_text(line.strip()))
            continue

        if _HR.match(line):
            flush()
            close_blocks()
            out.append("<hr>")
            continue

        heading = _HEADING.match(line)
        if heading:
            flush()
            close_blocks()
            level = len(heading.group(1))
            out.append("<h%d>%s</h%d>" % (level, _text(heading.group(2)), level))
            continue

        quote = _QUOTE.match(line)
        if quote:
            flush()
            if stack[-1:] != ["blockquote"]:
                close_blocks()
                out.append("<blockquote>")
                stack.append("blockquote")
            out.append("<p>%s</p>" % _text(quote.group(1)))
            continue

        bullet = _ULI.match(line)
        ordered = None if bullet else _OLI.match(line)
        if bullet or ordered:
            flush()
            tag = "ul" if bullet else "ol"
            if stack[-1:] != [tag]:
                close_blocks()
                out.append("<%s>" % tag)
                stack.append(tag)
            else:
                flush_item()        # the previous item ends where this begins
            item.append((bullet.group(1) if bullet else ordered.group(2)).strip())
            continue

        # An indented line under an open list continues the item above it
        # rather than ending the list. Indentation is the signal markdown
        # itself uses, and it is what the authored sets wrote.
        if item and stack[-1:] in (["ul"], ["ol"]) and lines[idx][:1] in (" ", "	"):
            item.append(line.strip())
            continue

        if stack:
            close_blocks()
        para.append(line.strip())

    flush()
    close_blocks()
    return restore_math("\n".join(out), spans)
