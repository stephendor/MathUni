#!/bin/bash
# commit-state-guard: refuse a git commit whose outcome the session would misread.
#
# PreToolUse (Bash, PowerShell): denies `git commit ... | tail` without pipefail,
# because a pipeline reports its last command's status and a commit blocked by a
# hook then reads as exit 0 (obs 2026-09-08-blocked-commit-reported-exit-zero); denies
# a commit when HEAD is not the branch this session last saw in that repository
# (obs 2026-09-09-the-branch-moved-under-a-running-session); and denies skipping the
# git hooks (--no-verify, -c core.hooksPath=...).
# PostToolUse (Bash, PowerShell): records the branch of every repository a git
# command touched, one file per session, under <absolute-git-dir>/session-branches/.
#
# Logic lives in commit_state_guard.py. Fails OPEN with the FAILING OPEN marker that
# _receipt-wrap.sh records as decision=FAILOPEN in hook-receipts.log. Unlike the TDL
# original, nothing backs this hook up when it cannot run: MathUni has no git hooks, so
# the receipt is the only trace that a commit went unchecked.

INPUT=$(cat)
HERE=$(cd "$(dirname "$0")" && pwd)

OUTPUT=$(printf '%s' "$INPUT" | python "$HERE/commit_state_guard.py" 2>/dev/null)
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
  printf 'commit-state-guard: hook errored or timed out -- FAILING OPEN (command allowed).\n' >&2
  if printf '%s' "$INPUT" | grep -q '"PostToolUse"'; then
    exit 0
  fi
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
  exit 0
fi

printf '%s' "$OUTPUT"
exit 0
