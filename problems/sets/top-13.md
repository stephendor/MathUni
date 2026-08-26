# top-13 — Quotient constructions: cones, suspension, CW complexes

**Module:** Topology · **Unit:** top-13
**Sources:** Munkres, *Topology*, 2nd ed. — §22 "The Quotient Topology"
(pp. 136–147), for the constructions and Theorem 22.2; and Hatcher, *Algebraic
Topology* — ch. 0, "Cell Complexes" (pp. 5–8) and "Operations on Spaces"
(pp. 8–10). Numbered results used: Munkres Theorem 22.1, Theorem 22.2,
Corollary 22.3.

Interleaves top-12 throughout — every construction below is a quotient in the
sense of §22 — and top-05, since each is a quotient of a *product* $X \times I$
and Hatcher's warning about the CW topology on a product is a statement about
Theorem 19.1's basis.

**This unit is cited by at1-01 and at1-02.** at1-01 uses the universal property
in the form "a map out of a quotient is continuous exactly when its composite
with the quotient map is", attributing it to top-13; that is Munkres's
Theorem 22.2, proved in top-12 from §22 and applied here. at1-02 says its own
operations on spaces are "top-13's quotient constructions". **at1-02 reads the
same Hatcher pages as this unit** and owns the homotopy-theoretic half —
Proposition 0.17, collapsing a contractible subcomplex, the two criteria for
homotopy equivalence. This unit owns the point-set half: what each construction
*is*, as a quotient. Nothing below uses homotopy equivalence.

Submit your written solutions via `/grade top-13`.

---

## Problem 1 (easy — cone and suspension, from the definitions)

Hatcher (p. 8): the **cone** on $X$ is $CX = (X \times I)/(X \times \{0\})$, and
the **suspension** $SX$ is the quotient of $X \times I$ obtained by collapsing
$X \times \{0\}$ to one point and $X \times \{1\}$ to another.

(a) Write down the partition of $X \times I$ whose quotient is $CX$, in
Munkres's sense (top-12, p. 139): list the classes and say which are singletons.
Do the same for $SX$, and say exactly how many non-singleton classes each has.
(b) Describe the saturated open sets for each partition. For $CX$, what must a
saturated open set containing the cone point contain?
(c) Hatcher writes that one can regard $SX$ "as a double cone on $X$, the union
of two copies of the cone $CX$". Make that precise as a statement about
subspaces of $SX$, and say which two subspaces of $X \times I$ they come from.
(d) Take $X = S^1$. Identify $CX$ and $SX$ concretely, and say which of your two
identifications this unit is entitled to *prove* and which it can only state —
recalling top-12's finding that Munkres proves neither of his own two headline
identifications.

*(Hatcher ch. 0, p. 8, for the cone, the suspension and the double-cone remark.
The partition machinery is Munkres §22, p. 139.)*

<details><summary>Nudge</summary>
For (b), the collapsed set is a single class, so a saturated open set meeting it
contains all of $X \times \{0\}$.
</details>
<details><summary>Strategy</summary>
(a) For $CX$: the classes are the singletons $\{(x,t)\}$ with $t > 0$, together
with the single class $X \times \{0\}$. One non-singleton class. For $SX$: two.
(c) The images of $X \times [0, 1/2]$ and $X \times [1/2, 1]$ under the quotient
map, each of which is a copy of $CX$, meeting in the image of
$X \times \{1/2\}$, a copy of $X$.
</details>
<details><summary>Partial</summary>
(d) $CS^1$ is the disc and $SS^1 = S^2$ — Hatcher says the motivating example is
$X = S^n$ with $SX = S^{n+1}$. The disc identification is the one to be careful
about: top-12's Example 4 is exactly the ball-with-boundary-collapsed, and
Munkres states its conclusion with "One can show that…".
</details>
<details><summary>Worked start</summary>
(a) *Cone.* Take $X^* = \{\{(x,t)\} : x \in X,\ 0 < t \le 1\} \cup \{X \times \{0\}\}$.
This is a partition of $X \times I$: the sets are pairwise disjoint and their
union is everything, since every point with $t > 0$ is in its own singleton and
every point with $t = 0$ is in the one big class. Exactly one class is not a
singleton.
⟨your step: the suspension partition, with its count⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — the universal property in use)

Munkres's **Theorem 22.2** (p. 142) says a map $g : X \to Z$ constant on the
fibres of a quotient map $p$ induces $f$ with $f \circ p = g$, and $f$ is
continuous if and only if $g$ is.

(a) State the property in the form at1-01 uses: a map out of a quotient is
continuous exactly when its composite with the quotient map is. Prove it is a
restatement of Theorem 22.2's continuity clause and not more.
(b) Use it to define the **suspension of a map**. Hatcher (p. 8): "a map
$f : X \to Y$ suspends to $Sf : SX \to SY$, the quotient map of
$f \times \mathbb{1} : X \times I \to Y \times I$." Check that $f \times \mathbb{1}$
followed by the quotient map $Y \times I \to SY$ is constant on the fibres of
$X \times I \to SX$, and conclude that $Sf$ exists and is continuous.
(c) Prove that $S(g \circ f) = Sg \circ Sf$ and $S(\mathbb{1}_X) = \mathbb{1}_{SX}$.
Say in one sentence what those two facts together assert about suspension, in
language cat-01 would use — but do not claim anything §22 does not give you.
(d) Show the same construction fails for a map *into* a quotient: given
$h : Z \to SX$, there is in general no map $Z \to X \times I$ inducing it. Say
which asymmetry of Theorem 22.2 this reflects.

*(Munkres §22, p. 142 for Theorem 22.2; Hatcher ch. 0, p. 8, for the suspension
of a map. cat-01 is on `main` and may be cited for vocabulary only.)*

<details><summary>Nudge</summary>
In (b), the fibres of $X \times I \to SX$ are $X \times \{0\}$, $X \times \{1\}$
and singletons — check the composite is constant on each.
</details>
<details><summary>Strategy</summary>
(b) $f \times \mathbb{1}$ carries $X \times \{0\}$ into $Y \times \{0\}$, which
the quotient map sends to a single point; likewise at $1$. So the composite is
constant on every fibre, and Theorem 22.2 applies.
(d) Theorem 22.2 governs maps *out* of a quotient only. A map into $SX$ need not
lift, and the quotient map is not injective, so there is no candidate inverse to
compose with.
</details>
<details><summary>Partial</summary>
(c) Both are immediate from uniqueness of the induced map: two maps agreeing
after composition with a surjection are equal. Together they say suspension takes
identities to identities and respects composition — which is what a functor does,
though §22 supplies no category and this unit claims none.
</details>
<details><summary>Worked start</summary>
(b) Write $p_X : X \times I \to SX$ and $p_Y : Y \times I \to SY$ for the
quotient maps, and put $g = p_Y \circ (f \times \mathbb{1})$.
The fibres of $p_X$ are $X \times \{0\}$, $X \times \{1\}$, and the singletons
$\{(x,t)\}$ for $0 < t < 1$. On singletons any map is constant. On
$X \times \{0\}$: $(f \times \mathbb{1})(x, 0) = (f(x), 0)$, and every point of
$Y \times \{0\}$ has the same image under $p_Y$, namely the first suspension
point of $SY$.
⟨your step: the $X \times \{1\}$ case, then apply Theorem 22.2 and say which of
its clauses gives continuity⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — the rest of the kit)

Hatcher pp. 9–10 gives three more constructions, all quotients.

(a) **Join.** $X * Y$ is the quotient of $X \times Y \times I$ under
$(x, y_1, 0) \sim (x, y_2, 0)$ and $(x_1, y, 1) \sim (x_2, y, 1)$. Write down
the partition. Then verify Hatcher's two remarks: that $CX$ is the case
$Y = \text{point}$, and that $SX$ is the case $Y = S^0$ (two points).
(b) **Wedge sum.** $X \vee Y$ is the quotient of the disjoint union
$X \amalg Y$ identifying chosen points $x_0$ and $y_0$. Write down the
partition, and prove that $S^1 \vee S^1$ is homeomorphic to a figure eight —
using Corollary 22.3 with top-08's Theorem 26.6, and saying which hypothesis of
that criterion you must check for $S^1 \amalg S^1$.
(c) **Smash product.** $X \wedge Y = (X \times Y)/(X \vee Y)$, where $X \vee Y$
is identified with $X \times \{y_0\} \cup \{x_0\} \times Y$ inside $X \times Y$.
Verify that this union really is a copy of the wedge sum — the key point is what
the two pieces have in common — and write down the partition.
(d) Each of the five constructions is a quotient of a product or a disjoint
union. For each, name the space being quotiented and the subspace being
collapsed, in a single table. Then say which one is *not* of the form
"collapse a subspace to a point" and what it does instead.

*(Hatcher ch. 0, p. 9 for the join; p. 10 for the wedge sum and smash product.
Munkres §22, p. 142, for Corollary 22.3; top-08's Theorem 26.6 is Munkres §26,
p. 167.)*

<details><summary>Nudge</summary>
In (c), the two copies intersect in exactly one point — which one?
</details>
<details><summary>Strategy</summary>
(a) With $Y$ a point, $X \times Y \times I \cong X \times I$ and the second
relation collapses $X \times \{1\}$ while the first is vacuous — giving $CX$ up
to the orientation of $I$.
(b) $S^1 \amalg S^1$ is compact, being a finite union of compact spaces; the
figure eight is Hausdorff as a subspace of $\mathbb{R}^2$; so a continuous
surjection between them is enough.
</details>
<details><summary>Partial</summary>
(c) $X \times \{y_0\}$ and $\{x_0\} \times Y$ intersect exactly at $(x_0, y_0)$,
which is what makes their union a wedge sum rather than a disjoint union.
(d) The join is the one that is not a single collapse: it collapses two different
subspaces in two different ways, one for each end of $I$.
</details>
<details><summary>Worked start</summary>
(a) The partition of $X \times Y \times I$: for $0 < t < 1$ the singletons
$\{(x,y,t)\}$; for $t = 0$ the classes $\{x\} \times Y \times \{0\}$, one for
each $x \in X$; for $t = 1$ the classes $X \times \{y\} \times \{1\}$, one for
each $y \in Y$.
⟨your step: check this is a partition, then set $Y$ to a point and to $S^0$ and
identify what you get each time⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — cell complexes, and where the topology is not the obvious one)

Hatcher builds a **cell complex** (p. 5) inductively: start with a discrete set
$X^0$, form $X^n$ from $X^{n-1}$ by attaching $n$-cells $e^n_\alpha$ via maps
$\varphi_\alpha : S^{n-1} \to X^{n-1}$, and either stop or take the union with
the weak topology.

(a) Write the attaching step as a quotient in Munkres's sense: identify the
space being quotiented and the partition. Then say which of top-12's results
tells you a map out of $X^n$ is continuous, and what it requires you to check.
(b) State the weak topology condition on $X = \bigcup_n X^n$ and say why it is
a condition rather than a consequence.
(c) **Hatcher's warning, p. 8.** "For completely general CW complexes $X$ and $Y$
there is one small complication: The topology on $X \times Y$ as a cell complex
is sometimes finer than the product topology, with more open sets than the
product topology has, though the two topologies coincide if either $X$ or $Y$ has
only finitely many cells, or if both $X$ and $Y$ have countably many cells."
State that as a precise claim about two topologies on one set, and say which
hypothesis in this unit's *mission strip* the finiteness clause corresponds to.
(d) Hatcher defers the point-set details: "The reader who wonders about various
point-set topological questions lurking in the background of the following
discussion should consult the Appendix for details" (p. 5), and the explanation
of the letters "CW" is likewise "given in the Appendix". Record what that means
for this unit: name one claim in (a)–(c) that you have verified from the pages
read, and one that you have not.

*(Hatcher ch. 0, p. 5 for cell complexes, the weak topology and the deferral to
the Appendix; p. 8 for the product warning. Munkres §22, p. 142, for
Theorem 22.2.)*

<details><summary>Nudge</summary>
In (a), attaching cells is a quotient of a disjoint union — compare the mapping
cylinder in at1-01's Problem 4.
</details>
<details><summary>Strategy</summary>
(a) $X^n$ is the quotient of $X^{n-1} \amalg \left(\coprod_\alpha D^n_\alpha\right)$
identifying each $x \in \partial D^n_\alpha$ with $\varphi_\alpha(x) \in X^{n-1}$.
Theorem 22.2 then says a map out of $X^n$ is continuous exactly when its
composite with the quotient map is — i.e. exactly when its restrictions to
$X^{n-1}$ and to each $D^n_\alpha$ are continuous and agree on the boundaries.
(c) The finiteness clause corresponds to the word "finite" in "Finite simplicial
and CW complexes"; without it the strip's spaces are not guaranteed to have the
product topology on products.
</details>
<details><summary>Partial</summary>
(b) A set $A \subset X$ is open iff $A \cap X^n$ is open in $X^n$ for each $n$.
It is a condition because $X$ is being *defined* as a set with a topology chosen;
nothing forces that choice.
(d) Verified: the quotient description of the attaching step, from the pages read.
Not verified: anything about what "CW" stands for, or the Appendix's point-set
results, which this unit has not read.
</details>
<details><summary>Worked start</summary>
(a) Let $A = X^{n-1} \amalg \left(\coprod_\alpha D^n_\alpha\right)$. Define a
partition of $A$: each point of $X^{n-1}$ together with all boundary points
mapping to it forms one class, i.e. the class of $y \in X^{n-1}$ is
$\{y\} \cup \bigcup_\alpha \varphi_\alpha^{-1}(y)$; and each interior point of
each $D^n_\alpha$ is its own class.
⟨your step: check this is a partition, then state what Theorem 22.2 gives you and
what you must check to use it⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — the mission strip, and the boundary with at1-02)

(a) This unit's mission strip reads: "Finite simplicial and CW complexes are the
spaces whose homology a computer can compute — the on-ramp to at1 and the lab."
Take it clause by clause. Which of the following appear anywhere in Munkres §22
or Hatcher ch. 0's "Cell Complexes" and "Operations on Spaces": simplicial
complexes; homology; an algorithm; the word "finite" as a hypothesis? Answer with
a page for each that does appear and a plain "not present" for each that does not.
(b) The strip says "finite … CW complexes". Using Hatcher's product warning from
Problem 4(c), give one concrete reason why the finiteness is not decoration —
that is, name a property that finite CW complexes have and general ones may not,
from the pages read.
(c) at1-02 has the title "CW complexes and operations on spaces" and reads
Hatcher pp. 5–14; this unit reads pp. 5–10. Set out what each unit owns, using
at1-02's own sentence — it says its operations "are top-13's quotient
constructions" — and identify the one result that both units could reasonably
claim. Recommend where it should live and why.
(d) at1-01 attributes to top-13 the universal property "a map out of a quotient
is continuous exactly when its composite with the quotient map is". That property
is Munkres's Theorem 22.2, which lives in §22 — the resource of **top-12**, and
also of this unit. Say whether at1-01's attribution is satisfied, and what a
syllabus pass should do about the fact that two units share the section.

*(Munkres §22, pp. 136–147; Hatcher ch. 0, pp. 5–10. Part (c) refers to
`problems/sets/at1-02.md` and part (d) to `lessons/at1/at1-01.html`, both on
`main`.)*

<details><summary>Nudge</summary>
For (a), search the pages you have actually read rather than recalling what
Hatcher's book contains elsewhere.
</details>
<details><summary>Strategy</summary>
(a) Simplicial complexes: not present in these pages — Hatcher's simplicial
homology is §2.1. Homology: not present. An algorithm: not present. "Finite" as a
hypothesis: present, on p. 8, in the product warning.
(c) at1-02 owns the homotopy-theoretic half — the contractible-subcomplex collapsing result, collapsing a
contractible subcomplex, the two criteria. This unit owns the point-set half.
The shared result is the description of the operations themselves.
</details>
<details><summary>Partial</summary>
(b) For finite CW complexes the cell-complex topology on a product agrees with
the product topology; for general ones it may be strictly finer. That is a
property of the finite case named on the page.
(d) Satisfied, but by a section shared between top-12 and top-13. A syllabus pass
should decide whether §22's universal property belongs to top-12's resources
alone, and whether at1-01's citation should be re-pointed.
</details>
<details><summary>Worked start</summary>
(a) *Simplicial complexes.* Search Hatcher pp. 5–10 and Munkres §22. Neither
defines a simplicial complex; Hatcher's are introduced with simplicial homology
in Chapter 2.
⟨your step: do the same for homology, for an algorithm, and for "finite" as a
hypothesis, giving a page for each that is present⟩

(b), (c), (d) ⟨your step⟩
</details>
