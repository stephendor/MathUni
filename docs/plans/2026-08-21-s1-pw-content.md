# S1 · Proof Workshop (`pw`) — content plan

**Date:** 2026-08-21 · **Branch:** `s1-pw` (off `s1-gate-promotion`, see §6)
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
| pw-02 | Induction, strong induction, well-ordering | **L P** | pre-existing; **5 wrong citations open** (§3) |
| pw-03 | Sets, functions, images and preimages | **L** | **no problem set**; fails gate 8; to re-author |
| pw-04 | Epsilon-delta craft | **—** | unwritten |
| pw-05 | Proof style: writing and critiquing | **—** | unwritten |

Two of five are effectively done, one is half-built and needs re-authoring, and
two are unwritten. `pw-03` is the only unit in the whole repository with a
lesson and no problem set.

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

### Open — pw-02, five citations

Not repaired here: `pw-02` is a unit of this module and gets a full read-back
when its turn comes, not a sed pass.

| Where | Cited | Status |
|---|---|---|
| set, l. 14 | Exercise 4.1, p. 143 | not on p. 143 |
| set, l. 35 | Exercise 4.7, p. 144 | not on p. 144 |
| set, l. 56 | Exercise 4.12, pp. 131–133, 144 | not in that range |
| set, l. 77 | Theorem 4.8, pp. 126–127 | not on those pages |
| lesson, l. 196 | Theorem 4.8, pp. 126–127 | same, in the lesson |

Theorem 4.8 is the fundamental theorem of arithmetic, cited from `pw-01`'s
chapter-7 footnote as proved by strong induction — so it is genuinely a `pw-02`
result and only the page is wrong.

### Open — pw-03, one citation

`Definition 3.9` cited across pp. 82, 84, 252–253, 280–281 and not found. To be
resolved when `pw-03` is re-authored; §3.4 "Set Operations" begins at p. 82, so
the definition is nearby and the page is probably off by a small amount.

## 4. Gate 8

`pw-03` is on `curriculum/mission-drift.txt` (Class A, content divergence): its
lesson opens "continuity in topology is defined entirely via preimages — not
images. By the end of today you'll see in your bones why that's the only sane
choice", where the syllabus strip is "Continuity in topology is defined
entirely via preimages." The syllabus sentence is a prefix of the lesson's, so
the repair is to quote it and let the rest of the paragraph carry the flourish.
`pw-03` comes off the drift list when it is re-authored. `pw-01` and `pw-02`
pass gate 8 already.

## 5. Per-unit procedure

As `docs/plans/2026-08-11-s2-content.md §Per-unit procedure`, with one change:
step 5's source read-back keeps modality (`proves` / `states` /
`sets-as-exercise` / `disclaims` / `applies`) and whether the page supports the
*claim*, and hands the mechanical half to the gate:

```bash
python scripts/citations.py --unit <u>
```

That split is deliberate. The manual read-back on `pw-01` found six defects and
missed a seventh that the gate found on a file already read twice.

## 6. Branch base — needs sequencing

This branch is cut from `s1-gate-promotion`, not from `main`, because the gates
these units are held to live there and PR #20 has not merged. CI's
`pr-base-policy` requires every PR to target `main`, so a stacked PR is not
possible: **PR #20 must merge before `pw` can open a PR.** Once it does, this
branch rebases onto `main` and its diff is `pw` content alone.

## 7. Open decisions

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
