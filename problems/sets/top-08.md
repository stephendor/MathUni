# top-08 — Compactness

**Module:** Topology · **Unit:** top-08
**Sources:** Munkres, *Topology*, 2nd ed. — §26 "Compact Spaces" (pp. 163–171)
and §27 "Compact Subspaces of the Real Line" (pp. 172–178). Numbered results
used: Lemma 26.1, Theorem 26.2, Theorem 26.3, Theorem 26.5, Theorem 26.6,
Theorem 26.7, Lemma 26.8, Theorem 26.9, Theorem 27.1, Corollary 27.2,
Theorem 27.3, Theorem 27.4, Lemma 27.5, Theorem 27.6, Theorem 27.7,
Corollary 27.8.

Interleaves top-03 (Theorem 26.3 needs Hausdorff, and Theorem 26.6 is a
homeomorphism criterion resting on it), top-04 (Theorem 26.5 is the compactness
analogue of Theorem 23.5), top-06 (Lemma 27.5 and Theorem 27.6 are metric
statements), and top-07 throughout — §26 and §27 are the companion of §§23–25,
and Theorem 27.4 stands to compactness as Theorem 24.3 stands to connectedness.

Submit your written solutions via `/grade top-08`.

---

## Problem 1 (easy — covers, and the two spaces that fail)

A collection $\mathcal{A}$ **covers** $X$ if the union of its elements is $X$;
it is an **open covering** if its elements are open. $X$ is **compact** if every
open covering contains a finite subcollection that also covers $X$ (p. 164).

(a) Prove Lemma 26.1: $Y \subset X$ is compact if and only if every covering of
$Y$ by sets open in $X$ has a finite subcollection covering $Y$. Say what work
the lemma saves you in practice.
(b) Verify Munkres's Example 1 — $\mathbb{R}$ is not compact, via
$\{(n, n+2) : n \in \mathbb{Z}\}$ — and his Example 4: $(0,1]$ is not compact,
via $\{(1/n, 1) : n \in \mathbb{Z}_+\}$. For each, say which point or points a
finite subfamily fails to reach.
(c) Verify Example 2: $X = \{0\} \cup \{1/n : n \in \mathbb{Z}_+\}$ **is**
compact. Munkres's argument turns on one sentence — "the set $U$ contains all
but finitely many of the points $1/n$" — prove that sentence rather than
assuming it.
(d) Verify Example 3: any space with finitely many points is compact. Then say
what Examples 2 and 4 together show about which of $\{0\} \cup \{1/n\}$ and
$\{1/n\}$ is compact, and what the difference is.

*(Munkres §26, p. 164 for the definitions and Examples 1–4; pp. 164–165 for
Lemma 26.1.)*

<details><summary>Nudge</summary>
In (c), $U$ is open and contains $0$, so it contains an interval about $0$.
</details>
<details><summary>Strategy</summary>
(a) The two conditions differ only by intersecting with $Y$; the lemma lets you
work with sets open in the ambient space, which is usually where you can name
them.
(c) $U$ open with $0 \in U$ gives $\epsilon > 0$ with
$(-\epsilon, \epsilon) \cap X \subset U$; and $1/n < \epsilon$ for all
$n > 1/\epsilon$, so only finitely many points of $X$ escape $U$.
</details>
<details><summary>Partial</summary>
(b) A finite subfamily of $\{(n,n+2)\}$ is bounded, so misses all large reals. A
finite subfamily of $\{(1/n,1)\}$ has a largest $1/n$, so misses every point of
$(0, 1/n]$ — in particular it never reaches down towards $0$.
(d) $\{1/n : n \in \mathbb{Z}_+\}$ is *not* compact; adding the single limit
point $0$ makes it compact. The difference is exactly that $0$ forces every open
cover to swallow a tail.
</details>
<details><summary>Worked start</summary>
(c) Let $\mathcal{A}$ be an open covering of $X = \{0\} \cup \{1/n\}$ and choose
$U \in \mathcal{A}$ with $0 \in U$. Since $U$ is open in $X$, there is
$\epsilon > 0$ with $(-\epsilon, \epsilon) \cap X \subset U$. By the Archimedean
property there is $N$ with $1/N < \epsilon$; then $1/n < \epsilon$ for all
$n \ge N$, so every such $1/n$ lies in $U$.
⟨your step: so the points of $X$ outside $U$ are among $1, 1/2, \dots, 1/(N-1)$,
a finite list. Finish the covering argument.⟩

(a), (b), (d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — closed, Hausdorff, and the homeomorphism criterion)

(a) Prove Theorem 26.2: every closed subspace of a compact space is compact.
(b) Prove Theorem 26.3: every compact subspace of a Hausdorff space is closed.
Munkres's proof separates a point $x_0 \notin Y$ from each $y \in Y$ and then
takes a *finite intersection*; say why the intersection must be finite and what
would go wrong with an infinite one.
(c) Show that the Hausdorff hypothesis in Theorem 26.3 cannot be dropped: give a
non-Hausdorff space with a compact subspace that is not closed.
(d) Prove Theorem 26.6: a bijective continuous $f : X \to Y$ with $X$ compact
and $Y$ Hausdorff is a homeomorphism. Then revisit top-04's Example 6 — the map
$F : [0,1) \to S^1$, continuous and bijective and not a homeomorphism — and say
which hypothesis of Theorem 26.6 it fails, with the reason.

*(Munkres §26, p. 165 for Theorem 26.2; pp. 165–166 for Theorem 26.3; p. 167 for
Theorem 26.6. top-04's Example 6 is Munkres §18, p. 107.)*

<details><summary>Nudge</summary>
For (c), the finite complement topology on an infinite set is not Hausdorff and
has a great many compact subspaces.
</details>
<details><summary>Strategy</summary>
(b) The neighbourhoods $U_{y_1}, \dots, U_{y_n}$ of $x_0$ are finitely many
because compactness produced finitely many $V_{y_i}$; a finite intersection of
open sets is open, an infinite one need not be — top-01's axiom (3).
(d) $[0,1)$ is not compact: the covering $\{[0, 1 - 1/n)\}$ has no finite
subcover. $S^1$ is Hausdorff, being a subspace of $\mathbb{R}^2$
(Theorem 17.11).
</details>
<details><summary>Partial</summary>
(c) Take $X = \mathbb{R}$ with the finite complement topology and $Y = (0,1)$.
Every subspace of $X$ is compact — given a cover, one member's complement is
finite, so finitely many more finish the job — but $(0,1)$ is not closed, since
its complement is infinite and not all of $X$.
</details>
<details><summary>Worked start</summary>
(a) Let $Y$ be closed in the compact space $X$, and let $\mathcal{A}$ be a
covering of $Y$ by sets open in $X$. Adjoin the open set $X - Y$ to
$\mathcal{A}$; the result covers $X$.
⟨your step: extract a finite subcover of $X$, discard $X - Y$ if present, and
say why what remains still covers $Y$. Then cite Lemma 26.1.⟩

(d) By Theorem 26.6 it suffices to show $f$ carries closed sets to closed sets.
If $A$ is closed in $X$ then $A$ is compact (Theorem 26.2), so $f(A)$ is compact
(Theorem 26.5), so $f(A)$ is closed in $Y$ (Theorem 26.3, using $Y$ Hausdorff).
⟨your step: say why "carries closed sets to closed sets" is exactly the
continuity of $f^{-1}$, and then diagnose top-04's Example 6⟩

(b), (c) ⟨your step⟩
</details>

---

## Problem 3 (medium — products, tubes, and the finite intersection property)

(a) Prove Lemma 26.8, the tube lemma: for $Y$ compact, an open set $N$ of
$X \times Y$ containing the slice $x_0 \times Y$ contains a tube $W \times Y$
about it. Say precisely where compactness of $Y$ is used, and give an example
with $Y$ non-compact where the conclusion fails.
(b) Prove Theorem 26.7 for two factors, using the tube lemma. Then say why the
statement is restricted to *finitely* many factors here, and whether that
restriction is essential or merely what §26 proves — cite what Munkres says,
not what you expect.
(c) State the **finite intersection property** and prove Theorem 26.9: $X$ is
compact if and only if every collection of closed sets with the finite
intersection property has non-empty total intersection. Say which De Morgan
identity converts one statement into the other.
(d) Use Theorem 26.9 to prove the nested interval property: a decreasing
sequence $C_1 \supset C_2 \supset \cdots$ of non-empty closed subsets of a
compact space has non-empty intersection. Then show it fails in $\mathbb{R}$ by
exhibiting nested non-empty closed sets with empty intersection.

*(Munkres §26, p. 168 for Theorem 26.7 and Lemma 26.8; pp. 169–170 for the
finite intersection property and Theorem 26.9.)*

<details><summary>Nudge</summary>
For (a)'s failure, take $Y = \mathbb{R}$ and an open set that pinches towards
the slice.
</details>
<details><summary>Strategy</summary>
(a) Cover $x_0 \times Y$ by basis elements $U \times V$ inside $N$; compactness
of $Y$ (via the homeomorphism $Y \cong x_0 \times Y$) gives finitely many, and
$W$ is the intersection of their $U$'s — finite, hence open.
(c) $X$ is compact iff every open cover has a finite subcover; complementing
turns covers into collections of closed sets with empty intersection, and finite
subcovers into finite subcollections with empty intersection.
</details>
<details><summary>Partial</summary>
(a) With $Y = \mathbb{R}$ and $N = \{(x,y) : |x| \cdot (1 + y^2) < 1\}$, the
slice $0 \times \mathbb{R}$ lies in $N$ but no tube $W \times \mathbb{R}$ does.
(d) In $\mathbb{R}$, take $C_n = [n, \infty)$: each is non-empty and closed, they
are nested, and the intersection is empty.
</details>
<details><summary>Worked start</summary>
(c) *Statement.* $\mathcal{C}$ has the finite intersection property if every
finite subcollection has non-empty intersection.
*Proof of Theorem 26.9.* Given a collection $\mathcal{C}$ of subsets of $X$, put
$\mathcal{A} = \{X - C : C \in \mathcal{C}\}$. Then:
$\mathcal{C}$ consists of closed sets iff $\mathcal{A}$ consists of open sets;
and by De Morgan, $\bigcap_{C} C = \varnothing$ iff $\bigcup_{A} A = X$, i.e.
iff $\mathcal{A}$ covers $X$.
⟨your step: translate "some finite subcollection of $\mathcal{A}$ covers $X$"
into a statement about $\mathcal{C}$, and then read off both directions of the
theorem⟩

(a), (b), (d) ⟨your step⟩
</details>

---

## Problem 4 (medium–hard — the real line, and two theorems calculus assumed)

(a) Prove Theorem 27.1: in a simply ordered set with the least upper bound
property, every closed interval is compact in the order topology. Deduce
Corollary 27.2 for $\mathbb{R}$.
(b) Prove Theorem 27.3: $A \subset \mathbb{R}^n$ is compact if and only if it is
closed and bounded in the euclidean or square metric. Say which direction needs
Theorem 26.7 and which needs Theorem 26.2, and where top-06's Theorem 20.3 is
used.
(c) Prove Theorem 27.4, the extreme value theorem, in Munkres's generality.
Compare its structure with Theorem 24.3 of top-07: one is powered by
connectedness and the other by compactness, and each fails without its
hypothesis — give the two one-line counterexamples on $(0,1)$.
(d) Prove Lemma 27.5, the Lebesgue number lemma, and then Theorem 27.6, the
uniform continuity theorem. State the definition of uniform continuity first,
and say exactly which quantifier moves when "continuous" becomes "uniformly
continuous".

*(Munkres §27, pp. 172–173 for Theorem 27.1; p. 174 for Corollary 27.2 and
Theorem 27.3; p. 174 for Theorem 27.4; pp. 175–176 for the distance from a point
to a set, Lemma 27.5, uniform continuity and Theorem 27.6.)*

<details><summary>Nudge</summary>
For (c)'s counterexamples, $f(x) = 1/x$ on $(0,1)$ and $f(x) = x$ on
$(0,1)$ do different jobs.
</details>
<details><summary>Strategy</summary>
(b) Forwards: compact ⇒ closed needs $\mathbb{R}^n$ Hausdorff (Theorem 26.3),
and bounded follows from covering by balls. Backwards: closed and bounded puts
$A$ inside a cube $[-M,M]^n$, compact by Corollary 27.2 and Theorem 26.7, and
then Theorem 26.2 finishes. Theorem 20.3 is what lets you use either metric.
(d) In continuity, $\delta$ may depend on the point; in uniform continuity a
single $\delta$ must serve every point. The Lebesgue number is what produces the
uniform one.
</details>
<details><summary>Partial</summary>
(c) On $(0,1)$: $f(x) = 1/x$ is continuous and unbounded, so no maximum — the
extreme value theorem fails without compactness. And $f(x) = x$ on the
*disconnected* domain $(0,1) \cup (2,3)$ takes values below $1$ and above $2$ but
never $1.5$ — the intermediate value theorem fails without connectedness.
</details>
<details><summary>Worked start</summary>
(c) Let $f : X \to Y$ be continuous with $X$ compact and $Y$ ordered. The image
$f(X)$ is compact by Theorem 26.5. It suffices to show a non-empty compact
subspace $A$ of an ordered set has a largest and a smallest element.
⟨your step: suppose $A$ has no largest element. Then $\{(-\infty, a) : a \in A\}$
covers $A$ — why? — and a finite subcover has a largest $a_i$, which is then not
covered. Finish, and do the smallest element by symmetry.⟩

(a), (b), (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — uncountability, and the mission's trivial compactness)

(a) Define an **isolated point** (p. 176) and prove Theorem 27.7: a non-empty
compact Hausdorff space with no isolated points is uncountable. Then deduce
Corollary 27.8: every closed interval in $\mathbb{R}$ is uncountable.
(b) Munkres's §24, Example 6 — the ordered square is not path connected — ended
by appealing to the uncountability of $I$, "which we shall prove later"
(top-07's Problem 3(d)). Corollary 27.8 is that promise redeemed. Confirm that
the two are the same statement, and say whether the argument in Example 6 is now
complete.
(c) **The mission clause.** This unit's strip reads: "TDA's theory lives on
compact spaces; filtrations of compact data are where the theorems hold." Using
Munkres's Example 3, decide whether a point cloud is compact, and how much that
fact tells you. Then say what the *theorems* of TDA actually require to be
compact, and why that is a different space from the one the strip's phrase
"compact data" names.
(d) Give a compact space and a non-compact space that are homotopy equivalent,
and a compact space and a non-compact space that are not homeomorphic *for that
reason*. Then say, in one sentence each, whether compactness is a topological
property in Munkres's sense (top-04, p. 105) and whether it is a homotopy
invariant.

*(Munkres §27, p. 176 for isolated points and Theorem 27.7; p. 177 for
Corollary 27.8; §26, p. 164, Example 3, for finite spaces. Parts (c) and (d) are
not in Munkres; (d) uses the definition of a topological property from §18,
p. 105, and homotopy equivalence from at1-01.)*

<details><summary>Nudge</summary>
For (d), a point and $\mathbb{R}$ are homotopy equivalent — top-04's mission
bound already used this pair.
</details>
<details><summary>Strategy</summary>
(c) Example 3 says every finite space is compact, so a point cloud is compact
for a reason that has nothing to do with its geometry — exactly as top-06 found
its topology discrete for a reason that had nothing to do with its distances.
What TDA's theorems ask to be compact is the underlying space being sampled, or
the parameter interval of the filtration, not the finite sample.
(d) A one-point space is compact; $\mathbb{R}$ is not; they are homotopy
equivalent, so compactness is not a homotopy invariant. It *is* a topological
property, since it is stated purely in terms of open sets.
</details>
<details><summary>Partial</summary>
(c) Every point cloud is compact, trivially and uninformatively. The compactness
that the theorems use is a hypothesis on a different object.
(d) $[0,1]$ and $(0,1)$ are not homeomorphic, and compactness is a legitimate
reason: one is compact and the other is not, and compactness transfers along
homeomorphisms.
</details>
<details><summary>Worked start</summary>
(c) By Munkres's Example 3 (p. 164), "any space $X$ containing only finitely many
points is necessarily compact, because in this case every open covering of $X$ is
finite." A point cloud is a finite set, so it is compact — and the argument never
looked at a single distance.
⟨your step: say what this tells you about the point cloud (compare top-06's
Problem 1(d)), then identify what object TDA's stability and structure theorems
actually require to be compact, and say why the strip's phrase names the wrong
one⟩

(a), (b), (d) ⟨your step⟩
</details>
