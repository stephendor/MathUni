"""Negative controls for the lab output gate.

Every check the gate makes has a test here that watches it fail, because a gate
nobody has seen fire is a gate nobody knows works. The tests run trivial
``print`` blocks under the repo's own interpreter, so they need none of the lab
stack and stay offline.
"""
import sys

import pytest

from scripts.check_lab_outputs import (
    LabSetError,
    _normalise,
    check_versions,
    compare_outputs,
    compare_runs,
    main,
    parse_blocks,
    parse_env_pins,
)

PY = sys.version_info


def env_block(extra=""):
    return "```env\npython==%d.%d.%d\n%s```\n\n" % (PY[0], PY[1], PY[2], extra)


def code_block(block_id, body):
    return "```python id=%s\n%s\n```\n\n" % (block_id, body)


def out_block(block_id, body):
    return "```text id=%s\n%s\n```\n\n" % (block_id, body)


def write(tmp_path, text, name="lab-00.md"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------- parsing

def test_parses_paired_blocks_in_document_order():
    text = code_block("a", "print(1)") + out_block("a", "1") \
        + code_block("b", "print(2)") + out_block("b", "2")
    assert [b[0] for b in parse_blocks(text)] == ["a", "b"]


def test_untagged_blocks_are_ignored():
    text = "```python\nprint('student completes this')\n```\n\n" \
        + code_block("a", "print(1)") + out_block("a", "1")
    assert [b[0] for b in parse_blocks(text)] == ["a"]


def test_code_block_without_output_is_rejected():
    with pytest.raises(LabSetError, match="no recorded output"):
        parse_blocks(code_block("a", "print(1)"))


def test_output_block_without_code_is_rejected():
    with pytest.raises(LabSetError, match="matches no python block"):
        parse_blocks(out_block("ghost", "1"))


def test_duplicate_code_id_is_rejected():
    text = code_block("a", "print(1)") + out_block("a", "1") + code_block("a", "print(2)")
    with pytest.raises(LabSetError, match="duplicate python block id"):
        parse_blocks(text)


def test_env_pins_are_read():
    assert parse_env_pins("```env\ngudhi==3.13.0\nripser==0.6.15\n```") == {
        "gudhi": "3.13.0", "ripser": "0.6.15"}


def test_malformed_env_line_is_rejected():
    with pytest.raises(LabSetError, match="not 'name==version'"):
        parse_env_pins("```env\ngudhi 3.13.0\n```")


def test_normalise_ignores_trailing_and_surrounding_blank_lines():
    assert _normalise("\n\nx  \ny\n\n") == "x\ny"


def test_normalise_keeps_interior_blank_lines():
    assert _normalise("x\n\ny") == "x\n\ny"


# ------------------------------------------------------- version checking

def test_version_mismatch_is_reported():
    report = {"python": "3.11.11", "versions": {"gudhi": "3.11.0"}}
    failures = check_versions({"gudhi": "3.13.0"}, report)
    assert failures == [
        "FAIL env gudhi is pinned at 3.13.0 and the interpreter has 3.11.0"]


def test_missing_distribution_is_reported():
    report = {"python": "3.11.11", "versions": {"gudhi": None}}
    assert "not installed" in check_versions({"gudhi": "3.13.0"}, report)[0]


def test_python_pin_is_checked_against_the_interpreter():
    report = {"python": "3.13.5", "versions": {}}
    assert check_versions({"python": "3.11.11"}, report) == [
        "FAIL env python is pinned at 3.11.11 and the interpreter has 3.13.5"]


def test_matching_versions_produce_no_failures():
    report = {"python": "3.11.11", "versions": {"gudhi": "3.13.0"}}
    assert check_versions({"python": "3.11.11", "gudhi": "3.13.0"}, report) == []


# ------------------------------------------------------- output comparison

def test_output_mismatch_is_reported_with_the_block_id():
    blocks = [("circle", "", "H1 features: 1")]
    report = {"blocks": {"circle": {"stdout": "H1 features: 2", "error": None}}}
    failures = compare_outputs(blocks, report)
    assert len(failures) == 1 and failures[0].startswith("FAIL circle output differs")


def test_raising_block_is_reported_rather_than_compared():
    blocks = [("boom", "", "")]
    report = {"blocks": {"boom": {"stdout": "", "error": "ZeroDivisionError\n"}}}
    assert compare_outputs(blocks, report)[0].startswith("FAIL boom raised")


def test_block_that_never_ran_is_reported():
    blocks = [("a", "", "1"), ("b", "", "2")]
    report = {"blocks": {"a": {"stdout": "1", "error": None}}}
    assert compare_outputs(blocks, report) == [
        "FAIL b did not run (an earlier block raised)"]


def test_matching_output_produces_no_failures():
    blocks = [("a", "", "1  \n")]
    report = {"blocks": {"a": {"stdout": "1\n", "error": None}}}
    assert compare_outputs(blocks, report) == []


def test_leading_whitespace_is_significant():
    """numpy prints aligned columns; indentation is output, not decoration."""
    blocks = [("a", "", "[[1 2]\n [3 4]]")]
    report = {"blocks": {"a": {"stdout": "[[1 2]\n[3 4]]", "error": None}}}
    assert compare_outputs(blocks, report)[0].startswith("FAIL a output differs")


# ---------------------------------------------------------- determinism

def test_disagreeing_runs_are_reported():
    blocks = [("r", "", "")]
    first = {"blocks": {"r": {"stdout": "0.31", "error": None}}}
    second = {"blocks": {"r": {"stdout": "0.87", "error": None}}}
    assert compare_runs(blocks, first, second)[0].startswith("FAIL r is not deterministic")


def test_agreeing_runs_produce_no_failures():
    blocks = [("r", "", "")]
    report = {"blocks": {"r": {"stdout": "0.31", "error": None}}}
    assert compare_runs(blocks, report, report) == []


# ---------------------------------------------------------------- the CLI

def test_cli_passes_on_a_correct_set(tmp_path, capsys):
    text = env_block() + code_block("a", "print('hello')") + out_block("a", "hello")
    assert main([write(tmp_path, text), "--python", sys.executable]) == 0
    assert capsys.readouterr().out.startswith("PASS 1 blocks re-executed")


def test_cli_fails_on_a_wrong_recorded_output(tmp_path, capsys):
    text = env_block() + code_block("a", "print('hello')") + out_block("a", "hallo")
    assert main([write(tmp_path, text), "--python", sys.executable]) == 1
    assert "FAIL a output differs" in capsys.readouterr().out


def test_cli_fails_on_a_wrong_env_pin(tmp_path, capsys):
    text = "```env\npython==1.2.3\n```\n\n" \
        + code_block("a", "print('hello')") + out_block("a", "hello")
    assert main([write(tmp_path, text), "--python", sys.executable]) == 1
    assert "FAIL env python is pinned at 1.2.3" in capsys.readouterr().out


def test_cli_fails_on_a_nondeterministic_block(tmp_path, capsys):
    body = "import random\nprint(random.SystemRandom().randint(0, 10**12))"
    text = env_block() + code_block("a", body) + out_block("a", "0")
    assert main([write(tmp_path, text), "--python", sys.executable]) == 1
    assert "is not deterministic" in capsys.readouterr().out


def test_cli_fails_on_an_unpinned_set(tmp_path, capsys):
    text = code_block("a", "print('hello')") + out_block("a", "hello")
    assert main([write(tmp_path, text), "--python", sys.executable]) == 1
    assert "the environment is unrecorded" in capsys.readouterr().out


def test_cli_reports_a_set_with_no_executable_blocks_as_unchecked(tmp_path, capsys):
    assert main([write(tmp_path, "Just prose.\n"), "--python", sys.executable]) == 0
    assert capsys.readouterr().out.strip().startswith("UNCHECKED")


def test_cli_shares_state_across_blocks_in_document_order(tmp_path, capsys):
    text = env_block() + code_block("a", "x = 6") + out_block("a", "") \
        + code_block("b", "print(x * 7)") + out_block("b", "42")
    assert main([write(tmp_path, text), "--python", sys.executable]) == 0


def test_cli_reports_the_raising_block_by_id(tmp_path, capsys):
    text = env_block() + code_block("a", "1 / 0") + out_block("a", "")
    assert main([write(tmp_path, text), "--python", sys.executable]) == 1
    out = capsys.readouterr().out
    assert "FAIL a raised" in out and "ZeroDivisionError" in out
