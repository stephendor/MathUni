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
