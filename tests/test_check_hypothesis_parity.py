from scripts.check_hypothesis_parity import contract_errors, parity_errors, result_contexts


def test_scope_block_is_attached_to_following_named_result():
    contexts = result_contexts(
        "Let R be a commutative ring.\n\nProve Theorem 2.3: every ideal works.")
    assert "commutative" in contexts["Theorem 2.3"][0]


def test_missing_hypothesis_is_rejected():
    problem = """Throughout assume R is commutative.

Prove Corollary 9.11: maps correspond to matrices."""
    lesson = """<div class="theorem"><strong>Corollary 9.11.</strong>
Maps correspond to matrices.</div>"""
    assert parity_errors(problem, lesson) == [
        ("Corollary 9.11", {"commutative"}, set())]


def test_matching_hypothesis_passes():
    problem = "Let G be finite.\n\nProve Theorem 1.2."
    lesson = "<p><strong>Theorem 1.2.</strong> If G is finite, it works.</p>"
    assert parity_errors(problem, lesson) == []


def test_unrelated_prose_does_not_supply_a_hypothesis():
    problem = "Finite examples are useful.\n\nProve Theorem 1.2."
    lesson = "<p><strong>Theorem 1.2.</strong> It works.</p>"
    assert parity_errors(problem, lesson) == []


def test_explanatory_direction_words_are_not_hypotheses():
    problem = "Prove Theorem 1.2."
    lesson = "<p><strong>Theorem 1.2.</strong> Turn right after the finite example.</p>"
    assert parity_errors(problem, lesson) == []


def test_contract_requires_hypothesis_in_both_artifacts():
    problem = "Let R be commutative.\n\nProve Example 8.30."
    lesson = "<p><strong>Example 8.30.</strong> Every cyclic module is R/I.</p>"
    assert contract_errors(problem, lesson, {
        "Example 8.30": ["commutative"]}) == [
            "lesson Example 8.30 missing hypotheses ['commutative']"]


def test_contract_rejects_a_stale_result_label():
    assert contract_errors("Prove Theorem 1.2.", "<p>Theorem 1.2.</p>", {
        "Theorem 9.9": ["finite"]}) == [
            "set missing named result Theorem 9.9",
            "lesson missing named result Theorem 9.9"]
