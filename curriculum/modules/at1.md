# Module: Algebraic Topology I (at1) — Semester 3

**Primary text:** Hatcher, *Algebraic Topology*, **ch. 0–2** (Core Texts; prefer
`md\`, cite PDF pages). **Support:** Dexter Chua's *Algebraic Topology* (Part II)
notes; Stillwell, *Classical Topology and Combinatorial Group Theory* for the
geometric fundamental-group picture.

**Mission link:** this is where algebra and topology fuse into the mission's
core object. Homology is defined here — **Hₙ = ker ∂ₙ / im ∂ₙ₊₁** (at1-07), the
exact thing every persistence computation tracks — and it is proved to be a
**homotopy invariant** (at1-01), which is *why* topological features are robust
to noise. The fundamental group (at1-03/04) is the first algebraic invariant of
shape; H₁ is its abelianisation. And homology is shown to be a **functor**
Top→Ab (at1-10), the fact that lets persistence itself be a functor — the bridge
into `cat` and `tda1`.

**On-ramp:** builds on `top` (top-04 continuity, top-13 CW complexes) and cashes
in the whole `aa` groups/modules strand — π₁ needs groups (aa-23), Van Kampen
needs free groups and quotients (aa-25/26), covering spaces need group actions
(aa-24), and homology needs the module isomorphism theorems and quotients
(aa-17, la-09).

## Arc and unit map

Two movements: the **fundamental group** (ch. 0–1) then **homology** (ch. 2).
Section pins verified against the Hatcher TOC.

| Unit | Hatcher § | Throughline |
|---|---|---|
| at1-01 homotopy & homotopy equivalence | ch. 0 | deformation; homotopy invariance |
| at1-02 CW complexes & operations | ch. 0 | the computable spaces (←top-13) |
| at1-03 the fundamental group π₁ | 1.1 | first algebraic invariant (←aa-23) |
| at1-04 π₁(S¹) and applications | 1.1 | first real computation; Brouwer, FTA |
| at1-05 Van Kampen's theorem | 1.2 | local-to-global (←aa-25/26) |
| at1-06 covering spaces | 1.3 | π₁ as a group action (←aa-24) |
| at1-07 simplicial & singular homology | 2.1 | **Hₙ = ker ∂ / im ∂** (←aa-17, la-09) |
| at1-08 cellular homology & degree | 2.2 | hand-computable Betti numbers (←aa-22) |
| at1-09 Mayer–Vietoris & coefficients | 2.2 | assemble-from-parts; 𝔽₂ vs ℤ (←aa-06) |
| at1-10 the formal viewpoint | 2.3 | **homology as a functor** → cat, tda1 |

## Teaching notes

- **Name the quotient spiral one more time.** At at1-07, say it aloud: Hₙ is the
  same kernel-mod-image construction as aa-09 (rings), aa-17 (modules), la-09
  (quotient spaces), top-12 (quotient spaces). This is its final, decisive form.
- The groups strand pays out here and nowhere earlier — π₁ (at1-03) is the first
  time aa-23's abstract groups become geometric; deck transformations (at1-06)
  are aa-24's actions made visible. Foreshadow forward from aa; reward backward
  from here.
- at1-04 (π₁(S¹)=ℤ) is the module's first "wow": a hole detected purely
  algebraically. Slow down; it is the template for persistent H₁.
- at1-10 (functoriality) is the deliberate handoff. State "homology is a functor"
  as the sentence `cat` will formalise and `tda1` will exploit — persistence is a
  functor of functors.

## Scope note

Cohomology, cup products, and Poincaré duality (Hatcher ch. 3) are Semester 4
(`at2`), not here. Higher homotopy groups (ch. 4) are out of scope for the
mission. This module stops at the point where persistence theory (`tda1`) takes
homology and adds a filtration.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem set: Hatcher exercises (the §-numbered problems), with at least
  one explicit homology computation of a CW complex (torus, ℝP², Klein bottle)
  by hand. Graded per spec §7, 80% gate.

## Common misconceptions to watch (seed for learning-records)

- Homotopy equivalence vs homeomorphism (at1-01) — a mug *is* homotopy equivalent
  to a circle but not homeomorphic.
- Thinking π₁ is abelian (at1-03) — it is not, in general; H₁ is its abelianisation.
- Confusing simplicial with singular homology (at1-07) — same groups, different
  definitions; the theorem that they agree is the point.
- Believing homology "counts holes" naively — it is ranks and torsion of quotient
  groups (at1-08); torsion has no naive hole-count (ties back to aa-22).
- Forgetting coefficients matter (at1-09) — H₁(ℝP²) is ℤ/2, invisible over ℚ.
