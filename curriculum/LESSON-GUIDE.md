# Lesson Generation Guide (binding for every lesson)

A lesson serves ONE unit of syllabus.yaml and is a single self-contained
HTML file at `lessons/<module>/<unit>.html`, built from `lessons/_template.html`.

## Structure (in order, non-negotiable)
1. **Hook first.** `{{HOOK_HEADLINE}}` expands the unit's `hook` into 2-4
   sentences with a concrete, fun instance. Never open with a definition.
   End the hook with a **prediction gate**: one question the learner must
   commit to (a self-check whose answer the lesson then reveals) BEFORE
   segment 1 — the brain learns from prediction error, so make it predict.
2. **Mission strip** — the unit's `mission_link`, one sentence.
3. **2–3 segments**, each wrapped in `<div class="segment">` opening with
   `<span class="timebox">Segment N · ~25 min</span>` and a title. Between
   segments insert `<div class="break">☕ Break — stand up, 5 minutes.</div>`.
4. **Faded worked examples** within segments: first example fully worked
   (`.worked`), second partially completed (`.worked.fade`, gaps marked
   "⟨your step⟩"), then a `.you-try` block the learner does solo. Every
   technique the unit's `problems/sets/<unit>.md` uses must be demonstrated
   by at least one worked or faded example — read the problem set before
   drafting examples, not after.
5. **Intermediate lemmas.** Any lemma-style fact the unit's problem set
   relies on that isn't a named theorem in the primary text (e.g. "a·0=0"
   as a sub-step, not itself Axler's Theorem 1.29) must be explicitly
   stated and proved in the lesson body — never left for the learner to
   invent cold during grading.
6. **Self-checks**: 2–3 per segment (`.selfcheck` with 3-4 answer buttons,
   `onclick="check(this,true|false)"`, `data-ok` on the correct one, plus a
   `.explain` div giving WHY). Instant feedback, no page reload.
7. **Guided proof.** At least one point per lesson, after the self-checks
   and distinct from them: a free-response prompt where the learner writes
   a short proof inline, followed by a revealed model answer for
   self-comparison. Not multiple choice — this is deliberate proof-writing
   practice, not recognition.
8. **Visual element**: at least one per lesson — a `<canvas>` with a short
   inline JS animation/diagram (≤60 lines) OR an inline SVG diagram where
   animation adds nothing. Geometry over decoration.
9. **Blank-page ending**: just before the footer, a short block asking the
   learner to close their eyes / look away and reconstruct the lesson's
   argument skeleton from nothing (the 2-3 load-bearing claims and why each
   forces the next), with a collapsed `<details>` reveal to check against.
   Free reconstruction beats re-reading; this is the lesson's exit ritual.
10. **Footer citations**: every definition/theorem cites book + section +
   PDF page(s), e.g. `Axler §1A, pp. 2–5`. Resolve paths via
   resources/bookmap.json; verify quotes against the book's markdown.md.

## Source discipline

The mathematics comes from the sections named in the unit's `resources`, read
from the text — never from recollection. If the source available to the writer
does not contain something the lesson needs, say so in place rather than
supplying it from memory or quietly routing around it:

When a sentence's main claim belongs to a numbered result, cite that result in
that sentence. A supporting result used in its proof gets its own sentence and
citation; do not put two result numbers on one folio and leave review to infer
which one supports the claim.

```html
<p class="gap">NOT IN SOURCE: the proof that the cover is good</p>
```

A marked gap is an honest, reviewable defect; an unsupported claim is an
invisible one. **A lesson is not committable while it still carries a gap
marker** — `lesson_lint.py` fails on one. Resolve it by finding the source,
rescoping the lesson, or using the rubric's reviewed outside-source exception:
add the footer declaration, supply the independent justification and a finite
exhaustive check where possible, and complete `MATHEMATICAL-CLAIM-REVIEW.md`.
Only then remove the marker. The marker exists so that a
generation run can report the hole instead of inventing a filler, which is
exactly what the drift test measures.

## Register
- Definitions verbatim-faithful to the primary text (cite); narration in
  your own voice: vivid, precise, never breathless. Aluffi/Stillwell is the
  style bar. British English.
- Content depth = the primary text's sections named in the unit's
  `resources`, scoped to ONE lecture-equivalent (the DAG's next units take
  the rest). State explicitly what is deferred and to which unit.
- MathML or Unicode maths (no external LaTeX/JS libraries; file must render
  offline).

## Checklist before committing a lesson
hook-first ✓ · prediction gate ✓ · mission strip ✓ · 2-3 timeboxed
segments ✓ · break card ✓ · faded examples ✓ · intermediate lemmas
stated ✓ · ≥4 self-checks with explanations ✓ · guided proof block ✓ ·
visual ✓ · blank-page ending ✓ ·
citations with pages ✓ · self-contained (zero external requests) ✓ ·
`python scripts/check_lesson_coverage.py <problem-set-path> <lesson-html-path>`
reports no missing theorem/definition references ✓ ·
`python -c "from html.parser import HTMLParser; HTMLParser().feed(open(PATH,encoding='utf-8').read())"` runs clean ✓
