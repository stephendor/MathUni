# S1 · Linear Algebra (`la`) — content plan

**Date:** 2026-08-22 · **Branch:** `s1-la` (cut off `main` after PR #21 landed)
**Module:** 15 units, 2 pre-existing · **Primary text:** Axler, *Linear Algebra
Done Right*, 3rd ed.
**Preceded by:** `docs/plans/2026-08-21-s1-pw-content.md`

`la` is the load-bearing module of Semester 1: every mission strip in it points
at homology, and `la-06` (null space, range, fundamental theorem) and `la-09`
(quotients) are homology in miniature — H = ker ∂ / im ∂ is literally a null
space modulo a range, taken as a quotient. The module is a single-source module:
all fifteen units cite Axler and nothing else.

---

## 1. Tracker

`—` not started · `P` problem set · `L` lesson · `G` gates green · `✓` done

| Unit | Title | Axler | State | Note |
|---|---|---|---|---|
| la-01 | Vector spaces | 1A–1B | **✓** | pre-existing; 3 folios repaired (§3) |
| la-02 | Subspaces, sums, direct sums | 1C | **✓** | pre-existing; 3 folios + a false counterexample repaired (§3) |
| la-03 | Span and linear independence | 2A | — | |
| la-04 | Bases and dimension | 2B–2C | — | |
| la-05 | Linear maps | 3A | — | |
| la-06 | Null space, range, fundamental theorem | 3B | — | |
| la-07 | Matrices as linear maps | 3C | — | |
| la-08 | Invertibility and isomorphism | 3D | — | |
| la-09 | Products and quotient spaces | 3E | — | |
| la-10 | Duality | 3F | — | |
| la-11 | Eigenvalues, eigenvectors, invariant subspaces | 5A | — | |
| la-12 | Minimal polynomial and diagonalisability | 5B–5C | — | **title/source mismatch, see D-1** |
| la-13 | Inner product spaces | 6A | — | |
| la-14 | Orthonormal bases and Gram-Schmidt | 6B | — | |
| la-15 | Spectral theorem (real case) | 7A–7B | — | |

---

## 2. Verified source data

### 2.1 Axler's folio offset is not constant

`printed = PDF + offset`, fitted over all 352 PDF pages:

| offset | PDF range | printed range | pages with a folio |
|---|---|---|---|
| −17 | 18–66 | 1–49 | 20 |
| −16 | 67–177 | 51–161 | 57 |
| −15 | 178–346 | 163–331 | 85 |

The three single-page "plateaus" at PDF 347–349 (−14, −13, −12) are index
columns, not a fourth regime.

Chapter 2 straddles the first boundary and chapters 6–7 sit wholly in the
third, so **no single offset covers this module**. Every folio below was read
off the page it cites, not computed from one offset.

### 2.2 Section boundaries (printed folios)

| § | title | starts |
|---|---|---|
| 1.A | R^n and C^n | 2 |
| 1.B | Definition of Vector Space | 12 |
| 1.C | Subspaces | 18 |
| 2.A | Span and Linear Independence | 28 |
| 2.B | Bases | 39 |
| 2.C | Dimension | 44 |
| 3.A | The Vector Space of Linear Maps | 52 |
| 3.B | Null Spaces and Ranges | 59 |
| 3.C | Matrices | 70 |
| 3.D | Invertibility and Isomorphic Vector Spaces | 80 |
| 3.E | Products and Quotients of Vector Spaces | 91 |
| 3.F | Duality | 101 |
| 5.A | Invariant Subspaces | 132 |
| 5.B | Eigenvectors and Upper-Triangular Matrices | 143 |
| 5.C | Eigenspaces and Diagonal Matrices | 155 |
| 6.A | Inner Products and Norms | 164 |
| 6.B | Orthonormal Bases | 180 |
| 7.A | Self-Adjoint and Normal Operators | 204 |
| 7.B | The Spectral Theorem | 217 |

---

## 3. Source-boundary findings — citations

### 3.1 Repaired — la-01 and la-02, eight folios

All eight were off-by-one, in both directions.

| Where | Cited | Actually |
|---|---|---|
| la-01 lesson | Definition 1.10, p. 5 | p. **6** (PDF 23) |
| la-01 lesson | Definitions 1.12 and 1.17, pp. 6, 10 | pp. **7**, 10 — 1.12 shares a page with 1.13 |
| la-01 lesson | Theorem 1.13, p. 6 | p. **7** |
| la-01 set | §1.B Exercise 6, p. 18 | p. **17** — printed 18 opens §1.C |
| la-01 set | §1.C Exercise 20, p. 26 | p. **25** |
| la-02 lesson | §1.C Exercises 19 and 20, p. 26 | p. **25** — 26 begins at Exercise 21 |
| la-02 set | §1.C Exercise 19, p. 26 | p. **25** |

### 3.2 Repaired — la-02's problem set, a counterexample that was an example

Problem 1(c) asks whether {x ∈ **F**³ : x₁x₂x₃ = 0} is a subspace. Both the
*Partial* and *Worked start* reveals offered (1,0,0) + (0,1,0) = (1,1,0) as the
witness for failure of closure. That sum still has a zero coordinate, so it is
**in** the set: the counterexample was an example. The worked start noticed this
mid-sentence and corrected itself in front of the student.

Replaced with (1,1,0) + (0,0,1) = (1,1,1). The failed attempt is now stated
deliberately, as the point that a counterexample must be constructed rather than
stumbled on.

---

## 4. Open decisions

### D-1 — la-12's title names a result its source does not contain

`la-12` is titled **"Minimal polynomial and diagonalisability"** with resource
`Axler 5B-5C`. In the 3rd edition the minimal polynomial is **§8.C
"Characteristic and Minimal Polynomials", printed 261–270**. Sections 5.B and
5.C contain no minimal polynomial at all: 5.B is `p(T)`, the existence of an
eigenvalue over **C**, and upper-triangular matrices; 5.C is eigenspaces and
diagonalisability.

Content branches do not edit `curriculum/syllabus.yaml`, so the unit is written
against its declared resource. What 5.B *does* give is the germ the minimal
polynomial grows from — for v ≠ 0 the list v, Tv, …, Tⁿv is dependent, so some
nonzero polynomial p has p(T)v = 0 (Axler's proof of 5.21) — and the lesson
develops exactly that, names it as the germ, and says plainly that the minimal
polynomial itself is §8.C and out of scope for S1.

**Decision needed:** either (a) leave it, with the lesson's forward pointer
carrying the honesty; (b) amend the title to "Polynomials applied to operators
and diagonalisability" on a syllabus branch; or (c) add `Axler 8C` to the
resource list and grow the unit. Recommend **(b)** — the current title promises
a result the student will not meet, and (c) makes the heaviest unit in the
module heavier still.

---

## 5. Verification

Recorded at the end of the branch.
