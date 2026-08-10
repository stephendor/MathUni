# cat-06 — Adjunctions

**Module:** Category Theory · **Unit:** cat-06
**Sources:** Aluffi, *Algebra: Chapter 0* — §VIII.1.3 (pp. 492–493): the
informal introduction of adjoint functors as *natural* isomorphisms
$\operatorname{Hom}_\mathsf{C}(X, \mathcal{G}(Y)) \cong
\operatorname{Hom}_\mathsf{D}(\mathcal{F}(X), Y)$, the parenthetical that the
precise version needs a natural isomorphism of bifunctors
$\mathsf{C}^{\mathrm{op}} \times \mathsf{D} \to \mathsf{Set}$, Example 1.16 on
the free group functor as left adjoint to the forgetful functor with the remark
that free functors are "as a rule" left adjoints, and the observation that
properties of interesting functors translate into properties of harmless ones;
**Lemma 1.17**, that right-adjoint functors commute with limits, with Aluffi's
statement of the canonical isomorphism, his gloss that right adjoints are
therefore *continuous* and left adjoints *cocontinuous*, and his explicit
statement that he will not prove it "in gory detail" but will instead show that
such statements "boil down to suitable applications of the universal
properties" (p. 493).
Spivak, *Seven Sketches in Compositionality* — §3.4.2 (pp. 102–104):
the reduction of an adjunction between preorders to
$f(p) \le q$ iff $p \le g(q)$ and its rephrasing as an isomorphism of hom-sets;
Definition 3.70 of $L \dashv R$ with naturality in both variables and the
footnote spelling out the bifunctor square; the notation $L \dashv R$;
Example 3.71 identifying Galois connections with adjunctions between preorder
categories; Example 3.72 on currying with the exponential object $C^B$;
Exercise 3.73; and Example 3.74's five families of adjunctions — free
constructions, free preorders and categories, discrete things, codiscrete
things, and abelianisation. §1.4 (Ch. 1): Galois connections.

**Neither source proves Lemma 1.17.** Aluffi says so in the text: he sketches
it and declines the details. Problem 5 completes his sketch from his own
strategy; do not write "Aluffi proves".

Interleaves cat-04, whose natural transformations are what "natural" means
here, and cat-05, whose limits Lemma 1.17 is about.

Submit your written solutions via `/grade cat-06`.

---

## Problem 1 (easy — the definition, from preorders up)

(a) State the preorder version: monotone maps $f : P \to Q$ and
$g : Q \to P$ form a Galois connection when $f(p) \le q$ if and only if
$p \le g(q)$. Say why Spivak calls such a pair "almost inverses".
(b) Spivak rephrases this as an isomorphism of hom-sets
$Q(f(p), q) \cong P(p, g(q))$, noting that in a preorder a hom-set has one
element or none. Carry out the rephrasing carefully, and say why the
biconditional in (a) becomes an *isomorphism* rather than merely an implication.
(c) State Definition 3.70. Then state Aluffi's version, and confirm they agree
up to which functor is written on which side.
(d) Both authors insist the isomorphism be *natural*. Using cat-04's
Definition 1.15, say what naturality means here and in which variables, and
give Spivak's footnote 8 spelling out the commuting square.
(e) Say what would be lost if one asked only that the two hom-sets be in
bijection for each pair $(c, d)$, without naturality.

<details><summary>Hint</summary>
(b) A biconditional between two statements each of which is "this hom-set is
non-empty" says the two hom-sets are simultaneously empty or simultaneously
singletons.
(e) Bijection alone is a statement about cardinality.
</details>
<details><summary>Partial</summary>
(b) In a preorder, $Q(f(p), q)$ has one element if $f(p) \le q$ and none
otherwise, and similarly for $P(p, g(q))$. The biconditional says the two
conditions hold together, so the two hom-sets have the same size — and since
each has at most one element, same size means isomorphic. Naturality is
automatic here because any two functions between one-element sets agree.
⟨your step: say why that last remark means the preorder case cannot show you
what naturality is for.⟩
</details>
<details><summary>Strategy</summary>
The preorder case is the whole definition with all the difficulty removed,
which makes it a good on-ramp and a bad test: naturality is invisible there.
Keep track of what the general case adds.
</details>

---

## Problem 2 (easy — examples)

(a) Example 3.71: show that Galois connections between preorders and
adjunctions between the corresponding categories are the same thing.
(b) Example 3.72, currying. Define the exponential object $C^B$ in **Set** and
establish the natural isomorphism
$\mathbf{Set}(A \times B, C) \cong \mathbf{Set}(A, C^B)$. Say which functor is
the left adjoint and which the right.
(c) Do Spivak's Exercise 3.73: both functors were only described on objects.
Say what $- \times B$ and $(-)^B$ do to a morphism $f : X \to Y$; then curry
$+ : \mathbb{N} \times \mathbb{N} \to \mathbb{N}$ and compute $p(3)$.
(d) Aluffi's Example 1.16: verify that the free group functor
$F : \mathsf{Set} \to \mathsf{Grp}$ is left adjoint to the forgetful functor,
by writing the bijection $\operatorname{Hom}_{\mathsf{Set}}(A, S(G)) \cong
\operatorname{Hom}_{\mathsf{Grp}}(F(A), G)$ and checking naturality in $A$.
(e) Spivak's Example 3.74 lists five families: free constructions, free
preorders and categories, discrete things, codiscrete things, and
abelianisation. For each, say which of the pair is the left adjoint. Then note
how Spivak introduces the list — "If you know some abstract algebra or
topology, here are some other examples" — and say what that tells you about
whether these are established or offered for recognition.

<details><summary>Hint</summary>
(c) $p(3)$ should be a function $\mathbb{N} \to \mathbb{N}$, not a number.
(e) Count how many of the five he verifies.
</details>
<details><summary>Partial</summary>
(c) $-\times B$ sends $f : X \to Y$ to $f \times \mathrm{id}_B$; $(-)^B$ sends
$f$ to post-composition, $\varphi \mapsto f \circ \varphi$. Currying $+$ gives
$p : \mathbb{N} \to \mathbb{N}^\mathbb{N}$ with $p(3)$ the function
$n \mapsto 3 + n$.
(e) All five are stated and none is verified; Spivak frames them as things the
reader may already recognise. ⟨your step: say which of the five you could
actually prove from this unit's sources, and which you would be taking on
recognition.⟩
</details>

---

## Problem 3 (medium — mates and the unit)

(a) Define the *mate* of a morphism, following Definition 3.70: given
$f : c \to R(d)$, its mate is $g := \alpha_{c,d}(f) : L(c) \to d$, and
conversely. Show the two operations are mutually inverse.
(b) Take $c$ and put $d = L(c)$. Apply the isomorphism backwards to
$\mathrm{id}_{L(c)}$ and say what you get: a morphism
$\eta_c : c \to R(L(c))$. This is the *unit* of the adjunction. Do the dual
construction to get $\varepsilon_d : L(R(d)) \to d$.
(c) Show $\eta$ is a natural transformation from the identity functor on
$\mathcal{C}$ to $R \circ L$. Say which part of Definition 3.70 you are using
and where.
(d) In the free-group adjunction, identify $\eta_A : A \to S(F(A))$ concretely.
What familiar map is it?
(e) Show that the mate of any $f : c \to R(d)$ can be recovered from $\eta$ as
$L(f)$ followed by $\varepsilon_d$ — or state honestly if you cannot get there
from this unit's sources, and say what is missing.

<details><summary>Hint</summary>
(b) Every hom-set contains an identity when its two arguments agree, and that
is the same trick cat-04's Yoneda proof used.
(d) The generators of a free group sit inside it.
</details>
<details><summary>Partial</summary>
(b) With $d = L(c)$ the isomorphism reads $\mathcal{C}(c, R(L(c))) \cong
\mathcal{D}(L(c), L(c))$. The right side contains $\mathrm{id}_{L(c)}$; pulling
it back gives $\eta_c : c \to R(L(c))$.
(d) $\eta_A$ sends each element of $A$ to itself viewed as a one-letter word in
$F(A)$ — the inclusion of the generating set. ⟨your step: say why the universal
property of the free group is exactly the statement that $\eta_A$ is initial
among maps from $A$ into the underlying set of a group.⟩
</details>

---

## Problem 4 (medium — why adjunctions are worth finding)

(a) Aluffi writes that a functor having an adjoint "will endow that functor
with convenient features", and that "properties of the interesting ones may be
translated into properties of the harmless ones". Explain the strategy in your
own words.
(b) State Lemma 1.17 and its dual: right adjoints commute with limits, left
adjoints with colimits. Write out the canonical isomorphism
$\mathcal{G}(\varprojlim \mathcal{A}) \cong \varprojlim(\mathcal{G} \circ
\mathcal{A})$ and say what "if the limits exist" is guarding against.
(c) Aluffi glosses the lemma by saying right adjoints are *continuous* and left
adjoints *cocontinuous*, and adds that "every good calculus student should
readily understand" the analogy. Spell the analogy out, and then say where it
breaks down.
(d) Use Lemma 1.17 to deduce something concrete: the forgetful functor
$\mathsf{Grp} \to \mathsf{Set}$ is a right adjoint, so it preserves products.
Check the conclusion directly for two groups, and say which is more work.
(e) Now the negative use. Aluffi's strategy also lets you show a functor has
*no* left adjoint, by finding a limit it fails to preserve. Set up such an
argument in outline, and say what you would need to exhibit.

<details><summary>Hint</summary>
(c) A continuous function commutes with limits of sequences. Ask what plays the
role of the sequence and what plays the role of the function.
(e) Contrapositive of Lemma 1.17.
</details>
<details><summary>Partial</summary>
(d) The underlying set of $G \times H$ is the product of the underlying sets,
with the projections; that is the statement that the forgetful functor
preserves products, and Lemma 1.17 gives it for free once you know the functor
is a right adjoint. Directly, one checks the universal property in
$\mathsf{Grp}$ and then again in $\mathsf{Set}$. ⟨your step: say which
verification you would rather do for an infinite family, and why that is
Aluffi's point.⟩
</details>

---

## Problem 5 (hard — completing Aluffi's sketch, and auditing the strip)

Aluffi states Lemma 1.17 and says explicitly that he "will not prove it in gory
detail", offering instead to convince the reader that such statements "just
boil down to suitable applications of the universal properties defining the
various concepts". Problem 5 completes his sketch from his own strategy.

(a) Set up. Let $\mathcal{G} : \mathsf{D} \to \mathsf{C}$ be right adjoint to
$\mathcal{F}$, and $\mathcal{A} : \mathsf{I} \to \mathsf{D}$ a functor with a
limit. Write down the cone exhibiting $\varprojlim \mathcal{A}$, following
cat-05's Definition 3.92.
(b) Apply $\mathcal{G}$. Show that $\mathcal{G}(\varprojlim \mathcal{A})$ with
the images of the projections is a cone over $\mathcal{G} \circ \mathcal{A}$.
Which functor property is doing this?
(c) Now the substance: show that this cone is *terminal*. Given any cone
$(M, \mu_*)$ over $\mathcal{G} \circ \mathcal{A}$ in $\mathsf{C}$, use the
adjunction to transport it to a cone over $\mathcal{A}$ in $\mathsf{D}$, apply
the universal property of $\varprojlim \mathcal{A}$ there, and transport back.
Say at each step which of the two universal properties — the limit's or the
adjunction's — you are using.
(d) Where does *naturality* of the adjunction isomorphism enter? It is needed
exactly once, and skipping it is the standard way this proof goes wrong. Say
where, and what would fail without it.
(e) The reflection, in three separate parts. The mission strip says
"Adjunctions organise the constructions (free complex, geometric realisation)
that turn data into topology."

  First: what does this unit establish about *free* constructions? Be precise
  about the difference between Aluffi's Example 1.16, which he verifies, and
  Spivak's Example 3.74, which he lists.

  Second: neither source mentions simplicial complexes, geometric realisation,
  or data. Say what would have to be supplied to make the strip's parenthetical
  a theorem rather than a pointer, and which module owes it.

  Third: the strip says adjunctions *organise* these constructions. Using
  Lemma 1.17 and Problem 4, say what organisational work an adjunction actually
  does — what you get to conclude about a construction once you know it is a
  left adjoint — and state that as a general claim you could defend from this
  unit's pages.

<details><summary>Hint</summary>
(c) A cone over $\mathcal{G} \circ \mathcal{A}$ has components
$\mu_I : M \to \mathcal{G}(\mathcal{A}(I))$; the adjunction turns each into a
morphism $\mathcal{F}(M) \to \mathcal{A}(I)$.
(d) You transported a whole *cone*, not just its components — so the cone
condition has to survive the transport.
</details>
<details><summary>Partial</summary>
(b) Functoriality: applying $\mathcal{G}$ to the commuting triangles of the
cone gives commuting triangles, because functors preserve composites. That is
cat-03's observation that commutative diagrams go to commutative diagrams.
(d) The transported components $\mathcal{F}(M) \to \mathcal{A}(I)$ must
themselves form a cone, that is, satisfy $\mu'_J = \mathcal{A}(\alpha) \circ
\mu'_I$. That the mates of a compatible family are compatible is precisely the
naturality of $\alpha_{c,d}$ in the second variable. ⟨your step: write out the
naturality square for $\alpha$ at the morphism $\mathcal{A}(\alpha)$ and read
the cone condition off it.⟩
</details>
<details><summary>Worked start</summary>
(e) *First question.* Aluffi verifies one instance: Example 1.16 establishes
$\operatorname{Hom}_{\mathsf{Set}}(A, S(G)) \cong
\operatorname{Hom}_{\mathsf{Grp}}(F(A), G)$ for free groups, and adds that "the
free functor is, as a rule, left-adjoint to the forgetful functor" — a remark,
not a theorem, and the words "as a rule" are his. Spivak's Example 3.74 lists
five families, introduces them with "If you know some abstract algebra or
topology, here are some other examples", and verifies none. So: one worked
instance and two informal generalisations. ⟨your step: complete the audit by
saying which of Spivak's five you could prove from these pages.⟩
</details>
<details><summary>Strategy</summary>
Part (c) is the only real proof in the unit and it is worth the time; part (d)
is where it is usually got wrong. Part (e)'s third question is the one that
matters for the degree — "adjunctions organise X" is a claim you should be able
to cash out as "knowing X is a left adjoint tells you Y", and Lemma 1.17 is the
Y this unit can actually supply.
</details>
