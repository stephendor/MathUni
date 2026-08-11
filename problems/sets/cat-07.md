# cat-07 — Homology and persistence as functors

**Module:** Category Theory · **Unit:** cat-07
**Sources:** Oudot, *Persistence Theory: From Quiver Representations to Data
Analysis* — Chapter 1 "Algebraic Persistence" (pp. 13–28): §1's treatment of
representations of arbitrary subposets of $(\mathbb{R}, \le)$, where the poset
is "regard[ed] as a category in the natural way" — footnote 4: "with one object
per element $i \in T$ and a single morphism per couple $i \le j$" — and a
representation is defined to be **a functor to the category of vector spaces**,
with the remark that representations of any poset may be defined the same way
(p. 19); §2, Definition 1.7 that a persistence module over $T \subseteq
\mathbb{R}$ is a representation of the poset $(T, \le)$, Definition 1.8 on
zigzag modules and its rephrasing as a poset representation, the definition of
an interval and of the associated interval module, and **Theorem 1.9** (Interval
Decomposition) with its two sufficient conditions and its uniqueness clause
(pp. 20–21); §3 on barcodes and diagrams, including the $\mathsf{H}_0$ example
(pp. 21–27); the remark that such objects are pointwise finite-dimensional
representations of $(\mathbb{R}, \le)$ with identity and composition rules
"following from functoriality" (p. 26).
Spivak, *Seven Sketches in Compositionality* — §3.3.2 Definition 3.35 and
§3.3.4 Definition 3.49, carried in from cat-03 and cat-04.

**Where this unit's sources stop.** Oudot's account of filtrations, and of the
homology functor turning them into persistence modules, opens **Chapter 2**
(p. 29) — outside this unit's resources. Stability is Chapter 3 (p. 49), also
outside. So the composite that produces a persistence module from a filtration
is assembled here from cat-03's composition rule and at1-10's homology functor,
with Oudot supplying the target end only.

Interleaves at1-10, cat-03 and cat-04, whose composites, functors and natural
transformations this unit finally puts to the use the module was aimed at.

Submit your written solutions via `/grade cat-07`.

---

## Problem 1 (easy — the definition, and how little is new)

(a) State Oudot's Definition 1.7. Then unwind it completely: given his footnote
4, say what the category $(T, \le)$ is, what a functor out of it into
$\mathsf{Vect}_k$ consists of, and what the two functor conditions say here.
(b) Compare with cat-01's Example 3.3. Oudot writes $(T, \le)$ for
$T \subseteq \mathbb{R}$; Aluffi's construction needs only a reflexive
transitive relation. Say which is the special case of which, and whether
anything in Definition 1.7 uses antisymmetry.
(c) Oudot remarks that the identity and composition rules "follow from
functoriality". Write those rules out explicitly as conditions on the linear
maps $v_i^j : V_i \to V_j$, and match each to one clause of cat-03's
Definition 1.1.
(d) State Definition 1.8 and its rephrasing. Say why a general $A_n$-type
quiver gives a *zigzag* module rather than a persistence module, in terms of
the order relation involved.
(e) Oudot says a quiver "can be viewed as a category, with one object per node
and one morphism per finite oriented path", and that its representations are
"functors to the category of vector spaces". Say what this adds to the poset
picture and where the two coincide.

<details><summary>Hint</summary>
(b) A subset of $\mathbb{R}$ with $\le$ is a poset; posets are preorders with
antisymmetry.
(d) An $A_n$ quiver may have arrows pointing both ways along the line.
</details>
<details><summary>Partial</summary>
(a) The category has one object per element of $T$ and exactly one morphism
$i \to j$ whenever $i \le j$. A functor to $\mathsf{Vect}_k$ assigns a vector
space $V_i$ to each $i$ and a linear map $v_i^j : V_i \to V_j$ to each $i \le
j$, with $v_i^i = \mathrm{id}$ and $v_j^k \circ v_i^j = v_i^k$.
(b) $(T, \le)$ is a poset, hence a preorder, so Oudot's construction is a
special case of Aluffi's Example 3.3. ⟨your step: check whether antisymmetry is
used anywhere in Definition 1.7, and say what would change if $T$ carried only
a preorder.⟩
</details>
<details><summary>Strategy</summary>
The point of this problem is that Definition 1.7 introduces no new mathematics
at all — it names an object cat-01 and cat-03 already built. Notice how little
work it does, and then notice in Problem 3 how much Theorem 1.9 does.
</details>

---

## Problem 2 (easy — interval modules)

(a) Define an *interval* of $T$, following Oudot: a subset $S$ such that for
$i \le j \le k$ in $T$, if $i, k \in S$ then $j \in S$. Show that intervals of
$(\mathbb{R}, \le)$ are exactly the order-convex subsets, and list the possible
shapes.
(b) Define the interval module associated to $S$: $k$ at every index in $S$,
zero elsewhere, identities between copies of $k$, all other maps zero. Verify
it is a functor — that is, check the two conditions of Problem 1(c).
(c) Oudot notes that this definition "is oblivious to the actual map
orientations". Say what that means and why it matters for zigzag modules.
(d) Show that an interval module is *indecomposable*: it is not isomorphic to a
direct sum of two non-zero persistence modules. Say which fact about the field
$k$ you use.
(e) Give a persistence module over $T = \{1, 2, 3\}$ that is not an interval
module, and decompose it into interval modules by hand.

<details><summary>Hint</summary>
(b) The composition condition has cases depending on which of $i, j, k$ lie in
$S$; do them all.
(d) A direct sum decomposition would split some $V_i = k$.
</details>
<details><summary>Partial</summary>
(b) If $i \le j \le k$ all lie in $S$, both sides of $v_j^k v_i^j = v_i^k$ are
the identity. If any of them lies outside $S$, at least one map in the
composite is zero and so is $v_i^k$ — but you must check this using convexity:
if $i, k \in S$ and $j \notin S$, then $S$ is not an interval, so that case
cannot arise. ⟨your step: enumerate the remaining cases and confirm each.⟩
</details>

---

## Problem 3 (medium — the structure theorem)

(a) State Theorem 1.9 in full: both sufficient conditions (i) and (ii), the
conclusion, and the uniqueness clause.
(b) Condition (ii) requires $\mathbb{V}$ to be *pointwise finite-dimensional*.
Define that, and say why it is a condition on each $V_i$ separately rather than
on the module as a whole.
(c) Oudot says the theorem "summarizes the structural results from Section 1
(Theorems 1.1, 1.2, 1.3 and 1.6)" and that its conditions "are sufficient for
our purposes". Say what work "sufficient" is doing — in particular, whether the
theorem claims to characterise when interval decompositions exist.
(d) The uniqueness clause says the decomposition is unique "up to isomorphism
and permutation of the terms". Say why both qualifications are needed, and
connect this to cat-02's Proposition 5.4.
(e) A barcode is the multiset of intervals appearing in the decomposition.
Explain why Theorem 1.9 is exactly what makes a barcode a *well-defined
invariant*, and say what would go wrong without the uniqueness clause.

<details><summary>Hint</summary>
(c) Sufficient conditions are not necessary conditions.
(e) Without uniqueness, two different decompositions would give two different
barcodes for one module.
</details>
<details><summary>Partial</summary>
(c) Theorem 1.9 gives conditions under which a decomposition *exists*; it does
not say these are the only such conditions, and Oudot is explicit that they are
chosen as sufficient for his purposes. So a module failing both (i) and (ii)
is not thereby shown to be indecomposable or non-decomposable. ⟨your step: say
why that matters for anyone who wants to compute a barcode for a module arising
from data.⟩
(e) The barcode is read off a decomposition. If a module admitted two
essentially different decompositions, "the" barcode would not be defined —
uniqueness up to permutation is what makes the multiset an invariant of the
module rather than of the chosen decomposition.
</details>

---

## Problem 4 (medium — assembling the composite)

(a) Let $(T, \le) \subseteq (\mathbb{R}, \le)$ and let
$\mathcal{X} : (T, \le) \to \mathbf{Top}$ be a functor. Say concretely what
$\mathcal{X}$ is, and confirm that a nested family of spaces with inclusions is
one.
(b) Let $\mathsf{H}_p : \mathbf{Top} \to \mathsf{Vect}_k$ be homology with
field coefficients — a functor, by at1-10, and landing in vector spaces by
at1-09's coefficient material. Form the composite
$\mathsf{H}_p \circ \mathcal{X}$ and verify it is a functor, citing cat-03.
(c) Show that $\mathsf{H}_p \circ \mathcal{X}$ satisfies Oudot's
Definition 1.7 — that is, that it *is* a persistence module over $T$. Say which
of the two functor conditions supplies $v_i^i = \mathrm{id}$ and which supplies
$v_j^k v_i^j = v_i^k$.
(d) at1-10 and cat-03 both warned that "sample the filtration at level $t$" can
name two different functors, only one of which composes with $\mathsf{H}_p$ to
give a persistence module. Restate the distinction, and confirm that the
composite in (b) is the right one.
(e) Under what condition on $\mathcal{X}$ is the resulting module pointwise
finite-dimensional, so that Theorem 1.9(ii) applies? Say honestly whether this
unit's sources let you verify that condition for any particular family of
spaces, or whether that is owed by another module.

<details><summary>Hint</summary>
(c) The two conditions are exactly $F(\mathrm{id}) = \mathrm{id}$ and
$F(g \circ f) = F(g) \circ F(f)$.
(e) Pointwise finite-dimensional means each $\mathsf{H}_p(X_i)$ is
finite-dimensional.
</details>
<details><summary>Partial</summary>
(c) A composite of functors is a functor (cat-03), so $\mathsf{H}_p \circ
\mathcal{X}$ assigns a vector space to each $i \in T$ and a linear map to each
$i \le j$. $F(\mathrm{id}) = \mathrm{id}$ gives $v_i^i = \mathrm{id}$;
$F(g \circ f) = F(g) \circ F(f)$ gives $v_j^k v_i^j = v_i^k$. Those are exactly
Oudot's identity and composition rules, which he says "follow from
functoriality" — and this is that. ⟨your step: say what remains to be checked,
if anything.⟩
</details>

---

## Problem 5 (hard — why stability is not a natural transformation)

(a) Two persistence modules $M, N$ over $(\mathbb{R}, \le)$ are functors
$(\mathbb{R}, \le) \to \mathsf{Vect}_k$, so they are objects of a functor
category (cat-04, Aluffi's Exercise 1.9). Say what a *morphism* between them is
in that category, spelled out as a family of linear maps and a condition.
(b) For $\varepsilon \ge 0$ define the shift $N(\cdot + \varepsilon)$. Show
that shifting is a functor $(\mathbb{R}, \le) \to (\mathbb{R}, \le)$, so that
$N(\cdot + \varepsilon)$ is a composite and hence again a persistence module.
Say where $\varepsilon \ge 0$ is used.
(c) State what an $\varepsilon$-interleaving is, following cat-04's mission
strip: a pair of natural transformations $M \Rightarrow N(\cdot + \varepsilon)$
and $N \Rightarrow M(\cdot + \varepsilon)$ whose composites are the
$2\varepsilon$-shift maps. Write both composites out and say what the condition
asserts about each.
(d) Now the point. Explain why an interleaving is *not* a natural
transformation $M \Rightarrow N$, by identifying precisely what would have to
be true for such a transformation to exist and why interleaving is strictly
weaker. Give the case $\varepsilon = 0$ and say what an interleaving reduces to
there.
(e) The reflection, in three separate parts. This unit's mission strip is the
most careful of the seven in the module: it says persistence is a functor, that
stability is expressed *through interleavings of those functors*, and — the
clause worth dwelling on — "not as a natural transformation in its own right."

  First: which parts of that does this unit's sources establish? Be specific
  about what Oudot's Chapter 1 gives and what it does not.

  Second: the strip's caveat is a correction to a natural but wrong guess. Say
  what the wrong guess is, why it is tempting given cat-04, and why the caveat
  is right.

  Third: the module is now finished. Looking back across cat-01 to cat-07, name
  one place where a mission strip was loose and had to be bounded, one place
  where a source itself declined to prove what it stated, and one place where
  the categorical language did genuine work rather than renaming something. For
  each, say in one sentence what the episode taught.

<details><summary>Hint</summary>
(d) A natural transformation $M \Rightarrow N$ would give maps
$M_t \to N_t$ for every $t$, commuting with everything. An interleaving only
gives maps $M_t \to N_{t+\varepsilon}$.
(e) For the second question: cat-04 defined natural transformations and this
unit's strip is about a pair of them — so the tempting error is to compress the
pair into one.
</details>
<details><summary>Partial</summary>
(b) For $\varepsilon \ge 0$, $s \le t$ implies $s + \varepsilon \le t +
\varepsilon$, so shifting is monotone, hence a functor between the poset
categories. If $\varepsilon < 0$ it is still monotone — so say more precisely
what $\varepsilon \ge 0$ is needed for in the *interleaving* definition, rather
than in the shift alone.
(d) A natural transformation $M \Rightarrow N$ requires maps $M_t \to N_t$ for
each $t$, commuting with the internal maps of both modules. An interleaving
supplies only maps $M_t \to N_{t+\varepsilon}$ — the target has been shifted,
so nothing lands in $N_t$ at all. ⟨your step: do the case $\varepsilon = 0$ and
say what the pair of transformations and the composite condition reduce to.⟩
</details>
<details><summary>Worked start</summary>
(e) *First question.* Oudot's Chapter 1 establishes that a persistence module
*is* a functor: he regards $(T, \le)$ as a category "in the natural way" and
defines a representation to be a functor to vector spaces, then Definition 1.7
names such a representation a persistence module. He also gives Theorem 1.9,
the interval decomposition, which is what makes a barcode well defined.

What Chapter 1 does *not* give: filtrations and the homology functor turning
them into persistence modules — that opens Chapter 2, p. 29 — and stability,
which is Chapter 3, p. 49. Neither is in this unit's resources. So the
composite of Problem 4 is assembled from cat-03's composition rule and
at1-10's homology functor, with Oudot supplying only the target end; and the
strip's stability clause is a forward pointer to tda1-06 and tda1-07.

⟨your step: complete the audit, then answer the second and third questions.⟩
</details>
<details><summary>Strategy</summary>
(d) is the mathematical heart and (e) is the point of the module. The caveat in
the mission strip — "not as a natural transformation in its own right" — is the
kind of precision that only becomes visible once you have cat-04's definition
in hand and try to apply it; before that, "there is a map between the two
modules" sounds like it must mean a natural transformation. Getting clear on
why it does not is the last thing the cat module is for.
</details>
