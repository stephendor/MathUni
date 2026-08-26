# top-10 — The countability axioms

**Module:** Topology · **Unit:** top-10
**Sources:** Munkres, *Topology*, 2nd ed. — §30 "The Countability Axioms"
(pp. 190–194). Numbered results used: Theorem 30.1, Theorem 30.2, Theorem 30.3,
together with Lemma 21.2, Theorem 21.3, Theorem 20.4 and Theorem 20.5 from
top-06, which §30 generalises.

Interleaves top-06 directly: Theorem 30.1 is Lemma 21.2 and Theorem 21.3 with
"metrizable" replaced by the weaker hypothesis those proofs actually used, which
Munkres flagged at the time. Also top-05, since Theorem 30.2 is about countable
products and the examples turn on Theorem 19.1's finiteness clause.

Submit your written solutions via `/grade top-10`.

---

## Problem 1 (easy — the two axioms, and the debt from top-06)

$X$ has a **countable basis at $x$** if there is a countable collection
$\mathcal{B}$ of neighbourhoods of $x$ such that each neighbourhood of $x$
contains at least one element of $\mathcal{B}$; $X$ is **first-countable** if this
holds at every point. $X$ is **second-countable** if it has a countable basis for
its topology (pp. 190–191).

(a) Prove that second-countable implies first-countable, and give a
first-countable space that is not second-countable. (Munkres supplies two; use
either and say which.)
(b) Prove Theorem 30.1(a): if a sequence of points of $A$ converges to $x$ then
$x \in \bar{A}$, and the converse holds if $X$ is first-countable. Compare it
line by line with top-06's Lemma 21.2 and say exactly which words changed.
(c) Prove Theorem 30.1(b) and compare with top-06's Theorem 21.3 in the same
way. Munkres remarked in §21 that "All we really needed was the countable
collection $B_d(x, 1/n)$ of balls about $x$" (p. 130); show that Theorem 30.1 is
that remark made into a theorem.
(d) Every metrizable space is first-countable. Prove it, and then say why the
converse fails — naming a first-countable non-metrizable space from §28 or §30
and the property that separates it.

*(Munkres §30, p. 190 for the first countability axiom; p. 190 for the second and
for Theorem 30.1; §21, pp. 130–131, for the original versions and Munkres's
remark.)*

<details><summary>Nudge</summary>
For (a), $\mathbb{R}^\omega$ in the uniform topology is Munkres's Example 2, and
$\mathbb{R}_\ell$ is his Example 3.
</details>
<details><summary>Strategy</summary>
(b) Replace "let $d$ be a metric and take $B_d(x, 1/n)$" by "let $\{U_n\}$ be a
countable basis at $x$ and take $B_n = U_1 \cap \cdots \cap U_n$". The
intersection is needed because the $U_n$ need not shrink.
(d) $\{B_d(x, 1/n)\}$ is a countable basis at $x$. $S_\Omega$ is first-countable
(Munkres says so in §28, p. 181, as something to check) and not metrizable,
because it is limit point compact and not compact.
</details>
<details><summary>Partial</summary>
(a) $\mathbb{R}^\omega$ in the uniform topology is first-countable, being
metrizable, and is not second-countable (Example 2). $\mathbb{R}_\ell$
"satisfies all the countability axioms but the second" (Example 3).
</details>
<details><summary>Worked start</summary>
(a) Let $\mathcal{B}$ be a countable basis for $X$ and fix $x$. Put
$\mathcal{B}_x = \{B \in \mathcal{B} : x \in B\}$, a subcollection of a countable
set and so countable. Given any neighbourhood $U$ of $x$, the definition of the
generated topology (top-02) supplies $B \in \mathcal{B}$ with
$x \in B \subset U$, and that $B$ lies in $\mathcal{B}_x$.
⟨your step: conclude, then name the separating example and say which axiom it
has and which it lacks⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — what survives subspaces and products)

**Theorem 30.2** (p. 191): a subspace of a first-countable space is
first-countable, and a countable product of first-countable spaces is
first-countable; the same two statements hold with "second" in place of "first".

(a) Prove the second-countable half, both clauses, following Munkres. In the
product clause, say precisely where the hypothesis that the index set is
*countable* is used, and where Theorem 19.1's finiteness clause is used — they
are two different steps.
(b) Prove the first-countable half. Munkres says only "The proof for the first
countability axiom is similar"; write the part that is not a transcription.
(c) Verify Munkres's Example 1: $\mathbb{R}$, $\mathbb{R}^n$ and
$\mathbb{R}^\omega$ (product topology) all have countable bases. For
$\mathbb{R}^\omega$, write down the basis he gives and prove it is countable —
the counting argument is the interesting part.
(d) Use Theorem 30.2 to prove that $\mathbb{R}_\ell^2$ is not second-countable,
given Example 3's statement that $\mathbb{R}_\ell$ is not. Say which clause of
the theorem you use and in which direction.

*(Munkres §30, p. 191 for Theorem 30.2 and its proof; p. 190 for Example 1; p. 192
for Example 3; p. 193 for Example 4.)*

<details><summary>Nudge</summary>
In (c), a set indexed by finite sequences of rationals is a countable union of
countable sets.
</details>
<details><summary>Strategy</summary>
(a) Countability of the index set is needed so that the collection of *finite*
subsets of the index set is countable; Theorem 19.1's clause is what makes each
basis element depend on only finitely many coordinates in the first place.
(d) $\mathbb{R}_\ell$ is homeomorphic to the subspace $\mathbb{R}_\ell \times \{0\}$
of $\mathbb{R}_\ell^2$; if $\mathbb{R}_\ell^2$ were second-countable, the subspace
clause would make $\mathbb{R}_\ell$ second-countable too.
</details>
<details><summary>Partial</summary>
(c) The basis is all products $\prod_n U_n$ with $U_n$ an open interval with
rational endpoints for finitely many $n$ and $U_n = \mathbb{R}$ otherwise. It is
indexed by (a finite subset of $\mathbb{Z}_+$, a rational interval for each
index), a countable union over finite subsets of countable sets.
</details>
<details><summary>Worked start</summary>
(a) *Subspaces.* If $\mathcal{B}$ is a countable basis for $X$ and $A \subset X$,
then $\{B \cap A : B \in \mathcal{B}\}$ is a basis for the subspace topology by
Lemma 16.1 (top-02), and it is countable as the image of a countable set.
*Products.* ⟨your step: write down Munkres's collection, then argue countability
in two steps — first that each basis element is determined by a finite set of
indices together with a choice from each $\mathcal{B}_i$, and second that the
totality is countable. Name where "countable index set" enters and where
Theorem 19.1 enters.⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — Lindelöf, separable, and how badly they behave)

**Theorem 30.3** (p. 192): if $X$ has a countable basis then (a) every open
covering of $X$ contains a countable subcollection covering $X$; and (b) there
is a countable subset of $X$ dense in $X$. A space with property (a) is
**Lindelöf**; one with property (b) is **separable**.

(a) Prove both parts of Theorem 30.3.
(b) Munkres calls "separable" "an unfortunate choice of terminology". Say why —
what other family of axioms does the word collide with? Then note his blunter
assessment: "We shall not use these properties to prove any theorems"
(p. 192). Given that, say what he does use the Lindelöf condition for.
(c) Verify Example 5: the ordered square $I_o^2$ is Lindelöf (why, in one line?)
but its subspace $A = I \times (0,1)$ is not. Reproduce Munkres's argument
through the uncountable family $U_x = \{x\} \times (0,1)$.
(d) Munkres says these properties are "not as well behaved as one might wish
under the operations of taking subspaces and cartesian products". Assemble the
evidence from §30: name one property that fails to pass to subspaces and one
that fails to pass to finite products, citing the example for each. Then contrast
with Theorem 30.2 and say what the second countability axiom has that these two
do not.

*(Munkres §30, p. 192 for Theorem 30.3, the definitions of Lindelöf and
separable, the remark about terminology and the assessment; pp. 192–193 for
Example 3; p. 193 for Example 4, the Sorgenfrey plane; p. 194 for Example 5.)*

<details><summary>Nudge</summary>
For (b)'s collision, look at the names in §31.
</details>
<details><summary>Strategy</summary>
(a) For Lindelöf, replace each member of the cover by countably many basis
elements inside it and choose one cover member per basis element used. For
separable, pick one point from each basis element.
(c) $I_o^2$ is compact (top-07, Example 6 makes it a linear continuum; top-08's
Theorem 27.1 makes closed intervals compact), and a compact space is Lindelöf
trivially since a finite subcover is a countable one.
</details>
<details><summary>Partial</summary>
(b) The word collides with the *separation* axioms of §31 — Hausdorff, regular,
normal — with which it has nothing to do. Munkres uses the Lindelöf condition
only "in dealing with some examples".
(d) Lindelöf fails for subspaces (Example 5, the ordered square) and for finite
products (Example 4, the Sorgenfrey plane). Second countability passes to both,
by Theorem 30.2 — that is exactly what makes it the useful axiom.
</details>
<details><summary>Worked start</summary>
(a) *Separable.* Let $\mathcal{B} = \{B_n\}$ be a countable basis. Discard any
empty $B_n$ and choose $x_n \in B_n$ for each remaining index; let $D$ be the set
of chosen points, countable as the image of a countable index set.
⟨your step: show $\bar{D} = X$, using Theorem 17.5(b) — the basis form of the
closure criterion — and say why using 17.5(b) rather than 17.5(a) is what makes
the argument work at all⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — the examples that pull the axioms apart)

(a) Verify Munkres's Example 2 in full: $\mathbb{R}^\omega$ in the **uniform**
topology is first-countable and not second-countable. His argument runs through
a lemma — "if $X$ is a space having a countable basis $\mathcal{B}$, then any
discrete subspace $A$ of $X$ must be countable" — prove that lemma, then produce
an uncountable discrete subspace of the uniform $\mathbb{R}^\omega$.
(b) Verify Example 3: $\mathbb{R}_\ell$ satisfies the first countability axiom,
is Lindelöf and is separable, but is not second-countable. Take the
non-second-countability as the one to prove carefully.
(c) Verify Example 4: $\mathbb{R}_\ell$ is Lindelöf but the Sorgenfrey plane
$\mathbb{R}_\ell^2$ is not. Munkres's argument uses the antidiagonal
$L = \{x \times (-x)\}$; reconstruct it and say what property of $L$ as a
subspace makes the covering uncountable and irreducible.
(d) Fill in this table for the five spaces $\mathbb{R}$, $\mathbb{R}^\omega$
(product), $\mathbb{R}^\omega$ (uniform), $\mathbb{R}_\ell$,
$\mathbb{R}_\ell^2$, against the four properties first-countable,
second-countable, Lindelöf, separable. Mark each cell ✓, ✗ or "not settled in
§30", and give the source for every entry. Three of the twenty cells are not
settled by §30; identify them and say so rather than guessing.

*(Munkres §30, p. 190 for Example 2; pp. 192–193 for Example 3; p. 193 for
Example 4; p. 194 for Example 5. Munkres §20, Theorem 20.4 p. 124 and Theorem 20.5 p. 125, give the
relation between the uniform and product topologies on $\mathbb{R}^\omega$.)*

<details><summary>Nudge</summary>
For (a), consider the set of sequences with entries in $\{0,1\}$ and the uniform
metric — how far apart are two distinct such sequences?
</details>
<details><summary>Strategy</summary>
(a) In the uniform metric $\bar\rho$, two distinct 0–1 sequences are at distance
exactly $1$, so the balls of radius $1/2$ about them are disjoint. That makes the
set of all 0–1 sequences an uncountable discrete subspace.
(d) The unsettled cells concern the uniform $\mathbb{R}^\omega$'s Lindelöf and
separability status, and $\mathbb{R}_\ell^2$'s separability; §30 states none of
the three.
</details>
<details><summary>Partial</summary>
(a) The lemma: choose for each $a \in A$ a basis element $B_a$ meeting $A$ only
in $a$; then $a \mapsto B_a$ is injective into a countable set.
(d) $\mathbb{R}_\ell^2$ is first-countable by Theorem 30.2 (finite product) and
not second-countable by Theorem 30.2 (subspace) with Example 3; it is not
Lindelöf by Example 4.
</details>
<details><summary>Worked start</summary>
(a) *The lemma.* Suppose $X$ has a countable basis $\mathcal{B}$ and $A \subset X$
is discrete in the subspace topology. For each $a \in A$ the set $\{a\}$ is open
in $A$, so $\{a\} = U \cap A$ for some $U$ open in $X$; choose
$B_a \in \mathcal{B}$ with $a \in B_a \subset U$. Then $B_a \cap A = \{a\}$.
⟨your step: show $a \mapsto B_a$ is injective and conclude $A$ is countable⟩

⟨your step: now exhibit an uncountable discrete subspace of $\mathbb{R}^\omega$
in the uniform topology, computing the distance between two distinct members⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — what countability does and does not separate)

(a) Munkres's Chapter 4 introduction (p. 189) states the goal: "if a topological
space $X$ satisfies a certain countability axiom (the second) and a certain
separation axiom (the regularity axiom), then $X$ can be imbedded in a metric
space and is thus metrizable." Say which section proves it, and state precisely
what §30 contributes to that proof and what it does not.
(b) Munkres adds of Lindelöf and separable that each "is equivalent to the second
countability axiom when the space is metrizable (see Exercise 5)". State the
three-way equivalence for metrizable spaces, note that §30 leaves it as an
exercise, and say what that equivalence buys in analysis — Munkres's own reason
is on p. 192.
(c) **The mission clause.** This unit's strip reads: "Countability separates the
pathological spaces from the ones data can actually sample." Let $X$ be a finite
metric space, which by top-06 carries the discrete topology. Determine whether
$X$ is first-countable, second-countable, Lindelöf and separable. Then say what
the strip's claim can and cannot mean, given your answer, and identify the object
about which countability *would* be informative.
(d) The hook says second-countability "quietly powers half the metrization
results". Test the word "half" against what you can verify: name every
metrization theorem you have seen a *statement* of, say which of them §30's axiom
appears in, and say plainly which ones you have not read. Do not attribute
content to a theorem you have only seen the title of.

*(Munkres p. 189 for the Chapter 4 introduction; §30, p. 192, for the metrizable
equivalence and the analysis remark, and for the reference to Exercise 5. Parts
(c) and (d) are not in Munkres; (c) is derived from top-06 and (d) is a question
about what this unit has and has not read.)*

<details><summary>Nudge</summary>
In (c), what is the smallest basis a finite discrete space admits?
</details>
<details><summary>Strategy</summary>
(c) A finite discrete space has the finite basis of singletons, so it is
second-countable, hence first-countable, Lindelöf and separable by
Theorem 30.3 — all four, trivially, for the fourth consecutive unit in which
finiteness settles a property before the geometry is consulted.
(d) You have read the *statement* of no metrization theorem in this unit. You
have read Munkres's one-sentence description of the Urysohn metrization theorem
in the Chapter 4 introduction, and that is all — so "half" is not a claim you
are in a position to assess, and saying so is the correct answer.
</details>
<details><summary>Partial</summary>
(c) All four hold, trivially. So countability separates nothing about a point
cloud; the object it could be informative about is the space being sampled, and
§30 says nothing about that either.

(d) The honest answer names the Urysohn metrization theorem as described on
p. 189 and proved in §34, p. 214, records that §40, p. 248, is titled for another
metrization theorem whose statement this unit has not read, and declines to
quantify "half".
</details>
<details><summary>Worked start</summary>
(c) Let $X$ be finite with the discrete topology. The collection of singletons
$\{\{x\} : x \in X\}$ is a basis: every open set is a union of them, and the two
basis conditions are immediate. It is finite, hence countable, so $X$ is
second-countable.
⟨your step: deduce the other three, naming the results used, and then say what
the mission strip's claim can mean given that all four verdicts came from
finiteness alone⟩

(a), (b), (d) ⟨your step⟩
</details>
