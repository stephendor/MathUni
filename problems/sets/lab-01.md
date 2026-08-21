# lab-01 — Setup and point clouds

**Module:** Computational Lab · **Unit:** lab-01
**Sources:** executed code, in the environment pinned below. API surfaces
verified by execution: `numpy.random.Generator`, `scipy.spatial.distance.pdist`
and `squareform`, `gtda.homology.VietorisRipsPersistence` (fit_transform,
`homology_dimensions`, `reduced_homology`). No book is opened by this unit.

Carried, as syllabus units rather than as pages read here: an2-01's
**Definition 3.1.1** (the metric axioms), an2-02's **Definition 3.4.3**
(completeness), an2-03's **Definition 3.5.2** (compactness). `an-14` is the S1
metric-spaces bridge and is not yet written; where this set needs a metric-space
fact it takes it from the an2 unit that proves it.

## The environment

Every worked answer below is real program output. It is only meaningful next to
the interpreter that produced it, so the environment is pinned and the pins are
checked by gate 9 before any output is compared:

```env
python==3.11.11
giotto-tda==0.6.2
gudhi==3.13.0
numpy==1.26.4
scikit-learn==1.3.2
scipy==1.17.1
```

```python id=env
import sys
from importlib.metadata import version
print("%-14s%s" % ("python", ".".join(str(p) for p in sys.version_info[:3])))
for dist in ("giotto-tda", "gudhi", "numpy", "scikit-learn", "scipy"):
    print("%-14s%s" % (dist, version(dist)))

# A pin read from metadata does not load anything: importlib.metadata reads a
# .dist-info directory, so a distribution whose compiled extensions are missing
# reports its pinned version and fails later, in a block whose diff reads like a
# content error. Import what the later blocks use, at the submodule they use.
for module in ("gtda.homology", "numpy", "scipy.spatial.distance"):
    try:
        __import__(module)
        print("%-24s%s" % (module, "imports"))
    except Exception as exc:
        print("%-24s%s: %s" % (module, type(exc).__name__, exc))

# A module that imports is not an API that exists. These names are the ones
# later blocks use; importing them here means a rename or a broken subpackage
# stops the set at its environment block, not four blocks later in a diff that
# reads like a content error. This is the list the header calls "API surfaces
# verified by execution", and it is now verified rather than asserted.
from gtda.homology import VietorisRipsPersistence
from scipy.spatial.distance import pdist, squareform
```

```text id=env
python        3.11.11
giotto-tda    0.6.2
gudhi         3.13.0
numpy         1.26.4
scikit-learn  1.3.2
scipy         1.17.1
gtda.homology           imports
numpy                   imports
scipy.spatial.distance  imports
```

The repo's own interpreter is Python 3.13.5 and carries **different** versions of
gudhi, ripser and scikit-learn. Running this set there does not reproduce these
numbers, which is why the pin is a gate and not a comment.

---

## Problem 1 (easy — the object, and what it already is)

A *point cloud* is a finite set of points with the distance inherited from the
ambient space. The mission strip says it is a finite metric space, and that is
worth taking literally rather than as a slogan.

(a) Build the cloud. Eighty points sampled uniformly by angle on the unit
circle, then displaced by Gaussian noise of standard deviation 0.06.

```python id=cloud
import numpy as np

rng = np.random.default_rng(20260813)
theta = rng.uniform(0, 2 * np.pi, 80)
X = np.c_[np.cos(theta), np.sin(theta)] + rng.normal(0, 0.06, (80, 2))
print("X.shape   %s" % (X.shape,))
print("X.dtype   %s" % X.dtype)
print("point 0   (%+.4f, %+.4f)" % (X[0, 0], X[0, 1]))
print("point 79  (%+.4f, %+.4f)" % (X[79, 0], X[79, 1]))
```

```text id=cloud
X.shape   (80, 2)
X.dtype   float64
point 0   (+0.9041, -0.2586)
point 79  (+0.8901, -0.0211)
```

Say why `default_rng(20260813)` appears rather than `np.random.seed` or nothing
at all, in terms of what gate 9 checks. Then say what would happen to this
problem set if the seed were removed — not to the mathematics, to the *set*.

(b) Verify **Definition 3.1.1** on this object, all three clauses, by execution
rather than by assertion. Note that clause (iii) is checked over every one of
the $80^3$ triples, which is affordable exactly because the space is finite —
and that finiteness is the whole subject of this problem.

```python id=metric
from scipy.spatial.distance import pdist, squareform

D = squareform(pdist(X))
off_diagonal = D[~np.eye(80, dtype=bool)]
print("D.shape                 %s" % (D.shape,))
print("(i)   d(x,x) = 0        %s" % bool((np.diag(D) == 0).all()))
print("(i)   d(x,y) > 0 else   %s" % bool((off_diagonal > 0).all()))
print("(ii)  d(x,y) = d(y,x)   %s" % np.array_equal(D, D.T))
i, j, k = np.meshgrid(*[np.arange(80)] * 3, indexing="ij")
violations = int((D[i, j] > D[i, k] + D[k, j] + 1e-12).sum())
print("(iii) triangle violations, of %d triples: %d" % (80 ** 3, violations))
```

```text id=metric
D.shape                 (80, 80)
(i)   d(x,x) = 0        True
(i)   d(x,y) > 0 else   True
(ii)  d(x,y) = d(y,x)   True
(iii) triangle violations, of 512000 triples: 0
```

(c) The `1e-12` in the triangle-inequality check is not decoration. Say what it
is for, and say what the check would be testing without it. Then answer the
harder half: this check **passed**, and it was never going to fail. Name the
reason — one sentence, about where the metric came from — and say what the check
is therefore evidence of.

*(The matrix `D` is the real object here. `X` is a set of coordinates in the
plane; `D` is the metric space. The **Rips** pipeline of this unit consumes `D`
and nothing else — that is the whole content of `metric_only=True` — and so is
defined for any finite metric space, with or without an embedding.*

*This is a property of Rips, not of the module. lab-02 hands **coordinates** to
`gudhi.DelaunayCechComplex(points=…)`, because a Čech-type complex is built from
balls in an ambient space and a distance matrix does not determine one; lab-05
perturbs `X` itself, because "move every point by at most δ" is a statement about
positions. The input contract to carry forward is per-construction: know which of
the two your complex needs, and do not assume a distance matrix is always
enough.)*

<details><summary>Nudge</summary>
For (a): gate 9 runs the file twice and requires the two runs to agree.
For (c): the distances were computed by `pdist` from points in $\mathbb{R}^2$.
</details>
<details><summary>Strategy</summary>
(c) Floating-point addition is not associative and $d(x,k) + d(k,j)$ is computed
in a different order from $d(i,j)$, so an exact `>` comparison can report a
violation that is an artefact of rounding rather than of the metric. The
tolerance absorbs that. Without it you would be testing the floating-point
arithmetic, not the axiom.
</details>
<details><summary>Partial</summary>
(a) Without the seed the outputs change on every run, so gate 9's determinism
check fails: two runs of the same file disagree and the set is rejected before
any output is compared. The mathematics is unaffected — a different sample is
just as good a point cloud — but a *recorded* output that cannot be re-derived
is not a worked answer, it is a claim.

(c) The Euclidean metric on $\mathbb{R}^2$ satisfies the axioms, and a subset of
a metric space is a metric space under the restricted distance. So the
verification could not have failed, and it is evidence about **the code**, not
about the mathematics: it says `pdist` and `squareform` return what their names
promise, in this version, in this environment. That is the whole of what an
executed check on a known theorem can buy, and it is worth having — an2-01 spent
a unit proving Definition 3.1.1's clauses by hand, and the thing that can still
go wrong at this point is a library, not a proof.
</details>

---

## Problem 2 (medium — the point of the unit: this space has no topology)

The reader has just spent a semester on metric spaces. Ask what that semester
says about *this* metric space.

(a) Compute the separation — the smallest distance between two distinct points —
and check whether every ball of half that radius contains exactly one point.

```python id=discrete
separation = off_diagonal.min()
print("separation r        %.6f" % separation)
print("diameter            %.6f" % D.max())
singletons = ((D < separation / 2).sum(axis=1) == 1).all()
print("every B(x, r/2) is a singleton: %s" % bool(singletons))
```

```text id=discrete
separation r        0.004290
diameter            2.233080
every B(x, r/2) is a singleton: True
```

(b) Conclude. Every singleton is open, so **every** subset is open, so the
topology on this space is the discrete one. Write down what that costs, item by
item, and be blunt about each:

  (i) its homology, in every degree;
  (ii) whether it is compact, in the sense of an2-03's Definition 3.5.2;
  (iii) whether it is complete, in the sense of an2-02's Definition 3.4.3;
  (iv) which continuous functions it admits.

(c) Three of those four answers are *yes* and are worth nothing. Say precisely
why — what a hypothesis buys you when everything satisfies it — and then state
the consequence for this module in one sentence. This is the sentence lab-02
exists to act on.

(d) The cloud was sampled from a circle. The circle has $H_1 = \mathbb{Z}$. The
cloud has $H_1 = 0$. Both statements are true and neither is a mistake. Say what
is wrong with the question that makes them look like a contradiction.

<details><summary>Nudge</summary>
For (c): a hypothesis that every object satisfies cannot distinguish any object
from any other.
For (d): "the topology of the point cloud" is not the thing anyone wanted to know.
</details>
<details><summary>Partial</summary>
(b) (i) $H_0 = \mathbb{Z}^{80}$ and $H_n = 0$ for $n \geq 1$ — eighty
contractible pieces. (ii) Compact: yes, trivially, since every sequence in a
finite set has a constant subsequence. (iii) Complete: yes, trivially, since a
Cauchy sequence in a discrete space is eventually constant — this is an2-02's
worked example, and it applies here with nothing to check. (iv) Every function
out of it is continuous, since every preimage is open.

(c) A hypothesis satisfied by every object in sight separates nothing. an2-03
spent a unit showing that compactness is the property that makes infinite behave
like finite; on a finite space it is free, and buys correspondingly nothing.
**Consequence: the topology of a point cloud is never the object of study. The
object of study is a one-parameter family of spaces built from it, and the
parameter is the scale.**

(d) The question "what is the homology of the data?" has no useful answer. The
data is 80 points and its homology says so. What the reader wants is the
homology of the *circle the points were sampled from*, which is not determined by
the points at all — it is inferred, at a scale, with a guarantee. Getting from
one to the other is the whole module, and lab-05 is where the guarantee arrives.
</details>

---

## Problem 3 (medium — the first pipeline, and the first number that means something)

(a) Run Vietoris–Rips persistence in degrees 0 and 1. lab-02 builds this complex
by hand; here it is a black box on purpose, so that the *shape of the answer* can
be looked at before the construction is understood.

```python id=persistence
from gtda.homology import VietorisRipsPersistence

dgm = VietorisRipsPersistence(homology_dimensions=[0, 1]).fit_transform(X[None])[0]
h0 = dgm[dgm[:, 2] == 0]
h1 = dgm[dgm[:, 2] == 1]
print("H0 intervals returned  %d" % len(h0))
print("H1 intervals returned  %d" % len(h1))
life = h1[:, 1] - h1[:, 0]
for rank, idx in enumerate(np.argsort(-life)[:3], start=1):
    print("H1 #%d  birth %.4f  death %.4f  life %.4f"
          % (rank, h1[idx, 0], h1[idx, 1], life[idx]))
print("ratio longest : runner-up   %.1f" % (life.max() / np.sort(life)[-2]))
```

```text id=persistence
H0 intervals returned  79
H1 intervals returned  6
H1 #1  birth 0.3991  death 1.6361  life 1.2370
H1 #2  birth 0.1133  death 0.1259  life 0.0126
H1 #3  birth 0.1796  death 0.1911  life 0.0115
ratio longest : runner-up   98.1
```

(b) Six $H_1$ intervals were returned and the circle has one hole. Do **not**
say five of them are wrong. Say what all six are, what distinguishes the first
from the other five, and — the part that matters — whether the distinction is
categorical or a matter of degree. Support the answer with the ratio 98.1, and
say what you would be entitled to conclude if that ratio were 1.4 instead.

(c) The input to this computation was 80 points with no topology at all, from
Problem 2. Explain, without using the word "hole", where the number 1.2370 came
from.

<details><summary>Nudge</summary>
For (b): the five short intervals are also real features of a real complex.
For (c): the answer names a parameter that does not appear anywhere in `X`.
</details>
<details><summary>Partial</summary>
(b) All six are genuine 1-cycles that appear and vanish in the filtration; the
five short ones are the gaps between neighbouring points that briefly fail to
fill in. The distinction is **entirely a matter of degree** — nothing in the
algorithm marks one interval as signal — and the ratio 98.1 is the whole of the
evidence. At 1.4 you would be entitled to conclude nothing: the longest bar would
be within the noise band, and a second sample from the same distribution could
reorder them. Persistence is a *ranking*, and lab-05 is where the ranking
acquires a theorem.

(c) From the scale parameter. The computation does not ask what shape the points
form; it builds a complex at every radius $\epsilon$ simultaneously and records
the radii at which a 1-cycle appears and is filled. 1.2370 is the width of the
band of radii on which the eighty points are connected enough to close a loop and
not yet connected enough to fill it. It is a fact about the *family*, and there
is no single space it is a fact about.
</details>

---

## Problem 4 (medium — the library is a source, and it has conventions)

Eighty points, and Problem 3 reported 79 intervals in $H_0$.

(a) Run the comparison.

```python id=reduced
full = VietorisRipsPersistence(homology_dimensions=[0, 1],
                               reduced_homology=False).fit_transform(X[None])[0]
print("reduced_homology=True   H0 count %d" % len(h0))
print("reduced_homology=False  H0 count %d" % int((full[:, 2] == 0).sum()))
print("points in the cloud     %d" % len(X))
```

```text id=reduced
reduced_homology=True   H0 count 79
reduced_homology=False  H0 count 80
points in the cloud     80
```

(b) Explain the missing interval. Which class is it, why is it the one dropped,
and what is its death value under `reduced_homology=False`?

(c) `reduced_homology=True` is the **default**. State the discipline this
imposes, and compare it with an2's rule that a citation's verb is a property of
the page cited. Write the version of that rule for a library.

(d) Suppose a later unit reports "the number of $H_0$ bars equals the number of
connected components". Say under which flag that sentence is true, under which it
is false, and why a reader of the sentence alone cannot tell.

<details><summary>Nudge</summary>
For (b): one component never dies.
</details>
<details><summary>Partial</summary>
(b) The essential class — the one connected component that survives to the end of
the filtration. Reduced homology quotients out $\tilde{H}_0$'s extra generator,
so the essential interval disappears; with `reduced_homology=False` it is present
with death $\infty$.

(c) **An API's default is part of the citation.** "giotto-tda returns 79
intervals" is not a fact about the data, it is a fact about the data *and* a flag
nobody wrote down. The an2 rule was: a result's modality — proved, stated, set as
an exercise — belongs to the page, so read the page. Here: a number's meaning
belongs to the call that produced it, so record the call, with its version and
its non-default *and default* arguments. The default is the dangerous one,
because it is invisible at the call site.

(d) True under `reduced_homology=False`, false under the default by exactly one.
The reader cannot tell because the sentence names neither the flag nor the
version, and both are load-bearing. This is the lab analogue of a citation with
no page number.
</details>

---

## Problem 5 (hard — the strip, audited)

> A point cloud is a finite metric space; every pipeline in this lab starts
> exactly here.

(a) The first clause is true, and Problem 1 verified it by execution. Say what
Problem 2 then shows about how much that clause is worth, and reconcile the two:
the strip is not wrong, but it is *not the reason the module works either*.

(b) The second clause says every pipeline starts here. Check it against the
module: name, for each of lab-02 through lab-05, the object that unit actually
consumes, and say whether it is the point cloud, the distance matrix, or
something built from them. Then say whether "starts exactly here" survives.

(c) Write the sentence the strip is missing — one sentence, naming the object
that carries the topology, since Problem 2 established that the point cloud does
not.

(d) A reader who has done an2 might reasonably ask why a whole semester of metric
space theory was needed if every point cloud is a discrete space on which all of
it is trivial. Answer them. The answer is not "it becomes useful later"; name the
space the theory is actually about in this module, and which an2 unit supplies
the fact that space needs.

<details><summary>Nudge</summary>
For (d): the theory is not applied to the point cloud. Ask what space the
*diagrams* live in.
</details>
<details><summary>Partial</summary>
(a) Both are true. A point cloud is a finite metric space, and a finite metric
space is topologically trivial. The strip identifies the input correctly and
says nothing about where the content is, which is in the filtration. **No
syllabus action: the strip is accurate and incomplete, and the incompleteness is
what this unit teaches.**

(c) Something of the form: *the topology is carried by the one-parameter family
of complexes built from the distance matrix, not by the points, and the
persistence diagram is the summary of that family.*

(d) The metric-space theory is not applied to the data. It is applied to the
**space of persistence diagrams** — an2-01 established the bottleneck distance is
an extended pseudometric on diagrams in general, an2-02 audited what completeness
does and does not mean there, and lab-05 needs exactly that vocabulary to state
stability. The data is a finite metric space and is trivial; the *output* lives
in an infinite-dimensional space where none of it is trivial. That inversion is
worth stating out loud, because the syllabus order hides it.
</details>
