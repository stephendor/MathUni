"""Verify that a `lab` problem set's recorded outputs are what the code produces.

Every other gate in the suite asks "is this well formed?". The `lab` module's
claim is different in kind: not "this theorem is cited" but "this code was run,
in this environment, and produced this". Nothing checked that, so the recorded
output rested on the author's word — the self-attestation pattern the project's
failure record blames for most of its defects.

This gate re-derives the three things that claim depends on:

1. **The environment.** An ```env``` block pins ``distribution==version`` lines.
   Each pin is checked against what the target interpreter actually has
   installed, via ``importlib.metadata``, so a set recorded under giotto-tda
   0.6.2 cannot be silently re-verified under a different resolve.
2. **The outputs.** Each ```python id=<name>``` block is paired with a
   ```text id=<name>``` block. The code blocks run in order in one interpreter,
   sharing state like a notebook; each block's stdout is captured separately and
   compared with its recorded pair.
3. **Determinism.** The whole file runs twice by default. Unseeded randomness
   produces a set whose outputs are true once and false thereafter, which is
   exactly the failure a single run cannot see. ``--repeat 1`` opts out.

Only blocks carrying ``id=`` participate, so a set can still show code the
reader is meant to complete without the gate trying to run it.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

FENCE = re.compile(
    r"(?m)^```(?P<info>[^\n`]*)\n(?P<body>.*?)^```[ \t]*$",
    re.DOTALL,
)
_ID = re.compile(r"\bid\s*=\s*([A-Za-z0-9_.-]+)")
_PIN = re.compile(r"^([A-Za-z0-9_.-]+)\s*==\s*([A-Za-z0-9_.+-]+)$")

PYTHON_LANGS = {"python", "py"}
OUTPUT_LANGS = {"text", "output", "console"}


class LabSetError(Exception):
    """The problem set's blocks are malformed, before any code is run."""


def _normalise(text):
    """Trailing whitespace and surrounding blank lines are not output."""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def parse_env_pins(markdown_text):
    """Return ``{distribution: version}`` from the set's ```env``` block.

    A set with no ```env``` block returns ``{}`` and is reported as unpinned by
    the caller rather than quietly accepted.
    """
    pins = {}
    for match in FENCE.finditer(markdown_text):
        if match.group("info").strip().split(" ")[0] != "env":
            continue
        for raw in match.group("body").split("\n"):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            pin = _PIN.match(line)
            if pin is None:
                raise LabSetError(
                    "env block line is not 'name==version': %r" % line)
            pins[pin.group(1)] = pin.group(2)
    return pins


def parse_blocks(markdown_text):
    """Return ``[(id, code, expected_output)]`` in document order.

    Raises :class:`LabSetError` when an id is duplicated, when a code block has
    no recorded output, or when an output block matches no code block — each of
    which would otherwise let a block skip verification silently.
    """
    code = []
    outputs = {}
    seen_code = set()
    for match in FENCE.finditer(markdown_text):
        info = match.group("info").strip()
        lang = info.split(" ")[0] if info else ""
        found = _ID.search(info)
        if found is None:
            continue
        block_id = found.group(1)
        if lang in PYTHON_LANGS:
            if block_id in seen_code:
                raise LabSetError("duplicate python block id: %s" % block_id)
            seen_code.add(block_id)
            code.append((block_id, match.group("body")))
        elif lang in OUTPUT_LANGS:
            if block_id in outputs:
                raise LabSetError("duplicate output block id: %s" % block_id)
            outputs[block_id] = match.group("body")

    for block_id, _ in code:
        if block_id not in outputs:
            raise LabSetError("python block '%s' has no recorded output" % block_id)
    for block_id in outputs:
        if block_id not in seen_code:
            raise LabSetError("output block '%s' matches no python block" % block_id)

    return [(bid, body, outputs[bid]) for bid, body in code]


DRIVER = r'''
import contextlib, io, json, sys, traceback

with open(sys.argv[1], encoding="utf-8") as handle:
    spec = json.load(handle)

results = {"versions": {}, "python": ".".join(str(p) for p in sys.version_info[:3])}

try:
    from importlib.metadata import version as _dist_version, PackageNotFoundError
except ImportError:
    _dist_version = None

for dist in spec["pins"]:
    if dist == "python" or _dist_version is None:
        continue
    try:
        results["versions"][dist] = _dist_version(dist)
    except PackageNotFoundError:
        results["versions"][dist] = None

shared = {"__name__": "__lab__"}
captured = {}
for block_id, source in spec["blocks"]:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(compile(source, "<%s>" % block_id, "exec"), shared)
    except Exception:
        captured[block_id] = {
            "stdout": buffer.getvalue(),
            "error": traceback.format_exc(limit=3),
        }
        break
    captured[block_id] = {"stdout": buffer.getvalue(), "error": None}

results["blocks"] = captured
sys.stdout.write("\n<<<LAB-RESULTS>>>\n")
sys.stdout.write(json.dumps(results))
'''


def run_blocks(python_executable, blocks, pins, timeout=900):
    """Execute the blocks in one interpreter and return the driver's report."""
    spec = {"blocks": [[bid, code] for bid, code, _ in blocks],
            "pins": sorted(pins)}
    workdir = tempfile.mkdtemp(prefix="labgate-")
    spec_path = os.path.join(workdir, "spec.json")
    driver_path = os.path.join(workdir, "driver.py")
    with open(spec_path, "w", encoding="utf-8") as handle:
        json.dump(spec, handle)
    with open(driver_path, "w", encoding="utf-8") as handle:
        handle.write(DRIVER)
    environment = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0")
    completed = subprocess.run(
        [python_executable, driver_path, spec_path],
        capture_output=True, text=True, encoding="utf-8",
        timeout=timeout, env=environment,
    )
    marker = "\n<<<LAB-RESULTS>>>\n"
    if marker not in completed.stdout:
        raise LabSetError(
            "driver produced no result block (exit %d)\n%s"
            % (completed.returncode, completed.stderr[-2000:]))
    return json.loads(completed.stdout.split(marker, 1)[1])


def check_versions(pins, report):
    """Return failure lines for pins the interpreter does not satisfy."""
    failures = []
    for dist, pinned in sorted(pins.items()):
        actual = report["python"] if dist == "python" else report["versions"].get(dist)
        if actual is None:
            failures.append("FAIL env %s is pinned at %s and is not installed"
                            % (dist, pinned))
        elif actual != pinned:
            failures.append("FAIL env %s is pinned at %s and the interpreter has %s"
                            % (dist, pinned, actual))
    return failures


def compare_outputs(blocks, report):
    """Return failure lines for blocks whose stdout is not what was recorded."""
    failures = []
    for block_id, _, expected in blocks:
        observed = report["blocks"].get(block_id)
        if observed is None:
            failures.append("FAIL %s did not run (an earlier block raised)" % block_id)
            continue
        if observed["error"]:
            failures.append("FAIL %s raised\n%s" % (block_id, observed["error"].rstrip()))
            continue
        want = _normalise(expected)
        got = _normalise(observed["stdout"])
        if want != got:
            failures.append(
                "FAIL %s output differs\n  recorded: %r\n  produced: %r"
                % (block_id, want, got))
    return failures


def compare_runs(blocks, first, second):
    """Return failure lines for blocks that did not repeat themselves."""
    failures = []
    for block_id, _, _ in blocks:
        a = first["blocks"].get(block_id, {}).get("stdout")
        b = second["blocks"].get(block_id, {}).get("stdout")
        if _normalise(a or "") != _normalise(b or ""):
            failures.append(
                "FAIL %s is not deterministic: two runs of the same file disagree\n"
                "  run 1: %r\n  run 2: %r"
                % (block_id, _normalise(a or ""), _normalise(b or "")))
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("problem_set_path")
    parser.add_argument(
        "--python", default=os.environ.get("LAB_PYTHON", sys.executable),
        help="interpreter to execute the blocks in; defaults to $LAB_PYTHON")
    parser.add_argument(
        "--repeat", type=int, default=2,
        help="runs of the whole file; 2 (the default) checks determinism")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument(
        "--allow-unpinned", action="store_true",
        help="accept a set with no env block instead of failing")
    args = parser.parse_args(argv)

    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    with open(args.problem_set_path, encoding="utf-8") as handle:
        text = handle.read()

    try:
        pins = parse_env_pins(text)
        blocks = parse_blocks(text)
    except LabSetError as error:
        print("FAIL %s" % error)
        return 1

    if not blocks:
        print("UNCHECKED no id-tagged python blocks - nothing to verify")
        return 0
    if not pins and not args.allow_unpinned:
        print("FAIL %d executable blocks and no env block: the environment is "
              "unrecorded, so the outputs cannot be attributed to one"
              % len(blocks))
        return 1

    try:
        reports = [run_blocks(args.python, blocks, pins, args.timeout)
                   for _ in range(args.repeat)]
    except LabSetError as error:
        print("FAIL %s" % error)
        return 1
    except subprocess.TimeoutExpired:
        print("FAIL execution exceeded %ds" % args.timeout)
        return 1

    failures = check_versions(pins, reports[0])
    failures += compare_outputs(blocks, reports[0])
    for later in reports[1:]:
        failures += compare_runs(blocks, reports[0], later)

    if failures:
        for line in failures:
            print(line)
        return 1

    print("PASS %d blocks re-executed, %d pins verified, %d runs agree"
          % (len(blocks), len(pins), args.repeat))
    return 0


if __name__ == "__main__":
    sys.exit(main())
