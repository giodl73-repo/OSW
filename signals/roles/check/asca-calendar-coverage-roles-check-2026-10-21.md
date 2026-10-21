---
skill: roles-check
topic: asca-calendar-coverage
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Agulhas calendar coverage review

Source baseline: e5fde03600835b23b0917c8ec30fc7c1a5090005 plus this batch.
Artifact: source-derived scientific summaries, Rust query integration and atlas
UI. Seven relevant functional lenses below; ORBIT has no planetary comparison
to review. This is repository review, not external scientific peer review.

| Role / reason | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT / physical interpretation | Conditional resolved spans cannot establish physical annual extrema. | P2 resolved | Protocol, report exclusion flags and adjacent UI caveat prohibit admission; retain. |
| CURRENT | Full nominal support is not full resolved support: 2017 resolves 131/438. | P2 resolved | Figure and UI give denominator; retain failures and partial-year labels. |
| CURRENT | Fixed-array −v at 100m is not a flow-normal width. | P3 | Source method and figure title preserve variable/depth; no map band or playback added. |
| SOUNDER / source identity | Rounded presentation values must not drive quantiles. | P2 resolved | Producer uses stored unrounded spans and Decimal type7; six-decimal final readback, separate display rounding. |
| SOUNDER | Source clock has alternating 71936/72064-second steps. | P3 | Original timestamps and membership retained; test rejects changed association; do not snap timestamps. |
| SOUNDER | Standalone plot and derived record need source credit. | P2 resolved | Added Beal et al., ASCA2.0, DOI and CC BY4.0 credit to plot; copied citation/URL/license to report and UI. |
| CHART / visual interpretation | A shared km axis supports comparison without implied geographic boundaries. | P3 | Both panels use same scale, explicit finite min–max and percentile legend. |
| CHART | Pooled months have unequal year support. | P2 resolved | Figure title says uneven support/not climatology; table gives year-bin counts and exact membership links. |
| CHART | Partial endpoint years require explicit labels. | P3 | 2016/2018 marked partial, April/June partial bins marked; keep labels. |
| BEACON / public claim | A full year may be mistaken for complete physical sampling. | P2 resolved | Lead paragraph states 131/438 and conditional statistics; do not shorten to annual width. |
| BEACON | A percentile interval may be mistaken for uncertainty. | P2 resolved | Adjacent text disclaims confidence intervals; legend names percentiles. |
| BEACON | Forty-eight records are summaries, not new independent measurements. | P3 | Plan/status distinguish cohort records from unchanged 931 profiles/2793 attempts. |
| HARBOR / access | Charts require a textual data alternative. | P3 | Sixteen-row semantic table and exact source links accompany alt text. |
| HARBOR | Wide tables must work by keyboard on phones. | P2 resolved | Focusable named scroll region; browser gate covers ArrowRight and 320px document reflow. |
| HARBOR | Added details must preserve dated-view keyboard controls. | P3 | Dedicated new/old details selectors retain existing assertions; regression browser gate required. |
| KEEL / reproducibility | Source dependency or owner mutation must fail. | P3 | Rust compares exact report/figure/input pins and one Agulhas owner; negative mutation/erasure tests. |
| KEEL | Initial test fixture incorrectly assumed Bundle Clone. | P2 resolved | Fresh fixture per mutation; 84 Rust tests and native/WASM build now pass. |
| KEEL | Local byte reproduction is not independent Linux proof. | P3 | All19 local reports exact; require truthful separate CI status after push, without relabeling older full suite. |
| LOGBOOK / repository status | Do not make a PR for each remaining gap. | P3 | Same branch and PR83; no main merge. |
| LOGBOOK | New summaries must not inflate width coverage. | P3 | Width inventory remains156 records/82 owners; preservation checks44 unchanged collections and49 old diagnostics. |
| LOGBOOK | Complete source checksum and full corrigendum review remain open. | P2 resolved | Inherited source-method limits remain visible; no completion claim or invented source dates. |

Roles reviewed: 7. Unresolved P1: 0; unresolved P2: 0. P3 notes: 11.
Verdict: APPROVED-WITH-CONDITIONS. Publication requires successful focused
browser and staged-blob gates; independent new-head CI remains a separately
reported release condition. The full current measurement program is incomplete.

Top finding: resolved sample ranges are not physical annual width ranges.
CURRENT, SOUNDER, CHART and BEACON agree on this interpretation boundary.

Three amendments applied: preserve source denominators and partial support;
add source credit to standalone/derived views; isolate calendar and dated UI
selectors while preserving regression assertions.
