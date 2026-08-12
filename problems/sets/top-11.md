# top-11 — Separation axioms and normal spaces

**Module:** Topology · **Unit:** top-11
**Sources:** Munkres, *Topology*, 2nd ed. — §31 "The Separation Axioms"
(pp. 195–199) and §32 "Normal Spaces" (pp. 200–206). Numbered results used:
Lemma 31.1, Theorem 31.2, Theorem 32.1, Theorem 32.2, Theorem 32.3,
Theorem 32.4.

Interleaves top-03 (the Hausdorff axiom and Theorem 17.8 are where this ladder
starts), top-05 (Theorem 31.2's product clause runs on Theorem 19.5), top-08
(Theorem 32.3 is about compact Hausdorff spaces and uses Theorem 26.3) and
top-10 (Theorem 32.1's hypothesis is second countability).

Submit your written solutions via `/grade top-11`.

---

## Problem 1 (easy — the ladder, and the convention that makes it one)

Munkres's definitions (p. 195) both begin "Suppose that one-point sets are closed
in $X$": then $X$ is **regular** if a point and a disjoint closed set have
disjoint open neighbourhoods, and **normal** if two disjoint closed sets do.

(a) Prove that a regular space is Hausdorff and a normal space is regular.
(b) Munkres explains the odd-looking hypothesis in a parenthesis: "A two-point
space in the indiscrete topology satisfies the other part of the definitions of
regularity and normality, even though it is not Hausdorff." Verify that claim in
full — check both "other parts" against the indiscrete two-point space — and say
what would go wrong with (a) if the hypothesis were dropped.
(c) Prove Lemma 31.1(a): with one-point sets closed, $X$ is regular if and only
if for every $x$ and every neighbourhood $U$ of $x$ there is a neighbourhood $V$
of $x$ with $\bar{V} \subset U$. Munkres says of part (b) only that "This proof
uses exactly the same argument; one just replaces the point $x$ by the set $A$
throughout" — do the replacement and check that nothing else changes.
(d) Munkres distinguishes this use of "separation" from the one in top-07: there
the two open sets had to have union the whole space, here they need not. Give a
space, a point and a closed set that are separated in the §31 sense while the
space is connected, so that the two senses genuinely differ.

*(Munkres §31, p. 195 for the definitions, the parenthesis about the indiscrete
two-point space, and the remark distinguishing the two senses of "separation";
p. 196 for Lemma 31.1.)*

<details><summary>Nudge</summary>
For (d), any regular connected space will do — $\mathbb{R}$ is one.
</details>
<details><summary>Strategy</summary>
(a) For regular ⇒ Hausdorff: given $x \neq y$, the set $\{y\}$ is closed by
hypothesis and disjoint from $x$, so regularity separates them.
(c) Forwards, put $B = X - U$ and take the disjoint $V, W$ regularity gives;
$\bar V$ misses $B$ because every $y \in B$ has the neighbourhood $W$ disjoint
from $V$.
</details>
<details><summary>Partial</summary>
(b) In the indiscrete two-point space the only closed sets are $\varnothing$ and
$X$, so the only pair (point, disjoint closed set) has the closed set empty, and
$\varnothing, X$ are disjoint open sets containing them. Both "other parts" hold
vacuously, and the space is not Hausdorff — so without the one-point-sets-closed
clause, "regular" would not imply Hausdorff.
</details>
<details><summary>Worked start</summary>
(c) ($\Rightarrow$) Let $X$ be regular, $x \in X$, $U$ a neighbourhood of $x$.
Put $B = X - U$, a closed set not containing $x$. Regularity gives disjoint open
$V \ni x$ and $W \supset B$. Now $\bar{V}$ is disjoint from $B$: if $y \in B$
then $W$ is a neighbourhood of $y$ disjoint from $V$, so $y \notin \bar{V}$ by
Theorem 17.5(a). Hence $\bar{V} \subset X - B = U$.
⟨your step: the converse — given the neighbourhood condition, produce the two
disjoint open sets, and say which one is built from $\bar V$⟩

(a), (b), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — what the lower rungs inherit)

**Theorem 31.2** (p. 196): (a) a subspace of a Hausdorff space is Hausdorff and
a product of Hausdorff spaces is Hausdorff; (b) the same two statements with
"regular" in place of "Hausdorff".

(a) Prove (a). The product clause needs only one coordinate; say which, and why
that is enough.
(b) Prove (b). Munkres's product argument uses Lemma 31.1(a) and then cites
top-05's **Theorem 19.5** — $\prod \bar{A}_\alpha = \overline{\prod A_\alpha}$ —
at the crucial line. Identify that line and say what would fail without the
identification of the closure of a product with the product of closures.
(c) In Munkres's product argument for regularity he writes: "if it happens that
$U_\alpha = X_\alpha$, choose $V_\alpha = X_\alpha$." Explain why that clause is
necessary rather than merely convenient — what property of the resulting
$V = \prod V_\alpha$ would fail without it?
(d) Immediately after Theorem 31.2 Munkres writes: "There is no analogous
theorem for normal spaces, as we shall see shortly, in this section and the
next." Locate the two promised counterexamples by name and page, and state
exactly which of the two closure properties each refutes.

*(Munkres §31, p. 196 for Theorem 31.2 and its proof, and for the sentence
denying the analogue for normal spaces; p. 198 for Example 3, the Sorgenfrey
plane; §32, p. 203, for Examples 1 and 2.)*

<details><summary>Nudge</summary>
In (c), a product-topology basis element must have all but finitely many factors
equal to the whole space.
</details>
<details><summary>Strategy</summary>
(b) The line is "Since $\bar{V} = \prod \bar{V}_\alpha$ by Theorem 19.5" — it is
what converts the coordinatewise choice of the $V_\alpha$ into a statement about
the closure of the single set $V$.
(c) Without it, infinitely many $V_\alpha$ could be proper subsets of $X_\alpha$,
and then $V = \prod V_\alpha$ would not be open in the product topology, by
top-05's Theorem 19.1.
</details>
<details><summary>Partial</summary>
(d) Example 3 of §31 — the Sorgenfrey plane $\mathbb{R}_\ell^2$ is not normal
although $\mathbb{R}_\ell$ is (Example 2) — refutes closure under products.
Example 2 of §32, $S_\Omega \times \bar{S}_\Omega$, and Example 1 of §32,
$\mathbb{R}^J$ for uncountable $J$, bear on products as well; the subspace
failure is the one to hunt for separately.
</details>
<details><summary>Worked start</summary>
(a) *Subspace.* Let $X$ be Hausdorff and $Y \subset X$, and let $x \neq y$ in
$Y$. Take disjoint $U, V$ open in $X$ with $x \in U$, $y \in V$. Then
$U \cap Y$ and $V \cap Y$ are disjoint, open in $Y$, and contain $x$ and $y$.
*Product.* Let $\mathbf{x} \neq \mathbf{y}$ in $\prod X_\alpha$. Then
$x_\beta \neq y_\beta$ for some single index $\beta$.
⟨your step: separate in that coordinate and pull back through $\pi_\beta$; say
why one coordinate suffices and why the resulting sets are open⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — the three sufficient conditions for normality)

§32 opens with three theorems, "three important sets of hypotheses under which
normality of a space is assured" (p. 200).

(a) Prove **Theorem 32.1**: every regular space with a countable basis is
normal. Munkres's proof builds countable covers $\{U_n\}$ of $A$ and $\{V_n\}$ of
$B$ and then performs "the following simple trick": $U'_n = U_n - \bigcup_{i \le n} \bar{V}_i$
and $V'_n = V_n - \bigcup_{i \le n} \bar{U}_i$. Reproduce the whole argument, and
in particular prove the final disjointness claim by the $j \le k$ case analysis.
(b) Where in (a) is regularity used, and where is the countable basis used? Give
one sentence each, and then say what breaks if the basis is uncountable — be
specific about which step needs the indexing by $\mathbb{Z}_+$.
(c) Prove **Theorem 32.2**: every metrizable space is normal. Then prove
**Theorem 32.3**: every compact Hausdorff space is normal, using top-08's
Theorem 26.3 or its proof technique.
(d) State **Theorem 32.4** and say which of the four theorems of this problem
gives you the normality of $\mathbb{R}$, of $[0,1]$, of an arbitrary metric
space, and of $\mathbb{Z}_+$ — noting where more than one applies.

*(Munkres §32, p. 200 for the opening remarks and Theorem 32.1; pp. 200–201 for
its proof; p. 202 for Theorem 32.2; p. 202 for Theorem 32.3; p. 203 for
Theorem 32.4.)*

<details><summary>Nudge</summary>
In (b), the trick subtracts $\bigcup_{i \le n} \bar{V}_i$ — a *finite* union,
which is closed. That is where the indexing matters.
</details>
<details><summary>Strategy</summary>
(a) Each $U'_n$ is open because it is an open set minus a finite union of closed
sets. $\{U'_n\}$ still covers $A$ because a point of $A$ lies in no $\bar{V}_i$
at all. For disjointness, if $x \in U'_j \cap V'_k$ with $j \le k$, then
$x \in U_j$ from the first and $x \notin \bar{U}_j$ from the second.
(b) Regularity produces the shrinking neighbourhoods; the countable basis is what
lets the cover of $A$ be indexed by $\mathbb{Z}_+$, which is what makes
$\bigcup_{i \le n}$ finite for each $n$.
</details>
<details><summary>Partial</summary>
(d) $\mathbb{R}$: Theorem 32.1 (regular with a countable basis) or Theorem 32.2
(metrizable). $[0,1]$: all three of 32.1, 32.2, 32.3. An arbitrary metric space:
32.2 only, since it need not be second-countable. $\mathbb{Z}_+$: 32.2, and 32.4
since $\mathbb{Z}_+$ is well-ordered.
</details>
<details><summary>Worked start</summary>
(a) Let $A, B$ be disjoint closed sets in the regular, second-countable space
$X$. Each $x \in A$ has a neighbourhood not meeting $B$ (since $X - B$ is open);
by regularity, via Lemma 31.1(a), choose a neighbourhood whose closure lies
inside it; then choose a basis element containing $x$ inside that. Doing this for
every $x \in A$ gives a covering of $A$ by basis elements whose closures miss
$B$, and since the basis is countable, the covering is countable — index it as
$\{U_n\}$. Symmetrically get $\{V_n\}$ covering $B$ with each $\bar{V}_n$ missing
$A$.
⟨your step: define $U'_n$ and $V'_n$, check each is open, check the two families
still cover $A$ and $B$, and then run the $j \le k$ argument for disjointness⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — the examples that separate the rungs)

(a) Verify Munkres's Example 1 of §31: $\mathbb{R}_K$ is Hausdorff but not
regular. The point $0$ and the closed set $K = \{1/n\}$ are the pair to work
with; show $K$ is closed in $\mathbb{R}_K$ and that no disjoint open sets
separate it from $0$.
(b) Verify Example 2: $\mathbb{R}_\ell$ is normal. Munkres's proof chooses
$[a, x_a)$ for each $a \in A$ and $[b, x_b)$ for each $b \in B$; complete it,
and say why the same construction fails in $\mathbb{R}$ with the standard
topology.
(c) State what Example 3 asserts — the Sorgenfrey plane is not normal — and say
what (b) and (c) together establish about normality as a property. Munkres does
not prove Example 3 in §31; say where the proof is deferred to, or record that
you have not found it.
(d) Munkres's Example 1 of §32 says that for uncountable $J$ the product
$\mathbb{R}^J$ is not normal, and adds: "The proof is fairly difficult; we leave
it as a challenging exercise (see Exercise 9)." Record that as a *stated,
unproved* claim. Then use it, together with Theorem 31.2(b), to conclude
something about $\mathbb{R}^J$ that does not depend on the unproved part.

*(Munkres §31, p. 197 for Example 1; p. 198 for Examples 2 and 3; §32, p. 203,
for Examples 1 and 2, the first of which is explicitly left as an exercise.)*

<details><summary>Nudge</summary>
In (a), any basis element of $\mathbb{R}_K$ containing $0$ has the form
$(a,b) - K$; ask what it must still contain near each $1/n$.
</details>
<details><summary>Strategy</summary>
(a) $\mathbb{R}_K - K$ is open, since each point of it has an interval or an
interval-minus-$K$ around it missing $K$; so $K$ is closed. A basis element about
$0$ inside $\mathbb{R}_K - K$ must be some $(a,b) - K$, and any open set
containing $K$ contains an interval about each $1/n$; those intervals meet
$(a,b) - K$ for large $n$.
(d) $\mathbb{R}^J$ is regular by Theorem 31.2(b), since $\mathbb{R}$ is. So
combining with the stated Example 1: for uncountable $J$, $\mathbb{R}^J$ is a
regular space that is not normal — which by Theorem 32.1 forces it to have no
countable basis, and that conclusion needs Example 1 only as an input, not its
proof.
</details>
<details><summary>Partial</summary>
(b) The sets $U = \bigcup_{a \in A}[a, x_a)$ and $V = \bigcup_{b \in B}[b, x_b)$
are open, contain $A$ and $B$, and are disjoint — if a point lay in both, one of
the two half-open intervals would contain the left endpoint of the other,
contradicting the choice.
(c) Together they show normality passes to neither products nor, in general,
subspaces: $\mathbb{R}_\ell$ is normal and $\mathbb{R}_\ell^2$ is not.
</details>
<details><summary>Worked start</summary>
(a) *$K$ is closed in $\mathbb{R}_K$.* Let $x \notin K$. If $x \neq 0$, some
interval about $x$ misses $K$. If $x = 0$, the basis element $(-1,1) - K$
contains $0$ and misses $K$. So $\mathbb{R}_K - K$ is open.
⟨your step: now suppose $U \ni 0$ and $V \supset K$ are open and disjoint. Take
a basis element $(a,b) - K \subset U$ about $0$ and a basis element about $1/n$
inside $V$ for $n$ large; derive a contradiction by finding a point in both.⟩

(b), (c), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — the ladder is not uniform, and the mission's diagrams)

(a) Assemble the behaviour table. For each of Hausdorff, regular and normal, say
whether §§31–32 establish that it passes to subspaces and to products, and cite
the theorem or example for each of the six cells. Mark any cell §§31–32 does not
settle as unsettled rather than guessing.
(b) The word "ladder" suggests the three axioms differ only in strength. Using
your table, say in what respect they are a ladder and in what respect they are
not. Munkres's own verdict is on p. 200: "In one sense, the term 'normal' is
something of a misnomer, for normal spaces are not as well-behaved as one might
wish." Quote it and say what he means by it.
(c) top-03 recorded Munkres promising to explain "the reason for this strange
terminology" — the $T_1$ numbering — in Chapter 4. Search §31 and §32 for that
explanation. Report what you find: either quote it with its page, or state that
you did not find it in these two sections and say what Munkres does instead.
(d) **The mission clause.** This unit's strip reads: "Hausdorffness is the sanity
axiom persistence diagrams and their limits silently assume." Take the two halves
separately. First: is a point cloud Hausdorff, and by what argument? Second: what
would have to be true of the *space of persistence diagrams* for the strip's
claim to be a theorem rather than an expectation, and which of §§31–32's results
would you reach for — noting that none of them is about diagrams.

*(Munkres §32, p. 200 for the "misnomer" remark. Part (c) asks you to search
§§31–32 and report honestly. Part (d) is not in Munkres; the metric on diagram
space is tda1-06's, and tda1-05 established that neither of its sources supplies
one.)*

<details><summary>Nudge</summary>
In (d), a metrizable space is Hausdorff — so the question reduces to whether
diagram space has a metric, which is a question for a different unit.
</details>
<details><summary>Strategy</summary>
(b) They are a ladder in strength — normal ⇒ regular ⇒ Hausdorff, given
one-point sets closed. They are not a ladder in behaviour: the lower two are
closed under subspaces and products and the top one is not, so the stronger
property is the worse-behaved one, which is exactly Munkres's misnomer remark.
(d) A point cloud is discrete (top-06), hence metrizable by construction, hence
Hausdorff — the eighth property in this module settled by finiteness. For the
second half: diagram space would need a metric, or at least a Hausdorff topology,
and §§31–32 supply Theorem 32.2 (metrizable ⇒ normal ⇒ regular ⇒ Hausdorff) as
the route — but only once someone has produced the metric.
</details>
<details><summary>Partial</summary>
(a) Hausdorff: subspaces ✓ and products ✓ (Theorem 31.2(a)). Regular: ✓ and ✓
(Theorem 31.2(b)). Normal: products ✗ (Example 3 of §31, with Example 2);
subspaces — say what §§31–32 do and do not establish.
(d) Yes, trivially Hausdorff. The strip's claim about diagram space is an
expectation until a metric or a topology on that space is exhibited, which is
tda1-06's business, not §31's.
</details>
<details><summary>Worked start</summary>
(d) *A point cloud.* By top-06's Problem 1(c) a finite metric space carries the
discrete topology, and it is metrized by its own metric, so it is Hausdorff —
directly, since distinct points $x \neq y$ have disjoint balls of radius
$d(x,y)/2$.
⟨your step: add it to the module's running tally and say what the verdict is
worth. Then take the second half: state what would have to exist before "diagram
space is Hausdorff" is a theorem, and name the unit where that object is
constructed.⟩

(a), (b), (c) ⟨your step⟩
</details>
