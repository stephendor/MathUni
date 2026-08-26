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
