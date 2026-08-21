"""Gates 4-6. Every check here is paired with a control that watches it fire —
a gate nobody has seen fail is a gate nobody knows works (invariant I2b)."""
from scripts.gate import (external_hits, script_bodies, selftest, tag_errors)


# --- gate 4: tag balance --------------------------------------------------

def test_crossed_tags_with_balanced_counts_are_caught():
    """The case lesson_lint.py structurally cannot see: open/close counts match,
    so a counting gate passes it; only a stack notices the ordering."""
    from scripts.lesson_lint import tag_imbalances
    html = "<div><em><strong>x</em></strong></div>"
    assert tag_imbalances(html) == {}      # counting gate: clean
    assert tag_errors(html)                # ordering gate: not clean


def test_unclosed_element_is_caught():
    assert any("never closed" in e for e in tag_errors("<div><span>x</span>"))


def test_stray_end_tag_is_caught_and_named():
    errs = tag_errors("<div>x</div></section>")
    assert len(errs) == 1
    assert "</section> with no matching <section>" in errs[0]


def test_one_stray_p_produces_one_error_not_a_cascade():
    """aa-00 shipped exactly this. The scratchpad gate popped the stack on the
    stray </p>, consuming the open <div>, and then misattributed every close
    after it: four error lines from one defect, three of them wreckage."""
    errs = tag_errors("<html><body><div><strong>x</strong> y</p></div></body></html>")
    assert len(errs) == 1
    assert "</p> with no matching <p>" in errs[0]


def test_omitted_optional_end_tags_are_not_errors():
    assert tag_errors("<div><p>one<p>two</p></div>") == []
    assert tag_errors("<table><tr><td>a<td>b</tr></table>") == []
    assert tag_errors("<ul><li>a<li>b</ul>") == []


def test_p_implicitly_closed_by_a_block_start_is_not_an_error():
    assert tag_errors("<div><p>one<div>two</div></div>") == []


def test_surplus_optional_end_tag_is_still_an_error():
    """Optional means the end tag may be OMITTED, not that a surplus one is
    legal. Excluding <p> from the stack must not excuse this."""
    assert any("</td> with no matching" in e
               for e in tag_errors("<table><tr><td>a</td></td></tr></table>"))


def test_void_elements_do_not_need_closing():
    assert tag_errors("<div><br><img src=x><hr></div>") == []


# --- gate 5: no external requests -----------------------------------------

def test_svg_xmlns_is_not_an_external_request():
    """The false positive that failed an-02, pw-01 and pw-03 while 76 S2-S4
    lessons passed only because their authors omitted the attribute. An XML
    namespace is an identifier; nothing is fetched."""
    assert external_hits('<svg xmlns="http://www.w3.org/2000/svg"></svg>') == []
    assert external_hits("<svg xmlns:xlink='http://www.w3.org/1999/xlink'/>") == []


def test_real_external_references_still_fire():
    assert external_hits('<script src="https://cdn.example.com/x.js"></script>')
    assert external_hits("<style>@import url(x);</style>")
    assert external_hits('<a href="http://example.com">x</a>')
    assert external_hits('<link rel="stylesheet" href="x.css">')


def test_a_line_with_both_a_namespace_and_a_real_url_still_fires():
    """The exemption is scoped to the attribute, not to the line: stripping the
    whole line because it happened to carry an xmlns would be the silent hole."""
    hits = external_hits('<svg xmlns="http://www.w3.org/2000/svg">'
                         '<image href="http://example.com/a.png"/></svg>')
    assert len(hits) == 1


# --- gate 6: inline scripts parse -----------------------------------------

def test_empty_script_bodies_are_not_counted():
    assert script_bodies("<script></script><script>   </script>") == []
    assert script_bodies("<script>var x=1;</script>") == ["var x=1;"]


# --- the committed corpus -------------------------------------------------

def test_selftest_passes():
    assert selftest() == 0
