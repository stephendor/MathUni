# top-12 — The quotient topology

**Module:** Topology · **Unit:** top-12
**Sources:** Munkres, *Topology*, 2nd ed. — §22 "The Quotient Topology"
(pp. 136–147). Numbered results used: Theorem 22.1, Theorem 22.2,
Corollary 22.3.

Interleaves top-04 (a quotient map is a strengthening of continuity, and
Theorem 22.2 is the tool that makes maps out of quotients tractable — compare
Theorem 18.3), top-03 (Corollary 22.3(b) is about Hausdorffness) and top-05
(Example 7 is about products of quotient maps).

**This unit is cited by tda2-06.** Its mission strip reads: "The Reeb graph is
the quotient of $X$ by the relation 'lies in the same connected component of a
level set of $f$' — top-12's quotient topology applied to a scalar field", and
its Problem 1 is headed "the quotient that defines the graph [interleaves
top-12]". So what tda2-06 needs from here is exactly two things: the quotient
topology attached to an equivalence relation, and the universal property that
makes maps out of it checkable. Problems 2 and 4 are those.

Submit your written solutions via `/grade top-12`.

---

## Problem 1 (easy — quotient maps, and the two ways to be one)

$p : X \to Y$ surjective is a **quotient map** if a subset $U$ of $Y$ is open in
$Y$ **if and only if** $p^{-1}(U)$ is open in $X$ (p. 137).

(a) Show that a quotient map is continuous, and that the converse fails: give a
continuous surjection that is not a quotient map.
(b) Munkres notes that a surjective continuous map that is either an **open map**
or a **closed map** is a quotient map. Prove both, and say why neither
implication reverses.
(c) Verify Example 2: the projection $\pi_1 : \mathbb{R} \times \mathbb{R} \to \mathbb{R}$
is an open map and not a closed map. Give the closed set whose image is not
closed.
(d) A subset $A$ of $X$ is **saturated** with respect to $p$ if it contains every
set $p^{-1}(\{y\})$ that it intersects. Restate the definition of a quotient map
in terms of saturated sets, and verify your restatement against Example 1 —
$X = [0,1] \cup [2,3]$, $Y = [0,2]$, with $p$ the obvious map.

*(Munkres §22, p. 137 for the definition of a quotient map, open and closed maps,
saturated sets, and Examples 1 and 2.)*

<details><summary>Nudge</summary>
For (c), the hyperbola $xy = 1$ is closed in the plane; what is its image under
$\pi_1$?
</details>
<details><summary>Strategy</summary>
(a) Continuity is the "only if" half alone. For the converse, any continuous
bijection that is not a homeomorphism works — top-04's $F : [0,1) \to S^1$ is
one.
(d) $p$ is a quotient map iff it is surjective and carries saturated open sets to
open sets — equivalently, saturated closed sets to closed sets.
</details>
<details><summary>Partial</summary>
(c) $C = \{x \times y : xy = 1\}$ is closed in $\mathbb{R}^2$ and
$\pi_1(C) = \mathbb{R} - \{0\}$, which is not closed.
</details>
<details><summary>Worked start</summary>
(b) Suppose $p$ is a surjective continuous open map and let $U \subset Y$ with
$p^{-1}(U)$ open. Then $p(p^{-1}(U))$ is open, since $p$ is an open map; and
$p(p^{-1}(U)) = U$ because $p$ is surjective. So $U$ is open, which together with
continuity gives the biconditional.
⟨your step: the closed case, and then a quotient map that is neither open nor
closed — Example 1 is a candidate, so check it⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — from a partition to a space)

Munkres's construction (p. 139): let $X^*$ be a partition of $X$ into disjoint
subsets whose union is $X$, and let $p : X \to X^*$ send each point to the
element containing it. With the quotient topology induced by $p$, $X^*$ is a
**quotient space** of $X$.

(a) Prove that for any surjection $p : X \to A$ there is **exactly one** topology
on $A$ making $p$ a quotient map (p. 138). Uniqueness is the part with content;
say why.
(b) Munkres records the bridge this unit is cited for: "Given $X^*$, there is an
equivalence relation on $X$ of which the elements of $X^*$ are the equivalence
classes." Make it explicit in both directions — partition to relation and
relation to partition — and conclude that "the quotient of $X$ by an equivalence
relation $\sim$" is a definition, not an abuse of language.
(c) Prove Munkres's reformulation: "the typical open set of $X^*$ is a collection
of equivalence classes whose *union* is an open set of $X$."
(d) Work Example 5: $X = [0,1] \times [0,1]$, with $X^*$ consisting of the
one-point sets $\{x \times y\}$ for $0 < x,y < 1$, the two-point sets
$\{x \times 0, x \times 1\}$ and $\{0 \times y, 1 \times y\}$, and the four-point
set of corners. Describe three saturated open sets, one meeting the interior
only, one meeting an edge pair, one meeting the corner class. Then say in one
sentence what $X^*$ is.

*(Munkres §22, p. 138 for the uniqueness of the quotient topology; p. 139 for the
partition definition, the equivalence-relation remark, the reformulation, and
Examples 4 and 5.)*

<details><summary>Nudge</summary>
For (a), two topologies making $p$ a quotient map would have the same open sets
by the biconditional.
</details>
<details><summary>Strategy</summary>
(a) The collection $\{U \subset A : p^{-1}(U) \text{ open in } X\}$ is a topology
— check the three axioms using that $p^{-1}$ commutes with unions and
intersections — and it is forced, since the biconditional determines membership.
(b) From a partition, define $x \sim y$ iff they lie in the same block; from a
relation, take the set of classes. Each construction inverts the other.
</details>
<details><summary>Partial</summary>
(d) A saturated open set meeting an edge pair must contain both halves — an open
strip along the left edge together with the matching strip along the right. The
quotient $X^*$ is the torus.
</details>
<details><summary>Worked start</summary>
(a) *Existence.* Put $\mathcal{T} = \{U \subset A : p^{-1}(U) \text{ open in } X\}$.
Then $p^{-1}(\varnothing) = \varnothing$ and $p^{-1}(A) = X$ are open;
$p^{-1}(\bigcup U_\alpha) = \bigcup p^{-1}(U_\alpha)$ and
$p^{-1}(\bigcap_{i=1}^n U_i) = \bigcap_{i=1}^n p^{-1}(U_i)$ give the other two
axioms. And $p$ is a quotient map for $\mathcal{T}$ by construction.
⟨your step: uniqueness — suppose $\mathcal{T}'$ also makes $p$ a quotient map and
show $\mathcal{T}' = \mathcal{T}$ in one line. Say why this is the part that
needs the biconditional rather than mere continuity.⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — restricting a quotient map)

**Theorem 22.1** (p. 140): let $p : X \to Y$ be a quotient map, $A$ a subspace of
$X$ saturated with respect to $p$, and $q : A \to p(A)$ the restriction. Then
(1) if $A$ is open or closed in $X$, $q$ is a quotient map; (2) if $p$ is an open
map or a closed map, $q$ is a quotient map.

(a) Prove the two preliminary identities Munkres uses: $q^{-1}(V) = p^{-1}(V)$
for $V \subset p(A)$, and $p(U) = q(U)$ for $U \subset A$. Say where saturation
is needed.
(b) Prove (1) for $A$ open. Then prove (2) for $p$ open.
(c) Show the saturation hypothesis cannot be dropped: give a quotient map and a
non-saturated open subspace whose restriction is not a quotient map.
(d) Munkres's Example 7 asserts that "the product of two quotient maps need not
be a quotient map" (p. 143). State what that rules out, and contrast it with
top-05's Theorem 19.6 — which said maps *into* a product are governed
coordinatewise. Say why the two statements are compatible.

*(Munkres §22, p. 140 for Theorem 22.1 and its proof; p. 143 for Example 7.)*

<details><summary>Nudge</summary>
For (d), Theorem 19.6 is about the domain being arbitrary and the codomain a
product; Example 7 is about a map between two products.
</details>
<details><summary>Strategy</summary>
(a) Saturation is what makes $p^{-1}(V) \subset A$ for $V \subset p(A)$, so that
the restriction has the same preimages as the original.
(d) Theorem 19.6 characterises continuity of $f : A \to \prod X_\alpha$ by its
coordinate functions. Example 7 concerns $p \times q : X \times A \to Y \times B$,
a map whose *domain* is a product — the case top-04 recorded as having no
criterion. No conflict.
</details>
<details><summary>Partial</summary>
(a) For $V \subset p(A)$ and $A$ saturated, every point of $p^{-1}(V)$ lies in
$A$, since its class meets $A$; hence $q^{-1}(V) = p^{-1}(V)$.
</details>
<details><summary>Worked start</summary>
(b) Let $A$ be open and saturated, $V \subset p(A)$ with $q^{-1}(V)$ open in $A$.
Since $A$ is open in $X$, $q^{-1}(V)$ is open in $X$ (top-02, Lemma 16.2). By
(a), $q^{-1}(V) = p^{-1}(V)$, so $p^{-1}(V)$ is open in $X$, so $V$ is open in
$Y$ because $p$ is a quotient map.
⟨your step: conclude that $V$ is open in $p(A)$ — which needs one more remark
about $p(A)$ as a subspace of $Y$ — and then do case (2)⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — the universal property, which is what everyone actually uses)

**Theorem 22.2** (p. 142): let $p : X \to Y$ be a quotient map, $Z$ a space, and
$g : X \to Z$ constant on each set $p^{-1}(\{y\})$. Then $g$ induces
$f : Y \to Z$ with $f \circ p = g$; $f$ is continuous if and only if $g$ is; and
$f$ is a quotient map if and only if $g$ is.

(a) Prove the theorem. All three clauses. In the continuity half, the whole
argument is the identity $g^{-1}(V) = p^{-1}(f^{-1}(V))$; verify it and say which
property of $p$ turns it into the conclusion.
(b) State the universal property in the form at1-01 and at1-02 use it: *a map out
of a quotient is continuous exactly when its composite with the quotient map is.*
Show that this is Theorem 22.2's continuity clause and not more.
(c) Prove **Corollary 22.3**: for a surjective continuous $g : X \to Z$ and
$X^* = \{g^{-1}(\{z\})\}$ with the quotient topology, (a) $g$ induces a bijective
continuous $f : X^* \to Z$, a homeomorphism if and only if $g$ is a quotient map;
(b) if $Z$ is Hausdorff so is $X^*$.
(d) Combine Corollary 22.3(a) with top-08's Theorem 26.6 to get a working
criterion: if $X$ is compact, $Z$ is Hausdorff and $g : X \to Z$ is a continuous
surjection, then $X^*$ is homeomorphic to $Z$. Prove it, and then use it on
Example 4 — the closed unit ball with its boundary circle collapsed — to say
precisely what would still have to be supplied to conclude that $X^*$ is $S^2$.

*(Munkres §22, p. 142 for Theorem 22.2 and Corollary 22.3 with their proofs;
p. 139 for Example 4, whose conclusion is stated as "One can show that…" and not
proved. top-08's Theorem 26.6 is Munkres §26, p. 167.)*

<details><summary>Nudge</summary>
In (d), Theorem 26.6 needs a continuous bijection from a compact space to a
Hausdorff one.
</details>
<details><summary>Strategy</summary>
(a) Given $V$ open in $Z$: $g^{-1}(V)$ is open by continuity of $g$; it equals
$p^{-1}(f^{-1}(V))$; and $p$ being a quotient map converts "$p^{-1}(f^{-1}(V))$
open" into "$f^{-1}(V)$ open". The biconditional in the definition of a quotient
map is exactly what is consumed.
(d) $X^*$ is compact as a continuous image of $X$ (Theorem 26.5); $f$ is a
continuous bijection $X^* \to Z$; $Z$ is Hausdorff; so Theorem 26.6 makes $f$ a
homeomorphism.
</details>
<details><summary>Partial</summary>
(d) For Example 4 you would still need a continuous surjection from the closed
ball onto $S^2$ whose point-preimages are exactly the elements of Munkres's
partition. Munkres does not construct one — he writes "One can show that $X^*$ is
homeomorphic with… $S^2$" and leaves it.
</details>
<details><summary>Worked start</summary>
(a) *Existence of $f$.* For each $y \in Y$ the set $g(p^{-1}(\{y\}))$ is a single
point of $Z$, since $g$ is constant there; call it $f(y)$. Then
$f(p(x)) = g(x)$ for every $x$, i.e. $f \circ p = g$.
*Continuity, one way.* If $f$ is continuous then $g = f \circ p$ is a composite
of continuous maps, hence continuous.
*Continuity, the other way.* Let $V$ be open in $Z$. Then $g^{-1}(V)$ is open in
$X$. ⟨your step: verify $g^{-1}(V) = p^{-1}(f^{-1}(V))$ from $f \circ p = g$, then
apply the definition of a quotient map to conclude $f^{-1}(V)$ is open in $Y$⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — what a quotient can destroy, and the tda2-06 clause)

(a) Corollary 22.3(b) says a quotient of a space mapping onto a Hausdorff $Z$ is
Hausdorff. Show that quotients do **not** preserve Hausdorffness in general:
give a Hausdorff $X$ and a partition $X^*$ with $X^*$ not Hausdorff. Then say
what Corollary 22.3(b) is really assuming.
(b) Work Munkres's Example 6: $X$ the union of the segments
$[0,1] \times \{n\}$ for $n \in \mathbb{Z}_+$, and $Z$ the union of the segments
from the origin through $x \times (x/n)$. Say what the natural map $X \to Z$ does,
and why it is a continuous bijection on each piece yet not a quotient map. Which
hypothesis of Problem 4(d)'s criterion fails?
(c) **The tda2-06 clause.** That unit's mission strip says the Reeb graph is "the
quotient of $X$ by the relation 'lies in the same connected component of a level
set of $f$' — top-12's quotient topology applied to a scalar field". Using
Problem 2(b), state precisely what §22 supplies for that sentence and what it does
not. In particular: does §22 guarantee the resulting quotient is a graph, is
Hausdorff, or is anything other than a topological space?
(d) The mission strip of *this* unit calls quotients "the fourth and most
geometric rehearsal of the collapse move". Take the geometric half seriously:
using Example 5, describe the partition of the square whose quotient is the
torus, and identify which element of the partition has four points and why it
must. Then say what §22 does **not** provide about the torus — specifically,
whether §22 proves the quotient is homeomorphic to a torus, or merely constructs
it.

*(Munkres §22, p. 142 for Corollary 22.3; pp. 142–143 for Example 6; p. 139 for
Example 5. Part (c) refers to `lessons/tda2/tda2-06.html`, already on `main`;
part (d) concerns this unit's own mission strip.)*

<details><summary>Nudge</summary>
For (a), collapse a closed set and a point that cannot be separated from it after
the collapse — $\mathbb{R}$ with $\mathbb{Z}$ collapsed to a point is a standard
try.
</details>
<details><summary>Strategy</summary>
(c) §22 supplies the topology on the set of equivalence classes and the universal
property for maps out of it. It supplies nothing about the classes being points
of a graph, and nothing about Hausdorffness — Corollary 22.3(b) needs a
Hausdorff target and a map onto it, which is an extra hypothesis, not a
consequence.
(d) §22 constructs the quotient and describes its saturated open sets. Munkres
does not prove the quotient is homeomorphic to the torus in §22; Example 5 states
the partition and the figures show it.
</details>
<details><summary>Partial</summary>
(a) $\mathbb{R}/\mathbb{Z}$ — collapsing the integers to a single point — is not
Hausdorff: any saturated open set containing $\mathbb{Z}$ has an interval about
every integer, and two such sets always meet a neighbourhood of any other point
you try to separate from it. Corollary 22.3(b) assumes a Hausdorff $Z$ and a map
onto it, which is precisely what a bare partition does not give you.
(d) The four-point class is the corner set $\{0\times0, 0\times1, 1\times0, 1\times1\}$;
it has four points because both identifications act on it.
</details>
<details><summary>Worked start</summary>
(c) By Problem 2(b), a partition of $X$ and an equivalence relation on $X$ are
the same data, so "the quotient of $X$ by $\sim$" is defined: take the set of
$\sim$-classes and give it the quotient topology induced by the map sending each
point to its class. For the Reeb graph, $\sim$ is "lies in the same connected
component of the same level set of $f$", so the construction applies verbatim and
$\mathsf{R}_f$ is a topological space.
⟨your step: now list what §22 does *not* give — take each of "is a graph", "is
Hausdorff", "is finite" in turn and say which section or hypothesis would be
needed, citing Corollary 22.3(b) for the second⟩

(a), (b), (d) ⟨your step⟩
</details>
