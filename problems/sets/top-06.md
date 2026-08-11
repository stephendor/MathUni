# top-06 — The metric topology

**Module:** Topology · **Unit:** top-06
**Sources:** Munkres, *Topology*, 2nd ed. — §20 "The Metric Topology"
(pp. 119–128) and §21 "The Metric Topology (continued)" (pp. 129–135).
Numbered results used: Theorem 20.1, Lemma 20.2, Theorem 20.3, Theorem 20.4,
Theorem 20.5, Theorem 21.1, Lemma 21.2, Theorem 21.3, Lemma 21.4, Theorem 21.5,
Theorem 21.6.

Interleaves top-05 throughout — Theorems 20.3, 20.4 and 20.5 are all statements
about product topologies — and top-04, since §21 is where the $\epsilon$-$\delta$
definition Munkres deferred there finally arrives (Theorem 21.1).

`an-14`, named in this unit's hook, is a syllabus unit whose lesson has not been
written; nothing below depends on it.

Submit your written solutions via `/grade top-06`.

---

## Problem 1 (easy — the metric axioms, the balls, and the finite case)

A **metric** on $X$ is $d : X \times X \to \mathbb{R}$ with (1) $d(x,y) \ge 0$
with equality iff $x = y$; (2) $d(x,y) = d(y,x)$; (3) the triangle inequality
$d(x,y) + d(y,z) \ge d(x,z)$ (p. 119). The $\epsilon$-ball is
$B_d(x,\epsilon) = \{y : d(x,y) < \epsilon\}$, and the collection of all
$\epsilon$-balls is a basis for the **metric topology** (p. 119).

(a) Verify that the $\epsilon$-balls form a basis. Munkres's key step is that if
$y \in B(x,\epsilon)$ then $B(y, \delta) \subset B(x,\epsilon)$ for
$\delta = \epsilon - d(x,y)$; prove it, and say which metric axiom each line uses.
(b) Prove Theorem 20.1: $\bar{d}(x,y) = \min\{d(x,y), 1\}$ is a metric inducing
the same topology as $d$. Munkres's proof of the triangle inequality splits into
two cases; do both, and then give his argument that the topologies agree —
which turns on the observation that the $\epsilon$-balls with $\epsilon < 1$
already form a basis.
(c) **The finite case.** Let $(X,d)$ be a metric space with $X$ finite and
$|X| \ge 2$. Prove that the metric topology on $X$ is the **discrete** topology.
Then say what happens when $|X| = 1$ and when $X = \varnothing$, so that the
statement you end with is true without exception.
(d) Deduce from (c) that the metric topology of a finite metric space depends on
$d$ not at all. Then state precisely what a point cloud's metric topology
records about the point cloud, and what it discards.

*(Munkres §20, p. 119 for the metric axioms, the $\epsilon$-ball and the metric
topology; pp. 119–120 for the basis verification; pp. 121–122 for Theorem 20.1.
Parts (c) and (d) are not in §20; they are derived from its definitions.)*

<details><summary>Nudge</summary>
For (c), you need $\epsilon > 0$ with $B(x,\epsilon) = \{x\}$. What is the
smallest distance from $x$ to a point that is not $x$, and why is it positive?
</details>
<details><summary>Strategy</summary>
(c) Fix $x$ and put $\epsilon_x = \min\{d(x,y) : y \in X,\ y \neq x\}$. The set
being minimised over is finite and non-empty, so the minimum is attained, and it
is positive by axiom (1). Then $B(x, \epsilon_x) = \{x\}$, so every singleton is
open, so every subset is open.
(d) All metrics on a finite set induce the same topology, so the topology cannot
see any distance. It records the *cardinality* of the point cloud and nothing
else.
</details>
<details><summary>Partial</summary>
(c) For $|X| = 1$ the discrete and indiscrete topologies coincide (top-01,
Problem 2(c)), so the conclusion still holds but is not informative; for
$X = \varnothing$ there is only one topology. The clean statement: *every* finite
metric space carries the discrete topology.
(d) It records $|X|$ and discards every distance — which is why a point cloud is
never analysed through its own metric topology.
</details>
<details><summary>Worked start</summary>
(a) Let $y \in B(x,\epsilon)$, so $d(x,y) < \epsilon$, and set
$\delta = \epsilon - d(x,y) > 0$. If $z \in B(y,\delta)$ then
$d(y,z) < \epsilon - d(x,y)$, so by the triangle inequality (axiom 3)
$$d(x,z) \le d(x,y) + d(y,z) < d(x,y) + \big(\epsilon - d(x,y)\big) = \epsilon,$$
so $z \in B(x,\epsilon)$. Hence $B(y,\delta) \subset B(x,\epsilon)$.
⟨your step: now use this twice to get basis condition (2) for two balls
$B_1, B_2$ and a point $y \in B_1 \cap B_2$⟩

(c) Suppose $X$ is finite with at least two points and fix $x \in X$. The set
$\{d(x,y) : y \neq x\}$ is finite and non-empty, so it has a least element
$\epsilon_x$, and $\epsilon_x > 0$ by axiom (1) since each $y \neq x$.
⟨your step: compute $B(x, \epsilon_x)$, conclude that $\{x\}$ is open, and get
from there to "every subset is open"⟩

(b), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — comparing metrics, and $\mathbb{R}^n$)

**Lemma 20.2** (p. 122): for metrics $d, d'$ on $X$ inducing $\mathcal{T},
\mathcal{T}'$, the topology $\mathcal{T}'$ is finer than $\mathcal{T}$ if and
only if for each $x$ and each $\epsilon > 0$ there is $\delta > 0$ with
$B_{d'}(x,\delta) \subset B_d(x,\epsilon)$.

(a) Prove Lemma 20.2. Both directions use Lemma 13.3 of top-02; say which
form of it each uses and what extra step is needed to get from "a basis element
inside" to "a ball *centred at $x$* inside".
(b) Prove Theorem 20.3: the euclidean metric $d$ and the square metric $\rho$
induce the same topology on $\mathbb{R}^n$, and it is the product topology.
Munkres's proof runs off the inequalities
$\rho(\mathbf{x},\mathbf{y}) \le d(\mathbf{x},\mathbf{y}) \le \sqrt{n}\,\rho(\mathbf{x},\mathbf{y})$;
verify both, and say which of the two inclusions of topologies each gives via
Lemma 20.2.
(c) Munkres says that in $\mathbb{R}^2$ the $d$-balls are circular regions and
the $\rho$-balls are square regions. Draw both and use the picture to state, in
one sentence, the geometric content of Lemma 20.2 for this pair.
(d) Why does the $\sqrt{n}$ in (b) not spoil the argument, and what would go
wrong if $n$ were allowed to be infinite? Answer the second part by naming the
relevant quantity and saying what happens to it.

*(Munkres §20, p. 121 for the norm, the euclidean and square metrics; p. 122 for
Lemma 20.2 with its proof; pp. 122–123 for Theorem 20.3.)*

<details><summary>Nudge</summary>
In (d), $\sqrt{n}$ is a constant for each fixed $n$ — but a bound that grows
without limit is no bound at all.
</details>
<details><summary>Strategy</summary>
(a) Forwards, Lemma 13.3 gives a $\mathcal{T}'$-basis element $B'$ with
$x \in B' \subset B_d(x,\epsilon)$; but $B'$ need not be centred at $x$, so use
Problem 1(a) to shrink it to a $d'$-ball centred at $x$.
(b) $\rho \le d$ gives $B_d(x,\epsilon) \subset B_\rho(x,\epsilon)$, so the
$d$-topology is finer; $d \le \sqrt{n}\rho$ gives the reverse.
</details>
<details><summary>Partial</summary>
(d) For fixed $n$, $\sqrt{n}$ is a constant, so $\delta = \epsilon/\sqrt{n}$
works uniformly. With infinitely many coordinates the analogous bound is
$\sup_i |x_i - y_i|$ against a sum that need not converge at all; there is no
finite constant, and indeed $\mathbb{R}^J$ in the box topology is not metrizable
for infinite $J$ — Munkres says as much on p. 125.
</details>
<details><summary>Worked start</summary>
(b) *The inequalities.* Write $\rho(\mathbf{x},\mathbf{y}) = \max_i |x_i - y_i|$
and $d(\mathbf{x},\mathbf{y}) = \left(\sum_i (x_i - y_i)^2\right)^{1/2}$. Then
each $|x_i - y_i| \le d(\mathbf{x},\mathbf{y})$, so
$\rho \le d$; and each $(x_i - y_i)^2 \le \rho^2$, so
$d^2 \le n\rho^2$, i.e. $d \le \sqrt{n}\,\rho$.
⟨your step: feed each inequality into Lemma 20.2 and name the resulting
inclusion of topologies; then handle the product topology, using top-05's
Theorem 19.1 to say what a basis element looks like⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — three topologies on $\mathbb{R}^J$, and one metric that works)

Munkres defines the **uniform metric** on $\mathbb{R}^J$ by
$\bar{\rho}(\mathbf{x},\mathbf{y}) = \sup\{\bar{d}(x_\alpha, y_\alpha) : \alpha \in J\}$,
where $\bar{d}$ is the standard bounded metric on $\mathbb{R}$ (p. 124).

(a) Prove Theorem 20.4: the uniform topology on $\mathbb{R}^J$ is finer than the
product topology and coarser than the box topology. Follow Munkres's two
arguments. In the first, say why the set of indices with $U_\alpha \neq \mathbb{R}$
being *finite* is exactly what lets you take a minimum.
(b) Munkres adds that "these three topologies are all different if $J$ is
infinite" and then writes: "Showing these three topologies are different if $J$
is infinite is a task we leave to the exercises" (p. 125). Show that the uniform
topology is strictly finer than the product topology on $\mathbb{R}^\omega$, by
exhibiting a $\bar{\rho}$-ball that is not open in the product topology.
(c) Prove Theorem 20.5: with $\bar{d}$ the standard bounded metric on
$\mathbb{R}$, the function
$D(\mathbf{x},\mathbf{y}) = \sup\{\bar{d}(x_i,y_i)/i\}$ is a metric on
$\mathbb{R}^\omega$ inducing the **product** topology.
(d) Munkres states on p. 125 that "the only one of these cases where
$\mathbb{R}^J$ is metrizable is the case where $J$ is countable and
$\mathbb{R}^J$ has the product topology." Theorem 20.5 proves the positive half.
Say precisely what the negative half asserts and whether §20 proves it; then say
which of the three topologies on $\mathbb{R}^\omega$ Theorem 20.5 shows to be
metrizable, and which two it says nothing about.

*(Munkres §20, p. 124 for the uniform metric and topology; pp. 124–125 for
Theorem 20.4 with its proof and the sentence deferring the strictness to the
exercises; p. 125 for the metrizability claim and Theorem 20.5.)*

<details><summary>Nudge</summary>
For (b), a $\bar\rho$-ball constrains *every* coordinate at once — compare with
top-05's Theorem 19.1.
</details>
<details><summary>Strategy</summary>
(a) Given a product basis element $\prod U_\alpha$ about $\mathbf{x}$, only
finitely many $U_\alpha$ differ from $\mathbb{R}$, so the finitely many
$\epsilon_i$ have a positive minimum. With infinitely many the infimum could be
$0$ and there would be no ball to take.
(b) The ball $B_{\bar\rho}(\mathbf{0}, 1/2)$ constrains every coordinate to
within $1/2$; no product-topology basis element does that.
</details>
<details><summary>Partial</summary>
(d) The negative half asserts that $\mathbb{R}^J$ is *not* metrizable in the box
topology for infinite $J$, nor in the product topology for uncountable $J$.
Munkres asserts it here ("as we shall see") and does not prove it in §20 —
Theorem 20.5 proves only the positive case.
</details>
<details><summary>Worked start</summary>
(a) *Uniform finer than product.* Let $\mathbf{x} \in \prod U_\alpha$, a product
basis element. By top-05's Theorem 19.1 there are only finitely many indices
$\alpha_1, \dots, \alpha_n$ with $U_{\alpha} \neq \mathbb{R}$. For each $i$
choose $\epsilon_i > 0$ with the $\epsilon_i$-ball about $x_{\alpha_i}$ in the
$\bar{d}$ metric inside $U_{\alpha_i}$; put $\epsilon = \min\{\epsilon_1,\dots,\epsilon_n\}$.
⟨your step: show $B_{\bar\rho}(\mathbf{x},\epsilon) \subset \prod U_\alpha$, and
then say in one sentence why the minimum step fails if infinitely many
$U_\alpha$ differ from $\mathbb{R}$⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — epsilons return, and sequences almost suffice)

(a) Prove Theorem 21.1: for metrizable $X$ and $Y$, continuity of $f$ is
equivalent to the $\epsilon$-$\delta$ condition. Compare with top-04, where
Munkres proved one direction of this for $\mathbb{R}$ only and deferred the rest
"when we study metric spaces"; say what §21 adds beyond that special case.
(b) Prove **Lemma 21.2**, the sequence lemma: if some sequence of points of $A$
converges to $x$ then $x \in \bar{A}$, and the converse holds if $X$ is
metrizable. Then prove Theorem 21.3, and state exactly where the metrizability
hypothesis is used in each — Munkres notes parenthetically in Theorem 21.3's
proof that "metrizability of $Y$ is not needed".
(c) Munkres observes that neither proof used the full force of metrizability —
"All we really needed was the countable collection $B_d(x, 1/n)$ of balls about
$x$" — and defines the **first countability axiom** accordingly (pp. 130–131).
State it. Then show how his substitution
$B_n = U_1 \cap U_2 \cap \cdots \cap U_n$ repairs the proof of Lemma 21.2 for a
first-countable space, and say why the intersection is taken rather than using
$U_n$ directly.
(d) Give a topological space and a subset $A$ with a point in $\bar{A}$ that is
the limit of no sequence of points of $A$. You may not use a metrizable space —
say why not, in one line, before you start.

*(Munkres §21, p. 129 for the opening survey and Theorem 21.1; p. 130 for
Lemma 21.2 and Theorem 21.3 with the parenthetical remark; pp. 130–131 for the
first countability axiom and the repair.)*

<details><summary>Nudge</summary>
For (d), a space where every neighbourhood of a point is enormous will do — try
an uncountable set with the countable complement topology.
</details>
<details><summary>Strategy</summary>
(c) The sets $U_n$ need not shrink; $B_n$ is decreasing by construction, which
is what makes "for all $i \ge N$" work at the end of the argument.
(d) Take $X = \mathbb{R}$ with the countable complement topology $\mathcal{T}_c$
of top-01 and let $A$ be an uncountable set with uncountable complement. A
sequence in $A$ converging to $x \notin A$ would have to enter every
$\mathcal{T}_c$-neighbourhood of $x$, and the complement of the sequence's range
is such a neighbourhood.
</details>
<details><summary>Partial</summary>
(b) In Lemma 21.2 metrizability supplies the balls $B_d(x,1/n)$ to choose points
from. In Theorem 21.3's converse it is used only through the lemma, applied in
$X$ — hence the parenthetical remark that $Y$ need not be metrizable.
(d) Metrizable spaces are excluded because Lemma 21.2's converse holds in them,
so no counterexample can live there.
</details>
<details><summary>Worked start</summary>
(b) *Lemma 21.2, forwards.* Suppose $x_n \to x$ with each $x_n \in A$. Let $U$
be a neighbourhood of $x$. By the definition of convergence there is $N$ with
$x_n \in U$ for all $n \ge N$; in particular $U$ contains a point of $A$. By
Theorem 17.5(a), $x \in \bar{A}$. Note that no hypothesis on $X$ was used.
*Converse.* Let $X$ be metrizable with metric $d$ and let $x \in \bar{A}$. For
each $n$, the ball $B_d(x, 1/n)$ is a neighbourhood of $x$, so by Theorem 17.5(a)
it meets $A$; choose $x_n \in B_d(x,1/n) \cap A$.
⟨your step: prove $x_n \to x$, and say which sentence of your argument is the one
that needs the radii to shrink to zero⟩

(a), (c), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — building continuous functions two more ways)

(a) State **Lemma 21.4** and Munkres's disposition of it: "You have probably
seen this lemma proved before; it is a standard '$\epsilon$-$\delta$ argument.'
If not, a proof is outlined in Exercise 12 below" (p. 131). Prove that addition
is continuous $\mathbb{R} \times \mathbb{R} \to \mathbb{R}$ using
Theorem 21.1, and say why the argument is a statement about a map *out of* a
product and therefore not covered by top-04's Theorem 18.4.
(b) Prove Theorem 21.5 from Lemma 21.4. Munkres's proof is four lines and uses
Theorem 18.4; reproduce it, and say which map is built by Theorem 18.4 and which
by Theorem 18.2.
(c) State the definition of **uniform convergence** (p. 131) and prove
**Theorem 21.6**, the uniform limit theorem. Munkres's proof is the $\epsilon/3$
argument; write out all three inequalities and say which choice supplies each.
(d) Munkres remarks that "uniformity of convergence depends not only on the
topology of $Y$ but also on its metric" (p. 131). Make that precise: exhibit two
metrics on the same set inducing the same topology, and a sequence of functions
converging uniformly with respect to one and not the other. Then say why
Theorem 21.6's *conclusion* — that $f$ is continuous — is nevertheless a purely
topological statement.

*(Munkres §21, p. 131 for Lemma 21.4 with its deferral to Exercise 12, for
Theorem 21.5, for the definition of uniform convergence and the remark about
metric dependence; pp. 131–132 for Theorem 21.6 and its proof.)*

<details><summary>Nudge</summary>
For (d), an unbounded metric and its standard bounded companion $\bar{d}$ from
Theorem 20.1 induce the same topology — and $\bar{d}$ can never register a
distance above $1$.
</details>
<details><summary>Strategy</summary>
(a) Given $(x_0, y_0)$ and $\epsilon$, take $\delta = \epsilon/2$ in the square
metric on $\mathbb{R}^2$; then $|x - x_0| < \delta$ and $|y - y_0| < \delta$ give
$|(x+y) - (x_0+y_0)| < \epsilon$. Theorem 20.3 says the square metric induces the
product topology, which is what lets an $\epsilon$-$\delta$ argument speak about
the product at all.
(d) Take $Y = \mathbb{R}$ with $d(a,b) = |a-b|$ and $\bar{d} = \min\{|a-b|,1\}$.
By Theorem 20.1 they induce the same topology. The constant functions
$f_n \equiv n$ converge to nothing under either, so instead compare
$f_n(x) = n$ against $f(x) = 0$: under $\bar{d}$ the distance is capped at $1$,
so no sequence can be made to converge uniformly that did not already — build the
example the other way, with distances shrinking below $1$ in one metric only.
</details>
<details><summary>Partial</summary>
(c) The three inequalities are $d(f(x), f_N(x)) < \epsilon/3$ by the choice of
$N$; $d(f_N(x), f_N(x_0)) < \epsilon/3$ by the choice of $U$, which used
continuity of $f_N$; and $d(f_N(x_0), f(x_0)) < \epsilon/3$ by the choice of $N$
again. The triangle inequality then gives $d(f(x), y_0) < \epsilon$.
(d) The conclusion is topological because "continuous" is defined without
reference to any metric; only the *hypothesis* of uniform convergence is
metric-dependent.
</details>
<details><summary>Worked start</summary>
(b) The map $h : X \to \mathbb{R} \times \mathbb{R}$ given by
$h(x) = f(x) \times g(x)$ is continuous by Theorem 18.4, since its coordinate
functions are $f$ and $g$. The sum $f + g$ is the composite of $h$ with the
addition map $+ : \mathbb{R} \times \mathbb{R} \to \mathbb{R}$, which is
continuous by Lemma 21.4. A composite of continuous maps is continuous by
Theorem 18.2(c), so $f + g$ is continuous.
⟨your step: the same for $f - g$, $f \cdot g$ and $f/g$, saying what the
hypothesis $g(x) \neq 0$ is doing and which map's domain it changes⟩

(c) Let $V$ be open in $Y$ and $x_0 \in f^{-1}(V)$; put $y_0 = f(x_0)$. Choose
$\epsilon$ with $B(y_0,\epsilon) \subset V$. Choose $N$ so that
$d(f_n(x), f(x)) < \epsilon/3$ for all $n \ge N$ and all $x$. Choose a
neighbourhood $U$ of $x_0$ with $f_N(U) \subset B(f_N(x_0), \epsilon/3)$.
⟨your step: for $x \in U$, write the three inequalities and combine them⟩

(a), (d) ⟨your step⟩
</details>
