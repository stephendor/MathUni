# Module: Point-Set Topology (top) — Semester 2

**Primary text:** Munkres, *Topology* (2nd ed.), Part I: General Topology —
§12–32 (Core Texts folder; prefer `md\`, cite PDF pages).
**Support:** Dexter Chua's Part IB *Metric and Topological Spaces* notes;
Conway, *A Course in Point Set Topology*; McCleary for the geometric bent.

**Mission link:** Topology is where "shape" is finally defined without distance,
and it is the language the whole mission is written in. Connected components are
**H0** (top-07); the **quotient topology** (top-12) and **cell complexes**
(top-13) are how every space whose homology a computer computes is actually
built. Continuity-as-preimages-of-open-sets (top-04) is the definition algebraic
topology and TDA keep verbatim. This module turns Semester-1 analysis on ℝ into
topology on anything.

**On-ramp:** builds directly on an-07 (open/closed sets in ℝ) and an-14 (metric
spaces). The metric topology (top-06) proves that everything you did in an-14 was
topology in disguise, so the strands converge rather than repeat.

## Arc and unit map

A single linear spine, top-01 → top-13, deliberately resequenced so the
**quotient material comes last as the payoff** rather than mid-book where Munkres
places §22. Foundations first (spaces, continuity, products, metrics), then the
two great theorems (connectedness = H0, compactness), then the countability and
separation hygiene, then quotients and cell complexes as the bridge out of the
module.

| Unit | Munkres § | Throughline |
|---|---|---|
| top-01 spaces & open sets | §12 | topology = the minimal structure for continuity |
| top-02 basis, order, subspace | §13, §14, §16 | ways to specify a topology; inherited structure |
| top-03 closure, interior, limit points | §17 | boundary made precise |
| top-04 continuity & homeomorphism | §18 | continuity via preimages; "same shape" |
| top-05 product topology | §15, §19 | box vs product subtlety (→ multiparameter) |
| top-06 metric topology | §20, §21 | every metric space is a space (←an-14) |
| top-07 connectedness & components | §23, §24, §25 | **= H0** |
| top-08 compactness | §26, §27 | finiteness for the infinite (←an-08) |
| top-09 limit-point & local compactness | §28, §29 | flavours of compactness; manifolds |
| top-10 countability axioms | §30 | which spaces data can sample |
| top-11 separation axioms, normal spaces | §31, §32 | Hausdorff = the sanity axiom |
| top-12 quotient topology ★ | §22 | glue to build; the collapse move, geometric |
| top-13 cones, suspension, CW complexes ★ | §22 + Hatcher ch. 0 | the computable spaces; on-ramp to at1/lab |

## Teaching notes

- **Name the quotient spiral aloud.** At top-12, say explicitly: this is the same
  construction as la-09 (quotient spaces), aa-09 (quotient rings), and aa-16
  (quotient modules). Point-set topology gives it its most *geometric* face —
  gluing — and that picture is what makes cell complexes intuitive.
- top-07 (connectedness) and top-08 (compactness) are the module's two theorems
  that matter most for the mission. Slow down; connect top-07 to H0 out loud and
  top-08 to where TDA's stability theory can hold.
- The metric topology (top-06) should feel like a homecoming, not new material:
  reframe an-14, don't re-teach it. Every open ball is now "just" a basis element.
- top-05: do not skip the box-vs-product distinction — it is the first place the
  "obvious" definition is wrong, and it recurs conceptually in multiparameter
  persistence (S4).
- top-13's CW complexes are Hatcher's ch. 0, not Munkres — treat this unit as the
  deliberate handoff into Semester 3's `at1` and the `lab`. Keep it concrete:
  build S¹, S², the torus, ℝP² by gluing.

## Scope note

Urysohn's lemma, the metrization theorem, and Tietze extension (Munkres §33–35)
are **out of scope** for the mission and omitted from the DAG; add just-in-time
only if a later unit demands metrizability. The Tychonoff theorem (§37) is
likewise deferred. The module stops where algebraic topology (`at1`) begins.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem set: Munkres exercises (the §-numbered problems), plus a small
  set of "glue-and-identify" constructions (torus, Klein bottle, ℝPⁿ) that feed
  directly into `at1`. Graded per spec §7, 80% gate.

## Common misconceptions to watch (seed for learning-records)

- "Open = not closed" — sets can be both (clopen) or neither; this is exactly
  what connectedness (top-07) detects.
- Confusing the box and product topologies (top-05); assuming the finite
  intuition survives to infinite products.
- Believing compactness means "closed and bounded" in general — Heine–Borel is a
  theorem about ℝⁿ (top-08), not a definition.
- Treating a quotient space as a subspace; forgetting the quotient map is the
  object that carries the topology (top-12).
- "Continuous = preserves limits of sequences" without a countability hypothesis
  (top-10 is where that hypothesis lives).
