"""The definitions/theorems index, which is an extraction problem first.

Every test here that looks fussy is guarding a way the extraction can go wrong
*quietly* — returning fewer entries, or shorter ones, without ever raising.
"""
import glob
import pathlib

from scripts.home import StaticLinks
from scripts.reference import (
    KINDS,
    blocks,
    build_index,
    counts,
    parse_lesson,
    render_reference,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]

LESSON = (
    "<h2>Segment one</h2>"
    '<div class="definition">'
    "<strong>Definition 1.1 (divides).</strong> Let a, b in Z. "
    '<span class="cite">— Aluffi §1.1, Definition 1.1, p. 4</span>'
    "</div>"
    "<h2>Segment two</h2>"
    '<div class="theorem">'
    "<p><strong>Lemma 1.2.</strong> If b divides a then |b| &lt;= |a|.</p>"
    "</div>"
)


def one(html, kind="definition"):
    return [e for e in parse_lesson(html, "aa-01", "aa") if e["kind"] == kind][0]


# --- balanced matching, which is the whole reason this is not one regex ------

def test_a_nested_div_does_not_truncate_the_block():
    """`<div class="theorem">(.*?)</div>` ends at the FIRST inner close tag.
    It loses the tail of the statement and raises nothing."""
    html = ('<div class="theorem">before'
            '<div class="worked">inner</div>'
            "after</div>")
    found = blocks(html)
    assert len(found) == 1
    kind, body, at = found[0]
    assert "before" in body and "after" in body, "the tail must survive"


def test_blocks_reports_where_it_found_each_one():
    """The offset is not decoration: the segment is the nearest <h2> above the
    block, and that is unrecoverable from the body alone."""
    kind, body, at = blocks('<h2>S</h2><div class="definition">x</div>')[0]
    assert at > 0 and "<h2>" not in body


def test_both_label_conventions_are_read():
    """The corpus grew two shapes. A pattern anchored to the first drops 602 of
    1054 blocks while still looking like it works."""
    bare = one('<div class="definition"><strong>Definition 2.2.</strong> body</div>')
    wrapped = one('<div class="definition"><p><strong>Definition 11.32.</strong> body</p></div>')
    assert bare["label"] == "Definition 2.2."
    assert wrapped["label"] == "Definition 11.32."


def test_a_block_with_no_label_is_kept_not_dropped():
    """6 of 1054. They are still real statements."""
    entry = one('<div class="definition">A set is a collection.</div>')
    assert entry["label"] == "Definition"
    assert "collection" in entry["statement"]


# --- the statement has to stay readable as mathematics ----------------------

def test_var_sub_and_sup_survive():
    """Dropping <var> turns "n = 2k" into "n = 2 k", which reads as a typo in
    every statement in the corpus. 4624 <var>, 4948 <sub>, 1184 <sup>."""
    entry = one('<div class="definition"><strong>D.</strong> '
                "<var>n</var> = 2<var>k</var>, D<sub>2n</sub>, x<sup>2</sup>"
                "</div>")
    assert "<var>n</var> = 2<var>k</var>" in entry["statement"]
    assert "<sub>2n</sub>" in entry["statement"]
    assert "<sup>2</sup>" in entry["statement"]


def test_tags_outside_the_whitelist_lose_their_markup_but_keep_their_text():
    entry = one('<div class="definition"><strong>D.</strong> '
                '<p>first</p><p>second</p></div>')
    assert "<p>" not in entry["statement"]
    assert "first" in entry["statement"] and "second" in entry["statement"]
    assert "firstsecond" not in entry["statement"], "a dropped block tag is a boundary"


def test_no_attribute_from_a_lesson_reaches_the_page():
    entry = one('<div class="definition"><strong>D.</strong> '
                '<span onclick="x" style="y">text</span>'
                '<a href="http://evil">link</a></div>')
    assert "onclick" not in entry["statement"]
    assert "style" not in entry["statement"]
    assert "href" not in entry["statement"]
    assert "text" in entry["statement"] and "link" in entry["statement"]


def test_the_citation_is_extracted_and_leaves_the_statement():
    entry = one(LESSON)
    assert "Aluffi" in entry["cite"] and "p. 4" in entry["cite"]
    assert "Aluffi" not in entry["statement"], "the cite is shown separately"


def test_a_block_without_a_citation_is_still_an_entry():
    """86 of 1054 carry none."""
    entry = one('<div class="definition"><strong>D.</strong> body</div>')
    assert entry["cite"] == "" and entry["statement"] == "body"


# --- segments ---------------------------------------------------------------

def test_the_segment_is_the_nearest_heading_above():
    entries = parse_lesson(LESSON, "aa-01", "aa")
    assert entries[0]["segment"] == "Segment one"
    assert entries[1]["segment"] == "Segment two"


def test_a_block_before_any_heading_has_no_segment():
    entry = one('<div class="definition">x</div><h2>Later</h2>')
    assert entry["segment"] == ""


# --- the corpus, not a sample -----------------------------------------------

def test_the_whole_corpus_extracts():
    """1054 blocks over 145 lessons. Unit tests cover shapes I thought of;
    this covers the ones the authors wrote."""
    import yaml

    syllabus = yaml.safe_load(
        (ROOT / "curriculum" / "syllabus.yaml").read_text(encoding="utf-8"))
    index = build_index(syllabus["units"], root=str(ROOT / "lessons"))
    n = counts(index)
    assert len(index) > 900, "found only %d" % len(index)
    assert n["definition"] > 400 and n["theorem"] > 500
    assert all(e["kind"] in KINDS for e in index)
    assert all(e["label"] for e in index), "every entry needs something to show"
    unlabelled = [e for e in index if e["label"].title() == e["kind"].title()]
    assert len(unlabelled) < 20, "labels should be the overwhelming norm"


def test_the_index_follows_syllabus_order_not_the_filesystem():
    """So a definition appears after the one it depends on."""
    import yaml

    syllabus = yaml.safe_load(
        (ROOT / "curriculum" / "syllabus.yaml").read_text(encoding="utf-8"))
    order = [u["id"] for u in syllabus["units"]]
    index = build_index(syllabus["units"], root=str(ROOT / "lessons"))
    seen = [e["unit"] for e in index]
    positions = [order.index(u) for u in seen]
    assert positions == sorted(positions)


def test_every_lesson_on_disk_is_reachable():
    """A unit whose lesson exists but is skipped would silently shrink the
    reference, and nothing else would notice."""
    import yaml

    syllabus = yaml.safe_load(
        (ROOT / "curriculum" / "syllabus.yaml").read_text(encoding="utf-8"))
    index = build_index(syllabus["units"], root=str(ROOT / "lessons"))
    on_disk = {pathlib.Path(p).stem
               for p in glob.glob(str(ROOT / "lessons" / "*" / "*.html"))}
    listed = {u["id"] for u in syllabus["units"]}
    missed = (on_disk & listed) - {e["unit"] for e in index}
    # A lesson with no definitions and no theorems is legitimate.
    assert len(missed) < 10, sorted(missed)[:10]


# --- the page ---------------------------------------------------------------

def view():
    return parse_lesson(LESSON, "aa-01", "aa")


def test_the_page_carries_both_entries_and_their_counts():
    html = render_reference(view(), StaticLinks(), {"aa-01": "Integers"})
    assert "1 definitions" in html and "1 theorems" in html
    assert "Definition 1.1 (divides)." in html
    assert "Lemma 1.2." in html
    assert "Integers" in html


def test_each_entry_carries_a_lowercase_search_key():
    html = render_reference(view(), StaticLinks())
    assert 'data-t="' in html
    assert "definition 1.1 (divides)." in html, "the key is lowercased for search"


def test_the_search_key_carries_no_markup():
    html = render_reference(view(), StaticLinks())
    import re

    for key in re.findall(r'data-t="([^"]*)"', html):
        assert "<" not in key and ">" not in key


def test_the_page_links_back_to_the_lesson():
    html = render_reference(view(), StaticLinks())
    assert "../lessons/aa/aa-01.html" in html


def test_an_empty_index_still_renders_a_page():
    html = render_reference([], StaticLinks())
    assert "0 definitions" in html and "</html>" in html


def test_the_footer_says_where_this_came_from():
    """A reference that could hallucinate a theorem would be worse than none,
    so the page states its provenance rather than implying it."""
    html = render_reference(view(), StaticLinks())
    assert "no model" in html
    assert "scripts/reference.py" in html


def test_reference_links_never_promote_a_unit():
    """On the live server `links.lesson()` is an authenticated /open link that
    marks the unit in-progress, stamps last_studied and creates a learning
    record. Browsing the index would have advanced progress for every unit
    whose definition was looked up."""
    from scripts.home import ServerLinks

    html = render_reference(parse_lesson(LESSON, "aa-01", "aa"),
                            ServerLinks("SECRET"), {"aa-01": "Integers"})
    assert "/open/" not in html
    assert "SECRET" not in html
    assert "/lesson/aa-01" in html
