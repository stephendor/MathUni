# lab-09 — Mini-project: a full TDA analysis

**Module:** Computational Lab · **Unit:** lab-09
**Sources:** executed code, in the environment pinned below, plus the eight units
before it. Two results are used by name and are cited to their own books, since
the two number differently: Dey and Wang's **Theorem 13.1** (Λ∞ ≤ d_B, the landscape's
1-Lipschitz property), printed 393, established in `lab-06`; and Oudot's
**Corollary 3.6** (d_b(dgm f, dgm g) ≤ ‖f − g‖∞), printed 61, established
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

# A pin read from metadata does not load anything: importlib.metadata reads a
# .dist-info directory, so a distribution whose compiled extensions are missing
# reports its pinned version and fails later, in a block whose diff reads like a
# content error. Import what the later blocks use, at the submodule they use.
for module in ("gtda.diagrams", "gtda.homology", "numpy"):
    try:
        __import__(module)
        print("%-15s%s" % (module, "imports"))
    except Exception as exc:
        print("%-15s%s: %s" % (module, type(exc).__name__, exc))

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
    from gtda.diagrams import PersistenceLandscape
    from gtda.homology import VietorisRipsPersistence
    from numpy import abs, argmax, argsort, array, array_equal, c_, cos, linalg, pi, random, round, sin, sort

_api_surface()
```

```text id=env
python            3.11.11
giotto-tda        0.6.2
persim            0.3.8
numpy             1.26.4
gtda.diagrams  imports
gtda.homology  imports
numpy          imports
```

---

## Problem 1 (medium — the data, and the null it will be measured against)

lab-07 established that a number without a control is not a measurement. So the
null is built at the same time as the data, before anything is computed.

```python id=data
import numpy as np

R, r, NOISE = 2.0, 1.0, 0.03

def torus(n, seed):
    """n points on a torus of radii R and r, plus isotropic Gaussian noise.

    Returns the clean sample as well as the noisy one. NOISE is a standard
    deviation, and a Gaussian is unbounded: it is not a bound on how far any
    point moved. The stability theorem needs such a bound, so it has to be
    measured against the clean points rather than read off the generator.
    """
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, 2 * np.pi, n)
    v = rng.uniform(0, 2 * np.pi, n)
    P = np.c_[(R + r * np.cos(v)) * np.cos(u),
              (R + r * np.cos(v)) * np.sin(u),
              r * np.sin(v)]
    return P, P + rng.normal(0, NOISE, P.shape)

def shuffle_coordinates(P, seed):
    """Permute each coordinate independently. Marginals identical, structure gone."""
    rng = np.random.default_rng(seed)
    return np.c_[rng.permutation(P[:, 0]),
                 rng.permutation(P[:, 1]),
                 rng.permutation(P[:, 2])]

CLEAN, X = torus(600, 20260820)
DISPLACEMENT = np.linalg.norm(X - CLEAN, axis=1)
DELTA = float(DISPLACEMENT.max())

NULL_SEEDS = (7, 11, 13, 17, 19)
NULL = shuffle_coordinates(X, NULL_SEEDS[0])
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
print()
print("noise sd, a generator parameter        %.6f" % NOISE)
print("max Euclidean displacement, measured   %.6f" % DELTA)
print("mean displacement                      %.6f" % DISPLACEMENT.mean())
print("points displaced further than the sd   %d of %d"
      % (int((DISPLACEMENT > NOISE).sum()), len(X)))
```

```text id=data
cloud (600, 3) from a torus, R = 2.0, r = 1.0, noise sd = 0.03
null  (600, 3), each coordinate independently permuted

                       torus                      null
coordinate means       [ 0.006128 -0.017759  0.034594] [ 0.006128 -0.017759  0.034594]
coordinate sds         [1.452814 1.508928 0.69931 ] [1.452814 1.508928 0.69931 ]
sorted x identical                                True

noise sd, a generator parameter        0.030000
max Euclidean displacement, measured   0.131206
mean displacement                      0.047623
points displaced further than the sd   488 of 600
```

(a) The two clouds have identical coordinate means and identical coordinate
standard deviations, and the sorted x-coordinates are the same array. Say
precisely what class of alternative explanation this null rules out, and name the
construction in lab-07 that it is the geometric analogue of.

(b) It is not the strongest possible null. Name one structure that survives
independent coordinate permutation, and say what a null that destroyed it too
would look like.

(c) The noise level is `NOISE = 0.03` and it is written into the generator, so it
is tempting to say the unit knows lab-05's δ exactly. The last four lines of the
output say otherwise. Explain the discrepancy, say what δ actually is here, and
say what changes when the data is not synthetic.

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

(c) **δ is not 0.03.** lab-05's δ has to bound every point's Euclidean
displacement, and `NOISE` is the standard deviation of one Gaussian coordinate —
a scale parameter of an unbounded distribution, not a bound on anything. The
output makes the size of the confusion concrete: **488 of the 600 points moved
further than 0.03**, the mean displacement is 0.047623, and the largest is
0.131206. Reading σ as δ understates the true bound by a factor of 4.4 here, and
by an unbounded factor in principle, since a Gaussian has no maximum.

What δ *is* here is the measured maximum, **0.131206** — available because the
generator is ours and the clean sample can be kept. That is a legitimate δ and it
is exact, but note what makes it exact: not that the noise level is known, but
that the *realisation* is. Even a known σ would not supply a δ; a bounded noise
model would, and a Gaussian is not one.

On real data neither is available. δ becomes a claim about measurement, defended
from instrument specifications or a sampling model, and it is the weakest link in
the chain (lab-05, Problem 4(b)). Everything downstream that uses δ is, on real
data, conditional on that claim — and the mistake this problem exhibits, quoting a
standard deviation where a bound is required, is one the claim can easily
contain.
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
signal); H₁ does not (1.2373 against 0.5997 is 2.06×, and the null reaches 0.5012
at its worst seed).
The harder question gets the cleaner answer because a torus has **one** void and
**two** independent loops, and the two loops are of quite different geometric
size — the meridian at radius r = 1 and the longitude at radius R = 2 — so they sit
at different places in the barcode and are competing with a crowd of
sampling-artefact loops that the void has no analogue of. Multiplicity, not
dimension, is what makes H₁ hard here.
</details>

---

## Problem 3 (hard — four thresholds, four answers, and the one that works has no theorem)

```python id=thresholds
def gap_count(L):
    """The largest ratio between consecutive lifetimes, and where it falls."""
    ratios = L[:-1] / L[1:]
    k = int(np.argmax(ratios)) + 1
    return k, float(ratios[k - 1])

print("four ways to decide how many H1 bars are real. the answer is 2.")
print()

# One null draw is one number. Five pre-specified seeds give a range, and the
# threshold has to be taken from the top of it, not from whichever draw was run
# first -- otherwise the rule is calibrated on a coin flip.
null_maxima = np.array([float(lifetimes(shuffle_coordinates(X, s), 1)[0])
                        for s in NULL_SEEDS])
print("null longest-bar over %d pre-specified seeds: %s"
      % (len(NULL_SEEDS), np.round(null_maxima, 4)))
print("   min %.4f   mean %.4f   max %.4f"
      % (null_maxima.min(), null_maxima.mean(), null_maxima.max()))
print()

stability = 4 * DELTA
null_max = float(null_maxima.max())
k_gap, ratio = gap_count(h1)
print("%-42s %-12s %-8s" % ("rule", "threshold", "admits"))
print("%-42s %-12.4f %-8d" % ("naive: lifetime > 4 * noise sd",
                              4 * NOISE, int((h1 > 4 * NOISE).sum())))
print("%-42s %-12.4f %-8d" % ("lab-05 stability: lifetime > 4 delta",
                              stability, int((h1 > stability).sum())))
print("%-42s %-12.4f %-8d" % ("null-calibrated: longer than any null bar",
                              null_max, int((h1 > null_max).sum())))
print("%-42s %-12s %-8d" % ("largest lifetime gap", "ratio %.2f" % ratio, k_gap))
```

```text id=thresholds
four ways to decide how many H1 bars are real. the answer is 2.

null longest-bar over 5 pre-specified seeds: [0.4192 0.4584 0.4442 0.4006 0.5012]
   min 0.4006   mean 0.4447   max 0.5012

rule                                       threshold    admits
naive: lifetime > 4 * noise sd             0.1200       6
lab-05 stability: lifetime > 4 delta       0.5248       3
null-calibrated: longer than any null bar  0.5012       5
largest lifetime gap                       ratio 2.06   2
```

The stability rule's guarantee is about the diagram of the *clean* sample, not
about the torus. That is a different object and it is one we kept, so the claim
can be checked rather than asserted.

```python id=soundness
# Corollary 3.6 via lab-05's arithmetic: moving every point by at most delta moves
# each Rips filtration value by at most 2*delta, so d_b <= 2*delta -- NOT delta.
# A noisy bar longer than 4*delta is further than 2*delta from the diagonal, so no
# matching of cost 2*delta can send it there: it must have a partner in the CLEAN
# sample's diagram. That factor of 2 is the whole reason the threshold is 4*delta
# rather than 2*delta, so dropping it here would contradict the table above.
#
# What follows is NOT that matching. It reports, for each of the six longest noisy
# bars, the nearest point of the clean diagram -- six independent nearest
# neighbours, not a bijection. It is a consistency check the bound could have
# failed and did not; how far below 2*delta the distances sit says how loose the
# bound is on this data.
#
# Two columns are here to stop that consistency check being read as more than it
# is. "to diagonal" is what an optimal matching would pay to discard the bar
# instead of pairing it, and a bar is admitted exactly when that price exceeds
# 2*delta -- so the 4*delta rule IS the diagonal test, and for the bars it
# rejects the theorem positively permits the diagonal. "nearest" is the index of
# the clean point chosen, printed so that whether the six choices are distinct is
# a fact on the page rather than an assumption in the answer.
def diagram(P, dim):
    D = VR.fit_transform(P[None])[0]
    return D[D[:, 2] == dim][:, :2]

clean1, noisy1 = diagram(CLEAN, 1), diagram(X, 1)
print("clean sample H1, six longest: %s"
      % np.round(np.sort(clean1[:, 1] - clean1[:, 0])[::-1][:6], 4))
print("noisy sample H1, six longest: %s"
      % np.round(np.sort(noisy1[:, 1] - noisy1[:, 0])[::-1][:6], 4))
print()
print("%-4s %-10s %-12s %-12s %-12s %s"
      % ("bar", "lifetime", "admitted", "to diagonal", "sup dist to", "nearest"))
print("%-4s %-10s %-12s %-12s %-12s %s"
      % ("", "", "by 4 delta", "(discard it)", "nearest clean", "clean pt"))
order = np.argsort(noisy1[:, 1] - noisy1[:, 0])[::-1][:6]
chosen = []
for rank, k in enumerate(order, 1):
    point = noisy1[k]
    sup = np.abs(clean1 - point).max(axis=1)
    nearest = int(sup.argmin())
    chosen.append(nearest)
    print("%-4d %-10.4f %-12s %-12.6f %-12.6f %d"
          % (rank, point[1] - point[0],
             "yes" if point[1] - point[0] > 4 * DELTA else "no",
             (point[1] - point[0]) / 2, sup.min(), nearest))
print()
print("Corollary 3.6 allows d_b up to 2 delta:      %.6f" % (2 * DELTA))
print("largest of the six distances above:          %.6f"
      % max(float(np.abs(clean1 - noisy1[k]).max(axis=1).min()) for k in order))
print("the six nearest clean points are distinct:   %s"
      % ("yes" if len(set(chosen)) == len(chosen) else "no"))
print("bars whose diagonal cost is within 2 delta:  %d of 6"
      % sum(1 for k in order if (noisy1[k, 1] - noisy1[k, 0]) / 2 <= 2 * DELTA))
```

```text id=soundness
clean sample H1, six longest: [1.2963 1.2843 0.5425 0.5175 0.5161 0.5048]
noisy sample H1, six longest: [1.2965 1.2373 0.5997 0.5238 0.5233 0.495 ]

bar  lifetime   admitted     to diagonal  sup dist to  nearest
                by 4 delta   (discard it) nearest clean clean pt
1    1.2965     yes          0.648255     0.022348     99
2    1.2373     yes          0.618671     0.043158     99
3    0.5997     yes          0.299873     0.048810     71
4    0.5238     no           0.261920     0.015115     62
5    0.5233     no           0.261635     0.009466     62
6    0.4950     no           0.247477     0.019201     90

Corollary 3.6 allows d_b up to 2 delta:      0.262412
largest of the six distances above:          0.048810
the six nearest clean points are distinct:   no
bars whose diagonal cost is within 2 delta:  3 of 6
```

(a) The first row is the mistake Problem 1(c) diagnosed, kept in the table so the
size of it is visible: quoting 4 × the noise *standard deviation* gives 0.1200 and
admits all six bars. The second row is the rule actually licensed by Oudot's
**Corollary 3.6**, printed 61, via lab-05's arithmetic, using the measured
displacement bound: 4δ = 0.5248, admitting three.

Explain why admitting three — rather than the correct two — is not a defect in the
theorem, and state exactly what the rule guarantees and what it does not. Use the
words "sound" and "complete" and say which one it has. Then say which of the two
errors is more dangerous in a report: a threshold that is too low, or one that is
too high.

(b) The null-calibrated rule is the strongest empirical control this module has
built, and it admits five. Note first that it is computed from **five**
pre-specified seeds, not one: the null's longest bar ranges over 0.4006 to 0.5012
across them, so a single draw would have set the threshold anywhere in a band 25%
wide, and the first seed run happened to sit near the bottom of it. Diagnose the
rule: why does coordinate-shuffling a torus leave bars of length 0.4 to 0.5 at
all, and what does that tell you about using a null to set a threshold rather than
to answer a yes/no question?

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
(a) It is not a defect: the rule is **sound and not complete**, in the standard
directions. *Sound* means everything it asserts is true — every bar it admits has
a genuine partner in the clean sample's diagram, because a bar longer than 4δ sits
further than 2δ from the diagonal and **no matching of cost 2δ** can send it
there. Mind that factor. lab-05's arithmetic gives d_b ≤ **2δ**, not δ, because
moving every point by δ moves a Rips filtration value by up to 2δ — and it is
exactly that 2 which makes the threshold 4δ rather than 2δ. *Complete* would mean
everything true is asserted — every feature of the clean diagram is admitted —
and that fails: a genuine clean bar shorter than 4δ is **not guaranteed to be
admitted**. Not "is rejected": the rule is applied to the *noisy* bar, whose
lifetime need not equal its clean partner's, so a short clean feature can still
land above the threshold. The guarantee runs one way only. Sound and not complete
is exactly what a worst-case guarantee is: it never lies and it often says
nothing.

**The load-bearing word is "clean sample".** The `soundness` block prints that
diagram, and it has six long H₁ bars of its own: 1.2963, 1.2843, 0.5425, 0.5175,
0.5161, 0.5048. Each of the six longest noisy bars has a clean point within
0.0488, against a bound of 2δ = 0.2624 — a factor of five to spare.

Be exact about what that shows, because it is less than it looks. Six independent
nearest neighbours are not a bijection, and in this data they are not even
**injective**: bars 1 and 2 both choose clean point 99, and bars 4 and 5 both
choose point 62. The table cannot be promoted into a matching at all. It does not
*verify* the bottleneck bound; it is a consistency check the bound could have
refuted and did not, and the margin says the bound is loose here.

**And it establishes nothing whatever about bars 4, 5 and 6.** The `to diagonal`
column is what an optimal matching pays to *discard* a bar rather than pair it —
half its lifetime — and for those three the price is 0.261920, 0.261635 and
0.247477, every one of them **under 2δ = 0.262412**. A matching of cost 2δ is
therefore free to send all three to the diagonal, which is exactly to say the
theorem permits them to be artefacts of the noise. Finding a clean point nearby
does not forbid it: the theorem quantifies over *some* matching, and this table
reports the choices of a different procedure that is not one.

So the guarantee covers **bars 1, 2 and 3 and stops there** — precisely the three
the 4δ rule admits. The rule is not understating the theorem; it is stating it.
Read the two columns together and you can see why: a bar is admitted exactly when
discarding it would cost more than 2δ, so **the 4δ rule *is* the diagonal test**,
written in lifetimes instead of distances. That bars 4 to 6 have close clean
neighbours is a true observation about this pair of diagrams and carries no
guarantee at all.

And the torus has b₁ = 2, while the rule admits **three**. One guaranteed bar too
many is the whole of the argument, and bar 3 is it: the theorem hands it a partner
in the clean diagram, and the clean sample's own third-longest bar is 0.5425. So
the extra structure is a feature of the **clean 600-point sample**, not of the
surface it was drawn from: 600 points do not fill a torus, and the theorem's
guarantee has nothing to say about that, because sampling is not a displacement of
the points. Note that the argument now runs entirely on admitted bars — it never
needed the four it used to claim. This is the whole of the answer. The rule is not weak,
not misapplied and not approximate; it controls the wrong error. Substituting a
"sampling scale" for δ would make it bite and would silently convert Corollary 3.6
into a heuristic wearing its clothes.

Notice also how narrowly it gets three. Bars 4 and 5 are 0.5238 and 0.5233 against
4δ = 0.524824, missing by 0.2% and 0.3%; a δ of 0.130950 instead of 0.131206 would
return five. **The rule is sound, correctly applied, and its answer is balanced on
the fourth significant figure of δ** — which here is exact, and on real data is an
estimate. Any report using this rule should say how much δ would have to move to
change the count, because on this data the answer is: almost not at all.

On the two errors: **a threshold that is too low is the dangerous one**, and it is
the one the naive row commits. Too low, and the rule admits artefacts while still
carrying the word "proved" — it looks like a guarantee and is not one, because the
guarantee was never established for the δ actually used. Too high, and the rule
merely stays silent about real features, which is a loss of power and not a false
claim. Note that the naive error is also the *comfortable* one: 0.1200 admits
everything and so never contradicts a hoped-for conclusion.

(b) **First, what five draws cannot do.** Treated as a Monte Carlo permutation
test, five null draws bound the attainable p-value below at (0 + 1)/(5 + 1) =
0.167: even if every draw fell below the observed statistic, the smallest p-value
reportable is 0.17, which rejects nothing at any conventional level. Nothing here
is a test, and no p-value is claimed. The five seeds are a **variance probe** —
they exist to show that the number one draw hands you is not stable — and using
their maximum as a threshold is a conservative choice within that role, not a
test statistic. A report that wanted a p-value would need hundreds of draws and
would have to say so; a report that wants to know whether one draw is enough
needs about five, and the answer is no.

Permuting each coordinate independently preserves the sample size, each
coordinate's marginal distribution and the bounding box, and destroys the joint
distribution — which is the point. Say it that way rather than "the same density":
the torus cloud concentrates on a surface while the permuted cloud is spread
through the whole box, and that difference is exactly what the null is built to
create. A cloud of 600 points spread through a box has a Rips filtration with
plenty of medium-lived 1-cycles, because at intermediate scales the complex is
neither disconnected nor filled in. 0.4 to 0.5 is the length
of the longest such accident, and *which* value you get is itself a coin flip: the
five seeds give 0.4192, 0.4584, 0.4442, 0.4006 and 0.5012, a spread of 0.10 on a
quantity being used as a cutoff. Reporting the number from one draw would be
calibrating a threshold on a single sample of a random variable — the same error,
structurally, as reporting one cross-validation split in lab-07.

What it tells you: **a null is much better at answering "is this bar
distinguishable from nothing?" than at supplying a number.** The yes/no answer is
clear and stable for bars 1 and 2 (1.2965 and 1.2373 against a null maximum of at
most 0.5012 across every seed), and it is the *threshold* reading — "everything
above 0.5012 is real" — that fails, because the null's own bars are not a model of
this cloud's artefacts. The null is built by destroying the joint structure; the
artefacts in the real cloud are produced by *sparse sampling of a surface*, which
is a different mechanism, so there is no reason its upper tail should mark the
boundary between signal and artefact here.

(c) Its status is a **heuristic with no guarantee**, and the evidence for it here is
that it gives the right answer on data whose answer is known, at four different
seeds. That is real evidence and it is evidence about this generator, not about the
rule. A report should say: *the number of features was determined by the largest
gap in the lifetime spectrum (ratio 2.06 between the 2nd and 3rd bars). This is a
heuristic with no stability guarantee; the sound threshold derived from the
measured displacement bound (4δ = 0.5248) admits three bars and the
null-calibrated threshold (0.5012, the maximum over five pre-specified null draws)
admits five, so the conclusion rests on the gap and not on either of them.*

(d) Against the null's largest maximum, 0.5012, the ratios are 1.2965/0.5012 =
2.59, 1.2373/0.5012 = 2.47 and 0.5997/0.5012 = 1.20. It **does** help, and less
than one would like: it separates bars 1 and 2 from bar 3 by roughly a factor of
two in ratio, which is the same separation the gap rule found, expressed
differently. It has not supplied independent evidence — it has rescaled the same
numbers by a constant. The honest statement is that the null confirms bars 1 and 2
are far outside what structureless data produces, and does not by itself decide
whether bar 3 is in or out.

Note also that the ratio inherits the null's variability: computed against the
smallest of the five null maxima it reads 3.24, against the largest 2.59. A
"ratio to null" reported without saying which draw, or how many, is a number with
a 25% range hidden inside it.
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
    _, P = torus(400, 20260820 + seed)
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
print("reads as 'peak > 2 delta' = %.4f" % (2 * DELTA))
print("(reading it off the noise sd instead would give %.4f)" % (2 * NOISE))
```

```text id=landscape
landscape tensor per sample: (9, 100)  (dimension x layer, bins)

H1 layer   peak height      twice the peak
0          0.6448           1.2896
1          0.6148           1.2296
2          0.2988           0.5975

lab-06: a bar of lifetime L peaks at L/2, so 'lifetime > 4 delta'
reads as 'peak > 2 delta' = 0.2624
(reading it off the noise sd instead would give 0.0600)
```

(a) Twice the layer peaks are 1.2896, 1.2296 and 0.5975; the three longest H₁
lifetimes are 1.2965, 1.2373 and 0.5997. They agree to about 0.5% and not exactly.
Give the two reasons, one of which lab-06 established and one of which is a
property of this diagram.

(b) `PersistenceLandscape` was used because **Theorem 13.1** (Dey and Wang,
printed 393) makes the landscape 1-Lipschitz in the bottleneck distance. State,
in three clauses, exactly what this unit's landscape numbers inherit from it — and
name the clause that fails, from lab-06. Be careful about a detail lab-06's
counterexample does not settle: whether *sampling on a grid* is the culprit in
general, or only sampling as that particular implementation did it. The two calls
differ in whether one grid or two are involved.

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
sampled array: **it depends on the grid, and this is where the care is needed.**

If two diagrams are evaluated on **one shared grid**, sampling is just coordinate
projection and taking a maximum is 1-Lipschitz in the sup norm, so both steps are
non-expansive and the guarantee survives intact. lab-06's measured ratio of 1.0684
— above the permitted 1 — therefore does *not* show that sampling breaks the
theorem in general. It shows that one implementation's discretisation did, by
snapping values to its own grid rather than evaluating the landscape at the grid
points; the excess was of the order of the spacing, which is the signature of
snapping and not of projection.

If instead each diagram is passed through `fit_transform` **separately**, `fit`
derives the grid from whatever collection it saw, so the two arrays are sampled at
different abscissae. They are then not comparable coordinatewise at all, and the
question of a Lipschitz constant does not arise — the two vectors are not in the
same space, which is lab-06's persistence-image finding arriving in a second
guise. Clauses (i)–(iii) hold **for a fixed shared grid**; separately fitted,
data-dependent grids are simply outside Theorem 13.1's scope.

The practical rule: fit one transformer, then call `transform` for every diagram
being compared. (iii) Sampled array to the peak heights above: a maximum is
1-Lipschitz, so this step is safe. So the numbers are stable up to the
discretisation error, and the honest claim names the grid — and says that it is
one grid.

(c) Conclusion, roughly: *the cloud's Vietoris–Rips filtration carries two
long-lived 1-cycles (lifetimes 1.2965 and 1.2373) and one long-lived 2-cycle
(0.6845), against a coordinate-permuted null whose longest bars are 0.4192 and
0.2195 respectively. The counts are consistent with b₁ = 2, b₂ = 1.*
Disclosure, roughly: *Rips over ℤ/2, filtration by simplex diameter, dimensions 0
to 2, edge collapse on, no maximum edge length, giotto-tda 0.6.2 on Python 3.11.11
(full pins committed). 600 points, seed 20260820, Gaussian noise of standard
deviation 0.03; the perturbation bound used for stability is the **measured**
maximum displacement, δ = 0.131206, since a Gaussian standard deviation is not a
bound (488 of 600 points moved further than 0.03). Null: each coordinate
independently permuted, seeds 7, 11, 13, 17, 19; marginals identical by
construction; longest null bar 0.4006 to 0.5012 across the five.
The number of H₁ features was determined by the **largest gap in the lifetime
spectrum**, a heuristic with no stability guarantee. The sound threshold
(4δ = 0.5248) admits three of the six leading bars, and the null-calibrated
threshold (0.5012) admits five; neither supports the count of 2. The gap rule
returned 2 in four of four independent samples at n = 400, with gap ratios 1.41 to
1.89. Features were vectorised as persistence landscapes on a single 100-point grid
fitted once and applied to every diagram; Theorem 13.1's 1-Lipschitz guarantee
applies to the landscape function, and transfers to the samples only because the
grid is shared and fixed.*

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
