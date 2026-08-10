# cat-03 — Functors

**Module:** Category Theory · **Unit:** cat-03
**Sources:** Aluffi, *Algebra: Chapter 0* — §VIII.1.1–1.2 (pp. 484–487):
Definition 1.1 of a covariant functor, the definition of a contravariant
functor as a covariant functor on $\mathsf{C}^{\mathrm{op}}$, the reversal
$\mathcal{G}(\beta\alpha) = \mathcal{G}(\alpha)\mathcal{G}(\beta)$, the
statement that commutative diagrams go to commutative diagrams, presheaves,
additive functors, forgetful functors, Examples 1.2–1.5, and the Hom functors
$\operatorname{Hom}_\mathsf{C}(X,-)$ and $\operatorname{Hom}_\mathsf{C}(-,X)$
(pp. 484–486); Definition 1.6 (faithful, full) and Definition 1.7 (equivalence
of categories) with Examples 1.8 and 1.9 (p. 488).
Spivak, *Seven Sketches in Compositionality* — §3.3.2 (p. 91): Definition 3.35
of a functor in the specification style, Example 3.36 with the three functors
$\mathbf{2} \to \mathbf{3}$, Example 3.38 on the free and commutative square
categories, and the remark that these examples are all determined by their
action on objects while functors in general are not; §3.3.3 (p. 93):
Definition 3.44, that a $\mathcal{C}$-instance is a functor
$\mathcal{C} \to \mathbf{Set}$, and the summary that a schema is a category and
the data is a set-valued functor whose constraints are enforced by preservation
of composition; §3.3 (p. 101): the composite of two functors, worked through
$\mathbf{Gr} \to \mathrm{DDS} \to \mathbf{Set}$.

Interleaves cat-01 and cat-02, whose categories and universal properties are
what functors now move between, and at1-10, which met the definition from
Hatcher's side and formed a composite this unit can finally justify.

Submit your written solutions via `/grade cat-03`.

---

## Problem 1 (easy — the definition, twice)

(a) State Aluffi's Definition 1.1 of a covariant functor: the assignment on
objects, the function on Hom-sets, and the two conditions.
(b) State Spivak's Definition 3.35. He writes it as a specification — "to
specify a functor, one specifies …" — with two constituents and two properties.
Match his (i), (ii), (a), (b) against Aluffi's clauses and confirm they define
the same thing.
(c) Spivak writes composition in diagrammatic order, $F(f\,;g) = F(f)\,;F(g)$,
while Aluffi writes $\mathcal{F}(\beta\circ\alpha) =
\mathcal{F}(\beta)\circ\mathcal{F}(\alpha)$. Show these are the same condition,
and say what would go wrong if you mixed the conventions inside one argument.
(d) Aluffi defines a contravariant functor $\mathsf{C} \to \mathsf{D}$ as a
covariant functor $\mathsf{C}^{\mathrm{op}} \to \mathsf{D}$. Unwind that into a
direct statement, and derive the reversal
$\mathcal{G}(\beta\alpha) = \mathcal{G}(\alpha)\mathcal{G}(\beta)$.
(e) Both authors note that functors send commutative diagrams to commutative
diagrams. Prove it for a triangle, and say which of the two functor conditions
is doing the work.

<details><summary>Hint</summary>
(c) $f\,;g$ means "first $f$, then $g$"; $\beta\circ\alpha$ means the same thing
written the other way round.
(e) Commutativity is an equation between composites.
</details>
<details><summary>Partial</summary>
(d) A contravariant $\mathcal{G}$ assigns to each object $A$ an object
$\mathcal{G}(A)$, and to each $\alpha \in \operatorname{Hom}(A,B)$ a morphism
$\mathcal{G}(\alpha) \in \operatorname{Hom}(\mathcal{G}(B), \mathcal{G}(A))$ —
note the swap — preserving identities, with
$\mathcal{G}(\beta\alpha) = \mathcal{G}(\alpha)\mathcal{G}(\beta)$. The
reversal is forced: in $\mathsf{C}^{\mathrm{op}}$ the composite of $\alpha$ and
$\beta$ is taken in the other order, so covariance there reads as reversal
here. ⟨your step: draw Aluffi's picture — $A \to B \to C$ going to
$\mathcal{G}(A) \leftarrow \mathcal{G}(B) \leftarrow \mathcal{G}(C)$ — and say
why the composite still lands where it should.⟩
</details>
<details><summary>Strategy</summary>
Two sources, two notations, one definition. Getting (c) straight now is worth
the ten minutes; diagrammatic order is standard in the applied-category
literature this degree will draw on, and classical order is standard in
algebra.
</details>

---

## Problem 2 (easy — examples, and one that reverses)

(a) Explain what a *forgetful* functor is, and verify Aluffi's example: sending
a ring to its underlying abelian group is a covariant functor
$\mathsf{Ring} \to \mathsf{Ab}$. Say exactly which fact about ring
homomorphisms makes the morphism half work.
(b) Example 1.2: show that $R \mapsto R^*$, the group of units, is a covariant
functor $\mathsf{Ring} \to \mathsf{Grp}$.
(c) Example 1.4: show that $\operatorname{Spec}$ is *contravariant*. The
morphism half is $\varphi \mapsto \varphi^{-1}$ on prime ideals; say why taking
preimages reverses the arrows, and check the composition condition in the
reversed order.
(d) The Hom functors. Fix an object $X$ of $\mathsf{C}$. Show that
$A \mapsto \operatorname{Hom}_\mathsf{C}(X, A)$ is covariant and that
$A \mapsto \operatorname{Hom}_\mathsf{C}(A, X)$ is contravariant, in both cases
by saying what the functor does to a morphism $\alpha : A \to B$.
(e) Example 1.5: a *presheaf of sets* on a set $S$ is a contravariant functor
$\hat S \to \mathsf{Set}$, where $\hat S$ is cat-01's power-set category. Verify
Aluffi's prototypical example — $U \mapsto$ the set of functions $U \to Y$ for
a fixed $Y$, with inclusions going to restrictions — and say why restriction
makes it contravariant rather than covariant.

<details><summary>Hint</summary>
(d) Post-composition for the first; pre-composition for the second.
(e) An inclusion $U \subseteq V$ lets you restrict a function on $V$ to $U$,
not the other way round.
</details>
<details><summary>Partial</summary>
(d) For $\alpha : A \to B$, the covariant functor sends $\varphi \in
\operatorname{Hom}(X,A)$ to $\alpha\varphi \in \operatorname{Hom}(X,B)$ —
post-composition. The contravariant one sends $\psi \in \operatorname{Hom}(B,X)$
to $\psi\alpha \in \operatorname{Hom}(A,X)$ — pre-composition, which reverses.
⟨your step: check both preserve identities and composition, with the order
reversed in the second case.⟩
</details>

---

## Problem 3 (medium — Spivak's functors and instances)

(a) Example 3.36 draws three functors $\mathbf{2} \to \mathbf{3}$. Describe
each on objects and on morphisms. Then do Spivak's Exercise 3.37: find all the
remaining functors $\mathbf{2} \to \mathbf{3}$, and justify that your list is
complete.
(b) Example 3.38: there is *exactly one* functor from the free square category
to the commutative square category sending $A' \mapsto A$, …, $D' \mapsto D$.
Do Exercise 3.39 — say where each of the ten morphisms goes — and explain why
the action on objects determines everything here.
(c) Spivak then remarks that his examples so far "have been completely
determined by what they do on objects, but this is usually not the case". Give
a functor that is *not* determined by its action on objects, and say what
feature of the source category his examples had that yours lacks.
(d) State Definition 3.44: a $\mathcal{C}$-instance is a functor
$\mathcal{C} \to \mathbf{Set}$. Take Spivak's Beatles example and write out the
schema, then write out the instance as a functor: what is the image of each
object, and of each morphism?
(e) Spivak's summary is that "a database schema is a category, and an instance
on that schema — the data itself — is a set-valued functor. All the constraints,
or business rules, are ensured by the rules of functors, namely that functors
preserve composition." Give a constraint that functoriality enforces
automatically, and one that it does not.

<details><summary>Hint</summary>
(c) In $\mathbf{2}$ and in the square categories, how many morphisms are there
between any given pair of objects?
(e) Two paths in the schema with the same source and target that are declared
equal must give equal functions. What about a path being required to be
injective?
</details>
<details><summary>Partial</summary>
(c) In $\mathbf{2}$, $\mathbf{3}$ and the commutative square, each Hom-set has
at most one element, so once the objects are placed there is nothing left to
choose — the same phenomenon that made every morphism a monomorphism in
cat-01's Example 4.10. Take instead a functor between one-object categories,
that is, a group homomorphism $G \to H$: the object assignment is forced and
carries no information at all, while the morphism assignment is the whole
content.
(e) Functoriality enforces path equations declared in the schema. It does not
enforce injectivity, surjectivity, or any cardinality condition — nothing in
Definition 3.35 constrains the *sets* beyond the commutativity the schema
imposes.
</details>

---

## Problem 4 (medium — faithful, full, and equivalence)

(a) State Definitions 1.6 and 1.7: faithful, full, fully faithful, essentially
surjective, and equivalence of categories.
(b) Give a faithful functor that is not full, and a full functor that is not
faithful. Forgetful functors are a good source for the first.
(c) Why is "equivalence" defined as fully faithful plus essentially surjective,
rather than as "bijective on objects and on morphisms"? Say what the second,
stricter condition would be called, and give two categories that are equivalent
without being related by any such bijection.
(d) Work Example 1.8: the category whose objects are non-negative integers with
$\operatorname{Hom}(m,n)$ the $n \times m$ matrices over a field $k$ is
equivalent to the category of finite-dimensional $k$-vector spaces. Say what the
functor is, prove it is fully faithful, and say which classification theorem
supplies essential surjectivity.
(e) Aluffi says Example 1.8 "makes (more) precise the heuristic considerations
at the end of §VI.2.1" — the sense in which a finite-dimensional vector space
"is" $k^n$. Say what is *lost* by replacing the category of vector spaces with
the category of matrices, and what is gained, and why "equivalent" rather than
"isomorphic" is the right word for the relationship.

<details><summary>Hint</summary>
(c) A vector space has no canonical basis; the matrix category has one built in
by fiat.
(e) Count the objects on each side.
</details>
<details><summary>Partial</summary>
(d) Send $n$ to $k^n$ with its standard basis, and each $n \times m$ matrix to
the corresponding linear map $k^m \to k^n$. Fully faithful: linear maps
$k^m \to k^n$ correspond bijectively to $n \times m$ matrices once bases are
fixed. Essentially surjective: every finite-dimensional space is isomorphic to
some $k^n$, because vector spaces are classified by dimension. ⟨your step: say
where "isomorphic to", rather than "equal to", is doing the work.⟩
(e) The matrix category has one object per dimension; the vector space category
has a proper class of them. So no bijection on objects is possible, and yet the
categories carry the same information. That is precisely the gap "equivalent"
is designed to bridge.
</details>

---

## Problem 5 (hard — composition, and which composite is persistence)

(a) Prove that functors compose: if $F : \mathcal{C} \to \mathcal{D}$ and
$G : \mathcal{D} \to \mathcal{E}$ are functors then so is $G \circ F$. Check
both conditions.
(b) Spivak works a composite explicitly on p. 101: $F : \mathbf{Gr} \to
\mathrm{DDS}$ followed by an instance $I : \mathrm{DDS} \to \mathbf{Set}$,
giving $F\,;I : \mathbf{Gr} \to \mathbf{Set}$. Describe what the composite does
to objects and to morphisms, and say why the result is again an instance —
this time on $\mathbf{Gr}$.
(c) Now set up the persistence composite properly, using cat-01's Example 3.3.
Let $(P, \le)$ be a preorder regarded as a category. Say what a functor
$\mathcal{X} : P \to \mathbf{Top}$ is, concretely, and confirm that a nested
family of subspaces with inclusions is one.
(d) at1-10 formed the composite $H_n \circ \mathcal{X} : P \to \mathbf{Ab}$
before functors had been defined in this module. Redo it now with
Definition 1.1 in hand: verify both functor conditions for the composite, and
describe the result concretely — one abelian group per index, one homomorphism
per comparison.
(e) The reflection, and it turns on a distinction the mission strip does not
draw. The strip says: *homology is a functor; so is "sample the filtration at
level $t$"; persistence composes the two.* There are two different things that
"sample at level $t$" could name, and they are both functors:

  - the filtration itself, $\mathcal{X} : P \to \mathbf{Top}$, whose value at
    $t$ is $X_t$;
  - *evaluation at $t$*, the functor
    $\mathrm{ev}_t : \mathbf{Top}^P \to \mathbf{Top}$ from the category of all
    such filtrations, sending $\mathcal{X}$ to $X_t$.

  Compute both composites with $H_n$. Say which one is a persistence module and
  which one is a single abelian group, and hence which reading of the strip is
  the correct one. Then say what this shows about slogans of the form "A is a
  functor and B is a functor, so composing them gives C".

<details><summary>Hint</summary>
(e) Compose the domains and codomains first, before thinking about what the
functors do. One composite has domain $P$; the other has domain
$\mathbf{Top}^P$.
</details>
<details><summary>Partial</summary>
(a) $(G \circ F)(1_A) = G(F(1_A)) = G(1_{F(A)}) = 1_{G(F(A))}$, and
$(G \circ F)(\beta\alpha) = G(F(\beta)F(\alpha)) = G(F(\beta))G(F(\alpha))$.
Both conditions are used once each, in each factor.
(c) A functor $P \to \mathbf{Top}$ assigns a space $X_p$ to each $p$ and a
continuous map $X_p \to X_q$ to each relation $p \le q$, with the map for
$p \le p$ the identity and the map for $p \le r$ the composite of those for
$p \le q$ and $q \le r$. A nested family with inclusions satisfies both, since
composites of inclusions are inclusions. ⟨your step: note that antisymmetry is
never used, so $P$ may be a preorder — cat-01's Example 3.3, not a poset.⟩
</details>
<details><summary>Worked start</summary>
(e) Compose the types first.

$H_n \circ \mathcal{X}$ has domain $P$ and codomain $\mathbf{Ab}$. Its value at
$p$ is $H_n(X_p)$ and its value on $p \le q$ is the induced homomorphism. That
is a group for every index and a map for every comparison: **a persistence
module**.

$H_n \circ \mathrm{ev}_t$ has domain $\mathbf{Top}^P$ and codomain
$\mathbf{Ab}$. Its value at a filtration $\mathcal{X}$ is the single group
$H_n(X_t)$. That is **one abelian group per filtration** — the $t$-th slice,
with no comparisons in it at all.

⟨your step: both are legitimate functors, so the strip is not false; but only
one of them is persistence. Say which, and then state the general moral: naming
two functors does not determine their composite, because a composite is
determined by *which* two and in which order — the domains have to match up.
Check your moral against at1-10's version of the same point, and say whether
this unit strengthens it or merely repeats it.⟩
</details>
<details><summary>Strategy</summary>
(e) is the unit's payoff and it is a type-checking exercise before it is a
mathematical one. The habit worth forming: when a slogan composes two things,
write down the domain and codomain of each before believing the composite is
what you were told it is.
</details>
