from scripts.update_unlocks import recompute

UNITS = [{"id": "a", "prereqs": []}, {"id": "b", "prereqs": ["a"]},
         {"id": "c", "prereqs": ["a", "b"]}]

def test_mastered_when_gate_met():
    prog = recompute(UNITS, {"a": {"status": "in-progress"}}, {"a": {"score": 0.85}})
    assert prog["a"]["status"] == "mastered"

def test_below_gate_not_mastered():
    prog = recompute(UNITS, {"a": {"status": "in-progress"}}, {"a": {"score": 0.7}})
    assert prog["a"]["status"] == "in-progress"

def test_dependents_unlock():
    prog = recompute(UNITS, {"a": {"status": "in-progress"}, "b": {"status": "locked"},
                             "c": {"status": "locked"}}, {"a": {"score": 0.9}})
    assert prog["b"]["status"] == "unlocked" and prog["c"]["status"] == "locked"

def test_in_progress_never_demoted():
    prog = recompute(UNITS, {"a": {"status": "mastered"}, "b": {"status": "in-progress"},
                             "c": {"status": "locked"}}, {"a": {"score": 0.9}})
    assert prog["b"]["status"] == "in-progress"

def test_roots_stay_unlocked_without_mastery():
    prog = recompute(UNITS, {"a": {"status": "unlocked"}, "b": {"status": "locked"}}, {})
    assert prog["a"]["status"] == "unlocked"
