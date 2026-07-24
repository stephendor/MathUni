# Module: Algebraic Topology II (at2) — Semester 4

**Primary text:** Hatcher, *Algebraic Topology*, **ch. 3** (Core Texts; prefer
`md\`, cite PDF pages). **Support:** Dexter Chua's *Algebraic Topology III*
notes; Ghrist §6.13 and Dey–Wang §2.5.4 for the persistent-cohomology unit.

**Mission link:** `at1` built homology; this module builds its dual and cashes
the duality in. Two payoffs are mission-critical. First, **persistent
cohomology** (at2-08): over a field it produces the *same barcode* as persistent
homology but reduces far more cheaply — the speed-up `tda1-09` named but could
not explain — and a persistent H¹ class lifts to a genuine circular coordinate
on the data. Second, **the ring structure** (at2-04): cohomology multiplies, so
it separates spaces that homology cannot, which is the first invariant in the
curriculum strictly finer than Betti numbers.

**On-ramp:** builds directly on `at1` (at1-07 singular homology, at1-08 cellular
homology, at1-09 exact sequences) and cashes in `la-10` (dual spaces — the whole
module is Hom(−, G) applied to a chain complex), `aa-20` (the PID structure
theorem, which is what the Ext term in the UCT is made of) and `aa-05` (rings,
for the cohomology ring).

## Arc and unit map

Three movements, following Hatcher's own three sections: **construct** the
theory (3.1), give it a **product** (3.2), then prove the **duality** that is
the chapter's destination (3.3). Section pins verified against the Hatcher TOC
(ch. 3 begins p. 185; 3.1 p. 190, 3.2 p. 206, 3.3 p. 230).

| Unit | Hatcher § | Throughline |
|---|---|---|
| at2-01 cochain complexes & cohomology | 3.1 | dualise the complex (←at1-07, la-10) |
| at2-02 the Universal Coefficient Theorem | 3.1 (p. 190) | Ext is the torsion correction (←aa-20) |
| at2-03 cohomology of spaces; cellular cohomology | 3.1 (p. 197) | transpose the boundary matrices (←at1-08) |
| at2-04 cup product & the cohomology ring | 3.2 (ring p. 212) | **finer than homology** (←aa-05) |
| at2-05 the Künneth formula | 3.2 (p. 214) | products decompose (←top-05) |
| at2-06 orientation & the fundamental class | 3.3 (p. 233) | when does [M] exist? (←at1-09) |
| at2-07 Poincaré duality | 3.3 (p. 239, 249) | H^k ≅ H_{n−k} on a closed orientable M (←la-10) |
| at2-08 persistent cohomology & circular coordinates | 3.1 + Dey 2.5.4, Ghrist 6.13 | **the mission payoff** (←tda1-09) |

## Teaching notes

- **Say what actually changes when you dualise.** Over a field, nothing
  interesting happens to the ranks — that is the *point*, and it is why TDA can
  use cohomology freely. Everything genuinely new (Ext, torsion, the ring) shows
  up over ℤ. Lead with that split so at2-02 does not feel like bookkeeping.
- at2-04 is the module's "wow" and deserves the slow lane: S²×S¹ and S²∨S¹∨S³
  have isomorphic homology groups and non-isomorphic cohomology rings. It is the
  first time in the curriculum that a finer invariant is *needed*.
- **Hypotheses are load-bearing in 3.3.** Poincaré duality needs *closed* and
  *R-orientable*. Say both aloud every time; `cap-03` will ask exactly this
  question of a published paper.
- at2-08 is the deliberate handoff into `tda2` and `cap`. State the barcode
  equality as a theorem over a field, not as folklore, and be explicit that the
  advantage is computational (reduction cost), not informational.

## Scope note

Higher homotopy groups, fibrations and spectral sequences (Hatcher ch. 4) are
out of scope for the mission. Of Hatcher's ch. 3 additional topics, only what
at2-08 needs is drawn on; 3.C–3.H are not covered. Cohomology *of sheaves* is
not here — that is `tda2-10`, and it is cellular sheaf cohomology from Ghrist
ch. 9, a different construction with a different index category.

## Boundary with other modules

- vs `at1`: at1 stops at homology and functoriality; at2 starts by dualising it.
- vs `tda1`: tda1-09 uses the cohomological speed-up as a fact about the
  algorithm; at2-08 supplies the theorem behind it.
- vs `tda2-10`: sheaf cohomology is *not* singular cohomology with coefficients.
  Name the difference out loud at at2-01 so the two do not blur in S4.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem set: Hatcher ch. 3 §-numbered exercises, including at least one
  cohomology-ring computation done by hand (ℝP², the torus, or a product) and
  one explicit use of Poincaré duality with its hypotheses checked. Graded per
  spec §7, 80% gate.

## Common misconceptions to watch (seed for learning-records)

- "Cohomology is just homology with the arrows flipped, so it carries the same
  information" (at2-01) — over a field the ranks agree, but over ℤ the Ext term
  is real, and the ring structure (at2-04) is extra information in every case.
- Reading the UCT as an isomorphism H^n ≅ Hom(H_n, G) (at2-02) — that holds only
  when Ext vanishes, e.g. over a field or for free homology.
- Assuming every manifold has a fundamental class (at2-06) — non-orientable
  closed manifolds have H_n = 0 over ℤ.
- Applying Poincaré duality to a manifold with boundary or a non-compact one
  (at2-07) — those need Lefschetz duality or the compactly-supported version.
- Believing persistent cohomology gives a *different* (better) barcode (at2-08)
  — over a field it gives the same one, faster.
