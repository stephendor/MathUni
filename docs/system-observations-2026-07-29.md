# MathUni system-observation disposition — 2026-07-29

**Source:** `TDL/docs/plans/strategy/system-review-2026-07-26-decision-report.md`

**Baseline:** `origin/main` at `b4c749d7ff4b0679da20e2217894a91b91792b12`

**Implementation branch:** `codex/address-mathuni-system-observations`

This is the repository-owned packet requested by the system review. It records
what was already present on the baseline, what this branch adds, and what
remains a semantic review rather than a mechanical claim.

| Observation | Disposition | Evidence |
|---|---|---|
| 96 | Implemented | Abstract Algebra declares `primary_resource: Aluffi Underground`; the validator rejects a contradictory lead source and chapter-only locator, with paired controls. `aa-00` is the explicit visual-on-ramp exception. |
| 97 | Implemented | `check_id_consistency.py` reconciles syllabus ids with progress, SRS, lessons, problem sets, solutions, and learning records. It also requires the expected artifacts for `in-progress` and `mastered` units. Negative controls cover orphan SRS cards, orphan lessons, and missing active-unit artifacts. |
| 98 | Verified present | `curriculum/LESSON-RUBRIC.md` already separates mechanical admission from a veto-level mathematical-correctness review and scored depth review. |
| 99 | Closed with control | `srs/scheduler.py` already pins stdout/stderr to UTF-8. A subprocess test now runs `due`, `stats`, and `rate` with `PYTHONIOENCODING=cp1252`, decodes UTF-8, and parses the JSON. |
| 102 (MathUni part) | Closed with control | `test_mastered_and_in_progress_survive_empty_mastery_record` proves `update_unlocks.recompute` cannot demote existing active states when mastery data is absent. |
| 107 | Implemented | `.gitattributes` fixes text to LF across platforms; `docs/phase1-notes.md` no longer calls the issue harmless or open. |
| 109 | Verified present | `lesson_lint.py` enforces render fidelity and structural counts; `LESSON-RUBRIC.md` records it as Gate 0.5. |
| 113 | Verified | The resource resolver boundary controls reject a run-on registered-name typo and an empty registry prefix. |
| 115 | Closed with controls | `lesson_lint.py --selftest` checks that script-only structure does not count. `test_coverage_error_bounces_candidate` proves a coverage-tool error is a failing drift-bundle result. |
| 118 | Implemented | PR CI rejects a base other than `main`. A scheduled/main-push recovery workflow also queries every merged PR and fails unless its exact head is reachable from the current default-branch head. Status controls cover reachable and stale-base cases; a live run against current GitHub history passed. |
| 119 | Verified | The baseline validator already failed closed on unreadable registries and rejected empty/malformed resource lists; its 10 controls passed before this branch extended them to 12. |

## Real-data correction found by the new gate

The first live `check_id_consistency.py` run found that `an-02` and `an-03`
were `in-progress` without learning records. This branch adds bounded records:

- `an-02` cites the existing 2026-07-18 session evidence that its lesson was
  opened.
- `an-03` preserves the recorded 2026-07-20 state while explicitly marking
  the missing session evidence; it does not invent a reflection or outcome.

## Validation

- Real syllabus: PASS.
- Validator controls: 12/12.
- Real id-space reconciliation: PASS after the two record corrections above.
- Lesson-lint controls: 8/8.
- Repository tests: 46/46.
- Live merged-head reachability against GitHub: PASS.
- Workflow YAML parse and `git diff --check`: PASS.

## Honest limits

- A section-level locator proves enough precision for a migration gate to bite;
  it does not prove that the cited section discusses the claimed topic.
  The syllabus authoring checklist still requires a source/TOC read.
- No mechanical gate proves mathematical truth. Lesson acceptance still
  requires Gate 2 review against the cited sources, with a recorded verdict.
- The merged-head gate deliberately certifies exact PR-head reachability. If
  the repository later adopts squash merges, the policy and gate must change
  together because a squash does not preserve the original head commit.
