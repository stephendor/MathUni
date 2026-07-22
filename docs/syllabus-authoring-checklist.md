# Syllabus-authoring pre-flight

The gate a semester-authoring run passes **before its PR**. It splits the failure
surface the way it actually splits: a **mechanical** half that `validate_syllabus.py`
enforces on every run, and a **semantic** half that no validator can judge — the
eyeball / second-model pass. As the material deepens (S3 →), the errors get
quieter and the checking gets more expensive; the point of this gate is to move
that cost onto the machine wherever it can go, and to make the human pass short
enough that it actually happens.

## 1. Mechanical — must be green

```bash
python scripts/validate_syllabus.py
```

Enforces: unique unit ids · every prereq resolves · **DAG acyclic** · all required
fields present and non-empty · **every resource resolves** to a `bookmap.json`
book or a registered source in `resources/resource_sources.json` · **no prereq
points forward into a later semester** (the common cross-module mis-wire).

Prove the two new gates can still fire (negative control — an always-green gate is
worthless):

```bash
python scripts/validate_syllabus.py --selftest
```

**Register sources before citing them.** A new book → add it to
`resources/bookmap.json`; a new non-book source (course notes, tool docs, a paper)
→ add its prefix to `resources/resource_sources.json`. An unregistered citation
fails the build. That failure *is* the anti-hallucination catch — do not work
around it by loosening a prefix; add the real source.

## 2. Semantic — eyeball / second-model (the validator cannot judge these)

For every new unit:

1. **§-pins are real and right.** Open the **actual text TOC** (bookmap `md\` /
   `pages\`), not memory. Confirm the cited chapter/section exists *and* covers
   the unit's topic. This is the first thing that breaks on non-linear texts
   (Hatcher, Dey–Wang, research monographs) — pin against the page, cite the page.
2. **Each prereq is a TRUE dependency.** Would the lesson genuinely stall without
   it? Cut decorative edges; add the cross-strand edge the content actually needs.
3. **Mission-link is honest AND correct.** From S3 on, the mission-link stops
   being a slogan and becomes a mathematical claim (this *is* homology; that *is*
   the barcode). Verify it like a proof line, not a tagline. No overclaiming.
4. **Hook is concrete and specific to THIS unit** — one idea, prediction-inviting,
   not a generic gesture that would fit any unit in the module.
5. **No silent overlap.** Does another module already cover this? Name the
   boundary out loud (e.g. `tda1` theory vs `lab` computation; `cat` vs `aa`'s
   "category of —" thread). Record it in the module doc.

## 3. Module doc

Each new module gets `curriculum/modules/<id>.md` in the `aa`/`la`/`top` pattern:
mission link, arc + unit map (with §-pins), teaching notes, common misconceptions.
State what it **absorbs** and where it **hands off**.

## 4. State + sign-off

- [ ] `validate_syllabus.py` green · `--selftest` green
- [ ] every §-pin checked against the text TOC (not memory)
- [ ] every prereq edge justified · every mission-link verified as a claim
- [ ] no silent overlap with an existing module
- [ ] module doc(s) written
- [ ] `progress.json` updated — new units `locked` unless a prereq is already
      mastered; keys still == syllabus units; no premature unlocks
- [ ] `build_dashboard.py` renders the new module bars

> Companion gate: this pre-flight gates the **authoring** of units;
> `curriculum/LESSON-RUBRIC.md` gates the **generation of lessons** for those
> units. Different steps, same philosophy — a scored gate in place of vigilance.
