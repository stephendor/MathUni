# la-01 — Remedial set (2026-07-10)

Targets the specific gaps from the 2026-07-10 grading (score 0.74), not a
full redo. Sources: Axler §1.A–1.B (as la-01).

---

## R1 — Verification discipline (closes Problem 1's sign slip)

Solve for $x \in \mathbb{R}^4$:
$$(2,-5,3,-1) + 3x = (-1, 4, 0, 8).$$

Then **substitute your answer back into the original equation** and show
each component checks out. (The 2026-07-10 attempt at a similar problem
had a sign error in one component that a check would have caught — build
the habit of always verifying before declaring the answer final.)

---

## R2 — Justifying scalar-times-zero (closes Problem 3's gap)

Prove that $a \cdot 0 = 0$ for every scalar $a \in \mathbb{F}$ (where the
$0$ on both sides is the zero *vector*). Do not just assert it — use the
same style of argument as Theorem 1.29's proof that $0v = 0$ (distributivity,
then cancel).

*(This is exactly the fact you asserted without proof when justifying
$a^{-1}\cdot 0 = 0$ in Problem 3 — closing this gap directly.)*

---

## R3 — Vacuous truth (closes Problem 4's gap)

Definition 1.19 has eight clauses, each of the form "for all $v \in V$ (and
$u,w\in V$, $a,b\in\mathbb{F}$), [property] holds" — except the additive
identity clause, which is existential ("there exists $0 \in V$ such
that…"). For $V = \varnothing$: explain, in one or two sentences, *why*
every universally-quantified clause is automatically true, and why this
reasoning cannot rescue the one existential clause. (This is the half of
Problem 4 that was skipped — the "why do the other seven axioms not save
it" argument.)
