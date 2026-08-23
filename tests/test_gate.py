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


# --- Codex review of PR #20 ------------------------------------------------
# Four findings against gates 4-6, all four reproduced before being fixed.

def test_crossed_optional_end_elements_are_caught():
    """Per-tag counters lose the nesting order, so this came back clean —
    a crossed pair, which is the one thing gate 4 exists for and the one thing
    lesson_lint.py's counting approach structurally cannot see. `</tr>`
    implicitly closes the cell; the trailing `</td>` is then surplus."""
    errs = tag_errors("<table><tr><td>x</tr></td></table>")
    assert any("</td> with no matching" in e for e in errs)


def test_omitted_table_end_tags_are_still_fine():
    """The fix must not make ordinary spec-legal omission an error."""
    assert tag_errors("<table><tr><td>a<td>b</tr></table>") == []
    assert tag_errors("<table><thead><tr><th>h</thead><tbody><tr><td>d</tbody></table>") == []


def test_self_closing_non_void_html_is_reported():
    """Browsers ignore the slash on a non-void HTML element and leave it open,
    where it can absorb the rest of the document."""
    assert any("does not self-close" in e for e in tag_errors("<body><div/></body>"))
    assert any("does not self-close" in e for e in tag_errors("<section/>"))


def test_self_closing_inside_svg_is_foreign_content_and_legal():
    """The corpus really does ship these — an-02, pw-01, tda2-02."""
    assert tag_errors('<svg><circle cx="1"/><path d="M0 0"/></svg>') == []
    assert tag_errors("<div><svg><rect/></svg><br/></div>") == []


def test_self_closing_after_the_svg_closes_is_caught_again():
    """The foreign-content exemption must not leak past </svg>."""
    assert any("does not self-close" in e
               for e in tag_errors("<svg><circle/></svg><div/>"))


def test_protocol_relative_urls_are_external_requests():
    """`//host/x` is a real fetch that neither `https?://` nor `src=` matches."""
    assert external_hits("<style>body{background:url(//example.com/a.png)}</style>")
    assert external_hits('<video poster="//example.com/a.jpg"></video>')


def test_a_javascript_comment_is_not_an_external_request():
    """The obvious false positive the `//` pattern invites."""
    assert external_hits("<script>// set up the canvas\nvar x=1;</script>") == []
    assert external_hits("<p>the ratio a//b is not a url</p>") == []


def test_non_javascript_script_blocks_are_not_sent_to_node():
    """`<script type="application/json">{"x": 1}</script>` is data. node --check
    rejects it as JavaScript, failing a valid offline lesson."""
    from scripts.gate import script_blocks
    assert script_bodies('<script type="application/json">{"x": 1}</script>') == []
    assert len(script_blocks('<script type="application/json">{"x":1}</script>')) == 1


def test_javascript_script_blocks_are_still_checked():
    """The type carve-out must not become a way to skip real scripts."""
    assert len(script_bodies("<script>var x=1;</script>")) == 1
    assert len(script_bodies('<script type="module">let x = 1;</script>')) == 1
    assert len(script_bodies('<script type="text/javascript">var y=2;</script>')) == 1


# --- Codex review of PR #20, second round ----------------------------------

def test_the_optional_end_list_is_complete_not_just_sufficient():
    """Gate 4 is a hard corpus gate that promises to accept spec-legal
    omission. An eleven-element list reported three errors on a document that
    is entirely valid — html, head, body, colgroup, rt and rp were missing."""
    assert tag_errors("<!doctype html><html><head><title>x</title>"
                      "<body><p>ok") == []
    assert tag_errors("<table><colgroup><col><col><tbody><tr><td>a</table>") == []
    assert tag_errors("<ruby>x<rt>y<rp>)</ruby>") == []


def test_html_and_body_are_not_implicitly_closed_by_a_start_tag():
    """Their end tags may be omitted at EOF, but nothing closes them early.
    Giving them a close-on-any-start rule made the first <div> of every lesson
    close <body>, which then made the document's own </body> a surplus tag."""
    assert tag_errors("<html><body><div>x</div></body></html>") == []
    assert any("</body> with no matching" in e
               for e in tag_errors("<html><body>x</body></body></html>"))


def test_col_keeps_colgroup_open_but_anything_else_closes_it():
    assert tag_errors("<table><colgroup><col><col></colgroup></table>") == []
    assert tag_errors("<table><colgroup><col><tr><td>a</table>") == []


def test_a_javascript_type_with_parameters_is_still_checked():
    """An exact-string type compare skipped a browser-executable block, which
    is a false PASS for any syntax error inside it. Skipping is the dangerous
    direction, so the classifier must be the permissive one."""
    assert len(script_bodies('<script type="text/javascript; charset=utf-8">'
                             "var x=1;</script>")) == 1
    assert len(script_bodies('<script type="  TEXT/JavaScript ">x</script>')) == 1


def test_a_non_javascript_type_with_parameters_is_still_skipped():
    assert script_bodies('<script type="application/json; charset=utf-8">'
                         '{"x":1}</script>') == []


# --- Codex review of PR #20, fourth round -----------------------------------

def test_a_data_type_attribute_is_not_read_as_the_script_type():
    """`\btype` also matches inside `data-type`, because `-` is a word
    boundary. An executable script carrying data-type="application/json" was
    classified as JSON and skipped — a false PASS for any syntax error in it."""
    from scripts.gate import script_blocks
    assert script_blocks('<script data-type="application/json">var x=1;</script>') \
        == [("", "var x=1;")]
    assert len(script_bodies('<script data-type="application/json">x</script>')) == 1
    # the real attribute is still read
    assert script_blocks('<script type="application/json">{"x":1}</script>') \
        == [("application/json", '{"x":1}')]


def test_a_self_closing_foreign_root_is_legal():
    """<svg/> reaches handle_startendtag with foreign depth still 0, since
    nothing has entered foreign content yet — so a legal empty root was being
    reported as malformed."""
    assert tag_errors("<div><svg/></div>") == []
    assert tag_errors("<div><math/></div>") == []
    assert any("does not self-close" in e for e in tag_errors("<body><div/></body>"))


def test_end_tags_for_void_elements_are_rejected():
    """Browsers do not merely drop `</br>`: the HTML parser treats it as a
    `<br>` START tag and inserts a line break nobody wrote."""
    for bad in ("<div>a</br>b</div>", "<div></img></div>", "<div></input></div>"):
        assert any("is void and cannot have an end tag" in e
                   for e in tag_errors(bad)), bad
    assert tag_errors("<div>a<br>b<br/>c<img src=x></div>") == []


def test_a_top_level_return_in_a_classic_script_is_rejected():
    """`node --check` parses under CommonJS, which wraps the body in a
    function, so a top-level `return` was accepted and gate 6 printed PASS for
    `<script>return 1;</script>` — which a browser refuses outright. vm.Script
    compiles under the Script grammar a classic inline <script> actually gets."""
    from scripts.gate import script_errors
    bad, n = script_errors(["return 1;"])
    assert n == 1 and bad and "Illegal return" in bad[0]


def test_valid_classic_and_module_scripts_still_pass():
    from scripts.gate import script_errors
    assert script_errors(["var x=1; function f(){ return 2; }"])[0] == []
    assert script_errors(["let x = 1; export {x};"], [True])[0] == []


def test_a_module_is_parsed_with_the_module_grammar():
    """An `export` is a syntax error in a classic script and fine in a module;
    the two paths must not be swapped."""
    from scripts.gate import script_errors
    assert script_errors(["let x = 1; export {x};"], [False])[0] != []
    assert script_errors(["let x = 1; export {x};"], [True])[0] == []


# --- sixth round: four false verdicts in the three checks ------------------

def test_html_resumes_at_a_foreign_content_integration_point():
    """A foreign-content DEPTH counter exempted every descendant of an <svg>
    root, but children of <foreignObject> are HTML again, so the slash on
    <div/> is ignored and the div stays open. Reported as balanced."""
    assert tag_errors("<svg><foreignObject><div/></foreignObject></svg>")
    assert tag_errors("<svg><g><circle/></g></svg>") == []
    assert tag_errors("<svg><foreignObject><p>x</p></foreignObject></svg>") == []


def test_every_paragraph_closing_start_tag_is_listed():
    """menu, hgroup and search close an open <p> and were missing, so the
    surplus </p> after one of them read as balanced markup."""
    for tag in ("menu", "hgroup", "search", "dir", "center"):
        assert tag_errors("<div><p>x<%s>y</%s></p></div>" % (tag, tag)), tag


def test_an_ip_literal_protocol_relative_host_is_an_external_request():
    """The alphabetic-TLD requirement that keeps prose quiet also excluded
    IP hosts, so a lesson that cannot render offline passed gate 5."""
    assert external_hits("url(//203.0.113.10/a.png)")
    assert external_hits('href="//[2001:db8::1]/x"')
    assert external_hits("// 1. first step, then 2. second step") == []


def test_legacy_javascript_mime_types_are_checked_not_skipped():
    """Browsers execute these; classifying them as data is a false PASS for
    any syntax error inside."""
    for t in ("text/x-javascript", "text/jscript", "text/javascript1.5",
              "application/x-ecmascript", "text/livescript"):
        assert script_bodies('<script type="%s">var x=;;</script>' % t), t
    assert script_bodies('<script type="application/json">{"a":1}</script>') == []


def test_a_script_inside_a_comment_is_not_executed_and_not_checked():
    """The browser runs nothing in a comment, so gate 6 was hard-failing valid
    lessons over a commented-out example. The reverse nesting must survive:
    the legacy `<script><!-- ... //--></script>` idiom is still real code."""
    from scripts.gate import script_blocks
    assert script_blocks("<!-- <script>var x=;;</script> -->") == []
    assert len(script_blocks("<script><!-- var x=1; //--></script>")) == 1
    assert len(script_blocks("<!-- <script>a=;</script> -->"
                             "<script>var b=1;</script>")) == 1


def test_a_truncated_event_handler_is_caught():
    """`onclick="check(this,false"` is well-formed HTML — the attribute value
    ends at the second quote and the tag closes normally — so tag_errors is
    silent and the <script> checker never reads attributes. The handler throws
    only when a student clicks the button. One shipped in la-07."""
    from scripts.gate import handler_bodies, handler_errors, tag_errors
    shipped = '<button onclick="check(this,false">no</button>'
    assert tag_errors(shipped) == []
    assert handler_bodies(shipped) == ["check(this,false"]
    bad, checked = handler_errors(handler_bodies(shipped))
    assert checked == 1 and bad


def test_the_repaired_handler_passes():
    from scripts.gate import handler_errors
    assert handler_errors(["check(this,false)"])[0] == []


def test_every_handler_is_reported_separately_not_only_the_first():
    """Batching all of a file's handlers into one node process must not let an
    early syntax error mask a later one, or hide which handler failed."""
    from scripts.gate import handler_errors
    bad, checked = handler_errors(["f(", "g()", "h(]"])
    assert checked == 3
    assert len(bad) == 2
    assert bad[0].startswith("handler 1 ") and bad[1].startswith("handler 3 ")


def test_an_empty_handler_is_not_sent_to_node():
    from scripts.gate import handler_errors
    assert handler_errors(["", "   "]) == ([], 2)


def test_only_event_handler_attributes_are_treated_as_script():
    from scripts.gate import handler_bodies
    assert handler_bodies('<a href="i.html" title="onclick">x</a>') == []
    assert handler_bodies('<b onclick="f()" onmouseover="g()">x</b>') == [
        "f()", "g()"]


def test_a_single_quoted_handler_is_extracted_too():
    """The first version of this row matched double-quoted values only, so the
    same defect it exists to catch was counted as zero handlers and passed."""
    from scripts.gate import handler_bodies, handler_errors
    single = "<button onclick='check(this,false'>x</button>"
    assert handler_bodies(single) == ["check(this,false"]
    bad, checked = handler_errors(handler_bodies(single))
    assert checked == 1 and len(bad) == 1


def test_handler_like_text_outside_an_attribute_is_not_compiled():
    from scripts.gate import handler_bodies
    prose = '<p>Write onclick="f(" to see the gate fire.</p>'
    assert handler_bodies(prose) == []


def test_return_in_a_handler_is_valid_and_must_not_fail_the_gate():
    """A handler attribute is compiled by the browser as a function BODY, so
    `return false` is legal there. Parsing it as Script grammar rejects it with
    "Illegal return statement" — a gate that fails valid lesson HTML."""
    from scripts.gate import handler_errors
    assert handler_errors(["return false;"]) == ([], 1)
    assert handler_errors(["if(x){return false}else{g()}"]) == ([], 1)


def test_a_broken_handler_is_still_caught_under_function_body_grammar():
    """The negative control for the change above: relaxing the grammar must not
    relax the check."""
    from scripts.gate import handler_errors
    bad, checked = handler_errors(["return false", "check(this,false"])
    assert checked == 2
    assert len(bad) == 1 and bad[0].startswith("handler 2 ")


def test_entities_in_a_handler_are_unescaped_before_compiling():
    """A browser unescapes the attribute value first, so `&amp;&amp;` is the
    operator && and must compile."""
    from scripts.gate import handler_bodies, handler_errors
    bodies = handler_bodies('<b onclick="a&amp;&amp;b()">x</b>')
    assert bodies == ["a&&b()"]
    assert handler_errors(bodies) == ([], 1)
