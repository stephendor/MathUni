import json

from scripts.review import REVIEW_CAP, build_queue, embed_json, render_review


def card(cid, due, unit="pw-01", front="F", back="B"):
    return {"id": cid, "unit": unit, "type": "definition", "front": front,
            "back": back, "due": due, "ease": 2.5, "interval": 1,
            "reps": 1, "lapses": 0}


DECK = [card("c%02d" % n, "2026-08-%02d" % (1 + n % 28)) for n in range(66)]


# --- build_queue ------------------------------------------------------------

def test_queue_is_capped():
    assert len(build_queue(DECK)) == REVIEW_CAP


def test_cap_matches_the_review_skill():
    """15 is the cap already stated in .claude/skills/review/SKILL.md."""
    assert REVIEW_CAP == 15


def test_queue_is_oldest_due_first():
    q = build_queue(DECK)
    assert q == sorted(q, key=lambda c: c["due"])
    assert q[0]["due"] <= min(c["due"] for c in DECK)


def test_cap_does_not_pad_a_short_queue():
    q = build_queue([card("a", "2026-08-01"), card("b", "2026-08-02")])
    assert len(q) == 2


def test_empty_deck_gives_an_empty_queue():
    assert build_queue([]) == []


def test_ordering_does_not_depend_on_input_order():
    """The caller's sort is not trusted; the cap must still mean 'oldest'."""
    assert [c["id"] for c in build_queue(list(reversed(DECK)))] == \
           [c["id"] for c in build_queue(DECK)]


# --- embedding --------------------------------------------------------------

def test_script_terminator_in_card_text_cannot_break_out():
    """`</script>` inside a card would otherwise end the block early and spill
    the rest of the deck into the document as markup."""
    out = embed_json([card("x", "2026-08-01", front="close </script> here")])
    assert "</script>" not in out
    assert "\\u003c" in out


def test_embedded_json_still_parses_back_to_the_same_cards():
    cards = [card("x", "2026-08-01", front="a <b> & c", back="∀x ∈ X")]
    assert json.loads(embed_json(cards)) == cards


def test_unicode_maths_survives_embedding():
    out = embed_json([card("x", "2026-08-01", back="n = 2k + 1 ⇒ odd")])
    assert "⇒" in out, "cards carry maths; escaping must not mangle it"


# --- render_review ----------------------------------------------------------

def html(queue=None, token="TOK", total=66, notice=None):
    return render_review(build_queue(DECK) if queue is None else queue,
                         token, total, notice)


def test_page_is_a_document():
    out = html()
    assert out.startswith("<!DOCTYPE html>") and "</html>" in out


def test_the_writeback_url_carries_the_token():
    assert "'/api/rate?t=' + 'TOK'" in html()


def test_the_page_says_what_it_is_holding_back():
    """A silently truncated queue is its own kind of lie."""
    out = html()
    assert "15 of 66 due" in out
    assert "the other 51 keep their place" in out


def test_no_held_back_message_when_the_whole_queue_fits():
    out = render_review(build_queue(DECK[:5]), "TOK", 5)
    assert "5 due" in out
    assert "keep their place" not in out


def test_all_four_ratings_are_offered():
    out = html()
    for label in ("Again", "Hard", "Good", "Easy"):
        assert label in out


def test_an_empty_queue_does_not_invent_work():
    out = render_review([], "TOK", 0)
    assert "Nothing is due" in out
    assert "data-rate" not in out


def test_a_failed_rating_is_surfaced_rather_than_swallowed():
    """Advancing past a rating that never saved is the failure this replaces."""
    out = html()
    assert "did not save" in out
    assert "The card is still due" in out


def test_engram_notice_is_relayed_when_supplied():
    out = html(notice="[engram] 50 reviews logged")
    assert "50 reviews logged" in out


def test_no_engram_notice_when_there_is_none():
    assert "engram" not in html().lower()


def test_review_page_makes_no_external_requests():
    """Same rule gate.py enforces on lessons: it must work offline."""
    out = html()
    for probe in ("http://", "https://", "//cdn", "@import", "<link ", "src="):
        assert probe not in out, probe


def test_card_text_reaches_the_page_only_through_the_json_block():
    """Nothing interpolates card text into markup; the script escapes it at
    render time with textContent, so a card cannot inject HTML."""
    out = render_review([card("x", "2026-08-01", front="<img onerror=alert(1)>")],
                        "TOK", 1)
    assert "<img onerror" not in out


def test_a_successful_retry_retracts_the_failure_notice():
    """Without this the queue advances while the page still says the rating did
    not save, which invites a reload and a second review of the same card."""
    from scripts.review import render_review

    html = render_review(build_queue(DECK[:2]), "TOK", 2)
    success = html[html.index(".then(function(){"):]
    hide = success.index("err.style.display = 'none'")
    advance = success.index("tally[r]++")
    assert hide < advance, "retract before advancing, not after"
