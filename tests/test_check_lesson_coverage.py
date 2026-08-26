from scripts.check_lesson_coverage import find_missing_refs, find_refs, main


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


def test_propositions_and_examples_belong_to_coverage_population():
    problem_set = "Use Proposition 9.25 and Example 9.39."
    lesson = "<p>Example 9.39 is worked here.</p>"
    assert find_missing_refs(problem_set, lesson) == ["Proposition 9.25"]


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


def test_cli_rejects_zero_refs_without_a_disposition(tmp_path, capsys):
    problem_set = tmp_path / "problems.md"
    lesson = tmp_path / "lesson.html"
    problem_set.write_text("Discuss the chapter introduction.", encoding="utf-8")
    lesson.write_text("<html>discussion</html>", encoding="utf-8")

    assert main([str(problem_set), str(lesson)]) == 1
    assert "supply --expect-zero-refs" in capsys.readouterr().out


def test_cli_accepts_an_explicit_zero_ref_disposition(tmp_path, capsys):
    problem_set = tmp_path / "problems.md"
    lesson = tmp_path / "lesson.html"
    problem_set.write_text("Discuss the chapter introduction.", encoding="utf-8")
    lesson.write_text("<html>discussion</html>", encoding="utf-8")

    assert main(["--expect-zero-refs", "introductory discussion only",
                 str(problem_set), str(lesson)]) == 0
    assert "expected: introductory discussion only" in capsys.readouterr().out


def test_cli_rejects_a_stale_zero_ref_disposition(tmp_path, capsys):
    problem_set = tmp_path / "problems.md"
    lesson = tmp_path / "lesson.html"
    problem_set.write_text("Apply Lemma 3.1.", encoding="utf-8")
    lesson.write_text("<html>Lemma 3.1</html>", encoding="utf-8")

    assert main(["--expect-zero-refs", "none expected",
                 str(problem_set), str(lesson)]) == 1
    assert "expected zero refs" in capsys.readouterr().out


def test_cli_min_refs_rejects_vacuous_coverage(tmp_path, capsys):
    problem_set = tmp_path / "problems.md"
    lesson = tmp_path / "lesson.html"
    problem_set.write_text("Discuss the chapter introduction.", encoding="utf-8")
    lesson.write_text("<html>discussion</html>", encoding="utf-8")

    assert main(["--min-refs", "1", str(problem_set), str(lesson)]) == 1
    assert capsys.readouterr().out.strip() == "FAIL checked 0 refs; minimum required is 1"


def test_cli_reports_nonvacuous_denominator(tmp_path, capsys):
    problem_set = tmp_path / "problems.md"
    lesson = tmp_path / "lesson.html"
    problem_set.write_text("Apply Lemma 3.1.", encoding="utf-8")
    lesson.write_text("<html>Lemma 3.1</html>", encoding="utf-8")

    assert main([str(problem_set), str(lesson)]) == 0
    assert capsys.readouterr().out.strip() == "PASS checked 1 refs, 0 missing"


def test_lesson_range_citation_covers_its_individual_numbers():
    """Obs 153: a lesson citing 'Definitions 11.8-11.9' teaches both numbers,
    even though REF_PATTERN never matches the plural, dash-joined form."""
    problem_set = "Use Definition 11.9 to build the basis."
    lesson = "<p>See Definitions 11.8-11.9, p. 328, for the construction.</p>"
    assert find_missing_refs(problem_set, lesson) == []


def test_lesson_range_citation_with_en_dash_and_comma_list():
    problem_set = "Use Theorem 3 and Theorem 5."
    lesson = "<p>Theorems 3, 4 and 5 are proved together below.</p>"
    assert find_missing_refs(problem_set, lesson) == []


def test_problem_set_range_citation_is_expanded_too():
    problem_set = "See Definitions 2.1-2.2 for the setup."
    lesson = "<p>Definition 2.1 and Definition 2.2 are both stated here.</p>"
    assert find_missing_refs(problem_set, lesson) == []


def test_range_citation_does_not_mask_a_genuinely_untaught_number():
    problem_set = "Use Definition 11.9."
    lesson = "<p>See Definitions 5.1-5.2 for something unrelated.</p>"
    assert find_missing_refs(problem_set, lesson) == ["Definition 11.9"]


def test_citation_wrapped_across_lines_is_canonicalised():
    r"""Obs 2026-08-10: `\s+` eats newlines, so a wrapped citation used to
    produce an unmatchable ref and a false failure."""
    problem_set = "See Corollary\n3.6 for the bound."
    assert find_refs(problem_set) == ["Corollary 3.6"]


def test_wrapped_citation_is_covered_by_an_unwrapped_lesson():
    problem_set = "See Corollary\n3.6 for the bound."
    lesson = "<p>Corollary 3.6 gives the bound.</p>"
    assert find_missing_refs(problem_set, lesson) == []


def test_unwrapped_citation_is_covered_by_a_wrapped_lesson():
    problem_set = "See Corollary 3.6 for the bound."
    lesson = "<p>Corollary\n3.6 gives the bound.</p>"
    assert find_missing_refs(problem_set, lesson) == []


def test_wrapping_does_not_make_an_absent_ref_look_present():
    problem_set = "See Corollary\n3.6 for the bound."
    lesson = "<p>Corollary 3.7 is a different result.</p>"
    assert find_missing_refs(problem_set, lesson) == ["Corollary 3.6"]
