---
skill: roles-check
topic: reference-route-eddy-atlas
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Current and eddy global atlas

Internal installed role perspectives; not independent scientific approval.
CURRENT/SOUNDER cover physical meaning and evidence; CHART/BEACON/HARBOR
cover atlas interpretation, explanation and access; KEEL/LOGBOOK cover code
and inventory fidelity. ORBIT is not relevant to this interface.

| Role | Finding | Severity | Resolution / remaining condition |
| --- | --- | --- | --- |
| CURRENT | 100 ring names share a regional gateway | P2 | Group into one marker; per-name selection explicitly states no individual center or footprint. |
| CURRENT | Stored polygons are historical snapshots | P2 | Show observation date and historical status on selection; do not imply simultaneous live eddies. |
| CURRENT | SSH contour proxy differs from an operational polygon | P3 | Preserve feature role in selected explanation; do not relabel proxy as observed material boundary. |
| SOUNDER | Source geography points are not eddy axes | P3 | Selection explicitly describes locator and unresolved footprint/trajectory. |
| SOUNDER | An approximate reported center has distinct evidence | P3 | Separate center language from generic geography-locator language. |
| SOUNDER | No new dimensional evidence is acquired | P3 | No radius, area, transport, seasonal range or canonical measurement admission. |
| CHART | Shared names must not be displaced into fictional positions | P3 | Render one gateway at stored location; never spread names across fabricated centers. |
| CHART | All currents remain accessible above eddy layer | P3 | Current stations remain above purple layer; selectors provide access to overlaps. |
| CHART | Polygons and point locators need different symbols | P3 | Purple outlines versus purple circles, with textual explanation. |
| BEACON | Inventory totals can become stale after updates | P2 | Status derives current/name/detection counts from loaded snapshot. |
| BEACON | Current and eddy record actions have different destinations | P3 | Current route cards open directly; eddy selection exposes explicit record link. |
| BEACON | Names should appear only on hover/focus | P3 | Point labels hidden except hover/focus; polygon labels use accessible names/native titles. |
| HARBOR | Aggregated marker must support keyboard activation | P3 | Enter/Space zoom gateway and focus eddy selector without navigating to an arbitrary name. |
| HARBOR | Dense overlays need a visibility control | P3 | Show eddies checkbox; selecting an eddy restores layer visibility. |
| HARBOR | Additional selectors could overflow small screens | P3 | Wrapping controls; 320px browser check passes. |
| KEEL | Current navigation must survive eddy support | P3 | Existing zoom/pan/Home/route-card/return checks pass after implementation. |
| KEEL | Selecting a group could retain previous record action | P3 | Clear selection and hide link when opening shared gateway. |
| KEEL | Full inventory coverage cannot rely on one example | P3 | Browser selects all 140 eddy/detection IDs and checks each record URL and relevant evidence label. |
| LOGBOOK | Five polygons do not imply 140 footprints | P3 | Test five polygon elements; explain unresolved identities separately. |
| LOGBOOK | Screenshot should verify actual map rendering | P3 | Current/eddy screenshot inspected: geographic ground, purple markers and controls visible. |
| LOGBOOK | Full atlas science remains incomplete | P3 | Keep goal active: remaining routes, lengths, widths, seasonal geometry and identity-specific eddy footprints require further evidence. |

21 findings: 0 P1 / 3 P2 / 18 P3. APPROVED-WITH-CONDITIONS for local inspection.
All three P2 interface issues amended: shared-gateway grouping, dated scope
labels, and snapshot-derived status totals. Scientific completeness is not
claimed. Cross-role consensus: complete name access must preserve incomplete
location evidence and distinguish dated geometry from live flow.

Verification: focused browser test passed for 100 current stations, current
navigation and return, every 140 eddy/detection records, dates for all five
polygons, shared gateway keyboard activation, layer toggle, and 320px reflow.
Screenshot: figures/reference-route-current-eddy-atlas-review.png. No full-suite
or independent scientific review claim.
