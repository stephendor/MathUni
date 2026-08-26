from scripts.check_source_modality import errors


def test_known_source_and_modality_pass():
    rows = {"u-01": [{"claim": "X", "source": "Book", "section": "1",
                       "page": 2, "modality": "proves"}]}
    assert errors(rows, {"Book": {}}) == []


def test_location_without_modality_fails():
    rows = {"u-01": [{"claim": "X", "source": "Book", "section": "1",
                       "page": 2}]}
    assert any("modality" in error for error in errors(rows, {"Book": {}}))


def test_unknown_unit_key_fails():
    rows = {"cta-04": [{"claim": "X", "source": "Book", "section": "1",
                         "page": 2, "modality": "proves"}]}
    assert "unknown unit 'cta-04'" in errors(rows, {"Book": {}}, {"cat-04"})


def test_empty_record_population_fails():
    assert "no modality records were provided" in errors({}, {"Book": {}})


def test_source_must_belong_to_the_enclosing_unit():
    rows = {"cat-04": [{"claim": "X", "source": "Axler", "section": "1",
                         "page": 2, "modality": "states"}]}
    found = errors(rows, {"Axler": {}, "Spivak": {}}, {"cat-04"},
                   {"cat-04": {"Spivak"}})
    assert "cat-04[1] source 'Axler' is not a resource for cat-04" in found


def test_locations_require_scalar_types_and_match_indexed_section():
    rows = {"u-01": [{"claim": "X", "source": "Book", "section": {},
                       "page": "banana", "modality": "proves"}]}
    found = errors(rows, {"Book": {}}, sections={
        "Book": {"sections": {"1.1": 1, "1.2": 5}}})
    assert "u-01[1] section must be a string" in found
    assert "u-01[1] page must be a positive integer" in found


def test_page_must_fall_inside_indexed_section():
    rows = {"u-01": [{"claim": "X", "source": "Book", "section": "1.1",
                       "page": 5, "modality": "proves"}]}
    assert "u-01[1] page 5 is outside indexed section 1.1" in errors(
        rows, {"Book": {}}, sections={
            "Book": {"sections": {"1.1": 1, "1.2": 5}}})


def test_shared_boundary_page_may_belong_to_preceding_section():
    rows = {"u-01": [{"claim": "X", "source": "Book", "section": "1.1",
                       "page": 5, "modality": "proves"}]}
    assert errors(rows, {"Book": {}}, sections={
        "Book": {"sections": {"1.1": 1, "1.2": 5}, "shared": [5]}}) == []
