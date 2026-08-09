from scripts.lesson_lint import lint, tag_imbalances


def _failed(html, name):
    return any(check == name and not ok for check, ok, _ in lint(html))


def test_mismatched_sup_sub_pair_fails_balance_gate():
    assert tag_imbalances("Δ<sup>k+ℓ</sub>") == {
        "sub": (0, 1),
        "sup": (1, 0),
    }
    assert _failed("Δ<sup>k+ℓ</sub>", "render: tags balanced")


def test_balanced_governed_tags_pass_and_script_content_is_ignored():
    html = "<div><strong>x<sup>2</sup></strong></div><script>'<sup>x</sub>'</script>"
    assert tag_imbalances(html) == {}


def test_optional_p_end_tag_is_explicitly_outside_balance_gate():
    assert tag_imbalances("<p>one<p>two</p>") == {}
