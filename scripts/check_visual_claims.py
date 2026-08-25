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
    failures = run_probes(text)
    for name, detail in failures:
        print("FAIL visual claim %s: %s" % (name, detail))
    print("%s %d visual claim probe(s)" % (
        "FAIL" if failures else "PASS", len(found)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
