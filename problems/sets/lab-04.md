# lab-04 — Persistence diagrams and barcodes

**Module:** Computational Lab · **Unit:** lab-04
**Sources:** Oudot, *Persistence Theory: From Quiver Representations to Data
Analysis*, Chapter 1 "Algebraic persistence", printed **13–28** (folio =
PDF − 9). Specifically: **Theorem 1.1** (Krull–Remak–Schmidt), printed 16;
**Theorem 1.2** (Gabriel for Aₙ-type quivers), printed 17; **Theorem 1.4**
(Webb) and **Example 1.5**, printed 18; **Theorem 1.6** (Crawley-Boevey),
printed 19. Plus Edelsbrunner and Harer printed 181 for the multiplicity formula,
carried from lab-03. Plus executed code, in the environment pinned below. API
surfaces verified by execution: `gudhi.SimplexTree.persistence`,
`persistent_betti_numbers`, `num_simplices`.

**Oudot numbers his results.** Unlike Edelsbrunner, whose named-but-unnumbered
theorems left lab-02 and lab-03 with `UNCHECKED` coverage, this unit cites five
numbered theorems and gate 1 has a real denominator.

Carried: lab-03's Fundamental Lemma of Persistent Homology and its multiplicity
formula; lab-01's rule that an API's default is part of the citation.

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
for module in ("gudhi",):
    try:
        __import__(module)
        print("%-7s%s" % (module, "imports"))
    except Exception as exc:
        print("%-7s%s: %s" % (module, type(exc).__name__, exc))
```

```text id=env
python        3.11.11
gudhi         3.13.0
giotto-tda    0.6.2
numpy         1.26.4
gudhi  imports
```

---

## Problem 1 (medium — why a barcode exists at all)

lab-03 produced bars by pairing lowest ones. That is an algorithm, and it raises
a question it cannot answer: **why should the answer be a list of intervals?**
A persistence module is a sequence of vector spaces with linear maps between
them. Nothing in that description says it is a direct sum of intervals.

Oudot's Chapter 1 is the answer, and it is four theorems, not one, because the
answer depends on what you index by.

  (i) **Theorem 1.1** (Krull–Remak–Schmidt, printed 16): a finite-dimensional
  representation of a finite quiver decomposes into indecomposables, uniquely up
  to isomorphism and permutation.

  (ii) **Theorem 1.2** (Gabriel for Aₙ-type quivers, printed 17): every
  indecomposable finite-dimensional representation of an Aₙ-type quiver is an
  interval representation.

  (iii) **Theorem 1.4** (Webb, printed 18): any *pointwise finite-dimensional*
  representation of ℤ is a direct sum of interval representations.

  (iv) **Theorem 1.6** (Crawley-Boevey, printed 19): the same for any subposet
  T ⊆ ℝ.

(a) Build a small filtration and read its barcode.

```python id=module
import gudhi

FILT = [(("a",), 0.0), (("b",), 0.0), (("c",), 0.0), (("d",), 0.0),
        (("a", "b"), 1.0), (("b", "c"), 1.0),
        (("c", "d"), 2.0), (("a", "d"), 2.0),
        (("a", "c"), 3.0),
        (("a", "b", "c"), 4.0), (("a", "c", "d"), 4.0)]
LABEL = {"a": 0, "b": 1, "c": 2, "d": 3}

st = gudhi.SimplexTree()
for s, f in FILT:
    st.insert([LABEL[v] for v in s], filtration=f)
st.compute_persistence()
bars = sorted((dim, p[0], p[1]) for dim, p in st.persistence())
print("simplices %d" % st.num_simplices())
for dim, b, d in bars:
    print("  H%d  [%.1f, %s)" % (dim, b, "inf" if d == float("inf") else "%.1f" % d))
```

```text id=module
simplices 11
  H0  [0.0, 1.0)
  H0  [0.0, 1.0)
  H0  [0.0, 2.0)
  H0  [0.0, inf)
  H1  [2.0, 4.0)
  H1  [3.0, 4.0)
```

(b) **Which of the four theorems licenses this output?** Answer precisely. The
filtration takes five distinct values, so the index poset is finite; each vector
space is finite-dimensional. Name the theorem that applies, name the one that
would be needed if the index set were all of ℝ, and say why the difference is
invisible in the printout.

(c) Theorem 1.1 gives *existence and uniqueness of a decomposition into
indecomposables*; Theorem 1.2 identifies *what the indecomposables are*. Say why
both are needed, and what the barcode would be if only 1.1 held — what would you
have a list of?

(d) Oudot notes at printed 19 that for (ℤ, ≤) and (ℝ, ≤) "some intervals may be
left-infinite, or right-infinite, or both", and that since ℝ has limit points
"some intervals for (ℝ, ≤) may be open or half-open", neither of which happens
for Aₙ-type quivers. The printout shows one right-infinite bar and writes every
bar half-open as `[b, d)`. Say which of those two is forced by the mathematics
and which is a convention of the software, and how you would check.

<details><summary>Nudge</summary>
For (b): count the distinct filtration values.
For (c): indecomposable is not the same as interval.
</details>
<details><summary>Partial</summary>
(b) **Theorems 1.1 and 1.2 together.** Five distinct values means the index poset
is A₅, finite and Dynkin; every V_t is finite-dimensional; so 1.1 decomposes into
indecomposables and 1.2 says the indecomposables are intervals. If the index set
were all of ℝ you would need **Theorem 1.6** (Crawley-Boevey), with pointwise
finite-dimensionality as the hypothesis. The difference is invisible in the
printout because a barcode looks the same either way — which is exactly the
danger: the *output format* does not record which theorem produced it.

(c) 1.1 alone gives a decomposition into indecomposables, and an indecomposable
need not be an interval — for a general quiver there can be indecomposables of
arbitrarily large dimension, and the classification is, in Oudot's phrase,
"significantly harder if at all possible". Without 1.2 you would have a list of
*indecomposable modules*, with no reason to describe any of them by a pair of
numbers. Gabriel's theorem is what makes "birth, death" a complete description.

(d) The **right-infinite bar is forced**: the component born at 0.0 is never
killed, and the module genuinely has an interval unbounded on the right. The
**half-open `[b, d)` notation is the software's convention** — gudhi returns a
pair and the bracket style is this problem set's rendering of it. To check, look
for a feature whose birth and death coincide with filtration values and ask
whether the class is alive *at* the death value; the answer is a convention until
someone fixes an indexing scheme, and the honest citation names the library and
version.
</details>

---

## Problem 2 (hard — the diagram is the rank invariant, and here is the proof by execution)

lab-03 quoted the **Fundamental Lemma of Persistent Homology** (Edelsbrunner
printed 181): the persistent Betti numbers are determined by the diagram. This
problem runs the converse direction, which is what makes the diagram a
*sufficient* summary rather than merely a consistent one.

(a) Tabulate the rank invariant — the persistent Betti numbers β_p^{k,l} for
every pair of filtration values.

```python id=rank
VALUES = [0.0, 1.0, 2.0, 3.0, 4.0]

def beta(p, k, l):
    b = st.persistent_betti_numbers(k, l)
    return b[p] if p < len(b) else 0

for p in (0, 1):
    print("persistent Betti numbers beta_%d^{k,l}:" % p)
    print("      " + "".join("%6.1f" % l for l in VALUES))
    for k in VALUES:
        row = "".join(("%6d" % beta(p, k, l)) if k <= l else "     ." for l in VALUES)
        print("%5.1f " % k + row)
```

```text id=rank
persistent Betti numbers beta_0^{k,l}:
         0.0   1.0   2.0   3.0   4.0
  0.0      4     2     1     1     1
  1.0      .     2     1     1     1
  2.0      .     .     1     1     1
  3.0      .     .     .     1     1
  4.0      .     .     .     .     1
persistent Betti numbers beta_1^{k,l}:
         0.0   1.0   2.0   3.0   4.0
  0.0      0     0     0     0     0
  1.0      .     0     0     0     0
  2.0      .     .     1     1     0
  3.0      .     .     .     2     0
  4.0      .     .     .     .     0
```

(b) Now invert. Edelsbrunner's multiplicity formula at printed 181 recovers the
bars from the ranks by inclusion–exclusion on the grid.

```python id=recover
def mu(p, i, j):
    """Edelsbrunner printed 181: multiplicity by inclusion-exclusion on the grid."""
    a = beta(p, VALUES[i], VALUES[j - 1]) if j - 1 >= i else 0
    b = beta(p, VALUES[i], VALUES[j])
    c = beta(p, VALUES[i - 1], VALUES[j - 1]) if i >= 1 else 0
    d = beta(p, VALUES[i - 1], VALUES[j]) if i >= 1 else 0
    return (a - b) - (c - d)

for p in (0, 1):
    found = []
    for i in range(len(VALUES)):
        for j in range(i + 1, len(VALUES)):
            m = mu(p, i, j)
            if m:
                found.append((VALUES[i], VALUES[j], m))
    print("p=%d recovered from ranks alone: %s" % (p, found))

finite = [(dim, b, d) for dim, b, d in bars if d != float("inf")]
rebuilt = []
for p in (0, 1):
    for i in range(len(VALUES)):
        for j in range(i + 1, len(VALUES)):
            rebuilt += [(p, VALUES[i], VALUES[j])] * mu(p, i, j)
print("finite bars from persistence(): %s" % finite)
print("finite bars from ranks:         %s" % sorted(rebuilt))
print("agree: %s" % (sorted(finite) == sorted(rebuilt)))
```

```text id=recover
p=0 recovered from ranks alone: [(0.0, 1.0, 2), (0.0, 2.0, 1)]
p=1 recovered from ranks alone: [(2.0, 4.0, 1), (3.0, 4.0, 1)]
finite bars from persistence(): [(0, 0.0, 1.0), (0, 0.0, 1.0), (0, 0.0, 2.0), (1, 2.0, 4.0), (1, 3.0, 4.0)]
finite bars from ranks:         [(0, 0.0, 1.0), (0, 0.0, 1.0), (0, 0.0, 2.0), (1, 2.0, 4.0), (1, 3.0, 4.0)]
agree: True
```

The bars were recovered **without ever running the reduction algorithm** — only
from a table of ranks. Say what this establishes about the diagram as a summary,
and connect it to lab-03's statement that the Fundamental Lemma is what licenses
reasoning about data from the diagram alone.

(c) Read the recovery off the β₁ table by hand for the bar (2.0, 4.0). Write the
four entries the formula consumes, with their grid positions, and evaluate it.
Then say in words what the two subtractions are doing.

(d) The essential bar was not recovered.

```python id=essential
essential = [(dim, b) for dim, b, d in bars if d == float("inf")]
print("essential bars: %s" % essential)
print("recovered by the inclusion-exclusion formula: none, by construction")
print("reason: the formula needs a death index j, and these have none")
```

```text id=essential
essential bars: [(0, 0.0)]
recovered by the inclusion-exclusion formula: none, by construction
reason: the formula needs a death index j, and these have none
```

Say what has to be added to the rank invariant to pin down the essential classes
too, and whether their absence weakens the claim in (b). Then say which entry of
the β₀ table already tells you how many there are.

<details><summary>Partial</summary>
(b) It establishes that the diagram and the rank invariant carry **the same
information**: lab-03's lemma gives ranks from the diagram, and this computation
gives the diagram back from the ranks. So nothing is lost in passing to the
diagram, and lab-01's move — compute a diagram, then argue about the data from
the diagram — is justified rather than merely convenient. A summary that were
only *consistent* with the ranks could still have discarded something; this one
demonstrably has not.

(c) For (2.0, 4.0) with p = 1: i is the index of 2.0 (i = 2) and j the index of
4.0 (j = 4). The four entries are β(2.0, 3.0) = 1, β(2.0, 4.0) = 0,
β(1.0, 3.0) = 0, β(1.0, 4.0) = 0. So μ = (1 − 0) − (0 − 0) = 1. The first
subtraction counts classes alive at 2.0 that survive to 3.0 but not to 4.0 — that
is, that **die at 4.0**. The second removes those that were already alive at 1.0,
leaving only those **born at 2.0**. Born at 2.0 and dead at 4.0 is exactly the
bar.

(d) The essential classes need the ranks with l unbounded — or equivalently the
value β_p(k, ∞) — which is the number of classes alive at k that never die. Their
absence does not weaken (b), which was a claim about *finite* bars, but it does
mean "the rank invariant on the finite grid determines the barcode" is false as
stated and needs the infinite column. **β₀(4.0, 4.0) = 1 already gives the
count**: at the last filtration value one class is alive, and nothing can kill it
afterwards.
</details>

---

## Problem 3 (medium — the hypothesis, and why it is free here and not in general)

Every one of Oudot's decomposition theorems past 1.2 carries the hypothesis
**pointwise finite-dimensional**: each V_t is a finite-dimensional vector space.

(a) Check it on the module at hand.

```python id=pfd
dims = [st.persistent_betti_numbers(v, v) for v in VALUES]
print("dim V_t at each filtration value (p=0, p=1):")
for v, d in zip(VALUES, dims):
    print("  t=%.1f  %s" % (v, d))
print("every vector space finite-dimensional: %s"
      % all(all(x < float("inf") for x in d) for d in dims))
print("number of index values: %d (a finite poset, so an A_n quiver)" % len(VALUES))
```

```text id=pfd
dim V_t at each filtration value (p=0, p=1):
  t=0.0  [4, 0]
  t=1.0  [2, 0]
  t=2.0  [1, 1]
  t=3.0  [1, 2]
  t=4.0  [1, 0]
every vector space finite-dimensional: True
number of index values: 5 (a finite poset, so an A_n quiver)
```

(b) The hypothesis holds trivially, because the complex is finite. Compare this
with lab-01's finding that compactness and completeness hold trivially on a point
cloud, and say whether the two situations are the same. They are not — name the
difference, in terms of what the trivially-satisfied hypothesis is *for*.

(c) Oudot gives **Example 1.5** (printed 18, due to Webb) precisely to show the
hypothesis cannot be dropped: a representation of ℤ that is not pointwise
finite-dimensional and does not decompose into intervals. Say what such an example
proves about the theorems, and then say why no computation in this module could
ever produce one.

(d) So the hypothesis is free for everything the software computes. Write the
sentence a report should use, one sentence, that cites the right theorem without
overclaiming — noting that the *theory* the module talks about, ℝ-indexed and
stated in lab-05's stability theorem, needs the version with the hypothesis doing
real work.

<details><summary>Partial</summary>
(b) **Not the same.** In lab-01 the trivially-satisfied hypotheses —
compactness, completeness — were the *conclusions* of theorems the reader wanted
to apply, and their triviality meant those theorems said nothing useful about the
data. Here pointwise finite-dimensionality is a *hypothesis of a theorem whose
conclusion is doing real work*: it licenses the existence of the barcode. A
hypothesis being free is good news; a conclusion being free is bad news. lab-01's
situation was the second and this is the first.

(c) It proves the theorems are **sharp in that hypothesis** — the conclusion
genuinely fails without it, so it is not an artefact of the proof technique. No
computation here could produce one because a finite simplicial complex has finite
chain groups at every filtration value, so pointwise finite-dimensionality is a
consequence of finiteness and cannot be violated by any input the software
accepts.

(d) Something of the form: *the barcode exists by Gabriel's theorem
(Oudot Theorem 1.2, printed 17) applied to the Aₙ quiver of the n distinct
filtration values, the pointwise finite-dimensionality hypothesis being automatic
for a finite complex; the ℝ-indexed statements this module relies on downstream
rest instead on Crawley-Boevey's Theorem 1.6, printed 19, where that hypothesis is
a genuine restriction.*
</details>

---

## Problem 4 (hard — the strip, and an object that does not exist yet)

> The barcode is aa-20's decomposition made visible; this is the mission's
> central object.

(a) The strip credits `aa-20`, a Semester 3 unit that is not written. State what
this unit may therefore assume, and write the citation this lesson should use in
its place — naming a theorem and a page.

(b) "Made visible" is doing more work than it looks. The barcode and the
persistence diagram are two pictures of the same list of intervals: a bar
`[b, d)` becomes a point `(b, d)` above the diagonal. Say what each picture makes
easy to see that the other does not, and name the specific downstream operation —
it arrives in lab-05 — that requires the diagram rather than the barcode.

(c) "The mission's central object." Test the claim. lab-01 established that the
data has no topology and lab-03 that the reduction supplies no threshold. Say
what is left for the diagram to be central *to*, and identify the one property it
must have for the rest of the module to be possible at all. Name the unit that
supplies it.

(d) Oudot's Chapter 1 is titled "Algebraic persistence" and never mentions point
clouds, distances or noise. Say what that tells you about where the barcode's
existence comes from, and why that is reassuring rather than a gap.

<details><summary>Partial</summary>
(a) Nothing about `aa-20` may be assumed. The replacement citation is
**Theorem 1.2** (Gabriel for Aₙ-type quivers, Oudot printed 17) together with
**Theorem 1.1** (Krull–Remak–Schmidt, printed 16), or **Theorem 1.6**
(Crawley-Boevey, printed 19) for the ℝ-indexed case.

(b) The **barcode** makes lifetimes easy to compare — they are lengths, read off
against one axis, which is how lab-01's ratio of 98.1 was visible at a glance.
The **diagram** makes *distance between two summaries* easy to define, because
points can be matched to points and to the diagonal. The downstream operation is
the **bottleneck distance**, lab-05, which is a matching problem between two
diagrams and has no natural formulation on barcodes.

(c) What is left is being the object that everything downstream is a function of:
vectorisation in lab-06, features in lab-07, and any statement relating two
datasets. The property it must have is **stability** — that a small change to the
data produces a small change to the diagram — without which none of those
functions is meaningful. lab-05 supplies it.

(d) It tells you the barcode's existence is a fact of **linear algebra over a
poset**, not of geometry: nothing about sampling, noise, or metric spaces enters
the argument. That is reassuring, because it means the object is well defined
before any modelling assumption is made — the modelling assumptions enter later,
in what one is entitled to *infer* from it, which is where lab-05's hypotheses
live.
</details>
