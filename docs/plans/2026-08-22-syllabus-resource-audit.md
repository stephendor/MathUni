# Syllabus resource audit — every unit names something that can be read

**Date:** 2026-08-22 · **Branch:** `s1-syllabus-audit` (off `main` at `de09ec2`)
**Scope:** all 145 units, 217 resource references, 15 books
**Preceded by:** `docs/plans/2026-08-21-s1-pw-content.md` §8 D-5

---

## 1. Why a resource line is not documentation

`citations.py` picks the book a unit's citations are checked against from that
unit's `resources:` line. So a line naming a source that is not on the machine
does not merely misdescribe the unit — it aims the verification gate at the
wrong book, or at no book at all, and in the second case the gate reports
nothing rather than reporting a problem.

The measured effect, over the fourteen units whose resource lines this branch
touches or which sit next to them:

| | citations checked | wrong |
|---|---|---|
| before | 223 | 74 |
| after | **379** | **63** |

Two distinct mechanisms are in there:

- **Six an2 units were checking zero citations.** `an2-02`, `-03`, `-04`,
  `-07`, `-08` and `-09` listed only `"Oxford M2 … notes"`, which resolves to
  no book, so `book_for_unit` returned `None` and the gate could not run. 156
  citations were invisible to every check in the repository. This is the
  silent-absence failure mode at the syllabus level: the units did not fail,
  they were never examined.
- **`an2-01` went from 25 wrong to 5.** Its line was
  `["Oxford M2 Metric Spaces notes", "Abbott 8.2 (or equiv.)"]` while its
  lesson is written from Lindström, so the gate resolved it to Abbott and
  reported 25 of 31 citations wrong. Twenty of those were the syllabus, not
  the citations.

**Correction to an earlier claim.** The `s1-pw` plan (§8 F-4) and PR #21 record
an2-01's failures as an artifact of the folio fit, on the grounds that
"Lindström fits −12 globally where `pull.py --folio` measures −13". That
diagnosis is wrong. Lindström's global fit is a single plateau at −13 over PDF
15–382, which is correct and agrees with the local measurement. The two PDF
candidates in the failure message (56 and 320) are *Abbott's* — one for the
text, one for its bound-in solutions manual — which is what gave the wrong book
away. The five remaining an2-01 failures are unexamined and belong to the an2
module's own branch.

## 2. The gate

`scripts/check_resources.py`, wired into CI, with 22 selftest controls and 13
pytest cases. Two checks:

1. **RESOLVES.** Every resource names a book in `resources/bookmap.json`, or is
   a member of a non-book class *declared for that module*. The classes are
   per-module, not global: `self-directed` is the whole pedagogy of `cap` and
   would mean "no source was ever identified" in `la`, and `cap` does not
   inherit `lab`'s software-documentation class. Controls assert both
   directions.
2. **PARTS EXIST.** Where a resource names chapters or sections of a book that
   is on this machine, those chapters and sections exist in it. A range names
   its ends and never its interior, for the same reason `citations.py` expands
   page ranges that way: inferring the middle invents claims nobody made.

Check 2 needs the page trees, so CI runs `--shallow` and the script *prints*
which books it skipped rather than passing them silently.

**What this gate cannot catch, stated so nobody assumes otherwise:** a
reference to the wrong chapter of the *right* book. `pw-04`'s "Cummings Real
Analysis ch. 1-2" passes check 2, because that book does have chapters 1 and 2
— they are simply not where functional limits live. Only a reader catches
that, or `citations.py` downstream once the book is right.

## 3. What changed, and why

**Result of the audit: 22 failures across 22 units, 14 distinct phantom
references. Zero check-2 failures** — every chapter and section number named
against a book we hold does exist. The defects are phantom sources and, in
four cases found by reading, real chapters of the right book that do not hold
the material.

### 3.1 Phantom sources dropped (a resolvable core text was already there)

| Unit | Dropped | Kept |
|---|---|---|
| pw-03 | `Schumacher` | Cummings ch. 3, 8 |
| an-02 | `Stillwell, Roads to Infinity` | Abbott 1.5-1.6 |
| at1-03, at1-07 | `Dexter algebraic_topology notes` | Hatcher 1.1 / 2.1 |
| at1-04 | `Stillwell` | Hatcher 1.1 |
| at2-01 | `Dexter algebraic_topology_iii notes` | Hatcher 3.1 |
| aa-00 | `Macauley VGT lecture 1` | Carter ch. 1-2 |
| cap-04 | `Expository Writing folder` | self-directed |

The Macauley lectures are the video course that accompanies Carter's *Visual
Group Theory*; the book is the citable artifact and is already listed. The
Expository Writing folder exists but is not relevant to this curriculum.

### 3.2 Phantom sources replaced with a core text

| Unit | Was | Now |
|---|---|---|
| an-14 Metric spaces bridge | `Oxford M2 notes` | Abbott 8.2, **Lindstrom ch. 3** |
| an2-01 Metric-space topology | `Oxford M2 Metric Spaces notes` | **Lindstrom 3.1-3.3**, Abbott 8.2 |
| an2-02 Completeness and completion | same | **Lindstrom 3.4, 3.7** |
| an2-03 Compactness, Arzelà-Ascoli | same | **Lindstrom 3.5-3.6, 4.8** |
| an2-04 Contraction mapping theorem | same | **Lindstrom 3.4, 4.7** |
| an2-05 Uniform convergence of derivatives | `Oxford M2 Analysis III notes` | Abbott 6.2-6.3, **Lindstrom 4.3** |
| an2-06 Series of functions, M-test | same | Abbott 6.4-6.7, **Lindstrom 4.4, 4.10-4.11** |
| an2-07 Normed and Banach spaces | same | **Lindstrom 5.1-5.2** |
| an2-08 Function spaces C[a,b] | same | **Lindstrom 4.5-4.6** |
| an2-09 Differentiation in Rⁿ | `Oxford M2 notes (multivariable)` | **Lindstrom 6.1, 6.6-6.8** |

Lindström, *Spaces: An Introduction to Real Analysis*, is a metric-spaces text
and covers all nine units. Offset **−13**, measured with `pull.py --folio` over
three ranges spanning the book (PDF 20–26, 56–62, 186–192), all constant.
Section map read off the extract and each assignment then verified mechanically
by check 2:

| | | |
|---|---|---|
| 3.1 Definitions and examples p. 43 | 4.3 Integrating and differentiating sequences p. 86 | 5.1 Normed spaces p. 133 |
| 3.4 Complete spaces p. 59 | 4.5 Spaces of bounded functions p. 99 | 5.2 Infinite sums and bases p. 140 |
| 3.5 Compact sets p. 63 | 4.6 Spaces of bounded, continuous functions p. 101 | 6.1 The derivative p. 174 |
| 3.7 Completion of a metric space p. 71 | 4.7 Applications to differential equations p. 103 | 6.6 Partial derivatives p. 201 |
| 4.4 Applications to power series p. 92 | 4.8 Compact sets of continuous functions p. 107 | 6.7 Inverse Function Theorem p. 206 |

Banach's Fixed Point Theorem is **Theorem 3.4.5**, printed p. 61 — which is why
an2-04 gets §3.4 as well as §4.7.

### 3.3 Wrong chapters of the right book (found by reading, not by the gate)

| Unit | Was | Now | Why |
|---|---|---|---|
| pw-04 Epsilon-delta craft | Cummings Real Analysis **ch. 1-2** | **ch. 6** | Functional limits and continuity are Ch. 6 (Definition 6.8 p. 226, Definition 6.16 p. 238). Ch. 1-2 are the reals. |
| pw-05 Proof style | `Cummings appendix` | **Cummings ch. 1-9 Pro-Tips** | This edition has no writing appendix; the proof-writing advice is nine per-chapter Pro-Tips sections, pp. 27, 65, 98, 145, 186, 208, 237, 275, 309. |
| aa-23 Subgroups and homomorphisms | Carter **ch. 1-2** | **ch. 6, 8** | Ch. 1-2 are symmetry and Cayley diagrams. Subgroups, cosets and Lagrange are §6.2-6.5; embeddings and the Fundamental Homomorphism Theorem are §8.1-8.2. |
| aa-24 Group actions | `Oxford M1 Groups and Group Actions` | **Carter ch. 9** | §9.1 is "Group actions". |
| aa-25 Cyclic, dihedral, symmetric, free | Carter **ch. 2-3** | **ch. 5** | §5.1 cyclic, §5.3 dihedral, §5.4 symmetric and alternating. Ch. 2-3 are Cayley diagrams and symmetry groups. |

`aa-23`, `aa-24` and `aa-25` are unwritten, so this costs nothing now and would
have cost a wrong read-back later. `aa-00` is written and its Carter chapters
were already correct.

## 4. Deliberately not changed

- **`lab`'s software documentation** (giotto-tda, GUDHI, Ripser, persim,
  scikit-learn, Kepler-Mapper) and the two papers it names. `lab` is a
  computational module; library docs are its correct primary sources and there
  is no book to point at. Declared as a class in the gate rather than
  exempted case by case.
- **`cap`'s `self-directed` and `tdlbook.org`.** A capstone whose sources were
  fixed in advance would not be a capstone.
- **`Abbott 8.2 (or equiv.)`.** The hedge is untidy but Abbott 8.2 exists and
  resolves; tightening the wording is cosmetic and this branch is not doing
  cosmetics to 145 lines.

## 5. Verification

```
check_resources.py --selftest        22/22
check_resources.py                   145 units, 217 references, 0 wrong
check_resources.py --shallow         0 wrong (the CI half)
validate_syllabus.py                 syllabus OK
check_id_consistency.py              unit ids consistent
pytest                               236 passed
ruff --preview                       clean on both new files
```

No lesson or problem set is touched by this branch. `syllabus.yaml` is the only
content file that changes, which is the whole point of doing it here: content
branches do not edit it.

## 6. Open

- **The five remaining `an2-01` citation failures**, and the 13 in an2-05 and
  18 in an2-06, are now visible for the first time and are unexamined. They
  belong to the an2 module's branch.
- **`citations.py`'s docstring on `s1-pw` carries the wrong diagnosis** of the
  an2-01 failures (§1 above). It is corrected on that branch in a follow-up
  commit rather than here, since this branch does not touch `scripts/citations.py`.
