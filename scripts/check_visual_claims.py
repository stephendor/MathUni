"""Execute pure visual-claim probes embedded beside canvas computations."""
import argparse
import os
import re
import subprocess
import sys
import tempfile


PROBE = re.compile(
    r"// VISUAL-CLAIM-PROBE-BEGIN\s+([^\s]+)\s*\n(.*?)"
    r"// VISUAL-CLAIM-PROBE-END",
    re.S,
)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = {
    "lessons/la/la-15.html": {"spectral-eigenvector-angle"},
}


def probes(text):
    return PROBE.findall(text)


def run_probes(text, node="node"):
    failures = []
    for name, source in probes(text):
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", encoding="utf-8", delete=False) as handle:
            handle.write(source)
            path = handle.name
        try:
            result = subprocess.run([node, path], capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=10)
        finally:
            os.unlink(path)
        if result.returncode:
            failures.append((name, (result.stderr or result.stdout).strip()))
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_path")
    args = parser.parse_args(argv)
    with open(args.lesson_path, encoding="utf-8") as handle:
        text = handle.read()
    found = probes(text)
    rel = os.path.relpath(os.path.abspath(args.lesson_path), REPO).replace("\\", "/")
    missing = sorted(REQUIRED.get(rel, set()) - {name for name, _ in found})
    failures = run_probes(text)
    failures.extend((name, "required probe is missing") for name in missing)
    for name, detail in failures:
        print("FAIL visual claim %s: %s" % (name, detail))
    print("%s %d visual claim probe(s)" % (
        "FAIL" if failures else "PASS", len(found)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
