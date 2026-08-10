# cap-03 — Reading and verifying a research paper

**Module:** Capstone · **Unit:** cap-03
**Object of study.** By agreement, the work verified here is the TDL project's own
`results/trajectory_tda_integration`. Verifying your own results is the harder
exercise and the one the capstone actually requires; a published paper you did not
write is easier, because you have no stake in the answer.

**Sources.** No textbook. Claims bind to three things:

1. **Theorems already proved in this curriculum**, cited to their texts. Dey &
   Wang — Definition 4.14 (p. 138), Theorem 2.1 (p. 31), Definition 6.1 (p. 181),
   Theorem 6.3 (p. 182), Theorem 9.5 and Theorem 9.9 (pp. 262, 265),
   Definition 12.13 and Fact 12.2 (p. 375), Definition 12.14 and Definition 12.15
   (p. 376), Definition 12.16 (p. 377), Theorem 13.1 (p. 393), Theorem 13.2
   (p. 394), Theorem 13.3 (p. 395), Definition 13.8 (p. 406). Ghrist — Lemma 9.8
   (p. 187). Hatcher — Theorem 3.30, Poincaré Duality (p. 241).
2. **The artifacts themselves**, named by file, in
   `TDL/results/trajectory_tda_integration/`.
3. **Repo artifacts** — `MISSION.md`, and cap-01's and cap-02's methods.

Submit your written solutions via `/grade cap-03`.

---

## Problem 1 (easy — the protocol) [interleaves cap-01]

(a) Write down the verification protocol as an ordered list of five steps, each
one sentence. Step 1 must be "locate the load-bearing theorem"; you supply the
rest.
(b) Define "load-bearing" operationally: given a paper's conclusion, how do you
decide which of the results it cites is the one carrying it?
(c) A conclusion may be *weaker* than the theorem licenses, *equal* to it, or
*stronger*. Which of the three is a defect, which is a virtue, and which is
neither?
(d) Produce the artifact: a blank **verification sheet** — the five steps as
headed sections, with a hypothesis table whose columns are Hypothesis, Where
stated, Status (verified / assumed / unverifiable), Evidence.

*(The protocol is this unit's own; the standard it answers to is `MISSION.md`'s
"I can read a current TDA paper … and verify its main argument")*

<details><summary>Nudge</summary>
A theorem is load-bearing if removing it removes the conclusion.
</details>
<details><summary>Strategy</summary>
Most papers cite many results and lean on one or two. The rest are furniture.
</details>
<details><summary>Partial</summary>
"Unverifiable" is a status, not a failure — it is the status of a hypothesis about
a hidden object.
</details>
<details><summary>Worked start</summary>
(a) A workable protocol. **1.** Locate the load-bearing theorem — the result whose
failure would remove the conclusion. **2.** Extract its hypotheses, one line each,
in the form the theorem states them. **3.** Classify each hypothesis as *verified*
from the reported artifacts, *assumed* on grounds the authors give, or
*unverifiable* in principle from the data at hand. **4.** Check that the stated
conclusion is the one the theorem licenses, not a stronger one. **5.** Check that
the statistic actually computed is the quantity the theorem is stated in.
(b) Operationally: for each cited result, ask what would remain of the conclusion
if that result were false. If the conclusion survives, the result is context. If
it collapses, the result is load-bearing. Most papers have one or two; a paper
with none is reporting an observation rather than making an argument, which is a
finding in itself.
(c) A conclusion *weaker* than the theorem licenses is a virtue — the authors have
left margin. *Equal* is neither: it is what the theorem is for, though it means
any weakening of a hypothesis is fatal. *Stronger* is the defect, and it is the
one to hunt: it is the case where the reader who trusts the citation is misled,
because the citation is real and the inference from it is not.
(d) The sheet is the artifact. The one column readers skip is "Where stated" —
put the section and page, because half of verification is discovering that the
hypothesis is stated in a different place from the theorem, with different
quantifiers.
</details>

---

## Problem 2 (easy — four hypotheses and their theorems)

The unit's mission strip names four. For each of (a)–(d): state the theorem, state
the hypothesis exactly, and say whether a finite point sample could ever settle it.

(a) **Tameness for a barcode.** State Definition 4.14. Which part of a TDA
pipeline supplies it, and for which object is it automatic?
(b) **A good cover for a nerve claim.** State Theorem 2.1 as Dey and Wang quote
it. Then state what tda2-07 established actually holds for a Mapper pullback
cover, and name the two theorems.
(c) **Closed and orientable for a duality claim.** State Theorem 3.30. Then say
why tda2-10's Lemma 9.8, which Ghrist introduces as "a type of Poincaré duality",
is not an instance of it.
(d) **Interval-decomposability for a multiparameter distance.** State
Definition 12.15 and Definition 12.16, and say where Definition 12.13's bottleneck
distance needs them. State Fact 12.2.

*(Dey §4.5, Definition 4.14 p. 138; §2.2, Theorem 2.1 p. 31; §9.1, Theorem 9.5
p. 262 and Theorem 9.9 p. 265; §12.4, Definition 12.13 and Fact 12.2 p. 375,
Definition 12.15 p. 376, Definition 12.16 p. 377. Hatcher §3.3, Theorem 3.30
p. 241)*

<details><summary>Nudge</summary>
For (b), the pullback cover is path connected by construction, and that is the
only hypothesis the replacement theorems need.
</details>
<details><summary>Strategy</summary>
"Could a point sample settle it?" is a question about whether the object named in
the hypothesis is the sample or the thing sampled.
</details>
<details><summary>Partial</summary>
Theorem 9.5 and Theorem 9.9 give surjectivity in $\mathsf{H}_1$, not homotopy
equivalence.
</details>
<details><summary>Worked start</summary>
(a) Definition 4.14: an open interval $I \subseteq \mathbb{R}$ is a *regular
interval* if there is a space $Y$ and a homeomorphism $\Phi : Y \times I \to X_I$
with $f \circ \Phi$ the projection onto $I$, extending continuously to the
closure; $f$ is *of Morse type* if each levelset has finitely generated homology
and there are finitely many critical values, the complementary open intervals
being regular. What supplies it in a pipeline: the finiteness of the complex. A
PL-function on a finite simplicial complex is levelset tame, so for the *computed*
object tameness is automatic. What is not automatic is tameness of the *hidden*
function on the hidden space — and a sample cannot settle that, because the object
named is not the sample.
(b) Theorem 2.1: given a *finite* cover $\mathcal{U}$ (open or closed) of a *metric
space* $M$, the underlying space $|N(\mathcal{U})|$ is homotopy equivalent to $M$ if
every non-empty intersection of cover elements is contractible. What tda2-07
established: for a Mapper pullback cover nothing supplies contractibility, and the
chapter says so outright. What holds instead is weaker and provable — the pullback
cover consists of path connected components by construction, so Theorem 9.5 gives
that $\tilde\phi_{\mathcal{U}*} : \mathsf{H}_1(X) \to \mathsf{H}_1(N(\mathcal{U}))$
is a surjection, and Theorem 9.9 extends this to simplicial maps between nerves
induced by cover maps. Reading: loops in the picture come from loops in the data,
and loops in the data may vanish. Could a sample settle contractibility of the
intersections? Only for the computed cover, not for any cover of the hidden space.
(c) Theorem 3.30 (Poincaré Duality): if $M$ is a closed $R$-orientable
$n$-manifold with fundamental class $[M] \in \mathsf{H}_n(M;R)$, then
$D : \mathsf{H}^k(M;R) \to \mathsf{H}_{n-k}(M;R)$, $D(\alpha) = [M] \frown \alpha$,
is an isomorphism for all $k$. Ghrist's Lemma 9.8 asserts
$\mathsf{H}^0(\tilde X;\mathcal{F}) \cong \mathsf{H}^1(\tilde X;\mathcal{F})$ for a
flow sheaf on a subdivided network, proved by counting: $C^0 \cong C^1$ because
each vertex stalk is the sum of the stalks of its incoming edges and that
enumeration exhausts the cells, after which the isomorphism on cohomology comes
from exactness, $\dim \ker d = \dim \operatorname{coker} d$. It is not an instance
of Theorem 3.30 — there is no manifold, no orientation, no fundamental class, and
the isomorphism is induced by no pairing. The shared name records an analogy of
shape, $\mathsf{H}^k \cong \mathsf{H}^{n-k}$, not a shared mechanism. Could a
sample settle "closed and $R$-orientable"? No: that is a hypothesis about the
hidden manifold.
(d) Definition 12.15: a $d$-parameter *interval module* is a persistence module
supported on an interval in the sense of Definition 12.14, with identity maps
inside it. Definition 12.16: a $d$-parameter *interval decomposable module* is one
that can be decomposed into interval modules. Definition 12.13 defines the
bottleneck distance for modules $M \cong \bigoplus_i M_i$ and $N \cong \bigoplus_j N_j$
written in terms of their indecomposables — so a bottleneck distance between
multiparameter modules presumes a decomposition, and the clean case is interval
decomposability. Fact 12.2: $\mathsf{d}_I \leq \mathsf{d}_b$. Could a sample settle
interval-decomposability? It is a property of the computed module, so in principle
yes — but for $d \geq 2$ it is not automatic, which is exactly why
Definition 12.16 exists as a named condition rather than a remark.
</details>

---

## Problem 3 (medium — read the artifacts)

Open `TDL/results/trajectory_tda_integration/`.

(a) From `03_ph.json`: state the construction used, the landmark count, and for
each of $\mathsf{H}_0$ and $\mathsf{H}_1$ the number of features, the number of
infinite bars, and the three summary numbers reported.
(b) Which of those three summary numbers has a stability theorem in the sections
this curriculum has read? For each, name the theorem or write "none".
(c) From `04_nulls.json` and `04_nulls_wasserstein.json`: tabulate the null type,
the statistic, the permutation count, and the $\mathsf{H}_0$ and $\mathsf{H}_1$
p-values, for all eight tests.
(d) Produce the artifact: the **hypothesis table** for the analysis's main claim,
using Problem 1's four columns, with at least six rows drawn from Problem 2's four
hypotheses plus the pipeline choices of cap-02.

*(`TDL/results/trajectory_tda_integration/03_ph.json`, `04_nulls.json`,
`04_nulls_wasserstein.json`; Dey Theorem 13.1 p. 393, Theorem 13.2 p. 394,
Theorem 13.3 p. 395, Definition 13.8 p. 406)*

<details><summary>Nudge</summary>
The three summary numbers are total persistence, maximum persistence and
persistence entropy.
</details>
<details><summary>Strategy</summary>
For (b), look in §13.1 for a displayed stability bound naming each quantity. Two
of the three are not there at all.
</details>
<details><summary>Partial</summary>
$\mathsf{H}_1$ has 5962 features of which one is infinite.
</details>
<details><summary>Worked start</summary>
(a) `03_ph.json` records `n_landmarks = 5000` and a single summary block keyed
`maxmin_vr` — a Vietoris–Rips filtration on a maxmin (farthest-point) landmark
subsample. $\mathsf{H}_0$: 5000 features, 4999 finite, 1 infinite;
`total_persistence` 20411.13, `max_persistence` 15.809, `persistence_entropy`
8.447. $\mathsf{H}_1$: 5962 features, 5961 finite, 1 infinite;
`total_persistence` 2224.68, `max_persistence` 3.213, `persistence_entropy` 8.354.
The single infinite bar in each dimension is worth noting immediately: one
infinite $\mathsf{H}_1$ bar in a Rips filtration on a landmark set is a fact about
the maximum scale reached, not about the data, and the verification sheet should
ask whether the filtration was run to completion.
(b) None of the three has a stability theorem in the read sections. §13.1 gives
stability for the persistence *landscape* (Theorem 13.1, against $\mathsf{d}_B$,
constant 1), the persistence scale space kernel (Theorem 13.2, against
$\mathsf{d}_{W,1}$, constant $1/(2\pi\sigma)$) and persistence images
(Theorem 13.3). Total persistence, maximum persistence and persistence entropy
appear nowhere in §13.1, so for each the entry is **none**. That is not a claim
that they are unstable — it is the accurate statement that this curriculum has
proved nothing about them, and cap-02's ledger would record the row as
unconstrained.
(c) The eight tests:
| Null | Statistic | B | H0 p | H1 p |
|---|---|---|---|---|
| label_shuffle | total_persistence | 100 | 0.69 | 0.63 |
| cohort_shuffle | total_persistence | 100 | 0.66 | 0.54 |
| order_shuffle | total_persistence | 500 | 0.0 | 0.25 |
| markov | total_persistence | 500 | 0.148 | 0.652 |
| order_shuffle | wasserstein | 100 | 0.058 | 0.854 |
| markov | wasserstein | 100 | 0.002 | 0.086 |
| label_shuffle | wasserstein | 100 | 0.452 | 0.538 |
| markov2 | wasserstein | 100 | 0.546 | 0.078 |
(d) The hypothesis table is the artifact. Rows worth having: tameness of the
computed filtration (*verified* — finite complex); tameness of the hidden function
(*unverifiable*); sampling accuracy ε for Theorem 6.3 (*assumed*, and the argument
for it belongs in the evidence column); the reach or weak feature size, if any
inference theorem is invoked (*unverifiable*); the choice of statistic and whether
a stability theorem covers it (*verified* by inspection — and the answer here is
no); and the embedding, which cap-02's ledger records as constrained by nothing.
</details>

---

## Problem 4 (medium — when two summaries of the same diagrams disagree)

(a) Compare the two `order_shuffle` rows and the two `markov` rows of your
Problem 3 table. State the disagreement precisely.
(b) Both statistics summarise the *same* persistence diagrams. Explain how a
disagreement is possible at all, without either computation being wrong.
(c) One of the two statistics is the metric in which this curriculum's stability
theorems are stated, and one is not. Say which, cite the definition, and say what
follows for which of the two results is easier to defend.
(d) Produce the artifact: a **finding**, in the form the verification sheet asks
for — what was checked, what was observed, what it does and does not imply, and
what would settle it.

*(`04_nulls.json` and `04_nulls_wasserstein.json`; Dey Definition 13.8 p. 406,
Theorem 13.1 p. 393, Theorem 13.2 p. 394, Theorem 13.3 p. 395, Definition 6.1
p. 181, Theorem 6.3 p. 182, and §13.1.4's remark on bottleneck versus Wasserstein
stability p. 397)*

<details><summary>Nudge</summary>
A maximum, a sum and a matching cost are three different functionals of the same
diagram.
</details>
<details><summary>Strategy</summary>
A statistic with no stability theorem may still be a perfectly good test
statistic; the question is what a rejection using it licenses.
</details>
<details><summary>Partial</summary>
order_shuffle $\mathsf{H}_0$: p = 0.0 under total persistence, p = 0.058 under
Wasserstein.
</details>
<details><summary>Worked start</summary>
(a) Two disagreements, in opposite directions. Under `order_shuffle` in
$\mathsf{H}_0$, the total-persistence test reports p = 0.0 and is flagged
significant, while the Wasserstein test reports p = 0.058 and is not. Under
`markov` in $\mathsf{H}_0$, the total-persistence test reports p = 0.148 and is
not significant, while the Wasserstein test reports p = 0.002 and is. So each
statistic rejects a null the other does not.
(b) No computation need be wrong. Total persistence is a single number — the sum
of bar lengths — so a null distribution of total persistences compares one scalar
functional of the diagram. The Wasserstein statistic compares diagrams as objects,
through an optimal matching, and so is sensitive to *where* the bars are, not only
to how much bar length there is. Two diagrams can have equal total persistence and
be far apart in Wasserstein distance, and two diagrams can be Wasserstein-close
while differing in total persistence by an amount that is large relative to the
null spread. The tests are therefore genuinely different tests, and disagreement
is information about which aspect of the diagram each null perturbs.
(c) The Wasserstein distance is the metric: Definition 13.8 gives
$\mathsf{d}_{W,q}^p$, and §13.1's stability results — Theorem 13.2's
$1/(2\pi\sigma)$ bound for the PSSK, Theorem 13.3's for images — are stated
against $\mathsf{d}_{W,1}$, with Theorem 13.1's landscape bound stated against the
bottleneck distance. Total persistence appears in no stability statement in the
read sections. What follows is a preference, and the interesting part is what does
*not* follow. Do not upgrade "stated in the right metric" to "covered by a
stability theorem": the only bound this curriculum has from a perturbation of the
point cloud to a movement of the diagrams is Theorem 6.3, $\mathsf{d}_{\text{Rips}}
\leq \mathsf{d}_H$, and Definition 6.1 defines that left-hand side as
$\max_k \mathsf{d}_B$ between the corresponding diagrams. A bound in
$\mathsf{d}_B$ is not a bound in $\mathsf{d}_{W,1}$ — §13.1.4 remarks in passing
that bottleneck stability is the harder property to obtain for a vectorisation,
which is the same fact from the other side — so nothing read here reaches the
Wasserstein statistic either. This is cap-02's junction 2 in a new place: the chain
from data to statistic closes for neither. One statistic is written in the metric
the apparatus uses and the other is not; that is a reason for preference, not a
guarantee, and the verification sheet should say exactly that rather than treating
the two lines as interchangeable evidence.
(d) The finding is the artifact. Its "what it does not imply" line matters most:
the disagreement does not show either test is wrong, and it does not show the
effect is absent. What would settle it: running both statistics on the positive
control, where the answer is known by construction, and reporting which of the two
detects the planted signal.
</details>

---

## Problem 5 (hard — the full verification report)

(a) In `04_nulls_wasserstein.json`, each entry records `n_permutations = 100`, an
`obs_null_distribution` of length 100, and `n_null_null_pairs = 500`. The
`markov` $\mathsf{H}_0$ p-value is 0.002. Show that 0.002 is not attainable as
$1/(B+1)$ with B = 100, and state what the reference distribution must therefore
be. What does the protocol require you to do about this?
(b) Count the tests across both null files. Each entry carries its own
`significant_at_005` flag. State the multiple-comparison issue precisely, and say
what would have to be recorded for the flags to be interpretable.
(c) From `07_umap_sensitivity.json`: `pca_k = 7`, `umap_k = 6`, `ari ≈ 0.310`.
State what that shows about the embedding stage, and connect it to cap-02's ledger
entry for that stage.
(d) Open the single file in `positive_control/` and read what it records — the null
type, the statistic, the permutation count and the two p-values — then find the
script that produced it and read its docstring. State precisely what the file
establishes, what it does not, and whether it meets cap-01's requirement. Do the
same, more briefly, for `post_audit/`. Then produce the artifact: the
**verification report** — the five protocol steps, the hypothesis table, at least
three findings each with its "does not imply" line, and a closing paragraph
stating what you would need to see before the main claim could be reported as
established.

*(`TDL/results/trajectory_tda_integration/04_nulls.json`,
`04_nulls_wasserstein.json`, `07_umap_sensitivity.json`,
`positive_control/positive_control_markov1_L5000_20260502.json`, `post_audit/`;
`TDL/trajectory_tda/scripts/run_positive_control.py`; cap-01's falsifiability
plan; cap-02's parameter ledger)*

<details><summary>Nudge</summary>
With B permutations the finest attainable permutation p-value is $1/(B+1)$.
</details>
<details><summary>Strategy</summary>
For (b), the issue is not that multiple tests were run — it is that the flags are
per-test and the reader cannot recover the family. For (d), do not credit a
directory name; open the file, and when the file does not say what was planted,
go and read the script that wrote it.
</details>
<details><summary>Partial</summary>
$1/500 = 0.002$.
</details>
<details><summary>Worked start</summary>
(a) A permutation p-value computed as $(\#\{\text{null} \geq \text{obs}\} + 1)/(B+1)$
with B = 100 has a minimum of $1/101 \approx 0.0099$, so 0.002 cannot arise that
way; and $0.002 = 1/500$ exactly, which matches `n_null_null_pairs = 500`. So the
p-value is computed against the **null-to-null** distribution of 500 pairwise
distances, not against 100 permutations — the test asks whether the observed-to-null
distances sit outside the distribution of null-to-null distances, which is a
sensible design and a different one from a naive permutation test. What the
protocol requires: not to conclude that anything is wrong, but to **establish which
reference distribution is intended and record it**, because a reader who assumes
$B = 100$ will compute a resolution ten times coarser than the one used and will
misjudge every p-value in the file. Step 5 of the protocol — check the statistic
computed is the quantity the claim is stated in — is exactly this check.
(b) Eight tests appear across the two files (four nulls × one statistic in each),
each in two homology dimensions, so sixteen p-values, each carrying its own
`significant_at_005` flag. The issue is not that many tests were run — running
several nulls that destroy different structure is what cap-01 asks for — but that
the flags are computed per test with no record of the family they belong to. A
reader cannot tell whether "significant at 0.05" means "significant among these
sixteen" or "significant in isolation", and the two support very different claims.
What would have to be recorded: the family of tests fixed in advance, which of them
the claim depends on, and either a correction or an explicit statement that the
level is per-test and the family was pre-registered.
(c) `07_umap_sensitivity.json` reports that the same data, embedded by PCA and by
UMAP, yields 7 clusters and 6 clusters respectively, with an adjusted Rand index
of about 0.310 between the two labellings — that is, the downstream clustering is
substantially *not* stable to the choice of embedding. Connecting to cap-02: the
embedding row of the ledger has "none" in its "constrained by" column, and this
file is what that empty cell looks like when it is measured. The honest reading is
that any conclusion depending on the cluster structure is conditional on the
embedding choice, and the sensitivity analysis is evidence for how strongly.
Running it at all is exactly right; the finding is that its result belongs in the
claim.
(d) Read the file before crediting it, and this is the whole point of the problem.
It records `null_type` markov, `statistic` wasserstein, `n_permutations` 100, and
p = 0.588 in $\mathsf{H}_0$ and p = 0.822 in $\mathsf{H}_1$, neither flagged
significant. That is not a control that failed: `run_positive_control.py` states
the design in its docstring — the "observed" cloud is *itself generated* from the
fitted Markov-1 chain, and p ≈ 0.5 in both dimensions is the expected result,
because the null model reproduces the topology of data it generated. So the check
ran and returned its known answer. What it establishes is *specificity* — the test
does not reject when the null is literally true. What it does not establish is
*power*: no signal of known size is planted, so it cannot show the test would find
one, and cap-01's requirement is therefore not met by this file or by anything
else in the directory. The consequence is concrete: the non-rejections in the
directory, markov2 in $\mathsf{H}_1$ at p = 0.078 among them, cannot yet be read as
negative results. This is step 5 at its sharpest — the quantity computed is not the
quantity the name promises — and its "does not imply" line matters as much as any:
it does not imply the check is worthless, since it rules out a class of false
positive and was asked for by a reviewer, nor that anyone is confused, since the
docstring is exact. `post_audit/`'s alpha sweep at four values across two cohorts
at B = 1000 and its doubled-sample re-runs are the parameter sweeps cap-02's ledger
asks for on the rows that can afford them, and should be cited against that
requirement by name rather than as general diligence. The report is the artifact;
four findings worth having are the statistic disagreement of Problem 4, the
reference-distribution question of (a), the embedding sensitivity of (c), and the
reading of the control — each with a "does not imply" line, since none of the four
shows the main claim is false. The closing paragraph should say what would settle
the main claim: at minimum, a run of the headline statistic and null on a cloud
with a planted signal of known size, the family of tests as pre-registered, and a
statement of the sampling accuracy ε with the resulting persistence threshold from
cap-01.
</details>
