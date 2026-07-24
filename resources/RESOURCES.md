# Resources

Curated, high-trust sources per module. `/ingest` (Phase 4) builds the full
`inventory.json`; this file is the human-readable register.

## Core Texts folder
`D:\OneDrive - The Open University\NexusCollege Core Texts\`
- `pdf\<book>.pdf` — canonical PDFs (page-number citations)
- `md\<book>.pdf\markdown.md` — full-book markdown conversion (preferred for
  quoting/generation) with `pages\` per-page breakdown for precise citation.

Confirmed present (2026-07-04): Axler LADR, Abbott Understanding Analysis
(incl. instructor solutions), Aluffi Notes from the Underground, Cummings
Proofs, Carter Visual Group Theory. Stephen reports all remaining PDFs +
markdown conversions now added — verify at Phase 4 ingest.
Also added as a source: **Cummings, Real Analysis** (long-form companion to
Abbott-level material; use for alternative explanations and extra problems).

## Video courses (Semesters 1-2)

| Module | Series | Link | Notes |
|---|---|---|---|
| la | Axler's own LADR lectures | https://www.youtube.com/playlist?list=PLGAnmvB9m7zOBVCZBUUmSinFV0wEir2Vw | Pair with LADR chapters |
| an | Francis Su, Real Analysis | https://www.youtube.com/playlist?list=PL0E754696F72137EC | Verified 2026-07-04. Uses Rudin; regarded as exceptional. Map lectures to Abbott units where topics align |
| an | Chris Staecker, Real Analysis | https://www.youtube.com/playlist?list=PLqObMWX4M-If-BQGaUP3eJhqbygoNy_kN | Follows Abbott — primary video strand for an units |
| an | Marc Renault, Real Analysis | https://www.youtube.com/playlist?list=PLysi2xmniDSzz6xT7IzOifpoexeKccThh | Follows Abbott; extra notes+exercises in docx within Core Texts md folder |
| pw | Cummings Proofs companion series | https://www.youtube.com/playlist?list=PLcO7tC6LDUstySkU-c_UuuKtQtwtGrTQB | Pair with Proofs chapters |
| aa | Macauley, Visual Group Theory | https://www.youtube.com/playlist?list=PLwV-9DG53NDwl5uExD8m9FY16QX2fV4qh | Visual layer for the aa GROUPS units only (aa-00, aa-23, aa-25); Carter-based |
| aa | Borcherds, Group Theory | https://www.youtube.com/playlist?list=PL8yHsr3EFj51pjBvvCPipgAT3SYpIiIsJ | Depth/enrichment layer |
| aa | Borcherds, Rings and Modules | https://www.youtube.com/playlist?list=PL8yHsr3EFj52XDLrmvrFDgwcf6XOm2TEE | Priority for Semester 2 — modules strand |

Fallback: MIT OCW for any gap.

## Capstone resource
- **Topological Deep Learning book** — https://tdlbook.org/ (entirely online).
  Reserve for Semester 4 / capstone alongside the TDL project; do not surface
  in earlier modules.

## Existing collection folders (Phase 4 audit targets)
- `D:\OneDrive - The Open University\Undergraduate Mathematics` (+ subfolders)
- `D:\OneDrive - The Open University\Oxford Lecture Notes for essential topics`
- `D:\OneDrive - The Open University\Cambridge Lecture Notes\Cambridge Dexter Notes`
  (note `_def`/`_eg`/`_thm`/`_thm_proof` pre-split PDFs — primary SRS corpus)
- `D:\OneDrive - The Open University\Currently Reading`
- `D:\OneDrive - The Open University\Tripos Papers`

## Resource resolution rule (Phase 1)

`syllabus.yaml` resource strings resolve via `bookmap.json`: the longest slug
that is a prefix of the string names the book; the remainder is the section
reference (e.g. "Axler 1A-1B" → bookmap["Axler"], sections 1A-1B). Non-book
resources (video playlists, folder names like "Oxford M1 Groups") are not in
bookmap and resolve via the tables above. Lesson generators quote from `md`,
cite pages via `pages\` filenames, and fall back to `pdf` on conversion damage.

The **machine-checkable** half of this rule lives in `resource_sources.json` —
the flat list of permitted non-book source prefixes. `validate_syllabus.py`
fails the build on any syllabus resource that resolves to neither a `bookmap.json`
key nor a registered prefix, so **register a source there (or the book in
bookmap) before citing it**. Resolution is boundary-checked: a name matches
only when the citation ends there or continues with a delimiter (a space or
punctuation), so a run-on typo like `Hatcherx 2.1` is rejected rather than
silently absorbed. See `docs/syllabus-authoring-checklist.md`.
