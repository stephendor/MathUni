---
name: lecture
description: Open or generate the interactive lesson for a syllabus unit. Use for /lecture <unit-id>, "teach me <topic>", or when /today reaches a lecture slot.
---

# /lecture <unit-id> — deliver one lesson

1. **Resolve the unit** in curriculum/syllabus.yaml (fuzzy-match titles if
   given a topic, confirm with Stephen). Check prereqs in
   state/progress.json: if any prereq is `locked`/`unlocked` (i.e. not yet
   studied), warn and offer it instead — never hard-block (ADHD: gentle).
4. **Serve or generate**:
   - If lessons/<module>/<unit>.html exists: open it via PowerShell
     `Start-Process` with the **absolute** path, e.g.
     `Start-Process "C:\Users\steph\MathUni\lessons\<module>\<unit>.html"`
     (relative paths via `cmd /c start` from the bash shell are unreliable —
     use the absolute-path PowerShell form every time), and run the live layer.
   - If missing: generate it FIRST, following curriculum/LESSON-GUIDE.md
     exactly (template lessons/_template.html; sources via
     resources/bookmap.json, read the md, cite pages). Before committing,
     if problems/sets/<unit>.md exists, run
     `python scripts/check_lesson_coverage.py problems/sets/<unit>.md lessons/<module>/<unit>.html`
     — it must report no missing references; if it reports any, add the
     missing theorem/definition/lemma to the lesson body (per
     LESSON-GUIDE.md item 5) before committing. Then commit, then open.
5. **Live layer** (the part a file can't do): after Stephen reads each
   segment, ask one Socratic question about it; answer questions with
   citations into the source; at lesson end pose the unit's "minute paper" —
   one-sentence summary in Stephen's own words + muddiest point. Record both
   in learning-records/<unit>.md (create; append if exists).
6. **Hand off to grading**: after the minute paper is recorded, check
   whether problems/sets/<unit>.md exists. If not, generate it now
   (following the same rubric-authoring process /grade expects, alongside
   problems/solutions/<unit>.md) so Stephen is never left without a
   problem set for a unit just lectured. Open/display the problem set and
   ask: "Want to attempt this now, or later via /grade <unit>?" If Stephen
   says later, change nothing else — /grade <unit> continues to work
   standalone.
7. **State updates** (atomic): set unit status `unlocked` → `in-progress` in
   state/progress.json when the lesson opens. Append to today's session log.
8. **Never** mark `mastered` — that is /grade (Phase 2).

Model note: generation quality gate — if generating, the lesson must pass
the LESSON-GUIDE checklist before commit; run its html.parser check.
