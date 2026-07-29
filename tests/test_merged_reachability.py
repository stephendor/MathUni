import io

from scripts import check_merged_reachability
from scripts.check_merged_reachability import comparison_is_reachable


def test_main_ahead_of_merged_head_is_reachable():
    assert comparison_is_reachable("ahead")


def test_main_identical_to_merged_head_is_reachable():
    assert comparison_is_reachable("identical")


def test_head_merged_only_to_stale_base_is_rejected():
    assert not comparison_is_reachable("diverged")


def test_main_behind_pr_head_is_rejected():
    assert not comparison_is_reachable("behind")


def test_get_uses_finite_timeout(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["timeout"] = timeout
        return io.StringIO('{"ok": true}')

    monkeypatch.setattr(
        check_merged_reachability.urllib.request, "urlopen", fake_urlopen)
    assert check_merged_reachability._get("https://api.example.test", "token") == {
        "ok": True,
    }
    assert seen["timeout"] == check_merged_reachability.HTTP_TIMEOUT_SECONDS


def test_timeout_uses_operational_error_exit(monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setattr(
        check_merged_reachability,
        "_get",
        lambda url, token: (_ for _ in ()).throw(TimeoutError("timed out")),
    )
    assert check_merged_reachability.main() == 2
    assert "reachability check could not run" in capsys.readouterr().out


def test_workflow_dispatch_uses_default_branch_sha_not_event_sha(monkeypatch):
    api = "https://api.example.test"
    default_sha = "main-sha"
    feature_sha = "feature-sha"
    seen = []
    monkeypatch.setenv("GITHUB_API_URL", api)
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_SHA", feature_sha)
    monkeypatch.setattr(
        check_merged_reachability,
        "merged_pulls",
        lambda api, repository, token: iter([{
            "number": 9,
            "head": {"sha": "merged-head"},
        }]),
    )

    def fake_get(url, token):
        seen.append(url)
        if url == f"{api}/repos/owner/repo":
            return {"default_branch": "main"}
        if url == f"{api}/repos/owner/repo/branches/main":
            return {"commit": {"sha": default_sha}}
        if url.endswith(f"/compare/merged-head...{default_sha}"):
            return {"status": "ahead"}
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(check_merged_reachability, "_get", fake_get)
    assert check_merged_reachability.main() == 0
    assert any(default_sha in url for url in seen)
    assert all(feature_sha not in url for url in seen)
