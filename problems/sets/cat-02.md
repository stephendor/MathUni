# cat-02 — Universal properties; products and coproducts

**Module:** Category Theory · **Unit:** cat-02
**Sources:** Aluffi, *Algebra: Chapter 0* — §I.5 "Universal properties"
(pp. 31–38): the opening argument for why universal properties are worth having
and the remark that the explicit description may involve an arbitrary choice
while the universal property does not (p. 31); §5.1, Definition 5.1 of initial
and final objects, the word *terminal*, Example 5.2 (the ≤ category on
$\mathbb{Z}$ has neither), Example 5.3 (in **Set**, $\emptyset$ is initial and
uniquely so, while *every* singleton is final), and Proposition 5.4 with its
proof (pp. 31–32); §5.2, the working definition of a universal property as a
terminal object of an accessory category, and the warning that such assertions
routinely leave the category and the key morphism unstated (p. 33); §5.3,
quotients, Claim 5.5 and its proof, and the observation that the solution is
not $A/\!\sim$ but the projection $\pi$ (pp. 33–34); §5.4, products, their
universal property, the proof in **Set**, and the computation that the product
in the ≤ category is $\min(a,b)$ (pp. 35–36); §5.5, coproducts as the mirror
construction, Proposition 5.6 that disjoint union is the coproduct in **Set**,
and the remark that the coproduct in the ≤ category is $\max(a,b)$ (pp. 36–38).

**Functors are still not available.** Aluffi says in §5.2 that the natural
context for universal properties "requires a good familiarity with the language
of *functors*, which we will only introduce at a later stage (cf. §VIII.1.1)",
and offers a working definition instead. §VIII.1.1 is cat-03's resource. This
unit uses the working definition, as Aluffi does.

Interleaves cat-01, whose Examples 3.3 and 3.9 are the categories every
universal property in this unit is stated in.

Submit your written solutions via `/grade cat-02`.

---

## Problem 1 (easy — initial and final)

(a) State Definition 5.1 for both initial and final objects, in the Hom-set
form Aluffi gives: $\operatorname{Hom}_\mathsf{C}(I, A)$ is a singleton for
every $A$, and dually.
(b) Aluffi offers *terminal* as a word for either, and then advises against
using it without saying which end you mean. Say why the ambiguity is dangerous
by giving a category with an initial object and no final one.
(c) Example 5.2: prove that the ≤ category on $\mathbb{Z}$ has neither. Then
show that the slice category of Example 3.6 — the same category sliced over
$A = 3$ — *does* have a final object, namely $(3,3)$, and still has no initial
one.
(d) Example 5.3: prove $\emptyset$ is initial in **Set**, being careful about
the "empty graph" defining the unique function out of it. Then prove every
singleton is final. Note the asymmetry: the initial object is unique on the
nose, the final objects are not.
(e) Prove Proposition 5.4: initial objects are isomorphic, final objects are
isomorphic, and the isomorphisms are uniquely determined. Identify the step
where "there is exactly one morphism $I \to I$, so it must be $1_I$" is used,
and say why that step needs the category axioms and not just initiality.

<details><summary>Hint</summary>
(e) Initiality gives a *unique* morphism $I \to I$; the category axioms
guarantee $1_I$ is *a* morphism $I \to I$. Both halves are needed.
</details>
<details><summary>Partial</summary>
(e) If $I$ is initial there is exactly one morphism $I \to I$; since $1_I$ is
one such (by the category axioms), that unique morphism is $1_I$. Now let
$I_1, I_2$ both be initial, with $f : I_1 \to I_2$ and $g : I_2 \to I_1$ the
unique morphisms. Then $gf : I_1 \to I_1$ must be $1_{I_1}$, and $fg = 1_{I_2}$
by the same token. So $f$ is an isomorphism, and it is unique because
initiality gave only one candidate. ⟨your step: do the final case, or say
precisely what "entirely analogous" means here — Aluffi leaves it as
Exercise 5.3.⟩
</details>
<details><summary>Strategy</summary>
Proposition 5.4 is the engine of the entire unit. Every "the object defined by
this universal property" in the rest of the course is licensed by it, and the
qualifier "up to a unique isomorphism" is doing real work: it is what lets one
say *the* product rather than *a* product.
</details>

---

## Problem 2 (easy — reading a universal property)

(a) Give Aluffi's working definition: a construction satisfies a universal
property when it may be viewed as a terminal object of some category, the
category usually being described in words and often without the word
"category" appearing.
(b) Aluffi notes that this is a working definition, and that the natural
context requires functors. Say where he defers them to, and say what this means
for what you are entitled to claim in this unit.
(c) Translate: "$\emptyset$ is universal with respect to the property of
mapping to sets." Which category, which end, which object?
(d) Now the harder pattern. Translate the schema "object $X$ is universal with
respect to the following property: for any $Y$ such that …, there exists a
unique morphism $Y \to X$ such that …" into a statement about an accessory
category, naming the objects and the morphisms of that category.
(e) Aluffi warns that "it is not uncommon to sweep under the rug part of the
essential information about the solution to a universal problem (usually some
key morphism)". Give the example from §5.3 where exactly this happens, and say
what the swept-away datum is.

<details><summary>Hint</summary>
(e) The answer is one arrow, and Aluffi names it in the sentence beginning
"Worst of all".
</details>
<details><summary>Partial</summary>
(c) The category is **Set**; the end is *initial*; the object is $\emptyset$.
"Universal with respect to mapping to sets" is just "there is exactly one
morphism from it to every set".
(e) The solution to the quotient universal problem is not the set $A/\!\sim$
but the *morphism* $\pi : A \to A/\!\sim$. Aluffi says the omission is
forgivable only because no other morphism $A \to A/\!\sim$ is a plausible
candidate. ⟨your step: give a universal property where the omitted morphism
would *not* be recoverable from context, and say what goes wrong.⟩
</details>

---

## Problem 3 (medium — quotients)

(a) Set up the category behind the assertion "the quotient $A/\!\sim$ is
universal with respect to the property of mapping $A$ to a set in such a way
that equivalent elements have the same image". Objects are pairs $(\varphi, Z)$
with $\varphi : A \to Z$ satisfying $a' \sim a'' \Rightarrow \varphi(a') =
\varphi(a'')$; say what the morphisms are and why that is "the only reasonable
way".
(b) Aluffi says this category is "very similar to the category defined in
Example 3.7". Say in what sense, and in what sense it is not the same.
(c) Prove Claim 5.5: $(\pi, A/\!\sim)$ is an initial object. Follow Aluffi —
first show that commutativity *forces* $\overline\varphi([a]_\sim) =
\varphi(a)$, which gives uniqueness, and only then check well-definedness,
which is where the defining condition on $(\varphi, Z)$ is spent.
(d) Note the order of the argument in (c): uniqueness is established before
existence. Say why that is the natural order here and not merely a stylistic
choice.
(e) Aluffi observes that if $\sim$ comes from a function $f : A \to B$ as in
§2.8, then $\operatorname{im} f$ also satisfies the universal property, so
$\operatorname{im} f \cong A/\!\sim$ by Proposition 5.4 — which is the content
of his Theorem 2.7. Reconstruct that argument, and say what the universal
property has bought over a direct proof.

<details><summary>Hint</summary>
(d) The commuting triangle pins down what $\overline\varphi$ must do to each
element before you know there is any such function.
</details>
<details><summary>Partial</summary>
(c) If the triangle commutes then $\overline\varphi(\pi(a)) = \varphi(a)$, that
is, $\overline\varphi([a]_\sim) = \varphi(a)$; so $\overline\varphi$ is
determined, hence unique if it exists. For existence, the prescription is
well-defined because $[a_1]_\sim = [a_2]_\sim$ implies $a_1 \sim a_2$ implies
$\varphi(a_1) = \varphi(a_2)$ — and that last implication is exactly the
condition defining the objects of the category. ⟨your step: say what would fail
if the objects were allowed to be arbitrary functions $A \to Z$.⟩
</details>

---

## Problem 4 (medium — products)

(a) State the universal property of the product: given $A, B$ and projections
$\pi_A, \pi_B$, for every $Z$ with morphisms $f_A : Z \to A$ and
$f_B : Z \to B$ there is a unique $\sigma : Z \to A \times B$ making both
triangles commute.
(b) Prove it in **Set**, by Aluffi's argument. Point out where he notes there
is *no* well-definedness issue this time, and say why not — contrast with
Problem 3(c).
(c) Express the universal property as a statement about terminal objects: the
product is a *final* object in the category $\mathsf{C}_{A,B}$ of Example 3.9.
Say what an object and a morphism of $\mathsf{C}_{A,B}$ are.
(d) Define what it means for a category to *have finite products*. Then compute
the product in the ≤ category on $\mathbb{Z}$: write out what the universal
property says there, and identify the answer.
(e) Aluffi calls the resulting connection unexpected: the Cartesian product of
sets and the minimum of two integers are "both examples of products, taken in
different categories". Explain what makes them the same thing, and say what
would be lost if one insisted that a product must "look like" a product.

<details><summary>Hint</summary>
(d) The universal property reads: for all $z$ with $z \le a$ and $z \le b$, we
have $z \le a \times b$. What integer has that property and is itself $\le a$
and $\le b$?
</details>
<details><summary>Partial</summary>
(b) $\sigma(z) = (f_A(z), f_B(z))$ makes both triangles commute, and the
commutativity forces that formula, so $\sigma$ is unique. There is no
well-definedness issue because $\sigma$ is defined on elements of $Z$ directly,
not on equivalence classes — nothing has to be checked to be independent of a
representative.
(d) $\min(a,b)$. It is $\le a$ and $\le b$, supplying the two projections; and
any $z$ with $z \le a$ and $z \le b$ satisfies $z \le \min(a,b)$, supplying the
unique morphism. ⟨your step: say why uniqueness of $\sigma$ is automatic in
this category, and which fact from cat-01 you are using.⟩
</details>

---

## Problem 5 (hard — coproducts, and what "dual" buys)

(a) State the universal property of the coproduct $A \amalg B$ with its
morphisms $i_A, i_B$, obtained by reversing every arrow in Problem 4(a).
Express it as: the coproduct is an *initial* object in $\mathsf{C}^{A,B}$.
(b) Prove Proposition 5.6: disjoint union is the coproduct in **Set**. Use
Aluffi's explicit model $A \amalg B = (\{0\} \times A) \cup (\{1\} \times B)$
and define $\sigma$ by cases.
(c) Aluffi says this "sheds considerable light on the mysteries of disjoint
unions". Specifically: the explicit construction involved an arbitrary choice
(why $\{0\}$ and $\{1\}$?), and different choices gave isomorphic results. Say
exactly which earlier result explains that, and complete the analogy Aluffi
draws with singletons in **Set**.
(d) Compute the coproduct in the ≤ category on $\mathbb{Z}$ and check it
against Aluffi's answer. Then say what the pair (product, coproduct) = (min,
max) tells you about the relationship between the two constructions, and
whether that relationship holds in **Set**.
(e) Now the reflection, and it needs care because two claims are easy to merge.
Aluffi's slogan is that products and coproducts are "mirror" constructions,
obtained by reversing arrows. First: state precisely what that means — what is
reversed, and in which category. Second: decide whether "mirror" implies the
two constructions must be *different*. Check your answer against **Set**, where
$A \times B$ and $A \amalg B$ are visibly different, and against a category you
know from aa where the finite product and the finite coproduct of two objects
coincide. Third: say what that coincidence would mean for a claim of the form
"the direct sum is *the* universal property behind combining two objects".

<details><summary>Hint</summary>
(d) Reverse the inequalities in Problem 4(d).
(e) For the second and third parts, think about vector spaces or abelian
groups, and about what $V \oplus W$ satisfies. Then ask whether the same holds
for infinitely many summands.
</details>
<details><summary>Partial</summary>
(c) Proposition 5.4: terminal objects are unique up to a unique isomorphism but
not unique on the nose. So there is no "most beautiful" disjoint union, just as
there is no most beautiful singleton in **Set** — and the arbitrariness of
$\{0\}$ and $\{1\}$ is exactly of that kind, invisible to the universal
property.
(d) $\max(a,b)$, as Aluffi states. In **Set** the product and coproduct are
emphatically not the same construction; in the ≤ category they are $\min$ and
$\max$, which agree only when $a = b$. ⟨your step: so "mirror" does not mean
"equal" — but does it forbid equality? Answer that before (e).⟩
</details>
<details><summary>Worked start</summary>
(e) *What is reversed.* The product is a final object of $\mathsf{C}_{A,B}$,
whose objects are pairs of morphisms out of a common source into $A$ and $B$.
The coproduct is an initial object of $\mathsf{C}^{A,B}$, whose objects are
pairs of morphisms into a common target out of $A$ and $B$. Reversing every
arrow of $\mathsf{C}$ turns one category into the other and swaps initial with
final — this is Aluffi's Exercise 5.1, that a final object of $\mathsf{C}$ is
initial in $\mathsf{C}^{\mathrm{op}}$.

*Does mirror imply different?* No. Nothing in the definitions forbids one
object from satisfying both universal properties. ⟨your step: for finitely many
vector spaces or abelian groups, check that $V \oplus W$ with the inclusions is
a coproduct and that $V \oplus W$ with the projections is a product — two
different structures on one object. Then check what happens for an infinite
family, where the product and the coproduct part company, and say which one
$\bigoplus$ is. Finally, say what that means for describing "direct sum" as a
single universal property without specifying which.⟩
</details>
<details><summary>Strategy</summary>
(e) is the point of the unit. "Direct sum" names an object; "product" and
"coproduct" name universal properties, and in the finite case a single object
can carry both. That coincidence is a fact about particular categories, not
about the definitions — and it stops being true for infinite families. Any
slogan of the form "X is *the* universal property behind Y" should prompt the
question: which one, and for how many summands?
</details>
