# top-07 — Connectedness and components

**Module:** Topology · **Unit:** top-07
**Sources:** Munkres, *Topology*, 2nd ed. — §23 "Connected Spaces" (pp. 148–152),
§24 "Connected Subspaces of the Real Line" (pp. 153–158), §25 "Components and
Local Connectedness" (pp. 159–162). Numbered results used: Lemma 23.1,
Lemma 23.2, Theorem 23.3, Theorem 23.4, Theorem 23.5, Theorem 23.6,
Theorem 24.1, Corollary 24.2, Theorem 24.3, Theorem 25.1, Theorem 25.2,
Theorem 25.3, Theorem 25.4, Theorem 25.5.

Interleaves top-04 (Theorem 23.5 is about continuous images, and every path is a
continuous map), top-03 (Lemma 23.1 restates separation in terms of limit
points), and top-05 (Theorem 23.6 is about finite products).

Submit your written solutions via `/grade top-07`.

---

## Problem 1 (easy — separations, and the two ways to say it)

A **separation** of $X$ is a pair $U, V$ of disjoint non-empty open subsets of
$X$ whose union is $X$; $X$ is **connected** if no separation exists (p. 148).

(a) Prove Lemma 23.1: if $Y$ is a subspace of $X$, a separation of $Y$ is a pair
of disjoint non-empty sets $A, B$ whose union is $Y$, neither of which contains a
limit point of the other. Say why the reformulation is worth having — what does
it let you check without ever mentioning the subspace topology?
(b) Prove Lemma 23.2: if $C, D$ separate $X$ and $Y \subset X$ is connected,
then $Y$ lies entirely in $C$ or entirely in $D$.
(c) Show that $X$ is connected if and only if the only subsets of $X$ that are
both open and closed are $\varnothing$ and $X$. Then connect this to top-03's
Problem 5(d): a proper non-empty subset with empty boundary is exactly a
separation.
(d) Which of these are connected, and why: $\mathbb{Q}$ as a subspace of
$\mathbb{R}$; a two-point discrete space; a one-point space; $\varnothing$?
Give the degenerate cases explicitly — Munkres's definition requires the two
pieces to be non-empty, and that matters here.

*(Munkres §23, p. 148 for the definition and Lemma 23.1; p. 149 for Lemma 23.2.
Part (c) is not stated in §23; it is derived from the definition.)*

<details><summary>Nudge</summary>
For (d), $\mathbb{Q} = (\mathbb{Q} \cap (-\infty, \sqrt{2})) \cup (\mathbb{Q} \cap (\sqrt{2}, \infty))$.
</details>
<details><summary>Strategy</summary>
(b) $Y \cap C$ and $Y \cap D$ are open in $Y$, disjoint, and their union is $Y$;
if both were non-empty they would separate $Y$.
(c) $U$ clopen and proper non-empty means $U, X - U$ is a separation, and
conversely.
</details>
<details><summary>Partial</summary>
(d) $\mathbb{Q}$ is not connected; a two-point discrete space is not; a
one-point space is connected (there is no way to write it as two non-empty
pieces); $\varnothing$ is connected, again because a separation needs two
non-empty sets and $\varnothing$ has no non-empty subsets at all.
</details>
<details><summary>Worked start</summary>
(b) Suppose $C, D$ is a separation of $X$ and $Y \subset X$ is connected. The
sets $Y \cap C$ and $Y \cap D$ are open in $Y$ by the definition of the subspace
topology, are disjoint because $C \cap D = \varnothing$, and their union is
$Y \cap (C \cup D) = Y$.
⟨your step: conclude, saying which clause of the definition of a separation
forces one of them to be empty⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — the four construction theorems)

(a) Prove Theorem 23.3: the union of a collection of connected subspaces of $X$
having a point in common is connected.
(b) Prove Theorem 23.4: if $A$ is connected and $A \subset B \subset \bar{A}$,
then $B$ is connected. Note what this gives you for free: the closure of a
connected set is connected.
(c) Prove Theorem 23.5: the image of a connected space under a continuous map is
connected. Which characterisation of continuity from top-04 makes this shortest?
(d) Prove Theorem 23.6: a finite cartesian product of connected spaces is
connected. Then say what happens for infinite products — is the finiteness in
the statement essential, or an artefact of the proof? Do not guess; say what
§23 does and does not settle.

*(Munkres §23, p. 149 for Theorems 23.3 and 23.4; p. 150 for Theorem 23.5 and
Theorem 23.6.)*

<details><summary>Nudge</summary>
For (a), if $C, D$ separated the union, use Lemma 23.2 on each piece and then
look at the common point.
</details>
<details><summary>Strategy</summary>
(a) Each $A_\alpha$ lies wholly in $C$ or wholly in $D$ by Lemma 23.2; the
common point $p$ lies in one of them, say $C$, so every $A_\alpha$ containing $p$
lies in $C$, so $D$ is empty.
(c) Use the definition directly: a separation of the image pulls back to a
separation of the domain.
</details>
<details><summary>Partial</summary>
(b) A separation $C, D$ of $B$ has $A$ entirely in one, say $C$, by Lemma 23.2;
then $B \subset \bar{A} \subset \bar{C}$, and $D$ meets $\bar{C}$, so $D$
contains a limit point of $C$ — contradicting Lemma 23.1.
</details>
<details><summary>Worked start</summary>
(a) Let $\{A_\alpha\}$ be connected subspaces with a common point $p$, and let
$Y = \bigcup A_\alpha$. Suppose $Y = C \cup D$ is a separation. The point $p$ is
in one of them; say $p \in C$. Each $A_\alpha$ is connected and lies in $Y$, so
by Lemma 23.2 it lies entirely in $C$ or entirely in $D$; since $p \in A_\alpha$
and $p \in C$, it must lie in $C$.
⟨your step: conclude that $D = \varnothing$ and say which clause of the
definition that contradicts⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — the real line, and the theorem calculus took for granted)

A simply ordered set $L$ with more than one element is a **linear continuum**
if it has the least upper bound property and if for $x < y$ there is $z$ with
$x < z < y$ (p. 153).

(a) Prove Theorem 24.1: a linear continuum in the order topology is connected,
and so are intervals and rays in it. Then deduce Corollary 24.2 for
$\mathbb{R}$, saying which property of $\mathbb{R}$ makes it a linear continuum.
(b) Prove Theorem 24.3, the intermediate value theorem, in Munkres's generality:
$f : X \to Y$ continuous, $X$ connected, $Y$ ordered with the order topology,
$r$ between $f(a)$ and $f(b)$ — then $f(c) = r$ for some $c$. Say which two
earlier results the proof consumes.
(c) The calculus statement of the IVT is the case $X = [a,b]$, $Y = \mathbb{R}$.
Show it follows, naming the result that makes $[a,b]$ connected. Then give a
connected $X$ and a continuous $f$ for which the conclusion is vacuous, so that
you can see what connectedness is actually buying.
(d) Munkres's Example 6 (p. 156): the ordered square $I_o^2$ is connected but not
path connected. Reproduce the argument that no path joins $0 \times 0$ to
$1 \times 1$ — the sets $U_x = f^{-1}(x \times (0,1))$, the choice of a rational
in each, and the injection $I \to \mathbb{Q}$. Note that Munkres's last step
appeals to a fact he says "we shall prove later"; identify it and say whether
your argument depends on it.

*(Munkres §24, p. 153 for the linear continuum and Theorem 24.1; p. 154 for
Corollary 24.2; p. 154 for Theorem 24.3; p. 155 for the definition of a path and
the proof that path connected implies connected; p. 156 for Examples 3–6.)*

<details><summary>Nudge</summary>
In (b), the two sets $Y \cap (-\infty, r)$ and $Y \cap (r, +\infty)$ are the
pieces to work with.
</details>
<details><summary>Strategy</summary>
(b) The sets $A = f(X) \cap (-\infty, r)$ and $B = f(X) \cap (r, +\infty)$ are
open in $f(X)$ and disjoint. If $r$ were not in $f(X)$ they would cover it, and
each is non-empty because it contains $f(a)$ or $f(b)$ — so they would separate
$f(X)$, which is connected by Theorem 23.5.
(d) The final step needs $I$ to be uncountable; Munkres flags that he proves it
later. Your argument inherits the dependency, and it should say so.
</details>
<details><summary>Partial</summary>
(a) $\mathbb{R}$ has the least upper bound property and is densely ordered.
(c) $[a,b]$ is connected by Corollary 24.2. A vacuous case: any constant $f$ —
there is no $r$ strictly between $f(a)$ and $f(b)$ when they are equal.
</details>
<details><summary>Worked start</summary>
(b) Suppose there is no $c$ with $f(c) = r$. Put
$$A = f(X) \cap (-\infty, r), \qquad B = f(X) \cap (r, +\infty).$$
Each is open in $f(X)$, being the intersection of an open ray with $f(X)$
(top-02: the open rays are open in the order topology). They are disjoint. Their
union is $f(X)$, because $r \notin f(X)$ by assumption. And $A$ is non-empty
since it contains whichever of $f(a), f(b)$ is less than $r$, and $B$ likewise.
⟨your step: so $A, B$ separate $f(X)$ — now derive the contradiction, naming the
theorem that says $f(X)$ is connected⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — components, path components, and the gap between them)

Munkres defines two equivalence relations on $X$: $x \sim y$ if some connected
subspace contains both (classes: **components**), and $x \sim y$ if there is a
path from $x$ to $y$ (classes: **path components**) — pp. 159–160.

(a) Verify that both relations are equivalence relations. For the path relation,
Munkres's transitivity argument pastes two paths together and cites
Theorem 18.3; reproduce it, and say why reparametrising domains is needed first.
(b) Prove Theorem 25.1 and state Theorem 25.2. Munkres says of the second that
its proof "is similar to that of the theorem preceding"; do the part that is
*not* similar, namely the verification that a path component is path connected.
(c) Munkres observes that each component is closed, that with finitely many
components each is also open, but that in general components need not be open —
and that path components "need be neither open nor closed" (p. 161). Prove the
first two claims and verify the third against his Example 1: in
$\mathbb{Q} \subset \mathbb{R}$ each component is a single point and none is
open.
(d) Prove Theorem 25.5: each path component lies in a component, and if $X$ is
locally path connected the two agree. Then verify the failure without the
hypothesis using Munkres's Example 2, the topologist's sine curve
$\bar{S}$ with $S = \{x \times \sin(1/x) : 0 < x \le 1\}$: one component, two
path components $S$ and $V = 0 \times [-1,1]$, with $S$ open and not closed and
$V$ closed and not open.

*(Munkres §25, p. 159 for components and Theorem 25.1; p. 160 for path
components, the pasting argument and Theorem 25.2; p. 161 for the openness and
closedness remarks and Examples 1 and 2; p. 161 for local connectedness and
Theorems 25.3, 25.4; p. 162 for Theorem 25.5. The topologist's sine curve is
introduced in §24, Example 7, p. 156.)*

<details><summary>Nudge</summary>
For (d), the vertical segment $V$ cannot be reached by a path from $S$ — any
such path would have to oscillate infinitely often in finite time.
</details>
<details><summary>Strategy</summary>
(a) Two paths have domains $[0,1]$ and $[1,2]$ after reparametrising, which is
legitimate because any two closed intervals of $\mathbb{R}$ are homeomorphic;
then the pasting lemma applies with the two closed pieces meeting at $\{1\}$.
(d) For the first clause, a path component is path connected hence connected, so
it lies in a single component by Theorem 25.1. For the second, local path
connectedness makes path components open (Theorem 25.4), and a component
partitioned by open path components would be separated unless there is only one.
</details>
<details><summary>Partial</summary>
(c) A component is closed because the closure of a connected set is connected
(Theorem 23.4) and a component is maximal. With finitely many, each component's
complement is a finite union of closed sets, hence closed.
</details>
<details><summary>Worked start</summary>
(b) *Theorem 25.1.* The components are equivalence classes, so they are disjoint
and cover $X$. If a connected subspace $A$ meets components $C_1$ and $C_2$ at
$x_1$ and $x_2$, then $x_1 \sim x_2$ by the definition of the relation, so
$C_1 = C_2$.
*Each component $C$ is connected.* Fix $x_0 \in C$. For each $x \in C$ we have
$x_0 \sim x$, so there is a connected $A_x$ containing both; by the previous
paragraph $A_x \subset C$. Hence $C = \bigcup_{x \in C} A_x$, a union of connected
sets with the point $x_0$ in common, connected by Theorem 23.3.
⟨your step: now state Theorem 25.2 and prove that a path component is path
connected⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — local connectedness, and the mission's hidden hypothesis)

(a) State the definitions of **locally connected** and **locally path
connected** (p. 161). Show that a space can be connected without being locally
connected, using the topologist's sine curve, and locally connected without being
connected, using a two-point discrete space.
(b) Prove Theorem 25.3: $X$ is locally connected if and only if for every open
$U$, each component of $U$ is open in $X$. Then prove Theorem 25.4, the path
version.
(c) **The mission clause, examined.** This unit's mission strip reads: "Path
components ARE what zeroth homology counts — for TDA's finite complexes they are
the connected pieces, the first and most robust Betti number." Ignore homology,
which is not in §§23–25, and examine the middle clause. Using Theorem 25.5 and
Munkres's Example 2, say precisely under what hypothesis path components *are*
the connected pieces, and give the counterexample that shows the hypothesis
cannot be dropped. Then state which clause of the strip is doing the work of
supplying that hypothesis.
(d) Suppose $X$ is a finite topological space in which every singleton is open
— that is, a discrete space, which by top-06's Problem 1(c) is what a point
cloud's metric topology gives. Compute the components and the path components of
$X$. Are they equal? Is $X$ locally path connected? Say what this tells you about
why a point cloud is not analysed through its own metric topology, and which
construction replaces it.

*(Munkres §25, p. 161 for local connectedness and local path connectedness and
for Theorems 25.3 and 25.4; p. 162 for Theorem 25.5; p. 161, Example 2, for the
topologist's sine curve's components. Part (c) concerns this unit's mission
strip and part (d) is derived from top-06; neither is in Munkres.)*

<details><summary>Nudge</summary>
In (d), a path from $x$ to $y$ in a discrete space has connected image, and the
connected subsets of a discrete space are very small.
</details>
<details><summary>Strategy</summary>
(c) Theorem 25.5's second clause needs $X$ locally path connected. Without it,
$\bar{S}$ has one component and two path components, so the two notions come
apart. The strip's phrase "for TDA's finite complexes" is where the hypothesis is
smuggled in — whether finite complexes satisfy it is a question for at1-07 and
lab-02, not for §25.
(d) In a discrete space the connected subsets are exactly the singletons and
$\varnothing$, so components are singletons; a path $[a,b] \to X$ has connected
image, hence is constant, so path components are singletons too. They agree, and
$X$ is locally path connected — trivially, since $\{x\}$ is a path-connected
neighbourhood inside every neighbourhood of $x$.
</details>
<details><summary>Partial</summary>
(c) The hypothesis is local path connectedness. The counterexample is
$\bar{S}$: one component, two path components. The strip supplies the hypothesis
through the clause "for TDA's finite complexes", which is a restriction on the
spaces, not a theorem.
(d) Components = path components = the $n$ singletons; $X$ is locally path
connected; and the count is exactly $|X|$, which is all the discrete topology
knows. The replacement construction is the filtration (lab-02, tda1-01).
</details>
<details><summary>Worked start</summary>
(d) Let $X$ be discrete with $n$ points. *Connected subsets.* If $A \subset X$
has two distinct points $x, y$, then $\{x\}$ and $A - \{x\}$ are non-empty,
disjoint, open in $A$ and cover $A$ — a separation. So the connected subsets are
$\varnothing$ and the singletons.
⟨your step: read off the components from that; then handle path components by
asking what the image of a path must be, and finish with local path
connectedness⟩

⟨your step: state what the answer says about analysing a point cloud through its
metric topology, and name the construction that is used instead⟩

(a), (b), (c) ⟨your step⟩
</details>
