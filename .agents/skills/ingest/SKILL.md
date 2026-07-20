# /ingest — Phase 4 collection audit

Builds `resources/inventory.json`: a module-mapped catalogue of Stephen's
existing PDF collection, so lesson/problem/SRS generation for Semesters 2-4
can cite what he already owns instead of guessing.

**Model: run this under Sonnet (Codex-sonnet-5), default effort.** The work
is classification-by-name at folder level — it needs enough maths literacy to
map "M6 Constructive Mathematics" or "Ramsey Theory" onto (or off) the
syllabus, which is beyond Haiku, but there is nothing here worth Opus/Fable
or extended thinking. Do NOT open or read any PDF contents; classify from
folder and file names only. Do not spawn subagents; do the work yourself.

## Pre-scanned ground truth (2026-07-07 — trust this, do not re-derive)

| Collection | Path (under `D:\OneDrive - The Open University\`) | PDFs | Structure |
|---|---|---|---|
| Undergraduate Mathematics | `Undergraduate Mathematics` | 631 | 19 topical subfolders (Abstract Algebra, Analysis, Topology, Number Theory, Problem Books, John Stillwell, Unsorted, ...) |
| Oxford Lecture Notes | `Oxford Lecture Notes for essential topics` | 1949 | 19 course folders named `M1..M6 <Course>` + Bridging Material; each holds notes + problem sheets + solutions |
| Cambridge Dexter Notes | `Cambridge Lecture Notes\Cambridge Dexter Notes` | 381 | flat; ~63 courses x suffix set `<course>.pdf`, `_trim`, `_def`, `_eg`, `_thm`, `_thm_proof` |
| Currently Reading | `Currently Reading` | 5 | flat (Brannan, Stillwell x2, Spivak Calculus, Earl Companion) |
| Tripos Papers | `Tripos Papers` | 111 | IA / IB / II / Vintage |

## Procedure

1. Enumerate with cheap shell listings (`Get-ChildItem -Directory`, filename
   lists for flat folders). Classify at **folder level** everywhere except
   Dexter base names, Currently Reading, and Undergrad-Maths loose files.
2. For each entry decide: `module` (a syllabus module id from
   `curriculum/syllabus.yaml`, or `null` if outside the curriculum),
   `kind` (`course-notes | textbook | problem-sheets | srs-split | exam |
   enrichment`), `semester_relevance` (1-4 or `null`), and one-line `notes`.
   Off-curriculum material (QFT, statistics, mathematical physics) gets
   `module: null` — catalogued, never deleted or moved.
3. Dexter: emit one entry per *course* (not per file) with a `splits` list of
   the suffixes present. Set `srs_corpus: true` for courses matching syllabus
   modules (analysis, groups, linear algebra, metric/topological spaces,
   algebraic topology, ...) — the `_def`/`_thm` splits are the designated
   future SRS card source.
4. Oxford course folders map by name: M1 Groups→gt, M1 LA I/II→la,
   M2 Analysis I-III→an, M3 Intro Calculus→an-adjacent, others judge against
   the syllabus. Note that problem sheets + solutions exist per course —
   flag with `has_problem_sheets: true` (valuable for /grade remediation).
5. Tripos: single entry per tier (IA/IB/II/Vintage); IA is the
   semester-1-relevant tier.
6. Write `resources/inventory.json`:
   `{"generated": "<date>", "collections": {"<name>": {"path": ..., "entries": [...]}}}`
   — atomic write (`.tmp` + `os.replace` via a small python script, or write
   then rename). Validate it parses with `python -c "import json,sys; json.load(open('resources/inventory.json'))"`.
7. Append a summary section to `resources/RESOURCES.md` (counts per module,
   top gaps if any module has no owned backup text) and commit both files:
   `git commit -F <tempfile>` per house rules.

## Budget guardrails
- Zero PDF reads. Zero web fetches. Filename lists only; for the two big
  collections request names only (`-Name`) and process in one pass.
- Target: single session, well under 100k tokens. If a folder is ambiguous,
  record `kind: "unsorted"` and move on — perfect classification is not the
  bar; a usable citation index is.
