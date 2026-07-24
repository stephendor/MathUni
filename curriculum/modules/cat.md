# Module: Category Theory Essentials (cat) — Semester 3

**Primary text:** Aluffi, *Algebra: Chapter 0* — the categorical thread
(§I.3–I.5 categories/morphisms/universal properties; §VIII.1 functors; natural
transformations and adjunctions where Aluffi threads them). **Support:** Spivak,
*Category Theory for the Sciences* / *Applied Category Theory* — systematises
what Aluffi threads (limits/colimits, adjunctions, Yoneda), and supplies the
applied framing.

**Mission link:** category theory is the language in which the mission's final
statement is cleanest. **Homology is a functor** (at1-10); a **persistence
module is a functor** from a poset category (cat-07); and an **ε-interleaving is
a pair of natural transformations** φ: M ⇒ N(·+ε) and ψ: N ⇒ M(·+ε) whose two
composites are the 2ε-shift maps of M and of N (cat-04). Stability is not itself
a natural transformation — it is the inequality `tda1-07` proves — but
interleaving is the language it is stated in. This module makes the "category
of —" reflex Aluffi built through `aa`
into an explicit toolkit, so `tda1` can speak of persistence categorically.

**On-ramp:** builds directly on `aa` — aa-07 (category of rings), aa-15 (category
of modules), aa-08 (homomorphisms as the morphisms). It runs alongside `at1` in
Semester 3 and converges with it at cat-07 (which needs at1-10's functorial
homology).

## Arc and unit map

Aluffi introduces category theory *threaded* through an algebra book, not as a
standalone course; this module pulls that thread straight and lets Spivak fill
the systematic gaps (limits, Yoneda).

| Unit | Source | Throughline |
|---|---|---|
| cat-01 categories & morphisms | Aluffi §I.3–I.4 | objects + arrows (←aa-07) |
| cat-02 universal properties; (co)products | Aluffi §I.5 | define by property, not construction (←aa-15) |
| cat-03 functors | Aluffi §VIII.1 + Spivak | structure-preserving maps of categories (←aa-08) |
| cat-04 natural transformations & Yoneda | Aluffi + Spivak | maps of functors; an object = its arrows |
| cat-05 limits & colimits | Spivak + Aluffi §I.5 | one construction for all gluings |
| cat-06 adjunctions | Aluffi §VIII.1 + Spivak | free ⊣ forgetful |
| cat-07 homology & persistence as functors | Oudot ch. 1 + Spivak | **the mission, categorically** (←at1-10) |

## Teaching notes

- Every construction from the earlier strands is an instance of something here.
  Say it explicitly: quotients (la-09, aa-09/16, top-12) are colimits; products
  and direct sums are limits/colimits; the free group/module (aa-18, aa-25) is a
  left adjoint. The module's value is retrospective unification — reward the
  learner for recognising old friends.
- Keep it **essentials**: this is a working toolkit for the mission, not a full
  category-theory course. Yoneda is included (cat-04) for its role in the
  representable-functor view of persistence, not for its own sake; monoidal
  categories, operads, and higher categories are out of scope.
- cat-07 is the payoff and the boundary with `tda1`: here persistence is *named*
  as a functor and interleaving as a pair of natural transformations between
  shifted functors; `tda1` then *proves* the stability theorem in that language.
  Language here, theorems there — and do not let "stability is natural" become a
  slogan, because stability is an inequality, not a natural transformation.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem set: Aluffi §I exercises plus Spivak's diagram-chasing problems;
  at least one problem must re-express an earlier construction (a quotient, a free
  object) as a (co)limit or adjunction. Graded per spec §7, 80% gate.

## Common misconceptions to watch (seed for learning-records)

- Treating a universal property as a construction rather than a characterisation
  (cat-02) — the object is whatever satisfies it, up to unique isomorphism.
- Covariant vs contravariant functors (cat-03); forgetting a functor acts on
  morphisms, not just objects.
- Believing "natural" is informal (cat-04) — it is a precise commuting-square
  condition, and it is the whole content of naturality.
- Confusing a limit with a colimit (cat-05) — the arrows point the other way, and
  that flips product↔coproduct, kernel↔cokernel.
