# Lesson generation — handoff & drift-test procedure

**Goal.** Decide whether a cheaper model (e.g. Gemini Flash vs Pro tier) can
generate the ~55 pending S1 lessons at the LESSON-GUIDE standard, *before*
committing tokens to the full run. Method: prove it on one held-out unit, then a
small archetype batch, then the rest — each stage gated on `curriculum/LESSON-RUBRIC.md`.

Two variables are under test, keep them separate:
1. **Spec portability** — is `LESSON-GUIDE.md` + an exemplar enough to carry the standard to another model?
2. **Model capability** — is the cheap tier strong enough to execute it?

If output is weak, run the *same prompt* through a stronger tier first. If the
strong tier holds and the cheap one doesn't, it's a **model** limit. If neither
holds, tighten the **spec** and retry before blaming the model.

---

## Inputs the generator MUST receive (per unit)

Missing any of these and the model will hallucinate maths or drift on form:

1. `curriculum/LESSON-GUIDE.md` — the binding spec.
2. `curriculum/LESSON-RUBRIC.md` — tell it the exact criteria it will be graded on.
3. `lessons/_template.html` — the HTML skeleton to fill.
4. **Exemplar lesson(s)** — 1–2 known-good Opus lessons as few-shot gold standard.
   *Use a lesson on DIFFERENT content from the target* so the answer isn't leaked.
5. The target unit's **syllabus entry** (id, title, hook, mission_link, resources) from `curriculum/syllabus.yaml`.
6. The target unit's **problem set** `problems/sets/<u>.md` — the lesson must demonstrate every technique it uses and contain every theorem/def id it names (Gate 0.1).
7. **Primary-text source text** — the actual book section(s) named in `resources`, so statements/proofs are correct and citations are real. Resolve the book + pages via `resources/bookmap.json` / `resources/RESOURCES.md` and paste the relevant markdown.

**Output contract:** a single self-contained HTML file at `lessons/<m>/<u>.html`,
zero external requests, MathML/Unicode maths only (no LaTeX/JS libraries).

---

## Generation prompt (template)

> You are writing one self-contained HTML lesson for a mathematics self-study
> system. Follow **LESSON-GUIDE.md exactly** — every item in its Structure list
> is non-negotiable and in order. You will be graded against **LESSON-RUBRIC.md**
> (attached); a single mathematical error fails the lesson outright, so verify
> every statement and proof against the attached source text and cite book +
> section + page in the footer. Match the depth, register (British English,
> Aluffi/Stillwell voice), and scaffolding of the attached exemplar lesson(s).
> Fill the attached `_template.html`. Demonstrate every technique used by the
> attached problem set, and ensure every theorem/definition the problem set
> names appears in your lesson. Output only the complete HTML file.
>
> [attach: LESSON-GUIDE.md · LESSON-RUBRIC.md · _template.html · exemplar(s) ·
>  syllabus entry · problem set · source-text markdown]

---

## Stage 1 — Reference A/B (do this first)

Isolates the variables on a unit already built to standard.

- **Target:** regenerate `aa-01` (proof-heavy: has a guided proof, faded examples, *and* a canvas visual — maximum surface to drift on). Its problem set and syllabus entry already exist.
- **Exemplar (few-shot):** `lessons/an/an-03.html` — proof-heavy, Opus-built, *different content* (avoid `pw-02`, which overlaps aa-01's induction/well-ordering and would leak).
- **Held-out reference for scoring:** the committed `lessons/aa/aa-01.html` — do **not** show it to the generator.
- **Run twice:** once on the **cheap tier**, once on the **strong tier** (same prompt). The cheap tier is the real economic question; the strong tier tells you whether a failure is spec or model.

**Before sending back to me, run the free pre-filter (Gate 0.1–0.2):**
```
python scripts/check_lesson_coverage.py problems/sets/aa-01.md <candidate>.html
python -c "from html.parser import HTMLParser; HTMLParser().feed(open('<candidate>.html',encoding='utf-8').read())"
```
Bounce anything that fails straight back to the generator — no need to spend a review on it.

**Bring back to me:** both candidate HTML files (name them e.g. `aa-01.flash.html`,
`aa-01.pro.html`). I score each against `LESSON-RUBRIC.md` **head-to-head with the
held-out reference**, reading the per-row delta. Output: a filled scorecard per
candidate + a drift verdict (ACCEPT / REVISE / REJECT) and, if REVISE, exactly which rubric rows regressed.

**Decision gate:** proceed to Stage 2 only with a tier that scored ACCEPT. If only
the strong tier passes, the economics change — that's a real finding, decide then.

---

## Stage 2 — Archetype batch (~3–5 units)

Confirms Stage 1 wasn't a lucky unit. Pick units spanning the archetypes:

- **Computational/procedural** — e.g. `la-03` (span/independence) or `an-04` (monotone convergence).
- **Proof-heavy/abstract** — e.g. `an-08` (compactness, Heine–Borel) or `aa-10` (iso theorems for rings).
- **Conceptual/definitional** — e.g. `aa-05` (rings: definition) or `la-05` (linear maps).

For units whose problem set doesn't exist yet, generate **problem set first, then
lesson** (the coverage gate checks lesson ⊇ problem-set refs, and the guide says
read the set before drafting examples). Score every candidate on the rubric.

**Decision gate:** all archetypes ACCEPT ⇒ green-light the full run. Any REJECT ⇒
diagnose (spec vs model vs archetype) before scaling.

---

## Stage 3 — Full run (remaining pending lessons)

The 55 pending S1 lessons (pw 2 · la 13 · an 11 · aa 29). Per unit, the pipeline is:

1. problem set → 2. lesson → 3. Gate 0 pre-filter (coverage + parse) → 4. rubric score → 5. commit only on ACCEPT.

Feed each committed lesson as a fresh exemplar candidate to keep the gold-standard
pool current. Batch by module so a systematic drift in one strand is caught early,
not at unit 55.

> **Why staged and not big-bang:** 55 subtly-broken lessons each cost a full review
> to catch; that can exceed the generation saving. The gates make the review cheap
> (Gate 0 is free, Gates 1–3 are a scorecard) and catch drift at unit 1, not unit 55.
