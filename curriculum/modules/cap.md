# Module: Capstone (cap) — Semester 4

**Primary text:** the TDL project itself. **Support:** `tdlbook.org` (registered
source), the Expository Writing folder, and self-directed reading chosen during
cap-01. There is no textbook here by design — the capstone is where the
curriculum stops supplying the question.

**Mission link:** every prior module was instrumentation. This one is the
measurement. The mission was never "learn algebraic topology"; it was to be able
to read, verify and produce work in topological data analysis — so the capstone
is scored on whether a claim is *defensible*, not on whether a pipeline ran.
cap-03 in particular is the whole curriculum's exit exam in disguise: take a
published result, find its load-bearing theorem, and check whether its
hypotheses hold on the data in front of you.

**On-ramp:** requires `lab-09` (a full analysis has been run at least once),
`pw-05` (critique standard), and the S4 machinery that makes verification
possible — tda2-08/09 for the pipeline's parameter choices, tda2-04 and at2-08
for the theorems a modern TDA paper leans on.

## Arc and unit map

Four units, in the order the work actually happens: **decide what you are
claiming**, **do it end to end**, **learn to break someone else's**, **write
yours so it can be broken**.

| Unit | Prereqs | Throughline |
|---|---|---|
| cap-01 scoping a research question | pw-05, lab-09 | a claim that could come out the other way |
| cap-02 the TDL pipeline end to end | cap-01, tda2-09, tda2-08 | every parameter choice on the record |
| cap-03 reading and verifying a research paper | cap-01, tda2-04, at2-08 | **locate the load-bearing theorem, check its hypotheses** |
| cap-04 the written defence | cap-02, cap-03 | reproducible, or falsifiable, by a hostile reader |

## Teaching notes

- **cap-01's failure mode is a question that cannot lose.** "Does this dataset
  have interesting topology?" is not a research question. Push until there is a
  stated outcome that would count as evidence against the claim.
- cap-02 is not lab-09 again. lab-09 was allowed to leave choices implicit;
  cap-02 requires each of them named and justified — metric, filtration,
  coefficient field, sparsification tolerance, vectorisation and its stability
  constant. The deliverable is the record of choices as much as the result.
- **cap-03 is where the hypothesis-checking habit is graded.** The recurring
  examples to rehearse: tameness for a barcode decomposition (tda1-04),
  a good cover for a nerve claim (tda2-07), closed *and* orientable for a
  duality claim (at2-07), interval-decomposability for a bottleneck statement in
  the multiparameter setting (tda2-04). Pick a paper that actually has a soft
  spot; a flawless paper teaches less here.
- cap-04 inherits pw-05's standard and turns it on Stephen's own work. The test
  to state up front: could a competent reader who distrusts the conclusion
  either reproduce it or locate the flaw, using only what is written?

## Scope note

Not a substitute for a supervised research project, and not assessed as novel
research. The capstone certifies *verification competence and defensible
practice*, not originality. Publication, peer review and collaboration workflow
are out of scope.

## Boundary with other modules

- vs `lab-09`: lab-09 is a mini-project with training wheels — a dataset, a
  pipeline, a result. cap-02 removes the wheels and adds the justification
  burden.
- vs `pw-05`: pw-05 teaches critique of mathematical writing in general;
  cap-03/04 apply it to a live research claim, including one's own.

## Assessment

- No SRS quizzes; the capstone is assessed on artefacts.
- Deliverables: a scoped question (cap-01), a reproducible end-to-end analysis
  with its parameter record (cap-02), a written verification of a published
  paper naming its load-bearing theorem and hypothesis status (cap-03), and the
  final written defence (cap-04). Graded per spec §7 against the same 80% gate,
  with the rubric weighted toward hypothesis-checking and honest failure
  reporting rather than result strength.

## Common misconceptions to watch (seed for learning-records)

- Treating a persistence diagram as a result rather than as evidence for a
  stated claim (cap-01).
- Reporting a barcode without the coefficient field, filtration and metric that
  produced it (cap-02) — those choices change the answer.
- Reading a paper for its conclusion rather than for its hypotheses (cap-03).
- Writing the defence as a narrative of what was done rather than an argument
  for why it licenses the claim (cap-04).
