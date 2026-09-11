"""Prove the two skill trees are one file, modulo the substitutions declared here.

`.claude/skills/` and `.agents/skills/` are two copies of one set of skills.
They must differ in exactly the ways this file declares and in no other way.

Nothing checked that before. A blanket `claude` -> `Codex` rewrite of the
`.agents/` copy once rewrote a MODEL ID along with the branding, leaving
`Codex-sonnet-5` -- an id no provider serves -- in
`.agents/skills/ingest/SKILL.md`, where it sat until someone happened to diff
the trees by hand. A rename is a rewrite of every token that matches, including
the ones whose value is not prose.

The declared difference is one rule: a skill that cites a sibling skill's path
cites the copy in its OWN tree. Normalising each file's own tree prefix to a
sentinel makes the two copies byte-identical, and anything left over is drift.
That catches the inverse defect for free -- a file in one tree pointing into the
other tree does not normalise, so it fails rather than passing as "identical".

  python scripts/check_skill_mirror.py
  python scripts/check_skill_mirror.py --selftest

Exit 0 clean, 1 on drift, 2 if the check could not run. The clean path prints
what it compared, not just that it passed: a gate whose success is silent is
indistinguishable from a gate that never ran.
"""
import argparse
import os
import sys
import tempfile

for _stream in (sys.stdout, sys.stderr):  # cp1252-safe console
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The two trees, and the path prefix each one's files use to cite themselves.
TREES = (".claude/skills", ".agents/skills")
SELF = "<own-tree>/skills/"

# Files that legitimately exist in one tree only. Keep this list short and
# reasoned: every entry is a hole in the check. An OpenAI agent manifest has no
# meaning in the Claude tree, so its absence there is the correct state rather
# than a mirroring failure.
ALLOWED_ONLY_IN = {
    ".agents/skills": {"MathUni/agents/openai.yaml"},
    ".claude/skills": set(),
}

# Reported per file before truncating, so one reformatted file cannot bury the
# rest of the output.
MAX_LINES_SHOWN = 5


def normalise(text, own_tree):
    """Replace a file's own tree prefix with a sentinel.

    Only its OWN prefix: a `.claude/skills/...` path inside an `.agents/` file
    is left alone deliberately, so it shows up as drift.
    """
    return text.replace(own_tree + "/", SELF)


def walk(root):
    """relative posix path -> absolute path, for every file under root."""
    found = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            found[rel] = full
        # __pycache__ and the like have no business in a skill tree, so they are
        # not filtered out here -- if one appears, it should be reported.
    return found


def read(path):
    """Read a skill file while preserving its original line endings."""
    with open(path, encoding="utf-8", newline="") as handle:
        return handle.read()


def compare(root_a, root_b, tree_a=TREES[0], tree_b=TREES[1],
            allowed_only_in=None):
    """Errors describing every undeclared difference between two skill trees."""
    allowed = allowed_only_in if allowed_only_in is not None else ALLOWED_ONLY_IN
    files_a, files_b = walk(root_a), walk(root_b)
    errors = []

    for rel in sorted(set(files_a) - set(files_b)):
        if rel not in allowed.get(tree_a, set()):
            errors.append("%s: present in %s, missing from %s" % (rel, tree_a, tree_b))
    for rel in sorted(set(files_b) - set(files_a)):
        if rel not in allowed.get(tree_b, set()):
            errors.append("%s: present in %s, missing from %s" % (rel, tree_b, tree_a))

    compared = 0
    for rel in sorted(set(files_a) & set(files_b)):
        try:
            text_a = normalise(read(files_a[rel]), tree_a)
            text_b = normalise(read(files_b[rel]), tree_b)
        except UnicodeDecodeError as exc:
            errors.append("%s: not readable as utf-8 (%s)" % (rel, exc))
            continue
        compared += 1
        if text_a == text_b:
            continue
        lines_a, lines_b = text_a.splitlines(), text_b.splitlines()
        before = len(errors)
        shown = 0
        for num, (line_a, line_b) in enumerate(zip(lines_a, lines_b), start=1):
            if line_a == line_b:
                continue
            if shown >= MAX_LINES_SHOWN:
                errors.append("%s: ...further differences not shown" % rel)
                break
            errors.append(
                "%s: line %d differs and no declared substitution explains it\n"
                "    %s: %s\n"
                "    %s: %s" % (rel, num, tree_a, line_a.strip(), tree_b, line_b.strip()))
            shown += 1
        if len(lines_a) != len(lines_b):
            errors.append("%s: %s has %d lines, %s has %d"
                          % (rel, tree_a, len(lines_a), tree_b, len(lines_b)))
        if len(errors) == before:
            # The texts differ but every line compares equal: splitlines()
            # drops terminators, so a missing final newline or a CRLF/LF
            # difference produced NO diagnostic and the gate reported the trees
            # identical -- against its own byte-identical contract. Unequal
            # texts must never yield zero errors. (Codex review of PR #32.)
            errors.append("%s: differs only in line endings or a final newline"
                          " (%s ends %r, %s ends %r)"
                          % (rel, tree_a, text_a[-2:], tree_b, text_b[-2:]))
    return errors, compared


def _write(root, rel, text):
    """Write a synthetic skill-tree file for the self-test."""
    path = os.path.join(root, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def selftest():
    """Negative control: plant each defect this gate exists to catch and prove
    it fires, then prove the declared substitution does NOT make it fire.

    A gate nobody has watched fail is a gate nobody knows is wired up.
    """
    total, fails = [0], []

    def check_one(name, cond):
        """Record and print one self-test assertion."""
        total[0] += 1
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        a = os.path.join(tmp, "claude")
        b = os.path.join(tmp, "agents")
        empty = {TREES[0]: set(), TREES[1]: set()}

        def run(files_a, files_b, allowed=empty):
            """Populate two temporary trees and compare their contents."""
            for root in (a, b):
                for dirpath, _d, names in os.walk(root, topdown=False):
                    for name in names:
                        os.remove(os.path.join(dirpath, name))
                    if dirpath != root:
                        os.rmdir(dirpath)
            for rel, text in files_a.items():
                _write(a, rel, text)
            for rel, text in files_b.items():
                _write(b, rel, text)
            return compare(a, b, TREES[0], TREES[1], allowed)

        same = {"x/SKILL.md": "# x\n\nRun under Sonnet (claude-sonnet-5).\n"}
        errors, compared = run(same, dict(same))
        check_one("identical trees pass", errors == [] and compared == 1)

        # The defect that motivated this gate, exactly as it occurred.
        mangled = {"x/SKILL.md": "# x\n\nRun under Sonnet (Codex-sonnet-5).\n"}
        errors, _ = run(same, mangled)
        check_one("a model id mangled by a blanket rename fires the gate",
                  len(errors) == 1 and "line 3 differs" in errors[0]
                  and "Codex-sonnet-5" in errors[0])

        # The one difference that IS declared: each tree cites its own copy.
        cites_a = {"t/SKILL.md": "See .claude/skills/lecture/SKILL.md for each.\n"}
        cites_b = {"t/SKILL.md": "See .agents/skills/lecture/SKILL.md for each.\n"}
        errors, _ = run(cites_a, cites_b)
        check_one("the declared self-tree path substitution does not fire",
                  errors == [])

        # ...and the inverse: a file citing the tree it does not live in.
        errors, _ = run(cites_a, dict(cites_a))
        check_one("a file citing the other tree's path fires the gate",
                  len(errors) == 1 and "line 1 differs" in errors[0])

        errors, _ = run(same, {})
        check_one("a file missing from one tree fires the gate",
                  len(errors) == 1 and "missing from" in errors[0])

        extra = dict(same)
        extra["x/notes.md"] = "stray\n"
        errors, _ = run(same, extra)
        check_one("an undeclared extra file fires the gate",
                  len(errors) == 1 and "missing from" in errors[0])

        errors, _ = run(same, extra, {TREES[0]: set(), TREES[1]: {"x/notes.md"}})
        check_one("...and a declared one-tree-only file does not",
                  errors == [])

        errors, _ = run(same, {"x/SKILL.md": "# x\n\nRun under Sonnet (claude-sonnet-5).\nextra\n"})
        check_one("a trailing added line fires the gate",
                  any("has 3 lines" in e and "has 4" in e for e in errors))

        errors, _ = run(same, {"x/SKILL.md": same["x/SKILL.md"].rstrip("\n")})
        check_one("a file differing only by its final newline fires the gate",
                  len(errors) == 1 and "final newline" in errors[0])

        errors, _ = run(same, {"x/SKILL.md": same["x/SKILL.md"].replace("\n", "\r\n")})
        check_one("a file differing only in CRLF line endings fires the gate",
                  len(errors) == 1 and "line endings" in errors[0])

    print("\n%d/%d self-checks passed" % (total[0] - len(fails), total[0]))
    return 1 if fails else 0


def main(argv=None):
    """Compare the repository's Claude and Codex skill trees."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true",
                        help="prove the gate can fire, without touching the repo")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()

    roots = [os.path.join(REPO, tree.replace("/", os.sep)) for tree in TREES]
    missing = [tree for tree, root in zip(TREES, roots) if not os.path.isdir(root)]
    if missing:
        print("ERROR: skill mirror inputs unavailable: no %s" % ", ".join(missing))
        return 2

    errors, compared = compare(roots[0], roots[1])
    for error in errors:
        print("ERROR: %s" % error)
    if errors:
        return 1
    print("skill mirrors identical: %d files compared across %s and %s"
          % (compared, TREES[0], TREES[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
