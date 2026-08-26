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
    print("%s %d unit(s) checked, %d failed"
          % ("FAIL" if failed else "PASS", len(units), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
