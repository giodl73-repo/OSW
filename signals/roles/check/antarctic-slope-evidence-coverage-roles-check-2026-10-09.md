---
skill: roles-check
topic: antarctic-slope-evidence-coverage
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Antarctic Slope evidence coverage review

Internal review of primary-source scope, width decision and the shared
Rust/WASM/dashboard projection. Seven installed functional lenses apply;
ORBIT has no planetary comparison to assess. No external peer review claimed.

| Role | Finding | Severity | Resolution |
|---|---|---|---|
| CURRENT | Mooring distance is not a paired current width. | P2 | Explicitly exclude 5 km and 80 km station separations. |
| CURRENT | A dynamics length scale or curvature radius cannot become width. | P2 | Exclude the two uses of 10 km on original p13; keep dimensions null. |
| CURRENT | A local velocity series cannot establish seasonal width margins. | P2 | Source review states repeated cross-flow boundaries remain required. |
| SOUNDER | Original evidence must remain available offline. | P2 | Complete unchanged CC BY original, source receipt and SHA shipped. |
| SOUNDER | Observation date must differ from retrieval/publication date. | P2 | Dashboard uses released measurement endpoint 2021-02-13, not 2026 retrieval. |
| SOUNDER | Summary count must not imply 61 independent source measurements. | P2 | Series label distinguishes 49 means and 12 composites; retains 16,393 paired source readings. |
| CHART | Coverage lights must represent the selected evidence. | P2 | New observed-velocity metric and existing time metric light up; width remains zero. |
| CHART | A coverage station must not imply an occupied current footprint. | P2 | No width buffer or geometry capability added. Query retains fixed station support. |
| CHART | All visual projections must use the same evidence counts. | P2 | Shared Rust selection drives Beck/map/cards; native and WASM selection compared. |
| BEACON | Unassessed and reviewed-without-width are different decisions. | P2 | Inventory now has 29 unassessed and six reviewed owners; numeric coverage unchanged. |
| BEACON | Readers need a short path from light to real evidence. | P2 | Dashboard series link opens the velocity charts; scope note links primary paper. |
| BEACON | Current width must remain visibly unresolved. | P2 | Dashboard note describes exclusions and unknown paired boundaries beside source links. |
| HARBOR | New metric needs an explicit text label. | P2 | Named dropdown option and textual count supplement lights. |
| HARBOR | Mobile card must preserve source and observation-date meaning. | P2 | 320 px card inspected with details open, no horizontal document overflow. |
| HARBOR | Existing chart controls must remain accessible after navigation. | P2 | Dashboard-to-chart and atlas-to-chart tests pass; prior keyboard/reduced-motion tests retained. |
| KEEL | Coherent metadata edits must not evade source checks. | P2 | Native module checks count, date, depth, source hash, period and width review. |
| KEEL | JavaScript rewriting unrelated numbers can invalidate a rejection test. | P2 | Shared Python fixture helper verifies rejection in native first; exact same bytes tested in WASM with M6-specific error assertions. |
| KEEL | Source changes require derived receipts to be regenerated. | P2 | Width/frame dependency, dashboard, query bundle, source index and engine manifest regenerated. |
| LOGBOOK | Numeric width coverage must not increase after a negative review. | P2 | Counts remain 114 descriptions / 62 owners; only review classification changes. |
| LOGBOOK | Earlier remote runs cannot stand in for current publication. | P2 | Draft above PR71; separate CI and mainline state remain unverified. |
| LOGBOOK | Role review and verification scope need a durable record. | P2 | This review and batch receipt ship with source, data and visualization changes. |

## Result and conditions

Native Rust's 41 tests and native/WASM builds pass. Observed-coverage browser
selection, Beck light, mobile card, observation date and chart navigation pass.
Three coherently altered metadata cases reject at the M6 checks in native and
WASM. The earlier six velocity-record mutation fixtures now also verify their
native and WASM M6-specific rejection reasons, rather than only checking for an
error. Existing dashboard coverage/update/outage/browser tests pass. All 49
JavaScript files and 14 page assignments pass their checks.

Full Python suite and generic collection browser results were pending when
this review was written; final results belong in the batch receipt. Remote CI
and mainline publication are separate remaining conditions.

Three amendments: separate the meaning of the excluded physical scales;
connect observed time evidence to coverage lights and observation dates;
replace numerically rewritten browser mutation fixtures with native-verified
source-preserving fixtures.

### Final local validation

Full Python suite passed: 1,183 tests and 918 subtests, 510.50 seconds. All 40
query collections passed native/WASM first/last-page and inspection checks.
All five focused owner-specific source/coverage tests passed after removing
brittle global-count assertions. Product/source bytes were unchanged by that
assertion refinement. Remote CI and mainline publication remain unverified.
