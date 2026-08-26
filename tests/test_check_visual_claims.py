from scripts.check_visual_claims import main, probes, run_probes


def block(source):
    return "<script>// VISUAL-CLAIM-PROBE-BEGIN demo\n%s\n// VISUAL-CLAIM-PROBE-END</script>" % source


def test_probe_is_discovered_and_executed():
    text = block("if (2 + 2 !== 4) throw new Error('arithmetic');")
    assert [name for name, _source in probes(text)] == ["demo"]
    assert run_probes(text) == []


def test_non_discriminating_comparison_fails():
    text = block("const a=90,b=90;if(Math.abs(a-b)<5)throw new Error('no discrimination');")
    failures = run_probes(text)
    assert failures and failures[0][0] == "demo"


def test_comment_only_placeholder_is_not_a_probe():
    text = "<!-- " + block("// placeholder") + " -->"
    assert probes(text) == []


def test_required_probe_cannot_disappear(monkeypatch, tmp_path, capsys):
    path = tmp_path / "la-15.html"
    path.write_text("<canvas></canvas>", encoding="utf-8")
    monkeypatch.setattr("scripts.check_visual_claims.REPO", str(tmp_path.parent))
    monkeypatch.setattr("scripts.check_visual_claims.REQUIRED", {
        "%s/la-15.html" % tmp_path.name: {"spectral-eigenvector-angle"}})
    assert main([str(path)]) == 1
    assert "required probe is missing" in capsys.readouterr().out
