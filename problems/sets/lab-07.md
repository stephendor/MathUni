# lab-07 — TDA in machine-learning pipelines

**Module:** Computational Lab · **Unit:** lab-07
**Sources:** Dey and Wang, *Computational Topology for Data Analysis*, Chapter 13,
§13.3 "Statistical Treatment of Topological Summaries", printed **405–407**
(folio = PDF − 21, verified in lab-06). Specifically: **Definition 13.8**
((p, q)-Wasserstein distance), printed 406; **Definition 13.9** (the space of
persistence diagrams 𝔻ᵖ_q), printed 406; **Definition 13.10** (Fréchet function,
variance, expectation), printed 406; **Theorem 13.10** (the Fréchet mean set is
non-empty), printed 407, together with the remarks on that page that the Fréchet
mean is in general not unique and that its computation "remains open". Plus
executed code, in the environment pinned below. API surfaces verified by
execution: `gtda.pipeline.Pipeline`, `gtda.homology.VietorisRipsPersistence`,
`gtda.diagrams.Amplitude`, `gtda.diagrams.NumberOfPoints`,
`gtda.diagrams.BettiCurve`, `gtda.diagrams.PersistenceLandscape`,
`sklearn.pipeline.Pipeline`, `sklearn.feature_selection.SelectKBest`,
`sklearn.model_selection.cross_val_score`.

Carried: lab-06's finding that `BettiCurve`'s vector depends on the batch it was
fitted in, and the rule that forced — fit on training data only; lab-06's
Theorem 13.1, which is what the landscape amplitude feature inherits; lab-05's δ.

**Two source-boundary notes before anything else.**

1. The syllabus resource line names `giotto-tda: Pipeline API` and
   `scikit-learn Pipeline docs` and no book. Dey and Wang §13.3 is on disk and is
   the only source in this programme that says what a "mean" of topological
   summaries even is. It is used as a primary source and the divergence is
   recorded for the syllabus pass, alongside the identical finding for `lab-06`.
2. **This unit was drafted against a broken environment, and gate 9 said
   `pins verified` the whole time.** The first draft's classifier was
   `RandomForestClassifier`, and `import sklearn.ensemble` failed:
   `ModuleNotFoundError: No module named 'sklearn.ensemble._gradient_boosting'`.
   `sklearn/ensemble/` held its Python sources and **none** of its compiled
   extensions, while 55 were present elsewhere in the package; `igraph._igraph`
   was missing too, and several `.dist-info` directories had no `RECORD` file —
   the signature of an incomplete install. Throughout,
   `importlib.metadata.version("scikit-learn")` returned `"1.3.2"` and gate 9
   passed, because it compares metadata strings and imports nothing.
   Re-running the lockfile's own documented rebuild —
   `uv pip install --reinstall -r resources/lab-requirements.txt` — repaired
   every package and changed no version. **The lockfile was correct; the
   environment was not, and no check could tell them apart.** Gate 9 then caught
   the repair, failing this set's `env` block because the recorded output no
   longer matched — the gate working, in the opposite direction, on a difference
   that mattered. `LogisticRegression` is kept, on determinism grounds. **The
   convention this produces: a lab `env` block should import the specific modules
   its later blocks use**, so that a broken subpackage shows up as a gate-9 diff
   rather than as a green run. This set's `env` block does; `lab-01` to `lab-06`
   predate the rule.

## The environment

```env
python==3.11.11
giotto-tda==0.6.2
scikit-learn==1.3.2
numpy==1.26.4
```

```python id=env
import sys
from importlib.metadata import version
print("%-18s%s" % ("python", ".".join(str(p) for p in sys.version_info[:3])))
for dist in ("giotto-tda", "scikit-learn", "numpy"):
    print("%-18s%s" % (dist, version(dist)))

# A pin read from metadata does not load anything: importlib.metadata reads a
# .dist-info directory, so a distribution whose compiled extensions are missing
# reports its pinned version and fails later, in a block whose diff reads like a
# content error. Import what the later blocks use, at the submodule they use.
for module in ("gtda.diagrams", "gtda.homology", "gtda.pipeline", "numpy",
               "sklearn.feature_selection", "sklearn.linear_model",
               "sklearn.model_selection", "sklearn.pipeline",
               "sklearn.preprocessing"):
    try:
        __import__(module)
        print("%-27s%s" % (module, "imports"))
    except Exception as exc:
        print("%-27s%s: %s" % (module, type(exc).__name__, exc))

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
    from gtda.diagrams import Amplitude, BettiCurve, NumberOfPoints, PersistenceLandscape
    from gtda.homology import VietorisRipsPersistence
    from gtda.pipeline import Pipeline
    from numpy import array, bincount, c_, cos, cov, linalg, mean, pi, random, round, sin, sort, sqrt, vstack
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import Pipeline, make_union
    from sklearn.preprocessing import FunctionTransformer

_api_surface()
```

```text id=env
python            3.11.11
giotto-tda        0.6.2
scikit-learn      1.3.2
numpy             1.26.4
gtda.diagrams              imports
gtda.homology              imports
gtda.pipeline              imports
numpy                      imports
sklearn.feature_selection  imports
sklearn.linear_model       imports
sklearn.model_selection    imports
sklearn.pipeline           imports
sklearn.preprocessing      imports
```

---

## Problem 1 (medium — the score that proves nothing)

A classification task with an obvious topological answer: one circle against two
circles. If persistent homology is good for anything it is good for this.

```python id=data
import warnings
# Narrow, not blanket -- and "narrow" has to mean the message, not the category.
# Three warnings are expected here and are noise: scipy's L-BFGS-B deprecation
# notice (raised once per LogisticRegression fit, ~230 times), and the divide
# warnings f_classif raises on constant columns. Anything else still prints,
# which is the point of naming them; silencing DeprecationWarning as a class
# would also silence the next API removal, in a set whose whole claim is that
# its recorded output came from the pinned versions.
warnings.filterwarnings("ignore", category=DeprecationWarning,
                        message=r"scipy\.optimize: The .disp. and .iprint. options")
warnings.filterwarnings("ignore", category=RuntimeWarning,
                        message="invalid value encountered")
warnings.filterwarnings("ignore", category=RuntimeWarning,
                        message="divide by zero encountered")
warnings.filterwarnings("ignore", category=UserWarning,
                        message=r"Features \[.*\] are constant")
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold

SEED = 20260820

def make_clouds(n_each=30, n_pts=60, noise=0.06):
    """Class 0: one circle of radius 1. Class 1: two circles of radius 0.5."""
    rng = np.random.default_rng(SEED)
    clouds, labels = [], []
    for _ in range(n_each):
        th = rng.uniform(0, 2 * np.pi, n_pts)
        clouds.append(np.c_[np.cos(th), np.sin(th)] + rng.normal(0, noise, (n_pts, 2)))
        labels.append(0)
    for _ in range(n_each):
        th = rng.uniform(0, 2 * np.pi, n_pts)
        h = n_pts // 2
        left = np.c_[0.5 * np.cos(th[:h]) - 0.55, 0.5 * np.sin(th[:h])]
        right = np.c_[0.5 * np.cos(th[h:]) + 0.55, 0.5 * np.sin(th[h:])]
        clouds.append(np.vstack([left, right]) + rng.normal(0, noise, (n_pts, 2)))
        labels.append(1)
    return np.array(clouds), np.array(labels)

def moment_features(clouds):
    """Six numbers per cloud, and not one of them topological."""
    return np.c_[clouds.mean(1), np.array([np.cov(c.T).ravel() for c in clouds])]

CV = StratifiedKFold(5, shuffle=True, random_state=0)
def classifier():
    return LogisticRegression(max_iter=5000, random_state=0)

X, y = make_clouds()
print("clouds %s   labels %s" % (X.shape, np.bincount(y)))
B = moment_features(X)
print("moment features %s" % (B.shape,))
print("their spread across samples: %s" % np.round(B.std(0), 6))
print("moment baseline, 5-fold CV accuracy: %.4f"
      % cross_val_score(classifier(), B, y, cv=CV).mean())
```

```text id=data
clouds (60, 60, 2)   labels [30 30]
moment features (60, 6)
their spread across samples: [0.065202 0.069208 0.070125 0.035879 0.035879 0.184615]
moment baseline, 5-fold CV accuracy: 1.0000
```

Six numbers — two coordinate means and four covariance entries, containing no
topology whatever — separate the classes perfectly.

(a) Say what went wrong with the experimental design, and be specific: name the
property of the two generators that the baseline is exploiting, and point to the
entry of the spread vector that gives it away.

(b) The topological pipeline in Problem 3 scores 0.9333 on this same data. Say
what that number would have licensed you to claim if the baseline had not been
run, and what it actually licenses. Then state the general rule this is an
instance of.

(c) This is the same structural idea as a construction that has appeared twice
already in the lab module — once as a thing gate 9 does, once as a thing gate 2
has and gate 7 does not. Name it, and say why an analysis needs one as much as a
gate does.

<details><summary>Nudge</summary>
For (a): the two-circle clouds span [−1.05, 1.05]; the one-circle clouds span
[−1, 1].
</details>
<details><summary>Partial</summary>
(a) The two classes differ in **scale as well as in topology**, and nothing in the
construction prevented that. A one-circle cloud has radius 1; two circles of
radius 0.5 with centres at ±0.55 span ±1.05 horizontally and only ±0.5
vertically, so the covariance is strongly anisotropic where the circle's is
isotropic. The giveaway is the last entry of the spread vector, 0.184615 — the
y-variance term — running about **three times** the two mean terms (2.83 and 2.67
times 0.065202 and 0.069208) and five times the smallest entry. The confound is
geometric, it is large, and it was introduced by accident.

(b) Without the baseline, 0.9333 would have read as "persistent homology
distinguishes one hole from two". With the baseline, it reads as "some feature of
these clouds distinguishes the classes, and the topological pipeline extracts it
less well than six moments do". The rule: **a classification score is a claim
about a procedure, not about the features the procedure happens to use.**
Attributing it to topology requires showing that a non-topological alternative
does worse, which here it does not.

(c) A **negative control**. Gate 9's second run against the first is one; gate 2's
`selftest` is one; gate 7 has none, which is why it can be skipped without trace.
An analysis needs one for exactly the reason a gate does: a procedure that cannot
be observed to fail supplies no evidence when it passes. The baseline is the
negative control for "topology did the work", and the label permutation in
Problem 5 is the negative control for "the protocol is honest".
</details>

---

## Problem 2 (medium — controlling the confound, provably)

The repair is not to hunt for a better classifier. It is to remove the confound at
the source, and to be able to demonstrate that it is gone.

```python id=whiten
def whiten(clouds):
    """Centre each cloud and set its covariance to the identity. Affine, so H1 survives."""
    out = []
    for c in clouds:
        c = c - c.mean(0)
        w, V = np.linalg.eigh(np.cov(c.T))
        out.append(c @ (V / np.sqrt(w)) @ V.T)
    return np.array(out)

Xw = whiten(X)
Bw = moment_features(Xw)
print("moment features of the whitened clouds, spread: %s" % np.round(Bw.std(0), 6))
print("moment baseline on whitened clouds, 5-fold CV:  %.4f"
      % cross_val_score(classifier(), Bw, y, cv=CV).mean())
```

```text id=whiten
moment features of the whitened clouds, spread: [0. 0. 0. 0. 0. 0.]
moment baseline on whitened clouds, 5-fold CV:  0.5000
```

Every moment feature is now **identically constant across all sixty clouds** —
spread exactly zero, not approximately zero — and the baseline scores exactly
chance.

That settles the confound. It does not settle whether the repair damaged the thing
being measured, and the temptation is to argue that it cannot: an affine map is a
homeomorphism of the plane, homotopy type is a homeomorphism invariant, so one
loop stays one loop. **That argument is about the underlying space, and a Rips
filtration of sixty points is not the underlying space** — which is what lab-01
and lab-02 spent their length establishing. Anisotropic rescaling moves every
distance by a different factor, so which edges enter at which scale changes, and
nothing licenses transferring an invariance of the continuum to the sample. So
measure it:

```python id=whitencheck
from gtda.homology import VietorisRipsPersistence as VRP

def dominant_counts(clouds):
    """Bars longer than half the longest. A crude fixed rule, applied identically."""
    counts = []
    for d in VRP(homology_dimensions=[0, 1]).fit_transform(clouds):
        h1 = d[d[:, 2] == 1]
        life = np.sort(h1[:, 1] - h1[:, 0])[::-1]
        counts.append(0 if len(life) == 0 or life[0] == 0
                      else int((life > 0.5 * life[0]).sum()))
    return np.array(counts)

def longest(clouds):
    out = []
    for d in VRP(homology_dimensions=[0, 1]).fit_transform(clouds):
        h1 = d[d[:, 2] == 1]
        out.append(float((h1[:, 1] - h1[:, 0]).max()) if len(h1) else 0.0)
    return np.array(out)

raw_counts, wht_counts = dominant_counts(X), dominant_counts(Xw)
print("%-10s %-22s %-22s" % ("", "class 0 (one circle)", "class 1 (two circles)"))
for name, counts in (("raw", raw_counts), ("whitened", wht_counts)):
    print("%-10s %-22.3f %-22.3f"
          % (name, counts[y == 0].mean(), counts[y == 1].mean()))
print("clouds whose dominant-bar count changed: %d of %d"
      % (int((raw_counts != wht_counts).sum()), len(y)))
print("longest H1 lifetime, mean: raw %.4f -> whitened %.4f"
      % (longest(X).mean(), longest(Xw).mean()))
```

```text id=whitencheck
           class 0 (one circle)   class 1 (two circles)
raw        1.000                  1.933
whitened   1.000                  1.867
clouds whose dominant-bar count changed: 4 of 60
longest H1 lifetime, mean: raw 0.7651 -> whitened 1.1289
```

**The repair is not free.** Four of sixty clouds change their dominant-bar count,
and the mean longest lifetime moves by nearly 50%. Whitening trades a large
measured confound for a smaller measured perturbation of the signal — which is a
good trade, and is a trade, and is not the theorem the homeomorphism argument
seemed to promise.

(a) Explain why "spread exactly 0.000000" is a much stronger statement than
"baseline CV = 0.5000", and say which of the two you would put in a report.

(b) Whitening applies a different affine map to every cloud. The homeomorphism
argument above says the topological question is untouched; the table says four
clouds disagree. Locate the gap precisely: name the level at which the invariance
genuinely holds — the space, the complex, or the filtration — and say what would
have to be true of the *sample* for it to transfer, and why nothing in this module
establishes that.

(c) The whitening is itself computed from each cloud. Say whether that is
leakage, and give the criterion that decides such questions in general.

<details><summary>Partial</summary>
(a) "Spread exactly zero" is a statement about the **features**: no function
whatever of these six numbers can distinguish the classes, because the six numbers
are the same for every sample. "CV = 0.5000" is a statement about **one
classifier's performance**, which a different classifier might improve on. The
first rules out a whole family of alternative explanations; the second rules out
one. Report the first — and note that it also explains the second, since a
logistic regression on constant inputs predicts the majority class and 5-fold
stratified CV on balanced classes puts that at 0.5 exactly.

(b) The invariance holds **at the level of the space**, and nowhere lower. A
homeomorphism of the plane preserves the homotopy type of a union of balls of
*fixed* radius only if it preserves those balls, and an anisotropic affine map
does not: it takes balls to ellipses. At the level of the **filtration** the map
is straightforwardly destructive — every distance is scaled by a factor depending
on direction, so every birth and death moves, and the mean longest lifetime here
moves from 0.7651 to 1.1289.

For the invariance to transfer to the sample you would need the Rips complex at
the relevant scales to be determined by the underlying space rather than by the
sixty points — some sampling condition guaranteeing the complex recovers the
space's homotopy type both before and after, stably enough that the anisotropy
cannot break it. Such conditions exist in the literature and **this module has
established none of them**; lab-02's Nerve Theorem discussion is precisely the
record of not having one. So the correct status of the whitening step is
*empirically checked control*, not *provably topology-preserving transformation*,
and the four changed clouds are what that distinction costs.

It would be worse for a question about a specific lifetime, and lab-05's 4δ
threshold is such a question — whitening invalidates any δ measured before it.

(c) It is **not** leakage, because it uses only the cloud it is applied to and no
label and no other sample. The criterion: a transformation is safe if it can be
applied to a single test sample in isolation, knowing nothing about the training
set or the labels. `whiten` passes; `BettiCurve.fit` on a collection fails it,
which is Problem 3.
</details>

---

## Problem 3 (hard — the pipeline as an object, and why the transformer is a step)

```python id=pipeline
from gtda.homology import VietorisRipsPersistence
from gtda.diagrams import Amplitude, NumberOfPoints, BettiCurve
from gtda.pipeline import Pipeline
from sklearn.pipeline import make_union

def topological_pipeline():
    return Pipeline([
        ("rips", VietorisRipsPersistence(homology_dimensions=[0, 1])),
        ("features", make_union(Amplitude(metric="landscape"), NumberOfPoints())),
        ("clf", classifier()),
    ])

print("topological pipeline on the RAW clouds,      5-fold CV: %.4f"
      % cross_val_score(topological_pipeline(), X, y, cv=CV).mean())
print("topological pipeline on the WHITENED clouds, 5-fold CV: %.4f"
      % cross_val_score(topological_pipeline(), Xw, y, cv=CV).mean())
print()
diagrams = VietorisRipsPersistence(homology_dimensions=[0, 1]).fit_transform(Xw)
print("what a transformer inside the pipeline is refitted on, fold by fold:")
print("  %-6s %-9s %-16s" % ("fold", "n train", "H1 grid upper end"))
for k, (train, _) in enumerate(CV.split(Xw, y)):
    bc = BettiCurve(n_bins=100).fit(diagrams[train])
    print("  %-6d %-9d %-16.6f" % (k, len(train), bc.samplings_[1][-1]))
```

```text id=pipeline
topological pipeline on the RAW clouds,      5-fold CV: 0.9333
topological pipeline on the WHITENED clouds, 5-fold CV: 0.9500

what a transformer inside the pipeline is refitted on, fold by fold:
  fold   n train   H1 grid upper end
  0      48        2.334698        
  1      48        2.371028        
  2      48        2.371028        
  3      48        2.371028        
  4      48        2.371028        
```

(a) On whitened clouds the topological pipeline scores 0.9500 against a baseline
that is provably at chance. Say what that pair of numbers licenses that Problem
1's pair did not, and — carefully — what it still does not license.

(b) The fold table is lab-06's finding, relocated. Fold 0's grid ends at 2.334698
and the other four end at 2.371028. Explain what happened in fold 0, why the
difference is *desirable* rather than a nuisance, and what would have gone wrong
had the grid been fixed once on all sixty diagrams.

(c) The feature is `Amplitude(metric='landscape')`. lab-06 established Theorem
13.1: the landscape map is 1-Lipschitz from the bottleneck distance. State
precisely what this pipeline's features do and do not inherit from that theorem,
in three clauses — one about the diagram-to-landscape step, one about the
landscape-to-number step, and one about the classifier.

(d) `VietorisRipsPersistence` is also a pipeline step, and it has no `fit`
worth speaking of — it computes each diagram from its own cloud. Say why it
belongs inside the pipeline anyway, and name the two things you would lose by
precomputing the diagrams once and cross-validating from there.

<details><summary>Nudge</summary>
For (b): 48 of the 60 diagrams, and the grid's upper end is the largest filtration
value among them.
</details>
<details><summary>Partial</summary>
(a) It licenses: **these classes are separated by a feature that survives
whitening, and the six-moment family provably does not separate them.** That is a
real and useful statement, and it is about this dataset and this feature set. It
does not license "persistent homology recovers the number of holes" — the
pipeline could be reading the number of H₁ points rather than anything about
loops, and `NumberOfPoints` is literally one of its two features. Nor does it
license anything about a different dataset: the classes here were constructed to
differ topologically, and a classifier scoring 0.95 on constructed data is
evidence about the construction.

(b) Fold 0's training half happened to exclude whichever diagram carries the
largest H₁ death, so its grid stops at 2.334698. That is exactly right: the
transformer is being fitted on the training half only, so the test samples in fold
0 are vectorised on a grid that knows nothing about them. Had the grid been fixed
once on all sixty, every training vector in every fold would have been computed on
a grid whose upper end was set by a diagram in some test set — a quantity the
model is not supposed to have seen. The score would be optimistic and no error
would be raised.

(c) (i) Diagram to landscape: **inherits Theorem 13.1 exactly**, up to the
discretisation caveat lab-06 established — the sampled landscape is not the
function. (ii) Landscape to number: `Amplitude` takes a norm of the landscape,
and a norm is 1-Lipschitz for its own metric, so the feature is stable —
**provided the norm is the one Theorem 13.1 bounds**, which for the sup norm it
is and for others requires the Λ_p results Dey and Wang point to but do not state.
(iii) Classifier: **inherits nothing.** Logistic regression is Lipschitz in its
inputs with a constant depending on the fitted coefficients, which are not
bounded a priori, so no stability statement transfers to the predicted label.
Stability of features is not stability of decisions.

(d) Because `cross_val_score` must be able to clone and refit the *whole*
procedure on each fold, and because a later step might depend on a homology
parameter you want to tune. Precomputing loses (i) the ability to put
`homology_dimensions` or `max_edge_length` into a grid search without leaking the
selection across folds, and (ii) the guarantee that the reported score refers to
the procedure you would actually run on new data — which is the only thing a
cross-validated score is *for*.
</details>

---

## Problem 4 (medium — what "the mean" means, and why nobody computes it)

lab-06 showed that two diagrams can have three midpoints. Dey and Wang §13.3
addresses the general question.

> **Definition 13.10 (Fréchet function, variance, and expectation), printed 406.**
> Given a probability distribution ρ on 𝒟, its Fréchet function is
> ℱ_ρ(X) := ∫ d²(X, Y) dρ(Y). The Fréchet variance is inf_X ℱ_ρ(X), and the set at
> which it is attained is the Fréchet expectation, or Fréchet mean set.
>
> **Theorem 13.10, printed 407.** Let ρ be a probability measure on 𝒟 with a
> finite second moment. If ρ has compact support, then 𝔼(ρ) ≠ ∅.

Dey and Wang add, on the same page, that "in general, the Fréchet mean is not
unique", and that "the computational question for Fréchet mean … remains open".

```python id=mean
from gtda.diagrams import PersistenceLandscape

landscapes = PersistenceLandscape(n_layers=2, n_bins=60).fit_transform(diagrams)
print("landscape tensor %s  (samples, dimensions x layers, bins)" % (landscapes.shape,))
mean0 = landscapes[y == 0].mean(0)
mean1 = landscapes[y == 1].mean(0)
print("mean landscape of class 0, H1 layer 0, peak %.6f" % mean0[2].max())
print("mean landscape of class 1, H1 layer 0, peak %.6f" % mean1[2].max())
print("mean landscape of class 0, H1 layer 1, peak %.6f" % mean0[3].max())
print("mean landscape of class 1, H1 layer 1, peak %.6f" % mean1[3].max())
print("separation in H1 layer 1 peaks: %.6f" % abs(mean0[3].max() - mean1[3].max()))
```

```text id=mean
landscape tensor (60, 4, 60)  (samples, dimensions x layers, bins)
mean landscape of class 0, H1 layer 0, peak 0.722392
mean landscape of class 1, H1 layer 0, peak 0.282571
mean landscape of class 0, H1 layer 1, peak 0.000000
mean landscape of class 1, H1 layer 1, peak 0.148169
separation in H1 layer 1 peaks: 0.148169
```

(a) Class 0's mean second layer peaks at **exactly zero**; class 1's does not.
Say what that single number is measuring, and connect it to lab-06's reading of
what layer k is.

(b) Theorem 13.10 guarantees a Fréchet mean **set** is non-empty, under
compactness and a finite second moment. The averaging above took four lines and
no hypotheses at all. Say what the difference is between the two objects, and why
the second is available when the first is "open".

(c) So state the trade in its final form. Dey and Wang give the theory of means in
diagram space and record that it is not computable; every pipeline in this unit
averages in a vector space instead. What is given up, and where in a report should
it be said?

<details><summary>Partial</summary>
(a) Layer 1 of a landscape is the **second** upper envelope, and it is non-zero
only at values of t where at least two bars are simultaneously alive. A single
circle produces one long H₁ bar, so its second layer is identically zero and
averaging thirty of them gives exactly zero. Two circles produce two, which
overlap, so the second layer is positive. The number 0.148169 is therefore a
direct measurement of "there are two loops, and they coexist" — the cleanest
topological reading in the module, obtained by averaging.

(b) The Fréchet mean is an element **of diagram space** minimising a sum of
squared diagram distances. The mean landscape is an element **of a linear function
space** obtained by pointwise averaging. The second is available because the
target is a vector space, where the average is a one-line formula with no
optimisation and no existence question; the first requires minimising over an
infinite-dimensional non-linear metric space whose geodesics branch, which is
exactly what lab-06's three midpoints showed. Theorem 13.10 says a minimiser
exists; it does not say it is unique — the same page says it is not — and it gives
no way to find one.

(c) Given up: **the answer is no longer a diagram**. The mean landscape is a
legitimate element of ℒᵖ and is generally the landscape of no persistence diagram
(lab-06, Dey and Wang printed 392), so it cannot be interpreted as "the typical
topology of this class". It can be compared, classified and tested; it cannot be
read back as a barcode. That belongs in the methods section, in one sentence, next
to the statement of which vectorisation was used — because a reader who sees "mean
persistence landscape" and pictures an average barcode has been misled by the
name and not by anything false.
</details>

---

## Problem 5 (hard — the negative control for the protocol)

Problem 1's baseline was the negative control for "topology did the work". This is
the negative control for "the number I am reporting is real". It is the same
device gate 9 uses on itself.

```python id=leak
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.preprocessing import FunctionTransformer

K = 3

def curve_steps():
    """BettiCurve as a pipeline STEP, so its grid is refitted per training fold.

    Problem 3's table puts BettiCurve.fit inside the loop, because its sampling
    grid is derived from the whole collection it sees. Materialising the feature
    matrix once, outside, would contradict the rule this unit teaches.
    """
    return [("betti", BettiCurve(n_bins=500)),
            ("flat", FunctionTransformer(lambda a: a.reshape(len(a), -1)))]

def fully_honest(labels):
    """Grid and selection both refitted on each fold's training half."""
    pipe = SklearnPipeline(curve_steps() + [
        ("select", SelectKBest(f_classif, k=K)), ("clf", classifier())])
    return cross_val_score(pipe, diagrams, labels, cv=CV).mean()

# Fitted once on all 60 diagrams -- transductive, but it never sees a label.
curves = SklearnPipeline(curve_steps()).fit_transform(diagrams)

def grid_outside(labels):
    """Grid fitted on everything; selection still refitted per fold."""
    pipe = SklearnPipeline([("select", SelectKBest(f_classif, k=K)), ("clf", classifier())])
    return cross_val_score(pipe, curves, labels, cv=CV).mean()

def labels_outside(labels):
    """Selection fitted on every label there is, then cross-validate the rest."""
    chosen = SelectKBest(f_classif, k=K).fit(curves, labels)
    return cross_val_score(classifier(), chosen.transform(curves), labels, cv=CV).mean()

rng = np.random.default_rng(7)
permutations = [rng.permutation(y) for _ in range(20)]

print("Betti-curve feature matrix: %s   (%d samples, %d features)"
      % (curves.shape, curves.shape[0], curves.shape[1]))
print()
print("%-42s %-14s %-10s %-10s" % ("procedure", "real labels", "perm mean", "perm max"))
for name, procedure in (("everything inside the CV loop", fully_honest),
                        ("grid fitted on all samples, no labels", grid_outside),
                        ("grid and selection fitted on all labels", labels_outside)):
    scores = [procedure(p) for p in permutations]
    print("%-42s %-14.4f %-10.4f %-10.4f"
          % (name, procedure(y), np.mean(scores), max(scores)))
```

```text id=leak
Betti-curve feature matrix: (60, 1000)   (60 samples, 1000 features)

procedure                                  real labels    perm mean  perm max
everything inside the CV loop              0.9833         0.5108     0.6333
grid fitted on all samples, no labels      0.9833         0.5117     0.6333
grid and selection fitted on all labels    1.0000         0.6242     0.7167
```

Three rows, because there are two different ways to step outside the loop and
they are not equally bad. Row 1 refits everything per fold. Row 2 fits the
Betti-curve grid once on all sixty diagrams — transductive, since a test fold
influences the grid used on its own training fold, but the grid never sees a
label. Row 3 additionally fits the feature selection on every label there is.

(a) Compare rows 1 and 2 first, then rows 2 and 3. Explain the mechanism in each
case: with 1000 features and 60 samples, what does selecting the best 3 against
all the labels accomplish that fitting a *grid* on all the samples does not, and
why does cross-validation afterwards fail to catch either?

(b) State, as a single criterion, what makes a step "inside the loop" material.
Then classify each of these: whitening each cloud; `VietorisRipsPersistence`;
`BettiCurve.fit`; `SelectKBest`; choosing `n_bins` after looking at a
cross-validated score.

(c) The fully honest procedure's permuted mean is 0.5108, not 0.5000, and its
permuted max is 0.6333. Say whether that is a defect, and what it tells you about how to
read a *single* reported accuracy of 0.63 on sixty samples.

(d) Write the reporting rule. What must accompany a cross-validated accuracy for a
reader to be able to tell the two rows of this table apart, given that on real
labels they are almost identical?

<details><summary>Nudge</summary>
For (a): how many of 1000 pure-noise features will correlate with a random binary
label by chance?
</details>
<details><summary>Partial</summary>
(a) **Rows 1 and 2 differ by one prediction.** Identical on real labels (0.9833)
and on permuted max (0.6333); the permuted means are 0.5108 and 0.5117, which is
not agreement to three decimal places — they round to 0.511 and 0.512 — but
something more exact. Each permutation scores 60 predictions and there are 20 of
them, so a permuted mean is a whole number of correct predictions out of 1200:
0.5108 is 613/1200 and 0.5117 is 614/1200. **One prediction in twelve hundred is
the entire measured cost of the protocol violation.** Fitting the grid on all sixty samples is a genuine protocol violation and
it buys essentially nothing, for a reason worth stating: `BettiCurve.fit` reads
only the *diagrams*, never the labels, so whatever it learns from the test fold is
label-free and cannot manufacture label-dependent signal. It is transduction, not
leakage. It should still be inside the loop — the score is meant to describe a
procedure runnable on one new sample, and this one is not — but the honest report
is that the effect here is 0.001, not that it is dangerous.

**Row 3 is different in kind.** Among 1000 features and a random label, some will
correlate with it by chance — that is what 1000 draws buys you. Selecting the best
3 **on all sixty labels** finds exactly those, chosen because they fit *these*
labels, test folds included. Cross-validation afterwards cannot catch it because
the leak already happened: by the time the loop starts, the features have been
chosen using information from every fold, so no held-out data remains with respect
to that choice. Cross-validation protects the steps inside it and nothing else.

The distinction to carry: **it is contact with the labels that converts a protocol
violation into a manufactured result.** Both rows 2 and 3 break the rule; only row
3 produces a number. That is why the rule is stated in terms of dependence on
other samples *or on any label*, with the second disjunct doing the damage.

(b) The criterion: **a step must be inside the loop if its output depends on any
sample other than the one it is applied to, or on any label.** Whitening —
outside is fine, depends only on its own cloud. `VietorisRipsPersistence` —
same, though it belongs inside for the reasons in Problem 3(d). `BettiCurve.fit` —
**must be inside**: its grid depends on the whole collection. Row 2 of the table
is that violation measured, and it is worth one prediction in 1200; the criterion is not
consequentialist, and a rule you only follow when you have checked that breaking
it matters is not a rule. `SelectKBest` — **must be inside**: it depends on the
labels, which is the kind that costs 0.11.
Choosing `n_bins` by looking at a CV score — **must be inside**, and being inside
requires a *nested* loop, because the outer score is otherwise reporting the best
of several attempts.

(c) Not a defect — it is the finite-sample variance, and it is the useful part of
the output. Count what the numbers can resolve, at each of the three levels this
table stacks. **A fold** scores twelve test samples, so its accuracy is a multiple
of 1/12 ≈ 0.083 — and 6/12 = 0.5 exactly *is* attainable, so a fold landing on
chance is an ordinary event and not an impossible one. **A five-fold mean**
aggregates all sixty predictions and so moves in steps of 1/60 ≈ 0.017; that is
the grid the real-label column lives on, which is why 1.0000 against 0.9833 is
one sample. **A permuted mean** aggregates twenty of those, 1200 predictions, and
moves in steps of 1/1200 ≈ 0.00083. Rows 1 and 2 sit at 613 and 614 of those 1200:
adjacent points on the finest grid the experiment has. Nothing should be read into
which is larger, because there is no smaller difference for them to have had. The permuted max of 0.6333 says plainly: **on this data, an accuracy of
0.63 is attainable from labels that carry no information whatever.** So a single
reported 0.63 here is not evidence of anything, and the permutation distribution —
not intuition about what "above chance" means — is what establishes that.

(d) At minimum: the number of samples, the CV scheme, **the full list of steps
that were fitted inside the loop and those that were not**, and the permutation
distribution's mean and max under the same procedure. The last is what separates
row 3 from the others, because the real-label scores nearly do not — 1.0000 against
0.9833 is one sample in sixty. A report giving only "5-fold CV accuracy 1.00" is
compatible with every row of this table, and one of them is worthless.
</details>
