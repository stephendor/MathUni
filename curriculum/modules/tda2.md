# Module: TDA II (tda2) — Semester 4

**Primary text:** Dey & Wang, *Computational Topology for Data Analysis*
(Core Texts; prefer `md\`, cite PDF pages). **Support:** Ghrist, *Elementary
Applied Topology* — used as a genuine second spine for the two sheaf units
(ch. 9–10), not as background reading.

**Mission link:** `tda1` proved that a one-parameter filtration has a barcode
and that the barcode is stable. This module is what happens when each of those
hypotheses is dropped. Let the arrows point both ways and the barcode survives
(tda2-01, Gabriel). Add a second filtration parameter and **it does not**
(tda2-02) — there is no interval decomposition for d ≥ 2, so the rest of
multiparameter persistence is the search for computable substitutes (tda2-03/04).
The remaining units are the machinery a real analysis needs between the theorem
and the answer: shrink the complex (tda2-05, tda2-08), summarise the function
rather than the space (tda2-06), justify the picture (tda2-07), get the summary
into a model (tda2-09), and finally see the whole subject as one categorical
move (tda2-10/11).

**On-ramp:** builds on all of `tda1`, on `lab` for the computational units
(lab-03 reduction, lab-06/07 vectorisation and pipelines, lab-08 Mapper), on
`cat` for the categorical units (cat-03/04/05, cat-07), on `aa` for the algebra
of multiparameter modules (aa-13 polynomial rings, aa-15/19/20 modules), and on
`at2-01` for cohomology before sheaf cohomology.

## Arc and unit map

Four movements: **beyond one parameter** (01–04), **structure of the domain**
(05–08), **into machine learning** (09), **the categorical account** (10–11).
Section pins verified against the Dey–Wang and Ghrist TOCs.

| Unit | Pin | Throughline |
|---|---|---|
| tda2-01 zigzag & levelset zigzag | Dey 4.3, 4.5; Ghrist 5.15 | arrows both ways; barcode survives (←tda1-04) |
| tda2-02 multiparameter modules | Dey 11.1 | ℤ^d-graded k[x₁..x_d]-modules; **no barcode** (←aa-13, aa-15) |
| tda2-03 presentations, decomposition, invariants | Dey 11.2–11.4, 11.6 | generators & relations replace the structure theorem (←aa-19/20) |
| tda2-04 multiparameter distances | Dey 12.1–12.4 | interleaving generalises; computing it does not (←tda1-06, cat-07) |
| tda2-05 discrete Morse & graph reconstruction | Dey 10.1–10.5; Ghrist 7.8 | shrink the complex, keep the homology (←tda1-08) |
| tda2-06 Reeb graphs & their distances | Dey 7.1–7.3 | quotient by level-set components (←top-12) |
| tda2-07 cover, nerve, multiscale Mapper | Dey 9.1, 9.3, 9.4, 9.6 | **the theorem behind lab-08's picture** |
| tda2-08 sparsification & approximation | Dey 6.1–6.3, 2.3 | linear-size complexes, interleaved (←lab-03) |
| tda2-09 kernels, vectorisation, topological loss | Dey 13.1–13.3 | which of lab-06's maps are stable |
| tda2-10 cellular sheaves & sheaf cohomology | Ghrist 9.1–9.5 | data on cells; H⁰ = global sections (←cat-03, la-06) |
| tda2-11 cosheaves, categorification, interleaving | Ghrist 9.10, 10.1, 10.5, 10.6 | the one move the whole subject has been making (←cat-04/05) |

## Teaching notes

- **tda2-02 is the module's hinge and its bad news.** Do not soften it: for
  d ≥ 2 there is no complete discrete invariant analogous to the barcode. Every
  later multiparameter unit is a response to that fact, and stating it plainly
  is what stops tda2-03's invariants from looking arbitrary.
- The `aa` module strand pays out twice here and in opposite directions: aa-20's
  PID structure theorem *is* the one-parameter barcode theorem, and its
  **failure** over k[x,y] is precisely why tda2-03 needs presentations. Teach the
  pair together.
- tda2-07 is the retrospective justification of `lab-08`. Stephen ran Mapper as a
  tool a year earlier; the nerve theorem and the good-cover hypothesis are what
  make its output an argument rather than a picture. Foreshadow from lab-08.
- **Ghrist and Dey–Wang are different books with different registers.** Dey–Wang
  is algorithmic and proof-complete; Ghrist is panoramic and deliberately
  compressed. For tda2-10/11, supply the details Ghrist elides rather than
  pretending the exposition is self-contained.
- tda2-11 is the module's closing argument and should be taught as one: name
  homology, persistence, Mapper, sheaves and interleaving as instances of a
  single categorification move. It is the sentence `cap-03` will use to read a
  paper it has never seen.

## Scope note

Dey–Wang ch. 5 (optimal generators and persistent cycles) and ch. 8.3 (path
homology for directed graphs) are not covered — worthwhile but not on the
mission's critical path. Ghrist ch. 1–8 is covered elsewhere or out of scope;
only ch. 9–10 is pinned here. Sheaf theory is treated in its **cellular** form
only: no derived functors, no Grothendieck topologies.

## Boundary with other modules

- vs `tda1`: tda1 is the one-parameter theory and its stability. tda2 is every
  direction that theory generalises, plus the computational machinery.
- vs `lab`: lab is execution (run Mapper, vectorise a diagram). tda2 is the
  theorem that licenses the execution. Where both touch a topic (Mapper,
  vectorisation, reduction), lab came first and tda2 explains it.
- vs `at2`: at2-01's singular cohomology and tda2-10's cellular sheaf cohomology
  are different constructions over different index categories. Say so explicitly.
- vs `cat`: cat supplies functors, natural transformations, limits and colimits
  as pure category theory. tda2-11 uses them on persistence; it does not
  re-teach them.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem set: Dey–Wang chapter exercises, including at least one
  bigraded-module computation by hand (a presentation and its rank invariant)
  and one written argument checking a nerve or stability hypothesis on a
  concrete cover. Graded per spec §7, 80% gate.

## Common misconceptions to watch (seed for learning-records)

- Expecting a multiparameter barcode (tda2-02) — there is none for d ≥ 2; the
  rank invariant is not complete.
- Treating the matching distance as *the* multiparameter distance (tda2-04) —
  it is a computable lower bound for the interleaving distance.
- Believing Mapper's output is a topological invariant (tda2-07) — it depends on
  the cover, the lens and the clustering; stability is a statement about
  *multiscale* Mapper under interleaving of covers.
- Thinking sparsification is a heuristic (tda2-08) — the approximation carries a
  multiplicative interleaving guarantee, so tda1-07's stability still applies.
- Assuming any vectorisation of diagrams is stable (tda2-09) — stability is
  per-map with its own constant, and some convenient features have none.
- Conflating a cellular sheaf with a presheaf of functions on open sets
  (tda2-10) — the index category here is the face poset of a complex.
