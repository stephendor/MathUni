from scripts.check_visual_claims import probes, run_probes


def block(source):
    return "// VISUAL-CLAIM-PROBE-BEGIN demo\n%s\n// VISUAL-CLAIM-PROBE-END" % source


def test_probe_is_discovered_and_executed():
    text = block("if (2 + 2 !== 4) throw new Error('arithmetic');")
    assert [name for name, _source in probes(text)] == ["demo"]
    assert run_probes(text) == []


def test_non_discriminating_comparison_fails():
    text = block("const a=90,b=90;if(Math.abs(a-b)<5)throw new Error('no discrimination');")
    failures = run_probes(text)
    assert failures and failures[0][0] == "demo"
