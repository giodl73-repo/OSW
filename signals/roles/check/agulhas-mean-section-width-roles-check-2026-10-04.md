# Agulhas ACT mean-section width: roles review

Base commit: `629ed31`; working branch `codex/agulhas-mean-section-width`.
Artifact: scoped source extraction, validation and atlas/query presentation.
Internal functional review; independent scientific review remains required.

## Selection

CURRENT: mean boundary, depth and time support. SOUNDER: source access and
provenance. CHART: geographic class. BEACON: scalar interpretation. HARBOR:
controls and reflow. KEEL: reproducible joins and rejection checks. LOGBOOK:
local versus canonical status. ORBIT excluded: no analogy is introduced.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | Mean section must not become whole-current width. | P3 verified | 219 km restricted to ACT near 34 S; whole-current/ranking flags false. |
| 2 | CURRENT | Coast and mean zero isotach are not paired extracted velocity edges. | P2 resolved | New named metric and boundary class; validator rejects paired-zero reclassification. |
| 3 | CURRENT | Mean depth extent cannot set a width layer. | P3 verified | 3000 m retained as context; fixed layer null; mutation rejected. |
| 4 | SOUNDER | Publisher full article was inaccessible. | P3 open | Indexed publisher text and institutional abstract inspected; explicit HTTP 403/PDF/array limitations. Obtain original PDF before independent admission. |
| 5 | SOUNDER | Exact source scalar and support must remain bound. | P3 verified | Audit hash, source URL/locator, scalar, approximate latitude and period checked. |
| 6 | SOUNDER | Averaging interval is not exact occupied dates. | P3 verified | April 2010-February 2013 month precision; observed_period null. |
| 7 | CHART | A summary scalar might create a false footprint. | P3 verified | No boundary coordinates, section locator, route buffer or physical state join. |
| 8 | CHART | Full-width bar would imply recovered edge support. | P2 resolved | Bar omitted for Eulerian mean-section class. |
| 9 | CHART | Static route context needs its existing class. | P3 verified | Editorial route unchanged; source scalar displayed separately. |
| 10 | BEACON | Mean span must remain distinguishable from seasonal variation. | P3 verified | Title and interpretation state mean section and unknown annual range. |
| 11 | BEACON | Other arrays/model products are not annual margins. | P3 verified | Comparability restriction; proposed range [219,260] rejected. |
| 12 | BEACON | Readers need source and method access. | P3 verified | Inline width card links primary source and detailed record. |
| 13 | HARBOR | One mean state has no annual animation. | P3 verified | Play disabled; textual period and definition available. |
| 14 | HARBOR | Sharing must preserve selected evidence. | P3 verified | Current/phase share reload checked. |
| 15 | HARBOR | Narrow cards must keep limitations accessible. | P3 verified | 320 px reflow and visible textual evidence checked. |
| 16 | KEEL | Stale protocol/source dependencies could survive packaging. | P2 resolved | Refresh pinned inventory, seasonal and section receipts; dashboard/bundle rebuilt. |
| 17 | KEEL | Existing numerical widths must not change. | P3 verified | Prior 37 records and all Gulf/Loop section frames equal base commit. |
| 18 | KEEL | New interpretation needs executable rejection gates. | P3 verified | 15 scalar/context mutation cases; native/WASM and browser inspection checks. |
| 19 | LOGBOOK | Coverage totals must reconcile. | P3 verified | 38 records for 25 named currents; 68 unassessed; derived/scientific gates remain separate. |
| 20 | LOGBOOK | New source scalar is not canonical admission. | P3 verified | Canonical release diff empty; editorial status retained. |
| 21 | LOGBOOK | Publication must reflect actual Git state. | P3 open | Follow-up remains local and uncommitted; PR20 already merged separately. |

## Synthesis

Seven roles, 21 findings: zero open P1/P2, three resolved P2 issues, 18 P3
notes. APPROVED-WITH-CONDITIONS for local editorial presentation. CURRENT,
CHART and BEACON agree that mean-section support cannot create seasonal or
whole-current dimensions. Original-PDF and scientific admission remain open.

Verification: 59 focused Python tests and 399 subtests; 22 Rust tests;
source/bundle/WASM receipts; existing numerical records unchanged; browser
scalar/mean boundary, hidden bar/locator, disabled playback, source card,
share/reload, mobile and native/WASM inspection.
