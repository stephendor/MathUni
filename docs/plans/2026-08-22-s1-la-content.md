# S1 · Linear Algebra (`la`) — content plan

**Date:** 2026-08-22, completed 2026-08-23 · **Branch:** `s1-la` (cut off `main`
after PR #21 landed)
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
| la-01 | Vector spaces | 1A–1B | **✓** | pre-existing; 3 folios repaired (§3.1) |
| la-02 | Subspaces, sums, direct sums | 1C | **✓** | pre-existing; 3 folios + a false counterexample repaired (§3.1–3.2) |
| la-03 | Span and linear independence | 2A | **✓** | written this branch |
| la-04 | Bases and dimension | 2B–2C | **✓** | written this branch |
| la-05 | Linear maps | 3A | **✓** | written this branch |
| la-06 | Null space, range, fundamental theorem | 3B | **✓** | written this branch |
| la-07 | Matrices as linear maps | 3C | **✓** | written this branch |
| la-08 | Invertibility and isomorphism | 3D | **✓** | written this branch |
| la-09 | Products and quotient spaces | 3E | **✓** | written this branch |
| la-10 | Duality | 3F | **✓** | written this branch |
| la-11 | Eigenvalues, eigenvectors, invariant subspaces | 5A | **✓** | written this branch |
| la-12 | Minimal polynomial and diagonalisability | 5B–5C | **✓** | written this branch; **title/source mismatch, D-1 open** |
| la-13 | Inner product spaces | 6A | **✓** | written this branch |
| la-14 | Orthonormal bases and Gram-Schmidt | 6B | **✓** | written this branch |
| la-15 | Spectral theorem (real case) | 7A–7B | **✓** | written this branch; needs one §6.C definition, F-1 (closed) |

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
third, so **no single offset covers this module**. Every folio in the module was
read off the page it cites, not computed from one offset.

### 2.2 Section boundaries (printed folios)

Generated from the book's own page tree and committed to
`resources/sections.json` (see §5.1).

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
| 6.C | Orthogonal Complements | 193 |
| 7.A | Self-Adjoint and Normal Operators | 204 |
| 7.B | The Spectral Theorem | 217 |

Chapter 4 is unsectioned; its results are cited as "Axler, Chapter 4".

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

A ninth was found later by the new section gate: la-01's set header claimed
§1.B ran to printed 18, where §1.C begins. Corrected to pp. 12–17.

### 3.2 Repaired — la-02's problem set, a counterexample that was an example

Problem 1(c) asks whether {x ∈ **F**³ : x₁x₂x₃ = 0} is a subspace. Both the
*Partial* and *Worked start* reveals offered (1,0,0) + (0,1,0) = (1,1,0) as the
witness for failure of closure. That sum still has a zero coordinate, so it is
**in** the set: the counterexample was an example. The worked start noticed this
mid-sentence and corrected itself in front of the student.

Replaced with (1,1,0) + (0,0,1) = (1,1,1). The failed attempt is now stated
deliberately, as the point that a counterexample must be constructed rather than
stumbled on.

### 3.3 F-1 — la-15 needs one definition from §6.C

The Real Spectral Theorem's induction runs through the orthogonal complement
U^⊥, and Theorem 7.28 is stated in terms of it. §6.C is not the declared
resource of any `la` unit: la-14 is 6B and la-15 is 7A–7B. The lesson therefore
states the definition where it is needed and cites it — Axler §6.C, Definition
6.45, printed 193, with the splitting V = U ⊕ U^⊥ at Theorem 6.47, printed 194 —
and says in the footer that the ingredient comes from outside the module's
declared sources.

**Closed, 2026-08-23.** Owner decision: the dependency is acceptable as it
stands, because the definition is carried in the lesson rather than assumed. No
syllabus change. If `la-14` or `la-15` is edited for another reason, adding
`Axler 6C` to its resource list would tidy it, but nothing depends on that.

### 3.4 F-2 — no edition is recorded for any book

D-1's mismatch is the visible symptom of a gap: neither `resources/bookmap.json`
nor `curriculum/syllabus.yaml` records which *edition* of a text a unit is
pinned to. `bookmap.json` gives Axler a title, a PDF path and a page tree, and
no edition field. A section pin such as `5B-5C` is edition-relative — in the
copy on disk it is upper-triangular matrices and eigenspaces, in the 4th edition
the same string is the minimal polynomial and upper-triangular matrices — so a
unit drafted from one edition and read against another produces a pin that is
valid, resolvable, and about different mathematics.

Nothing can catch this today. `check_resources` asks whether a pinned section
exists, and 5.B exists in both editions; `check_sections.py` (§5.1) asks whether
a citation's section label agrees with the page it names, which is a
within-edition question. The check that would have caught D-1 compares a unit's
*title* against the *heading* of the section it pins, both read off the book —
the comparison this plan ran by hand in §4, D-1, which found one mismatch in
fifteen.

Recommend an `edition` field in `bookmap.json`, populated from each book's title
page, before the next module pins a new text. That is a prerequisite for the
title-versus-heading check, not a substitute for it.

---

## 4. Open decisions

### D-1 — la-12's title names a result no section of this book delivers

`la-12` is titled **"Minimal polynomial and diagonalisability"** with resource
`Axler 5B-5C`. In the copy on disk the minimal polynomial is **§8.C
"Characteristic and Minimal Polynomials", printed 261–270**. Sections 5.B and
5.C contain no minimal polynomial at all: 5.B is "Eigenvectors and
Upper-Triangular Matrices" — p(T), the existence of an eigenvalue over **C**,
and the invariant-flag characterisation — and 5.C is "Eigenspaces and Diagonal
Matrices".

**The title is a one-off.** Reading each Axler section's own heading off its
printed page and setting it beside the unit title that pins it, all fourteen
other `la` units track their sections closely (la-13 "Inner product spaces" /
6.A "Inner Products and Norms"; la-15 "Spectral theorem (real case)" / 7.B "The
Spectral Theorem"). la-12 is the only unit of fifteen whose title names
something its sections do not contain, so this is drift in one entry rather
than a systematic mispinning.

**Where the title comes from.** "The Minimal Polynomial" is a section name in
Axler's *4th* edition, where chapter 5 runs 5.A Invariant Subspaces, 5.B The
Minimal Polynomial, 5.C Upper-Triangular Matrices, 5.D Diagonalizable
Operators. This entry reads as having been drafted from that table of contents.
I cannot verify the 4e TOC from disk — no copy is in `bookmap.json` — so treat
the provenance as inference; the decision below does not depend on it. The
edition itself is nowhere recorded (F-2), which is why nothing could flag the
mismatch.

**Option (c) — add `Axler 8C` and grow the unit — is not available.** It was
listed as the expensive option in the draft of this plan; it is in fact
impossible. The string "diagonaliz" does not occur anywhere in printed 261–269.
§8.C never connects the minimal polynomial to diagonalisability; the criterion
that does — a diagonalisable operator is exactly one whose minimal polynomial
has distinct linear factors — is a 4th-edition result and is absent here. So
(c) would buy the minimal polynomial and still not buy "and diagonalisability".
It is also dearer than it looks: 8.40's existence proof is cheap (it needs only
dim L(V) = n², 3.61, and the Linear Dependence Lemma 2.21, both already in the
module), but everything that makes §8.C worth teaching is built on chapter 8 —
8.34 defines the characteristic polynomial through generalized-eigenspace
multiplicities, 8.37 Cayley–Hamilton is proved through them, and both are
stated for **C** only.

**The sections are load-bearing and cannot be swapped out.** la-15 lists la-12
as a prerequisite, and what its proof actually consumes is 5.B and 5.C — the
polynomial machinery behind 7.27 and the eigenspace decomposition — not the
minimal polynomial. The mission strip, "Structure theorems here foreshadow
persistence module decomposition", is likewise served by 5.C's V as a direct sum
of eigenspaces and not by the minimal polynomial. Repointing the resource would
break both.

**Recommendation: (b), amend the title.** The unit as written is the correct
unit; only its name is wrong. Suggested edit, on a syllabus branch:

| field | from | to |
|---|---|---|
| `title` | Minimal polynomial and diagonalisability | Upper-triangular matrices and diagonalisability |
| `hook` | One polynomial that knows everything about your operator. | Every complex operator can be put in triangular form. Which ones go further, to diagonal? |

`resources`, `prereqs` and `mission_link` stand unchanged. The lesson's
`<title>` and `<h1>` mirror the syllabus title and change with it; the body does
not, beyond deleting the forward pointer that currently apologises for the
title. The germ argument stays — it is good mathematics and the honest lead-in
to §8.C — but it becomes a closing remark rather than a repair.

### D-2 — whether to wire `scripts/check_sections.py` into CI

The new section gate (§5.1) is not wired into any workflow. Adding a gate to the
pipeline is an owner decision, so this branch ships the script, its index and its
tests without touching CI. Evidence for wiring it: it found 22 wrong section
labels in one lesson under construction and 2 in already-merged work, none of
which any existing gate could see; it needs no book drive, so it runs anywhere;
and it exits 2 rather than 0 when it cannot run. Evidence against: it currently
indexes one book, so it reports SKIP for most of the corpus, and a SKIP-heavy
green run is exactly the shape of a check that stops being read.

Recommend wiring it **after** the remaining books are indexed, so that its first
CI run has a meaningful denominator.

---

## 5. Gate changes made on this branch

Each was found by a defect in this module's own content, and each ships with
controls that fire on the original defect.

### 5.1 New: `scripts/check_sections.py`

A citation asserts three things — a section label, a result number, and a
printed page. `citations.py` verified the last two and never looked at the
first, so `— Axler §3.A, Definition 3.12, p. 59` passed in full while naming
the wrong section, printed 59 being where §3.B begins. Twenty-two citations in
la-06 were in that state, plus two in already-merged work.

The index is generated from the book's page tree by `--refresh` and committed to
`resources/sections.json`, never hand-written. Exit 2 when the index is missing
or empty or when no file named an indexed book, so an unrunnable check cannot
read as a clean one. 15 selftest controls, 15 tests.

One later fix to it: the 220-character safety cap on a citation's tail landed
inside "101" in la-10's Sources line, so the tail ended "pp. 1" and a correct
citation was reported as naming printed page 1. A cap that silently shortens a
page number can turn a wrong page into a plausible one as easily as it turned a
right one into an absurd one. Cap raised to 400 and made digit-safe.

### 5.2 `scripts/gate.py` — event-handler attributes are parsed

`onclick="check(this,false"` is well-formed HTML: the attribute value ends at
the second quote and the tag closes normally, so the tag checker is silent, and
the `<script>` checker never reads attributes. The handler throws only when a
student clicks. One shipped in la-07. Seven controls, five tests. Batched to one
`node` process per file — the naive version took over two minutes on the corpus
and would simply have stopped being run; batched it is 19 seconds, and each
handler still reports its own index so an early error cannot mask a later one.

### 5.3 `scripts/citations.py` — four holes closed

* **Lettered exercise items.** Axler prints 2.A.5 as `5 (a) Show that ...`, and
  requiring a letter after the number meant the exercise had no label and a
  correct citation was reported wrong.
* **Markdown list markers.** The converter sometimes emits its own ordered-list
  marker in front of the book's number: `1. 1 Suppose T in L(U, V)` on printed
  88, and — where it counted a part (b) as an item of its own — `4. 3 Suppose T
  in L(R^3)` on printed 189, with the marker one ahead. Any integer marker is
  now admitted, which is safe because the number sought is anchored *after* it
  and so can never be read as it.
* **`Notation` as a result kind.** Axler heads L(V, W), F^{m,n} and the
  row/column notation that way. Without the kind word the citation produced no
  id at all, so the folio was never checked and the denominator never moved —
  the absence looked exactly like a file with nothing to check. Eleven citations
  across la-01, la-03 and la-05 were in that state.
* Selftest 72 → 82 over the branch.

### 5.4 Authoring rules learned the hard way

Recorded because each cost more than one occurrence:

* **Pages attach per clause.** `citations.py` charges every page named in a
  clause to every result named in the same clause, so a footer sentence carrying
  both an earlier unit's folio and one of this unit's results checks the second
  against the first's page. This happened on five units before the shape that
  works was settled: a bare `X is Axler §Y, Result, p. N.` sentence with nothing
  else in it, followed by a separate sentence naming no numbers.
* **A reference in running prose is checked by nobody.** `citations.py` reads
  only recognised citation spans, so "that is la-03's Theorem 2.26, p. 36"
  written as prose is counted by the coverage gate and the section gate and
  verified by neither. Five such references were found and moved into spans.
* **Footer exercise lists need the section-then-numbers form.** "Exercises 2.A 5
  and 11" parses as nothing at all; the singular "Exercise 3.E 15" parses as
  "Exercise 3", a real exercise on a different page. Seven footers were
  rewritten, adding 21 newly checked citations.
* **Every numbered result a problem set cites must be named in its lesson.**
  The coverage gate enforces this and caught it on six units. Where the
  reference is load-bearing the lesson now states it; where it was a basic
  definition dressed up as a citation ("by additivity of φ (la-05, Definition
  3.2)"), the number was dropped from the hint instead.

---

## 6. Verification

Run on the completed branch, with the book drive present.

| Check | Result |
|---|---|
| `citations` — 15 lessons | 639 citations checked, **0 wrong** |
| `citations` — 15 problem sets | 333 citations checked, **0 wrong** |
| `check_lesson_coverage` — 15 units | 214 refs checked, **0 missing** |
| `check_sections` — 31 la files | **0 wrong labels** |
| `gate` (4–6) — 15 lessons | 60/60 rows PASS, exit 0 |
| `lesson_lint` — 15 lessons | 15/15 each |
| `mission` (gate 8) — 15 lessons | verbatim, exit 0 |
| `check_id_consistency` | consistent |
| `validate_syllabus` | OK |
| `check_resources --shallow` | 145 units, 217 references, 0 wrong |
| `pytest` | 307 passed |
| `ruff check scripts/ tests/` | 1 pre-existing E702 in `tests/test_scheduler.py`, untouched by this branch |

`curriculum/syllabus.yaml` is not modified on this branch.
