# Module: Python for TDA Lab (lab) — Semester 2

**Primary text:** the tool documentation — Ripser / GUDHI / giotto-tda /
scikit-tda (persim, KeplerMapper). **Support:** Edelsbrunner–Harer,
*Computational Topology* and Oudot, *Persistence Theory* (Core Texts) as the
theory backstops; Otter et al., *A roadmap for the computation of persistent
homology* (2017) as the practical map.

**Mission link:** this is the module where the mission stops being abstract. A
**point cloud** becomes a **filtered simplicial complex** (lab-02), whose
**persistence** is one boundary-matrix reduction (lab-03), read off as a
**barcode** (lab-04) — which is an analogue of aa-20's structure theorem, now visible in the barcode. It
is the hands-on counterpart to the algebra (`aa`), the topology (`top`), and the
Semester-3 theory (`tda1`); the mini-project (lab-09) is a dry run of the
capstone.

**Nature of the module:** unlike the proof-based strands, `lab` units are
build-and-run. Each lesson ends not with a blank-page proof but with **runnable
code and a plot** — a computed diagram, a distance, a Mapper graph. The
LESSON-GUIDE structure still holds (hook, prediction, self-checks), but the
"guided proof" slot is a **guided computation** and the visual is a real output.

## Arc and unit map

Linear spine lab-01 → lab-09. The cross-links are load-bearing: each is the
Semester-1/2 unit whose machinery that step makes runnable.

| Unit | Focus | Depends on (cross-strand) |
|---|---|---|
| lab-01 setup & point clouds | environment; sampling shapes; a hole to find | ←la-01, an-14 |
| lab-02 simplicial complexes | Vietoris–Rips, Čech; the filtration | |
| lab-03 computing persistence | boundary-matrix reduction over 𝔽₂ | ←la-07, aa-18 |
| lab-04 diagrams & barcodes | birth/death; intervals = the structure theorem | ←aa-20 |
| lab-05 bottleneck/Wasserstein; stability | diagram distances; the stability theorem | ←pw-04, an2-03 |
| lab-06 vectorising diagrams | persistence images, landscapes, Betti curves | |
| lab-07 TDA in ML pipelines | persistence as a scikit-learn feature step | |
| lab-08 Mapper | cover → cluster → graph summary | ←la-15 |
| lab-09 mini-project | one dataset, full pipeline, written up | |

## Teaching notes

- **Every unit produces an artifact** the learner keeps: a script + a figure.
  Prefer giotto-tda for the pipeline-shaped units (03, 04, 06, 07) and GUDHI /
  Ripser where raw speed or clarity of the complex helps (02, 03).
- Tie each computation back to its proof. When the barcode appears (lab-04), say
  it out loud: "these intervals are the summands aa-20 promised." When stability
  is demonstrated numerically (lab-05), name it as the epsilon statement pw-04
  trained and the compactness argument an2-03 underwrites.
- lab-03 is the conceptual summit — the reduction algorithm IS homology. Do it by
  hand on a tiny complex (a filled triangle) before calling the library, so the
  library is demystified, not magic.
- Keep environments reproducible: pin versions, note that Ripser/GUDHI are the
  fast C++ backends and giotto-tda/persim the scikit-friendly front ends.
- Every theorem quoted in a blockquote has an executable hypothesis-boundary
  instantiation before the next problem, marked `# THEOREM-PROBE: <case>`.
  Illustrating a typical conclusion is not enough: choose a case that could
  falsify a missing or misstated hypothesis.
- Print evidence at the finest granularity used by the prose. If an answer
  reasons about parts of an aggregate, its recorded block prints those parts;
  a roll-up alone cannot support a claim about its decomposition.
- lab-08 (Mapper) leans on la-15 (spectral methods) for its clustering step;
  lab-09 should reuse, not re-derive, everything from 01–08.

## Assessment

- No SRS deck for most lab units (the deliverable is code, not recall); a short
  "what does this function return / why this parameter" check per unit.
- Module deliverable: the **lab-09 mini-project** — a notebook taking a chosen
  dataset from point cloud to interpreted barcode/Mapper graph, with a short
  written analysis. Graded per spec §7 against a computational rubric (correct
  pipeline, honest interpretation, reproducible), 80% gate.

## Common misconceptions to watch (seed for learning-records)

- Reading noise (short bars) as signal — the whole point of stability (lab-05) is
  to justify ignoring them.
- Vietoris–Rips vs Čech: assuming they give the same complex (they interleave but
  differ; VR is cheaper, Čech has the nerve-theorem guarantee) (lab-02).
- Forgetting the coefficient field: persistence over 𝔽₂ hides orientation/torsion
  that integral homology would show (lab-03, ties back to aa-06/aa-22).
- Treating a persistence diagram as a vector and feeding it straight to a model —
  vectorisation (lab-06) exists precisely because you cannot.
- Over-reading a Mapper graph: its shape depends on cover/lens choices; it is a
  summary, not a canonical invariant (lab-08).
