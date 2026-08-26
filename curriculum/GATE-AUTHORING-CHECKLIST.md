# Gate-Authoring Checklist

Use this before introducing, widening, relaxing, or wiring any authoring gate.
A gate is complete only when its claim, population, controls, execution signal,
and limitations are reviewable together. A green run on today's corpus is not a
substitute for this checklist.

Record the answers in the gate's plan, PR, or test module. A blank answer is a
design gap, not an implicit “not applicable”.

## 1. State the guarantee

- [ ] **G1 — Claim.** Write one sentence the gate is meant to stop being
      self-attested. Name the semantic property, not the incident that prompted
      the gate.
- [ ] **G2 — Reading boundary.** Name the largest object the gate reads: token,
      clause, sentence, file, unit, or corpus. If the claim spans a larger object,
      add the wider check or state the limitation explicitly.
- [ ] **G3 — Population.** Derive the full governed population mechanically and
      report its size. A reviewer's examples are samples, not the population.
- [ ] **G4 — Attribution.** Make the checker's unit of attribution match the
      author's unit of composition. Do not attach one clause's page, hypothesis,
      or result number to a neighbouring claim.
- [ ] **G5 — Shared parser.** If another checker reads the same corpus structure,
      import its parser/resolver rather than reimplementing citation, book, page,
      or clause logic.

## 2. Prove the gate can distinguish right from wrong

- [ ] **G6 — Known failure.** Before first use, run the gate against a known
      defective input it must rediscover.
- [ ] **G7 — Spec-derived controls.** Enumerate accepted and rejected cases from
      the guarantee, including inputs absent from the current corpus. Do not
      derive the control set only from today's files.
- [ ] **G8 — Distinguishing control.** For every property claimed about the gate
      (“monotone”, “can only shrink”, “never decreases”), include a control that
      violates that property in the forbidden direction.
- [ ] **G9 — Boundaries and intersections.** Put suppression controls at the edge
      of the suppressed region. When adding or relaxing a feature, test its
      intersection with every older guarantee it overlaps.
- [ ] **G10 — Runtime dialect.** For delegated parsers or linters, name the
      artifact's runtime and the checker's grammar, then test an input on which
      the two dialects disagree.
- [ ] **G11 — Hidden containers.** Enumerate every container in which the checked
      language or property can occur; checking `<script>` does not check event
      attributes, URLs, SVG, or CSS.
- [ ] **G12 — Format coverage.** Spot-verify at least one finding per distinct
      source or format. One book's typography validates one book.

## 3. Make silence impossible

- [ ] **G13 — Outcome partition.** Every parse failure, missing field, unresolved
      selector, pageless result, and absent input has an explicit FAIL, WARN, or
      recorded exemption outcome. No `except` or `continue` path reports PASS.
- [ ] **G14 — Denominator.** Report both verdict and independently derived
      denominator: files, claims, citations, or records checked. Assert
      `checked + unchecked == total` (or the equivalent identity).
- [ ] **G15 — Measured limitation.** State the current count behind every known
      gap or unsupported form. “Known limitation” without magnitude silently
      normalises an unbounded backlog.
- [ ] **G16 — Safe bounds.** A safety cap may reject or return no candidate; it
      must never truncate a value into a different plausible value of the same
      type.
- [ ] **G17 — Positive execution signal.** A successful run names the gate,
      governed population, and denominator. A green workflow without that signal
      does not prove the gate ran.

## 4. Validate the execution path, not just the function

- [ ] **G18 — Supply chain.** Fixture generation, baseline fetches, registry
      resolution, and downloads fail loudly. Do not use `|| true` on a step that
      supplies a gate's input.
- [ ] **G19 — Corpus wiring.** Wire a per-artifact gate into the full-corpus CI
      loop in the same change, or record the bounded backlog and owner decision.
- [ ] **G20 — Manifest parity.** Local and CI runners derive their check list from
      one manifest; a parity control fails if either omits a gate.
- [ ] **G21 — Stable fixtures.** Controls depend on synthetic inputs or immutable
      fixtures, never on a currently broken lesson, an absent future file, a
      local book drive, or an environment-specific stdout string.
- [ ] **G22 — Functional environment.** Where the guarantee is a working runtime,
      execute the exact dependency path used later; a lockfile or top-level import
      proves only names and versions.
- [ ] **G23 — Versioned tool.** A checker used twice belongs in `scripts/` with a
      diff, tests, and CI entry; do not keep a recurring gate in a scratchpad.

## 5. Check that the evidence supports the claim

- [ ] **G24 — Composite binding.** If a claim needs multiple fields (result,
      section, page, edition), verify that they belong together, not merely that
      each exists independently.
- [ ] **G25 — Procedure versus property.** Verify the property the prose relies
      on directly. A correct nearest-neighbour table, rendering, or aggregate is
      not evidence for a matching, discrimination, or decomposition it does not
      compute.
- [ ] **G26 — Reproducibility versus sufficiency.** Re-execution matching stored
      output proves reproducibility. Separately require the decomposition or
      detail needed to support the prose conclusion.
- [ ] **G27 — Representation versus necessity.** Distinguish what a diagram makes
      legible from what the mathematics requires. A bijective representation does
      not create a new capability.
- [ ] **G28 — Mathematical controls.** Executable mathematical claims include a
      boundary-case probe. Fitted or empirical claims include the relevant
      negative/permutation control and state whether it tests existence of signal
      or calibrates a threshold.
- [ ] **G29 — Competing diagnosis.** Before publishing a diagnosis, state what
      output the competing hypothesis predicts and run a check that distinguishes
      the two.
- [ ] **G30 — Manual evidence.** A genuinely manual review leaves a dated,
      content-addressed or freshness-checked artifact proving it ran.

## 6. Change and review discipline

- [ ] **G31 — Precise relaxation.** Fix a false positive by improving the
      discriminator from source evidence. Preserve the original failure as a
      negative control; do not remove the region the gate uniquely protects.
- [ ] **G32 — Exemption uniqueness.** State what makes an exemption non-recurring.
      Prefer eliminating the exempted state when recurrence is possible.
- [ ] **G33 — Pattern closure.** For a reported instance, query the full change
      set for the same construct and record fixed, already compliant, or exempt
      with reason for every result.
- [ ] **G34 — Magnitude experiment.** Treat a review finding as a defect
      hypothesis. Where executable, compare original, fixed, and isolated-variable
      cases before describing the magnitude or cause.
- [ ] **G35 — Exact review set.** Capture review-thread IDs when read and resolve
      only that set; do not re-query “unresolved” and close later arrivals.
- [ ] **G36 — Authoring safety.** Never write regex, LaTeX, or other
      backslash-bearing content through a shell heredoc. Use a structured edit and
      inspect literal bytes if prior tooling may have transformed escapes.

## 7. Limits no per-file gate can solve

- [ ] **G37 — Cross-artifact claims.** Add an explicit cross-unit or
      lesson/problem-set comparison for hypotheses, references, and conclusions
      that no single-file gate can see.
- [ ] **G38 — Unmechanisable binding.** If a checker cannot determine which of
      two valid results a sentence means, write the authoring rule and make the
      limitation reviewer-visible rather than claiming mechanical coverage.
- [ ] **G39 — Source modality.** Record whether a source proves, states, applies,
      sets as an exercise, or disclaims a result; page presence alone does not
      establish attribution.
- [ ] **G40 — Stop claim.** End with the exact guarantee demonstrated, measured
      residual gaps, and claims that remain manual. Do not promote corpus green to
      mathematical truth or population-wide reliability.

## Coverage ledger for the 2026-08-20—25 review window

Every principle in `docs/plans/2026-08-25-gate-hardening-backlog-handoff.md`
maps to exactly one owning checklist row:

| Handoff principle | Owner | Handoff principle | Owner |
|---:|:---:|---:|:---:|
| 1 | G8 | 21 | G25 |
| 2 | G1 | 22 | G27 |
| 3 | G3 | 23 | G2 |
| 4 | G13 | 24 | G21 |
| 5 | G31 | 25 | G13 |
| 6 | G9 | 26 | G36 |
| 7 | G8 | 27 | G20 |
| 8 | G32 | 28 | G18 |
| 9 | G10 | 29 | G15 |
| 10 | G11 | 30 | G4 |
| 11 | G16 | 31 | G26 |
| 12 | G31 | 32 | G28 |
| 13 | G9 | 33 | G28 |
| 14 | G14 | 34 | G22 |
| 15 | G13 | 35 | G28 |
| 16 | G24 | 36 | G30 |
| 17 | G5 | 37 | G34 |
| 18 | G6 | 38 | G35 |
| 19 | G7 | 39 | G29 |
| 20 | G19 | 40 | G23 |
## Closing observations

When a backlog observation is actioned, update it in the same change window:
remove it from the active observation log, append it to the dated archive with
`Status: ACTIONED`, and record the exact implementation and validation evidence.
Do not leave the tracker update as an unwritten after-session convention.

