# lab-03 — Computing persistence; boundary-matrix reduction

**Module:** Computational Lab · **Unit:** lab-03
**Sources:** Edelsbrunner and Harer, *Computational Topology: An Introduction*,
§VII.1 "Persistent Homology", printed **179–186** — the Elder Rule and
filtrations (printed 181), the Fundamental Lemma of Persistent Homology
(printed 181), the reduction algorithm and R = ∂·V (printed 182), and the
uniqueness of the lowest ones (printed 183). Read alongside §IV.2 "Matrix
Reduction", printed **101–106**, which is where matrix reduction is introduced
for ordinary homology and which the tracker's resource line does not name.
Folio = PDF − 12. Plus executed code, in the environment pinned below. API
surfaces verified by execution: `gudhi.SimplexTree` (`insert` with `filtration=`,
`compute_persistence`, `persistence`).

**How Edelsbrunner labels things.** As in lab-02, **he numbers none of his
results** — the Elder Rule and the Fundamental Lemma of Persistent Homology are
named, not numbered — so gate 1 reports `UNCHECKED checked 0 refs` for this unit
and the honest `--min-refs` is 0. See lab-02 Problem 5 for why that is neither
the gate's defect nor the book's.

Carried: lab-02's filtration, and lab-01's rule that an API's default is part of
the citation.

## The environment

```env
python==3.11.11
gudhi==3.13.0
numpy==1.26.4
```

```python id=env
import sys
from importlib.metadata import version
print("%-14s%s" % ("python", ".".join(str(p) for p in sys.version_info[:3])))
for dist in ("gudhi", "numpy"):
    print("%-14s%s" % (dist, version(dist)))

# A pin read from metadata does not load anything: importlib.metadata reads a
# .dist-info directory, so a distribution whose compiled extensions are missing
# reports its pinned version and fails later, in a block whose diff reads like a
# content error. Import what the later blocks use, at the submodule they use.
for module in ("gudhi",):
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
    from gudhi import SimplexTree

_api_surface()
```

```text id=env
python        3.11.11
gudhi         3.13.0
numpy         1.26.4
gudhi  imports
```

---

## Problem 1 (easy–medium — a filtration you can hold in your head)

Everything in this unit runs on seven simplices. That is deliberate: the
algorithm is short enough to execute by hand, and a discrepancy between hand and
machine is then findable.

(a) The filtration: a triangle whose three edges arrive at times 1, 1 and 2, and
whose face arrives at 3.

```python id=filtration
FILT = [(("a",), 0.0), (("b",), 0.0), (("c",), 0.0),
        (("a", "b"), 1.0), (("b", "c"), 1.0), (("a", "c"), 2.0),
        (("a", "b", "c"), 3.0)]
IDX = {s: i for i, (s, _) in enumerate(FILT)}
m = len(FILT)

def faces(simplex):
    if len(simplex) == 1:
        return []
    return [tuple(simplex[:k] + simplex[k + 1:]) for k in range(len(simplex))]

print("simplices m = %d" % m)
print("faces precede cofaces: %s"
      % all(IDX[face] < IDX[s] for s, _ in FILT for face in faces(s)))
print("filtration monotonic:  %s"
      % all(FILT[IDX[face]][1] <= f for s, f in FILT for face in faces(s)))
```

```text id=filtration
simplices m = 7
faces precede cofaces: True
filtration monotonic:  True
```

Edelsbrunner requires f to be **monotonic** — non-decreasing along increasing
chains of faces, so that f(σ) ≤ f(τ) whenever σ is a face of τ (printed 181).
Say what monotonicity buys, in one sentence, naming the object that would fail to
exist without it. Then say why the *ordering* check and the *value* check are two
different conditions, and give a filtration that passes one and fails the other.

(b) Build the boundary matrix over ℤ/2. A column per simplex; the 1s in column j
mark the faces of simplex j.

```python id=boundary
D = [set(IDX[f] for f in faces(s)) for s, _ in FILT]
print("boundary matrix, one column per simplex (row indices of the 1s):")
for j, (s, f) in enumerate(FILT):
    print("  col %d  %-12s f=%.1f  %s" % (j, "".join(s), f, sorted(D[j]) or "-"))
```

```text id=boundary
boundary matrix, one column per simplex (row indices of the 1s):
  col 0  a            f=0.0  -
  col 1  b            f=0.0  -
  col 2  c            f=0.0  -
  col 3  ab           f=1.0  [0, 1]
  col 4  bc           f=1.0  [1, 2]
  col 5  ac           f=2.0  [0, 2]
  col 6  abc          f=3.0  [3, 4, 5]
```

Edelsbrunner notes at printed 182 that "since each simplex is preceded by its
proper faces, ∂ is upper triangular". Confirm that from the printout, and say
which check in part (a) is exactly the condition that makes it so.

(c) Working over ℤ/2 means the boundary has no signs and a column is just a set.
Say what is lost and what is gained, and name one thing about the resulting
homology that is *different* from homology over ℤ. Then say whether that
difference matters for the ranking lab-01 produced.

<details><summary>Nudge</summary>
For (a): what has to be a subcomplex for the filtration to be a filtration?
For (c): torsion.
</details>
<details><summary>Partial</summary>
(a) Monotonicity makes every sublevel set K(a) = f⁻¹(−∞, a] a **subcomplex**, and
without that there is no filtration at all — the sequence of sublevel sets would
contain sets that are not complexes, and homology would not be defined on them.
The two checks differ: the ordering check is about the *list*, that no simplex
appears before one of its faces, and the value check is about *f*. A filtration
with `(("a","b"), 1.0)` before `(("a",), 1.0)` passes the value check — the
values are equal, so f is monotonic — and fails the ordering check.

(b) Upper triangular: every 1 in column j sits in a row i < j. That is exactly
the *ordering* check, not the value check.

(c) Lost: orientation, and with it the ability to see torsion — over ℤ/2 the
Klein bottle and the torus are not distinguished in the way they are over ℤ.
Gained: a column is a set, addition is symmetric difference, and there is no
sign bookkeeping, which is why the algorithm below is fifteen lines.

What to say about lab-01's ranking is **less** than it is tempting to say. The
honest statement is that the ranking reported there is a ranking of ℤ/2 Betti
numbers, because that is what the software computed, and the coefficient field
belongs in the methods sentence for the same reason the filtration parameter
does. What does *not* follow is that the ranking would be the same over ℚ or ℤ.
Being sampled from a subset of ℝⁿ does not supply that: the Rips complex is a
*clique complex on a distance graph*, and its homotopy type is not constrained
to be that of the ambient region — this module's own lab-02 makes exactly that
point about the nerve. Nothing here establishes that these filtrations are
torsion-free, and nothing here needs it, as long as the claim stays inside the
field it was computed in.
</details>

---

## Problem 2 (medium — the algorithm, verbatim)

Edelsbrunner gives the algorithm at printed 182 in six lines:

> R = ∂;
> for j = 1 to m do
>   while there exists j′ < j with low(j′) = low(j) do
>     add column j′ to column j
>   endwhile
> endfor.

where low(j) is the row index of the lowest 1 in column j, undefined if the
column is zero. R is *reduced* when no two non-zero columns share a low.

(a) Implement it, and a deliberately different variant that keeps performing
legal column additions after the matrix is already reduced.

```python id=reduce
def low(col):
    return max(col) if col else None

def reduce_matrix(columns, exhaustive=False):
    """printed 182, verbatim; `exhaustive` keeps going past reduced form."""
    R = [set(c) for c in columns]
    adds = 0
    for j in range(len(R)):
        while True:
            lj = low(R[j])
            if lj is None:
                break
            rival = next((k for k in range(j) if low(R[k]) == lj), None)
            if rival is None:
                break
            R[j] ^= R[rival]
            adds += 1
        if exhaustive:
            for k in range(j):
                lk = low(R[k])
                if lk is not None and lk in R[j] and lk != low(R[j]):
                    R[j] ^= R[k]
                    adds += 1
    return R, adds

R1, adds1 = reduce_matrix(D)
print("column additions %d" % adds1)
print("reduced R:")
for j in range(m):
    print("  col %d  %-10s low=%s" % (j, str(sorted(R1[j])) if R1[j] else "-", low(R1[j])))
```

```text id=reduce
column additions 2
reduced R:
  col 0  -          low=None
  col 1  -          low=None
  col 2  -          low=None
  col 3  [0, 1]     low=1
  col 4  [1, 2]     low=2
  col 5  -          low=None
  col 6  [3, 4, 5]  low=5
```

(b) Column 5 — the edge `ac` — started as `[0, 2]` and reduced to zero. Trace the
two column additions by hand and say which columns were added to it. Then say
what a zero column *means*, in terms of cycles.

(c) Edelsbrunner writes the reduction in matrix form as **R = ∂·V**, with V
upper triangular, and says the j-th column of V "encodes the columns in ∂ that
add up to give the j-th column in R". The implementation above never builds V.
Say what is lost by not building it, and name one thing you would need V for.

<details><summary>Nudge</summary>
For (b): a zero column means the boundary of that simplex was already a boundary.
</details>
<details><summary>Partial</summary>
(b) Column 5 begins `[0, 2]` with low 2. Column 4 also has low 2, so column 4 is
added: `[0,2] ^ [1,2] = [0,1]`, low 1. Column 3 has low 1, so column 3 is added:
`[0,1] ^ [0,1] = {}`. Two additions, matching the printed count. A zero column at
j means the boundary of simplex j was already the boundary of something earlier —
so adding σ_j **creates a cycle** rather than killing one, and σ_j is a *birth*.

(c) V records the change of basis: it says *which* combination of original
columns produced each reduced one. Without it you get the barcode but not
representative cycles — you know a 1-cycle was born at radius 2.0 and died at
3.0, and you cannot say which edges it runs along. Any application that wants to
*localise* a feature on the data, rather than merely count it, needs V.
</details>

---

## Problem 3 (hard — the theorem that makes the answer well defined)

Edelsbrunner is careful at printed 183: the reduced matrix R "is not" unique —
"we may or may not continue the operations once we reached a reduced matrix" —
and he then shows **the lowest ones are unique** regardless.

(a) Test it. The `exhaustive` variant does exactly what he describes: it keeps
performing legal additions past the point of reduction.

```python id=uniqueness
R2, adds2 = reduce_matrix(D, exhaustive=True)
print("R1 == R2                : %s" % (R1 == R2))
print("low(j) for R1           : %s" % [low(c) for c in R1])
print("low(j) for R2           : %s" % [low(c) for c in R2])
print("lowest ones identical   : %s" % ([low(c) for c in R1] == [low(c) for c in R2]))
for j in range(m):
    if R1[j] != R2[j]:
        print("column %d differs        : %s vs %s" % (j, sorted(R1[j]), sorted(R2[j])))
```

```text id=uniqueness
R1 == R2                : False
low(j) for R1           : [None, None, None, 1, 2, None, 5]
low(j) for R2           : [None, None, None, 1, 2, None, 5]
lowest ones identical   : True
column 4 differs        : [1, 2] vs [0, 2]
```

Column 4 is `[1, 2]` in one reduction and `[0, 2]` in the other. Both are
correct. Say what the two columns have in common that forces the barcode to
agree, and state the consequence for anyone comparing two implementations of
persistence: what may differ, and what may not.

(b) Edelsbrunner's proof of uniqueness argues about the ranks of lower-left
submatrices R^j_i, which are invariant under left-to-right column operations.
Explain in one sentence why *left-to-right* is essential — what would break if
the algorithm were allowed to add a later column to an earlier one.

(c) Now the Betti numbers, by the count on printed 182:
β_p = #Zero_p − #Low_p.

```python id=betti
def dim_of(j):
    return len(FILT[j][0]) - 1

lows = [low(c) for c in R1]
for p in (0, 1):
    zero = sum(1 for j in range(m) if dim_of(j) == p and not R1[j])
    low_p = sum(1 for j in range(m) if lows[j] is not None and dim_of(lows[j]) == p)
    print("p=%d  #Zero_p=%d  #Low_p=%d  beta_p = %d" % (p, zero, low_p, zero - low_p))
```

```text id=betti
p=0  #Zero_p=3  #Low_p=2  beta_p = 1
p=1  #Zero_p=1  #Low_p=1  beta_p = 0
```

β₀ = 1 and β₁ = 0. Say what space those are the Betti numbers *of* — be precise,
because it is not the triangle at every stage — and check the answer against what
a filled triangle should give.

<details><summary>Partial</summary>
(a) They have the same **low**: 2 in both cases. The pairing is read off the lows
alone, so it is untouched, and the barcode is a function of the pairing. **What
may differ between two implementations: the reduced matrix, the number of column
additions, and the representative cycles. What may not: the lowest ones, the
pairing, and therefore the diagram.** A test that compares two persistence
implementations by comparing their matrices is testing the wrong object.

(b) Left-to-right is what makes V upper triangular, and upper-triangularity is
what makes the lower-left submatrix ranks invariant. Allowing a later column into
an earlier one would let the algorithm change a low that had already been fixed,
and the pairing would depend on the order of operations — exactly the
non-uniqueness the theorem rules out.

(c) Of the **final** complex K, the whole filled triangle: β₀ = 1 one component,
β₁ = 0 no holes, since the face is present and fills the loop. The count is over
the entire reduced matrix, so it describes the last complex in the filtration and
not the intermediate ones. The intermediate ones are what the *barcode* is for.
</details>

---

## Problem 4 (medium — reading the bars off the pairing, and checking against a library)

(a) The pairing rule: if low(j) = i then simplex i **births** a class that
simplex j **kills**, giving a bar from f(σ_i) to f(σ_j). A zero column whose
index is never a low births a class that never dies.

```python id=barcode
def barcode(R):
    pairs = {j: low(R[j]) for j in range(len(R)) if low(R[j]) is not None}
    born_and_died = set(pairs.values())
    bars = []
    for j, i in sorted(pairs.items()):
        if FILT[j][1] > FILT[i][1]:
            bars.append((dim_of(i), FILT[i][1], FILT[j][1]))
    for j in range(len(R)):
        if not R[j] and j not in born_and_died:
            bars.append((dim_of(j), FILT[j][1], float("inf")))
    return sorted(bars)

for name, R in (("standard", R1), ("exhaustive", R2)):
    print("%-11s %s" % (name, barcode(R)))
```

```text id=barcode
standard    [(0, 0.0, 1.0), (0, 0.0, 1.0), (0, 0.0, inf), (1, 2.0, 3.0)]
exhaustive  [(0, 0.0, 1.0), (0, 0.0, 1.0), (0, 0.0, inf), (1, 2.0, 3.0)]
```

The two reductions give the same barcode, as Problem 3 promised. Account for each
of the four bars in words — which simplex births it, which kills it, and what it
is geometrically.

(b) The `if FILT[j][1] > FILT[i][1]` test drops pairs whose birth and death have
the same filtration value. Say what such a pair is, why dropping it is right, and
what would appear in the barcode if it were kept.

(c) Check against a library that shares none of this code.

```python id=crosscheck
import gudhi

st = gudhi.SimplexTree()
label = {"a": 0, "b": 1, "c": 2}
for s, f in FILT:
    st.insert([label[v] for v in s], filtration=f)
st.compute_persistence()
theirs = sorted((d, p[0], p[1]) for d, p in st.persistence())
mine = barcode(R1)
print("gudhi      %s" % [(d, b, dd) for d, b, dd in theirs])
print("by hand    %s" % [(d, b, dd) for d, b, dd in mine])
print("agree      %s" % (theirs == mine))
```

```text id=crosscheck
gudhi      [(0, 0.0, 1.0), (0, 0.0, 1.0), (0, 0.0, inf), (1, 2.0, 3.0)]
by hand    [(0, 0.0, 1.0), (0, 0.0, 1.0), (0, 0.0, inf), (1, 2.0, 3.0)]
agree      True
```

This is a different kind of check from the ones in lab-01 and lab-02. Say how —
in those units the executed check confirmed a theorem already proved, and could
not have failed for mathematical reasons. Say what *this* check could genuinely
have caught, and what it therefore is evidence for.

<details><summary>Partial</summary>
(a) `ab` at 1.0 kills the component born by `b` at 0.0 → bar (0, 0.0, 1.0).
`bc` at 1.0 kills the component born by `c` → the second (0, 0.0, 1.0). `a`
births the component that never dies → (0, 0.0, ∞). `ac` at 2.0 creates the
1-cycle a→b→c→a, which `abc` at 3.0 fills → (1, 2.0, 3.0). Four bars, three
components merging to one and one hole.

(b) A pair born and killed at the same filtration value — a feature of zero
lifetime, present in the *index* filtration but not in the *value* filtration.
Dropping it is right because the bar is empty: it represents nothing that exists
at any value of the parameter. Keeping it would put points exactly **on the
diagonal** of the diagram, which is where Edelsbrunner puts points of infinite
multiplicity anyway (printed 181) — so they are harmless but uninformative, and
some libraries do emit them.

(c) Genuinely different. The theorem here — that the reduction computes
persistent homology — is proved, but **my implementation of it is not**, and
gudhi's is an independent code path with no shared lines. A disagreement would
have been a real bug in one of the two, and finding one would have been
informative rather than embarrassing. So this is evidence for *the
implementation*, which is exactly what lab-01 Problem 1(c) said an executed check
can buy — the difference being that here there was a real chance of failure.
</details>

---

## Problem 5 (hard — the strip, and the lemma that licenses the whole module)

> The computational heart: reducing boundary matrices IS computing homology
> (aa-18 made runnable).

(a) The strip's first clause is true, and Problem 3(c) is the demonstration:
β_p = #Zero_p − #Low_p reads Betti numbers straight off R. But the module does
not want Betti numbers; it wants barcodes. Say what the reduction gives *beyond*
the Betti numbers, and identify the exact line of the algorithm that produces
that extra information.

(b) The strip credits `aa-18`. That unit is Semester 3 and is not yet written.
State what this unit is therefore entitled to assume, and write the sentence this
lesson should use in place of "as aa-18 showed".

(c) The **Fundamental Lemma of Persistent Homology** (printed 181) says that for
every k ≤ l and every p, the persistent Betti number β_p^{k,l} is the sum of the
multiplicities μ_p^{i,j} over i ≤ k and j > l. Edelsbrunner comments: "It says
the diagram encodes the entire information about persistent homology groups."

State what would go wrong with this module if that lemma were false — name the
specific step in lab-01's pipeline that would become unjustified — and say
whether it is proved in the cited pages.

(d) A ranking, revisited. lab-01 produced six H₁ bars and a ratio of 98.1, and
said the threshold between signal and noise was the reader's. This unit has now
shown where the bars come from. Say whether anything in the reduction algorithm
supplies a threshold, and name the unit that will.

<details><summary>Nudge</summary>
For (a): the Betti-number count uses only whether a column is zero. What else does R carry?
</details>
<details><summary>Partial</summary>
(a) The **pairing**. The Betti count uses only *whether* each column is zero;
the barcode uses *which row* each low sits in, which pairs a birth simplex with a
death simplex and hence a birth value with a death value. The line that produces
it is `low(j)` itself — everything else in the algorithm exists to make that
value well defined.

(b) Nothing about `aa-18` may be assumed; it is unwritten. The unit is entitled
to the algorithm and the theorems in Edelsbrunner §VII.1, which it reads
directly. The sentence should be of the form: *the reduction is the algebra of
`aa-18`'s syllabus unit made executable; that unit is not yet written, and every
algebraic fact used here is taken from Edelsbrunner printed 182–183.*

(c) The lemma is what makes the **diagram** a sufficient summary. Without it a
diagram could lose information that the persistent homology groups contain, and
lab-01's entire move — compute a diagram, then reason about the data from the
diagram alone — would be unjustified at the first step. Every later unit inherits
the same dependency, and lab-05's stability theorem is a statement about diagrams
and would be about the wrong object. Edelsbrunner **states** it at printed 181;
the pages cited here do not prove it.

(d) **Nothing in the algorithm supplies a threshold.** The reduction is exact
linear algebra over ℤ/2 and returns every bar, including the six in lab-01, with
no notion of significance. A threshold has to come from a statement about how far
the diagram can move when the data moves — which is stability, and which is
lab-05.
</details>
