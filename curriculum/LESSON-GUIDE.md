# Lesson Generation Guide (binding for every lesson)

A lesson serves ONE unit of syllabus.yaml and is a single self-contained
HTML file at `lessons/<module>/<unit>.html`, built from `lessons/_template.html`.

## Structure (in order, non-negotiable)
1. **Hook first.** `{{HOOK_HEADLINE}}` expands the unit's `hook` into 2-4
   sentences with a concrete, fun instance. Never open with a definition.
2. **Mission strip** — the unit's `mission_link`, one sentence.
3. **2–3 segments**, each wrapped in `<div class="segment">` opening with
   `<span class="timebox">Segment N · ~25 min</span>` and a title. Between
   segments insert `<div class="break">☕ Break — stand up, 5 minutes.</div>`.
4. **Faded worked examples** within segments: first example fully worked
   (`.worked`), second partially completed (`.worked.fade`, gaps marked
   "⟨your step⟩"), then a `.you-try` block the learner does solo.
5. **Self-checks**: 2–3 per segment (`.selfcheck` with 3-4 answer buttons,
   `onclick="check(this,true|false)"`, `data-ok` on the correct one, plus a
   `.explain` div giving WHY). Instant feedback, no page reload.
6. **Visual element**: at least one per lesson — a `<canvas>` with a short
   inline JS animation/diagram (≤60 lines) OR an inline SVG diagram where
   animation adds nothing. Geometry over decoration.
7. **Footer citations**: every definition/theorem cites book + section +
   PDF page(s), e.g. `Axler §1A, pp. 2–5`. Resolve paths via
   resources/bookmap.json; verify quotes against the book's markdown.md.

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
hook-first ✓ · mission strip ✓ · 2-3 timeboxed segments ✓ · break card ✓ ·
faded examples ✓ · ≥4 self-checks with explanations ✓ · visual ✓ ·
citations with pages ✓ · self-contained (zero external requests) ✓ ·
`python -c "from html.parser import HTMLParser; HTMLParser().feed(open(PATH,encoding='utf-8').read())"` runs clean ✓
