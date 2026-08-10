# cat-01 — Categories and morphisms

**Module:** Category Theory · **Unit:** cat-01
**Sources:** Aluffi, *Algebra: Chapter 0* — §I.3 "Categories" (pp. 18–26):
the class-versus-set difficulty and the term *small* (p. 18); Definition 3.1
with the identity, composition, associativity, unit and disjointness clauses,
endomorphisms, $\operatorname{End}_\mathsf{C}(A)$, arrow notation and
commutative diagrams (p. 19); §3.2 Examples, the remark that the morphisms are
the important constituents, Example 3.2 (**Set**) and Example 3.3 (a set with
a reflexive transitive relation) (pp. 20–21); Example 3.4 (the power set
ordered by inclusion) and Example 3.5 (slice categories) (pp. 22–23);
Examples 3.6–3.10 (pp. 24–25).
§I.4 "Morphisms" (pp. 27–30): the opening remark that objects of a general
category have no elements; Definition 4.1 of an isomorphism (p. 27);
Proposition 4.2 that the inverse is unique, Proposition 4.3, Examples 4.4 and
4.5 (p. 28); Example 4.6 on groupoids, $\operatorname{Aut}_\mathsf{C}(A)$ as a
group, §4.2 with Definition 4.7 (monomorphism), Definition 4.8 (epimorphism)
and Example 4.9 (p. 29); Example 4.10 and the paragraph on why mono plus epi
does not give iso outside **Set** (p. 30).

**Functors are not in this unit's sources.** Aluffi says so in a footnote on
p. 18: the first formal encounter with functors is Chapter VIII, which is
cat-03's resource. Nothing here may use one.

Interleaves at1-10, which met categories from Hatcher's side and used the
poset-as-category example; Problem 5 reconciles the two treatments, which
differ in a way that matters.

Submit your written solutions via `/grade cat-01`.

---

## Problem 1 (easy — the definition, clause by clause)

(a) State Definition 3.1 in full: the class of objects, the sets
$\operatorname{Hom}_\mathsf{C}(A,B)$, and all four conditions on morphisms.
(b) Aluffi writes *class* rather than *set* for the objects, and explains why.
Give his reason, name the paradox he cites, and say what the word *small*
means for a category.
(c) One clause is easy to skip: the sets $\operatorname{Hom}_\mathsf{C}(A,B)$
and $\operatorname{Hom}_\mathsf{C}(C,D)$ must be *disjoint* unless $A = C$ and
$B = D$. Say what this rules out, and why it "holds for ordinary
set-functions". Then say what would go wrong in the definition of composition
if it were dropped.
(d) Define $\operatorname{End}_\mathsf{C}(A)$ and show that composition is an
operation on it. Why is it a *pointed* set?
(e) Verify Example 3.2: sets as objects and set-functions as morphisms form a
category. Check every clause, including disjointness.

<details><summary>Hint</summary>
(c) If a morphism did not remember its source and target, what would
$gf$ even mean?
(d) "Pointed" means a set with a distinguished element. Which axiom supplies
one?
</details>
<details><summary>Partial</summary>
(c) Disjointness makes the source and target part of the datum of a morphism,
so that a morphism knows where it comes from and where it goes. For
set-functions this is automatic on Aluffi's convention: two functions that are
the same function necessarily have the same source and target. Without it, a
single $f$ could lie in two different Hom-sets and the composite $gf$ would not
be determined by $f$ and $g$ alone. ⟨your step: give a concrete pair of
"functions" that would become ambiguous — the inclusion
$\mathbb{Z} \hookrightarrow \mathbb{Z}$ and the identity are a good place to
start.⟩
</details>
<details><summary>Strategy</summary>
Aluffi remarks that 90% of the definition goes into the properties of
morphisms, and that the morphisms *are* the important constituents. Read the
definition with that in mind: objects are almost placeholders, and every axiom
is about arrows.
</details>

---

## Problem 2 (easy — categories that are not made of sets and functions)

(a) Example 3.3. Let $S$ be a set with a relation $\sim$ that is reflexive and
transitive. Build the category: objects, Hom-sets, identities, composition.
Verify every clause of Definition 3.1.
(b) Exactly which of the two properties of $\sim$ gives identities, and which
gives composition? Aluffi asks for one of these to be checked carefully in
Exercise 3.3; do it.
(c) Note what Aluffi does *not* assume: antisymmetry. Take $S = \mathbb{Z}$
with $\le$ and then take a relation that is reflexive and transitive but not
antisymmetric, and describe the difference between the two resulting
categories. What can happen in the second that cannot happen in the first?
(d) Exercise 3.4 asks whether the same construction works with $<$ on
$\mathbb{Z}$. Answer it, and say which single clause fails.
(e) Example 3.4 builds a category $\hat S$ from the power set of $S$ ordered by
inclusion. Verify the axioms, and then explain Aluffi's footnote: in what sense
is Example 3.4 an instance of Example 3.3 (his Exercise 3.5)?

<details><summary>Hint</summary>
(b) One of them produces a morphism $a \to a$; the other produces a morphism
$a \to c$ from morphisms $a \to b$ and $b \to c$.
(d) $<$ is transitive. Is it reflexive?
</details>
<details><summary>Partial</summary>
(b) Reflexivity gives $a \sim a$, hence a morphism $1_a = (a,a) \in
\operatorname{Hom}(a,a)$; transitivity gives $a \sim b$ and $b \sim c$ implies
$a \sim c$, which is composition. ⟨your step: Exercise 3.3 asks you to show
$1_a$ really is an identity for composition. Since there is at most one
morphism in each Hom-set, that verification is shorter than you expect — say
why.⟩
(d) It fails at reflexivity: $a < a$ is false, so there is no morphism
$a \to a$ and no candidate for $1_a$. Transitivity and associativity are fine.
</details>
<details><summary>Strategy</summary>
These are the examples that break the habit of thinking "objects are sets,
morphisms are functions". In Example 3.3 the morphisms are *pairs* — bare
tokens recording that a relation holds — and nothing is applied to anything.
Everything in §4 will be tested against this example.
</details>

---

## Problem 3 (medium — slice categories)

(a) Example 3.5. Fix a category $\mathsf{C}$ and an object $A$. The objects of
$\mathsf{C}_A$ are the morphisms $f : Z \to A$ for all objects $Z$. Aluffi
invites you to work out the morphisms yourself before reading on. Do that:
propose a definition, then compare with his.
(b) Having fixed the morphisms, define composition and identities in
$\mathsf{C}_A$ and check the axioms.
(c) Example 3.6 runs the construction concretely: $\mathsf{C}$ is the category
of Example 3.3 for $S = \mathbb{Z}$ and $\sim$ equal to $\le$, and $A = 3$.
Describe $\operatorname{Obj}(\mathsf{C}_3)$ explicitly, and describe when there
is a morphism between two of its objects.
(d) Example 3.7 flips the arrows to get *coslice* categories, and Aluffi leaves
the details as Exercise 3.7. Supply them: objects, morphisms, composition,
identities.
(e) Example 3.8 takes $\mathsf{C} = \mathsf{Set}$ and $A$ a singleton
$\{*\}$, calling the result $\mathsf{Set}^*$. Say concretely what an object and
a morphism of $\mathsf{Set}^*$ are, and what familiar notion this category
captures.

<details><summary>Hint</summary>
(a) An object is an arrow into $A$. A morphism between two such arrows should
be an arrow between their sources that is compatible with them — which means
one triangle commutes.
(e) An arrow from a singleton into $X$ picks out an element of $X$.
</details>
<details><summary>Partial</summary>
(a) A morphism from $f : Z \to A$ to $g : W \to A$ is a morphism
$\sigma : Z \to W$ in $\mathsf{C}$ with $g\sigma = f$ — the triangle over $A$
commutes. Composition is composition in $\mathsf{C}$: if $g\sigma = f$ and
$h\tau = g$ then $h(\tau\sigma) = (h\tau)\sigma = g\sigma = f$. The identity on
$f$ is $1_Z$. ⟨your step: check the remaining axioms, and check that
disjointness of Hom-sets is inherited.⟩
(e) An object of $\mathsf{Set}^*$ is a set with a chosen element — a *pointed
set* — and a morphism is a function preserving the chosen element.
</details>

---

## Problem 4 (medium — isomorphisms)

(a) State Definition 4.1. Then prove Proposition 4.2, that the inverse of an
isomorphism is unique, by Aluffi's one-line computation. Identify which axiom
each of the five equalities uses.
(b) Aluffi remarks that the argument proves more than stated: if $f$ has a
left-inverse $g_1$ and a right-inverse $g_2$, then $f$ is an isomorphism and
$g_1 = g_2$. Extract that stronger statement from the same computation.
(c) Prove Proposition 4.3, all three parts. For the third, note that inversion
*reverses* the order: $(gf)^{-1} = f^{-1}g^{-1}$. Say why that is forced rather
than a convention.
(d) Deduce that "isomorphic" is an equivalence relation on the objects of any
category, saying which part of Proposition 4.3 gives reflexivity, which
symmetry, and which transitivity.
(e) Prove that $\operatorname{Aut}_\mathsf{C}(A)$ is a group, for every object
$A$ of every category $\mathsf{C}$, checking the four bullet points Aluffi
lists. Then compute $\operatorname{Aut}_\mathsf{C}(a)$ for an object $a$ of the
category of Example 3.3, and $\operatorname{Aut}_{\mathsf{Set}}(X)$ for a
finite set $X$.

<details><summary>Hint</summary>
(c) Try to compose $g^{-1}f^{-1}$ with $gf$ and watch it fail to cancel.
(e) One of the two computations gives the trivial group; the other gives a
group you have met in aa.
</details>
<details><summary>Partial</summary>
(a) $g_1 = g_1 1_B = g_1(fg_2) = (g_1f)g_2 = 1_A g_2 = g_2$. The five steps
use, in order: the unit axiom; that $g_2$ is a right-inverse; associativity;
that $g_1$ is a left-inverse; the unit axiom again.
(e) $\operatorname{Aut}_\mathsf{C}(a)$ in Example 3.3 is trivial, since the
only morphism $a \to a$ is $1_a$. $\operatorname{Aut}_{\mathsf{Set}}(X)$ for
$|X| = n$ is the symmetric group $S_n$, since isomorphisms in $\mathsf{Set}$
are bijections (Example 4.4). ⟨your step: say what it means that *every*
object of *every* category has an automorphism group — in particular, where
group theory comes from on this account.⟩
</details>
<details><summary>Strategy</summary>
Every proof in this problem is pure arrow-pushing: no element is named
anywhere, because in a general category there are none to name. That is the
methodological content of §4, and Aluffi says so in its first paragraph.
</details>

---

## Problem 5 (hard — mono, epi, and the failure you should expect)

(a) State Definitions 4.7 and 4.8. Explain why they are phrased as
cancellation properties rather than in terms of elements, quoting Aluffi's
reason.
(b) Example 4.9: in $\mathsf{Set}$, monomorphisms are exactly the injections
and epimorphisms exactly the surjections. Prove one of the two directions of
each.
(c) Example 4.10. In the categories of Example 3.3, show that *every* morphism
is both a monomorphism and an epimorphism. The proof is one sentence; give it,
and say precisely which feature of those categories makes the conditions
vacuous.
(d) Now combine (c) with Example 4.5. In the category from $\le$ on
$\mathbb{Z}$, every morphism is mono and epi, while the only isomorphisms are
the identities. Conclude that "mono and epi implies iso" is *false* in general.
Then state carefully what Aluffi says about where it does hold — name the
category where it fails that you might have expected to behave, and name the
class of categories where it does hold, together with the caution he attaches
to that class.
(e) Finally, reconcile this unit with at1-10. There, following Hatcher, a
*partially ordered* set was made into a category. Here Aluffi requires only
reflexivity and transitivity — a *preorder*. Say what antisymmetry adds, in
terms of the categorical notions of this unit rather than in terms of the
order; and then say which of the two treatments is the more general, and
whether anything in at1-10's argument actually used antisymmetry.

<details><summary>Hint</summary>
(c) How many morphisms are there between any two objects?
(e) Answer in terms of isomorphism, not in terms of $\le$. Example 4.5 is the
model for the argument.
</details>
<details><summary>Partial</summary>
(c) There is at most one morphism between any two objects, so if
$f\alpha' = f\alpha''$ with $\alpha', \alpha'' : Z \to A$, then $\alpha'$ and
$\alpha''$ are both elements of a Hom-set with at most one element and are
therefore equal. The condition is satisfied vacuously — nothing is being
proved about $f$ at all. The same argument, with the arrows reversed, gives
epi.
(e) Antisymmetry says: if there are morphisms $a \to b$ and $b \to a$, then
$a = b$. Categorically, since any such pair composes to a morphism $a \to a$,
which must be $1_a$, antisymmetry is exactly the statement that *no two
distinct objects are isomorphic*. ⟨your step: so which treatment is more
general, and did at1-10's derivation of the persistence composite use
antisymmetry anywhere?⟩
</details>
<details><summary>Worked start</summary>
(d) In the category $\mathsf{C}$ from $\le$ on $\mathbb{Z}$: by (c) every
morphism is both a monomorphism and an epimorphism. By Example 4.5 an
isomorphism $f : a \to b$ requires a morphism $g : b \to a$ as well, so
$a \le b$ and $b \le a$, so $a = b$; and the only morphism $a \to a$ is $1_a$.
So the isomorphisms are exactly the identities, while the morphisms that are
both mono and epi are *all* of them. Since $\mathsf{C}$ has non-identity
morphisms — $2 \to 5$, for one — the implication fails.

⟨your step: complete the answer from Aluffi's paragraph following Example 4.10.
He names one category where you might have expected the implication to hold
and where it does not, one class of categories where it does, one theorem
number for that, and one warning about whether $\mathsf{Set}$ belongs to that
class. All four are wanted.⟩
</details>
<details><summary>Strategy</summary>
(d) and (e) are the point of the unit. The mono/epi definitions are built to
generalise injective and surjective, and in $\mathsf{Set}$ they do so exactly —
which is precisely what makes it tempting to carry the *rest* of one's
set-theoretic intuition across. Aluffi's Example 4.10 is a two-line
counterexample to the most natural of those carried-over beliefs. Expect to
lose others later.
</details>
