---
skill: roles-check
topic: indian-secc-band-readback-repair
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal review of SECC distance readback and support comparisons

Baseline4709940 failed scientific reconstruction on Linux. Source fix5bad057
now passes all25 reports byte exactly on Linux, run39717576696/scientific
job119623281799; the baseline reproducibility failure is resolved. Each
retained/rebuilt SHA matches the corresponding local file. This current review
has zeroP1 findings. The old raw equality claim was not cross-platform
reproducible. Seven installed lenses apply;
ORBIT has no planetary comparison here. Internal review is not external
scientific approval, and the source fix adds no admitted current dimensions.

| Role | Finding | Severity | Resolution / evidence |
| --- | --- | --- | --- |
| CURRENT | Numerical geodesic drift cannot define a changed current boundary. | P2 | Version2 compares boundary coordinates/status independently of distances; tests retain a real changed edge. |
| CURRENT | Readback rounding could be mistaken for physical uncertainty. | P2 | Explicit numerical-only protocol, six decimal km; no uncertainty/range/width admission. |
| CURRENT | Repair must not change peak, graph or source support. | P2 | All2,187 bands, connectivity, peaks and source brackets exact; nine actual northern crossings retained. |
| SOUNDER | Historical values must not be rounded to manufacture agreement. | P2 | All72 historical compact values and historical source report byte exact; only new distances rounded. |
| SOUNDER | Original cube and earlier producers need independent preservation. | P2 | All24 earlier reports/producers and426 prior indexed originals exact. |
| SOUNDER | Precision changes need explicit provenance and versioning. | P2 | Separately pinned readback protocol, schema v2, new comparison fields; no shared operator/global policy changes. |
| CHART | Rounding distances must not shift map geometry. | P2 | Final SVG/PNG byte-identical to visually inspected baseline figures. |
| CHART | Regenerated figure manifest must bind the corrected source. | P2 | Source/producer/asset pins verify and all396 staged engine hashes match. |
| CHART | Tiny numerical units must not imply resolved physical detail. | P2 | Under0.5mm maximum readback displacement explicitly numerical; source-grid limitations retained. |
| BEACON | Old exact-comparison label implied more than it proved. | P2 | Replaced with exact boundary/status and separate span-readback fields. |
| BEACON | Arithmetic drift had falsely increased recovered counts on Linux. | P2 | Recovery now requires changed northern edge support, not a distance inequality. |
| BEACON | Historical report needs a visible correction trail. | P2 | Versioned repair note and earlier batch erratum preserve the original failed-run evidence. |
| HARBOR | Corrected semantics must survive the actual query UI. | P2 | Actual native/WASM equality for12 graphs,12 summary rows and72 comparisons. |
| HARBOR | Navigation must remain usable without a pointer. | P2 | Keyboard card/figure gate passes; no new interaction model. |
| HARBOR | Field changes must preserve mobile reflow and source access. | P2 |320px query/card checks pass; zero automatic original downloads. |
| KEEL | Linux verification must include every required report. | P2 | All25 report bytes and hashes match at5bad057/run39717576696/job119623281799; NetCDF also passes. |
| KEEL | Tolerance must not hide genuine differences. | P2 |15 tests include raw drift, real distance change, changed boundary/status, original brackets and independent flood fill. |
| KEEL | Focused repair cannot close the complete offline suite. | P2 | IRD acquisition403/local4GiB disk guard remain separate; no overall green claim. |
| LOGBOOK | Current scientific rows and dates must remain unchanged. | P2 |50 collections/59,828 rows exact except SECC fingerprint; links/capabilities/dates preserved. |
| LOGBOOK | Failure history must not be erased by repinning originals. | P2 | Failed4709940/run39715841797 retained; raw sources untouched; new protocol addresses derived arithmetic only. |
| LOGBOOK | Continue in one publication destination. | P2 | Same draft PR83; no new PR/main merge; axis protocol declared but no new normal measurements claimed. |

21 currentP2 findings:20 resolved,one complete-suite gate open;zeroP1. The
previous baseline failure is verified repaired, not waived. Offline119623281786
still fails before tests on IRD Rotschi1972 HTTP403; no overall green claim.
Verdict APPROVED-WITH-CONDITIONS for the scoped repair; full program incomplete.
Three amendments: independent boundary/status comparison; scoped derived-only
distance precision; explicit source/history preservation and failed-run trail.
