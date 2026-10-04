---
skill: roles-check
topic: atlas-dated-surface-navigation
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Dated surface evidence in the current atlas

Internal review through installed role lenses; not independent scientific approval.
Artifacts: dashboard generator and data, atlas script and styles, focused tests,
and inspected screenshot. ORBIT is not applicable.

| Role | Finding | Severity | Section | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | An analyzed front is not a current centerline | P3 | Dated views | Front method and side retained; no whole-current length inferred. |
| CURRENT | A geostrophic diagnostic covers a partial reach | P3 | Diagnostic | Exact released role and scope note shown. |
| CURRENT | Different dates cannot establish simultaneous bounds | P3 | Time | September 25 diagnostic and September 28 fronts separately selectable; no width inferred. |
| SOUNDER | Geometry belongs to Gulf Stream System, not the Gulf Stream segment | P3 | Identity | Exact released owner retained; segment receives no geometry. |
| SOUNDER | Source links need a reproducible local receipt | P3 | Provenance | Released source URL and snapshot repository path preserved and tested. |
| SOUNDER | Display changes must not manufacture new observations | P3 | Release | Exact frozen coordinates and dates checked; no provider acquisition claimed. |
| CHART | Three existing dated lines were absent from the global atlas | P2 | Map | Supported dated roles drawn and selectable from global map and card. |
| CHART | Coarse OSW ground is not scientific spatial precision | P3 | Projection | Existing display caveat retained; exact line geometry preserved. |
| CHART | Shared selection must preserve the selected front | P3 | Navigation | Geometry query parameter restores each exact saved view on fresh load. |
| BEACON | Colors alone cannot communicate method and date | P3 | Card | Explicit method/date text, side labels and source note shown. |
| BEACON | Saved dated evidence is not seasonal animation | P3 | Explanation | No annual extent or width inferred; existing series link retained. |
| BEACON | Showing three lines must not increase route coverage counts | P3 | Coverage | Existing frozen geometry exposed; 55 candidates / 53 of 89 unchanged. |
| HARBOR | Focus outline obscured a large area of the map | P2 | Focus | Replaced bounding-box outline with visible line highlight and glow; screenshot inspected. |
| HARBOR | Hover names need keyboard equivalents | P3 | Input | Focus labels, Enter/Space selection and compact buttons available. |
| HARBOR | Dated controls must fit narrow cards | P3 | Reflow | Compact labels and grid; 320 px checks pass without horizontal overflow. |
| KEEL | New metadata must match released geometry | P3 | Generator | Nine dashboard tests include exact coordinates, date, side and receipt comparisons. |
| KEEL | Family navigation could override a selected view's extent | P3 | Fit | Dated fit runs after family handling; component regression passes. |
| KEEL | Browser verification must use a working installed runtime | P3 | Verification | Installed Chromium headless shell 1223 used; focused test accepts OSW_TEST_BROWSER. |
| LOGBOOK | Inventory update lights are not live ocean changes | P3 | Updates | Existing inventory fingerprint semantics retained. |
| LOGBOOK | Successful UI checks do not complete scientific admission | P3 | Status | Measurement, taxonomy and publication gates remain open. |
| LOGBOOK | Verification claims need a bounded record | P3 | Evidence | Specific unit and browser checks listed below; no complete-suite claim. |

21 findings: 0 P1, 2 P2 addressed, 19 P3 conditions. Approved for editorial
inspection with conditions: dated fronts and diagnostics remain distinct;
no annual geometry, inferred width or whole-current axis is admitted.
CURRENT and SOUNDER agree that geometry identity and method must survive navigation.

Evidence: nine dashboard unit tests; test_atlas_dated_current_browser.py
(exact shared-view restoration, keyboard, source receipts, mobile and reset);
test_atlas_component_navigation_browser.py (seven families, 17 links);
test_reference_route_atlas_browser.py (100 current selections, 140 eddy
records, navigation and mobile). Screenshot inspected after focus and compact
control fixes: figures/atlas-dated-surface-card-review.png. Canonical ledger
SHA-256 remains 6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e.
