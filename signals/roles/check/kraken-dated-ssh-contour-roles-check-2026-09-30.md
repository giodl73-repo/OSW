---
skill: roles-check
topic: kraken-dated-ssh-contour
date: 2026-09-30
depth: quick
roles_used: 6
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: Kraken 29 May SSH contour state assessment

Artifact: `analysis/build_published_kraken_figure_state_join.py`, `research/kraken-2013-figure2-state-audit.json`, the two named-eddy state assessments, and the screened atlas. Selected CURRENT, SOUNDER, CHART, HARBOR, KEEL, and LOGBOOK from `.roles/` for a dated physical proxy and public-facing data claim.

| Role | Finding | Severity | Recommendation |
| --- | --- | --- | --- |
| CURRENT | Figure 2 identifies the 29 May outer blue loop as an instantaneous SSH contour; later blue loops are advected and cannot be dated Eulerian footprints. | P2 | Restrict this derived footprint to 29 May and preserve the red-core distinction. |
| CURRENT | A 2-D SSH contour is a proxy for a ring footprint, not a material boundary or full-depth volume. | P2 | Keep the proxy qualifier and avoid whole-ring lifetime or volume claims. |
| SOUNDER | Exact source PDF and embedded JPEG are pinned, while manual axis tick readings remain a significant source of spatial uncertainty. | P2 | Preserve source hashes, tick positions, threshold cases, and axis perturbations with the record. |
| SOUNDER | Three RGB thresholds return one main closed loop; fine JPEG artifacts appear inside one threshold case. | P3 | Retain the large-loop and hollow-interior checks, and expose the threshold cases. |
| CHART | Nominal contour area is about 98.8% CAMR and 1.2% CARB; plausible axis perturbations give CAMR 92.58–100% and CARB 0–7.42%. | P2 | Label CAMR intersection robust, CARB intersection axis-sensitive, and containment unresolved. |
| CHART | OSW state boundaries are approximate display polygons, so the small CARB sliver is sensitive to both source calibration and atlas boundary choice. | P2 | Present fractions as overlap with this atlas geometry, not authoritative geographic area. |
| HARBOR | Readers need the two state assessments and uncertainty in text, without interpreting the source image's colors. | P2 | Keep separate labeled claim fields and a linked source audit in the record and state passport. |
| HARBOR | The screened site has automated browser coverage, but human accessibility sign-off remains open. | P3 | Complete human review before publication. |
| KEEL | The extraction is reproducible only with the pinned paper PDF and optional OpenCV dependency. | P2 | Pin the optional dependency, check exact hashes, and keep default checks offline. |
| KEEL | The full package and screened excerpt must agree about both CAMR and CARB claims. | P2 | Run release, preview, site, and browser validators after rebuilding. |
| LOGBOOK | This new use adapts the blue Figure 2 contour as well as red pixels. | P2 | Update third-party notice, source-use review, and published-observation limits. |
| LOGBOOK | The package still has rights-pending used sources and unreviewed scientific claims. | P1 | Keep the public release gate closed. |

Roles reviewed: 6. P1: 1; P2: 9; P3: 2. Verdict: **NEEDS-WORK for public release; suitable as an internal candidate after validation.** CURRENT and CHART agree that the dated SSH proxy warrants an intersection candidate but cannot establish whole-ring containment.

Amendments: (1) Separate the 29 May blue SSH proxy from three red-curve dates; (2) expose nominal and sensitivity overlap fractions and mark CARB axis-sensitive; (3) update the provenance notice and pin OpenCV. Remaining: scientific review of axis calibration and state geometry, human accessibility review, source rights reconciliation, and publication decision.
