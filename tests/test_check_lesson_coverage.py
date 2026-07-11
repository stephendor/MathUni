from scripts.check_lesson_coverage import find_missing_refs


def test_no_refs_in_problem_set_means_nothing_missing():
    assert find_missing_refs("Solve for x.", "<html>anything</html>") == []


def test_ref_present_in_lesson_is_not_missing():
    problem_set = "Use Theorem 1.29 to show av=0."
    lesson = "<p>Theorem 1.29 states that 0v=0 for all v.</p>"
    assert find_missing_refs(problem_set, lesson) == []


def test_ref_absent_from_lesson_is_reported():
    problem_set = "Use Theorem 1.29 and Definition 1.19."
    lesson = "<p>Definition 1.19 defines a vector space.</p>"
    assert find_missing_refs(problem_set, lesson) == ["Theorem 1.29"]


def test_multiple_missing_refs_sorted():
    problem_set = "See Theorem 1.34, Theorem 1.29, Definition 1.20."
    lesson = "<p>No theorems mentioned here.</p>"
    assert find_missing_refs(problem_set, lesson) == [
        "Definition 1.20", "Theorem 1.29", "Theorem 1.34",
    ]


def test_duplicate_refs_in_problem_set_reported_once():
    problem_set = "Theorem 1.29 and again Theorem 1.29."
    lesson = "<p>nothing</p>"
    assert find_missing_refs(problem_set, lesson) == ["Theorem 1.29"]


def test_ref_not_falsely_covered_by_longer_numbered_ref():
    problem_set = "Use Theorem 1.2 to finish the proof."
    lesson = "<p>Theorem 1.29 states something unrelated.</p>"
    assert find_missing_refs(problem_set, lesson) == ["Theorem 1.2"]
