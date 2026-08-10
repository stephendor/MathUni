# cap-02 — The TDL pipeline end to end

**Module:** Capstone · **Unit:** cap-02
**Sources.** No textbook. Claims bind to three things, and every problem says
which:

1. **Theorems already proved in this curriculum**, cited to their texts. Dey &
   Wang, *Computational Topology for Data Analysis* — Definition 2.9 and
   Definition 2.10 (p. 32); Corollary 6.1 and Proposition 6.2 and the Čech–Rips
   log 2 bound (p. 180); Definition 6.1 and Definition 6.2 (p. 181);
   Definition 6.3 and Theorem 6.3 (p. 182); Definition 6.4 (pp. 183–184);
   Definition 6.5 (pp. 185–186); Theorem 6.4 (p. 186); Definition 6.6 (p. 191);
   Theorem 6.8 (p. 192); Theorem 13.1 (p. 393); Definition 13.2 (p. 393);
   Definition 13.3 and Theorem 13.2 (p. 394); Definition 13.4 and Theorem 13.3
   (p. 395); Definition 13.5 (p. 396); Definition 13.8 (p. 406). Ghrist,
   *Elementary Applied Topology* — §6.13's requirement of field coefficients and
   the p-torsion condition (pp. 131–132).
2. **Repo artifacts** — `MISSION.md`, `resources/RESOURCES.md`.
3. **tdlbook.org** — *Topological Deep Learning: Going Beyond Graph Data*, cited
   for what it is and is not; see Problem 5.

Submit your written solutions via `/grade cap-02`.

---

## Problem 1 (easy — the ledger) [interleaves cap-01]

(a) Write out the pipeline as an ordered list of stages, from raw data to
reported number. Aim for seven or eight; name the object that enters and leaves
each.
(b) For each stage, name every free parameter it introduces. Mark each as *fixed
by the data*, *fixed by a theorem*, or *chosen*.
(c) How many of your parameters are fixed by the data? Comment on the ratio, and
say what cap-01's pre-registration stub has to contain as a result.
(d) Produce the artifact: the **parameter ledger** — a table with columns Stage,
Parameter, Value, Classification, Theorem that constrains it (or "none"), Swept?

*(The stage list is the unit's own; the theorem column draws on the citations in
the header)*

<details><summary>Nudge</summary>
"The default value in the library" is a choice made by someone else, and it is
still a choice.
</details>
<details><summary>Strategy</summary>
A parameter with "none" in the theorem column is one whose effect on the
conclusion is entirely unbounded by anything you have proved.
</details>
<details><summary>Partial</summary>
Almost nothing is fixed by the data. That is the finding, not a failure of the
exercise.
</details>
<details><summary>Worked start</summary>
(a) A workable decomposition, with objects: raw observations → (1) *feature
construction*: a point set in some ambient space; (2) *metric*: a finite metric
space; (3) *embedding or dimension reduction* (optional): another finite metric
space; (4) *subsampling or sparsification*: a smaller complex or filtration;
(5) *complex and filtration*: a filtered simplicial complex; (6) *persistence*: a
diagram or barcode; (7) *summary or vectorisation*: a vector or function;
(8) *statistic and null comparison*: a number and a reference distribution.
(b) and (c) The parameters, with classification: the feature encoding (*chosen*);
the metric (*chosen*); the embedding method, its target dimension and its
hyperparameters (*chosen*); the landmark count or sparsification tolerance ε
(*chosen*, and constrained by Theorem 6.4); Čech or Rips (*chosen*, and the pair
is constrained by the multiplicative 2-interleaving with its log 2 bound); the
maximum scale (*chosen*); the coefficient field (*chosen*, and constrained by the
requirement that a field is needed at all); the homology dimensions (*chosen*);
the summary or vectorisation and its own scale parameter σ (*chosen*, and
constrained by Theorem 13.1, 13.2 or 13.3 depending which); the null type and
permutation count (*chosen*); the significance level (*chosen*). The number of
items fixed by the data is, in a typical pipeline, **zero** — the data fixes the
observations and nothing else. The consequence for cap-01's stub: every one of
those rows is a decision that must be recorded before the analysis, because
afterwards there is no way to distinguish a value chosen because it was right
from one chosen because it worked.
(d) The ledger is the artifact. Its most useful column is the last but one: a row
whose "theorem that constrains it" reads "none" is a place where the pipeline's
behaviour is bounded by nothing you have proved, and the conclusion is
conditional on that choice in a way no stability result softens.
</details>

---

## Problem 2 (easy — metric and filtration)

(a) State Definition 2.9 and Definition 2.10. Which of the two complexes is a
nerve, and of what?
(b) State Corollary 6.1 and Proposition 6.2, with their hypotheses. Then state
the relation between the Čech and Rips filtrations and the bottleneck consequence
Dey and Wang record. What does that cost you, numerically, if you choose Rips for
speed?
(c) State Definition 6.2, Definition 6.3 and Theorem 6.3, both parts. When would
you need part (b) rather than part (a)?
(d) Produce the artifact: a **metric and filtration note** stating the metric you
chose and why, whether your two point sets live in a common ambient space, which
part of Theorem 6.3 therefore applies, and the numerical cost of your Čech-versus-
Rips decision.

*(Dey §2.2, Definition 2.9 and Definition 2.10 p. 32; §6.1, Corollary 6.1 and
Proposition 6.2 and Eq. (6.3) p. 180, Definition 6.1 and Definition 6.2 p. 181,
Definition 6.3 and Theorem 6.3 p. 182)*

<details><summary>Nudge</summary>
The Gromov–Hausdorff distance is for objects that do not share an ambient space.
</details>
<details><summary>Strategy</summary>
The Čech–Rips comparison is multiplicative, so its cost appears at log scale.
</details>
<details><summary>Partial</summary>
$\mathsf{d}_b(\mathrm{Dgm}_{\log}\mathcal{C}(P), \mathrm{Dgm}_{\log}\mathcal{R}(P)) \leq \log 2$.
</details>
<details><summary>Worked start</summary>
(a) Definition 2.9: for a metric space $(M,\mathsf{d})$ and finite $P$, the Čech
complex $\mathbb{C}^r(P)$ has $\sigma = \{p_0,\dots,p_k\}$ whenever
$\bigcap_i B(p_i, r) \neq \emptyset$. Definition 2.10: the Vietoris–Rips complex
$\mathbb{VR}^r(P)$ has $\sigma$ whenever $\mathsf{d}(p,q) \leq 2r$ for every pair
of vertices of $\sigma$. The Čech complex is the nerve — of the union of balls
$P^r = \bigcup_{p \in P} B(p,r)$.
(b) Corollary 6.1: for fixed $r \geq 0$, if $B_Z(x,r)$ is convex for every
$x \in P$, then $\mathbb{C}^r(P)$ is homotopy equivalent to $P^r$ and
$\mathsf{H}_k(\mathbb{C}^r(P)) \cong \mathsf{H}_k(P^r)$ for all $k$.
Proposition 6.2: if $B(x,r)$ is convex for every $x$ and *all* $r \geq 0$, then
the persistence modules $\mathsf{H}_k\mathcal{P}$ and $\mathsf{H}_k\mathcal{C}(P)$
are isomorphic and the diagrams are equal. The Čech and Rips filtrations are
multiplicatively 2-interleaved, so their modules are $\log 2$-interleaved at log
scale and
$\mathsf{d}_b(\mathrm{Dgm}_{\log}\mathcal{C}(P), \mathrm{Dgm}_{\log}\mathcal{R}(P)) \leq \log 2$.
The numerical cost of choosing Rips: $\log 2 \approx 0.693$ at log scale — a
factor of 2 in the scale parameter. Whether that is cheap depends entirely on the
persistence of the features you intend to claim, which is why this number belongs
in the ledger next to the choice, not in a footnote.
(c) Definition 6.2: $\mathsf{d}_H(A,B) = \max\{\max_{a\in A}\mathsf{d}_Z(a,B), \max_{b\in B}\mathsf{d}_Z(b,A)\}$
for compact $A, B$ in a common $(Z, \mathsf{d}_Z)$. Definition 6.3: for metric
spaces $(X,\mathsf{d}_X)$, $(Y,\mathsf{d}_Y)$, a correspondence $C \subseteq X\times Y$
meets every point of each; its distortion is
$\frac{1}{2}\sup_{(x,y),(x',y')\in C}|\mathsf{d}_X(x,x') - \mathsf{d}_Y(y,y')|$;
and $\mathsf{d}_{GH}$ is the infimum of distortions. Theorem 6.3: (a) for finite
$P,Q$ in a common $(Z,\mathsf{d}_Z)$,
$\mathsf{d}_{\mathrm{Cech}}(P,Q) \leq \mathsf{d}_H(P,Q)$ and
$\mathsf{d}_{\mathrm{Rips}}(P,Q) \leq \mathsf{d}_H(P,Q)$; (b) for finite metric
spaces, $\mathsf{d}_{\mathrm{Cech}}(P,Q) \leq 2\mathsf{d}_{GH}$ and
$\mathsf{d}_{\mathrm{Rips}}(P,Q) \leq \mathsf{d}_{GH}$. Part (b) is what you need
when the two objects are not embedded in a common space — comparing a dataset
against a surrogate generated in a different coordinate system, or two cohorts
embedded separately. Note the factor 2 on the Čech bound in (b), which Dey and
Wang trace to the change in metric balls when the ambient space is dropped.
(d) The note is the artifact. The non-obvious row is the second: if your
surrogates are embedded independently of the observation, you are in case (b),
and the applicable bound is weaker.
</details>

---

## Problem 3 (medium — the coefficient field) [interleaves at2-08]

(a) Why must the coefficients be a field at all, for the pipeline to produce a
barcode? Cite the requirement.
(b) Ghrist records a second, numerical reason for preferring a finite field
$\mathbb{F}_p$. State it.
(c) State the p-torsion condition from Ghrist §6.13: which map's kernel is at
issue, what is assumed about it, and what that assumption buys. Under what
circumstance would the assumption fail, and would you be able to tell from the
data?
(d) Produce the artifact: a **coefficient note** stating the field used, the
reason, and — if your claim depends on lifting to integral coefficients — the
torsion assumption written out as an assumption.

*(Ghrist §6.13, the requirement of field coefficients for Theorem 5.21, the
preference for $\mathbb{F}_p$, and the short exact sequence
$0 \to \mathbb{Z} \to \mathbb{Z} \to \mathbb{F}_p \to 0$ with the p-torsion
condition, pp. 131–132)*

<details><summary>Nudge</summary>
The Structure Theorem is what turns a persistence module into a barcode.
</details>
<details><summary>Strategy</summary>
"Rare in organic spaces" is a judgement about the world, not a theorem.
</details>
<details><summary>Partial</summary>
$\ker(\cdot p) = \operatorname{im}\delta$ by exactness.
</details>
<details><summary>Worked start</summary>
(a) Ghrist states it directly in the outline of de Silva, Morozov and
Vejdemo-Johansson: "For the Structure Theorem (Theorem 5.21), field coefficients
are required". Without a field the module need not decompose into intervals, and
there is no barcode to report — so this is not a convenience but the condition
under which the output object exists.
(b) "for numerical reasons (to avoid roundoff errors), coefficients in a finite
field $\mathbb{F}_p$ are preferred". Exact arithmetic in $\mathbb{F}_p$ removes a
class of error that floating-point rank computations introduce.
(c) The short exact sequence of coefficients
$0 \to \mathbb{Z} \xrightarrow{\cdot p} \mathbb{Z} \to \mathbb{F}_p \to 0$ yields
a long exact sequence on cohomology. The map at issue is
$\cdot p : \mathsf{H}^2(X;\mathbb{Z}) \to \mathsf{H}^2(X;\mathbb{Z})$, whose
kernel consists of the $p$-torsional classes; Ghrist writes that "for $p > 2$
these would seem to be rare occurrences in *organic* spaces $X$ living behind data
sets". By exactness $\ker(\cdot p) = \operatorname{im}\delta$, and *assuming this
is zero*, the map $\mathsf{H}^1(X;\mathbb{Z}) \to \mathsf{H}^1(X;\mathbb{F}_p)$ is
surjective, so persistent classes in $\mathbb{F}_p$ coefficients lift to integral
classes. The assumption fails when the hidden space carries $p$-torsion in
$\mathsf{H}^2$. Could you tell from the data? No: the object with the torsion is
$X$, and all you have is a sample of it — the same shape of unverifiable
hypothesis as the reach in cap-01. Ghrist's own hedge, "would seem to be rare",
is a judgement about the provenance of the data, and importing it is importing an
assumption about where your data came from.
(d) The coefficient note is the artifact. If your claim never lifts to integral
coefficients, the torsion assumption is not needed and the note should say so —
half the value of writing it down is discovering which assumptions you were not
actually using.
</details>

---

## Problem 4 (medium — sparsification and its tolerance) [interleaves tda2-08]

(a) State Definition 6.4 and Definition 6.5. What does the parameter ε control,
and what is the vertex set of the sparse complex at scale α?
(b) State Theorem 6.4, both parts. Give the approximation error and the size, and
evaluate both for a concrete choice: n = 10<sup>5</sup> points in
$\mathbb{R}^3$, ε = 0.1, k = 2.
(c) State Definition 6.6 and Theorem 6.8. Which construction is more accurate for
the same ε, and by what factor? Which is simpler?
(d) Produce the artifact: a **sparsification note** giving the construction used,
the tolerance ε, the resulting log-scale error, the resulting size bound, and a
sentence saying what happens to each as ε → 0.

*(Dey §6.2.1, Definition 6.4 pp. 183–184, Definition 6.5 pp. 185–186, Theorem 6.4
p. 186; §6.2.2, Definition 6.6 p. 191, Theorem 6.8 p. 192)*

<details><summary>Nudge</summary>
Theorem 6.4(a) gives $\log(1/(1-\varepsilon))$; Theorem 6.8 gives
$3\log(1+\varepsilon)$.
</details>
<details><summary>Strategy</summary>
For (d), the two quantities move in opposite directions, and saying so is the
whole content of the note.
</details>
<details><summary>Partial</summary>
$\Theta((1/\varepsilon)^{kd}n)$ with $k = 2$, $d = 3$, $\varepsilon = 0.1$ gives a
constant of $10^{6}$.
</details>
<details><summary>Worked start</summary>
(a) Definition 6.4: for finite $P \subset (\mathbb{R}^d,\mathsf{d})$, $Q \subseteq P$
is a $(\gamma,\gamma')$-net if it is a $\gamma$-sample (covering) and
$\gamma'$-sparse (packing); a *net-tower* is a nested family
$\{N_\gamma\}$ with $N_\gamma$ a $(\gamma,\gamma/c)$-net for a fixed $c$.
Definition 6.5: with weights $w_p(\alpha)$ built from the exit-times and the
net-induced distance
$\widehat{\mathsf{d}}_\alpha(p,q) = \mathsf{d}(p,q) + w_p(\alpha) + w_q(\alpha)$,
the open sparse Rips complex is
$\mathbf{Q}^\alpha = \{\sigma \subseteq N_{\varepsilon(1-\varepsilon)\alpha} \mid \widehat{\mathsf{d}}_\alpha(p,q) \leq 2\alpha\}$,
the cumulative complex is $\mathbb{S}^\alpha = \bigcup_{\beta\leq\alpha}\overline{\mathbf{Q}}^\beta$,
and the $\varepsilon$-sparse Rips filtration is $\{\mathbb{S}^\alpha\}$. So ε
controls the resolution of the sparsification, and the vertex set at scale α is
the net $N_{\varepsilon(1-\varepsilon)\alpha}$ — it shrinks as α grows.
(b) Theorem 6.4: for fixed $0 < \varepsilon < 1/3$, (a) $\mathbb{S}(P)$ and
$\mathcal{R}(P)$ are multiplicatively $1/(1-\varepsilon)$-interleaved, so
$\mathrm{Dgm}_k\mathbb{S}(P)$ is a $\log(1/(1-\varepsilon))$-approximation of
$\mathrm{Dgm}_k\mathcal{R}(P)$ at log scale; (b) the total number of
$k$-simplices ever appearing is $\Theta((1/\varepsilon)^{kd}n)$. For
$n = 10^5$, $d = 3$, $\varepsilon = 0.1$, $k = 2$: the error is
$\log(1/0.9) \approx 0.105$ at log scale, and the size is
$\Theta(10^{6}\cdot 10^{5}) = \Theta(10^{11})$ triangles. Compare like with like:
that is a count of *triangles*, so the exact figure to set beside it is the number
of triangles in the full complex once the scale passes the diameter, which is
$\binom{n}{3} = \Theta(n^3) \approx 1.7 \times 10^{14}$ — about **three** orders of
magnitude saved before hidden constants. (Do not compare it against
$\Theta(n^{d+1}) = \Theta(10^{20})$: that is the size of the whole $d$-skeleton for
$d = 3$, dominated by tetrahedra, and setting a triangle count against it inflates
the saving by six orders of magnitude. If you want the $H_2$ computation, take
$k = 3$ on both sides.) "Linear in $n$" is true and hides a constant exponential
in $kd$.
(c) Definition 6.6: two vector space towers are *weakly $\varepsilon$-interleaved*
if the interleaving maps exist and the diagrams commute only at the discrete
indices $a_0 + i\varepsilon$. Theorem 6.8: the simplicial-tower sparsification
$3\log(1+\varepsilon)$-approximates the discrete Rips filtration at log scale,
with $O((1/\varepsilon)^{O(kd)}n)$ simplices. For $\varepsilon = 0.1$ that is
$3\log(1.1) \approx 0.286$ against Definition 6.5's $0.105$ — Definition 6.5 is
about $2.7$ times more accurate. The tower is conceptually simpler, and the factor
of $3$ is precisely the price of the weak rather than strong interleaving.
(d) The note is the artifact. Its last sentence is the important one: as
$\varepsilon \to 0$ the error $\log(1/(1-\varepsilon)) \to 0$ while the size
constant $(1/\varepsilon)^{kd} \to \infty$. There is no setting of ε that makes
both small, and choosing it is choosing a point on that trade — which is why the
ledger records the value and not merely the fact that sparsification was used.
</details>

---

## Problem 5 (hard — vectorisation, and whether the errors compose)

(a) State Definition 13.2. Then state Definition 13.3 with Theorem 13.2, and
Definition 13.4 with Theorem 13.3. Against which distance is each stability bound
stated, and what is each constant?
(b) State Theorem 13.1. Against which distance is *it* stated? Then state
Definition 13.5, and say what tda2-09 established about the availability of a
stability constant for the persistence weighted Gaussian kernel and for the
persistence Fisher kernel.
(c) Now attempt the end-to-end budget. Chain: sampling error (Theorem 6.3(a)),
sparsification error (Theorem 6.4(a)), vectorisation error (Theorem 13.2). Write
each bound with its metric and its scale. Then answer: do these compose into a
single number? Justify your answer by naming, for each junction, whether the
quantity bounded by the previous step is the quantity the next step needs.
(d) Produce the artifact: an **error budget** listing each stage, its bound, its
metric, and its scale — with a final section headed "Where this budget does not
compose", naming each junction that fails and what would be needed to close it.

*(Dey §13.1.2, Definition 13.2 p. 393, Definition 13.3 and Theorem 13.2 p. 394;
§13.1.3, Definition 13.4 and Theorem 13.3 p. 395; §13.1.1, Theorem 13.1 p. 393;
§13.1.4, Definition 13.5 p. 396; §13.3, Definition 13.8 p. 406; §6.1, Theorem 6.3
p. 182; §6.2.1, Theorem 6.4 p. 186)*

<details><summary>Nudge</summary>
Theorem 6.3 bounds a *bottleneck* distance. Theorem 13.2 needs a *1-Wasserstein*
distance.
</details>
<details><summary>Strategy</summary>
Ask, at each junction, whether the corpus you have read supplies an inequality in
the direction you need.
</details>
<details><summary>Partial</summary>
Theorem 6.4(a)'s bound is multiplicative and at log scale; Theorem 6.3's is
additive.
</details>
<details><summary>Worked start</summary>
(a) Definition 13.2, quoted as the book has it: $\mathbf{k}$ is a *positive
semidefinite kernel* if symmetric and $\sum_{i,j}a_ia_j\mathbf{k}(x_i,x_j) \geq 0$
for all $n$, all $x_i$ and all $a_i$ summing to zero; *negative semidefinite* with
the inequality reversed. Flag this as you copy it: the standard convention puts no
constraint on the $a_i$ for the *positive* case, and the $\sum_i a_i = 0$
restriction is the *conditional* notion, which belongs on the negative side. Keep
the book's wording, since it is what §13.1.2 says, but note that the RKHS
correspondence used later needs the unrestricted property — which the PSSK has, and
for the reason given on the same page: $k_\sigma$ is an inner product
$\langle \Phi_\sigma(D), \Phi_\sigma(E)\rangle$, and an inner-product kernel is
unrestrictedly positive semidefinite.
Definition 13.3: the PSSK feature map
$\Phi_\sigma(D)(x) = \frac{1}{4\pi\sigma}\sum_{y\in D}[e^{-\|x-y\|^2/4\sigma} - e^{-\|x-\bar y\|^2/4\sigma}]$
with $\bar y$ the reflection across the diagonal, inducing $k_\sigma$.
Theorem 13.2: $\|\Phi_\sigma(D) - \Phi_\sigma(E)\|_{\mathcal{L}^2(\Omega)} \leq \frac{1}{2\pi\sigma}\mathsf{d}_{W,1}(D,E)$
— against the **1-Wasserstein** distance, constant $1/(2\pi\sigma)$.
Definition 13.4: the persistence surface $\mu_D(z) = \sum_{u\in T(D)}\omega(u)\phi_u(z)$
and its pixel integrals give the persistence image. Theorem 13.3:
$\|\mathrm{I}_D - \mathrm{I}_E\|_1 \leq (\sqrt5|\nabla\omega| + \sqrt{10/\pi}\,\|\omega\|_\infty/\sigma)\,\mathsf{d}_{W,1}(D,E)$
— again **1-Wasserstein**, constant depending on $\omega$ and $\sigma$.
(b) Theorem 13.1: $\Lambda_\infty(D,D') \leq \mathsf{d}_B(D,D')$ — against the
**bottleneck** distance, constant 1. That makes landscapes the odd one out, and
the useful one for a pipeline whose upstream bound is a bottleneck bound.
Definition 13.5: the persistence weighted kernel
$K_{k,\omega}(D,E) = \sum_{x\in D;y\in E}\omega(x)\omega(y)k(x,y)$ from the
feature map $\Psi_{k,\omega}(D) = \sum_{x\in D}\omega(x)k(\cdot,x)$. What tda2-09
established: §13.1.4 states that stability results for the PWGK exist in the cited
work, with bounds depending on ω and $k_G$, and *explicitly omits* them — so no
constant is available; and §13.1.6 proves the persistence Fisher kernel is
positive definite (Corollary 13.8) and states no stability result at all. A
pipeline using either has an unquantified vectorisation stage.
(c) The three bounds, written out.
- Sampling, Theorem 6.3(a): $\mathsf{d}_{\mathrm{Rips}}(P,X) \leq \mathsf{d}_H(P,X) \leq \varepsilon_{\mathrm{samp}}$,
  where $\mathsf{d}_{\mathrm{Rips}}$ is a max over $k$ of **bottleneck** distances;
  additive, linear scale.
- Sparsification, Theorem 6.4(a): $\mathsf{d}_b(\mathrm{Dgm}_{\log}\mathbb{S}, \mathrm{Dgm}_{\log}\mathcal{R}) \leq \log(1/(1-\varepsilon_{\mathrm{sp}}))$;
  **bottleneck**, but multiplicative and at **log scale**.
- Vectorisation, Theorem 13.2: $\|\Phi_\sigma(D) - \Phi_\sigma(E)\| \leq \frac{1}{2\pi\sigma}\mathsf{d}_{W,1}(D,E)$;
  **1-Wasserstein**, additive, linear scale.
Do they compose? **No**, and at two distinct junctions.
*Junction 1, sampling into sparsification.* Both bound bottleneck distances, but
one is additive on the linear scale and the other multiplicative on the log scale.
Adding them is a category error: an additive ε and an additive $\log(1/(1-\varepsilon))$
are increments on different axes, and converting between them requires knowing
where on the scale axis the features sit. A pipeline that reports
$\varepsilon_{\mathrm{samp}} + \log(1/(1-\varepsilon_{\mathrm{sp}}))$ has added a
length to a ratio.
*Junction 2, diagrams into vectorisation.* Theorem 13.2 needs a bound on
$\mathsf{d}_{W,1}$, and what the upstream steps supply is a bound on the
bottleneck distance. Nothing in the sections this curriculum has read supplies an
inequality bounding $\mathsf{d}_{W,1}$ by $\mathsf{d}_b$ — and the general
relationship runs the other way round, since a bottleneck distance is a maximum
over matched pairs while a Wasserstein distance sums over them. So the upstream
bound does not feed the downstream theorem at all, and the composite is not merely
loose: it is unavailable.
What *can* be said: each bound holds, in its own metric, between its own pair of
objects. That is three true statements, not one. And there is a repair for
Junction 2 which the corpus does supply: use a vectorisation whose stability is
stated against the **bottleneck** distance — Theorem 13.1's landscape, with
constant 1 — in which case the upstream bottleneck bound is exactly the input the
downstream theorem wants.
(d) The error budget is the artifact, and its last section is the point of the
exercise. A pipeline reporting one end-to-end number is claiming something no
theorem in this curriculum supplies; a pipeline reporting three numbers with their
metrics is reporting what is true.
</details>
