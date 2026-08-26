# cap-01 — Scoping a research question

**Module:** Capstone · **Unit:** cap-01
**Sources.** This unit has no textbook. Its claims bind to three things instead,
and every problem below says which:

1. **Repo artifacts** — `MISSION.md` (the success criteria the capstone answers
   to) and `curriculum/LESSON-RUBRIC.md` (a worked example of what it looks like
   to write down in advance what would count as failure).
2. **Theorems already proved in this curriculum**, cited to their texts: <span class="cite">Dey &
   Wang, *Computational Topology for Data Analysis* — Definition 6.1 and
   Definition 6.2 (p. 181), Theorem 6.3 (p. 182), Definition 6.8 (pp. 193–194),
   Definition 6.10 and Proposition 6.9 (p. 195), Theorem 6.11 (pp. 196–197),
    Theorem 6.13 (p. 198), Definition 13.8 (p. 406);</span> <span class="cite">Ghrist,
   *Elementary Applied Topology* — Theorem 10.15, p. 220.</span>
3. **tdlbook.org** — *Topological Deep Learning: Going Beyond Graph Data*, the
   capstone companion named in `resources/RESOURCES.md`. It is cited here for
   what it is and is not: a text on combinatorial complexes and neural networks,
   containing no persistent homology, no study design and no null models. Where a
   problem below needs any of those, it takes them from (2), not from the book.

Submit your written solutions via `/grade cap-01`.

---

## Problem 1 (easy — a claim and its falsifier) [interleaves pw-05]

(a) Write down, in one sentence each, three candidate claims you might make from
a persistent-homology analysis. Make one of them *unfalsifiable by construction*
and say what makes it so.
(b) For each of the three, state what observation would count as the claim being
wrong. If you cannot state one, that is the answer, and say why.
(c) `MISSION.md` lists four things that "success looks like". Quote the two that
a capstone claim must satisfy, and say for each whether it constrains the *claim*
or the *evidence*.
(d) Produce the artifact: a one-page **claim card** with four fields — Claim,
Falsifier, Evidence that would support it, Evidence that would kill it. Fill it in
for the question you actually intend to pursue.

*(MathUni `MISSION.md`, "Success looks like"; the argument here is the unit's own,
not a citation)*

<details><summary>Nudge</summary>
"The data has interesting topological structure" is not a claim; it is a mood.
</details>
<details><summary>Strategy</summary>
A falsifier must be an observation you could actually make with the pipeline you
intend to run — not one requiring data you will never have.
</details>
<details><summary>Partial</summary>
A claim whose falsifier is "the barcode would have looked different" is circular
unless you say *how* different, and against what reference.
</details>
<details><summary>Worked start</summary>
(a) Three candidates. (i) *"The trajectory embedding contains a persistent
one-dimensional cycle."* — falsifiable in principle, but only once "persistent"
is given a threshold and a reference. (ii) *"Topology reveals hidden structure in
the data."* — unfalsifiable by construction: "structure" is undefined, "reveals"
names no measurement, and no observation could contradict it. Every barcode has
bars; the sentence is compatible with all of them. (iii) *"The observed
H<sub>1</sub> diagram differs from the diagram of an order-shuffled null more than
null diagrams differ from each other."* — falsifiable, because it names the
statistic, the comparison and the reference class.
(b) For (i), the falsifier is: every H<sub>1</sub> feature has persistence below
the threshold fixed in advance. For (ii) there is none, which is the point. For
(iii): the observed-to-null distance lies inside the null-to-null distribution.
(c) From `MISSION.md`: "I can read a current TDA paper (e.g. on multiparameter
persistence) and verify its main argument" — this constrains the *evidence*, since
verification is an operation on argument and hypotheses; and "I can explain the
stability theorem for persistence diagrams and why it licenses the TDL pipeline's
conclusions" — this constrains the *claim*, since it says a conclusion must be
one a stability theorem licenses, which rules out claims about features the
theorem cannot see.
(d) The claim card is the deliverable; the model fragment is:
| Field | Entry |
|---|---|
| Claim | The H<sub>1</sub> structure of the embedded trajectories is not reproduced by a second-order Markov null. |
| Falsifier | The observed-to-null Wasserstein distance falls within the null-to-null distribution at the pre-registered level. |
| Supporting evidence | p below the pre-registered threshold, with a positive control that the test can detect a planted signal. |
| Killing evidence | p above threshold; or a positive control that fails, in which case the test detects nothing and the result is uninformative either way. |
Note the last row: a null result and an uninformative test are different outcomes,
and a claim card that cannot tell them apart is not finished.
</details>

---

## Problem 2 (easy — what the theorems let you ask about)

(a) State Theorem 6.3(a). What does it say about two point sets at Hausdorff
distance ε?
(b) Deduce: if your sample is accurate to ε in Hausdorff distance, which features
of the Rips diagram can a claim be *about*? Give the threshold in terms of ε and
justify it by the definition of the bottleneck distance.
(c) State Definition 6.8 and Definition 6.10. Neither the reach nor the weak
feature size is computable from a point cloud. What does that do to a claim that
invokes Theorem 6.11 or Theorem 6.13?
(d) Produce the artifact: a **claimable-features note** stating, for your intended
analysis, the sampling accuracy you are willing to assume, the resulting
persistence threshold below which no claim will be made, and the feature-size
quantity your inference theorem needs and how you will argue for it.

*(Dey §6.1, Definition 6.1 and Definition 6.2 p. 181, Theorem 6.3 p. 182; §6.3.1,
Definition 6.8 pp. 193–194 and Definition 6.10 p. 195; §6.3.2, Theorem 6.11
pp. 196–197; §6.3.3, Theorem 6.13 p. 198)*

<details><summary>Nudge</summary>
A diagram point at L<sub>∞</sub>-distance ε from the diagonal has persistence 2ε.
</details>
<details><summary>Strategy</summary>
Bottleneck distance allows matching a point to the diagonal; ask which points can
be matched away at cost ε.
</details>
<details><summary>Partial</summary>
Theorem 6.3(a): $\mathsf{d}_{\mathrm{Rips}}(P,Q) \leq \mathsf{d}_H(P,Q)$.
</details>
<details><summary>Worked start</summary>
(a) Theorem 6.3(a): for finite $P, Q \subseteq (Z,\mathsf{d}_Z)$,
$\mathsf{d}_{\mathrm{Cech}}(P,Q) \leq \mathsf{d}_H(P,Q)$ and
$\mathsf{d}_{\mathrm{Rips}}(P,Q) \leq \mathsf{d}_H(P,Q)$, where by Definition 6.1
$\mathsf{d}_{\mathrm{Rips}}$ is the maximum over $k$ of the bottleneck distance
between the $k$-th Rips diagrams. So two point sets within Hausdorff distance ε
have diagrams within bottleneck distance ε in every dimension.
(b) Suppose the true underlying set and your sample are within ε in Hausdorff
distance. Then the two Rips diagrams are ε-close in bottleneck distance, so there
is a matching in which every point moves at most ε in $L_\infty$ — and a point may
be matched to the diagonal at cost equal to its $L_\infty$-distance to the
diagonal, which for $(b,d)$ is $(d-b)/2$. Hence any feature with
$(d-b)/2 \leq \varepsilon$, that is with **persistence at most 2ε**, may be
matched away entirely: it can be present in one diagram and absent in the other
without violating the bound. A claim may therefore only be *about* features of
persistence exceeding 2ε. Below that threshold the theorem licenses nothing, and
a claim made there is a claim about the particular sample rather than about what
it samples.
(c) Definition 6.8: the local feature size at $x \in X$ is its distance to the
medial axis and the **reach** $\rho(X)$ is the minimum over $X$. Definition 6.10:
with $C$ the critical points of the generalised gradient, the **weak feature
size** is $\mathrm{wfs}(X) = \min_{x \in X}\inf_{c \in C}\mathsf{d}(x,c)$. Both are
properties of the hidden set, not of the sample. Theorem 6.11 requires
$3\varepsilon \leq \alpha \leq \frac{3}{16}\sqrt{3/5}\,\rho(X)$ and Theorem 6.13
requires $\varepsilon < \frac{1}{9}\mathrm{wfs}(X)$ with α in a window set by it,
so invoking either means *assuming* a lower bound on a quantity you cannot
measure. The consequence for a claim: it is conditional, and the condition must
appear in the claim rather than in a footnote. A scoped question says "if the
hidden set has reach at least ρ₀ and the sample is ε-dense, then …", and part of
scoping is deciding what argument — from the acquisition process, not from the
data — will support ρ₀.
(d) The artifact is the note; the shape is three lines and a paragraph: the
assumed ε and where it comes from; the derived threshold 2ε and the statement
that no feature below it will be discussed; and the feature-size quantity, which
theorem needs it, and the non-circular argument for the bound.
</details>

---

## Problem 3 (medium — could it come out the other way?)

(a) The unit's mission strip says a question is well scoped when the summary you
plan to compute "could in principle come out the other way". Restate that as an
operational requirement on the analysis, not on the analyst.
(b) A null model is the standard way to meet it. State what a null must do to the
object your statistic consumes, and give one example of a null that fails this
test — a perturbation that leaves the statistic's input unchanged.
(c) Explain what a *positive control* adds that a null does not, and describe the
outcome pattern that makes a study uninformative rather than negative.
(d) Produce the artifact: a **falsifiability plan** naming (i) the statistic, (ii)
at least two nulls that perturb different structure in the data, (iii) the
positive control, and (iv) the decision rule, fixed in advance.

*(The argument here is the unit's own; the statistic in (i) should be one of those
you have citations for, e.g. the $(p,q)$-Wasserstein distance of Dey
Definition 13.8, p. 406)*

<details><summary>Nudge</summary>
If shuffling something changes nothing about what the statistic reads, the
resulting "null" is a copy of the observation.
</details>
<details><summary>Strategy</summary>
For (c), consider a study whose null is not rejected *and* whose positive control
also fails.
</details>
<details><summary>Partial</summary>
Two nulls that perturb the same structure are one null run twice.
</details>
<details><summary>Worked start</summary>
(a) Operationally: before the analysis is run, there must exist a specified
outcome of the *computation* — not of the interpretation — that the analyst has
committed in advance to reporting as "the claim failed". "Could come out the
other way" is a property of the design, testable by asking someone else to name
the failing output.
(b) A null must perturb the object the statistic actually consumes. If the
statistic is the Wasserstein distance between the observed H<sub>1</sub> diagram
and a reference diagram, the null must produce a diagram — which means the
perturbation has to happen upstream of the filtration, at the level of the data
or the metric, and has to destroy the structure the claim is about while
preserving what the claim does not depend on. A failing example: permuting the
*labels* attached to points when the filtration is built from pairwise distances
alone. The Rips complex of Definition 2.10 depends only on the pairwise distances,
so relabelling leaves every distance, hence every simplex, hence the entire
diagram, identical; the "null distribution" is a spike at the observed value and
the test has no power at all.
(c) A null tells you what the statistic looks like when the claimed structure is
absent. A positive control tells you what it looks like when the structure is
*present* — you plant a signal of known size and check the test detects it.
Without one, a non-rejection is ambiguous between "no effect" and "no power". The
uninformative pattern is exactly that pair: the null is not rejected and the
positive control also fails to reject. Then nothing has been learned, and
reporting it as a negative result would be a mistake — the honest report is that
the instrument did not work.
(d) The artifact. A worked shape, with two nulls that genuinely differ in what
they destroy: (i) statistic — the 2-Wasserstein distance between H<sub>1</sub>
diagrams, in the sense of Definition 13.8's $\mathsf{d}^p_{W,q}$; (ii) nulls — an
*order shuffle*, which destroys temporal sequence while preserving the marginal
distribution of states, and a *second-order Markov surrogate*, which preserves
pairwise transition structure and destroys only what is above it; note these
target different structure, so agreement between them is evidence and
disagreement is informative; (iii) positive control — a synthetic dataset with a
planted cycle of known persistence, run through the identical pipeline; (iv)
decision rule — reject at a level fixed in advance, with the number of
permutations and the level both written down before any of it is run.
</details>

---

## Problem 4 (medium — the parameters are part of the question)

(a) List every free parameter the analysis you intend to run will require, from
raw data to reported number. For each, say whether it is fixed by the data, fixed
by a theorem, or chosen by you.
(b) For the chosen ones, say what would change about the conclusion if each were
moved. Which of them can be swept, and which are too expensive to sweep?
(c) `curriculum/LESSON-RUBRIC.md` is an example of a document that fixes in
advance what would count as failure, at four gates, with the ordering stated. Read
its Gate 0 and Gate 2 rows and say what each does that the other cannot. Then say
which of the two your falsifiability plan currently resembles.
(d) Produce the artifact: a **pre-registration stub** — the claim, the pipeline
with every parameter and its chosen value, the nulls, the positive control, the
decision rule, and a dated statement that this was written before the analysis was
run.

*(MathUni `curriculum/LESSON-RUBRIC.md`, Gate 0 and Gate 2; the rest is the unit's
own argument)*

<details><summary>Nudge</summary>
"The default" is a choice, not an absence of one.
</details>
<details><summary>Strategy</summary>
A parameter you cannot afford to sweep is a parameter your conclusion is
conditional on; say so rather than hoping.
</details>
<details><summary>Partial</summary>
Gate 0 is mechanical and cheap; Gate 2 is a human read and is the veto.
</details>
<details><summary>Worked start</summary>
(a) A typical list, with the classification: the metric on the raw space
(*chosen*); the embedding and its dimension (*chosen*); the subsample size or
landmark count (*chosen*); the complex — Čech or Rips (*chosen*, and the pair is
related by the multiplicative 2-interleaving of Dey §6.1 with its log 2 bottleneck
bound, so the choice costs a known constant); the coefficient field (*chosen*);
the maximum scale (*chosen*); the homology dimensions computed (*chosen*); the
summary statistic (*chosen*); the null type and permutation count (*chosen*); the
significance level (*chosen*). Almost nothing on that list is fixed by the data,
which is the point of writing it out.
(b) Some are cheap to sweep — the coefficient field, the significance level, the
homology dimension. Some are expensive — a landmark count of 5000 with a hundred
permutations of a Wasserstein statistic is hours of compute, so a sweep over
landmark counts multiplies that. The honest position for an unswept parameter is
that the conclusion is conditional on it, stated in the claim.
(c) Gate 0 is mechanical, model-agnostic, free, and run before a human looks; it
proves *form and mention*, never truth, and any failure rejects without further
scoring. Gate 2 is the correctness gate, the one no script can run, and it is a
veto: a single defect fails the artifact whatever the other gates say. What Gate 0
can do that Gate 2 cannot is run at zero cost on everything, every time; what
Gate 2 can do that Gate 0 cannot is notice that a true-looking statement is false.
A falsifiability plan that consists only of a decision rule on a p-value resembles
Gate 0 — cheap, mechanical, and blind to whether the quantity means what you think.
Most plans need a Gate 2 row: a named human check of whether the statistic's
hypotheses hold on this data.
(d) The pre-registration stub is the artifact. Its one non-obvious requirement is
the date and the ordering claim: a plan written after the analysis is a summary,
not a pre-registration, and the difference is not detectable from the document
unless the document says so.
</details>

---

## Problem 5 (hard — the scoped question, and what the companion text does not give you)

(a) `resources/RESOURCES.md` names tdlbook.org — *Topological Deep Learning:
Going Beyond Graph Data* — as the capstone companion. Consult it and answer: does
it contain persistent homology, filtrations or stability theorems? Does it contain
guidance on scoping a study, or null models? Where does it use Mapper, and in what
role?
(b) Given your answer, state precisely which parts of your scoping work the book
can support and which it cannot, and say where the unsupported parts come from
instead.
(c) A colleague proposes this question: *"Does topological data analysis reveal
structure in the trajectory data that clustering misses?"* Diagnose it against
Problems 1–4: name every respect in which it is not yet scoped, and rewrite it as
a claim that could come out the other way.
(d) Produce the artifact: the **scoping document** for your capstone question —
claim card, claimable-features note, falsifiability plan and pre-registration stub
assembled into one document, with a final section headed "What this question
cannot settle" listing at least three things, each with the reason.

*(tdlbook.org, *Topological Deep Learning: Going Beyond Graph Data*, table of
contents and §7.4, §9.4 and Appendix E; MathUni `resources/RESOURCES.md`, the
"Capstone resource" note)*

<details><summary>Nudge</summary>
"Reveals structure that clustering misses" contains three undefined terms and no
comparison.
</details>
<details><summary>Strategy</summary>
For (c), a rewritten claim needs: a statistic, a reference, a threshold and a
dimension.
</details>
<details><summary>Partial</summary>
The book's Mapper appears as a pooling operation, not as a summary of data.
</details>
<details><summary>Worked start</summary>
(a) The book is a text on topological *deep* learning: combinatorial complexes and
combinatorial complex neural networks, higher-order message passing, pooling and
unpooling, with applications to mesh segmentation and classification and software
in TopoNetX, TopoEmbedX and TopoModelX. It contains no persistent homology, no
filtrations, no persistence diagrams and no stability theorems; no guidance on
scoping or designing a study; and no null models or hypothesis testing. Mapper does
appear — §7.4 "Mapper and the CC-pooling operation", §9.4 "Pooling with mapper on
graphs and data classification", and Appendix E on a mapper-induced
topology-preserving CC-pooling operation — but in the role of a *pooling operation*
inside a neural architecture, not as a topological summary of data in tda2-07's
sense.
(b) It can support: the framing that data need not be a graph and that higher-order
structure is representable, and a genuine point of contact with tda2-07 — the same
Mapper construction, used for a different purpose. It cannot support: any claim
about persistence, stability, sampling accuracy, feature size, nulls or study
design. Those come from the curriculum's own texts — Theorem 6.3, Theorems 6.11 and
6.13, Definition 13.8, Ghrist's Theorem 10.15 — and from the argument of this unit.
Saying so in the scoping document is not a formality: a reader who assumes the
capstone's methodology came from the named companion will misjudge what is
supported.
(c) The proposal fails on every count. *"Topological data analysis"* names no
statistic. *"Reveal"* names no measurement and no threshold. *"Structure"* is
undefined. *"That clustering misses"* names a comparison but no way to make it —
two methods returning different objects cannot be compared without a common
quantity. There is no dimension, no reference class, and no outcome that would
count as failure. A rewrite: *"In the embedded trajectory data, the observed
H<sub>1</sub> diagram lies further from the diagrams of second-order Markov
surrogates, in 2-Wasserstein distance, than those surrogates lie from one another;
and this holds for features of persistence above 2ε, where ε is the assumed
sampling accuracy."* That names a statistic, a reference class, a dimension and a
threshold, and it fails if the observed distance falls inside the surrogate-to-
surrogate distribution.
(d) The scoping document is the deliverable. On its last section: three candidates
for "What this question cannot settle" are (i) anything about features of
persistence below 2ε, by Problem 2's derivation; (ii) anything requiring a bound
on the reach or weak feature size, since neither is computable from the sample and
Theorems 6.11 and 6.13 are conditional on them; (iii) any causal statement, since
the design is a comparison against surrogates and surrogates are not
interventions. Each entry names the reason, not just the limitation.
</details>
