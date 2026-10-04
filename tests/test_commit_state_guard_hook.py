"""Controls for ``.claude/hooks/commit-state-guard.sh``.

Two observations motivate the guard. ``2026-09-08-blocked-commit-reported-exit-zero``:
a backgrounded ``git commit ... | tail`` was blocked by a hook and still reported
exit 0, because a pipeline's status is its last command's. And
``2026-09-09-the-branch-moved-under-a-running-session``: another session moved HEAD in
the shared MathUni working directory, and nothing signalled it; the session had checked
its branch only at the start.

These tests drive the real hook under bash against real repositories, and fail rather
than skip without bash. The guard is a port of TDL's ``commit-state-guard`` (PR #300);
every control TDL carries is ported here, and the controls marked *new* cover what
the port changed or added: the ``core.hooksPath`` bypass, linked worktrees (MathUni's
real layout), a second session in the same worktree, detached HEADs in both directions,
and the wiring and receipts (the guard's only liveness signal, since MathUni has no git
hooks behind it).
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
HOOK = HOOKS_DIR / "commit-state-guard.sh"
RECEIPT_WRAP = HOOKS_DIR / "_receipt-wrap.sh"
SETTINGS = REPO_ROOT / ".claude" / "settings.json"


def _load_guard() -> ModuleType:
    spec = importlib.util.spec_from_file_location("commit_state_guard", HOOKS_DIR / "commit_state_guard.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # the dataclasses in the guard resolve their annotations through it
    spec.loader.exec_module(module)
    return module


GUARD = _load_guard()


def _bash() -> str:
    """Resolve a real bash rather than the WSL launcher stub, failing if none exists."""
    for candidate in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe"):
        if Path(candidate).exists():
            return candidate
    found = shutil.which("bash")
    if not found or "system32" in found.lower():
        pytest.fail("no usable bash: the commit-state guard's controls cannot run, and must not silently skip")
    return found


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, f"git {' '.join(args)} failed: {completed.stderr}"
    return completed.stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real repository on branch ``work`` with a second branch ``other``."""
    path = tmp_path / "repo"
    path.mkdir()
    _git(path, "init", "-q", "-b", "work")
    _git(path, "config", "user.email", "hook-test@example.invalid")
    _git(path, "config", "user.name", "Hook Test")
    (path / "a.txt").write_text("a\n", encoding="utf-8", newline="\n")
    _git(path, "add", "a.txt")
    _git(path, "commit", "-q", "--no-verify", "-m", "seed")
    _git(path, "branch", "other")
    return path


def _run(raw_stdin: str, hook: Path = HOOK, env: dict[str, str] | None = None) -> tuple[dict | None, str]:
    """Run the hook on raw stdin; return (parsed stdout JSON or None when silent, stderr)."""
    result = subprocess.run(
        [_bash(), str(hook)],
        input=raw_stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    return (json.loads(result.stdout) if result.stdout.strip() else None), result.stderr


def _payload(command: str, cwd: Path | str, session: str, tool: str, event: str) -> str:
    payload = {
        "session_id": session,
        "cwd": str(cwd),
        "hook_event_name": event,
        "tool_name": tool,
        "tool_input": {"command": command},
    }
    if event == "PostToolUse":
        payload["tool_response"] = {"stdout": "", "stderr": ""}
    return json.dumps(payload)


def _decide(raw_stdin: str) -> dict | None:
    """The hook's decision logic in-process: the same code the launcher runs, without a bash and python spawn."""
    return GUARD.decide(json.loads(raw_stdin))


def _pre(command: str, cwd: Path | str, session: str = "s1", tool: str = "Bash", launcher: bool = False) -> str:
    """The decision for a PreToolUse payload; ``launcher=True`` runs it through ``commit-state-guard.sh``."""
    raw = _payload(command, cwd, session, tool, "PreToolUse")
    output = _run(raw)[0] if launcher else _decide(raw)
    assert output is not None, "PreToolUse must always emit a decision"
    return output["hookSpecificOutput"]["permissionDecision"]


def _post(command: str, cwd: Path | str, session: str = "s1", launcher: bool = False) -> None:
    raw = _payload(command, cwd, session, "Bash", "PostToolUse")
    output = _run(raw)[0] if launcher else _decide(raw)
    assert output is None, "the PostToolUse recorder must stay silent"


PIPED_COMMITS = [
    "git commit -m 'x' 2>&1 | tail -5",
    "git add a.txt && git commit -F msg.txt | tail -30",
    "git -C some/path commit -m x | grep -v IDENTICAL",
    "git commit -m x |& tail",
    # the word pipefail somewhere in the command is not pipefail being on
    "git commit -m pipefail | tail -5",
    "set +o pipefail; git commit -m x | tail",
    "set -o pipefail; set +o pipefail; git commit -m x | tail",
    "git commit -m x | tail; set -o pipefail",
    # wrappers and grouping still run git
    "command git commit -m x | tail -5",
    "env X=1 git commit -m x | tail",
    "(git commit -m x) | tail",
]

NOT_PIPED = [
    "git commit -m 'x'",
    "set -o pipefail; git commit -m x 2>&1 | tail -5",
    "set -euo pipefail; git commit -m x | tail -5",
    "git commit -m 'subject with a | pipe inside the quotes'",
    "git log --oneline | head -3",
    "git commit -m x || echo failed",
]


@pytest.mark.parametrize("command", PIPED_COMMITS)
def test_a_piped_commit_is_refused(command: str, repo: Path) -> None:
    """A pipeline reports its last command's status, so a blocked commit would read as exit 0."""
    assert _pre(command, repo) == "deny"


@pytest.mark.parametrize("command", NOT_PIPED)
def test_unpiped_commits_and_other_pipelines_are_allowed(command: str, repo: Path) -> None:
    """Positive controls: pipefail, a quoted '|', '||', and non-commit pipelines all pass."""
    assert _pre(command, repo) == "allow"


def test_a_piped_commit_in_powershell_is_not_refused(repo: Path) -> None:
    """*New.* PowerShell's pipeline sets ``$LASTEXITCODE`` from the native command, so the pipe is no hazard
    there; the exclusion is deliberate and pinned so it cannot widen or narrow unseen."""
    assert _pre("git commit -m x | Select-Object -First 1", repo, tool="PowerShell") == "allow"


def test_a_branch_moved_by_another_writer_refuses_the_commit(repo: Path) -> None:
    """The session saw ``work``; HEAD moved to ``other`` underneath it; the commit is refused."""
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre("git commit -m x", repo) == "deny"


def test_observing_the_branch_again_admits_the_commit(repo: Path) -> None:
    """After the refusal the session re-reads git state, which records the branch it now knowingly commits to."""
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")
    assert _pre("git commit -m x", repo) == "deny"

    _post("git branch --show-current", repo)

    assert _pre("git commit -m x", repo) == "allow"


def test_a_commit_after_a_fresh_status_with_no_drift_is_admitted(repo: Path) -> None:
    """*New.* The plain positive control: the branch has not moved, so nothing is refused."""
    _post("git status", repo)

    assert _pre("git commit -m x", repo) == "allow"


def test_the_sessions_own_checkout_is_not_drift(repo: Path) -> None:
    """A branch switch the session made through a tool call is recorded, not treated as foreign."""
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")
    _post("git checkout other", repo)

    assert _pre("git commit -m x", repo) == "allow"


def test_another_sessions_checkout_refuses_this_sessions_commit(repo: Path) -> None:
    """*New.* The shape of the incident: two sessions share the worktree and one moves it. The mover's own
    commit is admitted (it recorded the move); the session that did not move it is refused."""
    _post("git status", repo, session="mine")
    _post("git status", repo, session="theirs")
    _git(repo, "checkout", "-q", "other")
    _post("git checkout other", repo, session="theirs")

    assert _pre("git commit -m x", repo, session="theirs") == "allow"
    assert _pre("git commit -m x", repo, session="mine") == "deny"


def test_each_linked_worktree_keeps_its_own_record(repo: Path, tmp_path: Path) -> None:
    """*New.* MathUni runs from several linked worktrees. The record lives in each worktree's own git dir,
    so moving one worktree's branch neither refuses nor admits a commit in another."""
    side = tmp_path / "side"
    _git(repo, "worktree", "add", "-q", "-b", "side", str(side))
    _post("git status", repo)
    _post("git status", side)
    _git(repo, "checkout", "-q", "other")

    assert _pre("git commit -m x", side) == "allow"
    assert _pre("git commit -m x", repo) == "deny"


def test_a_checkout_in_the_same_command_as_the_commit_is_not_drift(repo: Path) -> None:
    """``git checkout -b new && git commit`` moves the branch deliberately inside one call."""
    _post("git status", repo)

    assert _pre("git checkout -q -b fresh && git commit -m x", repo) == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "git checkout missing; git commit -m x",
        "git checkout missing || git commit -m x",
        "git checkout -- a.txt && git commit -m x",
    ],
)
def test_a_checkout_that_does_not_gate_the_commit_does_not_exempt_it(command: str, repo: Path) -> None:
    """Only a branch move the commit depends on through ``&&`` explains the new branch."""
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre(command, repo) == "deny"


def test_a_checkout_in_another_repository_does_not_exempt_the_commit(repo: Path, tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    _git(elsewhere, "init", "-q", "-b", "topic")
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre(f"git -C {elsewhere.as_posix()} checkout topic && git commit -m x", repo) == "deny"


@pytest.mark.parametrize("command", ["cd missing; git commit -m x", "cd missing || git commit -m x"])
def test_a_directory_change_that_can_fail_still_checks_the_original_repository(command: str, repo: Path) -> None:
    """If the ``cd`` fails the commit still runs here, so this repository's drift must still refuse it."""
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre(command, repo) == "deny"


def test_a_guarded_directory_change_moves_the_check(repo: Path, tmp_path: Path) -> None:
    """``cd elsewhere && git commit`` only commits if the cd succeeded, so the original repository is not checked."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    _git(elsewhere, "init", "-q", "-b", "topic")
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre(f"cd {elsewhere.as_posix()} && git commit -m x", repo) == "allow"


def test_git_dir_and_work_tree_select_the_repository(repo: Path, tmp_path: Path) -> None:
    _post(f"git --git-dir={(repo / '.git').as_posix()} --work-tree {repo.as_posix()} status", tmp_path)
    _git(repo, "checkout", "-q", "other")

    command = f"git --git-dir {(repo / '.git').as_posix()} --work-tree={repo.as_posix()} commit -m x"
    assert _pre(command, tmp_path) == "deny"


def test_powershell_paths_keep_their_backslashes(repo: Path, tmp_path: Path) -> None:
    """``git -C C:\\Users\\...`` in PowerShell must resolve to that directory, not ``C:Users...``.

    On a POSIX runner the path has no drive letter, so the posix spelling is used there; the point
    of the control on every platform is that the PowerShell tool name reaches the same decision.
    """
    spelled = str(repo).replace("/", "\\") if os.name == "nt" else str(repo)
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre(f"git -C {spelled} commit -m x", tmp_path, tool="PowerShell") == "deny"


def test_concurrent_recorders_keep_every_sessions_record(repo: Path) -> None:
    """Sessions record in separate files, so concurrent PostToolUse runs cannot drop each other's record."""
    sessions = [f"c{i}" for i in range(8)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda s: _post("git status", repo, session=s), sessions))
    _git(repo, "checkout", "-q", "other")

    assert all(_pre("git commit -m x", repo, session=s) == "deny" for s in sessions)


@pytest.mark.parametrize(
    "command",
    ["git commit --no-verify -m x", "git commit -n -m x", "git commit -anm x", "git push --no-verify origin work"],
)
def test_skipping_the_git_hooks_is_refused(command: str, repo: Path) -> None:
    """The owner's rule is that hooks are never skipped; the refusal holds for the day MathUni has one."""
    assert _pre(command, repo) == "deny"


def test_a_message_that_looks_like_a_flag_is_not_no_verify(repo: Path) -> None:
    assert _pre('git commit -m "-n"', repo) == "allow"


# *New* (TDL follow-up from PR #300 round 3): a hooks-path override skips the hooks exactly as --no-verify does.
HOOKS_PATH_OVERRIDES = [
    "git -c core.hooksPath=/dev/null commit -m x",
    "git -c core.hookspath=/dev/null commit -m x",
    "git -c CORE.HOOKSPATH=/dev/null commit -m x",
    "git -c user.name=a -c core.hooksPath=/dev/null commit -m x",
    "git --config-env=core.hooksPath=NOHOOKS commit -m x",
    "git --config-env core.hooksPath=NOHOOKS commit -m x",
    "GIT_CONFIG_PARAMETERS=\"'core.hookspath=/dev/null'\" git commit -m x",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -m x",
    "env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -m x",
    "git -c core.hooksPath=/dev/null push origin work",
]

HOOKS_PATH_LOOKALIKES = [
    "git -c user.name=a commit -m x",
    "git -c core.editor=true commit -m x",
    "git -c core.hooksPathology=1 commit -m x",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=user.name GIT_CONFIG_VALUE_0=core.hooksPath git commit -m x",
    "git config core.hooksPath",
    'git commit -m "core.hooksPath"',
]


@pytest.mark.parametrize("command", HOOKS_PATH_OVERRIDES)
def test_a_hooks_path_override_is_refused_like_no_verify(command: str, repo: Path) -> None:
    assert _pre(command, repo) == "deny"


@pytest.mark.parametrize("command", HOOKS_PATH_LOOKALIKES)
def test_commands_that_only_resemble_a_hooks_path_override_are_allowed(command: str, repo: Path) -> None:
    """Positive controls: other ``-c`` keys, a value that merely mentions the key, and a read of it all pass."""
    assert _pre(command, repo) == "allow"


def test_a_backgrounded_commit_is_refused_even_with_pipefail(repo: Path) -> None:
    assert _pre("set -o pipefail; git commit -m x | tail &", repo) == "deny"
    assert _pre("git commit -m x &", repo) == "deny"


def test_env_dash_c_moves_the_commit_target(repo: Path, tmp_path: Path) -> None:
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre(f"env -C {repo.as_posix()} git commit -m x", tmp_path) == "deny"
    assert _pre(f"env --chdir={repo.as_posix()} git commit -m x", tmp_path) == "deny"


def test_a_checkout_that_restores_a_path_is_not_a_branch_move(repo: Path) -> None:
    """``git checkout a.txt`` restores a file (no branch has that name), so it cannot explain a new branch."""
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre("git checkout a.txt && git commit -m x", repo) == "deny"
    assert _pre("git checkout work && git commit -m x", repo) == "allow", "a real branch move still exempts"


def _second_commit(repo: Path) -> tuple[str, str]:
    first = _git(repo, "rev-parse", "HEAD").strip()
    (repo / "b.txt").write_text("b\n", encoding="utf-8", newline="\n")
    _git(repo, "add", "b.txt")
    _git(repo, "commit", "-q", "--no-verify", "-m", "second")
    return first, _git(repo, "rev-parse", "HEAD").strip()


def test_two_distinct_detached_heads_are_not_the_same_state(repo: Path) -> None:
    """A session mid-rebase at commit A; another session detaches the shared tree at B.

    TDL's round-3 follow-up "detached A to B passes" concerns its git pre-commit gate, which compares
    symbolic refs only. This hook records the commit for a detached HEAD, so the control holds here.
    """
    first, second = _second_commit(repo)
    _git(repo, "checkout", "-q", "--detach", first)
    _post("git status", repo)
    _git(repo, "checkout", "-q", "--detach", second)

    assert _pre("git commit -m x", repo) == "deny"


def test_a_branch_session_whose_tree_was_detached_underneath_it_is_refused(repo: Path) -> None:
    """*New.* Branch to detached: the session saw ``work``; another session detached HEAD at the same commit."""
    _post("git status", repo)
    _git(repo, "checkout", "-q", "--detach")

    assert _pre("git commit -m x", repo) == "deny"


def test_a_detached_session_whose_tree_was_put_on_a_branch_underneath_it_is_refused(repo: Path) -> None:
    """*New.* Detached to branch: the reverse direction."""
    _git(repo, "checkout", "-q", "--detach")
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre("git commit -m x", repo) == "deny"


def test_a_detached_checkout_in_the_same_command_as_the_commit_is_not_drift(repo: Path) -> None:
    """*New.* The one deliberate way to move a detached HEAD, gated through ``&&``, is still admitted."""
    first, _second = _second_commit(repo)
    _post("git status", repo)

    assert _pre(f"git checkout -q --detach {first} && git commit -m x", repo) == "allow"


def test_sessions_are_isolated(repo: Path) -> None:
    """One session's observation neither refuses nor admits another session's commit."""
    _post("git status", repo, session="s1")
    _git(repo, "checkout", "-q", "other")

    assert _pre("git commit -m x", repo, session="s2") == "allow"
    assert _pre("git commit -m x", repo, session="s1") == "deny"


def test_the_commit_target_follows_git_dash_c(repo: Path, tmp_path: Path) -> None:
    """The branch checked is the one ``git -C`` commits in, not the tool call's cwd."""
    _post(f"git -C {repo.as_posix()} status", tmp_path)
    _git(repo, "checkout", "-q", "other")

    assert _pre(f"git -C {repo.as_posix()} commit -m x", tmp_path) == "deny"


def test_no_prior_observation_admits_and_records(repo: Path) -> None:
    """A first commit with no record is allowed; the guard cannot know an earlier expectation."""
    assert _pre("git commit -m x", repo, session="fresh") == "allow"


def test_non_commit_commands_are_allowed(repo: Path) -> None:
    _post("git status", repo)
    _git(repo, "checkout", "-q", "other")

    assert _pre("git push origin other", repo) == "allow"
    assert _pre("ls", repo) == "allow"


# --- fail-open must be visible -------------------------------------------------


def test_a_guard_error_fails_open_visibly() -> None:
    """Malformed input still lets the command run, with the marker _receipt-wrap records."""
    output, stderr = _run('{"tool_name": "Bash", "tool_input": {"command": "git commit -m x"')
    assert output is not None
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert "FAILING OPEN" in stderr


def test_a_recorder_error_fails_open_visibly_and_silently_on_stdout() -> None:
    """*New.* PostToolUse has no decision to emit, but the marker is the same."""
    output, stderr = _run('{"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {')
    assert output is None
    assert "FAILING OPEN" in stderr


def _project_with_hooks(tmp_path: Path) -> Path:
    """A scratch project holding byte-for-byte copies of the repository's hook scripts."""
    project = tmp_path / "project"
    shutil.copytree(HOOKS_DIR, project / ".claude" / "hooks", ignore=shutil.ignore_patterns("__pycache__", "*.log"))
    return project


def _configured_command(event: str, advisory: bool) -> str:
    """The command line settings.json wires for the guard under ``event`` -- the thing the harness runs."""
    hooks = json.loads(SETTINGS.read_text(encoding="utf-8"))["hooks"]
    commands = [
        hook["command"]
        for group in hooks[event]
        for hook in group["hooks"]
        if "commit-state-guard.sh" in hook["command"]
    ]
    assert len(commands) == 1, f"commit-state-guard.sh must be wired exactly once for {event}: {commands}"
    assert ("--advisory" in commands[0]) is advisory
    return commands[0]


def _harness(project: Path, event: str, command: str, cwd: Path, session: str = "s") -> subprocess.CompletedProcess[str]:
    """Run the command line settings.json wires for ``event``, as the harness would, on one tool call."""
    env = {**os.environ, "CLAUDE_PROJECT_DIR": project.as_posix()}
    wired = _configured_command(event, advisory=event == "PostToolUse")
    return subprocess.run(
        [_bash(), "-c", wired],
        input=_payload(command, cwd, session, "Bash", event),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=60,
    )


def _decision(result: subprocess.CompletedProcess[str]) -> str:
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]


def _receipts(project: Path) -> list[str]:
    log = project / ".claude" / "hooks" / "hook-receipts.log"
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


def test_the_launcher_reaches_the_decisions_the_matrix_asserts_in_process(repo: Path) -> None:
    """The matrix above calls ``decide`` in-process for speed. This runs one case of each decision type through
    ``commit-state-guard.sh`` itself, so a launcher that mangled stdin, dropped stdout or ate a deny would show."""
    assert _pre("git commit -m x | tail", repo, launcher=True) == "deny"
    assert _pre("git commit --no-verify -m x", repo, launcher=True) == "deny"
    assert _pre("git -c core.hooksPath=/dev/null commit -m x", repo, launcher=True) == "deny"
    assert _pre("git commit -m x &", repo, launcher=True) == "deny"
    assert _pre("git commit -m x", repo, launcher=True) == "allow"

    _post("git status", repo, launcher=True)
    _git(repo, "checkout", "-q", "other")
    assert _pre("git commit -m x", repo, launcher=True) == "deny"
    _post("git branch --show-current", repo, launcher=True)
    assert _pre("git commit -m x", repo, launcher=True) == "allow"


def test_the_configured_command_refuses_a_piped_commit_and_leaves_a_deny_receipt(repo: Path, tmp_path: Path) -> None:
    """*New.* The exact command string settings.json wires, run as the harness would: the deny reaches
    stdout and the receipt records ``decision=deny`` -- the positive execution signal."""
    project = _project_with_hooks(tmp_path)

    assert _decision(_harness(project, "PreToolUse", "git commit -m x | tail", repo)) == "deny"
    assert any("hook=commit-state-guard decision=deny" in line for line in _receipts(project))


def test_the_configured_command_admits_a_clean_commit_and_leaves_an_allow_receipt(repo: Path, tmp_path: Path) -> None:
    """*New.* The same wiring, an admitted commit: ``decision=allow`` is a receipt of a check that ran."""
    project = _project_with_hooks(tmp_path)

    assert _decision(_harness(project, "PreToolUse", "git commit -m x", repo)) == "allow"
    assert any("hook=commit-state-guard decision=allow" in line for line in _receipts(project))


def test_the_configured_recorder_feeds_the_configured_guard(repo: Path, tmp_path: Path) -> None:
    """*New.* The PostToolUse wiring end to end: it leaves a ``silent`` receipt (it ran and had nothing to say),
    and what it recorded is what the PreToolUse wiring then checks the commit against."""
    project = _project_with_hooks(tmp_path)
    post = _harness(project, "PostToolUse", "git status", repo)
    assert post.returncode == 0 and not post.stdout.strip(), post.stderr
    assert any("hook=commit-state-guard decision=silent" in line for line in _receipts(project))
    _git(repo, "checkout", "-q", "other")

    assert _decision(_harness(project, "PreToolUse", "git commit -m x", repo)) == "deny"


def test_a_fail_open_through_the_configured_command_is_a_failopen_receipt(tmp_path: Path) -> None:
    """*New.* Fail-open is visible twice over: the marker on stderr and ``decision=FAILOPEN`` in the log, so
    "nothing to refuse" and "the check never ran" cannot look alike afterwards."""
    project = _project_with_hooks(tmp_path)
    env = {**os.environ, "CLAUDE_PROJECT_DIR": project.as_posix()}
    result = subprocess.run(
        [_bash(), "-c", _configured_command("PreToolUse", advisory=False)],
        input='{"tool_name": "Bash", "tool_input": {"command": "git commit',
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=60,
    )

    assert "FAILING OPEN" in result.stderr
    assert _decision(result) == "allow"
    assert any("hook=commit-state-guard decision=FAILOPEN" in line for line in _receipts(project))


def test_the_guard_is_wired_before_and_after_both_shell_tools() -> None:
    """A guard that exists but is not wired guards nothing; the recorder must be advisory-wrapped."""
    hooks = json.loads(SETTINGS.read_text(encoding="utf-8"))["hooks"]
    for event, advisory in (("PreToolUse", False), ("PostToolUse", True)):
        wired = [
            group
            for group in hooks[event]
            for hook in group["hooks"]
            if "commit-state-guard.sh" in hook["command"] and "_receipt-wrap.sh" in hook["command"]
        ]
        assert len(wired) == 1, f"commit-state-guard.sh must be wired exactly once for {event}"
        assert set(wired[0]["matcher"].split("|")) >= {"Bash", "PowerShell"}
        command = next(h["command"] for h in wired[0]["hooks"] if "commit-state-guard.sh" in h["command"])
        assert ("--advisory" in command) is advisory


def test_the_receipt_wrapper_selftests_pass() -> None:
    """The wrapper's own sanitizer and mode negative controls still hold in this repository."""
    result = subprocess.run(
        [_bash(), str(RECEIPT_WRAP), "--selftest"], capture_output=True, text=True, encoding="utf-8", timeout=120
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "FAIL:" not in result.stdout


# --- the hook scripts must be executable bytes ----------------------------------


def _tracked_hook_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", ".claude/hooks"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line]


def test_every_hook_file_is_pinned_to_lf_and_carries_no_carriage_returns() -> None:
    """A CRLF shebang is ``#!/bin/bash\\r`` and a hook that does not run looks like one that found nothing.

    Checked on the staged blob (what every other clone receives) and on the working-tree bytes (what runs here).
    """
    files = _tracked_hook_files()
    assert {Path(f).name for f in files} >= {"_receipt-wrap.sh", "commit-state-guard.sh", "commit_state_guard.py"}, files
    for rel in files:
        attr = subprocess.run(
            ["git", "check-attr", "eol", "--", rel], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout
        assert attr.rsplit(":", 1)[-1].strip() == "lf", f"{rel} is not pinned to eol=lf"
        staged = subprocess.run(["git", "cat-file", "blob", f":{rel}"], cwd=REPO_ROOT, capture_output=True, check=True)
        assert b"\r" not in staged.stdout, f"{rel} is committed with a carriage return"
        assert b"\r" not in (REPO_ROOT / rel).read_bytes(), f"{rel} has a carriage return in the working tree"


def test_the_crlf_predicate_flags_crlf_bytes() -> None:
    """Negative control for the check above: the byte test rejects a CRLF shebang rather than passing on clean blobs."""
    assert b"\r" in b"#!/bin/bash\r\necho hi\r\n"
    assert b"\r" not in b"#!/bin/bash\necho hi\n"
