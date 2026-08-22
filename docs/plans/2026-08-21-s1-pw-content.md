# S1 · Proof Workshop (`pw`) — content plan

**Date:** 2026-08-21, completed 2026-08-22 · **Branch:** `s1-pw` (cut off
`s1-gate-promotion`; merged onto `main` after PR #20 landed, see §6)
**Module:** 5 units · **Primary text:** Cummings, *Proofs: A Long-Form
Mathematics Textbook*
**Preceded by:** `docs/plans/2026-08-21-s1-gate-promotion.md`

`pw` is the smallest S1 module and the one that gates the semester
pedagogically: `pw-01`'s three proof shapes are the moves every later unit
assumes. `pw-04` additionally depends on `an-03`, which already exists, so all
five units are unblocked in DAG order.

---

## 1. Tracker

`—` not started · `P` problem set · `L` lesson · `G` gates green · `✓` done

| Unit | Title | State | Note |
|---|---|---|---|
| pw-01 | Direct proof, contrapositive, contradiction | **✓** | pre-existing; 7 citations repaired (§3) |
| pw-02 | Induction, strong induction, well-ordering | **✓** | pre-existing; 5 wrong citations repaired, header rewritten (§3) |
| pw-03 | Sets, functions, images and preimages | **✓** | mission strip repaired and struck from the drift list; 3 citations fixed; **problem set written** (§4) |
| pw-04 | Epsilon-delta craft | **✓** | written this branch, lesson and set |
| pw-05 | Proof style: writing and critiquing | **✓** | written this branch, lesson and set |

## 2. Verified source data

**Cummings offset −4, constant across PDF 5–330** — established with
`scripts/pull.py --folio` on a local run and a distant chapter, with every page
in both ranges carrying a folio. `printed = PDF − 4`.

Section-start map (printed folios), from a heading sweep of the page tree:

| | | | |
|---|---|---|---|
| 1.1 Chessboard Problems 1 | 2.1 Working From Definitions 36 | 4.1 Dominoes, Ladders and Chips 107 | 7.1 Two Warm-Up Examples 215 |
| 1.3 Pigeonhole 11 | 2.2 Proofs by Cases 41 | 4.2 Examples 109 | 7.2 Examples 218 |
| 3.1 Definitions 73 | 2.3 Divisibility 42 | 4.3 Strong Induction 124 | 7.3 The Most Famous Proof 219 |
| 3.2 Proving A ⊆ B 77 | 2.4 Greatest Common Divisors 46 | 4.4 Non-Examples 133 | 7.4 The Pythagoreans 223 |
| 3.4 Set Operations 82 | 5.3 Quantifiers and Negations 167 | 6.1 Finding the Contrapositive 199 | 8.2 Injections, Surjections 251 |
| 3.5 Two Final Topics 91 | 5.4 Proving Quantified Stmts 174 | 6.2 Proofs Using the Contrapositive 200 | 8.4 Invertibility 266 |

**Chapter exercises sit at the END of each chapter, not beside the section.**
Chapter 2's begin at printed p. 68. This is the single largest source of the
citation errors in §3: four of them attribute an exercise to the section whose
material it drills.

## 3. Source-boundary findings — citations

`scripts/citations.py` (built this branch; see the gate-promotion plan's D-2,
now closed) checks that a cited printed page carries the result it names.

### Repaired here — pw-01, seven citations

| Where | Cited | Actually |
|---|---|---|
| set, Problem 1 | §2.2, Exercise 2.1, p. 43 | Exercise **2.5(a)**, p. **69** — and Cummings sets it for *every* integer, not only odd |
| set, Problem 2 | §2.2, Exercise 2.6, p. 43 | Exercise 2.6, p. **69**, in the chapter Exercises |
| set, Problem 5 | §7.3, Theorem 7.6 | §**7.4** — §7.3 ends at p. 222 |
| set, Problem 5 | "the lemma if 2∣k² then 2∣k" | **Lemma 2.17 part (iii)**, which Cummings names |
| set, Problem 6 | "composed" | **Proposition 7.2, p. 216**, proved there |
| lesson, footer | Prop 2.7, pp. 41–43 | pp. 41–**42**; p. 43 is §2.3 |
| lesson, l. 89 | §2.2, Exercise 2.1, p. 43 | Exercise 2.5(a), p. 69 — **missed by two manual read-backs, found by the gate** |

Printed p. 43 is Definition 2.8, divisibility. It appears three times in a unit
that never cites divisibility.

### Repaired — pw-02, five citations plus its header

Repaired 2026-08-22 with a full read-back, not a sed pass. Every page below was
read in the extract before the edit.

| Where | Cited | Status |
|---|---|---|
| set, l. 14 | Exercise 4.1, p. 143 | Exercise 4.1 is on p. **148** |
| set, l. 35 | Exercise 4.7, p. 144 | p. **149** |
| set, l. 56 | Exercise 4.12, pp. 131–133, 144 | Exercise 4.12 p. **149**; Proposition 4.10 runs **131–132**, §4.4 starts at 133 |
| set, l. 77 | Theorem 4.8, pp. 126–127 | statement on **125**, proof 126–127, so **125–127** |
| lesson, l. 196 | Theorem 4.8, pp. 126–127 | same repair |
| set, header | "§4 Exercises (4.1, 4.7, 4.12), pp. 143–145" | **pp. 148–149**, and written with kind words so the gate can see it at all |

Theorem 4.8 is the fundamental theorem of arithmetic, cited from `pw-01`'s
chapter-7 footnote as proved by strong induction — so it is genuinely a `pw-02`
result and only the page is wrong.

### Repaired — pw-03, three citations

| Where | Cited | Actually |
|---|---|---|
| footer | Definition 3.9 (complement) p. 84 | p. **83**, and it defines subtraction *and* complement |
| footer + body | Definition 8.3 (injective) inside pp. 252–253 | p. **251**; the equivalent form is on 252 |
| footer | Definition 8.5 / 8.7 both at p. 253 | 8.5 on **252**, 8.7 on 253 |

`pw-03` did **not** need re-authoring. The drift file records it as predating
every S2 convention; that is true of its mission strip and false of its body,
which already carries segments with timeboxes, a prediction gate, faded
examples, a you-try, a guided proof, seven self-checks, an SVG and a
blank-page ritual. Replacing a working artifact was not the assigned work
(the same judgement as pw-01's parked draft, §7 D-3), so the repairs above are
targeted and the lesson is otherwise untouched.

## 4. Gate 8 — pw-03 is off the drift list

`pw-03`'s lesson opened "continuity in topology is defined entirely via
preimages — not images. By the end of today you'll see in your bones why
that's the only sane choice", where the syllabus strip is "Continuity in
topology is defined entirely via preimages." The syllabus sentence was a
prefix of the lesson's, so the repair was to quote it exactly and move the
flourish to the paragraph below — the strip is a quotation, and prettifying or
extending a quotation is editing it.

`pw-03` is struck from `curriculum/mission-drift.txt`, which goes from 15
entries to 14. Worth recording: the ratchet's **stale** rule fired on the
repair before the strike, printing `STALE pw-03 passes now — strike it from
curriculum/mission-drift.txt` and exiting 1. That is the first time that rule
has run against a real repair rather than a synthetic control.

All five `pw` units now pass gate 8 on their own.

## 5. Written this branch — pw-04 and pw-05

Both units were unwritten; both now have a lesson and a five-problem set, and
both are green on gates 4-6, `lesson_lint` 15/15, gate 8, coverage and
citations.

**pw-04, Epsilon-delta craft.** Positioned against `an-03`, which already
covers the ε–N definition, the Algebraic Limit Theorem and the Order Limit
Theorem — so pw-04 is the *craft* and the ε–δ half that an-03 does not reach:
quantifier order as order of play, the reversed-quantifier diagnostic
(Abbott's "vercongence", which is boundedness wearing convergence's syntax),
the Scratch Work / Proof discipline taken from Cummings's own two-phase
examples, the min-trick for non-linear f, and continuity as the same game with
L pinned to f(c). Sources read: Abbott Definition 2.2.3 p. 39 and Exercises
2.2.2 p. 43, 2.2.7 p. 44; Cummings *Real Analysis* Definition 6.8 p. 226,
Examples 6.9 p. 231 and 6.10 p. 232, Definition 6.16 p. 238, chapter exercises
6.1, 6.2, 6.3, 6.5 p. 270.

**pw-05, Proof style: writing and critiquing.** Built around the syllabus
hook: a flawed proof of a true theorem carrying exactly five planted errors,
graded in Segment 2. Four of the five are failures to declare, name or
discharge something and are visible without arithmetic; one makes a written
line false while leaving the conclusion true, so it has no downstream trace.
Segment 3 is Cummings's asymmetry — a direct proof has one target and a slip
leaves you visibly short of it, a contradiction proof accepts any falsehood at
all, so a slip can manufacture its own contradiction and end looking like a
success.

## 6. Per-unit procedure

As `docs/plans/2026-08-11-s2-content.md §Per-unit procedure`, with one change:
step 5's source read-back keeps modality (`proves` / `states` /
`sets-as-exercise` / `disclaims` / `applies`) and whether the page supports the
*claim*, and hands the mechanical half to the gate:

```bash
python scripts/citations.py --unit <u>
```

That split is deliberate. The manual read-back on `pw-01` found six defects and
missed a seventh that the gate found on a file already read twice.

## 7. Branch base — resolved

This branch was cut from `s1-gate-promotion` because the gates these units are
held to lived there and PR #20 was open. CI's `pr-base-policy` requires every
PR to target `main`, so a stacked PR was impossible and `pw` could not open one
until #20 merged. #20 merged on 2026-08-22 as `de09ec2`; `main` is merged into
this branch and its diff is now `pw` content plus the citation-gate work in §8.

## 8. Open decisions and new findings

- **D-3.** `pw-01`'s pre-existing problem set has **six** problems where the
  house convention is five. A rewritten five-problem draft built from a fresh
  extract is parked at the session scratchpad as `pw-01-draft.md`; it is
  stronger on method-choice (the unit's actual hook) but replacing a working,
  gate-green artifact wholesale is not obviously the right call. **Recommend:**
  keep the repaired six-problem set, and fold the draft's Problem 4
  (choosing between the three methods) in as a replacement for its weakest
  item. Not done here — it is a content judgement, not a defect.
- **D-4.** 15 citations name a kind word the book does not use — 14 of them
  Axler results called "Theorem" where Axler prints only a number and a title
  ("1.34 Conditions for a subspace"). Harmless as mathematics and standard as
  practice, but it means a reader cannot search the book for the string we
  printed. `citations.py` reports these as WARN. **Recommend:** leave them, and
  keep the warning, rather than inventing a convention mid-semester.

- **D-5 (new).** Two syllabus resource lines point at material that does not
  exist as described, and both are recorded in the relevant lesson footer
  rather than silently worked around:
  - `pw-04` lists "Cummings Real Analysis ch. 1-2". Sequences are Ch. 3 in that
    book and functional limits and continuity are Ch. 6; the pages cited are
    the ones actually read.
  - `pw-05` lists "Cummings appendix" and an "Expository Writing folder". This
    edition of Cummings has no writing appendix — its proof-writing advice is
    distributed across nine per-chapter Pro-Tips sections (pp. 27, 65, 98, 145,
    186, 208, 237, 275, 309) — and no Expository Writing resource exists in
    `resources/bookmap.json`. **Recommend:** correct the two resource lines in
    `syllabus.yaml` on a separate branch; content branches do not edit it.

- **F-2 (new, source).** Cummings's own back-reference on printed p. 130 calls
  the chocolate-bar result "Proposition 4.10". It is Proposition 4.9; 4.10 is
  the 2a+5b proposition on p. 131. A book's cross-reference is not evidence
  about a number — read the number off the page where the result is stated.

- **F-3 (new, source).** Cummings's Fact 2.1 (p. 36) asserts that every integer
  is even *or* odd — at least one parity, not at most one. Proofs that end "so
  n² is both even and odd, contradiction" need the exclusivity, which comes
  from the uniqueness clause of Theorem 2.11, the division algorithm (p. 46).
  This is now the subject of pw-05's Error 4 and Problem 2 rather than a
  footnote, because the gap is exactly the kind that "clearly" hides.

- **F-4 (new, gate).** Using the citation gate on this module found four ways
  a citation was going unchecked entirely, all of them silent-absence rather
  than wrong verdicts, and one of them covering 190 citations corpus-wide. See
  the commit `citations: four ways a citation was going unchecked`. The gate
  now sees 2261 citations across the 90 lessons where it previously saw a
  fraction of that. Its corpus-wide failure count is **not** a defect count,
  and the largest contaminant is not in the script: it is the unit's
  `resources:` line, which is what picks the book to check against. an2-01
  named Oxford notes and Abbott while its lesson is written from Lindström, so
  the gate resolved it to Abbott and called 25 of 31 citations wrong; pointed
  at Lindström the same file reports 5. Six other an2 units named only a
  source that resolves to nothing, so the gate could not run on them at all.
  Repaired on `s1-syllabus-audit`, with `scripts/check_resources.py` as the
  gate. **Correction:** this entry previously blamed the folio fit — "Lindström
  fits −12 globally, −13 locally". That was wrong; the global fit is a single
  plateau at −13 and agrees with the local measurement. The two PDF candidates
  in the failure line were Abbott's, one for the text and one for its bound-in
  solutions manual, which is what gave the wrong book away.
