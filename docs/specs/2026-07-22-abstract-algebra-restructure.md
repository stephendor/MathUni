# Decision record: Group Theory → Abstract Algebra (Aluffi *Underground*)

**Date:** 2026-07-22
**Status:** Applied
**Supersedes (in part):** the Semester-1 `gt` module and the Semester-2 `rm`
stub in the 2026-07-03 design spec. That spec is left intact as the historical
record; this note carries the current decision.

## Problem

The Semester-1 `gt` module was a **standard group-theory course** (symmetry →
groups → subgroups → quotients → actions). An earlier pass this same day
switched its lead text to Aluffi *Notes from the Underground* but only mapped
Aluffi's section numbers onto that group-first skeleton — which fights the book.
*Underground* is deliberately **rings → modules → abelian groups → groups →
fields**, threading "the category of —" throughout, so it leads smoothly into
modules and category theory.

## Decision

Replace the group-theory course with **one continuous `Abstract Algebra` module
(`aa`)** that follows Aluffi's own arc across *Underground* ch. 1–12. Full
coverage of Parts I–III (Sylow and solvable groups included). Fields and Galois
(ch. 13–15) stay out of scope for the TDA mission (add just-in-time only if
research demands).

Chosen among the alternatives considered: a single continuous module (this),
an AA-I / AA-II split, and three finer Rings/Modules/Groups modules. The
single-module choice keeps the whole algebra spine in one DAG.

## Why this serves the mission (persistent homology)

- Module **quotients + isomorphism theorems** (§8.4–8.5) *are* homology.
- The **structure theorem for f.g. modules over a PID** (§9.5) is the algebra
  behind **persistence-module / barcode decomposition** (cf. Oudot,
  *Persistence Theory: From Quiver Representations*, already on the shelf).
- Aluffi rehearses **kernel → quotient → first isomorphism theorem three times**
  — rings (ch. 5), modules (§8.5), groups (§11.5) — so by the time groups arrive
  the single most mission-critical construction is already familiar in three
  categories (four, counting quotient vector spaces in la-09).

## Structure changes

- **New module `aa`** (semester label `s1`, spans into `s2`): 31 units, aa-00
  (optional) + aa-01 … aa-30. Primary text Aluffi *Underground* ch. 1–12.
- **Removed:** `gt` module and units gt-01 … gt-12.
- **Absorbed:** the `rm` (Rings & Modules, S2) stub — rings + modules are now
  the first two-thirds of `aa`.
- **Kept:** `cat` (Category Theory, S3, Aluffi *Chapter 0*) as the categorical
  deepening; it now builds on the "category of —" fluency developed in `aa`.
- **Visual layer:** Carter / Macauley retained for the **groups units only**
  (aa-00, aa-23, aa-25). Rings and modules units are Aluffi-native.
- **Migrated:** the studied gt-01 → **aa-00**, an optional prereq-free "why
  algebra?" motivation aside (lesson, problem set, solutions, learning record,
  progress key, and SRS cards moved). gt-02 **retired** (its group-axioms
  content is now aa-23; its 8 SRS cards re-pointed to aa-23).

## Unit → Aluffi section map

Rings (Part I): aa-01 §1.1–1.2 · aa-02 §1.3–1.4 · aa-03 §2.1–2.2 · aa-04
§2.3–2.5 · aa-05 §3.1–3.2 · aa-06 §3.3 · aa-07 §4.1–4.2 · aa-08 §4.3–4.4 ·
aa-09 §5.1–5.3 · aa-10 §5.4–5.7 · aa-11 §6.1–6.2 · aa-12 §6.3–6.5 · aa-13
§7.1–7.2 · aa-14 §7.3–7.5.

Modules (Part II): aa-15 §8.1–8.2 · aa-16 §8.3–8.4 · aa-17 §8.5 · aa-18
§9.1–9.2 · aa-19 §9.3–9.4 · **aa-20 §9.5–9.6 (structure theorem = barcodes)**.

Abelian groups (ch. 10): aa-21 §10.1–10.2 · aa-22 §10.3–10.4.

Groups (Part III): aa-23 §11.1 · aa-24 §11.2 · aa-25 §11.3 · aa-26 §11.4 ·
aa-27 §11.5 · aa-28 §12.1–12.2 · aa-29 §12.3–12.5 · aa-30 §12.6–12.7.

## Not done here (deliberate)

- No lesson HTML / problem sets generated — they build lazily via `/lecture`
  from the new syllabus (token-conscious; generation batches weekly).
- Fields/Galois (ch. 13–15) excluded.
- The la/an/pw strands are unchanged except for new prerequisite edges *into*
  `aa` (aa-01←pw-01, aa-03←pw-03, aa-15←la-05, aa-20←la-07).

## Verification performed

`python scripts/validate_syllabus.py` → `syllabus OK`; 31 `aa` units, no stray
`gt`; `progress.json` migrated (aa-00 in-progress, aa-01 unlocked, mastered
units preserved); SRS JSON re-points cleanly to aa-00 / aa-23.
