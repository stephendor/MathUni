# cat-04 — Natural transformations and the Yoneda lemma

**Module:** Category Theory · **Unit:** cat-04
**Sources:** Aluffi, *Algebra: Chapter 0* — §VIII.1.5 (pp. 492–493):
Definition 1.15 of a natural transformation and of a natural isomorphism, the
remark that any "there is a natural homomorphism…" is likely hiding one, with
the Hurewicz homomorphism named as an example, and the informal account of
adjoint functors with Example 1.16 on free groups; Exercise 1.9 (p. 497),
defining the functor category $\mathsf{D}^\mathsf{C}$ whose morphisms are
natural transformations, and the covariant functor
$X \mapsto h_X := \operatorname{Hom}_\mathsf{C}(-, X)$; **Exercise 1.10**
(p. 497), which *states* the Yoneda lemma and supplies a hint; item 1.11
(p. 497) on representable functors.
Spivak, *Seven Sketches in Compositionality* — §3.3.4 (p. 95): Definition 3.49
of a natural transformation in specification style with the naturality
condition and its commutative square, and Definition 3.51 of a diagram as a
functor from an indexing category; §1.2.3 (p. 20): Exercise 1.66 and the remark
naming it the **Yoneda lemma for preorders**, with the gloss that "to know an
element is the same as knowing its upper set".

**Which source carries the Yoneda lemma, and in what form.** Neither proves it.
Aluffi *sets* it, as Exercise 1.10, with a statement and a hint — so Problem 5
is that exercise worked from Aluffi's own hint, which is a legitimate use of the
source. Spivak gives only the preorder special case, and says of the general
lemma that "we have not introduced it". Do not write "Aluffi proves".

Interleaves cat-03, whose Hom functors are the $h_X$ this unit is about, and
cat-01, whose preorder categories are where Spivak's special case lives.

Submit your written solutions via `/grade cat-04`.

---

## Problem 1 (easy — the definition, twice again)

(a) State Aluffi's Definition 1.15 and Spivak's Definition 3.49, and check they
agree. Note that Spivak's naturality equation is written in diagrammatic order.
(b) Draw the naturality square and say, in words, what it asserts: that
transforming and then mapping equals mapping and then transforming.
(c) Define *natural isomorphism*. Aluffi asks that $\nu_X$ be an isomorphism for
every $X$; Spivak asks that each component be an isomorphism. Say why this is
not the same as asking that $\nu$ be an isomorphism in some larger sense — and
then say, using Exercise 1.9, in what sense it *is*.
(d) Aluffi remarks that any statement of the form "there is a natural
homomorphism…" is likely hiding a natural transformation, and names the
Hurewicz homomorphism $\pi_1 \to H_1$. Say which two functors it is a
transformation between, and what the naturality square asserts for a map
$f : X \to Y$ of spaces.
(e) Give a family of morphisms $\nu_X$ that is *not* natural, and say which
square fails.

<details><summary>Hint</summary>
(c) Exercise 1.9 makes natural transformations the morphisms of a category.
(e) Try two functors $\mathsf{Vect}_k \to \mathsf{Vect}_k$ and a family
depending on a choice of basis.
</details>
<details><summary>Partial</summary>
(c) A natural isomorphism is a natural transformation all of whose components
are isomorphisms. That is a condition checked object by object, not a statement
about $\nu$ itself. But by Exercise 1.9 the functors $\mathsf{C} \to \mathsf{D}$
form a category $\mathsf{D}^\mathsf{C}$ whose morphisms are natural
transformations — and in *that* category, a natural transformation is an
isomorphism exactly when every component is. ⟨your step: prove that equivalence;
the inverse components assemble into a natural transformation, and naturality
of the inverse is what has to be checked.⟩
</details>

---

## Problem 2 (easy — the functor category)

(a) Do Aluffi's Exercise 1.9: for $\mathsf{C}$ small, define the functor
category $\mathsf{D}^\mathsf{C}$ with covariant functors as objects and natural
transformations as morphisms. Give the identity natural transformation and the
composition, and verify the category axioms of cat-01's Definition 3.1.
(b) Why does Aluffi require $\mathsf{C}$ to be *small*? Say what would go wrong
otherwise, referring to cat-01's class-versus-set discussion.
(c) cat-03 used the category $\mathbf{Top}^P$ of filtrations without
constructing it. Construct it now: what are its objects, and what is a morphism
between two filtrations?
(d) Second half of Exercise 1.9: show that $X \mapsto h_X :=
\operatorname{Hom}_\mathsf{C}(-, X)$ defines a covariant functor
$\mathsf{C} \to \mathsf{Set}^{\mathsf{C}^{\mathrm{op}}}$. Define the action on
morphisms and check functoriality.
(e) Spivak's Definition 3.51 defines a *diagram* in $\mathsf{C}$ as a functor
$D : \mathsf{J} \to \mathsf{C}$ from an indexing category, and says $D$
commutes when $D(f) = D(f')$ for every parallel pair in $\mathsf{J}$. Use this
to say precisely what the naturality square of Problem 1(b) is a diagram *of*,
and what its indexing category is.

<details><summary>Hint</summary>
(b) The objects of $\mathsf{D}^\mathsf{C}$ are functors; for
$\operatorname{Hom}$ to be a *set* you need control over how many there are.
(d) For $\alpha : X \to Y$, you need a natural transformation
$h_X \Rightarrow h_Y$; its component at $A$ should send
$\varphi : A \to X$ to something in $\operatorname{Hom}(A, Y)$.
</details>
<details><summary>Partial</summary>
(d) The component at $A$ sends $\varphi \in \operatorname{Hom}(A, X)$ to
$\alpha\varphi \in \operatorname{Hom}(A, Y)$ — post-composition, exactly as in
cat-03. Naturality in $A$ says that pre-composing with $\psi : A' \to A$ and
then post-composing with $\alpha$ is the same as doing it the other way, which
is associativity. ⟨your step: check that $X \mapsto h_X$ preserves identities
and composition, so that it is a functor and not merely an assignment.⟩
</details>

---

## Problem 3 (medium — Spivak's preorder Yoneda)

(a) Do Spivak's Exercise 1.66, parts 1–4, for a preorder $(P, \le)$:
show $\uparrow p := \{p' \mid p \le p'\}$ is an upper set; show
$\uparrow$ is a monotone map $P^{\mathrm{op}} \to \mathsf{U}(P)$; show
$p \le p'$ if and only if $\uparrow(p') \subseteq \uparrow(p)$; and draw the
picture for $b \ge a \le c$.
(b) Part 3 is the substance. Say why the *only if* direction is easy and the
*if* direction is where the content is, and identify the point where you have
to produce an element of $\uparrow(p')$ to test against.
(c) Spivak glosses the result: "to know an element is the same as knowing its
upper set — that is, knowing its web of relationships with the other elements of
the preorder." Say precisely what "the same as" means here, in terms of part 3.
(d) Relate this to cat-01. A preorder is a category with at most one morphism
between any two objects. Say what $\uparrow p$ is in categorical language, and
why the monotone map is *contravariant* — that is, why it goes out of
$P^{\mathrm{op}}$.
(e) Spivak says the general Yoneda lemma "is a powerful tool in category theory,
and a fascinating philosophical idea besides", and elsewhere says of it "we have
not introduced it". State honestly what Spivak has and has not given you, and
say which source Problem 5 will have to draw on instead.

<details><summary>Hint</summary>
(d) $\uparrow p$ records, for each $p'$, whether $\operatorname{Hom}(p, p')$ is
empty. Compare $h_X = \operatorname{Hom}(-, X)$.
</details>
<details><summary>Partial</summary>
(d) $\uparrow p$ is the record of which objects receive a morphism *from* $p$,
so it corresponds to $\operatorname{Hom}(p, -)$ — the covariant Hom functor,
valued in truth values rather than sets because the Hom-sets here have at most
one element. It is contravariant as a map into $\mathsf{U}(P)$ ordered by
inclusion because a *larger* $p$ has a *smaller* upper set, which is exactly
part 3.
</details>

---

## Problem 4 (medium — naturality in practice)

(a) Aluffi introduces adjoint functors informally: $\mathcal{F}$ and
$\mathcal{G}$ are adjoint when there are *natural* isomorphisms
$\operatorname{Hom}_\mathsf{C}(X, \mathcal{G}(Y)) \cong
\operatorname{Hom}_\mathsf{D}(\mathcal{F}(X), Y)$. Say what "natural" is doing
in that sentence, and in which variables.
(b) Example 1.16: the free group functor $F : \mathsf{Set} \to \mathsf{Grp}$ is
left-adjoint to the forgetful functor $S$. Write out the bijection
$\operatorname{Hom}_{\mathsf{Set}}(A, S(G)) \cong
\operatorname{Hom}_{\mathsf{Grp}}(F(A), G)$ and verify naturality in $A$.
(c) Aluffi remarks that "the free functor is, as a rule, left-adjoint to the
forgetful functor". Give one further instance from aa and check the bijection.
(d) He also says the technical advantage is that "properties of the interesting
ones may be translated into properties of the harmless ones". Give an example of
that translation, using Lemma 1.17 as the model without proving it.
(e) Aluffi leaves the formalisation of adjunctions "to the inextinguishable
reader", noting that it needs a natural isomorphism of bifunctors
$\mathsf{C}^{\mathrm{op}} \times \mathsf{D} \to \mathsf{Set}$. Say what a
bifunctor is and why *two* variables are needed here rather than one.

<details><summary>Hint</summary>
(a) The bijection must commute with the maps induced by morphisms in each
variable separately.
</details>
<details><summary>Partial</summary>
(a) "Natural" means the bijection is a natural isomorphism, not merely a
bijection for each pair $(X, Y)$: it must commute with the maps induced by
$X' \to X$ and by $Y \to Y'$. Without naturality the condition is far too weak —
it would only say the two Hom-sets have the same cardinality. ⟨your step: give
two functors with equinumerous Hom-sets that are not adjoint, to show
naturality is not automatic.⟩
</details>

---

## Problem 5 (hard — the Yoneda lemma, from Aluffi's hint)

Aluffi *sets* this as Exercise 1.10 and does not prove it. What follows is his
statement and his hint, and the work is yours.

(a) State it. Let $\mathsf{C}$ be a category, $X$ an object, and
$h_X := \operatorname{Hom}_\mathsf{C}(-, X)$ the contravariant Hom functor. For
every contravariant $\mathscr{F} : \mathsf{C} \to \mathsf{Set}$, there is a
bijection between the set of natural transformations $h_X \Rightarrow
\mathscr{F}$ and the set $\mathscr{F}(X)$.
(b) Define the forward map, as Aluffi specifies: a natural transformation
$\nu : h_X \Rightarrow \mathscr{F}$ has a component
$\nu_X : h_X(X) = \operatorname{Hom}_\mathsf{C}(X, X) \to \mathscr{F}(X)$, and
$\operatorname{id}_X$ lives in $h_X(X)$. Send $\nu$ to
$\nu_X(\operatorname{id}_X) \in \mathscr{F}(X)$.
(c) Now Aluffi's hint: "Produce an inverse of the specified map. For every
$f \in \mathscr{F}(X)$ and every $\varphi \in \operatorname{Hom}_\mathsf{C}(A, X)$,
how do you construct an element of $\mathscr{F}(A)$?" Answer it, and use the
answer to define a candidate inverse.
(d) Prove the two round trips are identities. One direction is a short
computation; the other is where the *naturality* of $\nu$ is used, and it is
used exactly once. Say where.
(e) The reflection. Yoneda says an object is completely determined by the maps
into it — "an object is known by its arrows". Three questions, kept separate.
First: in what precise sense determined? State it via Aluffi's Exercise 1.11 on
representable functors, and say whether the determination is up to equality or
up to isomorphism. Second: compare with Spivak's preorder version from
Problem 3, and say which features of the general lemma are already visible
there and which are invisible because Hom-sets in a preorder have at most one
element. Third: the mission strip for this unit describes an $\varepsilon$-interleaving
as a pair of natural transformations. Say what the Yoneda lemma does and does
*not* contribute to that description — in particular, whether anything in this
unit shows that interleavings exist, or only what kind of object one would be.

<details><summary>Hint</summary>
(c) You have $\varphi : A \to X$ and $\mathscr{F}$ contravariant, so
$\mathscr{F}(\varphi)$ runs from $\mathscr{F}(X)$ to $\mathscr{F}(A)$. Apply it
to $f$.
(d) Naturality is needed to show that a natural transformation is recovered
from its value on $\operatorname{id}_X$ — that is, in the round trip that starts
and ends at $\nu$.
</details>
<details><summary>Partial</summary>
(c) Given $f \in \mathscr{F}(X)$ and $\varphi \in \operatorname{Hom}(A, X)$,
set $\nu^f_A(\varphi) := \mathscr{F}(\varphi)(f) \in \mathscr{F}(A)$. That
defines a component at every $A$; naturality of $\nu^f$ follows from
functoriality of $\mathscr{F}$ in the reversed order.
(d) Starting from $f$: $\nu^f_X(\operatorname{id}_X) = \mathscr{F}(\operatorname{id}_X)(f) = f$,
using only that $\mathscr{F}$ preserves identities. Starting from $\nu$: put
$f = \nu_X(\operatorname{id}_X)$ and take any $\varphi : A \to X$; then
$\nu^f_A(\varphi) = \mathscr{F}(\varphi)(\nu_X(\operatorname{id}_X))$, and
⟨your step: apply the naturality square of $\nu$ at $\varphi$ to rewrite this
as $\nu_A(h_X(\varphi)(\operatorname{id}_X)) = \nu_A(\varphi)$. Say which square
and which direction round it you used.⟩
</details>
<details><summary>Worked start</summary>
(e) *First question.* Exercise 1.11 defines a contravariant functor
$\mathsf{C} \to \mathsf{Set}$ to be *representable* when it is naturally
isomorphic to some $h_X$, and asks you to prove that $\mathsf{C}$ is equivalent
to the subcategory of representable functors in
$\mathsf{Set}^{\mathsf{C}^{\mathrm{op}}}$. So the determination is by an
*equivalence of categories* in cat-03's sense — fully faithful and essentially
surjective — and therefore up to isomorphism, never up to equality. ⟨your step:
say why "up to equality" is not even a sensible thing to hope for here, using
cat-03's Example 1.8 as the model.⟩

*Second and third questions:* ⟨yours. For the third, be careful to separate
"this unit tells you what an interleaving is made of" from "this unit shows
interleavings exist or that stability holds". Only one of those is true, and
saying which is the point of the exercise.⟩
</details>
<details><summary>Strategy</summary>
The proof is four lines and every line is forced; the difficulty is entirely in
keeping track of variance. Write $\mathscr{F}(\varphi)$ with its source and
target explicitly at every step and the argument writes itself. Part (e) is
where the unit connects to the mission, and the third question is the one to
answer carefully.
</details>
