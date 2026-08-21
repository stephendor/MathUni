# S1 gate promotion — putting the authoring gates in the repository

**Date:** 2026-08-21 · **Branch:** `s1-gate-promotion` (off `main`)
**Precedes:** the S1 content branches (`pw`, `la`, `an`, `aa` — 55 unwritten units)

Semester 1 is the semester that was skipped. Fifty-five of its sixty-five units
have no lesson and no problem set, and the ten that exist predate every
convention S2-S4 established. Before writing any of them, the gates those units
will be held to have to exist somewhere other than a temp directory.

`gate.py`, `mission.py`, `pull.py` and `build.py` were not in the repository.
They had been copied from session scratchpad to session scratchpad since S3, and
the S2 plan records that promoting them into `scripts/` "has now been deferred
three times". This branch promotes three of them, with tests, negative controls,
and CI wiring. What that promotion turned up is most of this document.

---

## 1. What was promoted, and what was not

| Script | Status | Note |
|---|---|---|
| `scripts/gate.py` | promoted | gates 4-6; `--selftest`, 50 controls |
| `scripts/mission.py` | promoted | gate 8; `--selftest`, 24 controls; `--known-failing` ratchet |
| `scripts/pull.py` | promoted | extraction; new `--folio` offset fitter |
| `build.py` | **not promoted** | see below |

`build.py` assembled a lesson by concatenating a scratchpad-local `head_tda.txt`
with a scratchpad-local `body_<unit>.html`. Neither file exists in any surviving
scratchpad, and the repository already carries `lessons/_template.html`, which is
what `LESSON-GUIDE.md` tells an author to start from. Promoting it would have
shipped a script that cannot run. It is recorded here as deliberately dropped
rather than overlooked.

## 2. The gates had never been run over the corpus

Each of these gates had only ever been run by an author, on the lesson in front
of them, at the moment they wrote it. Run across all 81 committed lessons for
the first time:

| Gate | Failed | Of |
|---|---|---|
| 4-6 (`gate.py`) | **5** | 81 |
| 8 (`mission.py`) | **15** | 81 |

The S2 plan had recorded three units as failing gate 8. Three was the sample.
Fifteen is the population. This is the failure mode the S1 handoff names
explicitly — *mechanise against the claim, not the sample* — and it cost nothing
to avoid here only because the population was derived before anything was fixed.

### 2.1 Gates 4-6: three of the five failures were the gate's fault

`an-02`, `pw-01` and `pw-03` failed "no external requests" on the string
`xmlns="http://www.w3.org/2000/svg"`. An XML namespace is an identifier, not a
URL; nothing is fetched, and the lessons render identically with the network
unplugged. The 76 S2-S4 lessons passed only because their authors happened to
omit the attribute — `at2-02` and `tda2-02` write inline `<svg>` without it.

Had the three lessons been "fixed" by stripping the attribute, the sample would
have gone green and the gate would still be wrong, waiting for the next author
who writes well-formed SVG. **Repaired in the gate**: namespace declarations are
stripped before the scan. Nothing else is exempted, and a line carrying both an
`xmlns` and a real URL still fires — there is a control for exactly that.

`aa-00` and `aa-01` were real: a stray `</p>` with no `<p>` open, three of them
between the two files. House style (`tda1-01`, and every S2-S4 `you-try`) wraps
these blocks in `<p>…</p>`; the opening tag had been dropped, so the repair is to
add it, not to delete the close. Done here, three one-tag edits, no prose touched.

Two defects in the balance check itself were repaired at the same time:

- **It cascaded.** Popping the stack on every end tag meant one stray `</p>`
  consumed the enclosing `<div>` and misattributed every close after it: four
  error lines from one defect, three of them wreckage. An end tag with nothing
  matching is now reported without popping.
- **It failed spec-legal markup.** HTML permits `</p>`, `</li>`, `</td>` and
  friends to be omitted, and a block start implicitly closes an open `<p>`.
  `lesson_lint.py` had already made this carve-out and documented why; `gate.py`
  now agrees with it. A *surplus* optional end tag is still an error — that is
  the aa-00 case, and dropping it would have been a silent weakening.

After the repairs: **81 of 81 pass**, and it lands as a hard CI gate.

### 2.2 Gate 8: fifteen failures, in two classes

Class A — **content divergence** (4): `aa-00`, `aa-01`, `pw-03`, `tda2-02`. The
lesson asserts something the syllabus does not.

Class B — **typography reverted while quoting** (11): `at2-01` … `at2-08`,
`tda2-01`, `tda2-03`, `tda2-06`. The right sentence, re-rendered: `H^n` → `Hn`,
`Z` → `ℤ`, `F_p` → `𝔽p`, `Kunneth` → `Künneth`, straight quotes → curly.

Class B looks like house style — lessons use literal Unicode maths and never
LaTeX — and it is worth being precise about why it is nevertheless a defect. The
question is settled by the corpus, not by argument: **`at1-03`, `at1-04`,
`at1-06`, `at1-09` and `tda2-10` all carry ASCII maths in their strips
(`H_1`, `pi_1`, `F_2`, `H^0`), quote it character for character, and pass.** The
mission strip is the one paragraph in a lesson that is a quotation rather than
prose, and prettifying a quotation is editing it. The eleven are the deviation.

**Neither class was fixed by loosening gate 8.** Normalising typography inside
the comparison would have made all eleven pass, and would have been the same act
as softening a quotation to make it true, one level up.

## 3. The ratchet

Fifteen failures meant gate 8 could not be a hard CI gate today, and the
alternative on offer — wire it non-blocking until someone repairs them — is
precisely how these scripts came to be deferred three times.

`--known-failing curriculum/mission-drift.txt` names the fifteen. They are
excused; every other lesson is held, so **no new lesson can drift**, which is
what matters for the 55 units about to be written. It is a ratchet rather than
an allowlist because of one rule: **a listed unit that starts passing fails the
run until it is struck off.** "Repaired but still listed" is the state a plain
allowlist is silent about, and that silence is what turns an allowlist into
permanent suppression. An entry whose lesson no longer exists fails the run too.

The list can only shrink. Class A comes off as `aa-00`, `aa-01` and `pw-03` are
re-authored in the S1 module branches; Class B and `tda2-02` are S3/S4 content
and get their own PR (§6).

## 4. Verified folio offsets — and Axler is not constant

`pull.py --folio` was written for this and mechanises what had been a prose
rule. It reads the printed folio off each page, fits an offset over a *range*
rather than trusting any single page, says `NO FOLIO` when it sees none, and
refuses to let a page without one contribute.

**Sign convention: `printed = PDF + offset`. Every offset is negative.**

| Book | Offset | Range (PDF) | Status |
|---|---|---|---|
| Cummings *Proofs* | **−4** | 5–330 | verified, constant whole book |
| Aluffi *Underground* | **−18** | 22–490 | verified, constant whole book |
| Abbott | **−12** | 13–**269** | verified; see the trap below |
| Axler | **−17** | 18–66 | verified |
| Axler | **−16** | 67–177 | verified |
| Axler | **−15** | 178–346 | verified |

**Axler drifts through three plateaus.** The handoff listed it as unverified and
warned that S4's plan had asserted a constant Ghrist offset that was false. Axler
is the same failure waiting to happen, and it matters more: `la` is fifteen units
against this book, spanning all three plateaus. `la-01` (Axler 1A-1B) sits at
−17; `la-11` (5A) sits at −15. **A single offset taken from `la-01` and carried
to `la-11` would be wrong by two printed pages on every citation.**

**Abbott's second plateau is the Instructor's Solutions Manual.** The fitter
found an offset of −276 across PDF 277–429 — the manual restarting its own
numbering from 1. This confirms the handoff's warning independently and
mechanically: the text ends at PDF 269, and **anything at PDF ≥ 270 is not the
text**. It matters for all 14 `an` units, because a naive heading search finds
every section from 1.1 twice and the second hit is the solutions.

`Aluffi Chapter 0` (offset −23) is a **different book** from *Underground* and is
not an S1 source; `aa` uses *Underground* at −18. Do not inherit `cat`'s −23.

### 4.1 The fitter had to be taught about chapter openers

The first version read the folio off the head of the page, and reported Axler's
offset jumping to −42 at PDF 44, −64 at 67, −129 at 133. Those pages read
`CHAPTER` / `2`, `CHAPTER` / `3`, `CHAPTER` / `4` at the head — **chapter
numbers, with the real folio at the tail** (PDF 44's tail is `27`; 44 − 27 = −17,
exactly its neighbours). Nine of Axler's twelve chapter openers do this.

This is the same mechanism the handoff describes for Ghrist, and it is worth
noting that reading one edge and trusting it would have produced a *confident*
wrong answer on nine pages. The fitter now collects candidates from both edges
and keeps the one consistent with the plateau, and reports a lone disagreeing
page as `SUSPECT` rather than as a pagination change — an index page-reference
looks identical to a one-page plateau, and crying drift on it would make the
tool useless on any book with an index.

## 5. Gate commands, after this branch

```bash
python scripts/check_lesson_coverage.py problems/sets/<u>.md lessons/<m>/<u>.html
python scripts/lesson_lint.py lessons/<m>/<u>.html
python -c "from html.parser import HTMLParser; HTMLParser().feed(open('lessons/<m>/<u>.html',encoding='utf-8').read())"
python scripts/gate.py lessons/<m>/<u>.html
python scripts/mission.py lessons/<m>/<u>.html
```

Gate 7 remains the manual canvas render-back and nothing else is gate 7. Gate 9
is `lab`-only. Before any commit: `python -m pytest -q` and
`python scripts/validate_syllabus.py`.

Authoring aids, now in the repo rather than in a scratchpad:

```bash
python scripts/pull.py --list
python scripts/pull.py Axler --find "linear functional"
python scripts/pull.py Axler --pages 60-72 --out extract.md
python scripts/pull.py Axler --folio 60-72
```

## 6. Source-boundary findings — for the syllabus pass, not for this branch

Content branches do not edit `curriculum/syllabus.yaml`. Nothing on this branch
touches it. One finding, and it is a question rather than a defect:

**F-1 — the syllabus writes mission strips in ASCII maths, and lessons render
Unicode.** Eleven S3/S4 lessons reverted the notation while quoting (§2.2). The
corpus convention is to quote the ASCII exactly, and five passing lessons prove
it is workable. But it is worth a deliberate ruling rather than an inherited
one, because "quote verbatim" and "lessons use literal Unicode maths, never
LaTeX" pull against each other in precisely this paragraph. Two options: repair
the eleven lessons to quote the ASCII (no syllabus change, mechanical); or
rewrite the eleven `mission_link` values in the syllabus to the Unicode the
lessons use and repair the lessons to match (a syllabus pass, and it would want
checking that nothing else consumes `mission_link` expecting ASCII). **This
branch assumes the former** and lists the eleven for a separate PR; the ratchet
holds them in the meantime.

## 7. What this unblocks, and what comes next

1. ~~Gate promotion~~ — this branch.
2. **`pw` (5 units)** — smallest module; `pw-01/02/03` gate the semester
   pedagogically. Includes re-authoring `pw-03` and writing its missing problem
   set (it is the only unit in the repo with a lesson and no set).
3. **`la` (15)** — three folio plateaus; watch the boundaries at PDF 67 and 178.
4. **`an` (14)** — nothing at PDF ≥ 270 is the text.
5. **`aa` (31)** — split along Aluffi's arc per
   `docs/specs/2026-07-22-abstract-algebra-restructure.md`.

Each gets its own plan document and its own branch off `main`, with a per-unit
tracker updated in the same commit as the unit.

## 7b. Codex review of PR #20 — eight findings, all eight real

An automated review raised two P1 and six P2 findings. Each was reproduced
against the committed code before anything was changed; all eight held, which
is worth recording because the previous three rounds of this session went the
other way (a gate wrong about the corpus rather than the corpus wrong).

| # | Finding | Was |
|---|---|---|
| P1 | drift list can GROW | a unit broken on purpose and then listed exited **0** |
| P1 | missing page file read as `NO FOLIO` | a range with only its endpoints extracted reported a consistent offset and exited 0 |
| P2 | equal plateaus split by a suspect | `OFFSET IS NOT CONSTANT` over a range with one offset |
| P2 | crossed optional-end elements | `<table><tr><td>x</tr></td></table>` came back clean |
| P2 | `<div/>` treated as closed | browsers leave it open; reported balanced |
| P2 | protocol-relative `//host/x` | not matched by gate 5 |
| P2 | non-JS `<script>` sent to `node` | a JSON data block fails a valid lesson |
| P2 | unreadable lesson file | `FileNotFoundError` exited **1** — the code reserved for a real mismatch |

Two of these deserve more than a table row.

**The ratchet was a claim, not a mechanism.** §3 above asserts "the list can
only shrink", and so did the commit message and the CI comment. The two stale
checks enforce no such thing: they catch a listed unit that starts passing and
one whose lesson is gone, and both of those make the list *shrink*. Nothing
stopped a branch adding a freshly-drifted unit and going green — verified, exit
0. `--baseline` now compares the list against the base ref and fails on any
addition, so the property is the one it was described as. A baseline that does
not exist is reported as missing rather than treated as empty, because an
absent baseline and a clean comparison must not look alike.

**Optional-end elements needed ordering, not counters.** The side-counter design
in §2.1 was chosen to stop a stray `</p>` cascading, and it did — but counters
discard nesting order, so a genuinely crossed pair of optional-end elements came
back clean. That is the exact failure mode gate 4 exists for and the one
`lesson_lint.py` structurally cannot see, so the carve-out had quietly given
away the gate's reason to exist over eleven tags. They are back on the stack
with HTML's implicit-close rules; omission is still legal, a surplus end tag is
still caught, and the stray `</p>` still does not cascade.

After the fixes: `gate.py --selftest` 36/36, `mission.py --selftest` 17/17,
pytest 115, gates 4-6 green on 81/81, gate 8 green under the ratchet.

## 7c. Codex review, second round — seven more, all seven real

| # | Finding | Was |
|---|---|---|
| P1 | singleton at a range EDGE excluded as SUSPECT | `--folio 66-70` reported "Consistent offset −16", exit 0, across Axler's real −17/−16 boundary |
| P2 | `git fetch … HEAD~1` is an invalid refspec | the baseline silently went missing on a push to main, and a missing baseline skips the growth check |
| P2 | optional-end list incomplete | a valid minimal HTML document reported 3 errors |
| P2 | MIME type compared as a raw string | `text/javascript; charset=utf-8` skipped — a false PASS on any syntax error inside |
| P2 | only the FIRST mission strip compared | a lesson could keep an exact strip and add a divergent second claim |
| P2 | unit id not anchored to the basename | `draft-aa-01.html` passed gate 8 as `aa-01` |
| P2 | ratchet could not reach zero | deleting the emptied list raised `FileNotFoundError` before any comparison |

**The P1 is the one that matters, and it inverts a claim in §4.1.** That section
says a lone disagreeing page is reported SUSPECT "rather than as a pagination
change", and cites the index-reference case. The rule as written was "any
plateau of one page", which is not the same thing: a singleton at the *first or
last* row of the range has evidence on one side only, so it cannot be shown to
disagree with both. Asking `--folio 66-70` — a range chosen to straddle the
documented 66/67 transition — returned `Consistent offset −16`, exit 0. **A
false "consistent" across a real boundary is the exact Ghrist failure this
subcommand was built to prevent**, reintroduced by the noise filter meant to
make it trustworthy. A singleton is now suspect only when it is interior *and*
the plateaus either side agree with each other, and the same rule decides both
the row labels and the verdict — they were two rules, and the verdict's copy
was the wrong one.

**Two of the others are the ratchet again.** The growth check landed in §7b and
was then unreachable in CI on a push to main, because `git fetch --depth=2
origin HEAD~1` treats `HEAD~1` as a refspec and dies; the failure was swallowed,
and mission.py skips the check when the baseline is absent. Checkout now uses
`fetch-depth: 0`, the base is `pull_request.base.sha` or `github.event.before`,
and **failing to resolve it is now a hard failure** — only "the base commit
exists and has no list" may skip. Separately, the ratchet could not reach its
own success state: the test told authors to delete the list once empty, and
`load_known_failing` then raised before comparing a single lesson. A missing
list is now an empty list, which excuses nothing and so cannot be used to
escape the gate.

After this round: `gate.py --selftest` 43/43, `mission.py --selftest` 22/22,
pytest 200, gates 4-6 green on 90/90, gate 8 75 PASS + 15 KNOWN-FAIL.

## 7d. Codex review, fourth round — six more, all six real

| # | Finding | Was |
|---|---|---|
| P2 | `node --check` uses the CommonJS grammar | `<script>return 1;</script>` passed gate 6; a browser refuses it |
| P2 | `type` matches inside `data-type` | an executable script was classified JSON and skipped |
| P2 | end tags for void elements ignored | `</br>`, `</img>`, `</input>` reported as balanced |
| P2 | `<svg/>` root reported malformed | foreign-content exemption only applied *inside* an already-open root |
| P2 | mission strip inside an HTML comment | gate 8 PASSed a lesson rendering no strip at all |
| P2 | ratchet reopens if the list is ever deleted | a later branch could reintroduce it with fresh mismatches |

**The script-grammar one is the most interesting.** `node --check foo.js` parses
under CommonJS, where the body is wrapped in a function, so a top-level
`return` is legal — and gate 6 printed `PASS inline scripts parse` for a script
the browser rejects outright with *Illegal return statement*. The gate was
running the right check under the wrong grammar. Classic bodies now compile
through `vm.Script`, which is exactly the Script grammar a plain inline
`<script>` gets; `type="module"` keeps `node --check` on a `.mjs` file, which is
the Module grammar. A control asserts the two paths are not swapped: an
`export` must fail as a classic script and pass as a module.

**The zero-state hole closes by making deletion impossible.** §7b's growth check
stands down when the base ref has no list, because that means the commit that
introduced it. If the file can ever be *deleted*, that condition stops being
unique: every later base also lacks the path, and a branch could reintroduce
the file alongside new mismatches and have them excused. So the list is now
permanent — the zero state is an empty file, not a deleted one — and mission.py
refuses a run where the baseline has a list and the working tree does not.

The remaining four are ordinary holes, each with a control: a word-boundary
that let `data-type` masquerade as `type`; `</br>`, which browsers do not drop
but re-interpret as a `<br>` start tag; a self-closing foreign root arriving
before foreign depth is incremented; and a commented-out mission strip, which
`lesson_lint.py` could not have caught either since its structure counter also
reads comments as text.

After this round: `gate.py --selftest` 50/50, `mission.py --selftest` 24/24,
pytest 212, gates 4-6 green on 90/90 with 173 inline scripts actually parsed.

## 8. Open decisions

- **D-1.** F-1 above: repair the eleven lessons, or change the syllabus strips?
  This branch assumes the former.
- **D-2.** `pull.py --folio` fits an offset but nothing binds a *citation* to it.
  A lesson citing "Axler p. 51" is not currently checked against the page it
  came from. A gate that re-reads every cited folio is buildable — the extract
  already carries PDF page numbers — and would close the last self-attested step
  in the authoring loop. Not attempted here; it is a gate, not a script
  promotion, and it wants its own design.
