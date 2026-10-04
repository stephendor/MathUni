"""ratchet.py -- the one allowlist ratchet every `--known-failing` list uses.

A drift list is only a ratchet if it has all three rules, and the third is the
one a copier drops:

  * a listed entry that now PASSES is stale and fails the run;
  * a listed entry whose subject is gone is stale and fails the run;
  * with --baseline, an entry ADDED since the base ref fails the run, so the
    list may only shrink. (Found by Codex on PR #20 for mission.py, and again
    on PR #32 for the canvas-label list, which had been "built on mission.py's
    shape" and copied the first two rules only.)

Those rules live here, behind one method, so a list cannot adopt one without
the others: `Ratchet.check` takes the verdicts and the existence predicate it
needs for the stale rules as REQUIRED arguments, and runs the growth rule in the
same call. `Ratchet.from_argv` is the only place `--known-failing` and
`--baseline` are parsed. `tests/test_allowlist_ratchets.py` fails any script
that mentions `--known-failing` without using this module, and any committed
drift list with no CI step that passes `--baseline`.

Exit codes follow mission.py: 1 means a ratchet rule fired, 2 means no verdict
could be reached (an unreadable list or baseline).
"""
import os


class Unreadable(Exception):
    """A ratchet input exists but could not be read. Verdict 2, not 1."""


class Usage(Exception):
    """The ratchet flags were malformed. Verdict 2."""


def load_known_failing(path):
    """Entry ids excused from failing, one per line; '#' starts a comment.

    A missing file is an EMPTY list, not an error, so the finished state can be
    reached at all, and so deleting the file cannot be used to escape the gate.
    But the file is PERMANENT: the zero state is an empty list, not a deleted
    one (see `Ratchet.check`, which refuses a deletion). An UNREADABLE file is
    neither empty nor a verdict: it raises `Unreadable`, so exit 1 never means
    "the gate could not read its own inputs". (Codex review of PR #20.)
    """
    ids = set()
    if not os.path.exists(path):
        return ids
    try:
        f = open(path, encoding="utf-8")
    except OSError as e:
        raise Unreadable("%s: %s" % (path, e)) from e
    with f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                ids.add(line)
    return ids


def additions_against(baseline_path, current):
    """Ids in the current list that the baseline did not have.

    Returns (additions, baseline_existed). A baseline that does not exist is
    reported as such rather than silently treated as empty: on the commit that
    introduces the list there is nothing to compare against, and that must be
    visible instead of looking like a clean comparison.
    """
    if not os.path.exists(baseline_path):
        return set(), False
    return current - load_known_failing(baseline_path), True


class Ratchet:
    def __init__(self, listfile, entries, baseline, label, remedy, subject="subject"):
        self.listfile = listfile
        self.entries = frozenset(entries)
        self.baseline = baseline
        self.label = label
        self.remedy = remedy
        self.subject = subject

    @classmethod
    def from_argv(cls, argv, *, label, remedy, subject="subject"):
        """Consume leading `--known-failing X` / `--baseline Y` flags.

        Returns (ratchet, remaining argv). `label` names the list in messages
        ("mission drift list"); `remedy` says what to do instead of listing
        ("Repair the lesson instead."); `subject` names what an entry stands
        for ("lesson"). Raises `Unreadable` for a list that
        exists but cannot be read, and `Usage` for `--baseline` without
        `--known-failing`.
        """
        listfile, baseline, entries = None, None, set()
        while len(argv) >= 2 and argv[0] in ("--known-failing", "--baseline"):
            if argv[0] == "--known-failing":
                listfile = argv[1]
                entries = load_known_failing(listfile)
            else:
                baseline = argv[1]
            argv = argv[2:]
        if baseline is not None and listfile is None:
            raise Usage("--baseline needs --known-failing")
        return cls(listfile, entries, baseline, label, remedy, subject), argv

    def excused(self, uid):
        return uid in self.entries

    def check(self, verdicts, *, exists, out=print, note=print):
        """Apply all three ratchet rules and return 0 or 1, printing each finding.

        `verdicts` maps an entry id to 1 if its subject still fails and 0 if it
        passes now, for every entry the caller judged this run. `exists(uid)`
        says whether an entry's subject is still there; it is asked about every
        entry that was not judged. Both are required: there is no way to run the
        growth rule without the stale rules, or the reverse. `out` receives each
        finding and `note` each informational line (both default to print).
        """
        rc = 0
        if self.baseline is not None:
            added, existed = additions_against(self.baseline, set(self.entries))
            if existed and not os.path.exists(self.listfile):
                # The base ref has a list and this ref does not. Deleting it
                # reopens the ratchet: "base has no list" stops meaning "the
                # introducing commit". (Codex review of PR #20, rounds 2 and 4.)
                out("DELETED %s existed at the baseline and is gone here. The"
                      " %s is permanent -- empty it, do not delete it, or the"
                      " growth check can never tell a reintroduction from the"
                      " original rollout." % (self.listfile, self.label))
                return 1
            if not existed:
                note("NOTE no baseline at %s -- this is the commit that"
                      " introduces the list, so there is nothing it could have"
                      " grown from" % self.baseline)
            elif added:
                for uid in sorted(added):
                    out("GREW %s was added to %s; the %s is a ratchet and"
                          " may only shrink. %s"
                          % (uid, self.listfile, self.label, self.remedy))
                rc = 1
            else:
                note("PASS %s has no additions against %s"
                      % (self.label, self.baseline))
        for uid in sorted(self.entries):
            if uid in verdicts:
                if verdicts[uid] == 0:
                    out("STALE %s passes now -- strike it from %s"
                          % (uid, self.listfile))
                    rc = 1
            elif not exists(uid):
                out("STALE %s is listed in %s but has no %s"
                      % (uid, self.listfile, self.subject))
                rc = 1
        return rc


# --- completeness: derived from the repository, never from a hand list --------

def _workflow_commands(root):
    """Every logical command line in every workflow `run:` block, as token lists."""
    import glob
    import shlex
    import yaml
    commands = []
    for path in sorted(glob.glob(os.path.join(root, ".github", "workflows", "*.y*ml"))):
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        for job in (doc.get("jobs") or {}).values():
            for step in job.get("steps") or []:
                run = step.get("run")
                if not isinstance(run, str):
                    continue
                for line in run.replace("\\\n", " ").splitlines():
                    try:
                        commands.append(shlex.split(line, comments=True))
                    except ValueError:
                        # An unbalanced quote (a multi-line string, an apostrophe
                        # in prose) must not hide a flag on the same line.
                        commands.append(line.split())
    return commands


def _value_after(tokens, flag):
    return tokens[tokens.index(flag) + 1] if flag in tokens[:-1] else None


def committed_drift_lists(root):
    """Every drift list the repository has, derived rather than enumerated.

    The union of: any `*-drift.txt` under `curriculum/`, any path named after
    `--known-failing` in a per-unit gate manifest, and any path named after it
    in a workflow. A list that is none of these and is wired nowhere is
    invisible to this check -- the limit of deriving the set from the repo.
    """
    import glob
    import json
    found = {os.path.relpath(p, root).replace(os.sep, "/")
             for p in glob.glob(os.path.join(root, "curriculum", "**", "*-drift.txt"),
                                recursive=True)}
    manifest = os.path.join(root, "curriculum", "unit-gates.json")
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as f:
            for gate in json.load(f).get("gates", []):
                value = _value_after(gate.get("argv", []), "--known-failing")
                if value:
                    found.add(value)
    for tokens in _workflow_commands(root):
        value = _value_after(tokens, "--known-failing")
        if value:
            found.add(value)
    return found


def lists_without_baseline_step(root):
    """Drift lists no CI step passes with `--baseline` -- lists that can grow unseen."""
    guarded = set()
    for tokens in _workflow_commands(root):
        listed = _value_after(tokens, "--known-failing")
        if listed and _value_after(tokens, "--baseline"):
            guarded.add(listed)
    return sorted(committed_drift_lists(root) - guarded)


def scripts_parsing_lists_without_the_helper(root):
    """Scripts that handle `--known-failing` but do not use this module: a re-copy of the shape."""
    import glob
    offenders = []
    for path in sorted(glob.glob(os.path.join(root, "scripts", "*.py"))):
        if os.path.basename(path) == "ratchet.py":
            continue
        with open(path, encoding="utf-8") as f:
            source = f.read()
        if '"--known-failing"' in source and "scripts.ratchet" not in source:
            offenders.append(os.path.relpath(path, root).replace(os.sep, "/"))
    return offenders
