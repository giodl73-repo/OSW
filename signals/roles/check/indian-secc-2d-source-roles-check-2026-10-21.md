---
skill: roles-check
topic: indian-secc-2d-source
date: 2026-10-21
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal source-intake and visualization review

Seven installed role lenses apply to the source cube, calculations, maps and
source-store/card integration. ORBIT is outside this physical-data scope.
This is internal editorial review, not external scientific approval.

| Role | Finding | Severity | Resolution / evidence |
| --- | --- | --- | --- |
| CURRENT | Surrounding eastward flow does not verify SECC association. | P2 | No axis, paired boundaries, width or length admitted; competing jets/SEC/eddies retained. |
| CURRENT | Monthly-mean fields are not mean instantaneous widths. | P2 | Explicit operator, period and non-admission flags; no physical seasonal ranges. |
| CURRENT | Frequency/classification support is not flow edges. | P2 | Prior EOF study unchanged; viewport independent of threshold or fitted boundaries. |
| SOUNDER | Original custody must be complete and reproducible. | P2 | Exact CSV/metadata ZIP, actual UTC/URLs/HTTP/length/hash/license receipts. |
| SOUNDER | Historical source slices must remain exact. | P2 |4464 vectors and744 monthly cells verified at float64 bits/masks/counts; outside tails preserved. |
| SOUNDER | Nominal depth and source clocks must not become invented observations. | P2 |15m mapped upper-ocean support,72 actual clocks, no resampling or new current observation dates. |
| CHART | The source viewport can be mistaken for current extent. | P2 | Figure/map labels and report state source context; no physical outline, area or state intersection. |
| CHART | Scale, vector direction and missingness need consistent meanings. | P2 | Fixed signed eastward scale, explicit clipping counts, fixed vector key/stride and distinct missing cells. |
| CHART | Bottom caption initially overlapped axes. | P2 | Bottom margin increased, figures regenerated; final PNG and320px card visually reviewed. |
| BEACON | Component extrema may sound like seasonal current dimensions. | P2 | Summary identifies spatial monthly-component extrema; width/length remain null. |
| BEACON | Source update should be distinguishable from measurement admission. | P2 | SECC source group/fingerprint updates; accepted width counts unchanged. |
| BEACON | Short path to data and method is required. | P2 | Map/full-fields/scalar-summary/original-ZIP links; exact native/WASM query and keyboard navigation pass. |
| HARBOR | Maps require a readable data equivalent. | P2 |12-row scalar summary plus complete monthly arrays/counts/clocks through source query. |
| HARBOR | Card disclosure/navigation must work by keyboard. | P2 | Actual Chrome keyboard disclosure, figure navigation and direct ZIP href pass. |
| HARBOR |320px reflow must preserve source qualifications. | P2 | Actual320px query/card/figure navigation and overflow gate pass. |
| KEEL | Parse/source changes must fail rather than repin history. | P2 | Ten source tests pass: malformed clock/grid/header/units, missing/duplicate rows, infinities and altered historical values/masks. |
| KEEL | Monthly arithmetic needs independent validation. | P2 | Paired-only count/mask checks and independent NumPy sums with forward-error bounds pass; new24th scientific target. |
| KEEL | Full integration/release gates must stay honest. | P2 | 109 Rust tests,10 Python tests, two actual browser gates and preservation pass; full suite remains open owing IRD403 and disk guard. |
| LOGBOOK | The continuing PR is the publication destination. | P2 | Existing branch/PR83, no new PR or main merge. |
| LOGBOOK | Expected counts cannot claim uncovered width closure. | P2 |18 uncovered owners and89 unranked lengths unchanged; scoped regional source-data gap only. |
| LOGBOOK | Source assets must have permission and exact staged pins. | P2 | Provider permits redistribution; archive retains notice. All386 staged engine dependency hashes match, including retained original ZIP. |

21 P2 findings:20 resolved,one full-suite integration item remains open;zeroP1.
Focused source-intake gates passed; whole-project full-suite gate remains open. Three
amendments: distinct source/physical evidence classes, independently checked
historical overlap, and separated figure caption/axes with semantic data access.
