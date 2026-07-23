# Module: Analysis II (an2) — Semester 2

**Primary text:** Oxford M2 *Analysis II / III* notes (metric spaces; uniform
convergence and integration). **Support:** Abbott, *Understanding Analysis*
ch. 6 & 8 (Core Texts — the parts an-01…an-14 did not reach); Sutherland,
*Introduction to Metric and Topological Spaces* as a metric-spaces companion.

**Mission link:** TDA's analysis happens in *spaces of things*, not on ℝ. The
space of persistence diagrams is a **complete metric space** (an2-02); proving
the diagram of noisy data is close to the diagram of clean data is a
**uniform / sup-norm** statement (an2-05) and a **compactness** argument
(an2-03). This module supplies the functional-analytic backbone the stability
theorem stands on, and the multivariable derivative (an2-09) that gradient-based
filtrations need.

**Relationship to `top`:** an2 and top cover overlapping ground (metric and
topological spaces) from two directions — an2 keeps the analyst's questions
(convergence, completeness, approximation, Banach spaces), top takes the
structural view (open sets, quotients, cell complexes). an2-01 deepens an-14;
top-06 proves the same objects are topological spaces. Do them in parallel.

## Arc and unit map

Linear spine an2-01 → an2-09, in three movements: **metric spaces**
(01–04: topology, completeness, compactness, contraction), **function
convergence** (05–06: uniform convergence, series, Weierstrass), **function
spaces** (07–09: normed/Banach spaces, C[a,b], differentiation in ℝⁿ).

| Unit | Focus | Cross-links |
|---|---|---|
| an2-01 metric-space topology, deepened | open balls, continuity, on any metric | ←an-14 |
| an2-02 completeness and completion | Cauchy ⇒ convergent; completing a space | ←an-05 |
| an2-03 compactness | sequential, total boundedness, Arzelà–Ascoli | |
| an2-04 contraction mapping theorem | unique fixed points; ODE existence | |
| an2-05 uniform convergence of d/dx, ∫ | swapping limits with derivatives/integrals | ←an-13 |
| an2-06 series of functions | Weierstrass M-test; polynomial approximation | ←an-06 |
| an2-07 normed and Banach spaces | length on a vector space, completed | ←la-01 |
| an2-08 function spaces: C[a,b] | the sup-norm space of continuous functions | |
| an2-09 differentiation in ℝⁿ | the derivative as a linear map | ←la-05, la-06 |

## Teaching notes

- The recurring refrain: **the object of study is a space of functions or
  diagrams, treated as a single point in a bigger space.** Every unit should
  reinforce that altitude shift; it is the whole reason this module exists for
  the mission.
- an2-03 (Arzelà–Ascoli) and an2-05 (uniform convergence) are the two units that
  feed `lab-05` (stability) most directly — foreshadow the bottleneck distance
  when teaching compactness of function/diagram spaces.
- an2-07/08: introduce the sup-norm on C[a,b] as the concrete Banach space, then
  name it as the setting the stability theorem's inequalities inhabit.
- an2-09: insist on the derivative-as-linear-map picture (Fréchet), not a
  gradient vector — this is what makes la-05/la-06 pay off and what Morse-theoretic
  TDA requires.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem set: Oxford M2 sheet problems plus Abbott ch. 6/8 exercises;
  at least one problem must construct a completion or apply Arzelà–Ascoli.
  Graded per spec §7, 80% gate.

## Common misconceptions to watch (seed for learning-records)

- Pointwise vs uniform convergence (an2-05) — the single most consequential
  distinction in the module; pointwise limits of continuous functions need not
  be continuous.
- "Complete = closed" — completeness is intrinsic; closedness is relative to an
  ambient space (an2-02).
- Assuming a bounded sequence in an infinite-dimensional space has a convergent
  subsequence (false without compactness — the point of an2-03).
- Treating the derivative in ℝⁿ as a number or a vector rather than a linear map
  (an2-09).
