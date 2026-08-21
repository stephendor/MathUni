# lab-05 — Bottleneck and Wasserstein distance; stability

**Module:** Computational Lab · **Unit:** lab-05
**Sources:** Oudot, *Persistence Theory: From Quiver Representations to Data
Analysis*, Chapter 3 "Stability", printed **49–66** (folio = PDF − 9).
Specifically: **Theorem 3.1** (Isometry), printed 49; the bottleneck distance and
the remark that it is an extended pseudometric, printed 51; **Definition 3.3**
(ε-interleaving), printed 52; **Lemma 3.4**, printed 56; **Corollary 3.6**,
printed 61. **Theorem 1.13** is cited by Oudot at printed 51 and lives in his
Chapter 1. Plus executed code, in the environment pinned below. API surfaces
verified by execution: `persim.bottleneck`,
`gtda.homology.VietorisRipsPersistence`.

Carried: lab-01's noisy circle and its ratio of 98.1; lab-04's diagram; an2-01's
finding, reported through tda1-06, that the bottleneck distance on diagrams in
general is an extended pseudometric.

## The environment

```env
python==3.11.11
persim==0.3.8
giotto-tda==0.6.2
numpy==1.26.4
```

```python id=env
import sys
from importlib.metadata import version
print("%-14s%s" % ("python", ".".join(str(p) for p in sys.version_info[:3])))
for dist in ("persim", "giotto-tda", "numpy"):
    print("%-14s%s" % (dist, version(dist)))

# A pin read from metadata does not load anything: importlib.metadata reads a
# .dist-info directory, so a distribution whose compiled extensions are missing
# reports its pinned version and fails later, in a block whose diff reads like a
# content error. Import what the later blocks use, at the submodule they use.
for module in ("gtda.homology", "numpy", "persim"):
    try:
        __import__(module)
        print("%-15s%s" % (module, "imports"))
    except Exception as exc:
        print("%-15s%s: %s" % (module, type(exc).__name__, exc))

# A module that imports is not an API that exists. These names are the ones
# later blocks use; importing them here means a rename or a broken subpackage
# stops the set at its environment block, not four blocks later in a diff that
# reads like a content error. This is the list the header calls "API surfaces
# verified by execution", and it is now verified rather than asserted.
from gtda.homology import VietorisRipsPersistence
```

```text id=env
python        3.11.11
persim        0.3.8
giotto-tda    0.6.2
numpy         1.26.4
gtda.homology  imports
numpy          imports
persim         imports
```

---

## Problem 1 (medium — a distance that can delete a point)

The bottleneck distance is the cost of the best *partial* matching between two
multisets: points may be matched to points, or discarded onto the diagonal, and
the cost of a matching is the **largest** cost it incurs.

(a) Compute one by hand and by machine.

```python id=matching
import numpy as np
import persim

P = np.array([[0.0, 3.0], [1.0, 1.4]])
Q = np.array([[0.2, 3.1]])
print("P has 2 points, Q has 1")
print("d_b(P, Q) = %.4f" % persim.bottleneck(P, Q))
print("cost of matching (0,3)->(0.2,3.1) in sup norm: %.4f" % 0.2)
print("cost of sending (1,1.4) to the diagonal:       %.4f" % ((1.4 - 1.0) / 2))
print("bottleneck cost is the MAX of the two:         %.4f" % max(0.2, 0.2))
```

```text id=matching
P has 2 points, Q has 1
d_b(P, Q) = 0.2000
cost of matching (0,3)->(0.2,3.1) in sup norm: 0.2000
cost of sending (1,1.4) to the diagonal:       0.2000
bottleneck cost is the MAX of the two:         0.2000
```

Explain why sending (1, 1.4) to the diagonal costs 0.2 rather than the distance
to the nearest diagonal point measured some other way, and say what feature of
the diagonal makes discarding a point legitimate at all. Then say why the answer
being the *maximum* rather than the sum matters for what the distance is
sensitive to.

(b) Oudot notes at printed 51 that "the actual choice of norm in ℝ² does not
matter fundamentally since all norms are equivalent, however the tightest bounds
in the isometry theorem are achieved using the ℓ∞-norm." Say what "does not matter
fundamentally" means precisely — which statements survive a change of norm and
which numbers do not — and connect the answer to lab-02's √2.

(c) A diagram with more points than another is not thereby further away. Give a
pair of diagrams, one with a hundred points and one with none, at bottleneck
distance 0.01, and say what that tells you about which features the distance can
see.

<details><summary>Nudge</summary>
For (a): the diagonal carries points of infinite multiplicity.
For (c): put all hundred points very close to the diagonal.
</details>
<details><summary>Partial</summary>
(a) In the ℓ∞ norm the distance from (b, d) to the diagonal is
(d − b)/2 — the nearest diagonal point is the midpoint ((b+d)/2, (b+d)/2), and the
sup-norm distance to it is half the lifetime. For (1, 1.4) that is 0.2.
Discarding is legitimate because the diagram is defined to include the diagonal
with **infinite multiplicity** (Edelsbrunner printed 181, carried from lab-03), so
a point matched to the diagonal is matched to a point genuinely present in the
other diagram. Taking the maximum rather than the sum makes the distance sensitive
to the **single worst** discrepancy and blind to how many small ones there are —
which is exactly why the Wasserstein distances exist as alternatives.

(b) Equivalence of norms means the *topology* and the qualitative statements —
that d_b is an extended pseudometric, that convergence means what it means, that
stability holds with **some** constant — survive any choice. (An extended
pseudometric, not a metric: Problem 2 is about exactly that gap, and norm
equivalence does not close it. It does carry the *repaired* statement equally
well — d_b is a genuine metric on locally finite multisets whichever norm is
used.) What does not survive is the
constant: the Isometry Theorem is an equality only in ℓ∞, and in another norm it
becomes an inequality with a factor. This is the same phenomenon as lab-02's √2,
where a containment held with a constant that depended on the geometry rather
than on the topology.

(c) Take a hundred points at (t, t + 0.02) for various t, and the empty diagram.
Every point is 0.01 from the diagonal in ℓ∞, so the matching that discards all of
them costs 0.01. The distance sees **only lifetimes**, not counts: a hundred
short-lived features are collectively as invisible as one.
</details>

---

## Problem 2 (medium — the qualification an2-01 recorded, located in the source)

an2-01 established, through tda1-06, that the bottleneck distance on diagrams in
general is an **extended pseudometric**: distinct objects at distance zero, values
in [0, ∞]. Oudot says the same at printed 51 and then says exactly when it stops
being true.

(a) Try to exhibit the pseudometric failure in the software, and watch the
attempt fail in an instructive way.

```python id=pseudometric
R = np.array([[0.0, 3.0], [1.0, 1.4], [2.0, 2.0]])
print("R is P's array with one extra row exactly on the diagonal")
print("the two arrays differ: %s" % (P.shape != R.shape))
print("d_b(P, R) = %.6f" % persim.bottleneck(P, R))
print("but Problem 1(a): every diagram contains the diagonal with infinite")
print("multiplicity, so adjoining a diagonal point changes no diagram --")
print("P and R are two arrays representing the SAME diagram")
```

```text id=pseudometric
R is P's array with one extra row exactly on the diagonal
the two arrays differ: True
d_b(P, R) = 0.000000
but Problem 1(a): every diagram contains the diagonal with infinite
multiplicity, so adjoining a diagonal point changes no diagram --
P and R are two arrays representing the SAME diagram
```

Say why this is **not** a counterexample to identity of indiscernibles, and what
it does establish about the relationship between a diagram and the array `persim`
accepts for it.

(b) So the genuine witness has to lie off the diagonal, and it is not computable
here. Oudot observes that ℚ² \ Δ and (ℚ + √2)² \ Δ are distinct
multisets at bottleneck distance zero, "the infimum in (3.2) is zero but not
attained in this case". State what goes wrong there, why part (a) does not go
wrong in the same way, and why no computation in this module can produce it.

(c) Now the repair, which is the sentence an2-02 needed and did not have. Oudot
records that a compactness argument shows the infimum **is** always attained when
P and Q are *locally finite* multisets in the extended plane minus the diagonal,
so d_b is a **true distance** for such multisets — and that by **Theorem 1.13**
these include all undecorated persistence diagrams of q-tame modules.

Write the corrected version of an2-02's claim: one sentence, saying on what class
the bottleneck distance is a genuine metric, and naming what guarantees a computed
diagram is in that class.

<details><summary>Partial</summary>
(a) Because the two arrays are not two diagrams. Under the convention of Problem
1(a) the diagonal belongs to every diagram with infinite multiplicity, so
adjoining one more diagonal point leaves the multiset off the diagonal unchanged
and hence the diagram unchanged; d_b = 0 between a thing and itself is identity of
indiscernibles **working**, not failing. What it does establish is that `persim`'s
input is a *representation*: the map from finite arrays to diagrams is not
injective, and the library is invariant along its fibres. That is a fact about the
software, and a useful one — but it says nothing about the metric.

(b) In (a) the infimum is attained by the matching that discards the extra
diagonal point, and the two diagrams were equal to begin with. In Oudot's example
the two multisets are genuinely distinct off the diagonal, infinite and dense; no
single matching achieves cost zero, but matchings of cost ε exist for every
ε > 0, so the infimum is zero and **not attained**. That is the failure of
identity of indiscernibles, and it requires a non-locally-finite diagram — which
is precisely why (a) could not produce it. No computation here can produce it
either, because every diagram this module builds is finite, and a finite multiset
is locally finite.

(c) Something of the form: *the bottleneck distance is a genuine metric on locally
finite multisets in the extended plane off the diagonal — Oudot, printed 51,
citing a compactness argument — and Theorem 1.13 puts every undecorated diagram of
a q-tame module in that class, so every diagram this module computes is in it.*
</details>

---

## Problem 3 (hard — the theorem the whole module has been deferring)

> **Theorem 3.1 (Isometry), printed 49.** Let V, W be q-tame persistence modules
> over ℝ. Then d_b(dgm(V), dgm(W)) = d_i(V, W).

Oudot calls it "the cornerstone of the theory" and splits it in two: the
**stability** part, d_b ≤ d_i, which says diagrams are stable signatures; and the
**converse stability** part, d_i ≤ d_b, which says they are *informative*. He
notes the first is "reputed to be difficult to prove" and the second "easy once
the stability part is given".

(a) Test the stability direction empirically on lab-01's circle. Perturbing every
point by at most δ changes each Vietoris–Rips filtration value by at most 2δ, so
the guarantee is d_b ≤ 2δ.

Read the two normalisation lines carefully before running it. δ has to bound each
point's **Euclidean** displacement, because that is the quantity a Rips filtration
value is built from; bounding each *coordinate* by δ permits a displacement of up
to √2 δ in the plane, and the ratio against the guarantee would then be computed
against a δ the perturbation does not satisfy.

```python id=perturb
from gtda.homology import VietorisRipsPersistence

rng = np.random.default_rng(20260813)
theta = rng.uniform(0, 2 * np.pi, 80)
X = np.c_[np.cos(theta), np.sin(theta)] + rng.normal(0, 0.06, (80, 2))

VR = VietorisRipsPersistence(homology_dimensions=[0, 1])

def h1(points):
    d = VR.fit_transform(points[None])[0]
    return d[d[:, 2] == 1][:, :2]

base = h1(X)
direction = rng.normal(0, 1, X.shape)
# Scale so the largest *row* has unit Euclidean norm: delta then bounds each
# point's displacement, which is what the Rips stability bound asks for. Scaling
# by the largest coordinate instead leaves rows of norm up to sqrt(2).
direction /= np.linalg.norm(direction, axis=1).max()

print("%-8s %-14s %-14s %-8s" % ("delta", "max shift", "d_b(H1)", "d_b / 2*delta"))
for delta in (0.01, 0.05, 0.20):
    Y = X + delta * direction
    shift = float(np.linalg.norm(Y - X, axis=1).max())
    db = float(persim.bottleneck(base, h1(Y)))
    print("%-8.2f %-14.4f %-14.6f %-8.3f" % (delta, shift, db, db / (2 * shift)))
```

```text id=perturb
delta    max shift      d_b(H1)        d_b / 2*delta
0.01     0.0100         0.005729       0.286   
0.05     0.0500         0.020832       0.208   
0.20     0.2000         0.073852       0.185
```

The observed ratios are 0.286, 0.208 and 0.185 against a guarantee of 1. Say what
that slack means and what it does **not** mean. In particular: is the theorem
loose, is this perturbation lucky, or is something else going on? Support your
answer by saying what a ratio above 1 would have implied.

(b) A green table again. Say what this experiment could genuinely have caught,
and compare with lab-03's cross-check against gudhi and lab-01's verification of
the metric axioms. Rank the three by how much was at stake.

(c) The theorem's hypothesis is **q-tame**, and its conclusion is about the
**interleaving** distance d_i between modules, not about the data. **Corollary
3.6** (printed 61) is the version that mentions functions: for q-tame f, g on X,
d_b(dgm f, dgm g) ≤ ‖f − g‖_∞. Oudot notes it is "a direct consequence of the
Isometry Theorem", and that the original statement by Cohen-Steiner, Edelsbrunner
and Harer carried extra conditions — X finitely triangulable, f and g continuous,
and a more restrictive notion of tameness — because "the authors did not have the
concept of interleaving between persistence modules" available.

Say what this history tells you about citing Corollary 3.6, and write the citation
a report should use if it is relying on the modern hypotheses rather than the
1980s-style ones.

<details><summary>Partial</summary>
(a) The slack means the **worst case did not occur**, and nothing more. The
theorem is a guarantee, not a prediction: it says no perturbation of size δ can
move the diagram by more than 2δ, and it is silent about how far any particular
one does move. This perturbation is not lucky — a single random direction is
typical, and worst cases are engineered rather than stumbled upon. A ratio above 1
would have meant something was **wrong**: a bug in the perturbation, in the
diagram computation, or in the bottleneck routine, because the theorem forbids it.

(b) At most stake was **lab-03**'s cross-check: an independent implementation of
an unproved-by-me algorithm, where disagreement was a live possibility. Next this
one: the bound is proved, so a violation would indicate a coding error rather than
a mathematical surprise — but the ratio is a real number that could have come out
anywhere in [0, 1] and the experiment is genuinely informative about how tight the
bound is in practice. Least at stake was **lab-01**'s metric-axiom check, which
could not have failed at all.

(c) It tells you the hypotheses of a named result **move over time**, and that
citing "Cohen-Steiner–Edelsbrunner–Harer stability" without a source can mean
either version. A report relying on the modern statement should cite *Oudot,
Corollary 3.6, printed 61*, and note that it is derived from the Isometry Theorem
under q-tameness, rather than citing the 2007 paper whose conditions are strictly
stronger.
</details>

---

## Problem 4 (hard — the threshold, at last)

lab-01 produced six H₁ bars, a longest of 1.2370, a runner-up of 0.0126, a ratio
of 98.1, and no way to say whether 98.1 was enough. lab-03 confirmed the reduction
supplies no threshold. This is where one arrives.

(a) Apply the guarantee. If the data is known to within δ, two datasets that
close cannot have diagrams further apart than 2δ, so a feature can be created or
destroyed by noise only if its lifetime is at most **4δ** — twice the diagram
displacement, since a bar must be moved to the diagonal.

```python id=threshold
longest = float((base[:, 1] - base[:, 0]).max())
runner_up = float(np.sort(base[:, 1] - base[:, 0])[-2])
print("longest H1 lifetime   %.4f" % longest)
print("runner-up lifetime    %.4f" % runner_up)
for delta in (0.01, 0.05, 0.20):
    guarantee = 4 * delta
    print("delta=%.2f  a bar longer than 4*delta = %.2f cannot be noise; "
          "longest survives: %s, runner-up survives: %s"
          % (delta, guarantee, longest > guarantee, runner_up > guarantee))
```

```text id=threshold
longest H1 lifetime   1.2370
runner-up lifetime    0.0126
delta=0.01  a bar longer than 4*delta = 0.04 cannot be noise; longest survives: True, runner-up survives: False
delta=0.05  a bar longer than 4*delta = 0.20 cannot be noise; longest survives: True, runner-up survives: False
delta=0.20  a bar longer than 4*delta = 0.80 cannot be noise; longest survives: True, runner-up survives: False
```

At every noise level tested the long bar clears the threshold and the runner-up
does not. Say precisely what has and has not been established — the answer is not
"the circle has one hole".

(b) The threshold depends on δ, and δ is **not** computed from the data. Say
where δ has to come from, and what a report is claiming when it states one. Then
say what happens to the conclusion if the true δ is 0.4 rather than 0.2.

(c) lab-01 asked what you would conclude if the ratio were 1.4 instead of 98.1.
Answer it now, properly, using the machinery of this unit rather than intuition.

(d) The whole chain, assembled. Write it out: from a point cloud with no topology
(lab-01), through a complex with no nerve theorem (lab-02), a reduction with no
threshold (lab-03), a diagram whose existence is a theorem (lab-04), to a
statement about the data. Name at each step the hypothesis that step needs, and
identify the single step where a modelling assumption — as opposed to a theorem —
enters.

<details><summary>Partial</summary>
(a) Established: **if** the data is accurate to δ, then no dataset within δ of
this one has an H₁ diagram in which the long feature is absent, while the
runner-up could be absent from such a dataset. Not established: that the points
were sampled from a circle, that the circle has one hole, or that the long bar
*is* that hole. Those are inferences about a space the data came from, and this
unit's theorems are about two datasets and their diagrams, never about a
generating object.

(b) δ is a claim about **measurement**, and it comes from outside — instrument
precision, a sampling model, a bound on adversarial corruption. A report stating
δ is making an empirical claim, not a mathematical one, and it is the weakest link
in the chain. At δ = 0.4 the threshold is 1.6, the longest bar is 1.2370, and
**the conclusion fails**: at that noise level even the long feature could be an
artefact.

(c) First the algebra, because the tempting answer is wrong. A δ separates the two
bars exactly when L₂ ≤ 4δ < L₁, that is when δ ∈ [L₂/4, L₁/4) — and whenever
L₁ > L₂ that window is **non-empty**. So it is false that no separating δ exists:
one always does, at any ratio above 1.

What the ratio measures is the **width of that window**, and so how much error in
δ the conclusion tolerates. Here L₁/L₂ = 98.1 and the window is [0.0032, 0.3093):
δ may be wrong by a factor approaching 98 and the verdict does not move. At a
ratio of 1.4 the window is [L₂/4, 1.4·L₂/4), a factor of 1.4 wide, so the
separation stands only if δ is known to within about 40%. Nothing in this module
supplies δ to any accuracy at all — Problem 4(b): it comes from outside — so at
1.4 the honest report is that **the conclusion is not robust to the one number
the analysis cannot check**, not that the two bars are provably indistinguishable.
The distinction matters: the first is a statement about the evidence, the second
would be a statement about the data, and only the first is supported.

(d) lab-01: a point cloud is a finite metric space (no hypothesis; and no
topology). lab-02: Rips or Čech at a scale — Čech carries the Nerve Theorem,
requiring closed convex sets; Rips carries only the sandwich, at a cost of √2.
lab-03: the reduction, requiring a monotonic filtration, giving a pairing whose
lows are unique. lab-04: the barcode exists, requiring pointwise
finite-dimensionality, free for finite complexes. lab-05: stability, requiring
q-tameness, giving d_b ≤ 2δ. **The modelling assumption enters exactly once, at
δ** — every other step is a theorem with a hypothesis the data satisfies
automatically.
</details>

---

## Problem 5 (medium — the strip)

> The stability theorem (an epsilon statement, cf. pw-04) is why TDA is
> trustworthy on noisy real data.

(a) "An epsilon statement" is right, and `pw-04` is an unwritten S1 unit. Write
the replacement citation, and say which ε in this unit is the one the strip means.

(b) "Why TDA is trustworthy on noisy real data" — audit it against Problem 4(b).
Say what the theorem does deliver, what it does not, and where the trust actually
has to be placed. Then write the corrected strip in one sentence.

<details><summary>Partial</summary>
(a) Cite Oudot's **Theorem 3.1**, printed 49, and its function-level consequence
**Corollary 3.6**, printed 61. The ε the strip means is the one bounding the
*input* perturbation — ‖f − g‖_∞, or the δ of Problem 4 — and the theorem's
content is that the *output* perturbation is bounded by it, which is the shape of
every ε-δ statement `pw-04` would have introduced.

(b) It delivers: a proved, tight, worst-case bound converting input error into
output error, with the converse direction guaranteeing the summary is not merely
stable but informative. It does not deliver: any value of ε. **Trust has to be
placed in the noise model, not in the theorem** — the theorem is unconditional and
the number it is applied with is not. A corrected strip: *stability converts a
bound on the data's error into a bound on the diagram's; supplying that bound is
the user's problem and is where the modelling risk lives.*

Note what the corrected strip does **not** say. The Isometry Theorem's equality is
between a persistence module and its diagram — d_b(dgm V, dgm W) = d_i(V, W) — so
the converse half is a statement about *modules*. The step from a point cloud to
its Rips module is no part of it, and it is not invertible: two very different
clouds can carry identical diagrams, which is why Problem 4(a) concludes nothing
about a generating object. The chain from data to diagram therefore runs in one
direction only, with a factor of 2, and a small change in a diagram licenses no
claim at all about a small change in the data.
</details>
