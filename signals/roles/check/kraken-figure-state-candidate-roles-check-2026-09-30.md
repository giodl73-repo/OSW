---
skill: roles-check
topic: kraken-figure-state-candidate
date: 2026-09-30
depth: quick
roles_used: 6
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: Kraken Figure 2 state candidate

Artifact: `analysis/build_published_kraken_figure_state_join.py`, its dated JSON audit, the `CAMR` named-eddy assessment, and the screened atlas display. Selected CURRENT, SOUNDER, CHART, HARBOR, KEEL, and LOGBOOK from `.roles/`.

| Role | Finding | Severity | Recommendation |
| --- | --- | --- | --- |
| CURRENT | The solid red material-core loop and dashed shielding loop are smaller than, and defined differently from, the whole instantaneous SSH ring. | P2 | Keep the finding about the depicted red curves only; never label it whole-ring containment. |
| CURRENT | A dated figure cannot establish persistence between 29 May, 1 August, and 12 October 2013. | P2 | Preserve the three panel dates and avoid a continuous track claim. |
| SOUNDER | The exact NOAA-hosted PDF and embedded JPEG are pinned, but the article does not publish closed numeric curve coordinates. | P2 | Keep source hashes, axis calibration, and no-closed-polygon status with the claim. |
| SOUNDER | Figure 2 is covered by the article's stated CC BY 4.0 license and has no separate figure credit; this is an adaptation. | P2 | Credit authors, article, license, and OSW's pixel analysis; do not package the source image unnecessarily. |
| CHART | The May red pixels approach the approximate `CAMR` edge; two fall outside under one axis calibration corner. | P2 | Report the 3,406/3,408 worst case and use `candidate`, not `contained`. |
| CHART | Pixel count is a curve sample count, not area or a polygon intersection fraction. | P2 | Keep the measured fraction labeled as red-pixel coverage only. |
| HARBOR | A reader needs the dated evidence in text without interpreting red lines on a figure. | P2 | Show dates, state, sensitivity, caveat, and state passport link in the screened record. |
| HARBOR | An accessible standalone source figure is not packaged in the screened site. | P3 | Keep the linked article and text audit; human accessibility review remains required. |
| KEEL | The optional reconstruction depends on exact PDF bytes and additional figure libraries. | P2 | Pin hashes and versions, verify the optional command, and keep default package checks offline. |
| KEEL | The new source ledger and assessment pointer must survive rights screening. | P2 | Check screened excerpt count, claim pointer closure, source exclusion, and browser detail. |
| LOGBOOK | The full candidate still has 17 used rights-pending sources and unreviewed scientific claims. | P1 | Keep the public release gate closed. |
| LOGBOOK | Source use changed from a citation to a figure-derived adaptation. | P2 | Update the source-use review and third-party notice to match actual data use. |

Roles reviewed: 6. P1: 1; P2: 10; P3: 1. Verdict: **NEEDS-WORK for public release; the figure candidate is suitable for internal review after the validators pass.** CURRENT, SOUNDER, and CHART agree that the red-curve evidence cannot establish whole-ring containment.

Amendments made: exact source and image hashes, CC BY adaptation notice, three dated panel envelopes, ±3-pixel calibration sensitivity, a `figure_derived_red_curve_candidate` evidence class, and text in the screened record. Remaining: scientific review of the figure calibration and a provider-defined or defensibly reconstructed whole-ring boundary for a physical intersection decision.
