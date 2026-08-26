# top-09 — Limit-point and local compactness

**Module:** Topology · **Unit:** top-09
**Sources:** Munkres, *Topology*, 2nd ed. — §28 "Limit Point Compactness"
(pp. 178–181) and §29 "Local Compactness" (pp. 182–188). Numbered results used:
Theorem 28.1, Theorem 28.2, Theorem 29.1, Theorem 29.2, Corollary 29.3,
Corollary 29.4.

Interleaves top-08 throughout — §28 exists to compare three properties against
the covering definition — top-03 (limit points, and the Hausdorff hypothesis
that runs through all of §29) and top-06 (Theorem 28.2 is a statement about
metrizable spaces, and its proof uses the balls B(x, 1/n) of Lemma 21.2).

Submit your written solutions via `/grade top-09`.

---

## Problem 1 (easy — three properties, and why they are three)

$X$ is **limit point compact** if every infinite subset of $X$ has a limit
point (p. 178). A **subsequence** of $(x_n)$ is $(x_{n_i})$ for an increasing
sequence of indices, and $X$ is **sequentially compact** if every sequence has a
convergent subsequence (p. 179).

(a) Prove the positive half of Theorem 28.1: compactness implies limit point
compactness. Argue by contraposition — an infinite set with no limit point is
closed, and gives a cover with no finite subcover.
(b) Verify Munkres's Example 1 for the negative half. Let $Y$ be a two-point set
with the indiscrete topology and let $X = \mathbb{Z}_+ \times Y$. Show that
every non-empty subset of $X$ has a limit point, so $X$ is limit point compact,
and that the covering by the sets $U_n = \{n\} \times Y$ has no finite
subcollection covering $X$.
(c) In (b), which separation axiom does $X$ fail, and where exactly does that
failure make "every non-empty subset has a limit point" so easy? Answer by
naming the pair of points that cannot be told apart.
(d) Give the three definitions side by side with their quantifiers in the same
order, and say which of the three speaks about *subsets*, which about
*sequences*, and which about *covers*. This is bookkeeping, and it is the reason
the three are not obviously comparable.

*(Munkres §28, p. 179 for limit point compactness, Theorem 28.1, Examples 1
and 2, and subsequences and sequential compactness.)*

<details><summary>Nudge</summary>
In (b), take any subset containing $\{n\} \times \{y\}$ — what are the open sets
containing the *other* point of $\{n\} \times Y$?
</details>
<details><summary>Strategy</summary>
(a) If $A \subset X$ is infinite with no limit point then $A$ is closed
(Corollary 17.7) and each $a \in A$ has a neighbourhood $U_a$ meeting $A$ only in
$a$. Then $\{U_a\} \cup \{X - A\}$ covers $X$ and no finite subfamily can, since
each $U_a$ captures one point of the infinite set $A$.
(b) Every open set of $X$ containing $(n, y)$ contains all of $\{n\} \times Y$,
because $Y$ is indiscrete. So the other point of that fibre is a limit point of
any set containing $(n,y)$.
</details>
<details><summary>Partial</summary>
(c) $X$ fails the $T_1$ axiom, hence Hausdorff: the two points of $\{n\} \times Y$
have exactly the same neighbourhoods, so each is a limit point of the singleton
containing the other. Limit points are cheap precisely because points are not
separated.
</details>
<details><summary>Worked start</summary>
(b) Write $Y = \{y_1, y_2\}$ with topology $\{\varnothing, Y\}$. A basis for
$X = \mathbb{Z}_+ \times Y$ consists of the sets $\{n\} \times Y$, since
$\mathbb{Z}_+$ is discrete (top-02, Example 3) and $Y$ has only the two open
sets.
Let $A \subset X$ be non-empty and pick $(n, y_1) \in A$, say. Every open set
containing $(n, y_2)$ contains a basis element about it, hence contains
$\{n\} \times Y$, hence contains $(n, y_1) \neq (n, y_2)$.
⟨your step: conclude that $(n,y_2)$ is a limit point of $A$, and then do the
covering half⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — and on metric spaces they are one)

**Theorem 28.2** (p. 179): for a metrizable $X$, the following are equivalent:
(1) $X$ is compact; (2) $X$ is limit point compact; (3) $X$ is sequentially
compact.

(a) Prove $(2) \Rightarrow (3)$, following Munkres. The proof splits on whether
$A = \{x_n\}$ is finite; do both cases, and in the infinite case say why the
ball $B(x, 1/i)$ meets $A$ in *infinitely* many points — which result of top-03
gives you that, and what hypothesis does it need?
(b) State what $(3) \Rightarrow (1)$ requires. You are not asked to prove it;
you are asked to say which of the two remaining implications is the hard one and
why, in terms of what each has to construct.
(c) Munkres's Example 3 (p. 181) says $\bar{S}_\Omega$ is not metrizable because
it fails the sequence lemma, and that $S_\Omega$ is not metrizable either
because it "is limit point compact but not compact". Explain how the second
reason is an application of Theorem 28.2, and say which direction of the
equivalence is being used contrapositively.
(d) Give an example, or say why none exists, of a **metrizable** space that is
limit point compact and not sequentially compact. Justify your answer with
Theorem 28.2 rather than by construction.

*(Munkres §28, p. 179 for Theorem 28.2 and its proof; pp. 179–180 for the
$(2) \Rightarrow (3)$ argument; p. 181 for Example 3.)*

<details><summary>Nudge</summary>
For (a), Theorem 17.9 is the one about neighbourhoods containing infinitely many
points — check its hypothesis.
</details>
<details><summary>Strategy</summary>
(a) Theorem 17.9 requires the $T_1$ axiom; a metrizable space is Hausdorff, hence
$T_1$ by Theorem 17.8. Without infinitude you could not keep choosing indices
$n_i > n_{i-1}$.
(d) None exists: Theorem 28.2 makes (2) and (3) equivalent for metrizable
spaces, so the question is answered by the theorem and no construction is
possible.
</details>
<details><summary>Partial</summary>
(b) $(3) \Rightarrow (1)$ is the hard one. The other implications extract an
object from a hypothesis about a *given* set or sequence; this one must produce a
finite subcover of an *arbitrary* cover, which is a statement about all covers at
once. Munkres's proof uses a Lebesgue number argument.
</details>
<details><summary>Worked start</summary>
(a) Assume $X$ metrizable and limit point compact, and let $(x_n)$ be a
sequence. Put $A = \{x_n : n \in \mathbb{Z}_+\}$.
*Case $A$ finite.* Some value $x$ is taken by $x_n$ for infinitely many $n$;
those indices give a constant subsequence, which converges to $x$.
*Case $A$ infinite.* By hypothesis $A$ has a limit point $x$. Choose $n_1$ with
$x_{n_1} \in B(x, 1)$. Given $n_{i-1}$, the ball $B(x, 1/i)$ meets $A$ in
infinitely many points ⟨your step: name the theorem and check its hypothesis
against $X$⟩, so we may choose $n_i > n_{i-1}$ with $x_{n_i} \in B(x, 1/i)$.
⟨your step: prove $(x_{n_i}) \to x$⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — local compactness)

$X$ is **locally compact at $x$** if some compact subspace of $X$ contains a
neighbourhood of $x$; **locally compact** if this holds at every point (p. 182).

(a) Verify Munkres's Example 1: $\mathbb{R}$ is locally compact. Then prove his
parenthetical claim, which he leaves to the reader — "The subspace $\mathbb{Q}$
of rational numbers is not locally compact, as you can check."
(b) Verify Example 2: $\mathbb{R}^n$ is locally compact. Munkres also asserts
that $\mathbb{R}^\omega$ is **not**, because "*none* of its basis elements are
contained in compact subspaces". Prove that, using top-05's Theorem 19.1 to say
what a basis element of $\mathbb{R}^\omega$ looks like.
(c) Verify Example 3: every simply ordered set with the least upper bound
property is locally compact. Name the result of top-08 that does the work.
(d) Show that compactness implies local compactness, and that the converse
fails. Then decide: is local compactness a topological property in the sense of
top-04 (§18, p. 105)? Is it inherited by arbitrary subspaces? Answer the second
with Corollary 29.3 and say exactly which subspaces it covers.

*(Munkres §29, p. 182 for the definition and Examples 1, 2; p. 183 for
Example 3; p. 185 for Corollary 29.3.)*

<details><summary>Nudge</summary>
For (a), a compact subspace of $\mathbb{Q}$ is closed and bounded in
$\mathbb{Q}$ — but the missing irrationals stop it from being compact.
</details>
<details><summary>Strategy</summary>
(a) A neighbourhood of $q \in \mathbb{Q}$ contains $\mathbb{Q} \cap (a,b)$. Any
compact subspace $C$ containing it is closed in $\mathbb{Q}$; but a sequence in
$\mathbb{Q} \cap (a,b)$ converging to an irrational has no convergent subsequence
in $C$, contradicting Theorem 28.2 since $\mathbb{Q}$ is metrizable.
(b) A basis element of $\mathbb{R}^\omega$ in the product topology is
$\prod U_n$ with $U_n = \mathbb{R}$ for all but finitely many $n$. Its closure —
and any set containing it — is unbounded in those coordinates, so it cannot lie
in a compact set, since compact subsets of a metric space are bounded.
</details>
<details><summary>Partial</summary>
(d) Compact ⇒ locally compact: $X$ itself is a compact subspace containing every
neighbourhood. The converse fails for $\mathbb{R}$. Local compactness is a
topological property, being stated in open sets and compactness. It is *not*
inherited by arbitrary subspaces — $\mathbb{Q} \subset \mathbb{R}$ is the
counterexample — and Corollary 29.3 covers only subspaces that are closed or
open, and only when $X$ is locally compact Hausdorff.
</details>
<details><summary>Worked start</summary>
(b) By top-05's Theorem 19.1 a basis element of $\mathbb{R}^\omega$ in the
product topology has the form $\prod_n U_n$ with $U_n$ open in $\mathbb{R}$ and
$U_n = \mathbb{R}$ for all but finitely many $n$. Fix such a $B$ and suppose
$B \subset C$ with $C$ compact.
⟨your step: pick an index $m$ with $U_m = \mathbb{R}$, and use the projection
$\pi_m$ — continuous by Theorem 19.6 — to derive a contradiction with
Theorem 27.3 or with boundedness. Say which fact about continuous images of
compact sets you are using.⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — the one-point compactification)

**Theorem 29.1** (p. 183): $X$ is locally compact Hausdorff if and only if there
is a space $Y$ with (1) $X$ a subspace of $Y$; (2) $Y - X$ a single point;
(3) $Y$ compact Hausdorff — and such a $Y$ is unique up to a homeomorphism
fixing $X$.

(a) Prove the uniqueness half (Munkres's Step 1). Given two such $Y, Y'$, define
$h$ to be the identity on $X$ and to match the two extra points; show $h$ carries
open sets to open sets, splitting on whether the open set contains the extra
point. Say which theorem of top-08 makes $Y - U$ compact and which makes its
image closed.
(b) Munkres constructs $Y = X \cup \{\infty\}$ in Step 2. Write down the
collection of open sets he uses and verify it is a topology.
(c) State the definitions of **compactification** and **one-point
compactification** (p. 185). Verify Munkres's Example 4 in one direction: the
one-point compactification of $\mathbb{R}$ is homeomorphic to the circle
$S^1$. He says "as you may readily check"; do the check, and use Theorem 26.6 of
top-08 to avoid constructing the inverse map by hand.
(d) Prove Corollary 29.4: $X$ is homeomorphic to an open subspace of a compact
Hausdorff space if and only if $X$ is locally compact Hausdorff.

*(Munkres §29, pp. 183–185 for Theorem 29.1 and its two steps; p. 185 for the
definitions of compactification and one-point compactification and for
Example 4, whose verification is left to the reader; p. 185 for
Corollary 29.4.)*

<details><summary>Nudge</summary>
For (c), map $[0,1]$ onto $S^1$ by $t \mapsto (\cos 2\pi t, \sin 2\pi t)$ and
think about which points get identified.
</details>
<details><summary>Strategy</summary>
(a) If $U \ni p$ is open in $Y$, then $C = Y - U$ is closed in the compact $Y$,
hence compact by Theorem 26.2; $C \subset X$, so $C$ is compact in $Y'$ too;
$Y'$ Hausdorff makes $C$ closed by Theorem 26.3; hence $h(U) = Y' - C$ is open.
(c) Extend $\mathbb{R} \to S^1$, $x \mapsto$ the point of $S^1$ at angle
$2\arctan x$, sending $\infty$ to $(-1, 0)$; it is a continuous bijection from a
compact space to a Hausdorff one.
</details>
<details><summary>Partial</summary>
(b) The open sets of $Y$ are: the sets $U$ open in $X$; and the sets $Y - C$
where $C$ is a compact closed subspace of $X$.
(d) Forwards: an open subspace of a compact Hausdorff space is locally compact
Hausdorff by Corollary 29.3 and the fact that subspaces of Hausdorff spaces are
Hausdorff (Theorem 17.11). Backwards: $X$ is open in its one-point
compactification.
</details>
<details><summary>Worked start</summary>
(a) Let $Y, Y'$ satisfy the three conditions, with $Y - X = \{p\}$ and
$Y' - X = \{q\}$. Define $h : Y \to Y'$ by $h(p) = q$ and $h|_X = \mathrm{id}$.
It is a bijection. We show it carries open sets to open sets; symmetry then
gives that $h$ is a homeomorphism.
*Case $p \notin U$.* Then $h(U) = U \subset X$, and $U$ is open in $Y$ and
contained in $X$, so it is open in $X$; and $X$ is open in $Y'$ ⟨your step: why
is $X$ open in $Y'$?⟩, so $U$ is open in $Y'$ by Lemma 16.2 of top-02.
*Case $p \in U$.* ⟨your step: run the compactness argument, naming Theorem 26.2
and Theorem 26.3 at the two points where they are used⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — the criterion, and the mission's manifolds)

(a) Prove Theorem 29.2: for Hausdorff $X$, local compactness is equivalent to
the condition that every neighbourhood $U$ of every $x$ contains a neighbourhood
$V$ of $x$ with $\bar{V}$ compact and $\bar{V} \subset U$. Say which direction
needs the one-point compactification and which is immediate.
(b) Prove Corollary 29.3, both cases — $A$ closed in $X$ and $A$ open in $X$.
Then show that the union of a closed subspace and an open subspace of a locally
compact Hausdorff space need not be locally compact, or prove that it must be.
(c) **The mission clause.** This unit's strip reads: "Local compactness
underwrites the well-behaved spaces (manifolds) that real data is sampled from."
Munkres does not define a manifold in §28 or §29 — the word first appears in the
Chapter 4 introduction, p. 189, as "the higher-dimensional analogue of a
surface", and manifolds are the subject of §36, p. 224. Say precisely what
§29 does and does not license about this claim: which of the two properties
(local compactness, being a manifold) has been defined here, which implication
between them would have to be proved, and in which section it would live.
(d) A point cloud is a finite metric space, hence discrete (top-06, Problem 1(c))
and compact (top-08, Munkres §26 Example 3). Is it locally compact? Answer with
the definition. Then say what this says about applying the mission strip to the
sample rather than to the sampled space, and check your answer against top-08's
version of the same question.

*(Munkres §29, p. 185 for Theorem 29.2 and Corollary 29.3. Part (c) refers to
p. 189, the Chapter 4 introduction, and to §36, p. 224, neither of which this
unit reads beyond the sentence quoted. Part (d) is derived from top-06 and
top-08.)*

<details><summary>Nudge</summary>
In (d), a discrete space has a very convenient compact neighbourhood of every
point.
</details>
<details><summary>Strategy</summary>
(a) The forward direction embeds $X$ in its one-point compactification $Y$ and
applies a separation argument in $Y$; the reverse is immediate, since $\bar{V}$
compact containing the neighbourhood $V$ is the definition.
(c) §29 defines local compactness and proves things about it. It defines no
manifold, so no implication of the form "manifolds are locally compact" can be
stated here, let alone proved. Such a statement would live in §36.
(d) Yes — trivially. $\{x\}$ is open and compact, so it is a compact subspace
containing a neighbourhood of $x$.
</details>
<details><summary>Partial</summary>
(c) Local compactness is defined here; "manifold" is not. The claim needs an
implication from one to the other, and that implication cannot be stated in §29,
because one of its two terms is undefined there.
(d) A point cloud is locally compact, trivially, exactly as it was compact
trivially and discrete trivially. Three properties, three vacuous verdicts, all
from finiteness and none from the geometry.
</details>
<details><summary>Worked start</summary>
(d) Let $X$ be a finite metric space, so discrete by top-06. Fix $x \in X$. The
set $\{x\}$ is open, hence a neighbourhood of $x$; and it is compact, being
finite (top-08, §26 Example 3). So $\{x\}$ is a compact subspace containing a
neighbourhood of $x$, and $X$ is locally compact at $x$.
⟨your step: now say what the pattern across top-06, top-08 and this unit is, and
which object the mission strip's claim would have to be about instead⟩

(a), (b), (c) ⟨your step⟩
</details>
