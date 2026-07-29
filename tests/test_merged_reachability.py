from scripts.check_merged_reachability import comparison_is_reachable


def test_main_ahead_of_merged_head_is_reachable():
    assert comparison_is_reachable("ahead")


def test_main_identical_to_merged_head_is_reachable():
    assert comparison_is_reachable("identical")


def test_head_merged_only_to_stale_base_is_rejected():
    assert not comparison_is_reachable("diverged")


def test_main_behind_pr_head_is_rejected():
    assert not comparison_is_reachable("behind")
