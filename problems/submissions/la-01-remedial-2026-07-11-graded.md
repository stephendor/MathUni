# la-01 — Remedial grading (2026-07-11)

Targets: the three specific gaps from the 2026-07-10 grading (score 0.74) —
sign-slip verification (R1), justifying $a\cdot 0=0$ (R2), and the vacuous-truth
argument (R3). Marking stance: skeptic first, logic judged on its own merits.

---

## R1 — Verification discipline — **1.0 / 1.0**

- Solve: $3x=(-1,4,0,8)-(2,-5,3,-1)=(-3,9,-3,9)$, so $x=(-1,3,-1,3)$ — correct,
  no sign slip.
- Verification: substitutes back and checks **all four components explicitly**
  ($2+3(-1)=-1$, $-5+3(3)=4$, $3+3(-1)=0$, $-1+3(3)=8$) rather than asserting
  it works — exactly the discipline this problem targeted.

This closes the gap cleanly: the 2026-07-10 attempt never assembled a final
answer or checked it; this one does both.

## R2 — Justifying scalar-times-zero — **0.9 / 1.0**

Proof, checked step by step:
- $0=0+0$ (zero vector identity) — correct, used correctly.
- $a\cdot 0 = a(0+0) = a\cdot 0 + a\cdot 0$ — correct application of distributivity.
- Adds $-(a\cdot 0)$ to both sides, invokes associativity and additive inverse
  to reach $0 = a\cdot 0$ — logic is valid and mirrors Theorem 1.29's
  distribute-then-cancel structure, as asked.

**Docked 0.1**: the last step compresses two separate facts (associativity
regrouping the RHS, then additive-inverse/additive-identity collapsing it to
$a\cdot 0$) into "using associativity and the additive inverse property" —
same under-narration pattern flagged in the 2026-07-10 pw-01 and la-01
gradings. The logic is sound; the exposition still skips naming which
identity does which job in the final line.

## R3 — Vacuous truth — **1.0 / 1.0**

Correctly identifies that a universally-quantified clause over $V=\varnothing$
has no possible counterexample (nothing to instantiate $v$ with), and
correctly distinguishes this from the additive-identity clause, which asserts
*existence* of a specific element — a claim vacuous truth cannot satisfy
because there's nothing in $\varnothing$ to witness it. This is exactly the
"why the other seven axioms don't save it" argument that was skipped on
2026-07-10.

---

## Total: (1.0 + 0.9 + 1.0) / 3 = **0.97 / 1.0**

All three targeted gaps closed. This is a remedial score on the specific
failure points, not a full unit redo — recorded as the new best score for
la-01 (mastery.json), since the remedial set was purpose-built to retest
exactly what the original score dropped points on.

## What was genuinely good

- R1: full component-by-component substitution check, unprompted rigor
  exactly matching what was missing before.
- R2: correct choice of proof structure (distribute, then cancel), matching
  Theorem 1.29's style as instructed.
- R3: precisely separates "vacuously true" (universal, no counterexample)
  from "cannot be vacuously satisfied" (existential, needs a witness) — this
  distinction is the crux of the exercise and it's stated correctly.

## The gap that matters most

Under-narrating the final step of an equation chain (R2's "using associativity
and the additive inverse property" collapses two moves into one) — small, but
it's the third time this term the same compression has shown up (pw-01, and
la-01's original Problem 2 and Problem 3). Worth naming each identity/property
on its own line when a proof chain has more than one algebraic move packed
into a single step.
