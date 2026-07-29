"""Fail when a merged PR head is not reachable from the repository default branch."""
import json
import os
import sys
import urllib.error
import urllib.request


def comparison_is_reachable(status):
    """GitHub compares `head PR sha` (base) to `main sha` (head)."""
    return status in {"ahead", "identical"}


def _get(url, token):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def merged_pulls(api, repository, token):
    page = 1
    while True:
        pulls = _get(
            f"{api}/repos/{repository}/pulls?state=closed&per_page=100&page={page}",
            token,
        )
        for pull in pulls:
            if pull.get("merged_at"):
                yield pull
        if len(pulls) < 100:
            return
        page += 1


def main():
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    repository = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    default_sha = os.environ.get("GITHUB_SHA")
    if not all((repository, token, default_sha)):
        print("ERROR: GITHUB_REPOSITORY, GITHUB_TOKEN, and GITHUB_SHA are required")
        return 2

    failures = []
    try:
        for pull in merged_pulls(api, repository, token):
            head_sha = pull["head"]["sha"]
            comparison = _get(
                f"{api}/repos/{repository}/compare/{head_sha}...{default_sha}",
                token,
            )
            if not comparison_is_reachable(comparison.get("status")):
                failures.append(
                    f"PR #{pull['number']} head {head_sha} is not reachable "
                    f"from default-branch head {default_sha} "
                    f"(comparison: {comparison.get('status')})")
    except (urllib.error.URLError, KeyError, ValueError) as exc:
        print(f"ERROR: reachability check could not run: {exc}")
        return 2

    for failure in failures:
        print(f"ERROR: {failure}")
    if failures:
        return 1
    print("all merged PR heads are reachable from the default branch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
