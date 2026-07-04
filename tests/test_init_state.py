from scripts.init_state import seed_progress

DOC = {"units": [
    {"id": "a-01", "prereqs": []},
    {"id": "a-02", "prereqs": ["a-01"]},
]}

def test_no_prereqs_unlocked():
    assert seed_progress(DOC)["a-01"]["status"] == "unlocked"

def test_with_prereqs_locked():
    assert seed_progress(DOC)["a-02"]["status"] == "locked"

def test_all_units_present():
    assert set(seed_progress(DOC)) == {"a-01", "a-02"}
