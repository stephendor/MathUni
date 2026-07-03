# Nexus College Phase 0 — Scaffold & Semester 1 Curriculum Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the MathUni repo with mission documents, a validated Semester 1 syllabus DAG, module specs, and seeded progress state — everything Phase 1's `/today` and `/lecture` skills will read.

**Architecture:** Content-first repo. Curriculum is data (`curriculum/syllabus.yaml`, a unit DAG), guarded by a small Python validator with pytest tests. State is derived from curriculum by a seeding script, never hand-edited. All prose documents follow Matt Pocock's teach-skill formats.

**Tech Stack:** Python 3.11+ (PyYAML, pytest), Markdown, YAML. No build step.

## Global Constraints

- Repo root: `C:\Users\steph\MathUni`, branch `main`. Verify cwd before every write/commit (user rule).
- Multi-line commit messages via `git commit -F <tempfile>` — never here-strings (user rule).
- Spec of record: `docs/specs/2026-07-03-nexus-college-design.md`. Nothing in this plan may contradict it.
- State-first rule: state files are JSON, written atomically (write temp, rename).
- No Obsidian anywhere. Viewing layer is browser/VSCode.
- Every unit in the syllabus MUST have: unique `id`, `module`, `title`, `prereqs` (list, may be empty), `resources` (list), `hook` (one engaging sentence — ADHD hard requirement), `mission_link` (one sentence).
- Core texts folder: `D:\OneDrive - The Open University\NexusCollege Core Texts\` (`pdf\` + `md\`; prefer `md\` when present).

---

### Task 1: Repo scaffold

**Files:**
- Create: `README.md`, `.gitignore`, `requirements-dev.txt`

**Interfaces:**
- Produces: directory conventions all later tasks rely on (see spec §4). Directories are created implicitly when files land (git tracks no empty dirs).

- [ ] **Step 1: Write `.gitignore`**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
state/sessions/*.tmp
*.tmp
```

- [ ] **Step 2: Write `requirements-dev.txt`**

```
pyyaml>=6.0
pytest>=8.0
```

- [ ] **Step 3: Write `README.md`**

```markdown
# Nexus College

A two-year, AT/TDA-specialised university mathematics curriculum, run by
Claude Code. Spec: [docs/specs/2026-07-03-nexus-college-design.md](docs/specs/2026-07-03-nexus-college-design.md).

## Layout
- `MISSION.md` / `NOTES.md` — learner mission and preferences (Pocock format)
- `curriculum/` — `syllabus.yaml` (unit DAG) + `modules/*.md` (module specs)
- `lessons/` — generated interactive HTML lessons
- `problems/` — problem sets, solutions, graded submissions
- `srs/` — spaced-repetition deck and local scheduler
- `state/` — progress, mastery, streaks, session logs (machine-written)
- `scripts/` — validator and state tooling
- `dashboard/` — generated HTML dashboard

## Rules
- `state/` is machine-written; never hand-edit.
- `curriculum/syllabus.yaml` must pass `python scripts/validate_syllabus.py` before commit.
- Sessions resume from files alone: see `state/SESSION-HANDOFF.md`.
```

- [ ] **Step 4: Commit**

```bash
cd /c/Users/steph/MathUni && git add -A && printf 'chore: repo scaffold (README, gitignore, dev requirements)\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n' > /tmp/cm.txt && git commit -F /tmp/cm.txt
```

---

### Task 2: MISSION.md and NOTES.md

**Files:**
- Create: `MISSION.md`, `NOTES.md`

**Interfaces:**
- Produces: mission text every lesson generator must echo; NOTES.md is the file `/today` and `/lecture` consult for learner preferences.

- [ ] **Step 1: Write `MISSION.md`**

```markdown
# Mission

## Why
Be able to read, verify, and produce research-level work in topological data
analysis — specifically to understand and extend the persistent-homology work
already underway in the TDL project (`C:\Users\steph\TDL`). The mathematics is
not abstract preparation: persistence diagrams from my own trajectory data are
already on disk waiting to be understood at full depth.

## Success looks like
- I can state and prove the core theorems of a first algebraic topology
  course (fundamental group, homology) without notes.
- I can read a current TDA paper (e.g. on multiparameter persistence) and
  verify its main argument.
- I can explain the stability theorem for persistence diagrams and why it
  licenses the TDL pipeline's conclusions.
- Capstone: a written, defended contribution to the TDL project.

## Constraints
- 4 study days/week, 2–3 lecture-equivalents/day; ~2-year horizon.
- ADHD: engagement design is load-bearing (hooks first, timeboxes, visible
  progress, one gentle nudge on missed days — never guilt).
- Sessions must survive usage-limit interruptions (state-first).
- Token-conscious: expensive generation batched weekly.

## Out of scope
Complex analysis, measure theory, number theory, ODEs/PDEs, statistics —
unless research demands them later (just-in-time modules only).
```

- [ ] **Step 2: Write `NOTES.md`**

```markdown
# Learner Notes

Preferences and teaching adjustments. Updated by any session that learns
something about how Stephen learns. Newest entries at top, dated.

## Standing preferences (2026-07-03)
- Loves: Aluffi's expository style, Stillwell's geometric-historical
  approach, visual-first treatments (Macauley/Carter for groups).
- Lessons open with the hook, never with "Definition 1.1".
- Proof feedback: rigorous and direct; hand-waves named as hand-waves.
- Timebox segments to 25–30 min with explicit breaks.
- Prefers markdown-converted texts (Core Texts `md\` folder) for quoting;
  PDFs are fallback and page-citation source.
```

- [ ] **Step 3: Commit**

```bash
cd /c/Users/steph/MathUni && git add MISSION.md NOTES.md && printf 'feat: add mission and learner notes (Pocock format)\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n' > /tmp/cm.txt && git commit -F /tmp/cm.txt
```

---

### Task 3: Syllabus validator (TDD)

**Files:**
- Create: `scripts/validate_syllabus.py`
- Test: `tests/test_validate_syllabus.py`

**Interfaces:**
- Produces: `validate(doc: dict) -> list[str]` (empty list = valid) and CLI
  `python scripts/validate_syllabus.py [path]` exiting 1 on errors. Task 4
  and Task 6 depend on the CLI; Task 6 also imports `load_syllabus(path) -> dict`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_validate_syllabus.py
import copy
from scripts.validate_syllabus import validate

VALID = {
    "version": 1,
    "semesters": [{"id": "s1", "title": "Rigour and machinery"}],
    "modules": [{"id": "la", "title": "Linear Algebra", "semester": "s1"}],
    "units": [
        {"id": "la-01", "module": "la", "title": "Vector spaces",
         "prereqs": [], "resources": ["Axler 1A-1B"],
         "hook": "Why polynomials are secretly vectors.",
         "mission_link": "Homology groups are vector spaces first."},
        {"id": "la-02", "module": "la", "title": "Subspaces",
         "prereqs": ["la-01"], "resources": ["Axler 1C"],
         "hook": "Planes through the origin.",
         "mission_link": "Cycles and boundaries are subspaces."},
    ],
}

def test_valid_doc_passes():
    assert validate(copy.deepcopy(VALID)) == []

def test_duplicate_unit_id_fails():
    doc = copy.deepcopy(VALID)
    doc["units"].append(dict(doc["units"][0]))
    assert any("duplicate" in e for e in validate(doc))

def test_unknown_prereq_fails():
    doc = copy.deepcopy(VALID)
    doc["units"][1]["prereqs"] = ["zz-99"]
    assert any("zz-99" in e for e in validate(doc))

def test_cycle_fails():
    doc = copy.deepcopy(VALID)
    doc["units"][0]["prereqs"] = ["la-02"]
    assert any("cycle" in e.lower() for e in validate(doc))

def test_unknown_module_fails():
    doc = copy.deepcopy(VALID)
    doc["units"][0]["module"] = "nope"
    assert any("nope" in e for e in validate(doc))

def test_missing_hook_fails():
    doc = copy.deepcopy(VALID)
    del doc["units"][0]["hook"]
    assert any("hook" in e for e in validate(doc))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /c/Users/steph/MathUni && python -m pytest tests/ -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts'` (add empty `scripts/__init__.py` and `tests/__init__.py` if needed, then errors become "cannot import validate").

- [ ] **Step 3: Implement `scripts/validate_syllabus.py`**

```python
"""Validate curriculum/syllabus.yaml: ids unique, prereqs exist, DAG acyclic,
modules/semesters consistent, required unit fields present."""
import sys
from graphlib import TopologicalSorter, CycleError

import yaml

REQUIRED_UNIT_FIELDS = ("id", "module", "title", "prereqs", "resources",
                        "hook", "mission_link")


def load_syllabus(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(doc):
    errors = []
    sem_ids = {s["id"] for s in doc.get("semesters", [])}
    mod_ids = set()
    for m in doc.get("modules", []):
        if m["id"] in mod_ids:
            errors.append(f"duplicate module id: {m['id']}")
        mod_ids.add(m["id"])
        if m.get("semester") not in sem_ids:
            errors.append(f"module {m['id']}: unknown semester {m.get('semester')}")

    unit_ids = set()
    for u in doc.get("units", []):
        uid = u.get("id", "<missing>")
        for field in REQUIRED_UNIT_FIELDS:
            if field not in u or u[field] in (None, ""):
                errors.append(f"unit {uid}: missing field '{field}'")
        if uid in unit_ids:
            errors.append(f"duplicate unit id: {uid}")
        unit_ids.add(uid)
        if u.get("module") not in mod_ids:
            errors.append(f"unit {uid}: unknown module {u.get('module')}")

    for u in doc.get("units", []):
        for p in u.get("prereqs", []):
            if p not in unit_ids:
                errors.append(f"unit {u['id']}: unknown prereq {p}")

    try:
        ts = TopologicalSorter(
            {u["id"]: set(u.get("prereqs", [])) & unit_ids
             for u in doc.get("units", [])})
        ts.prepare()
    except CycleError as e:
        errors.append(f"prerequisite cycle detected: {e.args[1]}")
    return errors


def main(path="curriculum/syllabus.yaml"):
    errors = validate(load_syllabus(path))
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        sys.exit(1)
    print("syllabus OK")


if __name__ == "__main__":
    main(*sys.argv[1:2])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /c/Users/steph/MathUni && python -m pytest tests/ -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /c/Users/steph/MathUni && git add scripts/ tests/ && printf 'feat: syllabus DAG validator with tests\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n' > /tmp/cm.txt && git commit -F /tmp/cm.txt
```

---

### Task 4: Semester 1 syllabus DAG

**Files:**
- Create: `curriculum/syllabus.yaml`

**Interfaces:**
- Consumes: validator CLI from Task 3.
- Produces: the unit DAG consumed by Task 5 (module specs mirror it), Task 6
  (state seeding), and all Phase 1 skills. Unit ids are permanent API.

- [ ] **Step 1: Write `curriculum/syllabus.yaml`**

Full content (46 units). Semesters 2–4 appear as stubs (modules only, no
units yet — added in later phases). Pacing check: 46 units × ~2.5 sessions
each ≈ 115 lecture slots against ~160 available in a 20-week semester at
4 days × 2 slots — comfortable slack for remediation and life.

```yaml
version: 1

semesters:
  - id: s1
    title: Rigour and machinery
  - id: s2
    title: Topology and modules
  - id: s3
    title: Algebraic topology and TDA I
  - id: s4
    title: Depth and research on-ramp

modules:
  - id: la
    title: Linear Algebra
    semester: s1
    primary_text: "Axler, Linear Algebra Done Right (Core Texts)"
    support: ["Oxford M1 Linear Algebra I/II notes"]
  - id: an
    title: Real Analysis I
    semester: s1
    primary_text: "Abbott, Understanding Analysis (Core Texts)"
    support: ["Brannan", "Oxford M2 Analysis I", "Spivak Calculus"]
  - id: gt
    title: Group Theory
    semester: s1
    primary_text: "Aluffi, Algebra: Notes from the Underground (Core Texts)"
    support: ["Carter, Visual Group Theory", "Macauley VGT playlist",
              "Oxford M1 Groups and Group Actions notes"]
  - id: pw
    title: Proof Workshop
    semester: s1
    primary_text: "Cummings, Proofs (Core Texts)"
    support: ["Schumacher, Chapter Zero", "Earl, Towards Higher Mathematics"]
  # Semester 2+ module stubs (units added in later phases)
  - id: top
    title: Point-Set Topology
    semester: s2
    primary_text: "Munkres, Topology (Core Texts)"
    support: ["Dexter Chua notes", "Conway", "McCleary"]
  - id: rm
    title: Rings and Modules
    semester: s2
    primary_text: "Aluffi Underground -> Chapter 0"
    support: []
  - id: an2
    title: Analysis II
    semester: s2
    primary_text: "Oxford M2 Analysis II/III notes"
    support: []
  - id: lab
    title: Python for TDA Lab
    semester: s2
    primary_text: "Ripser/GUDHI/giotto-tda docs"
    support: []
  - id: at1
    title: Algebraic Topology I
    semester: s3
    primary_text: "Hatcher ch. 0-2"
    support: ["Dexter algebraic_topology notes", "Stillwell"]
  - id: cat
    title: Category Theory Essentials
    semester: s3
    primary_text: "Aluffi Chapter 0"
    support: ["Spivak, Applied Category Theory"]
  - id: tda1
    title: TDA I
    semester: s3
    primary_text: "Edelsbrunner-Harer"
    support: ["Oudot"]
  - id: at2
    title: Algebraic Topology II
    semester: s4
    primary_text: "Hatcher ch. 3"
    support: ["Dexter algebraic_topology_iii notes"]
  - id: tda2
    title: TDA II
    semester: s4
    primary_text: "Dey-Wang"
    support: ["Ghrist, Elementary Applied Topology"]
  - id: cap
    title: Capstone
    semester: s4
    primary_text: "TDL project"
    support: []

units:
  # ---- Proof Workshop (woven strand; light prereqs, unlocks early) ----
  - id: pw-01
    module: pw
    title: "Direct proof, contrapositive, contradiction"
    prereqs: []
    resources: ["Cummings ch. 4-6"]
    hook: "Three ways to corner a truth — and how mathematicians pick locks."
    mission_link: "Every TDA paper you'll verify is built from these moves."
  - id: pw-02
    module: pw
    title: "Induction, strong induction, well-ordering"
    prereqs: ["pw-01"]
    resources: ["Cummings ch. 7"]
    hook: "Dominoes, but the row is infinite and you get to shove the first one."
    mission_link: "Simplicial complex arguments induct on dimension constantly."
  - id: pw-03
    module: pw
    title: "Sets, functions, images and preimages, done rigorously"
    prereqs: ["pw-01"]
    resources: ["Cummings ch. 3, 8", "Schumacher"]
    hook: "f(A ∩ B) ≠ f(A) ∩ f(B): the inequality that catches everyone once."
    mission_link: "Continuity in topology is defined entirely via preimages."
  - id: pw-04
    module: pw
    title: "Epsilon-delta craft"
    prereqs: ["pw-03", "an-03"]
    resources: ["Cummings ch. 10", "Abbott 2.2"]
    hook: "The adversarial game: they pick epsilon, you must always win."
    mission_link: "Stability of persistence diagrams is an epsilon statement."
  - id: pw-05
    module: pw
    title: "Proof style: writing and critiquing"
    prereqs: ["pw-02", "pw-03"]
    resources: ["Cummings appendix", "Expository Writing folder"]
    hook: "Grade a deliberately flawed proof — find all five planted errors."
    mission_link: "The capstone is written mathematics; style is substance."

  # ---- Linear Algebra (Axler LADR) ----
  - id: la-01
    module: la
    title: "Vector spaces"
    prereqs: []
    resources: ["Axler 1A-1B"]
    hook: "Polynomials, sequences, and functions are all secretly the same thing."
    mission_link: "Homology groups over a field are vector spaces — this is their home."
  - id: la-02
    module: la
    title: "Subspaces, sums, direct sums"
    prereqs: ["la-01"]
    resources: ["Axler 1C"]
    hook: "When does a plane plus a line fill space? Direct sums as jigsaw pieces."
    mission_link: "Cycles and boundaries sit inside chains as subspaces."
  - id: la-03
    module: la
    title: "Span and linear independence"
    prereqs: ["la-02"]
    resources: ["Axler 2A"]
    hook: "Redundancy detection: which vectors are freeloaders?"
    mission_link: "Betti numbers count independent cycles — independence is the point."
  - id: la-04
    module: la
    title: "Bases and dimension"
    prereqs: ["la-03"]
    resources: ["Axler 2B-2C"]
    hook: "Why every basis of the same space has the same size — a genuinely deep fact."
    mission_link: "dim(ker ∂)/im ∂ computations are how Betti numbers are actually found."
  - id: la-05
    module: la
    title: "Linear maps"
    prereqs: ["la-04"]
    resources: ["Axler 3A"]
    hook: "The only functions algebra truly loves — and why derivatives qualify."
    mission_link: "Boundary operators ∂ are linear maps; homology is their study."
  - id: la-06
    module: la
    title: "Null space, range, fundamental theorem"
    prereqs: ["la-05"]
    resources: ["Axler 3B"]
    hook: "Conservation law for dimensions: nothing is created or destroyed."
    mission_link: "Homology literally = null space of one map modulo range of another."
  - id: la-07
    module: la
    title: "Matrices as linear maps"
    prereqs: ["la-06"]
    resources: ["Axler 3C"]
    hook: "Matrices are the shadows linear maps cast once you pick a basis."
    mission_link: "Persistence software reduces boundary matrices — this is that bridge."
  - id: la-08
    module: la
    title: "Invertibility and isomorphism"
    prereqs: ["la-07"]
    resources: ["Axler 3D"]
    hook: "When are two vector spaces 'the same'? The first taste of isomorphism."
    mission_link: "Functoriality sends isomorphisms to isomorphisms — the habit starts here."
  - id: la-09
    module: la
    title: "Products and quotient spaces"
    prereqs: ["la-08"]
    resources: ["Axler 3E"]
    hook: "Collapse a subspace to zero and see what survives."
    mission_link: "H = Z/B is a quotient. This unit is homology in miniature."
  - id: la-10
    module: la
    title: "Duality"
    prereqs: ["la-09"]
    resources: ["Axler 3F"]
    hook: "Every space has a mirror world of measurements."
    mission_link: "Cohomology is homology's dual; persistent cohomology runs faster."
  - id: la-11
    module: la
    title: "Eigenvalues, eigenvectors, invariant subspaces"
    prereqs: ["la-08"]
    resources: ["Axler 5A"]
    hook: "Directions a transformation cannot bend, only stretch."
    mission_link: "Spectral methods appear in Mapper and graph-based TDA."
  - id: la-12
    module: la
    title: "Minimal polynomial and diagonalisability"
    prereqs: ["la-11"]
    resources: ["Axler 5B-5C"]
    hook: "One polynomial that knows everything about your operator."
    mission_link: "Structure theorems here foreshadow persistence module decomposition."
  - id: la-13
    module: la
    title: "Inner product spaces"
    prereqs: ["la-04"]
    resources: ["Axler 6A"]
    hook: "Geometry enters: length and angle from pure algebra."
    mission_link: "Point clouds live in inner product spaces; distances build filtrations."
  - id: la-14
    module: la
    title: "Orthonormal bases and Gram-Schmidt"
    prereqs: ["la-13"]
    resources: ["Axler 6B"]
    hook: "Straightening a skewed coordinate system, one vector at a time."
    mission_link: "PCA preprocessing before TDA pipelines is this machinery."
  - id: la-15
    module: la
    title: "Spectral theorem (real case)"
    prereqs: ["la-12", "la-14"]
    resources: ["Axler 7A-7B"]
    hook: "The crown jewel: symmetric operators diagonalise perfectly. Why?"
    mission_link: "Graph Laplacians in Mapper are symmetric — their spectra behave."

  # ---- Real Analysis I (Abbott) ----
  - id: an-01
    module: an
    title: "Reals, completeness, sup and inf"
    prereqs: []
    resources: ["Abbott 1.1-1.4"]
    hook: "√2 punched a hole in the rationals; completeness is the patch."
    mission_link: "Persistence values are reals; inf/sup define birth and death."
  - id: an-02
    module: an
    title: "Cardinality and Cantor's diagonal"
    prereqs: ["an-01"]
    resources: ["Abbott 1.5-1.6", "Stillwell, Roads to Infinity"]
    hook: "Some infinities are bigger than others — provably."
    mission_link: "Countability arguments recur in measure-free TDA foundations."
  - id: an-03
    module: an
    title: "Sequences and limits"
    prereqs: ["an-01"]
    resources: ["Abbott 2.2-2.3"]
    hook: "Make 'gets close to' bulletproof against every adversary."
    mission_link: "Convergence of persistence diagrams needs limits done right."
  - id: an-04
    module: an
    title: "Monotone convergence and Bolzano-Weierstrass"
    prereqs: ["an-03"]
    resources: ["Abbott 2.4-2.5"]
    hook: "Bounded sequences can't escape: something must accumulate."
    mission_link: "Compactness arguments in stability proofs start here."
  - id: an-05
    module: an
    title: "Cauchy sequences and completeness"
    prereqs: ["an-04"]
    resources: ["Abbott 2.6"]
    hook: "Convergence without knowing the destination."
    mission_link: "The space of persistence diagrams is complete — same criterion."
  - id: an-06
    module: an
    title: "Infinite series"
    prereqs: ["an-05"]
    resources: ["Abbott 2.7"]
    hook: "Rearrange a series, change its sum: conditional convergence is wild."
    mission_link: "Rigour training; series estimates appear in vectorisation methods."
  - id: an-07
    module: an
    title: "Open and closed sets in R"
    prereqs: ["an-03"]
    resources: ["Abbott 3.2"]
    hook: "The vocabulary the whole of topology is built from."
    mission_link: "Direct on-ramp to Semester 2's point-set topology."
  - id: an-08
    module: an
    title: "Compactness and Heine-Borel"
    prereqs: ["an-07", "an-04"]
    resources: ["Abbott 3.3"]
    hook: "The property that makes infinite behave like finite."
    mission_link: "Compact metric spaces are where TDA's theory lives."
  - id: an-09
    module: an
    title: "Connectedness and the Cantor set"
    prereqs: ["an-08"]
    resources: ["Abbott 3.4, 3.1"]
    hook: "A set with zero length and uncountably many points."
    mission_link: "Connected components are H0 — the first Betti story."
  - id: an-10
    module: an
    title: "Functional limits and continuity"
    prereqs: ["an-07", "pw-04"]
    resources: ["Abbott 4.2-4.3"]
    hook: "Continuity recast: preimages of open sets are open. Remember pw-03?"
    mission_link: "This definition, verbatim, is the one topology keeps."
  - id: an-11
    module: an
    title: "Continuity on compact sets; IVT and EVT"
    prereqs: ["an-10", "an-08"]
    resources: ["Abbott 4.4-4.5"]
    hook: "Why continuous images of compact sets can't misbehave."
    mission_link: "Filtration functions on compact spaces attain their bounds."
  - id: an-12
    module: an
    title: "The derivative and the Mean Value Theorem"
    prereqs: ["an-10"]
    resources: ["Abbott 5.2-5.3"]
    hook: "MVT: the theorem that quietly proves half of calculus."
    mission_link: "Morse-theoretic TDA needs derivatives treated honestly."
  - id: an-13
    module: an
    title: "Uniform convergence"
    prereqs: ["an-06", "an-10"]
    resources: ["Abbott 6.2"]
    hook: "When limits of nice functions go wrong — and the fix."
    mission_link: "Uniform (sup-norm) bounds are the language of the stability theorem."
  - id: an-14
    module: an
    title: "Metric spaces bridge"
    prereqs: ["an-08", "an-10"]
    resources: ["Abbott 8.2 (or equiv.)", "Oxford M2 notes"]
    hook: "Everything you just proved for R, replayed on any set with a distance."
    mission_link: "Point clouds, diagram space, bottleneck distance: all metric spaces."

  # ---- Group Theory (Aluffi Underground + visual strand) ----
  - id: gt-01
    module: gt
    title: "Symmetry: groups before the definition"
    prereqs: []
    resources: ["Carter ch. 1-2", "Macauley VGT lecture 1"]
    hook: "A rectangle, a light switch, and a dance move walk into a bar — same group."
    mission_link: "Groups measure symmetry; homology groups measure holes. Same idiom."
  - id: gt-02
    module: gt
    title: "Groups: definition and first properties"
    prereqs: ["gt-01", "pw-01"]
    resources: ["Aluffi Underground ch. 1", "Oxford M1 Groups"]
    hook: "Four axioms that generate a universe."
    mission_link: "H1 is a group before it's anything else."
  - id: gt-03
    module: gt
    title: "Cayley diagrams and generators"
    prereqs: ["gt-02"]
    resources: ["Carter ch. 2-3", "Macauley VGT lectures 2-3"]
    hook: "Draw the group: every group is a graph you can walk."
    mission_link: "Visual habit-building for fundamental group loops later."
  - id: gt-04
    module: gt
    title: "Subgroups and cyclic groups"
    prereqs: ["gt-02"]
    resources: ["Aluffi Underground ch. 2"]
    hook: "The clock arithmetic hiding inside every group."
    mission_link: "Torsion in homology = cyclic subgroups making themselves felt."
  - id: gt-05
    module: gt
    title: "Homomorphisms and isomorphisms"
    prereqs: ["gt-04"]
    resources: ["Aluffi Underground ch. 4", "Macauley VGT"]
    hook: "Structure-preserving maps: the only arrows that matter."
    mission_link: "Induced maps on homology are homomorphisms — functoriality's atoms."
  - id: gt-06
    module: gt
    title: "Cosets and Lagrange's theorem"
    prereqs: ["gt-04"]
    resources: ["Aluffi Underground ch. 3"]
    hook: "Tile a group by copies of a subgroup; count the tiles."
    mission_link: "Cosets are the elements of every quotient you'll ever take."
  - id: gt-07
    module: gt
    title: "Normal subgroups and quotient groups"
    prereqs: ["gt-05", "gt-06"]
    resources: ["Aluffi Underground ch. 5"]
    hook: "When does collapsing a subgroup leave a group behind? (Compare la-09.)"
    mission_link: "Homology IS a quotient group. This is the single most mission-critical unit."
  - id: gt-08
    module: gt
    title: "The isomorphism theorems"
    prereqs: ["gt-07"]
    resources: ["Aluffi Underground ch. 5"]
    hook: "Three theorems, one picture: the lattice folds."
    mission_link: "Used silently in every homology computation you'll do."
  - id: gt-09
    module: gt
    title: "Group actions"
    prereqs: ["gt-05"]
    resources: ["Aluffi Underground ch. 6", "Oxford M1 Groups and Group Actions"]
    hook: "Groups don't just exist — they DO things to spaces."
    mission_link: "Covering space theory (Semester 3) is group actions on topology."
  - id: gt-10
    module: gt
    title: "Orbit-stabiliser and counting"
    prereqs: ["gt-09"]
    resources: ["Aluffi Underground ch. 6"]
    hook: "How many truly different necklaces? Burnside knows."
    mission_link: "Orbit decompositions mirror how covering spaces partition fibres."
  - id: gt-11
    module: gt
    title: "Symmetric and alternating groups"
    prereqs: ["gt-06"]
    resources: ["Aluffi Underground ch. 7"]
    hook: "Every group hides inside a shuffle."
    mission_link: "Simplicial orientation signs are alternating-group bookkeeping."
  - id: gt-12
    module: gt
    title: "Direct products and small-group classification"
    prereqs: ["gt-08", "gt-11"]
    resources: ["Aluffi Underground ch. 8", "Carter"]
    hook: "Build a periodic table of every group up to order 15."
    mission_link: "Homology outputs decompose as direct sums — reading them needs this."
```

- [ ] **Step 2: Validate**

Run: `cd /c/Users/steph/MathUni && python scripts/validate_syllabus.py`
Expected: `syllabus OK` (fix any reported errors before committing).

- [ ] **Step 3: Commit**

```bash
cd /c/Users/steph/MathUni && git add curriculum/syllabus.yaml && printf 'feat: Semester 1 syllabus DAG (46 units, validated)\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n' > /tmp/cm.txt && git commit -F /tmp/cm.txt
```

---

### Task 5: Semester 1 module specs

**Files:**
- Create: `curriculum/modules/la.md`, `curriculum/modules/an.md`,
  `curriculum/modules/gt.md`, `curriculum/modules/pw.md`

**Interfaces:**
- Consumes: unit ids from Task 4 (specs must reference only existing ids).
- Produces: per-module teaching contract read by Phase 1 lesson generation.

- [ ] **Step 1: Write the four module specs**

Each file follows this exact template (content shown for `la.md`; write the
other three analogously using the syllabus data — module goals, texts,
unit list, assessment, mission paragraph):

```markdown
# Module: Linear Algebra (la) — Semester 1

**Mission link:** Homology over a field is linear algebra. Boundary matrices,
quotient spaces (la-09), and duality (la-10) are direct rehearsals for
Semester 3.

**Primary text:** Axler, *Linear Algebra Done Right* — Core Texts folder
(prefer `md\`, cite PDF pages).
**Support:** Oxford M1 Linear Algebra I/II notes.

**Units (in DAG order):** la-01 … la-15 (see syllabus.yaml; two tracks after
la-08: operators la-11→la-12, geometry la-13→la-14, converging at la-15).

**Teaching notes:**
- Axler is determinant-free by design; keep it that way until the module end.
- Emphasise quotient spaces (la-09) beyond Axler's pace — it is the single
  best preparation for homology.
- Visualise: every lesson gets at least one animated/geometric element.

**Assessment:**
- Unit mastery quizzes (SRS + 3-5 questions).
- Module problem set: ~10 problems, mix of Axler exercises, Oxford sheet
  problems, one Tripos IA-adapted problem. Graded per spec §7, 80% gate.

**Common misconceptions to watch** (seed for learning-records):
- "Vectors are arrows/columns" (representation vs object).
- Span vs basis; dimension of sums (inclusion-exclusion errors).
- Believing injective ⇔ surjective without finite-dimension hypothesis.
```

For `an.md`: mission paragraph on metric spaces/stability; misconceptions:
sequence vs series, sup vs max, pointwise vs uniform convergence, "compact
= closed and bounded everywhere". For `gt.md`: mission paragraph on
quotients/functoriality; visual strand instructions (Macauley video per
unit where mapped); misconceptions: normality as commutativity, cosets as
subgroups, "isomorphic = equal". For `pw.md`: workshop format (one forensic
critique/week, rotating across live modules); misconceptions: proof by
example, circularity, quantifier order.

- [ ] **Step 2: Cross-check unit ids**

Run: `cd /c/Users/steph/MathUni && grep -oE '\b(la|an|gt|pw)-[0-9]{2}\b' curriculum/modules/*.md | sort -u` and confirm every id exists in syllabus.yaml.

- [ ] **Step 3: Commit**

```bash
cd /c/Users/steph/MathUni && git add curriculum/modules/ && printf 'feat: Semester 1 module specs (la, an, gt, pw)\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n' > /tmp/cm.txt && git commit -F /tmp/cm.txt
```

---

### Task 6: State seeding (TDD)

**Files:**
- Create: `scripts/init_state.py`
- Test: `tests/test_init_state.py`
- Generates: `state/progress.json`, `state/streaks.json`, `state/SESSION-HANDOFF.md`

**Interfaces:**
- Consumes: `load_syllabus(path)` from `scripts/validate_syllabus.py`.
- Produces: `seed_progress(doc: dict) -> dict` mapping unit id →
  `{"status": "unlocked"|"locked"}` (unlocked iff all prereqs empty), and CLI
  `python scripts/init_state.py` writing the three state files (refusing to
  overwrite an existing non-empty progress.json without `--force`).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_init_state.py
from scripts.init_state import seed_progress

DOC = {"units": [
    {"id": "a-01", "prereqs": []},
    {"id": "a-02", "prereqs": ["a-01"]},
]}

def test_no_prereqs_unlocked():
    assert seed_progress(DOC)["a-01"]["status"] == "unlocked"

def test_with_prereqs_locked():
    assert seed_progress(DOC)["a-02"]["status"] == "locked"

def test_all_units_present():
    assert set(seed_progress(DOC)) == {"a-01", "a-02"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /c/Users/steph/MathUni && python -m pytest tests/test_init_state.py -v`
Expected: FAIL — cannot import `seed_progress`.

- [ ] **Step 3: Implement `scripts/init_state.py`**

```python
"""Seed state/ from curriculum/syllabus.yaml. Refuses to clobber existing
progress without --force. Writes atomically (tmp file + rename)."""
import json
import os
import sys
from datetime import date

from scripts.validate_syllabus import load_syllabus


def seed_progress(doc):
    return {u["id"]: {"status": "unlocked" if not u.get("prereqs") else "locked"}
            for u in doc.get("units", [])}


def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main(argv):
    force = "--force" in argv
    if os.path.exists("state/progress.json") and \
            os.path.getsize("state/progress.json") > 2 and not force:
        print("state/progress.json exists; use --force to reseed")
        sys.exit(1)
    os.makedirs("state/sessions", exist_ok=True)
    doc = load_syllabus("curriculum/syllabus.yaml")
    write_atomic("state/progress.json",
                 json.dumps(seed_progress(doc), indent=2))
    write_atomic("state/streaks.json", json.dumps(
        {"current": 0, "best": 0, "study_days": [],
         "seeded": date.today().isoformat()}, indent=2))
    write_atomic("state/SESSION-HANDOFF.md",
                 "# Session Handoff\n\nFresh install; no sessions yet. "
                 "Start with /today (Phase 1).\n")
    print("state seeded")


if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 4: Run tests, then run the CLI**

Run: `cd /c/Users/steph/MathUni && python -m pytest tests/ -v`
Expected: 9 passed (6 from Task 3 + 3 new).
Run: `python scripts/init_state.py`
Expected: `state seeded`; `state/progress.json` has exactly 4 unlocked units
(pw-01, la-01, an-01, gt-01) and 42 locked.

- [ ] **Step 5: Commit**

```bash
cd /c/Users/steph/MathUni && git add scripts/init_state.py tests/test_init_state.py state/ && printf 'feat: state seeding from syllabus DAG\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n' > /tmp/cm.txt && git commit -F /tmp/cm.txt
```

---

## Self-Review (completed)

- **Spec coverage:** Spec §4 scaffold ✓ (Tasks 1–2), §3 Semester 1 curriculum ✓ (Task 4), module specs ✓ (Task 5), state-first seed ✓ (Task 6). `lessons/`, `srs/`, `problems/`, `dashboard/`, `.claude/skills/` are Phase 1–3 per spec §9 — intentionally absent here.
- **Placeholder scan:** Task 5 gives the full template with one complete instance and enumerated content requirements for the other three — acceptable since the writer of an.md/gt.md/pw.md has the syllabus and spec in hand; no TBDs remain.
- **Type consistency:** `validate(doc) -> list[str]`, `load_syllabus(path)`, `seed_progress(doc)` used consistently across Tasks 3/4/6. Unit id regex in Task 5 matches the `xx-NN` scheme of Task 4.
