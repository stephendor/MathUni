# top-03 — Closed sets, closure, interior, and limit points

**Module:** Topology · **Unit:** top-03
**Sources:** Munkres, *Topology*, 2nd ed. — §17 "Closed Sets and Limit Points"
(pp. 92–101). Numbered results used: Theorem 17.1, Theorem 17.2, Theorem 17.3,
Theorem 17.4, Theorem 17.5, Theorem 17.6, Corollary 17.7, Theorem 17.8,
Theorem 17.9, Theorem 17.10, Theorem 17.11.

Interleaves top-02 throughout — Theorem 17.2 and Theorem 17.4 are both about
subspaces, and Theorem 17.5(b) is stated in terms of a basis — and top-01 in
Problem 1, where Theorem 17.1 is the three axioms read through complements.

Two of the results below Munkres states and does not prove. Theorem 17.3 comes
with "we leave the proof to you" (p. 94), and Theorem 17.11 with "The proof of
the following result is left to the exercises" (p. 100). Problems 1(d) and 5
are those.

Submit your written solutions via `/grade top-03`.

---

## Problem 1 (easy — closed sets are the axioms in a mirror)

A subset $A$ of a space $X$ is **closed** if $X - A$ is open (p. 93).

(a) Prove Theorem 17.1: $\varnothing$ and $X$ are closed; arbitrary
intersections of closed sets are closed; finite unions of closed sets are
closed. Use De Morgan, as Munkres does, and say for each clause which axiom of
top-01 it is the mirror of. In particular, say which of the three closed-set
clauses inherits the word "finite", and why it is not the same clause that
carried it for open sets.
(b) Munkres's Example 5: $Y = [0,1] \cup (2,3)$ as a subspace of $\mathbb{R}$.
Show that $[0,1]$ is open in $Y$ and closed in $Y$, and that $(2,3)$ is too.
Then answer his riddle — "How is a set different from a door?" — by giving four
subsets of $\mathbb{R}$, one open and not closed, one closed and not open, one
both, one neither.
(c) Prove Theorem 17.2: for $Y$ a subspace of $X$, a set $A$ is closed in $Y$
if and only if $A = C \cap Y$ for some $C$ closed in $X$.
(d) Munkres writes "we leave the proof to you" (p. 94) and then states
Theorem 17.3 (p. 95) — if $A$ is closed in $Y$ and $Y$ is closed in $X$ then $A$
is closed in $X$. Prove it. Then show the hypothesis "$Y$ closed in $X$" cannot be dropped, and
say which result of top-02 this theorem is the exact mirror of.

*(Munkres §17, p. 93 for the definition, Examples 1–5 and the riddle; p. 94 for
Theorem 17.1, Theorem 17.2 and the announcement "we leave the proof to you",
which is the last sentence of that page; p. 95 for the statement of Theorem 17.3
itself, which opens the next one. The theorem spans the page break; its
statement does not.)*

<details><summary>Nudge</summary>
For (d), the counterexample lives in the same place as top-02's: take
$Y = (0,1)$ inside $\mathbb{R}$.
</details>
<details><summary>Strategy</summary>
(a) $X - \bigcap A_\alpha = \bigcup (X - A_\alpha)$ turns an arbitrary
intersection of closed sets into an arbitrary union of open sets, so the
*intersection* clause is the unrestricted one on the closed side, while for open
sets it was the *union* clause. Complementation swaps the two operations, so it
swaps which one carries "finite".
(d) $A$ closed in $Y$ gives $A = C \cap Y$ with $C$ closed in $X$ by
Theorem 17.2; an intersection of two closed sets of $X$ is closed in $X$ by
Theorem 17.1(2).
</details>
<details><summary>Partial</summary>
(b) $[0,1] = Y \cap (-1/2, 3/2)$ is open in $Y$, and $(2,3)$ is open in $Y$
because it is open in $\mathbb{R}$; each is the complement in $Y$ of the other,
so each is also closed in $Y$. In $\mathbb{R}$: $(0,1)$ open not closed;
$[0,1]$ closed not open; $\varnothing$ and $\mathbb{R}$ both; $[0,1)$ neither.
(d) Take $X = \mathbb{R}$, $Y = (0,1)$, $A = (0,1/2]$: then $A$ is closed in $Y$
and not closed in $\mathbb{R}$. This theorem mirrors Lemma 16.2.
</details>
<details><summary>Worked start</summary>
(a) (2) Let $\{A_\alpha\}_{\alpha \in J}$ be closed sets. By De Morgan,
$$X - \bigcap_{\alpha \in J} A_\alpha = \bigcup_{\alpha \in J} (X - A_\alpha).$$
Each $X - A_\alpha$ is open by the definition of closed, so the right side is an
arbitrary union of open sets and is open by axiom (2) of top-01. Hence
$\bigcap A_\alpha$ is closed.
⟨your step: clause (3), and then the sentence saying which clause carries
"finite" on each side and why complementation swaps them⟩

(c) ($\Leftarrow$) Suppose $A = C \cap Y$ with $C$ closed in $X$. Then $X - C$
is open in $X$, so $(X - C) \cap Y$ is open in $Y$ by the definition of the
subspace topology. But $(X - C) \cap Y = Y - A$, so $Y - A$ is open in $Y$ and
$A$ is closed in $Y$.
⟨your step: the converse — start from $Y - A$ open in $Y$, write it as
$U \cap Y$, and identify the closed set of $X$⟩

(b), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — computing closures without listing every closed set)

The closure $\bar{A}$ is the intersection of all closed sets containing $A$
(p. 95), which is useless for computation. Theorem 17.5 repairs that:
(a) $x \in \bar{A}$ if and only if every open set $U$ containing $x$ intersects
$A$; (b) if the topology is given by a basis, $x \in \bar{A}$ if and only if
every basis element $B$ containing $x$ intersects $A$.

(a) Prove Theorem 17.5, both parts. Munkres proves (a) by contraposition and
says so explicitly — write out the contrapositive statement before proving it,
as he does, and say why the argument is easier in that form.
(b) Verify Munkres's Example 6 in full, using Theorem 17.5(b) with the standard
basis: for $A = (0,1]$, $B = \{1/n : n \in \mathbb{Z}_+\}$,
$C = \{0\} \cup (1,2)$, $\mathbb{Q}$, $\mathbb{Z}_+$ and $\mathbb{R}_+$, compute
the closure in $\mathbb{R}$ and justify each with the criterion, not by
inspection.
(c) Prove Theorem 17.4: for $A \subset Y \subset X$, the closure of $A$ in $Y$
equals $\bar{A} \cap Y$, where $\bar{A}$ is the closure in $X$. Then verify
Munkres's Example 7: $Y = (0,1]$, $A = (0,1/2)$, closure in $\mathbb{R}$ is
$[0,1/2]$ and closure in $Y$ is $(0,1/2]$.
(d) Munkres writes "we reserve the notation $\bar{A}$ to stand for the closure
of $A$ in $X$" (p. 95). Explain what goes wrong if you do not fix a convention —
give a single set $A$ sitting inside two different spaces where the unqualified
phrase "the closure of $A$" names two different sets.

*(Munkres §17, p. 95 for the definitions of interior and closure and for
Theorem 17.4; p. 96 for the "intersects" terminology, Theorem 17.5, the word
"neighborhood" and Example 6; pp. 96–97 for Example 7.)*

<details><summary>Nudge</summary>
For $\bar{\mathbb{Q}} = \mathbb{R}$, you need that every interval contains a
rational. For $\bar{\mathbb{Z}}_+ = \mathbb{Z}_+$, you need an interval about a
non-integer that misses $\mathbb{Z}_+$.
</details>
<details><summary>Strategy</summary>
(a) The contrapositive is: $x \notin \bar{A}$ if and only if there exists an
open set $U$ containing $x$ that does not intersect $A$. Forwards, take
$U = X - \bar{A}$; backwards, note $X - U$ is a closed set containing $A$, so it
contains $\bar{A}$. The gain is that both directions now produce or consume a
*single* witness set rather than quantifying over all closed sets.
(c) One inclusion uses Theorem 17.2 to see that $\bar{A} \cap Y$ is closed in
$Y$; the other writes the closure in $Y$ as $C \cap Y$ and uses minimality of
$\bar{A}$.
</details>
<details><summary>Partial</summary>
(b) $\bar{A} = [0,1]$; $\bar{B} = \{0\} \cup B$; $\bar{C} = \{0\} \cup [1,2]$;
$\bar{\mathbb{Q}} = \mathbb{R}$; $\bar{\mathbb{Z}}_+ = \mathbb{Z}_+$; and the
closure of $\mathbb{R}_+$ is $\mathbb{R}_+ \cup \{0\}$.
(d) $A = (0,1/2)$ inside $X = \mathbb{R}$ and inside $Y = (0,1]$: the closures
are $[0,1/2]$ and $(0,1/2]$.
</details>
<details><summary>Worked start</summary>
(a) Statement (a) has the form $P \Leftrightarrow Q$; replace each implication
by its contrapositive to get the equivalent
$$x \notin \bar{A} \iff \text{there is an open } U \ni x \text{ with } U \cap A = \varnothing.$$
($\Rightarrow$) If $x \notin \bar{A}$, then $U = X - \bar{A}$ is open, contains
$x$, and misses $A$ since $A \subset \bar{A}$.
($\Leftarrow$) ⟨your step: from such a $U$, produce a closed set containing $A$
and conclude $x \notin \bar{A}$⟩

Part (b) of the theorem: ⟨your step — one direction is immediate because a basis
element is open; the other needs the definition of the generated topology⟩

(b) Take $B = \{1/n\}$. If $x = 0$: every basis element $(a,b)$ containing $0$
has $b > 0$, and by the Archimedean property there is $n$ with $1/n < b$, so
$(a,b)$ meets $B$. Hence $0 \in \bar{B}$. ⟨your step: now show no other point
outside $B$ is in $\bar{B}$ — given $x \notin B \cup \{0\}$, produce a basis
element about $x$ missing $B$, treating $x < 0$, $x > 1$ and
$1/(n+1) < x < 1/n$ separately⟩

(c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — limit points, and the closure decomposed)

$x$ is a **limit point** of $A$ if every neighbourhood of $x$ intersects $A$ in
some point *other than $x$ itself*; equivalently, if $x \in \overline{A - \{x\}}$
(p. 97). $A'$ denotes the set of limit points of $A$.

(a) Prove Theorem 17.6: $\bar{A} = A \cup A'$.
(b) Prove Corollary 17.7: $A$ is closed if and only if it contains all its limit
points. Munkres's proof is one line; expand it, saying which equivalence each
step uses.
(c) Verify Munkres's Example 8 against Example 6, and explain the one place they
come apart: for $C = \{0\} \cup (1,2)$ the closure is $\{0\} \cup [1,2]$ but the
set of limit points is $[1,2]$ — so $0 \in C$ and $0 \notin C'$. Define
"isolated point" in terms of Munkres's definitions and say why Theorem 17.6 is
untroubled by this.
(d) Prove that $A'$ is closed for every $A$, or find a counterexample. The
instruction is deliberate: decide which of the two you are being asked for
before you start writing, and do not let the shape of the sentence decide for
you. If it turns out to be false in general, find the hypothesis that rescues it
and prove the rescued version. Then decide, separately and with proof or
counterexample, whether $(A')' = A'$ always.

*(Munkres §17, p. 97 for the definition of limit point, for Example 8 and for
Theorem 17.6; p. 98 for Corollary 17.7; p. 99 for the $T_1$ axiom. Parts (c) and
(d) go beyond the section: "isolated point" is not Munkres's term here, and the
closedness of $A'$ is not stated in §17 in any form — neither the true $T_1$
version nor the false unqualified one.)*

<details><summary>Nudge</summary>
For the second half of (d), test $A = \{1/n\}$ in $\mathbb{R}$ and compute both
$A'$ and $(A')'$.
</details>
<details><summary>Strategy</summary>
(a) $A' \subset \bar{A}$ by Theorem 17.5; $A \subset \bar{A}$ by definition. For
the reverse, take $x \in \bar{A}$ and split on whether $x \in A$.
(d) Try to show $\overline{A'} \subset A'$: if $x \in \overline{A'}$ then every
neighbourhood of $x$ meets $A'$, and a point of $A'$ inside a neighbourhood
drags points of $A$ in with it. The whole difficulty is getting a point of $A$
different from $x$, and the only move available is to shrink the neighbourhood
so that it excludes $x$. **Write down what that move assumes about $\{x\}$.**
Then ask whether every topological space grants it. If some space does not, that
space is your counterexample, and the assumption you wrote down is the
hypothesis to add.
</details>
<details><summary>Partial</summary>
(c) $x$ is an *isolated point* of $A$ if $x \in A$ and $x \notin A'$ —
equivalently if some neighbourhood of $x$ meets $A$ only in $x$. Theorem 17.6 is
untroubled because it takes a *union*: $0$ enters $\bar{C}$ through $C$, not
through $C'$.
(d) **$A'$ need not be closed** — the claim as posed is false, and the
counterexample has two points. Let $X = \{a,b\}$ carry the indiscrete topology
$\mathcal{T} = \{\varnothing, X\}$ and take $A = \{a\}$. Then $b \in A'$, because
$b$'s only neighbourhood is $X$ and $X$ contains $a \neq b$; and $a \notin A'$,
because $A - \{a\} = \varnothing$. So $A' = \{b\}$, and $\{b\}$ is not closed —
its complement $\{a\}$ is not open. What is true is that **$A'$ is closed in
every $T_1$ space**, and $T_1$ is exactly the hypothesis the shrinking step
needs. The second question is independent of all this: $(A')' = A'$ can fail even
in $\mathbb{R}$, which is as separated as one could ask — for $A = \{1/n\}$ we
get $A' = \{0\}$ and $(A')' = \varnothing$.
</details>
<details><summary>Worked start</summary>
(a) ($\supset$) If $x \in A'$ then every neighbourhood of $x$ intersects $A$ —
in a point different from $x$, but in particular it intersects $A$ — so
$x \in \bar{A}$ by Theorem 17.5(a). Together with $A \subset \bar{A}$ this gives
$A \cup A' \subset \bar{A}$.
($\subset$) Let $x \in \bar{A}$. If $x \in A$ we are done. If $x \notin A$, then
every neighbourhood $U$ of $x$ intersects $A$ by Theorem 17.5(a), and since
$x \notin A$ the point of $U \cap A$ is automatically different from $x$. So
$x \in A'$. ∎
⟨your step: say which hypothesis the phrase "automatically different from $x$"
is consuming, and why the argument would need more care if $x$ were in $A$⟩

(d) *The attempt, run until it stops.* Let $x \in \overline{A'}$ and let $U$ be a
neighbourhood of $x$. Then $U$ meets $A'$, say at $y \in U \cap A'$. If $y = x$
then $x \in A'$ and there is nothing left to do, so suppose $y \neq x$. Now $U$
is a neighbourhood of $y$ too, so $U$ meets $A$ in a point other than $y$ — but
that point may be $x$ itself, which is not good enough. The repair is to run the
argument on $U - \{x\}$ instead of $U$, and for that to be a neighbourhood of $y$
it must be **open**.

⟨your step: $U - \{x\} = U \cap (X - \{x\})$, so it is open as soon as $\{x\}$ is
closed. Name the axiom that says every one-point set is closed, finish the proof
under it, and state the theorem you have actually proved.⟩

*Why the hypothesis cannot be dropped.* In $X = \{a,b\}$ with
$\mathcal{T} = \{\varnothing, X\}$ and $A = \{a\}$, we have $A' = \{b\}$ and
$\overline{A'} = X$, so $a \in \overline{A'} \setminus A'$. Watch the attempt
fail at exactly the step above: $U = X$ is the only neighbourhood of $a$, it
meets $A'$ at $y = b \neq a$, and it does meet $A$ in a point other than $b$ —
namely $a$, which is $x$. And $U - \{x\} = \{b\}$ is not open, so there is
nowhere to retreat to.

⟨your step: confirm that this $X$ is not $T_1$, by naming the one-point set that
is not closed, and check that Theorem 17.9 also fails here — exhibit a limit
point whose neighbourhoods contain only finitely many points of $A$.⟩

(b), (c) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — Hausdorff, T₁, and what goes wrong without them)

Munkres motivates the Hausdorff axiom with a three-point space in which a
one-point set is not closed and a constant sequence converges to three different
points (p. 98). Take $X = \{a,b,c\}$ with the topology
$\mathcal{A} = \{\varnothing, X, \{b\}, \{a,b\}, \{b,c\}\}$ — the one Munkres
describes in prose in §12, p. 76, and which top-01 verified is a topology.

(a) Show that $\{b\}$ is not closed in $(X, \mathcal{A})$. Then, using Munkres's
definition of convergence (p. 98), show that the constant sequence $x_n = b$
converges to $a$, to $b$ and to $c$. Which of the three neighbourhoods you had
to check is the one that would fail in a Hausdorff space?
(b) State the Hausdorff condition (p. 98) and prove Theorem 17.8: every finite
point set in a Hausdorff space is closed. Then prove Theorem 17.10: in a
Hausdorff space a sequence converges to at most one point.
(c) Munkres says the condition that finite point sets be closed "is in fact
weaker than the Hausdorff condition", names it the $T_1$ axiom, and offers
$\mathbb{R}$ in the finite complement topology as a space that is $T_1$ and not
Hausdorff (p. 99). Prove both halves of that claim about
$(\mathbb{R}, \mathcal{T}_f)$ — that finite sets are closed, and that no two
distinct points have disjoint neighbourhoods.
(d) Prove Theorem 17.9: in a $T_1$ space, $x$ is a limit point of $A$ if and
only if every neighbourhood of $x$ contains infinitely many points of $A$. Then
show the $T_1$ hypothesis is not decorative: in the space of part (a), exhibit a
set $A$ and a limit point $x$ of $A$ with a neighbourhood of $x$ meeting $A$ in
finitely many points.

*(Munkres §17, p. 98 for the three-point example, the definition of convergence
and the Hausdorff definition; p. 99 for Theorem 17.8, the $T_1$ axiom, the
finite-complement example and Theorem 17.9; pp. 99–100 for Theorem 17.10. The
particular topology $\mathcal{A}$ above is from §12, p. 76; Munkres's Figure
17.3 is a diagram whose topology the text does not spell out, so it is not
relied on here.)*

<details><summary>Nudge</summary>
In (c), two non-empty $\mathcal{T}_f$-open sets in an infinite space always
meet — think about their complements.
</details>
<details><summary>Strategy</summary>
(a) $X - \{b\} = \{a,c\}$, and $\{a,c\} \notin \mathcal{A}$. For convergence to
$a$: the neighbourhoods of $a$ are $\{a,b\}$ and $X$, both of which contain $b$,
so $x_n = b$ lies in each for every $n$.
(c) If $U, V$ are non-empty and $\mathcal{T}_f$-open then
$\mathbb{R} - U$ and $\mathbb{R} - V$ are finite, so
$\mathbb{R} - (U \cap V)$ is finite, so $U \cap V$ is non-empty because
$\mathbb{R}$ is infinite.
(d) In the space of (a), take $A = \{b\}$ and $x = a$: every neighbourhood of
$a$ contains $b \neq a$, so $a \in A'$, and $A$ has one point.
</details>
<details><summary>Partial</summary>
(a) The neighbourhood that would fail is any one separating $b$ from $a$ — there
is none, since every open set containing $a$ also contains $b$.
(c) $\mathcal{T}_f$-closed sets are exactly $\mathbb{R}$ and the finite sets
(Munkres's Example 3, p. 93), so finite point sets are closed; and no two
non-empty open sets are disjoint, so the space is very far from Hausdorff.
</details>
<details><summary>Worked start</summary>
(b) *Theorem 17.8.* It suffices to show each one-point set $\{x_0\}$ is closed,
since a finite union of closed sets is closed by Theorem 17.1(3). Let
$x \neq x_0$. By the Hausdorff condition there are disjoint neighbourhoods $U$
of $x$ and $V$ of $x_0$. Since $U \cap V = \varnothing$ and $x_0 \in V$, the set
$U$ does not contain $x_0$, so $U$ does not intersect $\{x_0\}$. By
Theorem 17.5(a), $x \notin \overline{\{x_0\}}$. As $x$ was an arbitrary point
different from $x_0$, $\overline{\{x_0\}} = \{x_0\}$, which is therefore closed.

*Theorem 17.10.* ⟨your step: suppose $x_n \to x$ and $y \neq x$; take disjoint
neighbourhoods and count how many $n$ can have $x_n \in V$⟩

(d) ⟨your step: the easy direction first, then the contrapositive — if some
neighbourhood $U$ of $x$ meets $A$ in finitely many points, remove them. Say
exactly where $T_1$ is used.⟩

(a), (c) ⟨your step⟩
</details>

---

## Problem 5 (hard — Theorem 17.11, which Munkres leaves to the exercises)

Munkres writes: "The proof of the following result is left to the exercises"
(p. 100), and states **Theorem 17.11**: every simply ordered set is a Hausdorff
space in the order topology; the product of two Hausdorff spaces is a Hausdorff
space; a subspace of a Hausdorff space is a Hausdorff space.

(a) Prove the third clause. It is the shortest, and it needs Theorem 17.2 or
the definition of the subspace topology, not both.
(b) Prove the second clause, for the product topology on $X \times Y$ of
top-02's §15 sense. Say where you use that a product of open sets is a basis
element.
(c) Prove the first clause. Given $x < y$ in a simply ordered set $X$, there are
two cases — there is a point strictly between them, or there is not — and both
need a basis element produced. Handle the extreme elements of $X$ correctly:
your neighbourhoods must be basis elements of one of Munkres's three types
(top-02, §14, p. 84).
(d) Munkres defines the **boundary** of $A$ by
$\operatorname{Bd} A = \bar{A} \cap \overline{(X - A)}$ — but in Exercise 19
(p. 102), not in the body of §17, and he remarks in the body that "We shall not
make much use of the interior of a set" (p. 95). Prove his Exercise 19(a) and
19(b): that $\operatorname{Int} A$ and $\operatorname{Bd} A$ are disjoint with
$\bar{A} = \operatorname{Int} A \cup \operatorname{Bd} A$; and that
$\operatorname{Bd} A = \varnothing$ if and only if $A$ is both open and closed.
Then say which spaces have a subset other than $\varnothing$ and $X$ with empty
boundary, and name the property that fails for such a space — you have met it
under a different heading.

*(Munkres §17, p. 100 for Theorem 17.11 and the note that its proof is left to
the exercises; p. 95 for interior, closure and the remark about the interior;
§18, p. 102, Exercise 19, for the definition of the boundary and for parts (a) and
(b). The order topology and its three basis types are §14, p. 84.)*

<details><summary>Nudge</summary>
In (c), if there is no point strictly between $x$ and $y$, the sets
$(-\infty, y)$ and $(x, +\infty)$ do the work — but check they are basis
elements or unions of them, and check the case where $x$ is smallest or $y$ is
largest.
</details>
<details><summary>Strategy</summary>
(b) Given $(x_1,y_1) \neq (x_2,y_2)$, they differ in at least one coordinate;
separate in that coordinate and take the product with the whole of the other
factor.
(d) $\operatorname{Bd} A = \varnothing$ means $\bar{A}$ and $\overline{X - A}$
are disjoint, which forces $A$ to be clopen; a space in which the only clopen
sets are $\varnothing$ and $X$ is exactly one that cannot be split in two, which
is top-07's subject.
</details>
<details><summary>Partial</summary>
(a) If $X$ is Hausdorff and $Y \subset X$, separate two points of $Y$ in $X$ and
intersect both neighbourhoods with $Y$.
(c) Case 1: there is $z$ with $x < z < y$; take $(-\infty, z)$ and
$(z, +\infty)$. Case 2: no such $z$; take $(-\infty, y)$ and $(x, +\infty)$,
which are disjoint precisely because nothing lies strictly between.
(d) The property that fails is connectedness (top-07): a set other than
$\varnothing$ and $X$ with empty boundary is a proper non-empty clopen set, and
its existence is exactly a separation of $X$.
</details>
<details><summary>Worked start</summary>
(c) Let $x < y$ in $X$ with the order topology.
*Case 1: there exists $z$ with $x < z < y$.* Then $x \in (-\infty, z)$ and
$y \in (z, +\infty)$, and these two open rays are disjoint. Both are open by
top-02's Problem 4(c), which handled the extreme-element cases.
*Case 2: no such $z$.* ⟨your step: exhibit the two rays, check disjointness, and
say exactly which property of Case 2 you used⟩

(d) $\operatorname{Bd} A = \varnothing$ means
$\bar{A} \cap \overline{X - A} = \varnothing$. Since
$A \subset \bar{A}$ and $X - A \subset \overline{X - A}$, and the two closures
cover $X$ (every point is in the closure of $A$ or of $X - A$ — why?), we get
$\bar{A} = A$ and $\overline{X - A} = X - A$.
⟨your step: conclude that $A$ is closed and that $X - A$ is closed, hence $A$
is open; then do the converse⟩

(a), (b) ⟨your step⟩
</details>
