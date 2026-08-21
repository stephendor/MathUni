# lab-06 — Vectorising diagrams: persistence images, landscapes, Betti curves

**Module:** Computational Lab · **Unit:** lab-06
**Sources:** Dey and Wang, *Computational Topology for Data Analysis*, Chapter 13
"Topological Persistence and Machine Learning", §13.1 "Feature Vectorization of
Persistence Diagrams", printed **390–395** (folio = PDF − 21). Specifically:
**Definition 13.1** (persistence landscape), printed 391; the mean landscape and
**Claim 13.1**, printed 392; **Theorem 13.1** (Λ∞ ≤ d_B), printed 393;
**Definition 13.4** (persistence image), printed 395; **Theorem 13.3** (image
stability), printed 395. Plus executed code, in the environment pinned below. API
surfaces verified by execution: `persim.PersistenceImager`, `persim.bottleneck`,
`persim.landscapes.PersLandscapeExact`, `persim.landscapes.PersistenceLandscaper`,
`persim.wasserstein`, `gtda.diagrams.BettiCurve`.

Carried: lab-05's bottleneck distance and its 4δ threshold; lab-05's finding that
δ is the one place a modelling assumption enters; an2-07's record that a kernel
needs an inner product and that diagram space has none.

**A source-boundary note before anything else.** The syllabus resource line for
this unit names `giotto-tda: diagram vectorisation` and `scikit-tda persim` and no
book. Dey and Wang ch. 13 is on disk and defines every object in this unit, states
two of its three stability theorems, and names the papers the third would come
from. It is used here as the primary source and the divergence is recorded for the
syllabus pass.

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
for module in ("gtda.diagrams", "numpy", "persim", "persim.landscapes"):
    try:
        __import__(module)
        print("%-19s%s" % (module, "imports"))
    except Exception as exc:
        print("%-19s%s: %s" % (module, type(exc).__name__, exc))

# A module that imports is not an API that exists. These are the names later
# blocks reach for; importing them here means a rename or a broken subpackage
# stops the set at its environment block, not four blocks later in a diff that
# reads like a content error. This is the list the header calls "API surfaces
# verified by execution", and it is now verified rather than asserted.
#
# Inside a function on purpose: the blocks share one namespace, so binding
# names like `abs` or `round` at the top level here would shadow the builtins
# for every block that follows.
def _api_surface():
    from gtda.diagrams import BettiCurve
    from numpy import abs, allclose, array, array_equal, asarray, concatenate, linspace, maximum, minimum, ones_like, pi, round, sort, zeros
    from persim import PersistenceImager, bottleneck, wasserstein
    from persim.landscapes import PersLandscapeExact, PersistenceLandscaper

_api_surface()
```

```text id=env
python        3.11.11
persim        0.3.8
giotto-tda    0.6.2
numpy         1.26.4
gtda.diagrams      imports
numpy              imports
persim             imports
persim.landscapes  imports
```

---

## Problem 1 (medium — why the question exists at all)

Dey and Wang open §13.1 by saying that diagram space "lacks (e.g., inner product)
structure, which can pose challenges when used within a machine learning
framework" (printed 390). lab-05 gave that space a metric. A metric is not enough
to average with.

(a) Exhibit the failure directly: a pair of diagrams with three distinct
midpoints.

```python id=midpoints
import numpy as np
import persim

X = np.array([[0.0, 4.0]])
Y = np.array([[0.0, 4.0], [1.0, 3.0]])
print("X = {(0,4)};  Y = {(0,4), (1,3)}")
print("d_b(X, Y) = %.4f   (the cost of discarding (1,3))" % persim.bottleneck(X, Y))
print()
print("%-34s %-12s %-12s" % ("candidate midpoint M", "d_b(X, M)", "d_b(Y, M)"))
for name, M in (("{(0,4), (1.5,2.5)}", np.array([[0.0, 4.0], [1.5, 2.5]])),
                ("{(0.5,3.5), (1.5,2.5)}", np.array([[0.5, 3.5], [1.5, 2.5]])),
                ("{(-0.5,4.5), (1.5,2.5)}", np.array([[-0.5, 4.5], [1.5, 2.5]]))):
    print("%-34s %-12.4f %-12.4f" % (name, persim.bottleneck(X, M),
                                     persim.bottleneck(Y, M)))
```

```text id=midpoints
X = {(0,4)};  Y = {(0,4), (1,3)}
d_b(X, Y) = 1.0000   (the cost of discarding (1,3))

candidate midpoint M               d_b(X, M)    d_b(Y, M)   
{(0,4), (1.5,2.5)}                 0.5000       0.5000      
{(0.5,3.5), (1.5,2.5)}             0.5000       0.5000      
{(-0.5,4.5), (1.5,2.5)}            0.5000       0.5000      
```

Three distinct multisets sit exactly halfway between X and Y in the bottleneck
distance. Say what this rules out — be precise about which structure fails, and
distinguish it carefully from the pseudometric failure lab-05 exhibited. Those are
two different defects and only one of them is repaired by restricting to locally
finite diagrams.

(b) Verify by hand that each of the three is a midpoint, and then show that the
list is not exhaustive by producing a fourth.

(c) Say why "just take coordinatewise means of the points" is not a repair, using
X and Y themselves.

<details><summary>Nudge</summary>
For (a): in a normed space, how many *metric* midpoints does a pair of points
have? Careful — the answer depends on the norm, and (ℝ², ℓ∞) is the example to
try before answering.
For (c): how many points would the mean have?
</details>
<details><summary>Partial</summary>
(a) It rules out **any isometric embedding of diagram space into a strictly convex
normed space** — and the qualifier is not a technicality, it is the whole content.

The tempting answer is "into any normed space, because the midpoint of x and y is
(x + y)/2 and that is unique". The *algebraic* midpoint is unique in every normed
space. The *metric* midpoints — the points m with ‖x − m‖ = ‖y − m‖ = ‖x − y‖/2 —
need not be. In (ℝ², ℓ∞) take x = (−1, 0) and y = (1, 0), at distance 2: every
m = (0, t) with |t| ≤ 1 has ‖x − m‖ = ‖y − m‖ = max(1, |t|) = 1, so the whole
segment consists of midpoints. Uniqueness of metric midpoints is exactly **strict
convexity** of the unit ball, and ℓ∞ has not got it.

So branching geodesics obstruct embedding into strictly convex spaces: every
Hilbert space, and every L^p for 1 &lt; p &lt; ∞. They obstruct nothing about ℓ∞
or L¹ — which is unsurprising, since d_b is itself built from a sup norm.

**That is the class the useful norms sit in.** Vectorising means arriving in ℝ^N,
and what makes ℝ^N useful is a norm supporting means, inner products and
gradients — the ℓ² one, which is strictly convex. The three midpoints say that no
such landing can be *isometric*: **the distances must be distorted**, and the rest
of the unit is about measuring how much.

Two things that is **not**. It is not a claim that the vectorisation loses
*information* — the two are independent, and Problem 2 exhibits the separation:
by **Claim 13.1** the exact landscape map is injective, so it loses nothing at
all, and by **Theorem 13.1** it is 1-Lipschitz and not an isometry. Injective,
lossless, and distorting. Where this unit's methods do lose information is at a
different step — the **discretisation** onto a finite grid, which Problem 2(d)
measures — and conflating the two hides the fact that one is a theorem about
target geometry and the other is a resolution setting you choose.

And it is not a claim about every norm in this unit. ℓ¹ and ℓ∞ are not strictly
convex and the obstruction says nothing about them — unsurprising, since d_b is
itself built from a sup norm. Problem 3 measures ‖I_D − I_E‖₁, so the unit uses
one of the exempt norms in the very next problem. The trade is real and it is
specific: the obstruction bites exactly where the inner product lives.

This is **not** the pseudometric failure of lab-05: there the defect was two
distinct diagrams at distance *zero*, and restricting to locally finite multisets
repairs it. Here the distances are all genuinely positive and the diagrams
genuinely distinct; restricting the class does not help, because the branching is
a property of the sup-norm partial-matching cost itself.

(b) Each M matches (0,4) to its first point at sup-norm cost 0.5 or 0, and
discards or matches (1.5,2.5) at cost 0.5; and (1.5,2.5) is at sup-norm distance
0.5 from (1,3). A fourth: {(0,4), (1.5,2.5), (7.0, 7.5)} — the extra point has
lifetime 0.5 and so costs 0.25 to discard against either diagram, which does not
raise the maximum.

(c) X has one point and Y has two, so there is no coordinatewise mean to take:
the operation is not even defined until you have chosen a matching, and choosing
the matching is the whole problem. Three of them are optimal here.
</details>

---

## Problem 2 (medium — the landscape, and what it is made of)

> **Definition 13.1 (Persistence landscape), printed 391.** Given a finite
> persistence diagram D = {(bᵢ, dᵢ)}, the persistence landscape with respect to D
> is a function λ_D : ℕ × ℝ → ℝ where λ_D(k, t) := k-th largest value of
> [min{t − bᵢ, dᵢ − t}]₊ for i ∈ [1, n].

(a) Build one and read its structure off.

```python id=landscape
from persim.landscapes import PersLandscapeExact, PersistenceLandscaper

D = np.array([[0.0, 3.0], [0.5, 2.0], [1.0, 1.4]])
exact = PersLandscapeExact(dgms=[D], hom_deg=0)
print("critical pairs, layer by layer:")
for k, layer in enumerate(exact.critical_pairs):
    print("  layer %d  %s" % (k, [[round(x, 4) for x in pt] for pt in layer]))
print()
print("%-8s %-14s %-14s" % ("layer", "peak height", "half lifetime"))
lifetimes = np.sort(D[:, 1] - D[:, 0])[::-1]
for k, layer in enumerate(exact.critical_pairs):
    peak = max(pt[1] for pt in layer)
    print("%-8d %-14.4f %-14.4f" % (k, peak, lifetimes[k] / 2))

sampled = PersistenceLandscaper(hom_deg=0, start=0.0, stop=3.0,
                                num_steps=11, flatten=False)
V = np.asarray(sampled.fit_transform([D]))
print()
print("sampled on 11 points of [0, 3], shape %s:" % (V.shape,))
print(V)
```

```text id=landscape
critical pairs, layer by layer:
  layer 0  [[0.0, 0], [1.5, 1.5], [3.0, 0]]
  layer 1  [[0.5, 0], [1.25, 0.75], [2.0, 0]]
  layer 2  [[1.0, 0], [1.2, 0.2], [1.4, 0]]

layer    peak height    half lifetime 
0        1.5000         1.5000        
1        0.7500         0.7500        
2        0.2000         0.2000        

sampled on 11 points of [0, 3], shape (3, 11):
[[0.  0.3 0.6 0.9 1.2 1.5 1.2 0.9 0.6 0.3 0. ]
 [0.  0.  0.  0.3 0.6 0.6 0.3 0.  0.  0.  0. ]
 [0.  0.  0.  0.  0.3 0.  0.  0.  0.  0.  0. ]]
```

Layer k peaks at exactly half the k-th longest lifetime. Show that this is forced
by Definition 13.1 for **this** diagram, then find the hypothesis your argument
used and construct a diagram where the identity fails. (It does fail. The three
bars here are nested, which is not general.)

(b) Connect the y-axis to lab-05. lab-05's threshold was: a bar of lifetime L
survives noise of size δ if L > 4δ. Rewrite that as a statement about the
landscape's peak heights, and say what the rewritten form makes visible that the
barcode form did not. Then decide one thing carefully: can the *number* of bars
passing the test be read off the picture? Check whatever you answer against the
disjoint diagram from part (a).

(c) **Claim 13.1** (printed 392) says that from λ_D one can uniquely recover D — the
map is injective and lossless. Immediately afterwards Dey and Wang observe that "a
function λ : ℕ × ℝ → ℝ may not be the image of any valid persistence diagram. For
example, the mean landscape introduced above may not be the image of any
persistence diagram."

Those two sentences together are the whole trade. State it: what does vectorising
buy, what does it cost, and why is Problem 1 the reason anyone pays.

<details><summary>Partial</summary>
(a) For nested bars — b₁ ≤ b₂ ≤ … and d₁ ≥ d₂ ≥ … — the tent of bar i dominates
the tent of bar i+1 everywhere the latter is positive, so the k-th largest value
at any t is the k-th bar's tent, and the k-th layer *is* the k-th tent, peaking at
half its lifetime. The hypothesis is **nesting**. It fails for disjoint bars:
D = {(0,1), (10,11)} has two bars, but λ_D(2, ·) ≡ 0 because no t lies inside
both, so layer 1 has peak 0 while half the second lifetime is 0.5.

(b) A bar of lifetime L contributes a tent of peak L/2, so "L > 4δ" is
"**peak height > 2δ**" — a single horizontal line drawn across the landscape at
height 2δ.

What that buys is that the test becomes a statement about a *function* rather than
a pass over a list. Some bar is guaranteed exactly when ‖λ_D‖_∞ > 2δ, and that is
an inequality in the vector space Problem 3 works in — available to the arithmetic
that Problem 1 showed diagram space cannot support.

What it does **not** buy is the **count**, and this is the tempting misreading.
The number of layers crossing the line is not the number of qualifying bars: it is
the largest number of qualifying tents that are simultaneously positive at some
*common* parameter value — an overlap statistic, and only ever a lower bound on
the count. Part (a)'s diagram is the counterexample already in hand.
D = {(0,1), (10,11)} has two bars of equal lifetime, so for any 2δ < 0.5 both pass
the test, while λ_D(2, ·) ≡ 0 and exactly one layer ever crosses the line.

The two numbers agree under **nesting**, which is the same hypothesis (a) needed
and for the same reason: nesting is what makes layer k the k-th bar's tent. Off
that hypothesis the landscape answers "is anything guaranteed" and the barcode is
still where you go to answer "how many".

(c) It buys **arithmetic** — a linear space where means, variances, inner products
and every machine-learning primitive are defined, which Problem 1 shows diagram
space cannot supply. It costs **membership**: the results of that arithmetic
generally leave the image of the map. The mean of two landscapes is a perfectly
good element of ℒᵖ and is generally not the landscape of any diagram, so it cannot
be read back as a topological summary of anything. Claim 13.1 says nothing is lost
in the forward direction; it does not say the target is closed under the
operations you went there to perform.
</details>

---

## Problem 3 (hard — a theorem, and the object it is about)

> **Theorem 13.1, printed 393.** For persistence diagrams D and D′,
> Λ∞(D, D′) ≤ d_B(D, D′).

(a) Test it twice: once against the exact landscape of Definition 13.1, and once
against the finite vector a pipeline would actually consume.

```python id=lipschitz
def landscape_exact(dgm, t, layers):
    """Layer k of the landscape at t: the k-th largest tent value."""
    tents = np.maximum(np.minimum(t[:, None] - dgm[:, 0], dgm[:, 1] - t[:, None]), 0.0)
    tents = -np.sort(-tents, axis=1)
    out = np.zeros((layers, t.size))
    out[:tents.shape[1]] = tents.T[:layers]
    return out

base = np.array([[0.0, 3.0], [0.5, 2.0], [1.0, 1.4], [1.2, 1.5]])
pert = np.array([[-0.0167, 2.9597], [0.4889, 2.0219],
                 [0.9597, 1.3762], [1.2194, 1.4532]])
db = float(persim.bottleneck(base, pert))

grid = np.linspace(-0.5, 3.5, 400001)
A = landscape_exact(base, grid, 4)
B = landscape_exact(pert, grid, 4)
sup_exact = float(np.abs(A - B).max())

L = PersistenceLandscaper(hom_deg=0, start=0.0, stop=3.5,
                          num_steps=71, flatten=False)
a = np.asarray(L.fit_transform([base]))
b = np.asarray(L.fit_transform([pert]))
sup_sampled = float(np.abs(a - b).max())

print("d_b(base, pert)                      %.6f" % db)
print("sup norm of exact landscapes         %.6f   ratio %.4f" % (sup_exact, sup_exact / db))
print("sup norm of the sampled vectors      %.6f   ratio %.4f" % (sup_sampled, sup_sampled / db))
```

```text id=lipschitz
d_b(base, pert)                      0.046800
sup norm of exact landscapes         0.046800   ratio 1.0000
sup norm of the sampled vectors      0.050000   ratio 1.0684
```

The exact landscape achieves the bound with equality — ratio 1.0000, so the
theorem is **tight** on this pair. The sampled vector reports 1.0684, which the
theorem forbids.

Diagnose it. Say precisely what object Theorem 13.1 is a statement about, what
object the second number was computed from, and why the discrepancy is not a
counterexample. Then predict what happens to the 1.0684 as `num_steps` grows, and
say what it does **not** converge to.

(b) The exact ratio came out at exactly 1.0000, not merely below 1. Say what that
means about this particular pair, and whether a ratio of exactly 1 is evidence for
or against the code being correct. Compare with lab-05's ratios of 0.286, 0.208
and 0.185, where the slack was the point.

(c) Generalise the defect. Every vectorisation in this unit ends in a finite
vector obtained by evaluating a function on a grid. Name the property a
discretisation would need for the theorem to transfer to the vector, and say
whether "use a fine enough grid" is a repair or a mitigation.

<details><summary>Nudge</summary>
For (a): Definition 13.1 defines λ_D as a function on ℕ × ℝ, not a list of numbers.
</details>
<details><summary>Partial</summary>
(a) Theorem 13.1 bounds Λ∞ — the sup norm of the difference of two **functions**
λ_D and λ_D′ on ℕ × ℝ. The second number is the max over 71 sample points of the
difference of two **vectors** that `PersistenceLandscaper` produced, and those
entries are not exact evaluations of λ: the library returns values on its own
grid, which is why 1.4097 is reported as 1.4. The discrepancy is a
**discretisation artefact**, not a counterexample, and the giveaway is that the
excess (0.0032) is of the order of the grid spacing (0.05) rather than of the
signal. As `num_steps` grows the excess shrinks with the spacing and the ratio
approaches 1 from either side — it does **not** approach it monotonically, and the
vector never becomes the object the theorem is about.

(b) It means the optimal matching's worst-moved point is a point whose tent
attains its full displacement somewhere the layer is unobstructed — the bound has
no slack to give on this pair. A ratio of exactly 1 is **evidence for**
correctness, not against: the theorem permits it, and hitting a sharp bound
exactly is a much stronger consistency check than landing somewhere below it,
because an arbitrary bug lands below or above and almost never on. lab-05's slack
was the point there because the question was how tight the guarantee is in
practice; here the question is whether the implementation computes the object the
theorem is about, and equality answers it.

(c) You would need the discretisation to be **1-Lipschitz as a map from the
function to the vector** in the relevant norms — that is, sampling must not
increase the distance between two functions. Grid evaluation of continuous
functions has this property; grid *snapping* of values, which is what happened
here, does not. "Use a fine enough grid" is a **mitigation**: it bounds the excess
by the spacing, which is a real and quantifiable guarantee, but it does not make
the vector satisfy the theorem, and any report claiming Theorem 13.1 for a
computed feature vector is claiming something the computation does not establish.
</details>

---

## Problem 4 (hard — the hypothesis that is in the prose and not in the theorem)

> **Definition 13.4 (Persistence image), printed 395.** Let ω : ℝ² → ℝ be a
> nonnegative weight function for ℝ². Given a persistence diagram D, its
> *persistence surface* μ_D (w.r.t. ω) is μ_D(z) := Σ_{u ∈ T(D)} ω(u) φ_u(z).
>
> **Theorem 13.3, printed 395.** Suppose persistence images are computed with the
> normalized Gaussian distribution with variance σ² and weight function
> ω : ℝ² → ℝ. Then the persistence images are stable with respect to the
> 1-Wasserstein distance … ‖I_D − I_E‖₁ ≤ (√5 |∇ω| + √(10/π) ‖ω‖_∞ / σ) · d_{W,1}(D, E).

Read the hypotheses. The theorem as printed asks that ω be nonnegative, with a
bounded gradient and a bounded sup norm. It asks **nothing** about ω near the
diagonal. Between Definition 13.4 and the theorem, Dey and Wang remark that "a
natural choice of ω(u) could be the persistence |b − d| of point u = (b, d)" —
which is a weight that vanishes on the diagonal, offered as a recommendation.

(a) Take the theorem at its word and instantiate it with ω ≡ 1, which satisfies
every hypothesis printed: nonnegative, ‖ω‖_∞ = 1, |∇ω| = 0.

```python id=image
def constant_weight(birth, pers):
    """omega = 1 everywhere: bounded, zero gradient, and NOT zero on the diagonal."""
    return np.ones_like(np.asarray(pers, dtype=float))

def image(dgm, weight, params):
    imgr = persim.PersistenceImager(birth_range=(0.0, 2.0), pers_range=(0.0, 2.0),
                                    pixel_size=0.25, weight=weight,
                                    weight_params=params)
    return imgr.transform([dgm])[0]

# Dey Theorem 13.3, printed 395, with sigma = 1 (persim's default covariance):
#   ||I_D - I_E||_1 <= ( sqrt(5)|grad w| + sqrt(10/pi) ||w||_inf / sigma ) d_W1(D, E)
C_PERS = 5 ** 0.5 * 1.0 + (10 / np.pi) ** 0.5 * 2.0 / 1.0   # w = persistence on [0,2]
C_CONST = 5 ** 0.5 * 0.0 + (10 / np.pi) ** 0.5 * 1.0 / 1.0  # w = 1
print("Theorem 13.3 coefficient, omega = persistence : %.4f" % C_PERS)
print("Theorem 13.3 coefficient, omega = 1           : %.4f" % C_CONST)
print()

# Before testing printed constants, check that the distance on the right-hand
# side is the one the theorem means. Dey and Wang's Definition 3.10, printed 75,
# defines d_{W,q} with the ELL_q ground metric, so d_{W,1} measures matching cost
# in ell_1. persim.wasserstein uses the Euclidean ground metric and offers no way
# to change it. For one point at (b, b+eps) sent to the diagonal these differ by
# sqrt(2) -- eps against eps/sqrt(2) -- which is small, and is exactly the size of
# mistake that turns a factor-of-300 discrepancy into an argument nobody trusts.
def dw1(D):
    """d_{W,1}(D, empty) under the theorem's ell_1 ground metric.

    Every point must be matched to the diagonal, so the matching is forced and a
    point (b, d) costs min_t |b - t| + |d - t| = d - b. That is the whole
    computation for the diagrams below; no general matcher is implemented, and
    none would be correct to use without stating its ground metric either.
    """
    return float((D[:, 1] - D[:, 0]).sum())

empty = np.zeros((0, 2))
print("ground metric check, one point of lifetime eps against the empty diagram")
print("%-9s %-14s %-14s %-14s" % ("lifetime", "persim (l2)", "theorem (l1)", "ratio"))
for eps in (0.4, 0.02, 0.0008):
    D = np.array([[1.0, 1.0 + eps]])
    print("%-9.4f %-14.6f %-14.6f %-14.6f"
          % (eps, float(persim.wasserstein(D, empty)), dw1(D),
             dw1(D) / float(persim.wasserstein(D, empty))))
print()

print("%-9s %-10s %-11s %-11s %-11s %-11s" % (
    "lifetime", "d_W1", "L1 w=pers", "bound", "L1 w=1", "bound"))
for eps in (0.4, 0.1, 0.02, 0.004, 0.0008):
    D = np.array([[1.0, 1.0 + eps]])
    w1 = dw1(D)
    a = float(np.abs(image(D, "persistence", {"n": 1.0})
                     - image(empty, "persistence", {"n": 1.0})).sum())
    b = float(np.abs(image(D, constant_weight, {})
                     - image(empty, constant_weight, {})).sum())
    print("%-9.4f %-10.6f %-11.6f %-11.6f %-11.6f %-11.6f"
          % (eps, w1, a, C_PERS * w1, b, C_CONST * w1))
```

```text id=image
Theorem 13.3 coefficient, omega = persistence : 5.8043
Theorem 13.3 coefficient, omega = 1           : 1.7841

ground metric check, one point of lifetime eps against the empty diagram
lifetime  persim (l2)    theorem (l1)   ratio         
0.4000    0.282843       0.400000       1.414214      
0.0200    0.014142       0.020000       1.414214      
0.0008    0.000566       0.000800       1.414214      

lifetime  d_W1       L1 w=pers   bound       L1 w=1      bound      
0.4000    0.400000   0.164015    2.321726    0.410039    0.713650   
0.1000    0.100000   0.034893    0.580432    0.348930    0.178412   
0.0200    0.020000   0.006610    0.116086    0.330508    0.035682   
0.0040    0.004000   0.001307    0.023217    0.326755    0.007136   
0.0008    0.000800   0.000261    0.004643    0.326002    0.001427   
```

The first table is a convention check and it is not decoration. `persim.wasserstein`
computes the matching in the **Euclidean** ground metric; **Definition 3.10, printed
75**, defines d_{W,q} with the **ℓ_q** one, so the d_{W,1} in Theorem 13.3 is an ℓ¹
matching cost. For a point sent to the diagonal the two differ by exactly √2. Had
the library's number been used, every bound column below would have been quoted
√2 too small against a theorem stated in a different distance — and the argument
in (b) is that a *printed theorem* is wrong, which is not an argument to make while
an unchecked factor of 1.41 is sitting in the right-hand side.

With ω = persistence the L1 difference tracks d_{W,1} down and stays a factor of
ten inside the bound. With ω ≡ 1 it **plateaus at 0.326** while the bound falls
away — an excess factor growing without limit as the lifetime shrinks.

Explain the mechanism in one paragraph: what is the image of a diagram with one
point of lifetime 0.0008 under ω ≡ 1, what is the image of the empty diagram, and
why does their difference not shrink.

(b) Something has to give. Either the computation is wrong, or the theorem as
printed is. Argue for one, and — this is the part that matters — say what you can
and cannot establish about **Adams et al. [4]**, the paper Dey and Wang cite the
result to and which is not on disk here.

(c) Write the hypothesis that repairs the printed statement, in the weakest form
that still rules out ω ≡ 1. Then say what it costs: name a feature of a diagram
that a diagonal-vanishing weight is guaranteed to under-report, and connect it to
lab-05's finding about what the bottleneck distance can see.

(d) `persim.PersistenceImager`'s default is `weight='persistence'` with
`weight_params={'n': 1.0}`. Say what that default is doing for the user, whether
the right word for it is "default" or "hypothesis", and what a report should
therefore state alongside any persistence image it publishes.

<details><summary>Nudge</summary>
For (a): the Gaussian bump is placed at T(b, d) = (b, d − b), and its total mass
does not depend on where it sits.
</details>
<details><summary>Partial</summary>
(a) Under ω ≡ 1, a single point of any lifetime whatever contributes a full
unit-mass Gaussian bump to the surface, centred at (1, 0.0008) after the skew
T(b,d) = (b, d−b). The empty diagram's image is identically zero. So the L1
difference is the mass of one whole bump inside the window — about 0.326 — and it
is **independent of the lifetime**, because moving a bump towards the diagonal
does not shrink it. Meanwhile d_{W,1} → 0. A ratio of two quantities, one fixed
and one going to zero, is unbounded.

(b) The computation is right and the theorem as printed is false. The argument:
the mechanism in (a) is elementary and does not depend on persim at all — any
implementation of Definition 13.4 with ω ≡ 1 has it, because Definition 13.4 puts
the full weight ω(u) on every point regardless of position. What can be
established about [4]: **nothing, from here.** The paper is not on disk. It can be
recorded that Dey and Wang attribute the result to it, that they state a special
case, and that their prose recommends a weight the theorem does not require —
which is consistent with the missing hypothesis living in [4] and being dropped in
transit, but that is an inference about a document not read, and it must be
written as one.

(c) Weakest sufficient repair: **ω is continuous and ω(b, 0) = 0 for all b** —
that is, ω vanishes on the diagonal (in the skewed coordinates, on the horizontal
axis). Then a point of lifetime L contributes mass ω → 0 as L → 0, and the two
diagrams' images converge. The cost: a diagonal-vanishing weight is guaranteed to
**under-report short bars**, and in the limit to ignore them entirely — so a
dataset whose signal lives in the *number* of short-lived features is invisible to
a persistence image, exactly as it was invisible to the bottleneck distance in
lab-05. The same repair produces the same blindness in both places, and that is
not a coincidence: stability with respect to a distance that cannot see short bars
requires a summary that cannot see them either.

(d) The default supplies the missing hypothesis silently. `weight='persistence'`
with n = 1.0 is ω(b, p) = p, which vanishes linearly on the diagonal — so out of
the box the user gets a stable image, and never learns that the stability came
from the default rather than from the construction. The library's word is
"default"; the mathematical word is **hypothesis**. A report should state the
weight function and its behaviour at the diagonal alongside σ and the pixel grid,
on the grounds established in lab-01 and lab-02: a library default is part of the
citation, and this one is load-bearing.
</details>

---

## Problem 5 (medium — a second default, doing something quieter)

Same object, a different way of getting it wrong.

```python id=skew
D = np.array([[0.0, 3.0], [1.0, 1.4], [0.5, 0.9]])
imgr = persim.PersistenceImager(pixel_size=0.5)
print("bare defaults, before fit: %r" % imgr)
imgr.fit([D])
print("after fit on a birth-death diagram:")
print("  birth_range %s  pers_range %s  resolution %s"
      % (imgr.birth_range, tuple(round(v, 4) for v in imgr.pers_range), imgr.resolution))
skewed = imgr.transform([D])[0]
raw = imgr.transform([D], skew=False)[0]
print("  transform(D)              sum %.6f   (skew=True, the default)" % skewed.sum())
print("  transform(D, skew=False)  sum %.6f" % raw.sum())
print("  the two images agree: %s" % np.allclose(skewed, raw))
```

```text id=skew
bare defaults, before fit: PersistenceImager(birth_range=(0.0, 1.0), pers_range=(0.0, 1.0), pixel_size=0.5, weight=persistence, weight_params={'n': 1.0}, kernel=gaussian, kernel_params={'sigma': [[1.0, 0.0], [0.0, 1.0]]})
after fit on a birth-death diagram:
  birth_range (0.0, 1.0)  pers_range (0.2, 3.2)  resolution (2, 6)
  transform(D)              sum 0.757641   (skew=True, the default)
  transform(D, skew=False)  sum 1.253836
  the two images agree: False
```

(a) `pers_range` is a persistence range, not a death range: the transformer works
in the (birth, persistence) coordinates that Definition 13.4 calls T(D), and
`skew=True` is what applies T. Say what happens to a user who has already
converted their diagram to birth–persistence and then calls `transform` with the
default, and say whether any error is raised.

(b) Both images above are legitimate images of *something*. Say what each one is
the image of, and give the one-sentence rule that decides which call is correct.

(c) The bare defaults are `birth_range=(0,1)`, `pers_range=(0,1)` and a
`pixel_size` the constructor was given. After `fit` on this diagram the resolution
is 2 × 6. Say what would have happened had `fit` been skipped, and what that
implies about comparing two persistence images computed in different scripts.

<details><summary>Partial</summary>
(a) The skew is applied a second time: (b, p) becomes (b, p − b). No error is
raised — the values are finite and the shapes are right, so every downstream check
passes and the image is silently of a diagram that does not exist. Points with
p < b acquire negative persistence and land outside `pers_range`, where they are
simply not accumulated, so features are lost rather than misplaced.

(b) `transform(D)` is the image of D as a birth–death diagram, which is what D is.
`transform(D, skew=False)` is the image of D interpreted as already lying in
birth–persistence coordinates — that is, the image of the diagram with points
(0,3), (1,1.4), (0.5,0.9) read as (birth, persistence), i.e. bars of lifetime 3,
1.4 and 0.9 starting at 0, 1 and 0.5. The rule: **skew iff the second coordinate
of your array is a death time.**

(c) The image would have been computed on the default window
[0,1] × [0,1], and the bar of persistence 3.0 would have fallen entirely outside
it. (3.0 is the bar; 3.2 is the *padded upper end* of `pers_range` after `fit`,
which is a property of the fitted grid and not of any point of D.) The implication is that a persistence image is **not comparable across
scripts** unless the grid is stated: two images of the same diagram with different
`birth_range`, `pers_range` or `pixel_size` are vectors in different spaces, and
two images fitted on different collections are vectors in different spaces even
when the code is identical. Problem 6 makes that concrete.
</details>

---

## Problem 6 (hard — the vectoriser is fitted, and the third summary is not stable at all)

The Betti curve is the simplest vectorisation there is: β(t) is the number of bars
alive at t. Dey and Wang's §13.1 does not treat it.

```python id=betti
from gtda.diagrams import BettiCurve

one = np.array([[[0.0, 1.0, 0], [0.0, 3.0, 1]]])
pair = np.array([[[0.0, 1.0, 0], [0.0, 3.0, 1]],
                 [[0.0, 1.0, 0], [0.0, 9.0, 1]]])
alone = BettiCurve(n_bins=10)
va = alone.fit_transform(one)
together = BettiCurve(n_bins=10)
vb = together.fit_transform(pair)
print("the SAME H1 diagram, vectorised twice")
print("  fitted alone,   grid %s" % np.round(alone.samplings_[1], 4))
print("  fitted alone,   vector %s" % va[0][1].astype(int))
print("  fitted in pair, grid %s" % np.round(together.samplings_[1], 4))
print("  fitted in pair, vector %s" % vb[0][1].astype(int))
print("  identical: %s" % np.array_equal(va[0][1], vb[0][1]))
print()
print("%-10s %-10s %-16s" % ("lifetime", "d_b", "sup |beta diff|"))
for eps in (0.50, 0.10, 0.02):
    D = np.array([[[1.0, 1.0 + eps, 0]]])
    E = np.array([[[1.0, 1.0, 0]]])
    out = BettiCurve(n_bins=100).fit_transform(np.concatenate([D, E]))
    db = float(persim.bottleneck(np.array([[1.0, 1.0 + eps]]), np.zeros((0, 2))))
    print("%-10.2f %-10.4f %-16.1f" % (eps, db, np.abs(out[0] - out[1]).max()))
```

```text id=betti
the SAME H1 diagram, vectorised twice
  fitted alone,   grid [0.     0.3333 0.6667 1.     1.3333 1.6667 2.     2.3333 2.6667 3.    ]
  fitted alone,   vector [1 1 1 1 1 1 1 1 1 0]
  fitted in pair, grid [0. 1. 2. 3. 4. 5. 6. 7. 8. 9.]
  fitted in pair, vector [1 1 1 0 0 0 0 0 0 0]
  identical: False

lifetime   d_b        sup |beta diff| 
0.50       0.2500     1.0             
0.10       0.0500     1.0             
0.02       0.0100     1.0             
```

(a) The first half. One diagram, two vectors, differing in six of ten
coordinates — and nothing was random, nothing was wrong, and no warning was
emitted. Explain exactly what `fit` computed and why the two calls computed
different things. Then say what this forbids you from doing with a train/test
split, and state the rule it forces.

(b) The second half. As the lifetime shrinks by a factor of 25, d_b shrinks by 25
and the sup-norm difference between the two Betti curves does not move at all.
Show that the ratio is unbounded — no computation, three lines — and conclude what
is true of the Betti curve that is false of the landscape.

(c) A Betti curve is a genuinely useful feature and is used constantly. Reconcile
that with (b): say what weaker guarantee a Betti curve does satisfy, name the norm
in which it satisfies it, and state the one thing a report using Betti curves must
not claim.

(d) Assemble the unit. Three vectorisations, three verdicts, one pattern. State
the pattern in a sentence, and then say which of the three you would use for
lab-01's noisy circle and why.

<details><summary>Nudge</summary>
For (b): consider the empty diagram and {(t, t+ε)} and let ε → 0.
For (c): "not Lipschitz in the sup norm" and "not stable in any norm" are
different claims. Try L¹.
</details>
<details><summary>Partial</summary>
(a) `fit` computed the **sampling grid**, from the range of filtration values
present in the collection it was shown. Alone, the H₁ values run to 3 and the grid
spans [0, 3]; in the pair, the second diagram reaches 9 and the grid spans [0, 9],
so the same curve is now sampled at ten points, nine of which are past its death.
The vector is a property of the diagram *and the batch*. What it forbids:
**fitting the vectoriser on the whole dataset before splitting.** Doing so lets
the test set's filtration range set the grid the training vectors are computed on,
which is leakage — of exactly the quiet kind that shows up as an optimistic score
and no error. The rule: fit on training data only, and carry the fitted
transformer to the test data. That is lab-07's subject and it is why the
transformer has a `fit` at all.

(b) Let D_ε = {(t, t+ε)} and E = ∅. Then d_b(D_ε, E) = ε/2 → 0. But β_{D_ε} = 1 on
(t, t+ε) and β_E ≡ 0, so ‖β_{D_ε} − β_E‖_∞ = 1 for every ε > 0. Hence the ratio
‖β_D − β_E‖_∞ / d_b(D, E) = 2/ε → ∞. There is no constant C with
‖β_D − β_E‖_∞ ≤ C · d_b(D, E). The landscape satisfies exactly that inequality with
C = 1 (Theorem 13.1); the Betti curve satisfies it with no C at all.

(c) It satisfies an **L¹** bound: ‖β_D − β_E‖₁ is the total area between the
curves, and moving a point to the diagonal removes area equal to its lifetime, so
the L¹ distance is controlled by the 1-Wasserstein distance rather than the
bottleneck. The failure in (b) is specifically a sup-norm failure: a thin spike of
height 1 has small area and large height. What a report must not claim: that its
Betti-curve features **inherit the stability theorem** — they do not inherit
Theorem 13.1, and a claim of the form "our features are stable because persistence
is stable" is false for this feature.

(d) The pattern: **each vectorisation trades away a different piece of the
guarantee, and none of the three announces it.** The landscape keeps the bound
exactly and loses it again at the discretisation; the image keeps it only under a
hypothesis supplied by a library default; the Betti curve does not have it in the
sup norm at all. For lab-01's circle the landscape is the choice: the question
there was whether one bar stands above the rest, that is precisely a statement
about λ(1, ·)'s peak against 2δ, and it is the only one of the three whose
guarantee is a theorem in the source rather than a default or an absence.
</details>
