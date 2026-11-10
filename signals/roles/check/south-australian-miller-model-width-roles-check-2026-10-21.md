# South Australian local model-width report: internal review

Artifact: original-source extraction, Rust source binding and atlas card.
Seven applicable repository lenses; ORBIT omitted (no planetary analogy).
Internal functional review, not independent scientific peer review.

| Role | Finding | Severity | Resolution / gate |
|---|---|---|---|
| CURRENT | A model snapshot is not an observed width. | P1 if promoted | Measurement class and visual explicitly say local model report. |
| CURRENT | Annual forcing is not annual mean width. | P1 if promoted | Model day20 retained; annual-mean and mean-of-widths flags false. |
| CURRENT | Whole-current and seasonal boundaries are unknown. | P2 | No whole-current admission, range, date or geometry inferred. |
| SOUNDER | Indexed text was insufficient to confirm the experiment. | P2 | Complete original acquired; setup p.48, passage p.49 and Fig4.20e p.233 reviewed. |
| SOUNDER | The source name differs slightly from the ledger spelling. | P2 | Original label preserved, local South Australian owner explicit; Leeuwin width not substituted. |
| SOUNDER | Approximate prose has no specified edge operator or uncertainty. | P2 | No paired edges, cutoff, layer bounds or numerical error invented. |
| CHART | A drawn band could be mistaken for extracted boundaries. | P2 | Annotated numeric callout; no geographic band or area. |
| CHART | Section figure has substantial vertical structure. | P2 | Only source-reported scale retained; no depth slice digitized. |
| CHART | Nearby model diagnostics use a different source and year. | P2 | Existing HYCOM diagnostics kept separate; no validation or annual continuity claimed. |
| BEACON | A new report could imply an inventory gap is closed. | P2 | Source-acquisition gap closed; measurement-inventory admission and physical-width gaps remain explicit. |
| BEACON | Model day might be read as an observed calendar date. | P2 | Elapsed model day named; observed interval and calendar months null. |
| BEACON | Readers need concise access to quantities and source. | P3 | Numeric HTML summary, source-query link, original archive link and locators. |
| HARBOR | Image text shrinks on phones. | P2 | Equivalent full-size HTML values and scope beside responsive image. |
| HARBOR | Source access must be keyboard operable. | P2 | Native links; keyboard link activation included in browser verification. |
| HARBOR | Meaning must survive absence of color. | P3 | Written quantity, experiment and restrictions; no color-dependent classification. |
| KEEL | Source PDF must be available offline with exact bytes. | P2 | Original retained under explicit unlimited-distribution statement; byte count and checksum verified. |
| KEEL | Rehashed mutations could retain a misleading model claim. | P2 | Rust compares complete report to compiled source and checks dependencies/owner. |
| KEEL | Updating scope notes changes a dependent binding. | P2 | Regenerate existing scope index; its13 assessments and frozen inputs preserved. |
| LOGBOOK | Work must remain within PR83. | P2 | Same branch, no new PR, no main merge. |
| LOGBOOK | Public release does not imply a public-domain license. | P2 | Redistribution statement recorded; public-domain flag false, SPDX license null. |
| LOGBOOK | Broad CI result must not be inferred from focused tests. | P2 | Prior30d4d8e scientific reproduction succeeds; offline job fails during original-paper acquisition (HTTP403), before tests. New head needs its own result. |

Verdict: approved for source-defined **local model report** presentation.
No canonical measurement admission, scientific approval or annual-range closure.
Executed verification is recorded separately from this review.
