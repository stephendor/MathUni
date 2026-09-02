from scripts.mathdoc import extract_math, restore_math, to_html

D = "$"


# --- maths survives markdown, which is the whole point ----------------------

def test_subscripts_are_not_eaten_by_emphasis():
    """`x_1 ... x_n` inside maths would otherwise become an <em> and the formula
    would be silently corrupted. markdown and TeX disagree about `_`."""
    out = to_html("Let %sx_1 + x_2 = y_n%s hold." % (D, D))
    assert "$x_1 + x_2 = y_n$" in out
    assert "<em>" not in out


def test_asterisks_inside_maths_are_left_alone():
    out = to_html("Take %sa * b * c%s." % (D, D))
    assert "$a * b * c$" in out
    assert "<strong>" not in out and "<em>" not in out


def test_display_math_is_not_split_by_the_inline_rule():
    out = to_html("%s%s" % (D * 2, "\\int_0^1 f = 1" + D * 2))
    assert "$$\\int_0^1 f = 1$$" in out


def test_backslash_braces_survive():
    out = to_html("Compute %sf^{-1}(\\{0,1,4\\})%s." % (D, D))
    assert "f^{-1}(\\{0,1,4\\})" in out


def test_maths_containing_angle_brackets_is_escaped_not_dropped():
    """KaTeX reads text content, so `<` must arrive as an entity."""
    out = to_html("%sa < b%s" % (D, D))
    assert "&lt;" in out
    assert "<b>" not in out


def test_two_inline_spans_on_one_line_stay_separate():
    out = to_html("%sa%s and %sb%s" % (D, D, D, D))
    assert "$a$" in out and "$b$" in out


def test_a_lone_dollar_does_not_swallow_the_document():
    out = to_html("costs $5 today\nand more tomorrow")
    assert "and more tomorrow" in out


# --- the markdown subset ----------------------------------------------------

def test_headings_become_headings():
    out = to_html("# Title\n\n## Section")
    assert "<h1>Title</h1>" in out and "<h2>Section</h2>" in out


def test_horizontal_rule():
    assert "<hr>" in to_html("a\n\n---\n\nb")


def test_bold_and_italic():
    out = to_html("**Module:** *Proof* text")
    assert "<strong>Module:</strong>" in out and "<em>Proof</em>" in out


def test_inline_code():
    assert "<code>/grade pw-03</code>" in to_html("Submit via `/grade pw-03`.")


def test_unordered_list():
    out = to_html("- one\n- two")
    assert out.count("<li>") == 2 and "<ul>" in out and "</ul>" in out


def test_ordered_list():
    out = to_html("1. first\n2. second")
    assert "<ol>" in out and out.count("<li>") == 2


def test_blockquote():
    assert "<blockquote>" in to_html("> quoted line")


def test_paragraphs_are_separated_by_blank_lines():
    out = to_html("one line\nsame para\n\nnew para")
    assert out.count("<p>") == 2


def test_lists_close_before_a_following_paragraph():
    out = to_html("- item\n\nafter")
    assert out.index("</ul>") < out.index("<p>after</p>")


# --- escaping ---------------------------------------------------------------

def test_html_in_the_source_is_escaped():
    out = to_html("<script>alert(1)</script> & co")
    assert "<script>alert(1)</script>" not in out
    assert "&lt;script&gt;" in out and "&amp; co" in out


def test_markup_vocabulary_is_fixed():
    """Nothing in the file becomes a tag by accident: escaping happens first."""
    out = to_html("<img onerror=x> and <div>")
    assert "<img" not in out and "<div>" not in out


# --- the round trip ---------------------------------------------------------

def test_extract_then_restore_is_lossless():
    src = "Let %sx_1%s and %s%sy=2%s%s end." % (D, D, D, D, D, D)
    protected, spans = extract_math(src)
    assert "$" not in protected, "every span must be taken out"
    assert restore_math(protected, spans) == src


def test_a_document_with_no_maths_is_unchanged_in_substance():
    protected, spans = extract_math("plain text only")
    assert spans == [] and protected == "plain text only"


def test_a_real_set_opening_renders():
    src = (
        "# pw-03 " + chr(8212) + " Sets, functions\n\n"
        "**Module:** Proof Workshop " + chr(183) + " **Unit:** pw-03\n\n"
        "---\n\n"
        "## Problem 1 (easy)\n\n"
        "Let %sA = \\{-4,-3\\}%s and %sf : A \\to B%s be %sf(x) = x^2%s.\n"
        % (D, D, D, D, D, D)
    )
    out = to_html(src)
    assert "<h1>" in out and "<h2>" in out and "<hr>" in out
    assert "<strong>Module:</strong>" in out
    assert "f(x) = x^2" in out
    assert "\\to" in out


# --- the whole corpus, not a sample -----------------------------------------

def test_every_problem_set_renders_without_losing_or_corrupting_maths():
    """146 sets, 139 with LaTeX. Unit tests cover constructs I thought of; this
    covers the ones the authors actually wrote.

    The dollar count is the corruption check: markdown processing that ate a
    delimiter, or a placeholder that failed to come back, changes it. It cannot
    prove the maths is *right*, but it proves none went missing.
    """
    import glob
    import pathlib as pl

    root = pl.Path(__file__).resolve().parents[1]
    sets = sorted(glob.glob(str(root / "problems" / "sets" / "*.md")))
    assert len(sets) > 100, "corpus should be substantial; found %d" % len(sets)

    failures = []
    for path in sets:
        src = pl.Path(path).read_text(encoding="utf-8")
        try:
            out = to_html(src)
        except Exception as exc:            # noqa: BLE001 - report, do not raise
            failures.append((pl.Path(path).name, repr(exc)))
            continue
        if chr(0) in out:
            failures.append((pl.Path(path).name, "placeholder left unrestored"))
        if src.count("$") != out.count("$"):
            failures.append((pl.Path(path).name, "maths delimiters changed: %d -> %d"
                             % (src.count("$"), out.count("$"))))
        for tag in ("<script", "<iframe", "<img "):
            if tag in out.lower():
                failures.append((pl.Path(path).name, "unescaped %s" % tag))
    assert failures == [], failures[:8]

# --- the hint ladder, which is raw HTML and load-bearing --------------------

def test_details_blocks_survive_as_markup_not_text():
    """2899 <details>/<summary> pairs across 145 of 146 sets ARE the hint
    ladder. Escaping them does not just look wrong -- it prints nudge, strategy
    and worked answer as plain text, spoiling every hint at once."""
    src = ("<details><summary>Nudge</summary>" + chr(10)
           + "Try the definition." + chr(10) + "</details>")
    out = to_html(src)
    assert "<details><summary>Nudge</summary>" in out
    assert "</details>" in out
    assert "&lt;details&gt;" not in out


def test_details_are_not_wrapped_in_a_paragraph():
    """<p><details> is invalid nesting; all 2899 sit on their own line."""
    out = to_html("<details><summary>S</summary>" + chr(10) + "body" + chr(10)
                  + "</details>")
    assert "<p><details>" not in out
    assert out.startswith("<details>")


def test_inline_html_the_sets_use_is_kept():
    for src, want in (("x<sub>1</sub>", "<sub>1</sub>"),
                      ("2<sup>n</sup>", "<sup>n</sup>"),
                      ('<span class="cite">p. 136</span>', 'class="cite"')):
        assert want in to_html(src), src


def test_anything_outside_the_whitelist_stays_escaped():
    """The whitelist is exact strings, so no attribute can ride in on one."""
    for attack in ("<img onerror=alert(1)>",
                   "<details onclick=steal()>",
                   "<summary style=x>",
                   "<script>alert(1)</script>",
                   "<iframe src=evil>",
                   '<span class="cite" onclick=x>',
                   "<a href=javascript:alert(1)>x</a>"):
        out = to_html(attack)
        assert "onerror" not in out or "&lt;img" in out
        assert "<script" not in out.lower()
        assert "<iframe" not in out.lower()
        assert "<a " not in out.lower()
        if "onclick" in attack or "style=" in attack:
            assert "&lt;" in out, attack


# --- fenced code, which is the whole of the lab sets ------------------------

F = "`" * 3


def test_fenced_code_keeps_its_lines_and_indentation():
    """261 fences across the nine lab sets. Through the ordinary rules they
    lose indentation, join into one paragraph, and `#` comments become <h1>."""
    out = to_html(F + "python\nfor i in x:\n    # step\n    f(i)\n" + F)
    assert "<pre><code" in out and "</code></pre>" in out
    assert "    # step" in out
    assert "<h1>" not in out


def test_fence_info_string_yields_only_the_language():
    """The labs write ```python id=env; the id is not part of the language."""
    out = to_html(F + "python id=env\nx = 1\n" + F)
    assert 'class="lang-python"' in out


def test_fence_body_is_escaped_not_interpreted():
    out = to_html(F + "\n<script>alert(1)</script>\n" + F)
    assert "&lt;script&gt;" in out and "<script>alert(1)" not in out


def test_an_unclosed_fence_does_not_lose_the_rest_of_the_file():
    out = to_html(F + "python\nx = 1\nstill here")
    assert "still here" in out


def test_markdown_inside_a_fence_is_left_alone():
    out = to_html(F + "\n**not bold** and *not italic*\n" + F)
    assert "<strong>" not in out and "<em>" not in out


# --- tables -----------------------------------------------------------------

def test_a_table_becomes_a_table():
    out = to_html("| a | b |\n|---|---|\n| 1 | 2 |")
    assert "<table>" in out and out.count("<th>") == 2
    assert out.count("<tr>") == 2 and out.count("<td>") == 2


def test_empty_cells_survive_because_the_grids_are_fill_in():
    out = to_html("| Equation | unique? |\n|---|---|\n| x | |")
    assert "<td></td>" in out


def test_maths_in_a_cell_is_not_split_on_its_own_pipes():
    """Cells carry `$\\|x\\|$` and `$\\{x \\mid P\\}$`; splitting the raw line
    would cut the formula in half. Extraction happens first for this reason."""
    out = to_html("| n | v |\n|---|---|\n| %s\\|x\\|%s | %s\\{a \\mid b\\}%s |"
                  % (D, D, D, D))
    assert out.count("<td>") == 2
    assert "\\|x\\|" in out and "\\mid" in out


def test_a_leading_pipe_line_is_not_a_table_without_a_separator():
    """an2-07 line 122 opens with `|-1|\\,\\|...` -- a display formula broken
    across lines, so the inline rule never extracted it. A one-line shape test
    would render it as a table."""
    out = to_html("some text\n|-1|\\,\\|v-u\\| = 1\nmore text")
    assert "<table>" not in out


def test_the_separator_row_is_not_emitted_as_content():
    out = to_html("| a |\n|---|\n| 1 |")
    assert "---" not in out


def test_a_table_closes_before_the_following_paragraph():
    out = to_html("| a |\n|---|\n| 1 |\n\nafter")
    assert out.index("</table>") < out.index("<p>after</p>")


def test_every_lab_and_table_set_renders_its_structure():
    """The corpus check counts dollars; this one checks the blocks arrived."""
    import pathlib as pl

    root = pl.Path(__file__).resolve().parents[1]
    for name in ("lab-01", "lab-05", "lab-09"):
        out = to_html((root / "problems" / "sets" / ("%s.md" % name))
                      .read_text(encoding="utf-8"))
        assert "<pre><code" in out, name
    for name in ("an2-04", "an2-05", "cap-01"):
        out = to_html((root / "problems" / "sets" / ("%s.md" % name))
                      .read_text(encoding="utf-8"))
        assert "<table>" in out, name
        assert "|---|" not in out, name


def test_the_whitelist_carries_no_attribute_parsing():
    """It is a tuple of literal strings; nothing is built from the source."""
    from scripts.mathdoc import _ALLOWED_HTML

    assert all(isinstance(t, str) for t in _ALLOWED_HTML)
    attributed = [t for t in _ALLOWED_HTML if " " in t]
    assert attributed == ['<span class="cite">'], attributed


# --- formulas that wrap, which the block rules would otherwise cut in half ---

def test_a_formula_wrapping_onto_a_plus_line_stays_one_span():
    """at1-08 lines 102-103 and at1-07 lines 68-69 both break an inline span
    with the continuation starting `+ `, which _ULI reads as a bullet. KaTeX
    was handed two halves with unmatched delimiters."""
    src = (r"(a) %s|f_t(x)|^2 = \cos^2 t\,|x|^2" % D + chr(10)
           + r"+ \sin^2 t\,|v(x)|^2 = 1%s, using the norm." % D)
    out = to_html(src)
    assert "<ul>" not in out and "<li>" not in out
    assert out.count("$") == 2, out


def test_a_wrapped_formula_does_not_cross_a_blank_line():
    """A blank line ends a paragraph, so a span crossing one is a stray `$`
    finding a later `$`, not a formula."""
    out = to_html("costs %s5 today" % D + chr(10) * 2 + "and %s7 tomorrow" % D)
    assert "and " in out and "today" in out
    assert out.count("<p>") == 2


def test_a_wrapped_span_is_bounded_in_length():
    """Two lone dollars far apart must not become one span that eats the text
    between them."""
    body = chr(10).join("line %d" % i for i in range(8))
    out = to_html("costs %s5" % D + chr(10) + body + chr(10) + "or %s7" % D)
    for i in range(8):
        assert "line %d" % i in out


def test_a_wrapped_span_never_swallows_an_existing_placeholder():
    """Both passes run on text that already holds placeholders. A span that
    swallowed one would be stored WITH it, and restore_math substitutes in a
    single pass -- so the buried placeholder reappears as a NUL in the page."""
    src = ("%s%sx=1%s%s and %sa" % (D, D, D, D, D) + chr(10)
           + "+ b%s tail" % D)
    out = to_html(src)
    assert chr(0) not in out
    assert out.count("$") == src.count("$")


def test_the_whole_corpus_still_balances_after_the_wrapped_pass():
    import glob
    import pathlib as pl

    root = pl.Path(__file__).resolve().parents[1]
    for path in sorted(glob.glob(str(root / "problems" / "sets" / "*.md"))):
        src = pl.Path(path).read_text(encoding="utf-8")
        out = to_html(src)
        assert chr(0) not in out, pl.Path(path).name
        assert src.count("$") == out.count("$"), pl.Path(path).name


# --- list items that wrap ---------------------------------------------------

def test_a_wrapped_list_item_stays_one_item():
    """lab-07's numbered source notes run to three or four lines each. Emitting
    each physical line as a complete <li> restarted the <ol> at every real
    item, so the page showed a column of lists all numbered 1."""
    out = to_html("1. first line" + chr(10) + "   continued here" + chr(10)
                  + "2. second item")
    assert out.count("<ol>") == 1
    assert out.count("<li>") == 2
    assert "first line continued here" in out


def test_bold_split_across_a_wrapped_item_still_pairs():
    out = to_html("1. **This unit was drafted" + chr(10)
                  + "   against a broken environment.** Rest.")
    assert "<strong>" in out and "**" not in out


def test_an_unindented_line_after_a_list_still_ends_it():
    out = to_html("- item" + chr(10) + "not indented")
    assert out.index("</ul>") < out.index("not indented")


def test_a_wrapped_bullet_item_works_too():
    out = to_html("- first" + chr(10) + "  more" + chr(10) + "- second")
    assert out.count("<li>") == 2 and "first more" in out


def test_lab_07_renders_one_list_not_a_column_of_them():
    import pathlib as pl

    root = pl.Path(__file__).resolve().parents[1]
    out = to_html((root / "problems" / "sets" / "lab-07.md")
                  .read_text(encoding="utf-8"))
    assert out.count("<ol>") == 1, "one list, not one per line"


def test_a_wrapped_formula_is_not_mispaired_by_a_later_one():
    r"""The two-pass version's actual failure, and it is not obvious.

    at1-08's Partial block opens `$|f_t(x)|^2 = ...` on one line and closes it
    on the next, and that next line ALSO opens a second formula. A single-line
    pass reaching the continuation line first sees `$, using $` -- the closing
    delimiter of the wrapped formula and the opening delimiter of the next one
    -- and takes that as a span. Both real formulas are then left holding one
    delimiter each. Pairing left to right is what prevents it.
    """
    src = ("(a) %s|f|^2 = a" % D + chr(10)
           + "+ b = 1%s, using %s|x| = 1%s and more." % (D, D, D))
    out = to_html(src)
    assert "<li>" not in out and "<ul>" not in out
    assert "$|f|^2 = a" + chr(10) + "+ b = 1$" in out, out
    assert "$|x| = 1$" in out, out


def test_at1_08_and_at1_07_render_their_wrapped_formulas_whole():
    import pathlib as pl
    import re

    root = pl.Path(__file__).resolve().parents[1]
    for name, key in (("at1-08", r"\cos^2 t\,|x|^2"),
                      ("at1-07", r"\partial_{n-1}\partial_n(\sigma)")):
        out = to_html((root / "problems" / "sets" / ("%s.md" % name))
                      .read_text(encoding="utf-8"))
        block = re.search(r"<p>[^<]*" + re.escape(key) + r".*?</p>", out, re.S)
        assert block, name
        assert "<li>" not in block.group(0), name
        assert block.group(0).count("$") % 2 == 0, name


def test_an_unclosed_display_delimiter_is_not_a_licence():
    out = to_html("%sx = 1" % (D * 2) + chr(10) + "still here")
    assert "still here" in out


def test_a_rejected_closer_can_still_open_its_own_span():
    """Resuming after the rejected `$` rather than after the whole candidate:
    the second dollar may be the real opening delimiter."""
    out = to_html("cost $5" + chr(10) * 2 + "then %sx = 1%s done" % (D, D))
    assert "$x = 1$" in out


# --- fenced code is opaque to the math scanner ------------------------------

F3 = "`" * 3


def test_a_dollar_inside_a_fence_does_not_pair_with_math_after_it():
    """Math is paired before block structure is known. Without a fence guard
    the `$` in the code pairs with the opening `$` of the formula below, the
    captured span CONTAINS the closing fence line, the fence loop never finds
    its terminator, and the rest of the document renders as code."""
    src = (F3 + "bash" + chr(10) + "echo $HOME" + chr(10) + F3 + chr(10)
           + "then %sx = 1%s follows." % (D, D))
    out = to_html(src)
    assert "<pre><code" in out and "</code></pre>" in out
    assert "$x = 1$" in out
    assert "echo $HOME" in out
    assert out.count("<pre>") == 1


def test_the_document_after_a_fence_is_not_swallowed():
    src = (F3 + chr(10) + "cost $5" + chr(10) + F3 + chr(10)
           + "# A heading" + chr(10) + chr(10) + "a paragraph")
    out = to_html(src)
    assert "<h1>A heading</h1>" in out
    assert "<p>a paragraph</p>" in out


def test_math_inside_a_fence_stays_literal():
    src = F3 + "python" + chr(10) + "s = %sa + b%s" % (D, D) + chr(10) + F3
    out = to_html(src)
    assert "<pre><code" in out
    assert chr(0) not in out


def test_fenced_ranges_covers_the_fence_lines_themselves():
    from scripts.mathdoc import fenced_ranges

    src = "before" + chr(10) + F3 + chr(10) + "code" + chr(10) + F3 + chr(10) + "after"
    ranges = fenced_ranges(src)
    assert len(ranges) == 1
    start, stop = ranges[0]
    assert src[start:stop].startswith(F3) and src[start:stop].endswith(F3)
    assert "before" not in src[start:stop] and "after" not in src[start:stop]


def test_an_unterminated_fence_runs_to_the_end():
    """Matching what to_html does with one, so the two cannot disagree about
    where the code stops."""
    from scripts.mathdoc import fenced_ranges

    src = "before" + chr(10) + F3 + chr(10) + "code"
    assert fenced_ranges(src)[0][1] == len(src)


# --- quoted passages are paragraphs, not stacks of lines --------------------

def test_a_wrapped_quote_is_one_paragraph():
    """aa-00 lines 8-12 are a five-line note; a <p> per physical line showed it
    as a stack of sentence fragments with margins between arbitrary wraps."""
    out = to_html("> first line of the note" + chr(10)
                  + "> second line of it" + chr(10)
                  + "> and the third")
    assert out.count("<p>") == 1
    assert "first line of the note second line of it and the third" in out


def test_a_bare_quote_marker_separates_quoted_paragraphs():
    """lab-07 lines 492-498 use exactly this to hold two definitions."""
    out = to_html("> Definition one." + chr(10) + ">" + chr(10)
                  + "> Theorem two.")
    assert out.count("<blockquote>") == 1
    assert out.count("<p>") == 2


def test_a_quote_still_closes_before_following_prose():
    out = to_html("> quoted" + chr(10) + chr(10) + "after")
    assert out.index("</blockquote>") < out.index("<p>after</p>")


def test_bold_wrapped_across_quoted_lines_pairs():
    out = to_html("> **Definition 13.10 (Fréchet function)," + chr(10)
                  + "> printed 406.** Given a distribution.")
    assert "<strong>" in out and "**" not in out


def test_the_corpus_quotes_render_as_paragraphs():
    import pathlib as pl
    import re

    root = pl.Path(__file__).resolve().parents[1]
    out = to_html((root / "problems" / "sets" / "aa-00.md")
                  .read_text(encoding="utf-8"))
    block = re.search(r"<blockquote>.*?</blockquote>", out, re.S).group(0)
    assert block.count("<p>") == 1, block[:200]
