# lab-09 — Mini-project: a full TDA analysis

**Module:** Computational Lab · **Unit:** lab-09
**Sources:** executed code, in the environment pinned below, plus the eight units
before it. Two results are used by name and are cited to their own books, since
the two number differently: **Theorem 13.1** (Λ∞ ≤ d_B, the landscape's
1-Lipschitz property) is Dey and Wang, printed 393, established in `lab-06`; and
**Corollary 3.6** (d_b(dgm f, dgm g) ≤ ‖f − g‖∞) is Oudot, printed 61, established
in `lab-05`. API surfaces verified by execution:
`gtda.homology.VietorisRipsPersistence` with `collapse_edges=True`,
`gtda.diagrams.PersistenceLandscape`.

Carried: everything. lab-01's point cloud with no topology and its ratio; lab-02's
choice of Rips and what it costs; lab-03's reduction; lab-04's barcode;
lab-05's 4δ threshold and its single modelling assumption; lab-06's landscape and
the discretisation caveat; lab-07's two negative controls; lab-08's parameter
sweep discipline.

**Source-boundary note.** The syllabus resource line names `giotto-tda examples
gallery` and `self-directed dataset`. The dataset here is **synthetic and seeded**,
because the gates forbid external requests and gate 9 forbids nondeterminism —
and because a synthetic torus is the only kind of data whose answer is known in
advance, which is what makes the comparison in Problem 3 possible at all. That is
a luxury the capstone's data will not provide, and Problem 5 says exactly which of
this unit's conclusions survive without it.

## The environment

```env
python==3.11.11
giotto-tda==0.6.2
persim==0.3.8
numpy==1.26.4
```

```python id=env
import sys
from importlib.metadata import version
print("%-18s%s" % ("python", ".".join(str(p) for p in sys.version_info[:3])))
for dist in ("giotto-tda", "persim", "numpy"):
    print("%-18s%s" % (dist, version(dist)))
for module in ("gtda.homology", "gtda.diagrams", "persim", "numpy"):
    try:
        __import__(module)
        print("%-18s%s" % (module, "imports"))
    except Exception as exc:
        print("%-18s%s: %s" % (module, type(exc).__name__, exc))
```

```text id=env
python            3.11.11
giotto-tda        0.6.2
persim            0.3.8
numpy             1.26.4
gtda.homology     imports
gtda.diagrams     imports
persim            imports
numpy             imports
```

---

## Problem 1 (medium — the data, and the null it will be measured against)

lab-07 established that a number without a control is not a measurement. So the
null is built at the same time as the data, before anything is computed.

```python id=data
import numpy as np

R, r, NOISE = 2.0, 1.0, 0.03

def torus(n, seed):
    """n points on a torus of radii R and r, plus isotropic Gaussian noise."""
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, 2 * np.pi, n)
    v = rng.uniform(0, 2 * np.pi, n)
    P = np.c_[(R + r * np.cos(v)) * np.cos(u),
              (R + r * np.cos(v)) * np.sin(u),
              r * np.sin(v)]
    return P + rng.normal(0, NOISE, P.shape)

def shuffle_coordinates(P, seed):
    """Permute each coordinate independently. Marginals identical, structure gone."""
    rng = np.random.default_rng(seed)
    return np.c_[rng.permutation(P[:, 0]),
                 rng.permutation(P[:, 1]),
                 rng.permutation(P[:, 2])]

X = torus(600, 20260820)
NULL = shuffle_coordinates(X, 7)
print("cloud %s from a torus, R = %.1f, r = %.1f, noise sd = %.2f"
      % (X.shape, R, r, NOISE))
print("null  %s, each coordinate independently permuted" % (NULL.shape,))
print()
print("%-22s %-26s %-26s" % ("", "torus", "null"))
print("%-22s %-26s %-26s" % ("coordinate means",
                             np.round(X.mean(0), 6), np.round(NULL.mean(0), 6)))
print("%-22s %-26s %-26s" % ("coordinate sds",
                             np.round(X.std(0), 6), np.round(NULL.std(0), 6)))
print("%-22s %-26s %-26s" % ("sorted x identical", "", np.array_equal(
    np.sort(X[:, 0]), np.sort(NULL[:, 0]))))
```

```text id=data
cloud (600, 3) from a torus, R = 2.0, r = 1.0, noise sd = 0.03
null  (600, 3), each coordinate independently permuted

                       torus                      null                      
coordinate means       [ 0.006128 -0.017759  0.034594] [ 0.006128 -0.017759  0.034594]
coordinate sds         [1.452814 1.508928 0.69931 ] [1.452814 1.508928 0.69931 ]
sorted x identical                                True                      
```

(a) The two clouds have identical coordinate means and identical coordinate
standard deviations, and the sorted x-coordinates are the same array. Say
precisely what class of alternative explanation this null rules out, and name the
construction in lab-07 that it is the geometric analogue of.

(b) It is not the strongest possible null. Name one structure that survives
independent coordinate permutation, and say what a null that destroyed it too
would look like.

(c) The noise level is `NOISE = 0.03` and it is written into the generator. Say
what lab-05's δ is here, why this unit is in an unusual position with respect to
it, and what changes when the data is not synthetic.

<details><summary>Nudge</summary>
For (a): what could a sceptic say about a long bar, if there were no null?
</details>
<details><summary>Partial</summary>
(a) It rules out **"the feature is an artefact of the marginal distributions"** —
that a cloud whose coordinates spread this way produces long H₁ bars whatever its
structure. Since the null's marginals are not merely similar but *identical*
(same multiset of values in each coordinate), any difference between the two
diagrams is attributable to the **joint** structure and to nothing else. It is the
geometric analogue of lab-07's **label permutation**: destroy the structure under
test while preserving everything else exactly, and see what the procedure reports.

(b) The **support's overall shape** survives: the permuted cloud still lies inside
the same bounding box, and the marginal of each coordinate still has the
double-peaked shape a torus induces. A stronger null would resample from a
distribution matched on the full radial profile — points at the same distances
from the centroid but with the angular structure randomised — which would leave
even less for the diagram to see.

(c) δ is 0.03, the standard deviation written into the generator. **This unit
knows δ exactly**, which lab-05 spent a whole segment establishing is the one
quantity no theorem supplies. Here it is supplied by the construction. On real
data it is not: δ becomes a claim about measurement, defended from instrument
specifications or a sampling model, and it is the weakest link in the chain
(lab-05, Problem 4(b)). Everything downstream that uses δ is, on real data,
conditional on that claim.
</details>

---

## Problem 2 (medium — the computation, once, with its conventions stated)

```python id=persistence
from gtda.homology import VietorisRipsPersistence

VR = VietorisRipsPersistence(homology_dimensions=[0, 1, 2], collapse_edges=True)

def lifetimes(P, dim, k=6):
    D = VR.fit_transform(P[None])[0]
    d = D[D[:, 2] == dim]
    return np.sort(d[:, 1] - d[:, 0])[::-1][:k]

h1, h2 = lifetimes(X, 1), lifetimes(X, 2)
n1, n2 = lifetimes(NULL, 1), lifetimes(NULL, 2)
print("six longest lifetimes, Vietoris-Rips over Z/2")
print()
print("%-10s %s" % ("torus H1", np.round(h1, 4)))
print("%-10s %s" % ("null  H1", np.round(n1, 4)))
print("%-10s %s" % ("torus H2", np.round(h2, 4)))
print("%-10s %s" % ("null  H2", np.round(n2, 4)))
print()
print("a torus has b0 = 1, b1 = 2, b2 = 1")
```

```text id=persistence
six longest lifetimes, Vietoris-Rips over Z/2

torus H1   [1.2965 1.2373 0.5997 0.5238 0.5233 0.495 ]
null  H1   [0.4192 0.3798 0.3684 0.3614 0.3442 0.3372]
torus H2   [0.6845 0.1078 0.1058 0.0943 0.0907 0.0861]
null  H2   [0.2195 0.1847 0.1693 0.1582 0.1503 0.1498]

a torus has b0 = 1, b1 = 2, b2 = 1
```

(a) Write the methods sentence for this computation. It must state every
convention that lab-02 established is not determined by the words "Vietoris–Rips":
the filtration parameter and what it measures, the field, the maximum dimension,
and anything the library chose for you.

(b) `collapse_edges=True` is not a default. Look up what it does, say whether it
can change the answer, and state the rule for reporting an option of that kind.

(c) The H₂ column is the cleanest signal in the whole module: 0.6845 against a
next-longest of 0.1078, a factor of 6.3, with the null's longest at 0.2195. Say
what that establishes about the cloud, and — carefully — what it does not.

(d) Compare the H₁ and H₂ columns as evidence. One of them answers its question
much more decisively than the other. Say which, give the numbers, and explain why
the *harder* of the two questions gets the *cleaner* answer here.

<details><summary>Partial</summary>
(a) Something of the form: *Vietoris–Rips persistent homology in dimensions 0, 1
and 2 over the field ℤ/2, computed with `gtda.homology.VietorisRipsPersistence`
(giotto-tda 0.6.2) on the full pairwise Euclidean distance matrix, with the
filtration parameter equal to the **diameter** of a simplex — so a 2-simplex on a
unit equilateral triangle enters at 1.0, not at the circumradius — with edge
collapse enabled and no maximum edge length imposed.* The diameter convention is
lab-02's finding and must be stated, because Edelsbrunner's Rips(r) uses diam ≤ 2r
and the same simplex would then be quoted as 0.5.

(b) Edge collapse replaces the complex with a smaller one having the same
persistent homology, so it is a **performance** option and not a modelling one: it
cannot change the barcode. The rule is nonetheless to report it, on the same
grounds as lab-01's library defaults — a reader reproducing the computation without
it will get the same answer more slowly, and a reader who cannot tell which kind of
option it is cannot know that. Report every non-default argument, and say for each
whether it is a performance choice or a modelling one.

(c) It establishes that this cloud's Rips filtration has exactly one long-lived
2-dimensional cycle, comfortably longer than anything the null produces. It does
**not** establish that the points lie on a torus, or that the cloud "has a void" —
those are claims about a space the sample came from, and every theorem in this
module relates a dataset to its own diagram (lab-05, repeatedly). It also does not
establish that b₂ = 1 for the underlying surface: b₂ of the *filtration* at the
relevant scale is what is measured.

(d) H₂ answers decisively (6.3× separation, null at 0.2195, three times below the
signal); H₁ does not (1.2373 against 0.5997 is 2.06×, and the null reaches 0.4192).
The harder question gets the cleaner answer because a torus has **one** void and
**two** independent loops, and the two loops are of quite different geometric
size — the meridian at radius r = 1 and the longitude at radius R = 2 — so they sit
at different places in the barcode and are competing with a crowd of
sampling-artefact loops that the void has no analogue of. Multiplicity, not
dimension, is what makes H₁ hard here.
</details>

---

## Problem 3 (hard — three thresholds, three answers, and the one that works has no theorem)

```python id=thresholds
def gap_count(L):
    """The largest ratio between consecutive lifetimes, and where it falls."""
    ratios = L[:-1] / L[1:]
    k = int(np.argmax(ratios)) + 1
    return k, float(ratios[k - 1])

print("three ways to decide how many H1 bars are real. the answer is 2.")
print()
stability = 4 * NOISE
null_max = float(n1[0])
k_gap, ratio = gap_count(h1)
print("%-42s %-12s %-8s" % ("rule", "threshold", "admits"))
print("%-42s %-12.4f %-8d" % ("lab-05 stability: lifetime > 4 delta",
                              stability, int((h1 > stability).sum())))
print("%-42s %-12.4f %-8d" % ("null-calibrated: longer than any null bar",
                              null_max, int((h1 > null_max).sum())))
print("%-42s %-12s %-8d" % ("largest lifetime gap", "ratio %.2f" % ratio, k_gap))
print()
print("of the six lifetimes shown, the stability rule admits all six,")
print("the null rule admits %d, and the gap rule admits %d." % (int((h1 > null_max).sum()), k_gap))
```

```text id=thresholds
three ways to decide how many H1 bars are real. the answer is 2.

rule                                       threshold    admits  
lab-05 stability: lifetime > 4 delta       0.1200       6       
null-calibrated: longer than any null bar  0.4192       6       
largest lifetime gap                       ratio 2.06   2       

of the six lifetimes shown, the stability rule admits all six,
the null rule admits 6, and the gap rule admits 2.
```

(a) The stability rule is **proved** — it follows from Oudot's **Corollary 3.6**,
printed 61, by lab-05's arithmetic — and it admits all six bars. Explain why that
is not a defect in the theorem, and state exactly what the rule guarantees and what
it does not. Use the words "sound" and "complete" and say which one it has.

(b) The null-calibrated rule is the strongest empirical control this module has
built, and it also admits six. Diagnose it: why does coordinate-shuffling a torus
leave bars of length 0.42, and what does that tell you about using a null to set a
threshold rather than to answer a yes/no question?

(c) The gap rule gives 2. It is **lab-01's ratio of 98.1**, which lab-05 examined
and declined to license, and it has no theorem behind it at all. Say what its
status is, and write the sentence a report should use when its conclusion rests on
it.

(d) A tempting move: use the null to *calibrate* rather than to threshold — for
instance, report the ratio of the observed bar to the null's longest. Compute it
for the top three bars and say whether it helps. Be honest about the answer.

<details><summary>Nudge</summary>
For (b): what does an independent permutation of three coordinates leave behind?
</details>
<details><summary>Partial</summary>
(a) It is not a defect: the rule is **sound and not complete**. Soundness means
every bar it rejects is genuinely rejectable — a bar shorter than 4δ *could* be
created or destroyed by noise of size δ, so rejecting it is safe. Completeness
would mean every bar it admits is real, and the rule makes no such claim: it says
nothing whatever about the six bars above 0.12 except that noise of size 0.03
cannot have manufactured them. With δ = 0.03 the threshold is simply far below the
scale at which sampling artefacts live, so the rule is true and uninformative. A
sound-but-not-complete rule is exactly what a worst-case guarantee is.

(b) Permuting each coordinate independently leaves a cloud filling roughly the same
box, at roughly the same density — and a dense cloud of 600 points in a box has a
Rips filtration with plenty of medium-lived 1-cycles, because at intermediate
scales the complex is neither disconnected nor filled in. 0.42 is the length of the
longest such accident. What it tells you: **a null is much better at answering "is
this bar distinguishable from nothing?" than at supplying a number.** Here the
answer to the yes/no question is clear for bars 1 and 2 (1.30 and 1.24 against
0.42) and it is the *threshold* reading — "everything above 0.42" — that fails,
because the null's own bars are not a model of this cloud's artefacts.

(c) Its status is a **heuristic with no guarantee**, and the evidence for it here is
that it gives the right answer on data whose answer is known, at four different
seeds. That is real evidence and it is evidence about this generator, not about the
rule. A report should say: *the number of features was determined by the largest
gap in the lifetime spectrum (ratio 2.06 between the 2nd and 3rd bars). This is a
heuristic with no stability guarantee; the sound threshold derived from the noise
level admits all six bars and the null-calibrated threshold admits six, so the
conclusion rests on the gap and not on either of them.*

(d) The ratios are 1.2965/0.4192 = 3.09, 1.2373/0.4192 = 2.95 and
0.5997/0.4192 = 1.43. It **does** help, and less than one would like: it separates
bars 1 and 2 from bar 3 by roughly a factor of two in ratio, which is the same
separation the gap rule found, expressed differently. It has not supplied
independent evidence — it has rescaled the same numbers by a constant. The honest
statement is that the null confirms bars 1 and 2 are far outside what structureless
data produces, and does not by itself decide whether bar 3 is in or out.
</details>

---

## Problem 4 (medium — does the answer survive a fresh sample?)

lab-08's discipline: report a neighbouring setting, so a reader can see whether
you are in a stable region or on a boundary. Here the setting is the sample.

```python id=seeds
print("does the gap rule give 2 every time? four fresh samples, n = 400.")
print()
print("%-8s %-40s %-8s %-8s" % ("seed", "four longest H1 lifetimes", "gap at", "ratio"))
for seed in (1, 2, 3, 4):
    P = torus(400, 20260820 + seed)
    L = lifetimes(P, 1, k=4)
    k, ratio = gap_count(L)
    print("%-8d %-40s %-8d %-8.2f" % (seed, np.round(L, 4), k, ratio))
```

```text id=seeds
does the gap rule give 2 every time? four fresh samples, n = 400.

seed     four longest H1 lifetimes                gap at   ratio   
1        [1.3421 1.1391 0.806  0.6812]            2        1.41    
2        [1.2018 1.1507 0.7295 0.6143]            2        1.58    
3        [1.2425 1.2074 0.6385 0.6341]            2        1.89    
4        [1.3005 1.1288 0.7141 0.5808]            2        1.58    
```

(a) Four for four. Say what this establishes and what it does not — in particular,
whether it is evidence about the gap rule or about something narrower.

(b) The ratios are 1.41, 1.58, 1.89 and 1.58, against 2.06 at n = 600. Say what
the drop from 600 to 400 points has done, and predict — with a reason, not a
guess — what happens at n = 200.

(c) At seed 3 the two long bars are 1.2425 and 1.2074 and the next two are 0.6385
and 0.6341 — two near-ties. Say why that pattern is expected for *this* generator,
and what a report should say about it.

(d) Four seeds is a small number. State how many you would run before publishing,
what statistic you would report, and what result would make you abandon the gap
rule for this dataset.

<details><summary>Partial</summary>
(a) It establishes that **for this generator, at this n, at these parameters, the
gap rule recovers b₁ = 2 in four of four samples.** It is evidence about the
generator far more than about the rule: a torus with R = 2 and r = 1 has two loops
of quite different size, both large relative to the sampling scale, and that is
what puts them above the artefact crowd. Nothing here suggests the rule works on a
shape whose features are closer together, and lab-01's question — what if the
ratio were 1.4? — is exactly the case it does not cover.

(b) Fewer points means a sparser sample, so the sampling-artefact loops live at
larger scales and the third bar rises: 0.5997 at n = 600 becomes 0.6385 to 0.806
at n = 400, while the two real bars barely move. The gap shrinks from 2.06 to
around 1.5. At n = 200 the prediction is that the artefact bars rise further and
the gap closes towards 1, because the artefact scale grows like the typical
nearest-neighbour distance while the real features are fixed by R and r. At some n
the rule will pick the wrong k, and it will do so without any signal that it has.

(c) Because a torus's two independent 1-cycles are the meridian and the longitude,
and although their *geometric* radii differ (1 and 2), their Rips lifetimes are set
by how long each survives before being filled in, which for this R and r is
similar — hence the near-tie at the top. The second near-tie is two artefacts of
comparable size, which is what a crowd looks like. A report should say that the two
leading bars are within 3% of each other and should **not** claim they are
distinguishable or rank them.

(d) At least 20, reporting the **distribution** of the inferred k and the
distribution of the gap ratio — median and range, not a mean. What would make me
abandon the rule: the inferred k varying across seeds at all. A rule that returns 2
in 18 of 20 samples and 3 in the other 2 has told you it cannot be used as a
decision procedure on data whose answer you do not know, which is the only
situation in which you need it.
</details>

---

## Problem 5 (hard — the report, and what survives leaving the laboratory)

```python id=landscape
from gtda.diagrams import PersistenceLandscape

D = VR.fit_transform(X[None])
L = PersistenceLandscape(n_layers=3, n_bins=100).fit_transform(D)[0]
print("landscape tensor per sample: %s  (dimension x layer, bins)" % (L.shape,))
print()
print("%-10s %-16s %-16s" % ("H1 layer", "peak height", "twice the peak"))
for k in range(3):
    peak = float(L[3 + k].max())
    print("%-10d %-16.4f %-16.4f" % (k, peak, 2 * peak))
print()
print("lab-06: a bar of lifetime L peaks at L/2, so 'lifetime > 4 delta'")
print("reads as 'peak > 2 delta' = %.4f" % (2 * NOISE))
```

```text id=landscape
landscape tensor per sample: (9, 100)  (dimension x layer, bins)

H1 layer   peak height      twice the peak  
0          0.6448           1.2896          
1          0.6148           1.2296          
2          0.2988           0.5975          

lab-06: a bar of lifetime L peaks at L/2, so 'lifetime > 4 delta'
reads as 'peak > 2 delta' = 0.0600
```

(a) Twice the layer peaks are 1.2896, 1.2296 and 0.5975; the three longest H₁
lifetimes are 1.2965, 1.2373 and 0.5997. They agree to about 0.5% and not exactly.
Give the two reasons, one of which lab-06 established and one of which is a
property of this diagram.

(b) `PersistenceLandscape` was used because **Theorem 13.1** (Dey and Wang,
printed 393) makes the landscape 1-Lipschitz in the bottleneck distance. State,
in three clauses, exactly what this unit's landscape numbers inherit from it — and
name the clause that fails, from lab-06.

(c) Now write the report. One paragraph of conclusion and one of disclosure. The
conclusion states what was found; the disclosure states every choice, every
control and every threshold, and it must be sufficient for a hostile reader to
reproduce the analysis and to see which of its conclusions rest on a theorem and
which on a heuristic.

(d) Finally, the transfer. The capstone's data will be real: the answer will not be
known, δ will not be written into a generator, and there will be no second sample
to test seed-stability with. Go through this unit's five conclusions one at a time
and mark each **survives**, **survives with a stated assumption**, or **does not
transfer**. Then say which single piece of the method you would keep if you could
keep only one.

<details><summary>Partial</summary>
(a) First, **discretisation**: `n_bins=100` samples the landscape on a grid, and
the true peak generally falls between grid points, so the reported peak is a
slight under-estimate — lab-06's finding, there worth 0.0032 on a grid of spacing
0.05 and here worth about 0.006. Second, **the layers are not the bars**: layer k
is the k-th upper envelope, and it equals the k-th tent only when the bars are
nested. These bars are not nested, so layer 1 dips where the two tents do not
overlap and its peak is not exactly half the second lifetime. The agreement is
close because the two long bars happen to overlap substantially, and that is a
property of this diagram, not a general fact.

(b) (i) Diagram to landscape function: **inherits Theorem 13.1 exactly** — the map
is 1-Lipschitz from the bottleneck distance. (ii) Landscape function to the
sampled array: **does not inherit it** — this is the clause that fails, and lab-06
measured a ratio of 1.0684 where the theorem permits 1, an excess of the order of
the grid spacing. (iii) Sampled array to the peak heights above: a maximum is
1-Lipschitz, so this step is safe. So the numbers are stable up to the
discretisation error, and the honest claim names the grid.

(c) Conclusion, roughly: *the cloud's Vietoris–Rips filtration carries two
long-lived 1-cycles (lifetimes 1.2965 and 1.2373) and one long-lived 2-cycle
(0.6845), against a coordinate-permuted null whose longest bars are 0.4192 and
0.2195 respectively. The counts are consistent with b₁ = 2, b₂ = 1.*
Disclosure, roughly: *Rips over ℤ/2, filtration by simplex diameter, dimensions 0
to 2, edge collapse on, no maximum edge length, giotto-tda 0.6.2 on Python 3.11.11
(full pins committed). 600 points, seed 20260820, noise sd 0.03. Null: each
coordinate independently permuted, seed 7; marginals identical by construction.
The number of H₁ features was determined by the **largest gap in the lifetime
spectrum**, a heuristic with no stability guarantee. The sound threshold from the
noise level (4δ = 0.12) admits all six leading bars, and the null-calibrated
threshold (0.4192) also admits six; neither supports the count of 2. The gap rule
returned 2 in four of four independent samples at n = 400, with gap ratios 1.41 to
1.89. Features were vectorised as persistence landscapes on a 100-point grid;
Theorem 13.1's 1-Lipschitz guarantee applies to the landscape function and not to
its grid samples.*

(d) **Survives:** the conventions disclosure (a) — it is about the computation, not
the data. **Survives:** the coordinate-permutation null — it is constructed from
whatever data you have. **Survives with a stated assumption:** the stability
threshold, conditional on a claimed δ, which becomes the report's weakest link.
**Does not transfer:** the comparison with the known answer, which is what
established here that the gap rule is the one that works. **Does not transfer:**
the seed sweep, since there is one sample — though a bootstrap or subsampling
sweep is its nearest available substitute and should replace it. If I could keep
one: **the null**, because it is the only one of the five that requires nothing
from outside the data and still rules something out.
</details>
