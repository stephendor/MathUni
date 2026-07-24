# Module: TDA I (tda1) — Semester 3

**Primary text:** Edelsbrunner–Harer, *Computational Topology: An Introduction*
(ch. III–IV, VI–VIII) and Oudot, *Persistence Theory: From Quiver
Representations to Data Analysis* (Part 1, ch. 1–3) — Core Texts. **Support:**
Ghrist, *Elementary Applied Topology* for intuition.

**Mission link:** this is the mission, stated and proved. Filtrations (tda1-01)
feed **persistent homology** (tda1-03); the **structure theorem** (tda1-04)
decomposes a *tame* persistence module over a field — pointwise
finite-dimensional, and for the finite filtrations this course works with, of
finite type — uniquely into intervals, the **barcode**. In that finite-type case
it is exactly `aa-20` (finitely generated modules over a PID) applied to graded
k[t]-modules; drop the hypothesis and the decomposition can fail. The
**stability theorem** (tda1-07) proves the barcode moves by at
most ε when the data is perturbed by ε — the reason TDA is trustworthy. Every
theorem here is the *why* behind something `lab` computed.

**Boundary with `lab` (say it out loud — no silent overlap):** `lab` (Semester 2)
is hands-on computation — install the tools, get a barcode, read it. `tda1`
(Semester 3) is the **theory** — prove the barcode exists and is unique, prove it
is stable, prove the algorithm is correct. Where `lab-04` plotted a diagram,
`tda1-05` defines its space; where `lab-05` measured a distance, `tda1-06/07`
proves the stability bound. Compute first, prove second.

**On-ramp:** needs homology (`at1`, esp. at1-07/08), the structure theorem
(`aa-20`), metric spaces and compactness (`an2-01/03`), uniform bounds
(`an2-05`), matrix reduction (`la-07`), and the ε-craft of `pw-04`; it
cross-references the `lab` computations throughout.

## Arc and unit map

From filtration to stability, with the algorithm at the end. Section pins
verified against both TOCs (Edelsbrunner ch. III/IV/VI/VII/VIII; Oudot ch. 1–3).

| Unit | Source | Throughline |
|---|---|---|
| tda1-01 complexes & filtrations | E–H III.1, Oudot ch. 2 | the input object (←lab-02) |
| tda1-02 homology by matrix reduction | E–H IV.1–IV.2 | homology as linear algebra (←la-07) |
| tda1-03 persistent homology; the persistence module | E–H VII.1, Oudot ch. 1 | the central algebraic object |
| tda1-04 structure theorem: interval decomposition ★ | Oudot ch. 1 | **barcode = aa-20** |
| tda1-05 persistence diagrams & their space | Oudot ch. 1, E–H VII | diagram space is metric (←an2-01) |
| tda1-06 bottleneck & interleaving metrics | Oudot ch. 3, E–H VIII | algebraic vs geometric distance |
| tda1-07 the stability theorem ★ | Oudot ch. 3, E–H VIII.2 | **the keystone** (←pw-04, an2-05) |
| tda1-08 Morse theory & sublevel-set persistence | E–H VI–VII | scalar field → barcode (←an2-09) |
| tda1-09 the persistence algorithm & duality | E–H VII.2, IV.4 | why Ripser is fast (←lab-03) |

## Teaching notes

- **tda1-04 is the summit of the entire degree.** Everything — la's quotients,
  aa's modules and structure theorem, at1's homology — converges on the statement
  "a *tame* persistence module decomposes uniquely into intervals." Say the
  hypothesis every time the statement is said; it is the first thing `cap-03`
  will ask of a paper. Draw the line from aa-20 explicitly: for finite type the
  barcode is not a new theorem, it is aa-20 in a graded guise. Foreshadow it from
  aa-20 and lab-04.
- **tda1-07 (stability) is the keystone theorem.** Frame it as the ε-statement
  pw-04 trained and the compactness/uniform-bound machinery an2-03/05 underwrites.
  This is the theorem that justifies ignoring short bars as noise.
- Keep the lab boundary live: for each theory unit, point back to the lab unit
  that computed the object. The learner should feel they are proving what they
  already ran.
- Coefficients: persistence is usually done over a field (𝔽₂), so modules are
  vector spaces and the structure theorem is cleanest — connect to aa-06/at1-09.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem set: Edelsbrunner–Harer and Oudot exercises; at least one proof
  (interval decomposition on a small module, or a stability bound) and one
  computed-then-justified example reusing a `lab` result. Graded per spec §7,
  80% gate.

## Common misconceptions to watch (seed for learning-records)

- Reading the barcode as a picture rather than a decomposition theorem (tda1-04)
  — the intervals are algebraic summands, unique up to isomorphism.
- Confusing bottleneck and interleaving distance (tda1-06) — one is on diagrams,
  one on modules; the Isometry Theorem is precisely that they agree.
- Believing stability says the *homology* is stable — it is the *diagram/barcode*
  that is stable in bottleneck distance (tda1-07); individual groups can jump.
- Assuming Vietoris–Rips and Čech give the same persistence (they interleave,
  they do not coincide) — ties back to lab-02.
- Forgetting finiteness/tameness hypotheses under which the structure theorem
  holds (tda1-03/04).
