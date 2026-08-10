# cap-04 — The written defence

**Module:** Capstone · **Unit:** cap-04

**What you produce.** One document: the defence of a claim about the TDL project's
`results/trajectory_tda_integration`, in four parts — the claim, the topological
evidence, the stability guarantee that licenses it, and the failure modes ruled
out — together with a scorecard in which you fail your own draft.

**Sources.** No textbook, and two of this unit's named resources are unavailable.
Claims bind to three things:

1. **Repository artifacts.** `MISSION.md`, for the standard the defence answers
   to; `curriculum/LESSON-RUBRIC.md`, for a critique standard that exists in this
   repository and can be read; `curriculum/syllabus.yaml`, for the record of
   pw-05's resources.
2. **Theorems already proved in this curriculum**, cited to their texts. Dey &
   Wang — Definition 6.1 and Definition 6.2 (p. 181), Theorem 6.3 (p. 182),
   Theorem 6.4 (p. 186), Theorem 13.1 (p. 393), Theorem 13.2 (p. 394),
   Definition 13.8 (p. 406).
3. **The artifacts**, named by file, in `TDL/results/trajectory_tda_integration/`
   and the TDL source tree.

**Two resources are missing, and it matters.** The syllabus gives this unit
"Expository Writing folder" and "self-directed"; the mission strip invokes
"pw-05's critique standard". The Expository Writing folder is not in this
repository, is not in `resources/bookmap.json`, and is not listed in
`resources/RESOURCES.md`. pw-05 has no lesson, and its own two resources are that
same folder and "Cummings appendix" — and the Cummings copy in `bookmap.json` runs
from Chapter 1 to *Introduction to Group Theory* with no appendix. So the critique
standard the mission strip points at cannot be read. This unit substitutes
`curriculum/LESSON-RUBRIC.md`, says so in the open, and Problem 1 makes the
substitution part of the exercise.

Submit your written solutions via `/grade cap-04`.

---

## Problem 1 (easy — the four parts, and the standard) [interleaves cap-03]

(a) The mission strip names four parts. Write, in one sentence each, what a reader
should be able to do after reading each part that they could not do before.
(b) `curriculum/LESSON-RUBRIC.md` is a critique standard in four ordered gates.
State the ordering rule, state which gate carries the veto, and quote the sentence
that says what Gate 0 does *not* establish.
(c) Transpose the four gates from lessons to a research defence. For each, say what
the defence's version checks and by what method.
(d) Produce the artifact: the **defence skeleton** — the four parts as headed
sections, each with a one-line statement of what goes in it, followed by a blank
scorecard in the rubric's form.

*(`MISSION.md`; `curriculum/LESSON-RUBRIC.md` Gate 0–Gate 3 and the scorecard
summary; cap-03's five-step protocol)*

<details><summary>Nudge</summary>
The rubric's gates are ordered because a cheap check that can fail should run
before an expensive one that cannot be automated.
</details>
<details><summary>Strategy</summary>
The transposition is not a metaphor. Ask literally: what is the mechanical check
on a defence, and what is the check no script can run?
</details>
<details><summary>Partial</summary>
The veto gate is Gate 2, mathematical correctness, and the rubric's reason for it
is that "a lesson that teaches a false statement is worse than no lesson".
</details>
<details><summary>Worked start</summary>
(a) After the **claim**, a reader can state what would have to be observed for the
claim to be false. After the **evidence**, they can locate every number in a file
on disk. After the **stability guarantee**, they can say which theorem carries the
inference from data to conclusion, and under which hypotheses. After the **failure
modes**, they can name what you considered and rejected, and by what artifact.
(b) The rubric says "The four gates are ordered. A lesson must clear each to reach
the next." Gate 2, mathematical correctness, carries the veto: "Any single defect
here fails the lesson outright, whatever Gates 1/3 look like". And Gate 0's limit
is stated in its own warning: "Gate 0 proves **form and mention**, never truth."
(c) The transposition. **Gate 0, mechanical:** does every number in the defence
appear in a named file, and does every citation resolve to a section that contains
what is attributed to it? Method: open the files. **Gate 1, structural:** are all
four parts present, and does the claim part contain a statistic, a reference class,
a dimension and a threshold, as cap-01 requires? Method: read the headings.
**Gate 2, correctness — the veto:** is every theorem stated with its actual
hypotheses, and is every inference one the cited theorem licenses? Method: cap-03's
five steps. **Gate 3, depth:** does every claim carry its "does not imply" line, and
is the limits section as specific as the results section? Method: judgement, which
is why it is scored rather than checked.
(d) The skeleton is the artifact. The scorecard's most useful row is the rubric's
own "Declared gaps : __ (NOT IN SOURCE markers; zero is a claim, not a result)".
Transposed: a defence that
lists no limitations has not been checked, it has been asserted.
</details>

---

## Problem 2 (easy — the guarantee that does hold)

(a) State Theorem 6.3(a) and Definition 6.1 exactly. Then state, in one sentence,
what d<sub>H</sub>(P, X) ≤ ε buys you about the diagrams.
(b) A bottleneck matching may send a diagram point to the diagonal at cost equal to
its L<sub>∞</sub>-distance to it. Compute that distance for a point (b, d) and
deduce the persistence threshold. State the resulting rule as a constraint on a
claim.
(c) Theorem 6.3(a) is stated for **two finite sets** in a common metric space.
Which object are you putting in the second argument, and what does that commit you
to? Read the remark following Theorem 6.3 before answering.
(d) Produce the artifact: the first paragraph of part 3 of the defence — the
guarantee that holds, the claim form it licenses, and the hypothesis it needs.

*(Dey §6.1, Definition 6.1 and Definition 6.2 p. 181, Theorem 6.3 with the remark
that follows it p. 182; cap-01's threshold derivation)*

<details><summary>Nudge</summary>
The closest diagonal point to (b, d) in the L<sub>∞</sub> metric is the midpoint
((b+d)/2, (b+d)/2).
</details>
<details><summary>Strategy</summary>
For (c), the remark after Theorem 6.3 extends *one* of the two parts to spaces that
are not finite. Note which part, and what metric that part is stated in.
</details>
<details><summary>Partial</summary>
The threshold is 2ε, not ε, and the factor of two comes from the distance to the
diagonal.
</details>
<details><summary>Worked start</summary>
(a) Theorem 6.3(a): given two finite sets $P, Q \subseteq (Z, \mathsf{d}_Z)$,
$\mathsf{d}_{\text{Cech}}(P,Q) \leq \mathsf{d}_H(P,Q)$ and
$\mathsf{d}_{\text{Rips}}(P,Q) \leq \mathsf{d}_H(P,Q)$. Definition 6.1:
$\mathsf{d}_{\text{Rips}}(P,Q) = \max_k \mathsf{d}_B(\mathrm{Dgm}_k\mathcal{R}(P),
\mathrm{Dgm}_k\mathcal{R}(Q))$. Together: if $\mathsf{d}_H(P,X) \leq \varepsilon$
then for every $k$ there is a matching of $\mathrm{Dgm}_k\mathcal{R}(P)$ with
$\mathrm{Dgm}_k\mathcal{R}(X)$ moving no point more than $\varepsilon$ in
$L_\infty$, unmatched points going to the diagonal.
(b) The nearest diagonal point to $(b,d)$ in $L_\infty$ is the midpoint, at
distance $(d-b)/2$ — half the persistence. So a bar of persistence $2\varepsilon$
costs exactly $\varepsilon$ to delete, and the matching is permitted to delete it.
The rule: **only features of persistence strictly greater than $2\varepsilon$ may
be claimed.** It converts a statement about how well you sampled into a threshold
below which you have agreed not to speak.
(c) Here is the commitment. Theorem 6.3(a) quantifies over two *finite* sets in a
common metric space. If the second argument is the full embedded point cloud and
the first is the landmark subsample, both are finite and the theorem applies as
stated, with $\varepsilon$ the covering radius of the landmark set. If the second
argument is a hidden space that the trajectories sample, it is not finite, and (a)
does not literally cover it; the remark after Theorem 6.3 extends **(b)** — the
Gromov–Hausdorff part, with its factor of 2 for Čech — to totally bounded metric
spaces, which is a different statement in a different metric. The defence must say
which of the two it is doing. They are not the same claim and they do not have the
same $\varepsilon$.
(d) The paragraph is the artifact. It should name the theorem, the hypothesis, the
value of $\varepsilon$, the resulting threshold $2\varepsilon$, and the sentence
"features below this threshold are not claimed here" — and if $\varepsilon$ is not
known, it should say that in the same paragraph rather than a later one.
</details>

---

## Problem 3 (medium — the guarantee that does not hold, and the number that is missing)

(a) `03_ph.json` records `n_landmarks = 5000` and a `maxmin_vr` summary. Read
`TDL/trajectory_tda/topology/trajectory_ph.py`, function `maxmin_landmarks`. Does the
routine compute the covering radius? Does it return it? Does `03_ph.json` record
it? Answer all three, then say what follows for Problem 2's paragraph.
(b) The same repository records a covering radius elsewhere. Find where, and say
what that changes about how the finding in (a) should be written.
(c) State cap-02's two junctions in one sentence each, and say for each what would
be needed to close it. Then add the third gap cap-03 measured, the one no theorem
constrains at all.
(d) Using the recorded numbers, compute the mean finite bar length in each of
H<sub>0</sub> and H<sub>1</sub>, and deduce the largest ε under which the *typical*
H<sub>1</sub> bar could be claimed. Comment on what that implies for a statistic
that sums over all 5961 finite H<sub>1</sub> bars.
(e) Produce the artifact: the second paragraph of part 3 — the links that do not
close, each with what would close it.

*(`TDL/results/trajectory_tda_integration/03_ph.json`;
`TDL/trajectory_tda/topology/trajectory_ph.py`;
`TDL/trajectory_tda/topology/permutation_nulls.py`;
`07_umap_sensitivity.json`; Dey Theorem 6.4 p. 186, Theorem 13.1 p. 393,
Theorem 13.2 p. 394, Definition 13.8 p. 406; cap-02's junction analysis)*

<details><summary>Nudge</summary>
The maxmin loop maintains an array of distances from every point to the nearest
landmark. Look at what that array contains when the loop exits.
</details>
<details><summary>Strategy</summary>
An absence is only a finding if the thing absent was obtainable. Establish the cost
of obtaining it before you write the sentence.
</details>
<details><summary>Partial</summary>
2224.68 / 5961 ≈ 0.373.
</details>
<details><summary>Worked start</summary>
(a) The routine computes it, does not return it, and the artifact does not record
it. `maxmin_landmarks` maintains `min_dists`, the distance from each of the N points
to its nearest chosen landmark, updating it on every iteration precisely so it can
take the argmax. Its maximum at loop exit is the covering radius of every landmark
but the last — an upper bound on the true one — and one further update, the same
O(N) pass the loop already performs each iteration, makes it exact. The function
returns `indices, landmarks`. `03_ph.json` records
`n_landmarks`, `elapsed`, and the per-dimension summaries — no radius. What follows
for Problem 2's paragraph is severe and simple: the one hypothesis on which the
whole guarantee turns is a number this pipeline computed and discarded, so the
paragraph cannot be completed as written. Write it conditionally, in ε, and record
that ε is one line of code away.
(b) `TDL/trajectory_tda/topology/permutation_nulls.py` computes and records
`covering_radius_at_n_perm` on the deduplication path, choosing the permutation
count via `compute_greedy_dedup_count` so that — its docstring's words — "the
covering radius is at or below" a documented tolerance. That changes the finding from a criticism into a request: the project already has
the mechanism and already records the quantity — on a different path from the one
the headline result comes through. A finding written as "nobody thought of this" is
both ruder and less accurate than one written as "this is recorded on the null path
and not on the PH path", and only the second tells anyone what to do.
(c) *Junction 1, sampling to sparsification:* both bounds are on bottleneck
distances, but one is an increment on the linear scale and the other an increment
at log scale, so they cannot be added; closing it would need the composite stated
per scale band rather than as a single number, since the absolute size of a
multiplicative perturbation depends on where on the scale axis the feature sits.
*Junction 2, diagrams to vectorisation:* Theorem 13.2 requires a bound on
$\mathsf{d}_{W,1}$ and everything upstream supplies a bound on $\mathsf{d}_B$, and
by Definition 13.8 a Wasserstein distance is a sum over matched pairs where the
bottleneck distance is a maximum, so the needed inequality runs the wrong way;
closing it needs a vectorisation whose stability is stated against
$\mathsf{d}_B$ — Theorem 13.1's landscape is exactly that. *The third gap:* the
embedding is constrained by no theorem at all, and
`07_umap_sensitivity.json` measures the consequence — PCA and UMAP on the same data
give 7 and 6 clusters with an adjusted Rand index of about 0.310.
(d) $20411.13 / 4999 \approx 4.083$ in $\mathsf{H}_0$ and $2224.68 / 5961 \approx
0.373$ in $\mathsf{H}_1$. A bar of length $0.373$ clears the threshold only if
$2\varepsilon < 0.373$, that is $\varepsilon < 0.187$ in the embedding's metric.
The consequence for the statistic is the point: total persistence *sums* over all
5961 finite $\mathsf{H}_1$ bars, so unless $\varepsilon$ is below roughly $0.19$
the statistic is dominated by bars no theorem permits you to claim individually.
That is not an argument that the test is invalid — a sum of unclaimable bars can
still be a perfectly good test statistic, as cap-03's Problem 4 sets out — but it
is an argument that the defence must not describe the statistic as topological
evidence *licensed by the stability theorem*. It is licensed by the permutation
test's own logic, which is a different licence.
(e) The paragraph is the artifact. Each link gets one sentence for what fails and
one for what would close it, and the paragraph ends by naming which of the four
gaps is cheapest to fix — the covering radius, at one line.
</details>

---

## Problem 4 (medium — the failure modes actually ruled out)

Part 4 of the defence says which failure modes are ruled out. "Ruled out" means an
artifact rules them out.

(a) Build the **failure-mode ledger**: columns *Failure mode*, *What would produce
it*, *What rules it out*, *Status*. Include at least six rows. Every row whose
status is "ruled out" must name a file.
(b) Three rows you must include: label leakage; a null test that rejects because
the null model is degenerate rather than because the data has structure; and low
power. Give each its true status from the artifacts, not its convenient one.
(c) One row of your ledger should be a failure mode of the *defence* rather than of
the analysis. Propose one and give its status.
(d) State the rule that decides whether a row reads "ruled out" or "open", and
apply it to the row you would most like to write as "ruled out".

*(`04_nulls.json`, `04_nulls_wasserstein.json`,
`positive_control/positive_control_markov1_L5000_20260502.json`,
`post_audit/`, `07_umap_sensitivity.json`; cap-01's falsifiability requirements;
cap-03's reading of the control)*

<details><summary>Nudge</summary>
A ledger row with no file in its third column is an "open" row however confident
you feel.
</details>
<details><summary>Strategy</summary>
Take the three rows in (b) in order of how much you would like them to be ruled
out. The order is a good predictor of which one you will overstate.
</details>
<details><summary>Partial</summary>
The label-shuffle null under the Wasserstein statistic reports p = 0.452 in
$\mathsf{H}_0$ and 0.538 in $\mathsf{H}_1$.
</details>
<details><summary>Worked start</summary>
(a)–(b) The three required rows, honestly.

| Failure mode | What would produce it | What rules it out | Status |
|---|---|---|---|
| Label leakage — the effect is an artefact of the cohort labels | Structure in the labels rather than the trajectories | Nothing yet. `04_nulls_wasserstein.json` label_shuffle p = 0.452 (H<sub>0</sub>), 0.538 (H<sub>1</sub>) and `04_nulls.json` 0.69, 0.63 record that it was **not detected** | **Open — not detected** |
| The test rejects because the null is degenerate, not because the data has structure | A null whose draws are so unlike anything that any observation looks extreme | `positive_control/positive_control_markov1_L5000_20260502.json`: a cloud drawn *from* the Markov-1 null is not rejected against it, p = 0.588 and 0.822 | **Partly closed** — see below |
| Low power — the test could not detect a real effect | Any non-rejection, including markov2 in H<sub>1</sub> at p = 0.078 | Nothing. No artifact plants a signal of known size | **Open** |

Rows one and two are where the discipline bites, and the first is the trap. It is
tempting to write "ruled out": the label-shuffle null was run, it did not reject,
and leakage is exactly what it perturbs. But apply this problem's own rule from
part (d) — a row reads "ruled out" when a named artifact *would have shown the
failure mode had it been present*, and did not. That the test would have shown it
is precisely what row three says is unestablished. A non-rejection from a test of
unknown power records that nothing was detected, not that nothing is there, and
the ledger cannot say in row one what it denies in row three. Write **not
detected** and cite the p-values as the record of the attempt.

Row two needs splitting rather than downgrading. `positive_control/` shows that
when the observed cloud genuinely *is* a Markov-1 draw, the test does not reject
it — so a whole mechanical class of degeneracy is excluded: the obs-null and
null-null distances are not computed in some asymmetric way, and landmark
selection is not biasing one side. That much is closed, and it is worth having.
What is not closed is the modelling case: the control substitutes a *synthetic*
observed cloud, so it says nothing about whether a rejection on the *real* data is
attributable to topological structure rather than to the Markov-1 model being a
poor description of the trajectories in some non-topological respect. Split the
row in two and give each half its own status. What it does not establish either
way is power, so the same file cannot also be cited in row three — the error the
file's name invites.
(c) A failure mode of the defence itself. Row: *the defence is read as a prosecution
of its own work and discounted.* What would produce it: findings written without
their "does not imply" lines, or a limits section longer than the results section
with no statement of what the results are. What rules it out: nothing mechanical —
this is a Gate 3 row, scored not checked. Status: open, and the mitigation is that
every finding carries its limit and part 1 states a claim rather than a hedge.
(d) The rule: a row reads "ruled out" when a named artifact would have shown the
failure mode had it been present, and did not. Not when the failure mode seems
unlikely, and not when a related artifact exists. Applied to the row you most want:
the temptation is the embedding row — one would like to write that the topology is
robust to the embedding choice. `07_umap_sensitivity.json` is the relevant artifact
and it reports an adjusted Rand index of about 0.310 between the PCA and UMAP
clusterings, which is evidence *for* the failure mode, not against it. The row reads
"open, and measured", which is a stronger sentence than "open" and a more honest one
than "ruled out".
</details>

---

## Problem 5 (hard — the defence, and failing your own draft)

(a) Write the defence: four parts, using Problems 1–4's artifacts. Part 1 states a
claim in cap-01's form — statistic, reference class, dimension, threshold. Part 2
gives the evidence with every number traceable to a file. Part 3 is Problems 2 and
3's two paragraphs. Part 4 is Problem 4's ledger.
(b) Score your own draft on the four transposed gates. You must record at least one
Gate 2 defect or explain, in a sentence a sceptic would accept, why there is none —
and the rubric's own warning applies: zero is a claim, not a result.
(c) `MISSION.md` lists as a success criterion: "I can explain the stability theorem
for persistence diagrams and why it licenses the TDL pipeline's conclusions." Given
Problems 2 and 3, write the paragraph you owe the mission document. It should say
what is licensed, what is not, and what would change the answer.
(d) Write the closing paragraph: what a reader who distrusts you should do first to
try to break this, and what they would find.

*(all of the above; `MISSION.md`; `curriculum/LESSON-RUBRIC.md`'s scorecard summary
and its "zero is a claim, not a result" warning)*

<details><summary>Nudge</summary>
For (d), the fastest way to break the defence is the cheapest missing number.
</details>
<details><summary>Strategy</summary>
Write part 3 before part 1. What you can license determines what you may claim, and
doing it in the other order produces a claim you then have to walk back.
</details>
<details><summary>Partial</summary>
For (b), the likeliest Gate 2 defect in a first draft is a sentence that says a
result is "stable" without naming the metric.
</details>
<details><summary>Worked start</summary>
(a) Part 1, as a model fragment. *"In the embedded trajectory data
(n = 27280 trajectories; embedding named from your cap-02 ledger, since
`03_ph.json` does not record it), the H<sub>1</sub> persistence structure of a 5000-point
maxmin landmark subsample differs from that of second-order Markov surrogates by
more than the surrogates differ from each other, measured by mean 2-Wasserstein
distance between diagrams, at the 0.05 level."* Then, immediately:
*"This claim is not established: the test reports p = 0.078."* A claim you did not
establish still belongs in part 1, stated as the claim you tested, because a defence
that only states claims that came out well is not a defence.
(b) A defect worth recording, and one every first draft contains. Somewhere in part
2 you will have written that a result is "stable" or "robust". Gate 2 asks: in which
metric, and by which theorem? If the sentence survives that question, keep it; if it
does not, the fix is to name the metric, and the sentence usually gets shorter.
Record it as a defect found and fixed, with the location — because the scorecard is
evidence about your process, not a self-assessment.
(c) The paragraph the mission document is owed. *The stability theorem this
curriculum can bring to bear is Theorem 6.3(a) with Definition 6.1: a Hausdorff
perturbation of size ε moves every Rips persistence diagram by at most ε in the
bottleneck distance, so features of persistence above 2ε survive it and features
below 2ε may not. That licenses one form of conclusion — a claim about features
above an explicit threshold — and this pipeline cannot currently state it, because
the covering radius of the landmark subsample is not recorded. It does not license
the conclusions actually drawn, which are drawn from a sum over all bars and from a
Wasserstein distance between diagrams: the first appears in no stability theorem in
the sections read, and the second is separated from the upstream bound by
Definition 13.8's sum-versus-maximum, with no inequality in the direction required.
What would change the answer: recording the covering radius, which is one line;
restating the headline claim as a threshold claim, which is a design decision; or
proving the missing inequality under extra hypotheses, which is research.* Note what
this paragraph does not do: it does not say the pipeline's conclusions are wrong. It
says which of two licences they hold.
(d) The closing paragraph. Point the sceptic at the covering radius first, because
it is the cheapest thing to check and the one that most changes the reading: compute
`max(min_dists)` at the end of `maxmin_landmarks`, and if 2ε exceeds the mean bar
length of 0.373 in H<sub>1</sub>, then the typical bar in the statistic is
unclaimable and part 3's second paragraph is the honest description of the result.
Then point them at the power question, since nothing in the directory settles it.
Then invite them to re-run with a bottleneck-stable vectorisation and see whether
the chain closes. A defence that tells a hostile reader where to start is stronger
than one that does not, because the alternative is that they find it themselves and
wonder what else is there.
</details>
