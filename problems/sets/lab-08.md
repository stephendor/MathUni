# lab-08 — Mapper

**Module:** Computational Lab · **Unit:** lab-08
**Sources:** Dey and Wang, *Computational Topology for Data Analysis*, Chapter 9
"Cover, Nerve, and Mapper", §9.3 "Mapper and Multiscale Mapper", printed
**268–274** (folio = PDF − 21, verified in lab-06). Specifically:
**Definition 9.4** (Mapper), printed 269; Remark 9.1 on the covers that make
Mapper a Reeb graph or a merge tree, printed 269; the "Mapper for PCD"
construction, printed 270; **Definition 9.6** (pullback metric), printed 273;
**Proposition 9.15** (the pullback cover's Lebesgue number), printed 273;
**Theorem 9.16**, printed 274. Plus executed code, in the environment pinned
below. API surfaces verified by execution: `gtda.mapper.make_mapper_pipeline`,
`gtda.mapper.Projection`, `gtda.mapper.CubicalCover`, `gtda.mapper.Eccentricity`,
`kmapper.KeplerMapper.map`, `kmapper.Cover`, `sklearn.cluster.DBSCAN`.

Carried: lab-02's Nerve Theorem and the distinction between a complex with a
theorem attaching it to the data and one without; lab-05's stability, for
contrast; lab-07's rule that a reported number must be accompanied by what would
have made it different.

**Source-boundary notes.**

1. The syllabus resource line names `giotto-tda: Mapper`, `Kepler-Mapper docs`
   and `Singh-Memoli-Carlsson, Mapper (2007)`. The third **is not on disk** — it
   was already recorded as absent during the audit. Dey and Wang §9.3 **is** on
   disk and gives Definition 9.4, the point-cloud construction and Theorem 9.16.
   It is used as the primary source; the divergence is recorded for the syllabus
   pass, the third instance after `lab-06` and `lab-07`.
2. The `env` block below imports every module the later blocks use. That is the
   convention `lab-07` arrived at the hard way, and this is the first set
   authored under it.

## The environment

```env
python==3.11.11
giotto-tda==0.6.2
kmapper==2.1.0
igraph==1.0.0
scikit-learn==1.3.2
numpy==1.26.4
```

```python id=env
import sys
from importlib.metadata import version
print("%-16s%s" % ("python", ".".join(str(p) for p in sys.version_info[:3])))
for dist in ("giotto-tda", "kmapper", "igraph", "scikit-learn", "numpy"):
    print("%-16s%s" % (dist, version(dist)))

# A pin read from metadata does not load anything: importlib.metadata reads a
# .dist-info directory, so a distribution whose compiled extensions are missing
# reports its pinned version and fails later, in a block whose diff reads like a
# content error. Import what the later blocks use, at the submodule they use.
for module in ("gtda.mapper", "igraph", "kmapper", "numpy", "sklearn.cluster",
               "sklearn.preprocessing"):
    try:
        __import__(module)
        print("%-23s%s" % (module, "imports"))
    except Exception as exc:
        print("%-23s%s: %s" % (module, type(exc).__name__, exc))

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
    from gtda.mapper import CubicalCover, Eccentricity, Projection, make_mapper_pipeline
    from kmapper import Cover, KeplerMapper
    from numpy import c_, cos, linalg, pi, random, sin
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import FunctionTransformer

_api_surface()
```

```text id=env
python          3.11.11
giotto-tda      0.6.2
kmapper         2.1.0
igraph          1.0.0
scikit-learn    1.3.2
numpy           1.26.4
gtda.mapper            imports
igraph                 imports
kmapper                imports
numpy                  imports
sklearn.cluster        imports
sklearn.preprocessing  imports
```

---

## Problem 1 (medium — the construction, and the four places a choice enters)

> **Definition 9.4 (Mapper), printed 269.** Let X and Z be topological spaces and
> let f : X → Z be a well-behaved and continuous map. Let 𝒰 = {U_α} be a finite
> open cover of Z. The *mapper* arising from these data is defined to be the nerve
> of the pullback cover f*(𝒰) of X; that is, M(𝒰, f) := N(f*(𝒰)).

```python id=mapper
import numpy as np
import gtda.mapper as gm
from sklearn.cluster import DBSCAN

rng = np.random.default_rng(20260820)
theta = rng.uniform(0, 2 * np.pi, 300)
X = np.c_[np.cos(theta), np.sin(theta)] + rng.normal(0, 0.05, (300, 2))
print("point cloud %s, sampled from one circle" % (X.shape,))

def mapper_graph(filter_func, n_intervals=10, overlap_frac=0.30, eps=0.30):
    pipe = gm.make_mapper_pipeline(
        filter_func=filter_func,
        cover=gm.CubicalCover(n_intervals=n_intervals, overlap_frac=overlap_frac),
        clusterer=DBSCAN(eps=eps, min_samples=3),
        n_jobs=1)
    G = pipe.fit_transform(X)
    components = len(G.connected_components())
    return G.vcount(), G.ecount(), components, G.ecount() - G.vcount() + components

v, e, k, b1 = mapper_graph(gm.Projection(columns=[0]))
print("lens = x coordinate, 10 intervals, overlap 0.30, DBSCAN eps 0.30")
print("  nodes %d   edges %d   components %d   b1 = e - v + k = %d" % (v, e, k, b1))
print("  the circle has one loop, and the graph reports one")
```

```text id=mapper
point cloud (300, 2), sampled from one circle
lens = x coordinate, 10 intervals, overlap 0.30, DBSCAN eps 0.30
  nodes 18   edges 18   components 1   b1 = e - v + k = 1
  the circle has one loop, and the graph reports one
```

(a) Walk Definition 9.4 against that call and identify, one by one, what plays the
role of X, Z, f and 𝒰. Then name the object in the call that appears **nowhere**
in Definition 9.4, and say what it is standing in for.

(b) Dey and Wang's "Mapper for PCD" paragraph, printed 270, gives the discrete
construction: a graph G^r(P) with an edge whenever d(p, p′) ≤ r, and the
components of the subgraph spanned by each interval's points. Compare that with
what `DBSCAN(eps=0.30, min_samples=3)` computes, and say precisely where the two
differ. Then say what `min_samples=3` does that has no counterpart in the book at
all.

(c) Dey and Wang write that "in the limit that each interval degenerates to a
point, the discretized Reeb graph converges to the original Reeb graph as shown
in [132, 241]". Neither reference is on disk. Say what that sentence licenses, what
it does not, and compare its logical role here with the Nerve Theorem's role in
lab-02.

(d) Remark 9.1, printed 269, records that taking U_α = (−∞, α) gives merge trees
and U_α = (α − ε, α + ε) gives a relaxed Reeb graph. Say what that implies about
the phrase "the Mapper graph of this dataset".

<details><summary>Nudge</summary>
For (a): count the arguments to <code>make_mapper_pipeline</code> and subtract the
ones Definition 9.4 accounts for.
</details>
<details><summary>Partial</summary>
(a) X is the point cloud — a finite metric space, which *is* a topological space,
carrying the discrete topology, and that is exactly the problem rather than an
absence of one. Z is ℝ. f is the lens, here projection onto the first
coordinate. 𝒰 is the ten overlapping intervals of `CubicalCover`. The object with
no counterpart in Definition 9.4 is the **clusterer**. Definition 9.4 decomposes
f⁻¹(U_α) into its **path connected components**, which requires a topology on X;
a finite point cloud has only the discrete topology, in which every component is a
single point. DBSCAN is standing in for path-connectedness, and it is a choice
rather than a consequence.

(b) G^r(P) is the ε-neighbourhood graph and its components are the single-linkage
clusters at threshold r; DBSCAN with `min_samples=1` is exactly that. With
`min_samples=3` it is not: DBSCAN distinguishes core points, border points and
**noise**, and points that fail the density test are assigned to no cluster at
all and vanish from the Mapper graph entirely. Nothing in the book discards data.
So `min_samples` is a parameter that can delete points from the summary, with no
counterpart in Definition 9.4 or in the PCD construction.

(c) It licenses an asymptotic statement about a limit of covers, attributed to two
papers that have not been read. It does not license anything about any particular
cover, and every cover used in practice is finite and coarse. Compare lab-02: the
Nerve Theorem was a theorem, *in the source*, with checkable hypotheses (closed
convex sets), and it failed for Vietoris–Rips, which is why lab-02 could say
exactly what Rips did and did not carry. Here the bridging statement is a
**citation to an absent source about an unattained limit** — strictly weaker on
all three counts.

(d) That there is no such thing. The phrase names a family indexed by (f, 𝒰,
clusterer); Remark 9.1 shows that even holding f fixed, two different covers give
two structurally different objects — a merge tree, which is a tree and has no
loops at all, and a Reeb graph, which can. "The Mapper graph" is well defined only
relative to four stated choices, and a report that omits them has not specified
its own output.
</details>

---

## Problem 2 (hard — the theorem, and the sweep that instantiates it)

> **Theorem 9.16(a), printed 274.** Let f : X → Z be a map from a path connected
> space X to a metric space Z equipped with a cover 𝒰, and let 𝒰′ be the
> restriction of 𝒰 to f(X). Let z₁, …, z_g be an optimal cycle basis for H₁(X) in
> the pullback metric. Let ℓ = g + 1 if λ(𝒰′) > s(z_g); otherwise let ℓ be the
> smallest integer with s(z_ℓ) > λ(𝒰′). If ℓ ≠ 1, the class φ_{𝒰*}[z_j] = 0 for
> j = 1, …, ℓ − 1. Moreover, if ℓ ≠ g + 1, the classes {φ_{𝒰*}[z_j]}_{j=ℓ,…,g}
> generate H₁(N(f*𝒰)).

In words: **cycles smaller than the cover's Lebesgue number are killed; the
survivors generate.** So the cover decides which loops you see. Sweep it.

```python id=cover
# THEOREM-PROBE: Theorem 9.16 under cover refinement and fragmentation
print("b1 of the Mapper graph, over the cover parameters. The cloud has one loop.")
print()
overlaps = (0.05, 0.15, 0.30, 0.45)
print("%-10s%s" % ("intervals", "".join("%-18s" % ("overlap %.2f" % o) for o in overlaps)))
matching = 0
for n in (4, 6, 10, 15, 25):
    row = "%-10d" % n
    for o in overlaps:
        v, e, k, b1 = mapper_graph(gm.Projection(columns=[0]), n_intervals=n,
                                   overlap_frac=o)
        matching += (b1 == 1)
        row += "%-18s" % ("v%d e%d k%d b1=%d" % (v, e, k, b1))
    print(row)
print()
print("cells whose b1 matches the one loop: %d of 20" % matching)
```

```text id=cover
b1 of the Mapper graph, over the cover parameters. The cloud has one loop.

intervals overlap 0.05      overlap 0.15      overlap 0.30      overlap 0.45      
4         v6 e3 k3 b1=0     v6 e5 k1 b1=0     v6 e6 k1 b1=1     v6 e6 k1 b1=1     
6         v10 e5 k5 b1=0    v10 e10 k1 b1=1   v10 e10 k1 b1=1   v10 e10 k1 b1=1   
10        v18 e11 k7 b1=0   v18 e17 k1 b1=0   v18 e18 k1 b1=1   v18 e18 k1 b1=1   
15        v28 e12 k16 b1=0  v28 e25 k3 b1=0   v28 e27 k1 b1=0   v28 e28 k1 b1=1   
25        v46 e11 k35 b1=0  v45 e31 k14 b1=0  v46 e43 k3 b1=0   v46 e45 k1 b1=0   

cells whose b1 matches the one loop: 8 of 20
```

(a) Eight of twenty. Read the table as a whole and describe the region of
parameter space that works — is it a corner, a band, an island? Then say which of
the two parameters the answer is more sensitive to, and give a reason from the
construction rather than from the table.

(b) The whole `overlap 0.05` column reports b₁ = 0, with 3, 5, 7, 16 and 35
connected components. Explain what has gone wrong there, and say whether Theorem
9.16 predicts it. Be careful: the theorem is about cycles being *killed*, and
something else is happening.

(c) The bottom row, 25 intervals, reports b₁ = 0 at every overlap tested — the
finest cover in the sweep is the only one that never works. Reconcile that with
the reading of Theorem 9.16 as "shrink the cover and small cycles die, so a fine
cover keeps everything".

(d) Theorem 9.16 needs X path connected, f continuous and well behaved, and 𝒰 an
open cover of a metric space. List which of those the sweep's setup actually
satisfies. Then state, in one sentence, what the sweep table is evidence *for*,
given that the theorem does not apply to it.

<details><summary>Nudge</summary>
For (b): b₁ = e − v + k, and k is in the formula.
For (c): with 25 intervals over the same range, how many of the 300 points land in
each one?
</details>
<details><summary>Partial</summary>
(a) A **band running from the top-right towards the bottom-right corner**: you
need enough overlap for adjacent cover elements to intersect, and the more
intervals you use the more overlap you need. It is far more sensitive to
**overlap** — the 0.05 column is uniformly wrong and the 0.45 column is right in
four rows of five. The reason from the construction: an edge of the nerve exists
only when two cover elements share a point, so the overlap fraction directly
controls whether the graph has any edges at all, while the interval count controls
only how finely the loop is subdivided.

(b) The graph has **fallen apart**, not lost a cycle. At 25 intervals and 5%
overlap the pullback pieces barely meet, so the nerve has 46 vertices and 11 edges
in 35 components. b₁ = e − v + k = 11 − 46 + 35 = 0 not because a loop was killed
but because no loop was ever closed. Theorem 9.16 does **not** predict this: the
theorem is about which classes of H₁(X) map to zero under a cover that is a genuine
cover, and it presupposes the nerve is built from elements that overlap as the
topology of X requires. A cover of a finite point set whose pieces do not meet is
not modelling an open cover of the circle at all.

(c) Because "shrink the cover" in the theorem means shrink the *Lebesgue number*
of an open cover of a space, holding the covering property fixed. In the
discretisation, shrinking the intervals also shrinks the number of **points** in
each one — at 25 intervals roughly 12 points per interval, spread over a thin
band — and the clusterer then fragments them. The theorem's parameter and the
implementation's parameter move together but are not the same quantity, and the
implementation's failure mode (too few points per piece) has no counterpart in the
theorem at all.

(d) X path connected: **no** — a 300-point cloud is discrete. f continuous:
vacuously true on a discrete space, and therefore empty. f well behaved (finitely
many path components in each preimage): vacuously true, and again empty — every
preimage has as many components as it has points. 𝒰 an open cover of a metric
space: **yes**, of ℝ. So one hypothesis of four holds non-vacuously. The sweep is
therefore evidence for the *behaviour of the software*, and for the qualitative
claim that Mapper's output is a function of its parameters; it is not a test of
Theorem 9.16, which says nothing about any object in this problem set.
</details>

---

## Problem 3 (hard — the lens turns one hole into six)

Everything above held the lens fixed. Change only the lens.

```python id=lens
from sklearn.preprocessing import FunctionTransformer

radial = FunctionTransformer(lambda A: np.linalg.norm(A, axis=1).reshape(-1, 1))
print("same cloud, same cover (10 intervals, overlap 0.30), same clusterer.")
print("only the lens changes.")
print()
print("%-24s %-8s %-8s %-12s %-6s" % ("lens", "nodes", "edges", "components", "b1"))
for name, f in (("x coordinate", gm.Projection(columns=[0])),
                ("y coordinate", gm.Projection(columns=[1])),
                ("distance from origin", radial),
                ("eccentricity", gm.Eccentricity())):
    v, e, k, b1 = mapper_graph(f)
    print("%-24s %-8d %-8d %-12d %-6d" % (name, v, e, k, b1))
```

```text id=lens
same cloud, same cover (10 intervals, overlap 0.30), same clusterer.
only the lens changes.

lens                     nodes    edges    components   b1    
x coordinate             18       18       1            1     
y coordinate             18       18       1            1     
distance from origin     30       34       2            6     
eccentricity             33       32       4            3     
```

(a) The correct answer is 1. Two lenses give it, one gives **six**, one gives
three. Explain the distance-from-origin result mechanically: what does that lens
do to a noisy circle, what does the resulting cover look like, and where do six
loops come from?

(b) Definition 9.6, printed 273, defines the pullback pseudometric
d_f(x, x′) := inf over paths γ of diam_Z(f ∘ γ). Theorem 9.16, printed 274, has cycle sizes
s(z) are measured in it. Use that to say why the choice of lens is not a cosmetic
one — what does changing f change, in the theorem's own terms?

(c) Proposition 9.15, printed 273, states that the pullback cover f*𝒰 has the same
Lebesgue number as 𝒰′, the restriction of 𝒰 to f(X). Say what that buys you, and
then say why it does **not** rescue the distance-from-origin lens.

(d) A defensible report has to fix a lens. State the criterion you would apply,
and then say honestly whether the x-coordinate lens satisfies it here or whether
it was chosen because it gave the right answer.

<details><summary>Partial</summary>
(a) On a circle of radius 1 with noise 0.05, the distance from the origin is
≈ 1 for every point — it ranges over roughly [0.85, 1.15] rather than over
[−1, 1]. The ten intervals therefore subdivide the *noise*, not the circle. Each
interval's preimage is a scattered set of points from all round the circle, which
DBSCAN then splits into several clusters, and the nerve wires those clusters
together according to accidents of which noisy points happen to share an interval.
The six loops are artefacts of the noise, and would change with the seed. This is
the sharpest failure in the module: the lens has destroyed the structure before
any topology is computed.

(b) It changes the **metric in which the cycles are measured**. Theorem 9.16
compares s(z_j) with λ(𝒰′), and s is the size in the pullback pseudometric d_f,
which is defined *through f*. So changing the lens changes which cycles count as
small, and hence which ones the theorem says are killed. The lens is not a
visualisation choice sitting on top of a topological computation; it is part of
the metric the computation is about.

(c) It buys the ability to reason about the cover downstairs, in Z, rather than
about its pullback upstairs — you set λ by choosing intervals on ℝ and you get the
same λ on X for free. It does not rescue the radial lens because λ is measured in
d_f, and the radial lens makes d_f nearly degenerate: two points on opposite sides
of the circle have almost the same f-value, so every path between them has small
diam_Z(f ∘ γ) and the pullback pseudometric collapses. The cover is fine in Z and
useless on X, and Proposition 9.15 is what makes that precise rather than what
prevents it.

(d) A criterion: **the lens must be chosen from the modelling question, before
seeing the graph, and stated with the report** — and, ideally, a small family of
lenses should be reported rather than one. Honestly: the x-coordinate lens here
was chosen because a linear projection is the standard first choice for a planar
cloud, but it is also the one that gives the right answer, and this problem set
cannot distinguish those two reasons. That is exactly the situation a report must
disclose rather than resolve.
</details>

---

## Problem 4 (medium — the parameter with no counterpart in the definition)

```python id=cluster
print("same cloud, same cover, same lens. only DBSCAN's eps changes.")
print()
print("%-10s %-8s %-8s %-12s %-6s" % ("eps", "nodes", "edges", "components", "b1"))
for eps in (0.10, 0.20, 0.30, 0.60):
    v, e, k, b1 = mapper_graph(gm.Projection(columns=[0]), eps=eps)
    print("%-10.2f %-8d %-8d %-12d %-6d" % (eps, v, e, k, b1))
```

```text id=cluster
same cloud, same cover, same lens. only DBSCAN's eps changes.

eps        nodes    edges    components   b1    
0.10       32       23       9            0     
0.20       18       18       1            1     
0.30       18       18       1            1     
0.60       18       18       1            1     
```

(a) At eps = 0.10 the loop is gone and the graph is in nine pieces; at 0.20 and
above it is stable. Say what quantity of the data eps is competing against, and
estimate it from the construction — 300 points, one circle of radius 1.

(b) Definition 9.4 says "path connected components". Say what would have to be
true of eps for DBSCAN's clusters to be *the* right stand-in, and whether such a
value can be read off the data.

(c) Compare this table with the cover sweep in Problem 2. One shows sensitivity to
a parameter of the cover, the other to a parameter of the clusterer. Which is the
more serious problem for reporting, and why?

<details><summary>Partial</summary>
(a) eps competes against the **spacing between neighbouring points along the
circle**. 300 points on a circle of circumference 2π ≈ 6.28 gives a mean gap of
about 0.021, but they are uniformly random rather than evenly spaced, so the
largest gap in a sample of 300 is several times the mean — of order
6.28 · ln(300)/300 ≈ 0.12. At eps = 0.10 some of those gaps exceed eps, the
neighbourhood graph disconnects within intervals, and the ring breaks into nine
pieces. At 0.20 every gap is bridged. The threshold is a property of the
*sampling*, not of the circle.

(b) It would have to sit above the largest gap between consecutive points that
ought to be connected, and below the smallest distance between parts that ought
not to be — that is, the data would have to have a genuine gap in its distance
distribution. Such a value exists here (roughly 0.12 to 0.5) and can be estimated
from the data, but only because the truth is known; in general no such gap need
exist, and when it does not, no value of eps is right and the choice is arbitrary.

(c) The **clusterer** is the more serious problem, for two reasons. First, the
cover is at least a parameter of the object Definition 9.4 defines, so its effect
is described by Theorem 9.16 and can be reasoned about; the clusterer is a
substitute for a notion (path-connectedness) that the discrete setting does not
have, so nothing in the theory speaks to it at all. Second, the cover parameters
are conventionally reported and the clusterer's often are not — a paper saying
"Mapper with 10 intervals and 30% overlap" has told you half of what it did.
</details>

---

## Problem 5 (hard — two implementations, one definition)

```python id=implementations
import kmapper

def kepler_graph(n_cubes, perc_overlap):
    mapper = kmapper.KeplerMapper(verbose=0)
    graph = mapper.map(X[:, [0]], X,
                       cover=kmapper.Cover(n_cubes=n_cubes, perc_overlap=perc_overlap),
                       clusterer=DBSCAN(eps=0.30, min_samples=3))
    names = sorted(graph["nodes"])
    index = {name: i for i, name in enumerate(names)}
    edges = set()
    for a, targets in graph["links"].items():
        for b in targets:
            edges.add(tuple(sorted((index[a], index[b]))))
    parent = list(range(len(names)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    components = len({find(i) for i in range(len(names))})
    return len(names), len(edges), components, len(edges) - len(names) + components

print("two implementations of Definition 9.4, same cloud, same lens,")
print("same clusterer, same nominal cover parameters.")
print()
print("%-16s %-18s %-18s %s" % ("cover", "giotto-tda v/e/b1", "kepler-mapper v/e/b1", "verdict"))
for n, o in ((6, 0.15), (10, 0.30), (10, 0.10), (15, 0.45), (25, 0.30)):
    v, e, k, b1 = mapper_graph(gm.Projection(columns=[0]), n_intervals=n, overlap_frac=o)
    kv, ke, kk, kb1 = kepler_graph(n, o)
    print("%-16s %-18s %-18s %s"
          % ("n=%d ov=%.2f" % (n, o), "%d/%d/%d" % (v, e, b1),
             "%d/%d/%d" % (kv, ke, kb1),
             "agree" if (v, e, b1) == (kv, ke, kb1) else "DIFFER"))

# Each library at ITS OWN default, run rather than read off the sweep. The two
# parameters are not the same quantity -- giotto's overlap_frac and kmapper's
# perc_overlap are differently defined -- so neither default can be inferred
# from the other library's column.
print()
gv, ge, gk, gb1 = mapper_graph(gm.Projection(columns=[0]),
                               n_intervals=10, overlap_frac=0.1)
kv, ke, kk, kb1 = kepler_graph(10, 0.5)
# "matches" and not "correct": the cloud was built from one circle, so b1 = 1 is
# the benchmark this graph is being read against -- but no theorem in this unit
# says a Mapper graph is obliged to recover it, and DBSCAN discarding points is
# a documented way to miss it without anything being wrong. Recovering a known
# answer is evidence about these parameters on this cloud, not a correctness
# certificate for either library.
print("giotto-tda default   n=10 overlap_frac=0.10   %d/%d/%d   b1 %s"
      % (gv, ge, gb1, "matches the one loop" if gb1 == 1 else "misses it"))
print("kepler-mapper default n=10 perc_overlap=0.50  %d/%d/%d   b1 %s"
      % (kv, ke, kb1, "matches the one loop" if kb1 == 1 else "misses it"))
```

```text id=implementations
two implementations of Definition 9.4, same cloud, same lens,
same clusterer, same nominal cover parameters.

cover            giotto-tda v/e/b1  kepler-mapper v/e/b1 verdict
n=6 ov=0.15      10/10/1            10/10/1            agree
n=10 ov=0.30     18/18/1            18/18/1            agree
n=10 ov=0.10     18/15/0            18/15/0            agree
n=15 ov=0.45     28/28/1            26/25/0            DIFFER
n=25 ov=0.30     46/43/0            45/42/0            DIFFER

giotto-tda default   n=10 overlap_frac=0.10   18/15/0   b1 misses it
kepler-mapper default n=10 perc_overlap=0.50  16/16/1   b1 matches the one loop
```

(a) At n = 15, overlap 0.45 the two libraries disagree about **b₁ itself** — one
loop against none — on the same data with the same clusterer. Given that both
implement Definition 9.4, list the places where an implementation is free to
differ without being wrong, and say which one most plausibly accounts for this.

(b) `gtda.mapper.CubicalCover`'s default is `overlap_frac=0.1`;
`kmapper.Cover`'s default is `perc_overlap=0.5`. Given Problem 2's table, say what
each default would have given you on this data, and state the discipline this
demands — naming the two earlier units in this module that arrived at the same
discipline from different directions.

(c) lab-03 also cross-checked an implementation against another and they **agreed**,
and lab-05 tested a bound and it **held**. This is the first cross-check in the
module that fails. Say what that failure establishes and what it does not — in
particular, whether either library is thereby shown to have a bug.

(d) Write the reporting rule for a Mapper graph, in one paragraph. It must be
sufficient for a reader with the same data to reproduce the figure.

<details><summary>Partial</summary>
(a) Free to differ: how the cover's interval endpoints are placed (whether the
outer intervals extend to the data's extremes or are centred), whether the overlap
fraction is measured against the interval width or the gap, whether points on an
interval boundary go to one side or both, and whether empty or singleton clusters
become nodes. **The interval placement most plausibly accounts for it**: at n = 15
with 45% overlap the intervals are wide and heavily overlapping, so a small
difference in where the first and last intervals start changes how many points the
end intervals hold — and Kepler-Mapper reports 26 nodes where giotto-tda reports
28, which is exactly two fewer, consistent with two end clusters not being formed.

(b) Both defaults are **run**, in the last two lines of the block, rather than read
off the sweep — and that matters, because the two parameters are not the same
quantity. giotto's `overlap_frac` and Kepler-Mapper's `perc_overlap` are defined
differently, so a column of one table is not evidence about the other library, and
the measured Kepler-Mapper default gives **16/16/b₁ = 1**, a row that appears
nowhere in the sweep above.

giotto-tda's default (10 intervals, `overlap_frac=0.1`) gives 18/15 and
**b₁ = 0**, missing the loop the cloud was built from. Kepler-Mapper's default
(10 cubes, `perc_overlap=0.5`) gives 16/16 and **b₁ = 1**, recovering it. Two
libraries, two defaults, opposite answers, no warning from either.

Say "matches the benchmark", not "correct". The benchmark exists here only
because the cloud is synthetic and its answer was known before it was built;
nothing in Definition 9.4 or Theorem 9.16 obliges a Mapper graph to recover it,
and Problem 2 shows a cover under which missing the loop is the *right* behaviour
for the graph it defines. What the comparison establishes is about **defaults**,
which is a fact about the libraries and not a verdict on their outputs. The discipline
is the one lab-01 derived for library defaults ("a default is part of the
citation") and lab-02 derived for filtration conventions ("never quote a
filtration value bare"), arriving here as: **never report a Mapper graph without
its cover parameters, because the defaults do not agree and one of them is wrong
on this data.**

(c) It establishes that **the two configured pipelines produce different results**,
and — given that both are built to Definition 9.4 with the same nominal
parameters — that the definition plus those parameters does not determine the
graph. The definition leaves genuine freedom and two careful implementations land
in different places.

It does **not** establish that neither has a bug, and the earlier draft of this
answer claimed exactly that, on the grounds that "both are computing the nerve of
a pullback cover". Neither is, quite. Definition 9.4 takes path-connected
components of f⁻¹(U_α); both pipelines substitute DBSCAN, and DBSCAN with
`min_samples=3` **discards points as noise**, so the clusters need not cover
f⁻¹(U_α) at all and the family is not a pullback cover in the definition's sense.
Two heuristics that differ may differ because the definition underdetermines them,
or because one of them has a defect, and this experiment does not separate those.
Doing so would mean comparing interval endpoints, per-point assignments, noise
handling, the clusters themselves and the edge rule — none of which is done here.

The honest verdict is therefore: *disagreement is expected and is not evidence of
a bug, and this comparison also does not exclude one.* That is still the sharp
contrast with lab-03, where the underlying object — the barcode — is unique by a
theorem, so disagreement there would have been decisive. Here no theorem makes
either answer the right one, which is why the disagreement is uninformative in
both directions.

(d) Something of the form: *state the lens as an explicit function, the cover's
type and every parameter (number of intervals, overlap fraction, and how the
endpoints are placed), the clustering algorithm and all of its parameters
including any that can discard points, the library and its exact version, and the
random seed if any step uses one. Report at least one neighbouring parameter
setting so a reader can see whether the figure is in a stable region or on a
boundary.* The last clause is the one Problem 2's table argues for and that
convention does not currently require.
</details>
