# Nexus College — Design Spec

**Date:** 2026-07-03
**Status:** Approved in brainstorming session (this document is the written record)
**Learner:** Stephen (nexusstephen@gmail.com)
**Home:** `C:\Users\steph\MathUni` (git repo), driven from Claude Code / VSCode Insiders

---

## 1. Mission

> Be able to read, verify, and produce research-level work in topological data
> analysis — specifically to understand and extend the persistent-homology work
> already underway in the TDL project (`C:\Users\steph\TDL`).

Every module spec, lesson, and exercise must state (or clearly imply) how it
serves this mission. `MISSION.md` at the repo root is the canonical statement,
following Matt Pocock's teach-skill format (Why / Success looks like /
Constraints / Out of scope).

**Learner profile:** highly capable early first-year undergraduate level.
Solid calculus (level 3/4), a proofs course, smatterings of linear algebra,
analysis, topology, number theory, abstract algebra. ADHD — engagement design
is a hard requirement, not a nicety (see §6).

**Cadence:** 4 study days/week, 2–3 lecture-equivalents/day.
**Timeline:** research-ready in ~2 years (aggressive; the dependency graph
lets the schedule slip without the structure breaking).

## 2. Decisions taken (with the user, 2026-07-03)

| Decision | Choice |
|---|---|
| Endpoint/timeline | Research-ready in ~2 years |
| Home base | Dedicated git repo; **no Obsidian** (dropped to cut admin overhead) — visual tracking via repo dashboards + VSCode Insiders tooling |
| Lesson delivery | Interactive HTML lessons (Pocock-style, self-contained, reusable) |
| Assessment | Mastery gates (~80%) + rigorously graded proofs |
| Scheduling | Scheduled morning agent pre-builds each study day + notification; `/today` to start |
| Materials | Audit Stephen's existing collection first; canonical texts fill gaps |
| Resilience | State-first design: all progress written to disk continuously; any session cold-resumes from files |

## 3. Curriculum — four semesters, streamlined toward AT/TDA

Each semester ≈ 5 months. Deliberately cut: complex analysis, measure theory,
number theory, ODEs/PDEs, statistics — available later as just-in-time modules
if research demands them.

### Semester 1 — Rigour and machinery
- **Linear Algebra** (proof-based, Axler-style; Oxford M1 LA I/II notes as
  secondary) — the computational heart of homology.
- **Real Analysis I** (Abbott/Tao level; Brannan and Oxford M2 Analysis I as
  support; Cummings *Proofs* for technique) — rigour training, metric spaces early.
- **Group Theory** — primary: **Aluffi, *Algebra: Notes from the Underground***;
  visual strand: **Macauley's Visual Group Theory lectures**
  (https://www.youtube.com/playlist?list=PLwV-9DG53NDwl5uExD8m9FY16QX2fV4qh)
  with Carter's book; Oxford M1 Groups notes as support.
- Woven strand: **proof workshop** — one proof per week forensically critiqued.

### Semester 2 — Topology and modules
- **Point-Set Topology** (Munkres core; Dexter Chua notes; extra weight on
  quotient spaces — where AT intuition lives).
- **Rings and Modules** (Aluffi *Underground* → early *Chapter 0*; modules get
  full weight because homology *is* module theory).
- **Analysis II** (metric-space topology, uniform convergence, taste of
  functional analysis; Oxford M2 Analysis II/III).
- Lab strand: **Python for TDA** (Ripser, GUDHI, giotto-tda) — compute
  persistence diagrams before proving they exist, deliberately.

### Semester 3 — Algebraic Topology proper + TDA I
- **AT I**: fundamental group, covering spaces, simplicial & singular homology
  (Hatcher ch. 0–2; Dexter `algebraic_topology` notes; Stillwell's geometric
  style as intuition source).
- **Category theory essentials** (just-in-time: functors, natural
  transformations, enough for persistence modules; Aluffi *Chapter 0* +
  Spivak *Applied Category Theory*, both on disk).
- **TDA I**: filtrations, persistent homology, stability theorem, computation
  (Edelsbrunner–Harer, Oudot).

### Semester 4 — Depth + research on-ramp
- **AT II**: cohomology, cup products, Poincaré duality (Hatcher ch. 3;
  Dexter `algebraic_topology_iii`), light homotopy theory.
- **TDA II**: Mapper, multiparameter persistence, sheaf-theoretic viewpoint,
  vectorisation/ML integration (Dey–Wang).
- **Capstone**: a genuine contribution to the TDL project, written up and
  defended in a Feynman colloquium.

### Dependency graph, not a list
`curriculum/syllabus.yaml` encodes units as a DAG with prerequisite edges.
The system may offer any *unlocked* node when the learner is stuck or bored —
choice within structure (ADHD feature).

## 4. Architecture

```
C:\Users\steph\MathUni\
├── MISSION.md                     # Pocock mission anchor
├── NOTES.md                       # learner preferences, teaching adjustments
├── curriculum/
│   ├── syllabus.yaml              # unit DAG: id, title, prereqs, module, resources, mission-link
│   └── modules/<module>.md        # module specs
├── lessons/<module>/<unit>.html   # interactive HTML lessons (generated once, reused)
├── problems/
│   ├── sets/                      # problem sets (hint ladders embedded as spoilers)
│   ├── solutions/                 # hidden solutions (not surfaced during attempts)
│   └── submissions/               # Stephen's work + graded feedback
├── srs/
│   ├── deck.json                  # FSRS-style card store
│   └── scheduler.py               # local script — zero-token scheduling
├── state/
│   ├── progress.json              # unit status: locked/unlocked/in-progress/mastered
│   ├── mastery.json               # per-unit mastery scores, grading history
│   ├── streaks.json               # study-day streaks, session counts
│   ├── sessions/                  # append-only per-session logs
│   └── SESSION-HANDOFF.md         # rolling handoff for cold resume
├── learning-records/              # Pocock learning records (insights, misconceptions)
├── resources/
│   ├── RESOURCES.md               # curated source list per module
│   └── inventory.json             # map: PDF/video → syllabus units (built by /ingest)
├── dashboard/                     # generated HTML dashboard (kanban, heatmap, streaks)
└── .claude/skills/                # command set (§5)
```

**No Obsidian.** Visual tracking = generated HTML dashboard (openable in
browser/VSCode) + markdown kanban in-repo. VSCode Insiders extensions
(Markdown preview, live server) are the viewing layer.

**State-first rule:** every skill writes to `state/` *as it goes*, never only
at session end. Losing a 5-hour window mid-proof loses only chat transcript.

## 5. Command set and model assignments

| Command | Function | Model |
|---|---|---|
| `/today` | Assemble the day: SRS warm-up (10 min) → lecture 1 → lecture 2 → problem session; continuous state writes | Sonnet |
| `/lecture <unit>` | Open (or generate) the unit's HTML lesson; hook-first opening | Opus/Fable to generate; free to reopen |
| `/problems [unit]` | Problem session with hint ladder: nudge → strategy → partial → worked | Sonnet; Opus for hard proofs |
| `/grade` | Rubric-based proof grading, partial credit, written feedback, mastery.json update | **Opus/Fable only** |
| `/review` | SRS retrieval; scheduler.py picks cards, Claude engages only on failures | Haiku/Sonnet |
| `/status` | Dashboard refresh: kanban, streaks, mastery heatmap, unlocked units | Sonnet |
| `/resume` | Cold-restart from `state/` after a usage-limit reset | Sonnet |
| `/ingest` | Audit PDF/video collection against syllabus → `resources/inventory.json` | Haiku bulk, Sonnet mapping |
| `/colloquium` | Monthly Feynman session: Stephen lectures, Claude probes | Opus/Fable |

**Scheduled morning agent** (Sonnet, ~06:30 on study days): pre-builds day
plan, refreshes SRS queue, writes the daily plan file, sends a notification
whose text *is the hook* (e.g. "Today: why coffee cups are donuts — quotient
spaces. 14 cards waiting."). Implemented with Claude Code scheduled
routines/cron; push notification via the harness notification tool.

**Token budget strategy:**
- Expensive lesson generation (Opus/Fable) happens in a **weekly batch
  session**, not daily.
- Daily driving is Sonnet over pre-built local artifacts.
- SRS scheduling is a local Python script — zero tokens.
- Dexter notes' `_def`/`_eg`/`_thm`/`_thm_proof` pre-split PDFs are the
  primary card-generation corpus — near-zero extraction cost.
- Grading is the main daily Opus spend, by design.

## 6. Learning science requirements

- **Retrieval first:** every study day opens with recall, never re-reading.
- **FSRS spaced repetition** for definitions, theorem statements, and *proof
  sketches* ("outline the proof strategy of X").
- **Interleaving:** problem sets mix current and prior modules.
- **Faded worked examples:** full example → partially completed → solo.
- **ZPD gating:** mastery.json calibrates difficulty upward/downward.
- **Feynman colloquium** monthly.
- **ADHD design (hard requirements):**
  - Hook-first everything — the fun example opens every lesson and every
    morning notification; never "Definition 1.1" first.
  - 25–30 min timeboxed segments with explicit breaks.
  - Visible progress: streaks, filling mastery map, kanban movement.
  - Choice among unlocked DAG nodes when resistance hits.
  - Re-engagement rule: a missed day triggers exactly one gentle,
    interest-baited nudge. Never guilt, never escalation.

**Interactive HTML lessons:** self-contained (no build step), canvas/JS
animations (simplicial complexes assembling, filtrations sweeping, loops
deforming), embedded self-check questions with instant feedback, citations
into the actual PDFs on disk ("Hatcher p. 22"; "Dexter AT §2.1"),
reference-quality typography, printable.

## 7. Assessment and gating

- Per **unit**: SRS coverage + short mastery quiz.
- Per **module**: problem set graded by `/grade` against a rubric; proofs held
  to real standards (hand-waves marked as hand-waves); partial credit and
  written feedback; Tripos IA/IB/II papers mined for problems where they fit.
- **80% mastery gates progression.** Below threshold → targeted remediation
  set, not full redo.
- Semester boundaries: optional timed exam (config flag, default off).

## 8. Materials map (from collection skim, 2026-07-03)

| Need | On disk | Note |
|---|---|---|
| Proofs technique | Cummings *Proofs*, Schumacher *Chapter Zero*, Earl *Towards Higher Mathematics* | Currently Reading folder |
| Linear algebra | Oxford M1 LA I/II notes | **Acquire: Axler LADR** (check `Immediate Interest/` & subfolders first) |
| Analysis | Brannan, Spivak *Calculus*, Bressoud ×2, Oxford M2 Analysis I–III | Abbott/Tao optional additions |
| Group theory / algebra | **Aluffi *Underground***, **Aluffi *Chapter 0***, Pinter, Stillwell *Elements of Algebra*, Oxford M1 Groups | Macauley video playlist for visual strand |
| Point-set topology | Conway, McCleary, Dexter notes | Munkres possibly in subfolders — verify in /ingest |
| Algebraic topology | **Dexter `algebraic_topology` + `algebraic_topology_iii`** with `_def`/`_eg`/`_thm`/`_thm_proof` splits | **Acquire: Hatcher** (free PDF from his site) |
| Category theory | Spivak *Applied Category Theory*, Aluffi *Chapter 0* | |
| TDA | — | **Acquire: Edelsbrunner–Harer; Dey–Wang; Oudot** (Oudot free from author) |
| Problem sets | Tripos IA/IB/II + Vintage; `Advanced Problem Sets/`; Oxford sheets | |
| Videos | Macauley VGT playlist; MIT OCW as reliable fallback | |

Folders of record:
- `D:\OneDrive - The Open University\Undergraduate Mathematics` (+ subfolders)
- `D:\OneDrive - The Open University\Oxford Lecture Notes for essential topics`
- `D:\OneDrive - The Open University\Cambridge Lecture Notes\Cambridge Dexter Notes`
- `D:\OneDrive - The Open University\Currently Reading`
- `D:\OneDrive - The Open University\Tripos Papers`

## 9. Build order (each phase ends usable)

1. **Phase 0** — Repo scaffold, MISSION.md, NOTES.md, syllabus DAG
   (`syllabus.yaml`), module specs for Semester 1. *(≈1 session)*
2. **Phase 1** — `/today`, `/lecture`, `/status` + first two weeks of
   Semester 1 lessons. **Studying starts here.** *(2–3 sessions)*
3. **Phase 2** — SRS engine (`scheduler.py` + deck seeded from Dexter splits
   and Semester 1 lessons), `/grade`, first problem sets. *(1–2 sessions)*
4. **Phase 3** — Dashboard, morning scheduled agent, notifications, `/resume`
   hardening. *(1–2 sessions)*
5. **Phase 4** — `/ingest`: full collection audit → `inventory.json`,
   RESOURCES.md per module. *(1 session)*

## 10. Risks and mitigations

- **Two years is aggressive** → DAG lets schedule slip without structural break.
- **Claude grading Claude-adjacent material** → all grading anchored to real
  texts with citations; rubrics written per problem set at generation time.
- **Novelty decay (month 2–3)** → capstone is real research; deliberate
  system-refresh review scheduled at week 6.
- **Usage-limit interruptions** → state-first design; `/resume` from files only.
- **Token burn** → weekly batch generation; local SRS; model tiering per §5.
