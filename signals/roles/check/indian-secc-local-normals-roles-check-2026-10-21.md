---
skill: roles-check
topic: indian-secc-local-normals
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal local-axis and normal-section review

Baseline25bbdbb; source method, geometry, maps and query integration reviewed
through the seven applicable installed lenses. ORBIT has no planetary analogy.
This is internal review, not external scientific approval. Local integration/preservation gates pass. Linux5070eec/run39720938432/
scientific119633957327 reconstructs all26 report bytes exactly, with every SHA
matching its local report; NetCDF119633956968 also passes.

| Role | Finding | Severity | Resolution / evidence |
| --- | --- | --- | --- |
| CURRENT | One transverse peak cannot establish an along-current axis. | P2 | Five stations required; offset cases cannot pass that test. |
| CURRENT | A coarse-only success cannot be selected as a robust current width. | P2 | One10km pass,zero both-step passes; all failures retained, no canonical admission. |
| CURRENT | Monthly mean-field streamlines are not particle paths or annual extents. | P2 | Explicit operator/layer/period and null physical length/width/ranges/state join. |
| SOUNDER | Oversampling must not masquerade as native resolution. | P2 | Source-cell indices and native-grid-scale flags separate from5/10km steps. |
| SOUNDER | Paired support must be conservative and exact. | P2 | Four finite corners/continuous rectangles; missing-side stop, no zero fill or bridge. |
| SOUNDER | Existing source reports/producers must remain immutable. | P2 | All25 prior reports/producers and428 indexed originals exact; all430 source hashes verify. |
| CHART | Geographic display must preserve the geodesic measurement convention. | P2 | WGS84 normals/spans; equirectangular degree view explicitly not the distance ruler. |
| CHART | Missing pairs and failed candidates must remain visible. | P2 | Original seeds, crosses, dashed paths and local style labels; all cases in source data. |
| CHART | Map subset could conceal10km or offset failures. | P2 | Figure declares5km central cases; headline states zero both-step support; full cases linked. |
| BEACON |36 central spans could be mistaken for36 independent current-width observations. | P2 | Repeated source/seed/step support and candidate status explicit; no new width inventory records. |
| BEACON | Method gates could be tuned to manufacture a pass. | P2 | Predeclared1%/10km/15degree gates unchanged after results; one coarse pass not promoted. |
| BEACON | Threshold/step/seed sensitivity is not measurement uncertainty. | P2 | Separate comparisons and explicit false uncertainty/annual-range flags. |
| HARBOR | Standalone SVG requires its own accessible meaning. | P2 | Named image role/title/description and semantic12/144/72 data equivalents. |
| HARBOR | Card navigation must work by keyboard. | P2 | Actual Chrome keyboard disclosure/figure navigation pass. |
| HARBOR | Large query records must preserve phone reflow and data export. | P2 |320px/all144 outcomes/full passing and failed cases/export checks pass; semantic data equivalent retained. |
| KEEL | Positive control is needed so the method cannot merely reject everything. | P2 | Analytical straight jet passes five checks and matches independent geodesic half-peak width. |
| KEEL | Source calculations need independent and cross-platform evidence. | P2 |18 tests pass,including independent interpolation; all26 Linux report bytes/hashes match at5070eec/run39720938432. |
| KEEL | Scoped tests cannot close the entire release gate. | P2 | Current Stramma primary/mirror403 stops before tests; prior IRD403 is not reached; local4GiB guard remains unmet. |
| LOGBOOK | Current capabilities, dates and prior scientific rows must remain stable. | P2 | All59,828 rows exact except intended SECC fingerprint/links; capabilities/dates preserved. |
| LOGBOOK | Workspace cleanup must preserve original bytes. | P2 | Exact gzip/ZIP reconstruction hashes verified; original archives retained. |
| LOGBOOK | All batches belong in the continuing PR. | P2 | Same draft PR83; no new PR/main merge. |

21 P2 findings:20 resolved,one complete-suite release gate open;zeroP1.
Local build/browser/preservation,all403 staged hashes and26-report Linux
reconstruction pass. Offline119633957201 fails before tests on Stramma1992
HTTP403,not on a numerical reconstruction. No overall green CI claim. Amendments: explicit two-step nonrobustness,
analytical positive control plus independent vectors, and accessible SVG with
all failures/partial support retained in the semantic data.
