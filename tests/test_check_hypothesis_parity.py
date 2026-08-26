from scripts.check_hypothesis_parity import (contract_errors, main, parity_errors,
                                             registry_errors, result_contexts)


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


def test_same_sentence_and_prove_connector_preserves_scope():
    problem = "Assume G is finite and prove Theorem 1.2."
    lesson = "<p><strong>Theorem 1.2.</strong> It works.</p>"
    assert parity_errors(problem, lesson) == [
        ("Theorem 1.2", {"finite"}, set())]


def test_scope_does_not_jump_across_an_intervening_sentence():
    problem = "Assume G is finite. Discuss the example. Theorem 1.2 applies."
    lesson = "<p><strong>Theorem 1.2.</strong> It works.</p>"
    assert parity_errors(problem, lesson) == []


def test_negated_qualifier_cannot_satisfy_positive_hypothesis():
    problem = "Let R be commutative. Theorem 1.2 works."
    lesson = "<p>Let R be not commutative. Theorem 1.2 works.</p>"
    assert parity_errors(problem, lesson) == [
        ("Theorem 1.2", {"commutative"}, {"not commutative"})]


def test_hidden_html_cannot_satisfy_a_hypothesis_contract():
    problem = "Assume R is commutative and prove Corollary 9.11."
    lesson = ("<p><strong>Corollary 9.11.</strong> The conclusion holds.</p>"
              "<script>const note='Assume R is commutative. Corollary 9.11';</script>"
              "<style>/* Assume R is commutative. Corollary 9.11 */</style>")
    assert parity_errors(problem, lesson) == [
        ("Corollary 9.11", {"commutative"}, set())]


def test_unrelated_prose_does_not_supply_a_hypothesis():
    problem = "Finite examples are useful.\n\nProve Theorem 1.2."
    lesson = "<p><strong>Theorem 1.2.</strong> It works.</p>"
    assert parity_errors(problem, lesson) == []


def test_explanatory_direction_words_are_not_hypotheses():
    problem = "Prove Theorem 1.2."
    lesson = "<p><strong>Theorem 1.2.</strong> Turn right after the finite example.</p>"
    assert parity_errors(problem, lesson) == []


def test_scope_on_a_different_claim_does_not_attach_to_a_result_mention():
    problem = ("Suppose V is finite-dimensional. Prove that singular maps "
               "are not a subspace; use Theorem 1.34 for the subspace test.")
    lesson = "<p><strong>Theorem 1.34.</strong> A subset is a subspace iff...</p>"
    assert parity_errors(problem, lesson) == []


def test_a_narrower_lesson_statement_is_not_a_missing_prerequisite():
    problem = "Prove Theorem 1.2."
    lesson = "<p><strong>Theorem 1.2.</strong> If G is finite, it works.</p>"
    assert parity_errors(problem, lesson) == []


def test_contract_requires_hypothesis_in_both_artifacts():
    problem = "Let R be commutative.\n\nProve Example 8.30."
    lesson = "<p><strong>Example 8.30.</strong> Every cyclic module is R/I.</p>"
    assert contract_errors(problem, lesson, {
        "Example 8.30": ["commutative"]}) == [
        "lesson Example 8.30 missing hypotheses ['commutative']"]


def test_contract_qualifier_cannot_come_from_another_result_sentence():
    problem = ("Theorem 1.1 assumes R is commutative. "
               "Example 8.30 holds.")
    lesson = ("<p>Theorem 1.1 assumes R is commutative. "
              "Example 8.30 holds.</p>")
    assert contract_errors(problem, lesson, {
        "Example 8.30": ["commutative"]}) == [
            "set Example 8.30 missing hypotheses ['commutative']",
            "lesson Example 8.30 missing hypotheses ['commutative']"]


def test_contract_rejects_a_stale_result_label():
    assert contract_errors("Prove Theorem 1.2.", "<p>Theorem 1.2.</p>", {
        "Theorem 9.9": ["finite"]}) == [
            "set missing named result Theorem 9.9",
        "lesson missing named result Theorem 9.9"]


def test_contract_registry_rejects_unknown_unit_key():
    assert registry_errors({"cat-04"}, {"cta-04": {}}) == [
        "hypothesis contract names unknown unit cta-04"]


def test_cli_applies_general_parity_without_a_contract(tmp_path, capsys):
    problem = tmp_path / "set.md"
    lesson = tmp_path / "lesson.html"
    contracts = tmp_path / "contracts.json"
    problem.write_text("Let G be finite.\n\nProve Theorem 1.2.", encoding="utf-8")
    lesson.write_text("<p><strong>Theorem 1.2.</strong> It works.</p>",
                      encoding="utf-8")
    contracts.write_text("{}", encoding="utf-8")
    assert main(["--unit", "u-01", "--contracts", str(contracts),
                 str(problem), str(lesson)]) == 1
    assert "Theorem 1.2 differs" in capsys.readouterr().out
