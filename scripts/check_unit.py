"""Run the manifest-owned quality gates for one unit or the whole corpus."""
import argparse
import json
import os
import subprocess
import sys
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "curriculum", "unit-gates.json")
ZERO_REFS = os.path.join(REPO, "curriculum", "coverage-zero-refs.json")
SYLLABUS = os.path.join(REPO, "curriculum", "syllabus.yaml")


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def unit_context(uid):
    module = uid.rsplit("-", 1)[0]
    return {"unit": uid, "module": module,
            "problem": os.path.join("problems", "sets", uid + ".md"),
            "lesson": os.path.join("lessons", module, uid + ".html")}


def commands_for_unit(uid, ci=False, manifest_path=MANIFEST,
                      zero_refs_path=ZERO_REFS):
    manifest = load_json(manifest_path)
    zero_refs = load_json(zero_refs_path)
    context = unit_context(uid)
    commands = []
    for gate in manifest["gates"]:
        if ci and not gate.get("ci", False):
            continue
        if gate.get("modules") and context["module"] not in gate["modules"]:
            continue
        argv = [part.format(**context) for part in gate["argv"]]
        if gate.get("kind") == "coverage" and uid in zero_refs:
            argv[1:1] = ["--expect-zero-refs", zero_refs[uid]]
        commands.append((gate["id"], [sys.executable] + argv))
    return commands


def stale_zero_refs(manifest, zero_refs, units):
    """coverage-zero-refs entries that can no longer excuse anything.

    `coverage-zero-refs.json` names units whose sources carry no NUMBERED
    results, so the coverage gate is run with `--expect-zero-refs <reason>`
    instead of a minimum. That is an allowlist, and an allowlist without
    stale-entry detection is a suppression list with a comment: "the unit was
    rewritten to cite numbered results, but the exemption is still listed"
    emits no signal at all, which is how such a list becomes permanent.

    Half the ratchet is already built and lives in the gate itself:
    `check_lesson_coverage.py --expect-zero-refs` FAILS when refs are in fact
    found, so a listed unit that starts passing on its own merits cannot stay
    listed silently. This is the other half -- the entry that outlives the
    thing it excused:

      * a listed unit that the syllabus no longer governs;
      * a listed unit whose manifest gates include no coverage gate, so the
        exemption is never read and could never fire either way.

    Both are resolved against the syllabus and the manifest, never against the
    units this invocation happens to name, so `check_unit.py one-unit` cannot
    accuse the other entries of being stale.

    Returns [(uid, why)].
    """
    stale = []
    for uid in sorted(zero_refs):
        if uid not in units:
            stale.append((uid, "no unit %s in the syllabus" % uid))
            continue
        module = uid.rsplit("-", 1)[0]
        has_coverage = any(
            gate.get("kind") == "coverage"
            and (not gate.get("modules") or module in gate["modules"])
            for gate in manifest["gates"])
        if not has_coverage:
            stale.append((uid, "no coverage gate applies to %s, so the"
                               " exemption is never read" % uid))
    return stale


def load_syllabus_units(path=SYLLABUS):
    with open(path, encoding="utf-8") as handle:
        return {row["id"] for row in yaml.safe_load(handle)["units"]}


def discovered_units():
    # The syllabus owns the governed population.  Deriving --all from an
    # artifact intersection made deletion remove the unit from the run; using
    # the registry ensures run_unit sees and rejects either missing half.
    return sorted(load_syllabus_units())


def run_unit(uid, ci=False):
    context = unit_context(uid)
    missing = [path for path in (context["problem"], context["lesson"])
               if not os.path.isfile(os.path.join(REPO, path))]
    if missing:
        print("FAIL %s missing %s" % (uid, ", ".join(missing)))
        return 1
    failed = False
    for gate, command in commands_for_unit(uid, ci=ci):
        print("=== %s :: %s" % (uid, gate), flush=True)
        result = subprocess.run(command, cwd=REPO, text=True)
        if result.returncode:
            failed = True
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("unit", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args(argv)
    if args.all == bool(args.unit):
        parser.error("give exactly one UNIT or --all")
    units = discovered_units() if args.all else [args.unit]
    failed = [uid for uid in units if run_unit(uid, ci=args.ci)]
    stale = stale_zero_refs(load_json(MANIFEST), load_json(ZERO_REFS),
                            load_syllabus_units())
    for uid, why in stale:
        print("STALE %s is listed in curriculum/coverage-zero-refs.json but %s."
              " The list is a ratchet and may only shrink -- strike the entry."
              % (uid, why))
    print("%s %d unit(s) checked, %d failed, %d stale coverage-zero-refs"
          " entr%s"
          % ("FAIL" if failed or stale else "PASS", len(units), len(failed),
             len(stale), "y" if len(stale) == 1 else "ies"))
    return 1 if failed or stale else 0


if __name__ == "__main__":
    sys.exit(main())
