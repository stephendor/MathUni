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
3. **Determinism.** The whole file runs twice by default, **each repeat under a
   different** ``PYTHONHASHSEED``. Unseeded randomness produces a set whose
   outputs are true once and false thereafter, which is exactly the failure a
   single run cannot see; holding the hash seed fixed across repeats hid the
   hash-ordered half of it, since a student's ordinary launch randomises that
   seed and the recorded output never mentions one. Varying it is a probe rather
   than a proof — two seeds can order a small collection alike — and
   ``--repeat`` above 2 widens it. ``--repeat 1`` opts out. Every repeat is also
   checked for blocks that raised or never ran, because a block that succeeds
   once and fails afterwards produces the same stdout both times.
4. **That the pinned packages load.** ``importlib.metadata`` reads a
   ``.dist-info`` directory and imports nothing, so a distribution missing its
   compiled extensions reports its pinned version and fails several blocks
   later. The ``env`` block must therefore import every module the set uses, at
   the submodule it uses, **and every name the set takes out of one** — a class
   that has been renamed is as fatal as a subpackage that will not load, and a
   set's header claims those names are "verified by execution". A name counts
   however the set reaches it: ``from persim import bottleneck`` and
   ``persim.bottleneck(...)`` are the same claim about the same surface.
   Attribute chains stop at the first name, so ``np.linalg.norm`` asks for
   ``numpy.linalg`` and not for every function in it. Names are resolved **in
   execution order**, one running map advanced block by block: the blocks share
   an interpreter, so a name means whatever the most recent binding before that
   point made it mean, and gathering every binding into one map first let a
   later ``import b as api`` re-attribute an earlier ``api.method()`` to ``b``,
   leaving the surface actually reached undemanded. This gate checks all of it
   statically, and stops before running anything if any of it fails: once the
   environment declaration is wrong there is nothing to learn from the outputs.
   A block that will not parse is a failure and not a block to skip — skipping it
   dropped its imports from this analysis, so a set whose only user of a module
   was malformed used to pass.

Only blocks carrying ``id=`` participate, so a set can still show code the
reader is meant to complete without the gate trying to run it.

``--parse-only`` performs 1's structural half and 4 without executing anything,
which is the part that needs no lab interpreter and so the part CI can run. It
does **not** catch a recorded output that has drifted from the code beside it;
only re-execution does, and that needs the pinned interpreter.

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


_QUOTED_THEOREM = re.compile(r"^>\s+\*\*[^*\n]*Theorem[^*\n]*\*\*", re.MULTILINE)
_PROBLEM = re.compile(r"^##\s+Problem\b", re.MULTILINE)
_THEOREM_PROBE = re.compile(r"^\s*#\s*THEOREM-PROBE:\s*\S", re.MULTILINE)


def check_theorem_probes(markdown_text):
    """Require an executable boundary probe near every quoted theorem.

    The probe marker must occur after the blockquote and before the next
    problem.  This is intentionally coverage-style: execution/output checking
    remains owned by the ordinary block gate.
    """
    failures = []
    for match in _QUOTED_THEOREM.finditer(markdown_text):
        following = _PROBLEM.search(markdown_text, match.end())
        end = following.start() if following else len(markdown_text)
        executable_probe = False
        for fence in FENCE.finditer(markdown_text, match.end(), end):
            info = fence.group("info").strip()
            lang = info.split(" ")[0] if info else ""
            if lang in PYTHON_LANGS and _ID.search(info) \
                    and _THEOREM_PROBE.search(fence.group("body")):
                executable_probe = True
                break
        if not executable_probe:
            line = markdown_text[:match.start()].count("\n") + 1
            failures.append("FAIL quoted theorem at line %d has no executable "
                            "# THEOREM-PROBE before the next problem" % line)
    return failures


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


def _from_names(tree):
    """Return the ``(module, name)`` pairs an AST imports by name.

    ``from sklearn import preprocessing`` and ``from numpy import array`` are
    the same syntax, and nothing in the source says which name is a submodule
    and which is an attribute. Only the first requires ``sklearn.preprocessing``
    to load, so demanding a dotted import for every such name would be wrong,
    and demanding only the parent package lets ``import sklearn`` certify a set
    that goes on to load a subpackage that is broken.

    The way out is to stop guessing: a pair is satisfied either by a dotted
    import of ``module.name`` or by the ``env`` block containing the same
    ``from module import name``, which loads exactly what the later block
    loads whichever kind of name it is.
    """
    pairs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            for alias in node.names:
                if alias.name != "*":
                    pairs.add((node.module, alias.name))
    return pairs


def _scan_names(node, aliases, pairs):
    """Walk one node in source order, advancing ``aliases`` and filling ``pairs``.

    A name means whatever the most recent binding *before this point* made it
    mean, so bindings and uses have to be visited in order rather than gathered
    into one map first. ``ast.walk`` is breadth-first and answers a different
    question; this is depth-first in field order, which is source order for
    statements, with ``Assign`` taken value-first because that is the order the
    interpreter evaluates it in.
    """
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.asname:
                aliases[alias.asname] = alias.name
            else:
                root = alias.name.split(".")[0]
                aliases[root] = root
        return
    if isinstance(node, ast.ImportFrom):
        # ``from numpy import array`` binds a name *from* a module, not the
        # module, so it cancels any module meaning the name used to carry.
        for alias in node.names:
            aliases.pop(alias.asname or alias.name, None)
        return
    if isinstance(node, ast.Assign):
        _scan_names(node.value, aliases, pairs)
        for target in node.targets:
            _scan_names(target, aliases, pairs)
        return
    if isinstance(node, ast.Name):
        if isinstance(node.ctx, ast.Store):
            aliases.pop(node.id, None)
        return
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        module = aliases.get(node.value.id)
        if module:
            pairs.add((module, node.attr))
        return
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda,
                         ast.ClassDef)):
        # Python binds an import inside a function or class body to that body's
        # namespace, so ``import scipy as np`` in a helper must not change what
        # ``np`` means at the top level afterwards. The body is scanned with a
        # copy: uses inside it still resolve against the enclosing bindings, and
        # bindings made inside it are discarded on the way out. Decorators and
        # argument defaults are evaluated in the enclosing scope and are scanned
        # there. The def's own name is a binding in the enclosing scope, and it
        # is not a module, so it cancels any alias of that name.
        inner = dict(aliases)
        for field in ("decorator_list", "bases", "keywords"):
            for child in getattr(node, field, []) or []:
                _scan_names(child, aliases, pairs)
        arguments = getattr(node, "args", None)
        if isinstance(arguments, ast.arguments):
            for default in list(arguments.defaults) + [
                    d for d in arguments.kw_defaults if d is not None]:
                _scan_names(default, aliases, pairs)
        body = node.body if isinstance(node.body, list) else [node.body]
        for child in body:
            _scan_names(child, inner, pairs)
        name = getattr(node, "name", None)
        if name:
            aliases.pop(name, None)
        return
    for child in ast.iter_child_nodes(node):
        _scan_names(child, aliases, pairs)


def _attribute_names(tree, aliases):
    """Return the ``(module, attribute)`` pairs an AST reaches through a module.

    ``persim.bottleneck(...)`` names an API surface exactly as
    ``from persim import bottleneck`` does, and it is the form a set reaches for
    when the module is imported whole. Only the first attribute is taken:
    ``np.linalg.norm`` yields ``(numpy, linalg)``, because establishing that the
    submodule loads is the part that can fail as a unit, and walking deeper would
    demand a declaration for every function in the library.

    ``aliases`` is the running map of local names bound to modules and **this
    function advances it**, so it must be called once per block in the order the
    blocks execute: they share one interpreter namespace, so a binding carries
    into the next block. Resolving every use against a single map built from all
    the blocks first was wrong in both directions. A later ``import b as api``
    overwrote an earlier ``import a as api``, so an earlier ``api.method()`` was
    recorded as ``b.method`` and the surface actually reached was never demanded;
    and an alias bound only in a *later* block resolved an attribute in an
    earlier one, demanding a declaration for a name that was not a module yet.

    Function and class bodies are scanned with a **copy** of the map, because
    Python binds an import inside one to that body's namespace: a helper doing
    ``import scipy as np`` must not change what ``np`` means at the top level
    afterwards, which would attribute a later ``np.linalg.norm`` to the wrong
    package in whichever direction the env block happened to declare.

    Bodies are read in definition order rather than call order, which is the
    remaining approximation: a function defined before a rebinding and called
    after it resolves against the earlier binding. Deciding otherwise needs a
    call graph, and the conservative reading is the one that reports the surface
    the source names where it names it.
    """
    pairs = set()
    for child in ast.iter_child_nodes(tree):
        _scan_names(child, aliases, pairs)
    return pairs


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


def _feature_version(pins):
    """Return the ``(major, minor)`` grammar the set's ``python`` pin declares.

    The gate's structural half runs under whatever interpreter CI provides, and
    CI is not the pinned one: ``--parse-only`` runs on 3.13 while the sets pin
    3.11.11. Parsing with the runner's grammar accepts syntax the pinned
    interpreter rejects, so a block using ``type Alias = int`` would clear CI and
    then raise for the student. ``feature_version`` is best-effort rather than a
    full 3.11 parser — it rejects the grammar CPython gates on a version check
    and cannot know about library or runtime changes — but it turns the common
    case from a silent pass into a reported failure.
    """
    pinned = pins.get("python") if pins else None
    if not pinned:
        return None
    parts = pinned.split(".")
    try:
        version = (int(parts[0]), int(parts[1]))
    except (IndexError, ValueError):
        return None
    # ``ast.parse`` raises ValueError for a grammar this interpreter cannot
    # emulate -- anything before 3.4, or newer than itself. A pin the runner
    # cannot honour is not a reason to hand back a traceback instead of a
    # verdict, so the range is checked here and main() says out loud that the
    # check was not applied rather than passing quietly.
    if version[0] != 3 or not (4 <= version[1] <= sys.version_info.minor):
        return None
    return version


def check_env_imports(blocks, feature_version=None):
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

    # A block that will not parse is a failure, not a block to skip. Skipping it
    # dropped its imports from this analysis, so a set whose only user of a
    # module had a syntax error passed --parse-only -- and --parse-only is the
    # mode CI runs, so the set would have failed first for a reader.
    trees = {}
    failures = []
    for block_id, code, _ in blocks:
        try:
            trees[block_id] = (ast.parse(code, feature_version=feature_version)
                               if feature_version else ast.parse(code))
        except SyntaxError as error:
            failures.append(
                "FAIL block '%s' is not valid Python: %s (line %s)"
                % (block_id, error.msg, error.lineno))
    if failures:
        return failures

    # One running alias map, advanced block by block in execution order. The
    # env block is scanned in its turn rather than in a second pass, because
    # rewinding to it afterwards would resolve its names against bindings made
    # by blocks that had not run yet.
    aliases = {}
    used = {}
    used_names = {}
    declared = set()
    declared_names = set()
    for block_id, code, _ in blocks:
        tree = trees[block_id]
        pairs = _from_names(tree) | _attribute_names(tree, aliases)
        if block_id == "env":
            declared |= _module_targets(tree)
            declared_names |= pairs
            continue
        for module in _module_targets(tree):
            used.setdefault(module, block_id)
        for pair in pairs:
            used_names.setdefault(pair, block_id)

    external = {module: bid for module, bid in used.items()
                if module.split(".")[0] not in sys.stdlib_module_names}
    external_names = {pair: bid for pair, bid in used_names.items()
                      if pair[0].split(".")[0] not in sys.stdlib_module_names}

    # Both, not just the first. The blocks share a namespace, so a later block
    # can reach ``np.definitely_missing()`` on an alias the ``env`` block bound
    # and never import anything itself -- leaving ``used`` empty while
    # ``used_names`` holds exactly the renamed-API case this analysis exists to
    # catch. Returning on ``external`` alone certified it.
    if not external and not external_names:
        return []
    if not env_code:
        return ["FAIL no env block, so the %d module(s) and %d name(s) the set "
                "uses are never loaded before the outputs are attributed to them"
                % (len(external), len(external_names))]

    # Loading ``gtda.homology`` loads ``gtda`` on the way, so a declared dotted
    # path declares its ancestors. This is the safe direction: the parent does
    # not vouch for the child, which is the broken-subpackage case the check
    # exists for, but the child does vouch for the parent.
    for module in list(declared):
        parts = module.split(".")
        for depth in range(1, len(parts)):
            declared.add(".".join(parts[:depth]))

    for module in sorted(external):
        if module not in declared:
            failures.append(
                "FAIL env does not import %s, which block '%s' uses: a pin "
                "verified from metadata alone does not establish that the "
                "module loads" % (module, external[module]))

    for module, name in sorted(used_names):
        if module.split(".")[0] in sys.stdlib_module_names:
            continue
        if "%s.%s" % (module, name) in declared or (module, name) in declared_names:
            continue
        failures.append(
            "FAIL env does not import %s from %s, which block '%s' uses: "
            "importing %s alone leaves it unknown whether that name is a "
            "submodule that fails to load or an attribute that has been "
            "renamed. Add 'from %s import %s' to the env block"
            % (name, module, used_names[(module, name)], module, module, name))
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


def run_blocks(python_executable, blocks, pins, timeout=900, hash_seed="0"):
    """Execute the blocks in one interpreter and return the driver's report.

    ``hash_seed`` is deliberately varied between repeats. Pinning every run to
    ``PYTHONHASHSEED=0`` made the two runs agree about output that depends on
    iteration over a set or any other hash-ordered structure, so the gate
    certified as deterministic a recording that an ordinary launch -- which is
    what a student gets, hash randomisation being on by default -- could contradict.
    Agreement was being manufactured by an environment setting the recorded
    output never mentions.

    Two fixed seeds rather than randomisation, so a failure is reproducible from
    the command line. That is a probe and not a proof: two seeds can happen to
    order a small collection the same way, and a set can still be hash-order
    dependent without this catching it. ``--repeat`` above 2 widens the probe.
    """
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
                           PYTHONHASHSEED=str(hash_seed))
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

    theorem_failures = check_theorem_probes(text)
    if theorem_failures:
        for line in theorem_failures:
            print(line)
        return 1
    if not blocks:
        print("UNCHECKED no id-tagged python blocks - nothing to verify")
        return 0
    if not pins and not args.allow_unpinned:
        print("FAIL %d executable blocks and no env block: the environment is "
              "unrecorded, so the outputs cannot be attributed to one"
              % len(blocks))
        return 1

    grammar = _feature_version(pins)
    if pins.get("python") and grammar is None:
        # Qualified, not silent: the structural half still runs, but it ran
        # against the runner's grammar and the reader is told so.
        print("NOTE python is pinned at %s, which this interpreter (%s) cannot "
              "parse for, so blocks were parsed with the runner's grammar"
              % (pins["python"], ".".join(str(p) for p in sys.version_info[:3])))

    structural = check_env_imports(blocks, grammar)
    if structural:
        # The environment declaration is what licenses attributing the recorded
        # outputs to the recorded pins. If it is wrong there is nothing to learn
        # from running the blocks, so the gate stops here rather than spending
        # minutes producing a diff whose premise has already failed.
        for line in structural:
            print(line)
        return 1

    if args.parse_only:
        print("PASS %d blocks paired with recorded output, %d pins declared, "
              "env imports every module used (not executed: --parse-only)"
              % (len(blocks), len(pins)))
        return 0

    try:
        reports = [run_blocks(args.python, blocks, pins, args.timeout,
                              hash_seed=run)
                   for run in range(args.repeat)]
    except LabSetError as error:
        print("FAIL %s" % error)
        return 1
    except subprocess.TimeoutExpired:
        print("FAIL execution exceeded %ds" % args.timeout)
        return 1

    failures = check_versions(pins, reports[0])
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
