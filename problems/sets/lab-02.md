# lab-02 — Simplicial complexes: Vietoris–Rips and Čech

**Module:** Computational Lab · **Unit:** lab-02
**Sources:** Edelsbrunner and Harer, *Computational Topology: An Introduction*,
§III.2 "Convex Set Systems", printed **69–76** (folio = PDF − 12). Plus executed
code, in the environment pinned below. API surfaces verified by execution:
`gudhi.RipsComplex` (`max_edge_length`, `create_simplex_tree(max_dimension=…)`,
`distance_matrix=`), `gudhi.DelaunayCechComplex`
(`create_simplex_tree(output_squared_values=…)`), `SimplexTree.filtration`,
`SimplexTree.get_simplices`, `SimplexTree.num_simplices`.

**Results used, and how Edelsbrunner states them.** *Helly's Theorem*
(printed 69), the *Nerve Theorem* (printed 71), the *Vietoris–Rips Lemma*
(printed 74). **He numbers none of them** — they are named, not numbered, which
has a consequence for this repository recorded in the last problem.

Carried: lab-01's finding that a point cloud is discrete, and lab-01's citation
rule that an API's default is part of the citation.

## The environment

```env
python==3.11.11
gudhi==3.13.0
giotto-tda==0.6.2
numpy==1.26.4
```

```python id=env
import sys
from importlib.metadata import version
print("%-14s%s" % ("python", ".".join(str(p) for p in sys.version_info[:3])))
for dist in ("gudhi", "giotto-tda", "numpy"):
    print("%-14s%s" % (dist, version(dist)))

# A pin read from metadata does not load anything: importlib.metadata reads a
# .dist-info directory, so a distribution whose compiled extensions are missing
# reports its pinned version and fails later, in a block whose diff reads like a
# content error. Import what the later blocks use, at the submodule they use.
for module in ("gudhi", "numpy"):
    try:
        __import__(module)
        print("%-7s%s" % (module, "imports"))
    except Exception as exc:
        print("%-7s%s: %s" % (module, type(exc).__name__, exc))

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
    from gudhi import DelaunayCechComplex, RipsComplex
    from numpy import array, linalg, random, sqrt

_api_surface()
```

```text id=env
python        3.11.11
gudhi         3.13.0
giotto-tda    0.6.2
numpy         1.26.4
gudhi  imports
numpy  imports
```

---

## Problem 1 (easy–medium — one triangle, three numbers, none of them wrong)

lab-01 left the Vietoris–Rips complex as a black box. Open it on the smallest
example that can tell the two constructions apart: an equilateral triangle of
side 1.

(a) Build both complexes on it and read the filtration value of each simplex.

```python id=triangle
import numpy as np
import gudhi

tri = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, np.sqrt(3) / 2]])
rips = gudhi.RipsComplex(points=tri, max_edge_length=2.0).create_simplex_tree(max_dimension=2)
cech = gudhi.DelaunayCechComplex(points=tri).create_simplex_tree(output_squared_values=False)
print("%-10s %-22s %s" % ("simplex", "Rips filtration", "Cech filtration"))
for simplex in ((0, 1), (0, 2), (1, 2), (0, 1, 2)):
    r = rips.filtration(list(simplex))
    c = cech.filtration(list(simplex))
    print("%-10s %-22.5f %.5f" % (str(simplex), r, c))
```

```text id=triangle
simplex    Rips filtration        Cech filtration
(0, 1)     1.00000                0.50000
(0, 2)     1.00000                0.50000
(1, 2)     1.00000                0.50000
(0, 1, 2)  1.00000                0.57735
```

(b) Two things happened at once. Separate them.

  (i) Every edge is 1.00000 under Rips and 0.50000 under Čech, a clean factor of
  two on every simplex of dimension 1. Say what each library is measuring, and
  which of the two matches Edelsbrunner's Rips(r) = {σ : diam σ ≤ 2r}.

  (ii) The 2-simplex is at 1.00000 under Rips and 0.57735 under Čech, and
  0.57735 is **not** 1.00000 ÷ 2. Say why the factor of two fails exactly here,
  and identify 0.57735.

(c) Now the default. Re-read the Čech values without the flag.

```python id=squared
squared = gudhi.DelaunayCechComplex(points=tri).create_simplex_tree()
print("Cech, default             %.6f" % squared.filtration([0, 1, 2]))
print("Cech, output_squared_values=False  %.6f" % cech.filtration([0, 1, 2]))
print("square root of the default        %.6f" % np.sqrt(squared.filtration([0, 1, 2])))
print("1/sqrt(3), the circumradius       %.6f" % (1 / np.sqrt(3)))
```

```text id=squared
Cech, default             0.333333
Cech, output_squared_values=False  0.577350
square root of the default        0.577350
1/sqrt(3), the circumradius       0.577350
```

The same 2-simplex now carries **three** numbers — 1.00000, 0.57735, 0.33333 —
and every one of them is correct. Write the one-line citation that makes a
statement about "the filtration value of the triangle" unambiguous, in the form
lab-01 established.

<details><summary>Nudge</summary>
For (b)(ii): the circumcircle of an equilateral triangle of side 1.
</details>
<details><summary>Partial</summary>
(b)(i) gudhi's `RipsComplex` filters by the **diameter** — the longest edge —
so its parameter is Edelsbrunner's $2r$, not his $r$. gudhi's Čech filters by the
**radius** of the smallest enclosing ball. On a 1-simplex those differ by exactly
two, because the smallest ball enclosing two points has the segment as a
diameter. Edelsbrunner's Rips(r) matches the Čech-style parameter: at $r = 0.5$
his complex has all three edges, and gudhi reports them at `max_edge_length` 1.0.

(b)(ii) On a 2-simplex the diameter and the enclosing radius stop being
proportional. The smallest ball enclosing an equilateral triangle of side 1 is
its circumcircle, of radius $1/\sqrt{3} = 0.57735$, and $0.57735 \neq 0.5$. The
factor of two was never a fact about complexes; it was a fact about **two
points**.

(c) Something of the form: *gudhi 3.13.0,
`DelaunayCechComplex(points=…).create_simplex_tree(output_squared_values=False)`,
filtration = enclosing-ball radius.* Naming the version and the call is not
enough on its own — the default `output_squared_values=True` squares every value,
so the flag has to appear even when it is left alone.
</details>

---

## Problem 2 (medium — the theorem one of them has)

Edelsbrunner's §III.2 builds toward one result and states it without proof.

> **Nerve Theorem** (printed 71). *Let F be a finite collection of closed, convex
> sets in Euclidean space. Then the nerve of F and the union of the sets in F
> have the same homotopy type.*

He adds that the hypothesis can be relaxed: if the union is triangulable, the
sets are closed, and all non-empty common intersections are contractible, the
conclusion still holds.

(a) The Čech complex of S at radius r is the nerve of the balls of radius r
centred at the points of S (printed 72). Say, in one sentence, exactly what the
Nerve Theorem therefore buys — name the space Čech(r) is homotopy equivalent to,
and say why balls satisfy the hypothesis.

(b) Now the Vietoris–Rips complex, which Edelsbrunner motivates at printed 74:
"Instead of checking all subcollections, we may just check pairs and add 2- and
higher-dimensional simplices whenever we can." Rips(r) = {σ ⊆ S : diam σ ≤ 2r}.
**Is Rips(r) the nerve of the balls about the points of S?** Answer, and then say
what the Nerve Theorem gives you about the r-thickening of the data. Be exact,
and resist the wider claim: the question is about *these* balls, not about whether
some collection of convex sets somewhere has Rips(r) as its nerve.

(c) Witness the gap on the triangle of Problem 1, at r = 0.5.

```python id=nerve
centre = tri.mean(axis=0)
circumradius = np.linalg.norm(tri[0] - centre)
r = 0.5
pairwise = [np.linalg.norm(tri[i] - tri[j]) for i, j in ((0, 1), (0, 2), (1, 2))]
print("radius r                       %.5f" % r)
print("every pair of balls meets      %s" % all(d <= 2 * r + 1e-12 for d in pairwise))
print("circumradius                   %.5f" % circumradius)
print("all three balls share a point  %s" % bool(circumradius <= r + 1e-12))
print("so the 2-simplex is in Rips(r) but not in Cech(r)")
```

```text id=nerve
radius r                       0.50000
every pair of balls meets      True
circumradius                   0.57735
all three balls share a point  False
so the 2-simplex is in Rips(r) but not in Cech(r)
```

Edelsbrunner draws exactly this at printed 72 and remarks that the only
difference between the two complexes there "is the tenth triangle, which belongs
only to the former". Say what the union of the three balls at r = 0.5 looks like,
what Čech(0.5) is, what Rips(0.5) is, and which of the two has the homotopy type
of the union. Then say what Rips(0.5) has instead.

(d) The word "convex" in the Nerve Theorem is doing work. Edelsbrunner's
Figure III.6 shows four sets whose union is a disc with three holes and whose
nerve is the boundary of a tetrahedron — a sphere. State what that figure is a
counterexample to, precisely, and what it is *not* a counterexample to.

<details><summary>Nudge</summary>
For (b): count the collections of sets whose nerve could possibly be Rips.
</details>
<details><summary>Partial</summary>
(a) Čech(r) is homotopy equivalent to the union of the closed balls of radius r
about the points of S — that is, to the *r-thickening of the data*. Balls
qualify because a closed Euclidean ball is closed and convex, which is the
hypothesis verbatim.

(b) **Not of the balls, and so nothing about the data.** Rips(r) is not the nerve
of the radius-r balls about the points of S — Problem 2 exhibits three points
where it differs from Čech(r), which *is* that nerve — so the Nerve Theorem
attaches it to no union of balls and says nothing whatever about the r-thickening
of the data.

Be careful not to overstate this into the neat-sounding claim that Rips is the
nerve of *no* collection of convex sets. That is false: every finite simplicial
complex can be realised as the nerve of a collection of convex sets in a Euclidean
space of high enough dimension, and Rips(r) is a finite simplicial complex. But
such a realisation lives in an auxiliary space with no relation to where the data
sits, so its union is not the data thickened by anything, and the Nerve Theorem
applied to it computes the homotopy type of a set nobody asked about. **The
missing object is not convexity; it is a canonical realisation by the input's own
balls.** That is the central fact of the unit — the complex everyone computes is
not the one the theorem is about — and what Rips has instead is Problem 3's
sandwich.

(c) The union of three balls of radius 0.5 is three discs meeting pairwise in
lens-shaped regions, with a small curved triangular *hole* in the middle —
homotopy equivalent to a circle. Čech(0.5) is the boundary of a triangle: three
vertices, three edges, no 2-simplex. That is homotopy equivalent to a circle too,
which is the Nerve Theorem doing its job. Rips(0.5) is the *filled* triangle,
which is contractible. So Rips(0.5) gets the homotopy type wrong — it fills a
hole that is really there in the union — and it has no theorem to appeal to,
only the containments of Problem 3.

(d) It is a counterexample to the Nerve Theorem *with convexity dropped and
nothing put in its place*. It is **not** a counterexample to the relaxed version
Edelsbrunner states in the next sentence, because those four sets have a
non-empty common intersection pattern whose pieces are not all contractible; nor
is it a counterexample to anything about Čech complexes, whose sets are balls and
are convex.
</details>

---

## Problem 3 (medium–hard — the bridge, and what it costs)

Rips has no nerve theorem. What it has is this, and Edelsbrunner **proves** it at
printed 74–75:

> **Vietoris–Rips Lemma.** *Let S be a finite set of points in some Euclidean
> space and r ≥ 0. Then* Vietoris-Rips(r) ⊆ Čech(√2 · r).

Together with Čech(r) ⊆ Rips(r), which is immediate because Rips contains every
simplex its edges warrant, this sandwiches one complex between two copies of the
other.

(a) Implement the Čech membership test from the definition. A simplex σ is in
Čech(r) exactly when the balls of radius r about its vertices share a point,
which happens exactly when the **smallest enclosing ball** of σ has radius ≤ r.

```python id=cech-def
import itertools

def meb_radius(P):
    """Minimum enclosing ball radius, exactly, for 2 or 3 points in the plane."""
    if len(P) == 1:
        return 0.0
    if len(P) == 2:
        return float(np.linalg.norm(P[0] - P[1]) / 2)
    best = None
    for i, j in ((0, 1), (0, 2), (1, 2)):
        c = (P[i] + P[j]) / 2
        rad = np.linalg.norm(P[i] - P[j]) / 2
        if all(np.linalg.norm(p - c) <= rad + 1e-12 for p in P):
            if best is None or rad < best:
                best = rad
    if best is not None:
        return float(best)
    a, b, c2 = P
    ax, ay = a; bx, by = b; cx, cy = c2
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    return float(np.linalg.norm(a - np.array([ux, uy])))

print("triangle MEB radius  %.5f" % meb_radius(tri))
print("matches circumradius %s" % bool(abs(meb_radius(tri) - circumradius) < 1e-12))
```

```text id=cech-def
triangle MEB radius  0.57735
matches circumradius True
```

The function tries the three diametral balls before the circumcircle. Say why
that order is necessary and not merely an optimisation — name the shape of
triangle for which the circumcircle is the *wrong* answer.

(b) Check both containments on twelve random points, at three radii.

```python id=sandwich
rng = np.random.default_rng(7)
S = rng.uniform(0, 1, (12, 2))
D = np.linalg.norm(S[:, None, :] - S[None, :, :], axis=2)

# Split by dimension. The totals on their own cannot distinguish "the two
# definitions agreed" from "the two definitions could not have disagreed", and
# Problem 2(c) turns on exactly that distinction.
print("%-6s %-5s %-10s %-10s %-22s %s" % ("r", "dim", "|Cech(r)|", "|Rips(r)|", "Cech(r) not in Rips(r)", "Rips(r) not in Cech(sqrt2 r)"))
for r in (0.15, 0.25, 0.35):
    totals = [0, 0, 0, 0]
    for k in (2, 3):
        n_cech = n_rips = left = right = 0
        for idx in itertools.combinations(range(12), k):
            P = S[list(idx)]
            diam = max(D[i, j] for i, j in itertools.combinations(idx, 2))
            radius = meb_radius(P)
            in_rips = diam <= 2 * r
            in_cech = radius <= r
            n_rips += in_rips
            n_cech += in_cech
            if in_cech and not in_rips:
                left += 1
            if in_rips and not radius <= np.sqrt(2) * r:
                right += 1
        totals = [a + b for a, b in zip(totals, (n_cech, n_rips, left, right))]
        print("%-6.2f %-5d %-10d %-10d %-22d %d" % (r, k - 1, n_cech, n_rips, left, right))
    print("%-6.2f %-5s %-10d %-10d %-22d %d" % (r, "all", totals[0], totals[1], totals[2], totals[3]))
```

```text id=sandwich
r      dim   |Cech(r)|  |Rips(r)|  Cech(r) not in Rips(r) Rips(r) not in Cech(sqrt2 r)
0.15   1     8          8          0                      0
0.15   2     1          1          0                      0
0.15   all   9          9          0                      0
0.25   1     27         27         0                      0
0.25   2     18         18         0                      0
0.25   all   45         45         0                      0
0.35   1     48         48         0                      0
0.35   2     87         91         0                      0
0.35   all   135        139        0                      0
```

(c) At r = 0.15 and r = 0.25 the two complexes agree; at r = 0.35 they differ by
four. Say what those four simplices are. Then account for the agreement at the
smaller radii — and read the dimension rows before you do, because they rule out
one of the two explanations you are likely to reach for.

(d) The check reports zero violations in both directions at all three radii. Say
what that is and is not evidence for. In particular: the right-hand column tests
Rips(r) ⊆ Čech(√2 r), which is a **theorem**, so what did running it establish?
Compare your answer with lab-01 Problem 1(c).

(e) The constant √2 is not decoration. Edelsbrunner's proof computes the distance
from the origin to the barycentre of a standard d-simplex. State what would go
wrong with the sandwich if the constant were 1, and say — using Problem 2(c) —
why no constant smaller than some threshold can work.

<details><summary>Nudge</summary>
For (a): an obtuse triangle.
For (c): before assuming the smaller radii are edges only, count their triangles.
</details>
<details><summary>Partial</summary>
(a) For an **obtuse** triangle the circumcentre lies outside the triangle and the
smallest enclosing ball is the diametral ball on the longest side, which is
strictly smaller than the circumcircle. Returning the circumradius there would
overstate the Čech filtration value and put simplices into Čech(r) later than
they belong. The order is a correctness requirement.

(c) The four are 2-simplices — triples whose diameter is at most 0.7 but whose
smallest enclosing ball has radius above 0.35.

The agreement at the smaller radii is **not** forced by dimension, and the
dimension rows are what show it. On 1-simplices the two definitions genuinely do
**coincide** — the smallest ball enclosing two points has radius exactly half
their distance, so diam ≤ 2r and radius ≤ r are the same condition, and the edge
rows are therefore obliged to match at every radius, r = 0.35 included. But
neither complex is edges only: r = 0.15 already carries 1 triangle and r = 0.25
carries 18. Both radii were free to disagree and did not. What is true is a fact
about *this draw of twelve points* — every Rips triangle at those radii also
passes the Čech test, and at r = 0.35 four of the 91 stop doing so.

Dimension explains the edge rows. Geometry and the sample explain the triangle
rows, and the totals alone cannot tell the two apart — which is why the table
needed a dimension column before this question could be answered honestly.

(d) It is evidence about **the code**, not about the mathematics — the same
answer as lab-01 Problem 1(c), and worth having for the same reason. The
Vietoris–Rips Lemma is proved; the run cannot confirm it and could not have
refuted it. What a zero would have meant is that `meb_radius` or the diameter
computation is wrong. The left-hand column is the same: Čech(r) ⊆ Rips(r) is
immediate from the definitions. **A green column here certifies an
implementation, and the honest label for the whole table is "the code agrees
with two things already proved".**

(e) With constant 1 the containment is false, and Problem 2(c) is the
counterexample: the equilateral triangle at r = 0.5 is in Rips(0.5) and not in
Čech(0.5). Since its enclosing radius is $1/\sqrt3$ and its Rips radius is
$1/2$, any working constant must be at least $2/\sqrt3 \approx 1.1547$ for this
one simplex, so no constant below that can work in the plane. √2 is the bound
that works in **every** dimension, which is what the barycentre computation is
for.
</details>

---

## Problem 4 (medium — why anyone uses the one without the theorem)

(a) Rips is defined by checking pairs. Test what that means.

```python id=cost
from_points = gudhi.RipsComplex(points=S, max_edge_length=0.7).create_simplex_tree(max_dimension=2)
from_matrix = gudhi.RipsComplex(distance_matrix=D, max_edge_length=0.7).create_simplex_tree(max_dimension=2)
same = sorted(tuple(s) for s, _ in from_points.get_simplices()) == \
       sorted(tuple(s) for s, _ in from_matrix.get_simplices())
print("Rips from coordinates == Rips from the distance matrix: %s" % same)
print("simplices              %d" % from_points.num_simplices())
pairs = 12 * 11 // 2
triples = 12 * 11 * 10 // 6
print("pairwise distances Rips needs      %d" % pairs)
print("enclosing-ball problems Cech needs %d (one per triple, on top of the pairs)" % triples)
```

```text id=cost
Rips from coordinates == Rips from the distance matrix: True
simplices              151
pairwise distances Rips needs      66
enclosing-ball problems Cech needs 220 (one per triple, on top of the pairs)
```

State the property of Rips that the first line demonstrates, in one sentence, and
say why it is the reason lab-01's pipeline consumed the distance matrix `D` and
never the coordinates.

(b) The counts 66 and 220 are for twelve points and dimension 2 only. Write both
as functions of n and of the top dimension k, and say which one is the reason
Čech is rarely computed on real data.

(c) Here is the trade, stated plainly: **Čech has the theorem and Rips has the
algorithm.** Write the sentence a lab report should use when it computes Rips and
wants to say something about the shape of the data — one sentence, naming the
lemma and the constant, and conceding what is conceded.

(d) `gudhi` 3.13.0 offers `RipsComplex`, `AlphaComplex`, `DelaunayCechComplex`,
`DelaunayComplex`, `WitnessComplex` and others. It offers **no** `CechComplex`.
Given Problem 3(b), say why a library might reasonably decline to ship the plain
Čech complex, and what `DelaunayCechComplex` gives instead. Then say what a
reader must check before treating a `DelaunayCechComplex` result as a statement
about Čech.

<details><summary>Partial</summary>
(a) **Rips is determined by its 1-skeleton** — a simplex belongs exactly when all
its edges do — so the pairwise distances are the entire input and the coordinates
are surplus. That is why lab-01 said `D` is the metric space and `X` is only a
set of coordinates: every construction in this module past lab-01 consumes `D`.
Čech cannot be built from `D` in the same way, because the enclosing-ball radius
of a triple is a question about the ambient space.

(b) Separate two things the single phrase "the cost of Rips" runs together.

*What must be computed to determine the complex*: for Rips, $\binom{n}{2}$
distances, $O(n^2)$, whatever the top dimension — the 1-skeleton settles every
simplex, so no further geometry is ever consulted. For Čech, one
smallest-enclosing-ball problem per candidate simplex,
$\sum_{j \le k+1}\binom{n}{j}$, which is $O(n^{k+1})$; and the enclosing-ball
problem itself grows with the ambient dimension. **This is the contrast the unit
is about, and it is a contrast in the number of geometric predicates, not in the
size of the answer.**

*What must be enumerated and stored*: here the two are alike.
`create_simplex_tree(max_dimension=k)` builds the Rips complex explicitly, so it
enumerates up to $\sum_{j \le k+1}\binom{n}{j}$ simplices — the same count —
and without a dimension cap the complex can have $2^n - 1$ of them. Calling Rips
"$O(n^2)$" full stop therefore understates what a user of this lab will actually
wait for and store; the honest form is that Rips is *determined* by $O(n^2)$ data
and *materialised* at a cost exponential in $k$, exactly as Čech is. What Rips
saves is the predicate per simplex, and that is enough to explain why one of the
two is shipped by every library and the other by none.

(c) Something of the form: *we computed Rips(r); by the Vietoris–Rips Lemma it is
sandwiched, Čech(r) ⊆ Rips(r) ⊆ Čech(√2 r), so any feature persisting across a
range wider than a factor of √2 in radius is present in the Čech complex too, and
therefore in the thickened data — features narrower than that are not
distinguished by this argument.*

(d) Plain Čech on n points has $\binom{n}{j}$ simplices to test at each dimension
j, so shipping it invites users to run something intractable. `DelaunayCechComplex`
computes the Čech filtration **restricted to the Delaunay triangulation**, which
is far smaller and, for points in general position, has the same persistent
homology. The check before treating it as Čech: general position, and that the
question being asked is about persistent homology rather than about the complex
itself — the two complexes are genuinely different, and Problem 3's
simplex-counting test could not have been run with it.
</details>

---

## Problem 5 (hard — the strip, and a gate that cannot see this unit)

> Vietoris–Rips and Čech complexes are how raw points become something with
> computable homology.

(a) The strip is true and names both constructions. Audit the order it names them
in against Problem 2's finding, and say what a reader who stops at the strip will
believe about Vietoris–Rips that is false.

(b) "Computable" is the load-bearing word and it is doing two different jobs.
Separate them: for which of the two complexes does "computable" mean *cheap to
build*, and for which does it mean *provably about the data*? Then say whether
any single complex in this unit has both properties.

(c) Write the corrected strip: one sentence, keeping both names, and making the
asymmetry visible.

(d) **A finding about this repository, not about the mathematics.** Gate 1
cross-checks that a lesson covers every numbered result its problem set cites,
matching one of four keywords followed by a dotted number. This unit cites
Helly's Theorem, the Nerve Theorem and the Vietoris–Rips Lemma. Run the gate on
this unit and say what it reports and why. Then say which of these two is the
defect — the gate, or Edelsbrunner — and what the honest `--min-refs` value is
for a lab set sourced from this book.

(e) A second blind spot, found while writing part (d). The first draft of that
paragraph illustrated the gate's pattern by writing two example references out in
full, inside backticks, as specimens rather than as citations. Gate 1 read both
as citations of this unit and reported them missing from the lesson. Say what
distinction the gate is unable to draw, why no amount of widening its pattern
would fix it, and what that implies about the class of prose a coverage gate can
be run against.

<details><summary>Nudge</summary>
For (d): look at how Edelsbrunner labels his results, and then at the gate's
pattern.
</details>
<details><summary>Partial</summary>
(a) It names Vietoris–Rips first, and a reader who stops there will believe the
two are interchangeable routes to the same answer. They are not: only Čech has
the Nerve Theorem, and Problem 2(c) exhibits a case where Rips reports a
contractible complex for a union of balls that is homotopy equivalent to a
circle. **The strip is accurate and its ordering is misleading**, which is the
mildest possible form of the finding and still worth recording.

(b) *Cheap to build* is Rips, by Problem 4(a) — the 1-skeleton determines it, so
the geometric input is $O(n^2)$ distances and no per-simplex predicate at all
(the complex itself, once materialised, is as large as Čech's). *Provably about the data* is Čech, by the Nerve
Theorem — it is homotopy equivalent to the union of balls. **No complex here has
both**, and that is precisely why the Vietoris–Rips Lemma exists: it is the
device for borrowing the second property at a cost of √2 in scale.

(c) Something of the form: *the Čech complex is homotopy equivalent to the
thickened data and is expensive; Vietoris–Rips is cheap and is not, and the
Vietoris–Rips Lemma converts one into the other at a factor of √2 in radius.*

(d) The gate reports `UNCHECKED checked 0 refs - nothing to verify`, and exits 0.
The reason is that **Edelsbrunner numbers none of his results.** They carry names
— Helly's Theorem, Nerve Theorem, Vietoris–Rips Lemma — and the gate's pattern
requires a keyword followed by a digit, so it matches nothing here. Neither party
is defective: the gate encodes the citation style of the numbered textbooks the
other modules use, and Edelsbrunner's style is a legitimate alternative. What is
defective is treating the resulting exit code as coverage. **The honest
`--min-refs` for a lab set sourced from Edelsbrunner is 0, stated explicitly with
the reason, and the coverage this unit does have is carried by gate 9 and by the
source read-back instead.**

(e) The gate cannot distinguish **use from mention** — a reference being cited
from a reference being displayed as an example of what a reference looks like. No
widening helps, because the two are textually identical by construction: an
example of the pattern *is* an instance of the pattern. Backticks do not save it
either, since the gate reads the raw file and a citation inside code formatting is
still a citation elsewhere in the corpus. The implication is narrow but real: a
coverage gate can be run against prose that cites, and cannot be run against
prose that is *about* citing. This unit is the second kind, which is why its
honest reading is `UNCHECKED` and why part (d)'s paragraph now describes the
pattern instead of instantiating it.
</details>
