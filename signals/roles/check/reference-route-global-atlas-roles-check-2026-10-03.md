---
skill: roles-check
topic: reference-route-global-atlas
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Global route explorer, direct cards and state inventory review

Internal installed role perspectives, not independent scientific approval.
CURRENT/SOUNDER cover physical scope and evidence; CHART/HARBOR cover atlas
meaning/navigation/access; BEACON covers explanation; KEEL/LOGBOOK cover build
and publication state. ORBIT is irrelevant to this interface.

| Role | Finding | Severity | Resolution / remaining gate |
| --- | --- | --- | --- |
| CURRENT | State crossings are diagram relations | P2 | Separate reference-route inventory from physical passage and eddy containment. |
| CURRENT | Route cards retain layer/time limits | P3 | Scope, source and sensitivity remain adjacent to visual map. |
| CURRENT | Unknown routes still need complete identity access | P3 | 100 current stations/select options; unresolved routes open existing record. |
| SOUNDER | Crossing sensitivity could imply probability | P3 | Counts explicitly cases within declared grid, not seasonal occurrence. |
| SOUNDER | Join depends on candidate versions | P3 | Catalog/candidate/state join inputs SHA256-pinned; stale candidate rejected. |
| SOUNDER | No new provider field acquired | P3 | Map uses existing local geometry and locators; no live-flow claim. |
| CHART | Global map and schematic have distinct geometry | P3 | New explorer uses CRS84 projected equirectangular ground and stored routes. |
| CHART | Date-line jumps must not draw across globe | P3 | Paths start a new subpath for seam jumps; wide bounds may retain world view. |
| CHART | Zoom does not supply current width | P3 | Stroke/circle size is display scale; no buffered footprint. |
| BEACON | All currents could imply all route maps exist | P3 | Status names 100 currents and 39 with cards; missing paths explicitly pending. |
| BEACON | Partial/seasonal components could imply whole-current route | P3 | Selection opens first declared card; text notes other components remain separate. |
| BEACON | Map return needs a clear label | P3 | Each card has Back to global current map link and permalink. |
| HARBOR | Pointer-only pan prevents equivalent access | P3 | Buttons/select plus map arrows, +, -, Home provided. |
| HARBOR | Late fragment rendering loses target | P2 | Reveal after card construction; focus target and reserve all image dimensions. |
| HARBOR | Main almanac overflowed at 320 pixels | P3 | Navigation wraps and evidence counts reflow; state-browser check now passes. |
| KEEL | Native late navigation could override card scroll | P2 | Intercept unmodified route-card anchors with pushState and explicit reveal; modifier behavior retained. |
| KEEL | Scenario joins need nominal/alternative distinctions | P3 | Unit checks cover all-case and scenario-only crossings, missing and invalid states. |
| KEEL | Optional join failure must not disable state browser | P3 | Catch optional-data error and preserve original state evidence; 503 checked. |
| LOGBOOK | State inventory must cover every state | P3 | 56 states, 90 candidate/state pairs, 40 with candidates; all 56 UI inventories checked. |
| LOGBOOK | Generated updates must stay synchronized | P3 | Catalog rebuild refreshes state join before dashboard. |
| LOGBOOK | Full scientific goal remains incomplete | P3 | 50 of remaining 89 lack routes; canonical dimensions and full eddy footprints remain open. |

21 findings: 0 P1 / 3 P2 / 18 P3. APPROVED-WITH-CONDITIONS for local inspection.
No physical-passage, footprint, transport or seasonal-size admission.
Cross-role consensus: complete identity navigation must retain incomplete
measurement evidence and keep diagram crossings separate from physical flow.

Amendments: (1) state-first candidate join with nominal/scenario distinctions;
(2) deferred fragment reveal and reserved image heights, plus controlled in-page
navigation; (3) zoom/pan/select atlas and an explicit map-card return loop.

Verification: two aggregation tests; browser checks for initial Agulhas and South
Atlantic fragments, image loading, focus, comparison links and browser Back;
100 atlas stations/options, zoom, drag pan, keyboard reset, route selection,
map return, pending-route record and 320px reflow. All 56 state inventories,
expanded scope text, mobile layout and optional-join 503 retention inspected.
Global atlas screenshot visually inspected. No full default-suite claim.
