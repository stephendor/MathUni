# cat-05 — Limits and colimits

**Module:** Category Theory · **Unit:** cat-05
**Sources:** Spivak, *Seven Sketches in Compositionality* — §3.5 "Bonus: An
introduction to limits and colimits" (pp. 107–113): the opening question about
what products of sets, $\Pi_!$-operations and meets in a preorder have in
common (p. 107); §3.5.1, Definition 3.79 of a terminal object with
Example 3.80, Exercises 3.81–3.83, Proposition 3.84 that all terminal objects
are isomorphic, and Remark 3.85 on "the" versus "a" limit (p. 108);
Definition 3.86 of a product with its universal property (pp. 108–109);
§3.5.2, Definition 3.92 of a cone over a diagram, the category
$\mathbf{Cone}(D)$, and the limit as its terminal object, with Examples 3.93
and 3.94 identifying terminal objects and products as limits over the empty and
two-object discrete indexing categories (p. 111); §3.5.3, Example 3.99 on
pullbacks (p. 112); Remark 3.100 distinguishing two uses of that word (p. 113);
Definition 3.102, that a cocone in $\mathcal{C}$ is a cone in
$\mathcal{C}^{\mathrm{op}}$, with Spivak's remark that this is "like a
compressed file" and will be unpacked in Chapter 6 (p. 114).
Aluffi, *Algebra: Chapter 0* — §I.5 (pp. 31–38): Proposition 5.4, §5.3 on
quotients with Claim 5.5, §5.4 products, and §5.5 coproducts with
Proposition 5.6 and the remark that the coproduct in the $\le$ category is
$\max$.

**A source limitation worth knowing before you start.** Spivak gives limits in
full and then defines colimits in a single line by dualisation, saying the
definition is "completely useless for working with" until unpacked, and
deferring the unpacking to Chapter 6 — which is not in this unit's resources.
The concrete colimits in this unit therefore come from Aluffi §I.5: coproducts
and quotients, both worked explicitly there.

Interleaves cat-02, whose products and coproducts turn out to be the two
smallest cases, and cat-03, whose functors are what a diagram now is.

Submit your written solutions via `/grade cat-05`.

---

## Problem 1 (easy — terminal objects, again and better)

(a) State Spivak's Definition 3.79 and Aluffi's Definition 5.1. Confirm that
Spivak's *terminal* is Aluffi's *final*, and note that Aluffi warned against the
unqualified word.
(b) Prove Proposition 3.84, that all terminal objects in a category are
isomorphic, by Spivak's argument. Compare it line by line with Aluffi's proof
of Proposition 5.4 from cat-02 — they are the same argument; say whether either
adds anything the other omits.
(c) Remark 3.85 says terminal objects are unique up to *unique* isomorphism,
and that "to a category theorist, this is very nearly the same thing as saying
'all terminal objects are equal'". Say what the word *nearly* is protecting
against, and connect this to cat-02's Self-check 5 about $\emptyset$ and the
singletons in **Set**.
(d) Do Exercise 3.81: for a preorder $(P, \le)$ and the corresponding category
$\mathcal{P}$, show $z$ is terminal in $\mathcal{P}$ if and only if $z$ is a top
element of $P$.
(e) Do Exercise 3.83: find a category with no terminal object. cat-01's
Example 3.3 offers one; say which and why.

<details><summary>Hint</summary>
(b) Both proofs compose the two unique morphisms and use that the composite must
be the identity.
(e) Aluffi's Example 5.2 answers this.
</details>
<details><summary>Partial</summary>
(b) Spivak: $Z, Z'$ terminal give unique $a : Z \to Z'$ and $b : Z' \to Z$; the
composite $a\,;b : Z \to Z$ must be unique, and $\mathrm{id}_Z$ is such a map,
so $a\,;b = \mathrm{id}_Z$; symmetrically $b\,;a = \mathrm{id}_{Z'}$. Aluffi's
Proposition 5.4 is the same argument for initial objects, and adds the clause
that the isomorphism is *uniquely determined*, which Spivak states separately in
Remark 3.85 rather than inside the proposition.
</details>

---

## Problem 2 (easy — products as limits)

(a) State Definition 3.86 and check it against cat-02's statement of the product
universal property from Aluffi §5.4. Note the notation $\langle f, g\rangle$
for the unique morphism.
(b) Prove that a product of two sets, with its projections, satisfies
Definition 3.86.
(c) Spivak opens §3.5 by asking what products of sets, $\Pi_!$-operations on
database instances, and meets in a preorder have in common. Answer for the
first and third: show that the meet of two elements in a preorder is their
product in the corresponding category, and check it against Aluffi's
computation that the product in the $\le$ category on $\mathbb{Z}$ is
$\min(a,b)$.
(d) Example 3.94 says products are limits over the two-object discrete
indexing category. Say what a functor from that category is, and confirm that a
cone over it is exactly a pair of morphisms with a common source.
(e) Example 3.93 says terminal objects are limits over the *empty* indexing
category. Unwind that: what is a cone over the empty diagram, and why does the
terminal condition come out right?

<details><summary>Hint</summary>
(e) A cone over the empty diagram has an object and no morphisms, and the cone
condition is vacuous.
</details>
<details><summary>Partial</summary>
(e) A functor $\emptyset \to \mathcal{C}$ carries no data. A cone over it is
just an object $C$, with no component morphisms and no conditions. So
$\mathbf{Cone}(D)$ has one object for each object of $\mathcal{C}$ and one
morphism for each morphism, and its terminal object is a terminal object of
$\mathcal{C}$. ⟨your step: check that morphisms of cones reduce to morphisms of
$\mathcal{C}$ here, so that $\mathbf{Cone}(D) \cong \mathcal{C}$.⟩
</details>

---

## Problem 3 (medium — cones and the general definition)

(a) State Definition 3.92 in full: a cone $(C, c_*)$ over a diagram
$D : \mathcal{J} \to \mathcal{C}$, the cone condition, morphisms of cones, and
the category $\mathbf{Cone}(D)$. Then state the definition of $\lim(D)$.
(b) Verify that $\mathbf{Cone}(D)$ is a category: identities, composition, and
the axioms of cat-01's Definition 3.1.
(c) The definition of $\lim(D)$ is "the terminal object of $\mathbf{Cone}(D)$".
Say why that single sentence subsumes both halves of the usual formulation —
existence of a comparison morphism, and its uniqueness.
(d) Spivak notes that a diagram is a functor $D : \mathcal{J} \to \mathcal{C}$
(his Definition 3.51 from cat-04). Say what the *indexing category* contributes,
and give three different indexing categories with the three different notions of
limit they produce.
(e) Example 3.99: for $\mathcal{J}$ the cospan $\bullet \to \bullet \leftarrow
\bullet$, the limit is called a *pullback*, written $X \times_A Y$. Describe it
in **Set** using Spivak's account, and then say what the pullback is when $X$
and $Y$ are subsets of $A$ and both maps are inclusions.

<details><summary>Hint</summary>
(c) A terminal object receives exactly one morphism from every object. Read
"exactly one" as "at least one, and at most one".
(e) The pullback selects pairs that agree in $A$.
</details>
<details><summary>Partial</summary>
(c) Terminality says: for every cone $(M, \mu_*)$ there is exactly one morphism
of cones $(M, \mu_*) \to \lim(D)$. "At least one" is the existence of the
comparison morphism; "at most one" is its uniqueness; and being a morphism *of
cones* is exactly the requirement that all the triangles commute. The one
sentence carries all three.
(e) In **Set**, the pullback of $X \xrightarrow{f} A \xleftarrow{g} Y$ is
$\{(x,y) \in X \times Y : f(x) = g(y)\}$. If $X, Y \subseteq A$ and both maps
are inclusions, the condition $f(x) = g(y)$ says $x = y$, so the pullback is
$\{(x,x) : x \in X \cap Y\}$ — a set of pairs, hence canonically isomorphic to
$X \cap Y$ rather than equal to it. ⟨your step: exhibit the isomorphism, say
which of the two projections is which, and say what the universal property then
asserts about intersections.⟩
</details>

---

## Problem 4 (medium — colimits, and where the sources part)

(a) State Definition 3.102: a cocone in $\mathcal{C}$ is a cone in
$\mathcal{C}^{\mathrm{op}}$. Unpack it into a direct statement: what data, what
condition, and in which direction do the morphisms run?
(b) Define the colimit as the *initial* object of the category of cocones, and
say why "initial" rather than "terminal".
(c) Spivak calls Definition 3.102 "like a compressed file: useful for
transmitting quickly, but completely useless for working with, unless you can
successfully unpack it", and defers the unpacking to his Chapter 6. Do the
unpacking he declines to do, for the case where $\mathcal{J}$ is the two-object
discrete category, and check that you recover cat-02's coproduct.
(d) Now use Aluffi, who does work colimits concretely in §I.5. Show that the
disjoint union is the coproduct in **Set** (his Proposition 5.6), and that the
coproduct in the $\le$ category on $\mathbb{Z}$ is $\max$. Say which indexing
category each of these is a colimit over.
(e) Aluffi's §5.3 treats the quotient $A/\!\sim$ as an *initial* object of a
category of pairs $(\varphi, Z)$. Say why that makes it a colimit-flavoured
construction rather than a limit-flavoured one, and identify the diagram it is
a colimit of — being honest about whether the sources let you name that diagram
precisely.

<details><summary>Hint</summary>
(b) Initial in the cocone category is terminal in its opposite, and the
opposite of the cocone category is a cone category.
(e) The equivalence relation is generated by pairs; think about a diagram with
two parallel arrows.
</details>
<details><summary>Partial</summary>
(a) A cocone under $D : \mathcal{J} \to \mathcal{C}$ consists of an object $C$
and, for each $j$, a morphism $c_j : D(j) \to C$ — running *into* $C$ rather
than out of it — such that for each $f : j \to k$ we have $c_j = D(f)\,; c_k$.
(e) It is initial rather than final, and initiality is the colimit side. The
diagram it is a colimit of is a *coequalizer*: two parallel arrows from a set of
related pairs into $A$. ⟨your step: Aluffi does not use the word coequalizer in
§I.5, and Spivak does not construct one in §3.5 — so say plainly how far the
sources take you and where the identification is your own.⟩
</details>

---

## Problem 5 (hard — one idea from both sides)

(a) Prove that every limit is a terminal object and every colimit an initial
object, in the appropriate category, and that consequently each is unique up to
a unique isomorphism. Cite Proposition 3.84 or Proposition 5.4 as appropriate.
(b) Show that if $\mathcal{C}$ has a limit for a diagram $D$, then
$\mathcal{C}^{\mathrm{op}}$ has a colimit for the corresponding diagram, and
conversely. This is the precise content of "dual".
(c) Assemble the table. For each of the following indexing categories, name the
limit and the colimit: the empty category; the two-object discrete category;
the cospan (and its opposite, the span); a preorder. Check each entry against
either Spivak or Aluffi and say which.
(d) In the $\le$ category on $\mathbb{Z}$, the product is $\min$ and the
coproduct is $\max$. Extend this: what are the limit and colimit over an
arbitrary diagram in a preorder category, when they exist? Say what the answer
is in order-theoretic language, and why the general definition collapses to it.
(e) The reflection, in three separate parts. The mission strip says quotient and
gluing moves from la, aa and top "are all colimits — dual to the limits behind
products and intersections; one categorical idea seen from both sides."

  First: which part of that is *established* by this unit's sources? Be
  specific about what Spivak proves, what Aluffi proves, and what neither does.

  Second: "dual" is a precise word here. State what it means, using (b), and
  say whether duality guarantees that a category with all limits also has all
  colimits.

  Third: the strip's word *all*. Pick one construction from each of la, aa and
  top that you believe is a colimit, and for each say whether you can exhibit
  the indexing category and the diagram from this unit's sources, or whether
  you are relying on recognition. Report honestly.

<details><summary>Hint</summary>
(d) Think about what a cone over a family of elements in a preorder is: an
element below all of them.
(e) For the second question, consider whether $\mathcal{C}$ having all limits
tells you anything about $\mathcal{C}^{\mathrm{op}}$ having all limits.
</details>
<details><summary>Partial</summary>
(d) A cone over a diagram in a preorder category is an element below every
object in the diagram; the terminal such is the greatest lower bound, that is,
the *meet*. Dually the colimit is the *join*. The general definition collapses
because Hom-sets have at most one element, so the "unique morphism" clause is
automatic and only the existence of the bound is at issue — the same collapse
cat-01 saw in Example 4.10.
(e) *Second question.* Duality says: a colimit in $\mathcal{C}$ is a limit in
$\mathcal{C}^{\mathrm{op}}$, and vice versa. It does *not* say that a category
with all limits has all colimits — that would require $\mathcal{C}$ and
$\mathcal{C}^{\mathrm{op}}$ to have the same properties, which is exactly what
duality does not assert. ⟨your step: give a category with all finite products
that lacks some finite coproduct, or explain why you cannot from these sources.⟩
</details>
<details><summary>Worked start</summary>
(e) *First question.* Spivak establishes: terminal objects, products, cones,
the general limit as a terminal cone, pullbacks, and the one-line definition of
a cocone by dualisation. He explicitly declines to unpack colimits, calling
Definition 3.102 "completely useless for working with" until unpacked, and
defers that to his Chapter 6 — outside this unit's resources.

Aluffi establishes: initial and final objects with Proposition 5.4, the quotient
as an initial object (Claim 5.5), products, and coproducts with the disjoint
union in **Set** and $\max$ in the $\le$ category.

Neither establishes: that quotient and gluing constructions *in general* are
colimits, and neither mentions la, aa or top. ⟨your step: complete the audit —
say what would be needed to justify the strip's "all", and whether it is a
theorem or a slogan.⟩
</details>
<details><summary>Strategy</summary>
The third question of (e) is the one to take seriously. It is easy to nod along
to "quotients and gluings are colimits" because it is true and well known. The
exercise is to notice that *well known to you* and *established by the pages you
just read* are different things, and to say which is operating. That distinction
is the habit this whole module is for.
</details>
