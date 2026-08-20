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
   exactly the failure a single run cannot see. ``--repeat 1`` opts out. Every
   repeat is also checked for blocks that raised or never ran, because a block
   that succeeds once and fails afterwards produces the same stdout both times.
4. **That the pinned packages load.** ``importlib.metadata`` reads a
   ``.dist-info`` directory and imports nothing, so a distribution missing its
   compiled extensions reports its pinned version and fails several blocks
   later. The ``env`` block must therefore import every module the set uses, at
   the submodule it uses; this gate checks that statically before running.

Only blocks carrying ``id=`` participate, so a set can still show code the
reader is meant to complete without the gate trying to run it.

``--parse-only`` performs 1's structural half and 4 without executing anything,
which is the part that needs no lab interpreter and so the part CI can run.

This gate **executes the repository's own content** in the interpreter it is
pointed at, with the invoking environment inherited. That is the same trust
level as the test suite, and it is not a sandbox: point it only at a checkout
you would run ``pytest`` on.
"""
import argparse
import ast
import json
import os
import re
import shutil
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
            name, pinned = pin.group(1), pin.group(2)
            if name in pins and pins[name] != pinned:
                raise LabSetError(
                    "env block pins %s at both %s and %s: the recorded "
                    "environment is contradictory, so no interpreter can "
                    "satisfy it" % (name, pins[name], pinned))
            pins[name] = pinned
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


_DYNAMIC_IMPORT = ("__import__", "import_module")


def _is_dynamic_import(node):
    if not isinstance(node, ast.Call):
        return False
    function = node.func
    name = getattr(function, "id", None) or getattr(function, "attr", None)
    return name in _DYNAMIC_IMPORT


def _strings(node):
    return {child.value for child in ast.walk(node)
            if isinstance(child, ast.Constant) and isinstance(child.value, str)}


def _module_targets(tree):
    """Return the dotted module paths an AST loads.

    ``import gtda.mapper`` is an ``Import`` node, but a block that probes a list
    of names loads them through ``__import__(name)``, where the names are string
    constants. Only constants that reach such a call count: an ``env`` block
    also loops over *distribution* names to print their versions, and a
    distribution name that happens to match a module name would otherwise
    satisfy this check without anything being imported.
    """
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                modules.add(node.module)
        elif _is_dynamic_import(node):
            for argument in node.args:
                modules |= _strings(argument)
        elif isinstance(node, ast.For):
            if any(_is_dynamic_import(inner)
                   for statement in node.body
                   for inner in ast.walk(statement)):
                modules |= _strings(node.iter)
    return modules


def check_env_imports(blocks):
    """Return failure lines for modules the ``env`` block never imports.

    The environment pins are metadata: ``importlib.metadata.version`` reads a
    ``.dist-info`` directory and never loads the package, so a distribution
    whose compiled extensions are missing reports its pinned version happily
    and fails only later, in a block whose diff looks like a content error.
    Requiring the ``env`` block to import every module the set actually uses —
    at the submodule it uses, since a broken subpackage is the failure that
    occurs — turns that into an ``env`` diff on the first block instead.
    """
    env_code = [code for bid, code, _ in blocks if bid == "env"]
    used = {}
    for block_id, code, _ in blocks:
        if block_id == "env":
            continue
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        for module in _module_targets(tree):
            used.setdefault(module, block_id)

    external = {module: bid for module, bid in used.items()
                if module.split(".")[0] not in sys.stdlib_module_names}
    if not external:
        return []
    if not env_code:
        return ["FAIL no env block, so the %d module(s) the set imports are "
                "never loaded before the outputs are attributed to them"
                % len(external)]

    declared = set()
    for code in env_code:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        declared |= _module_targets(tree)

    failures = []
    for module in sorted(external):
        if module not in declared:
            failures.append(
                "FAIL env does not import %s, which block '%s' uses: a pin "
                "verified from metadata alone does not establish that the "
                "module loads" % (module, external[module]))
    return failures


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
    try:
        spec_path = os.path.join(workdir, "spec.json")
        driver_path = os.path.join(workdir, "driver.py")
        with open(spec_path, "w", encoding="utf-8") as handle:
            json.dump(spec, handle)
        with open(driver_path, "w", encoding="utf-8") as handle:
            handle.write(DRIVER)
        environment = dict(os.environ, PYTHONIOENCODING="utf-8",
                           PYTHONHASHSEED="0")
        completed = subprocess.run(
            [python_executable, driver_path, spec_path],
            capture_output=True, text=True, encoding="utf-8",
            timeout=timeout, env=environment,
        )
    finally:
        # A timeout raises through here too, so the driver's scratch directory
        # is removed on every exit rather than accumulating one per gate run.
        shutil.rmtree(workdir, ignore_errors=True)
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


def check_completed(blocks, report, label):
    """Return failure lines for blocks that did not run, or raised, in a run.

    Applied to every repeat, not only the first. A block that succeeds once and
    raises afterwards — the shape of any block that writes a file, or consumes
    a generator, or mutates state a later run inherits — produces the same
    stdout both times, so comparing stdout alone certifies it as deterministic.
    """
    failures = []
    for block_id, _, _ in blocks:
        observed = report["blocks"].get(block_id)
        if observed is None:
            failures.append("FAIL %s did not run in %s (an earlier block raised)"
                            % (block_id, label))
        elif observed["error"]:
            failures.append("FAIL %s raised in %s\n%s"
                            % (block_id, label, observed["error"].rstrip()))
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
    parser.add_argument(
        "--parse-only", action="store_true",
        help="check block structure, pins and env module coverage without "
             "executing anything; the part of this gate that needs no lab "
             "interpreter, and so the part CI can run")
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

    structural = check_env_imports(blocks)

    if args.parse_only:
        if structural:
            for line in structural:
                print(line)
            return 1
        print("PASS %d blocks paired with recorded output, %d pins declared, "
              "env imports every module used (not executed: --parse-only)"
              % (len(blocks), len(pins)))
        return 0

    try:
        reports = [run_blocks(args.python, blocks, pins, args.timeout)
                   for _ in range(args.repeat)]
    except LabSetError as error:
        print("FAIL %s" % error)
        return 1
    except subprocess.TimeoutExpired:
        print("FAIL execution exceeded %ds" % args.timeout)
        return 1

    failures = structural + check_versions(pins, reports[0])
    failures += compare_outputs(blocks, reports[0])
    for index, later in enumerate(reports[1:], start=2):
        label = "run %d" % index
        failures += check_completed(blocks, later, label)
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
