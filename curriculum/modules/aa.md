# Module: Abstract Algebra (aa) — Semesters 1–2

**Primary text:** Aluffi, *Algebra: Notes from the Underground* — the whole arc,
ch. 1–12 (Core Texts folder; prefer `md\`, cite PDF pages). This module follows
Aluffi's own order — **rings → modules → abelian groups → groups** — rather than
a group-theory-first course, because that order is the honest road to the
mission.

**Mission link:** Persistent homology *is* module theory. Chain groups are
modules; a homology group is a quotient module (Z/B); the barcode of a
persistence module is its decomposition as a finitely generated module over a
PID. Aluffi builds exactly this machinery, and rehearses its keystone — the
**quotient + isomorphism theorems** — three times: for rings (ch. 5), modules
(§8.5), and groups (§11.5). By the time groups appear they are the *third*
category in which you have met kernels, quotients, and the first isomorphism
theorem, not the first.

**Spans:** Semester 1 (rings, ch. 1–7) into Semester 2 (modules and groups,
ch. 8–12). The DAG, not the semester label, drives progression; `semester: s1`
in syllabus.yaml marks where the strand starts.

**Support / visual layer:** Carter, *Visual Group Theory* and Macauley's VGT
playlist are retained **only for the groups portion** (aa-00, aa-23, aa-25),
where symmetry and Cayley diagrams give intuition Aluffi's compressed treatment
does not. Oxford M1 Groups & Group Actions notes support aa-23/aa-24. The rings
and modules units are Aluffi-only. Category theory is threaded through Aluffi's
"the category of —" sections (aa-07, aa-15, aa-23) and deepened later by the S3
`cat` module (Aluffi *Chapter 0*).

**Absorbs:** the former Semester-2 `rm` (Rings & Modules) stub — rings and
modules are now the first two-thirds of this module.

## Arc and unit map

**Rings (Part I, ch. 1–7): aa-01 … aa-14.** Integers and modular arithmetic as
the concrete on-ramp (the first quotient, Z/nZ, is aa-03); rings, the category
of rings, kernels/ideals/quotient rings and the isomorphism theorems (aa-09,
aa-10); integral domains, PIDs/UFDs, polynomial rings.

**Modules (Part II, ch. 8–9): aa-15 … aa-20.** Modules as vector spaces over a
ring; submodules, direct sums, **quotient modules** and the isomorphism theorems
(aa-16, aa-17) — homology, one abstraction early; free/finitely presented
modules; the **structure theorem for f.g. modules over a PID** (aa-20) — the
barcode theorem.

**Abelian groups (ch. 10): aa-21, aa-22.** As Z-modules; classification of
finitely generated abelian groups — the exact content of an integral homology
group (free rank = Betti number, plus torsion).

**Groups (Part III, ch. 11–12): aa-23 … aa-30.** Groups and their category,
actions, the group zoo, normality & quotient groups (aa-26), the isomorphism
theorems (aa-27), Lagrange & the class equation, Sylow, solvability.

| Unit | § | Unit | § |
|---|---|---|---|
| aa-00 symmetry *(optional)* | Carter/Macauley | aa-16 quotient modules | 8.3–8.4 |
| aa-01 integers | 1.1–1.2 | aa-17 module iso theorems | 8.5 |
| aa-02 gcd, FTA | 1.3–1.4 | aa-18 free modules | 9.1–9.2 |
| aa-03 quotients, Z/nZ | 2.1–2.2 | aa-19 f.g. / f.p. modules | 9.3–9.4 |
| aa-04 Z/nZ, Fermat, RSA | 2.3–2.5 | aa-20 structure theorem ★ | 9.5–9.6 |
| aa-05 rings | 3.1–3.2 | aa-21 abelian groups | 10.1–10.2 |
| aa-06 domains, fields | 3.3 | aa-22 f.g. abelian classification | 10.3–10.4 |
| aa-07 category of rings | 4.1–4.2 | aa-23 groups & category | 11.1 |
| aa-08 ring homomorphisms | 4.3–4.4 | aa-24 group actions | 11.2 |
| aa-09 ideals, quotient rings | 5.1–5.3 | aa-25 cyclic/dihedral/symmetric | 11.3 |
| aa-10 ring iso theorems, CRT | 5.4–5.7 | aa-26 normality, quotients | 11.4 |
| aa-11 prime/maximal ideals | 6.1–6.2 | aa-27 group iso theorems | 11.5 |
| aa-12 EDs, PIDs, UFDs | 6.3–6.5 | aa-28 Lagrange, class equation | 12.1–12.2 |
| aa-13 polynomial rings | 7.1–7.2 | aa-29 classification, Sylow | 12.3–12.5 |
| aa-14 irreducibility | 7.3–7.5 | aa-30 A_n simple, solvable | 12.6–12.7 |
| aa-15 modules | 8.1–8.2 | | |

## Teaching notes

- Name the spiral aloud: at aa-16 (quotient modules) and aa-26 (quotient
  groups), say explicitly "this is the same move as aa-09 (quotient rings) and
  la-09 (quotient spaces)." The single most mission-critical idea is quotient +
  first isomorphism theorem; it recurs in four categories (rings, modules,
  groups, vector spaces) and every recurrence should be flagged.
- aa-20 (structure theorem) is the module's summit for the mission — connect it
  out loud to persistence barcodes / interval decomposition (Oudot). Foreshadow
  it from aa-12 (PIDs) and la-12 (structure theorems for operators).
- The groups portion (aa-23 onward) is where the retained visual layer earns its
  place: draw Cayley diagrams, invoke aa-00's rectangle. Rings and modules stay
  Aluffi-native — do not reach for Carter there.
- Emphasise functoriality from aa-07/aa-08 (category of rings, homomorphisms)
  onward: "a homomorphism is a map that respects structure" as a recurring
  refrain, not a one-off definition.

## Assessment

- Unit mastery quizzes (SRS + 3–5 questions).
- Module problem sets: drawn primarily from Aluffi *Underground* exercises, plus
  Tripos IA-adapted problems; Carter/Macauley worksheet problems only as optional
  visual enrichment on the groups units. Graded per spec §7, 80% gate.

## Common misconceptions to watch (seed for learning-records)

- Quotient confusion across categories: treating R/I, M/N, G/H as unrelated when
  they are one construction. Name the analogy every time.
- "Ideal = subring" (an ideal need not contain 1; a subring need not absorb
  outside multiplication).
- Normality as commutativity (gH = Hg, not ab = ba).
- Module vs vector space: the difference only bites when the ring is not a field
  — torsion is the whole point (aa-20, aa-22), and it is exactly what
  field-coefficient homology throws away.
- "Isomorphic = equal" (a structure-preserving bijection, not literal identity).

**Text-structure note:** *Underground* is deliberately rings-first (Part I rings,
Part II modules, Part III groups, Part IV fields), threading the categorical
viewpoint throughout; Aluffi argues this order (rings → modules → abelian groups
→ groups) is the most natural first approach for an audience without prior
exposure. Fields and Galois theory (ch. 13–15) are out of scope for the TDA
mission — add just-in-time only if research demands. See
docs/specs/2026-07-22-abstract-algebra-restructure.md for the decision record.
