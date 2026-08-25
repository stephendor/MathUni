from scripts.check_unit_headings import contract_errors


CONTRACT = {"book": "Axler", "edition": "3rd edition",
            "sections": ["5.B", "5.C"],
            "required_title_terms": ["upper-triangular", "diagonalisability"]}


def test_matching_edition_sections_and_title_pass():
    assert contract_errors(
        {"title": "Upper-triangular matrices and diagonalisability"},
        {"Axler": {"edition": "3rd edition"}},
        {"Axler": {"sections": {"5.B": 143, "5.C": 155}}}, CONTRACT) == []


def test_fourth_edition_title_fails_against_third_edition_contract():
    errors = contract_errors(
        {"title": "The Minimal Polynomial"},
        {"Axler": {"edition": "3rd edition"}},
        {"Axler": {"sections": {"5.B": 143, "5.C": 155}}}, CONTRACT)
    assert any("unit title omits" in error for error in errors)
