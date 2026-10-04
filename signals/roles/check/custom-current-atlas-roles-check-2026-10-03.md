---
skill: roles-check
topic: custom-current-atlas
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Custom current and eddy atlas review

Artifact: local atlas code, dashboard snapshot, navigation and state-evidence
join. These are internal installed role perspectives, not independent scientific
approval. CURRENT/SOUNDER assess scientific meaning and provenance;
CHART/BEACON/HARBOR assess cartography, explanation and access; KEEL/LOGBOOK
assess reproducibility and repository status. ORBIT is not relevant here.

| Role | Finding | Severity | Section | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | Editorial route crossings cannot establish physical current passage | P2 | Current preview state links | Resolved: nominal/scenario labels and explicit physical limitation accompany every route component. |
| CURRENT | A sampled reach is not a complete current | P3 | Current preview | Studied-reach label, layer, time and parent overlap notes retained. |
| CURRENT | Historical eddy polygon relations are date-specific | P3 | Eddy preview | Dated provider polygons, SSH proxies, center points and gateways remain separate kinds; no persistent footprint claim. |
| SOUNDER | Eddy state evidence needs an exact receipt | P3 | Dashboard builder and eddy preview | Records retain source file and row ID; snapshot pins input SHA256 and content fingerprint includes state evidence. |
| SOUNDER | Unknown state assessments must not become intersections | P3 | Dashboard builder | Unknown named-eddy footprint assessments excluded; missing exact dates remain unresolved. |
| SOUNDER | Scenario counts are not probabilities or annual frequency | P3 | Current preview | Explicit sensitivity interpretation beside counts; no seasonal-width inference. |
| CHART | Fine zoom could imply fine coastal measurement | P2 | Map context | Resolved: equirectangular projection, coarse coastline and approximate state geometry identified beside map; zoom does not add detail or precision. |
| CHART | Small coastal routes were hidden at regional zoom floor | P3 | Fit and zoom controls | Local route fit and lower zoom floor implemented; Ligurian vertices remain in fitted view. Name locators retain broad initial framing. |
| CHART | Longitude seams and aspect ratio must remain consistent | P3 | Projection and path drawing | Existing seam breaks, world clamps and 2:1 view ratio retained; this is an angular map, not an equal-area measurement surface. |
| BEACON | Readers need a short path from map to sources | P3 | Inline card | Full visual card, current record, state records and eddy evidence receipts linked. |
| BEACON | Data edits could be mistaken for active ocean events | P3 | Update indicator | Amber changes explicitly mean inventory edits since saved baseline, not live ocean activity. |
| BEACON | All selectable identities do not all have paths | P3 | Inventory status | 100 currents selectable, 45 with route cards; 136 named eddies and four dated detections separately counted. |
| HARBOR | Shared links lost the selected route component | P2 | Shareable address | Resolved: atlas-feature and atlas-route preserve current/component; fresh-page test verifies second component. |
| HARBOR | Names visible only on hover need equivalent keyboard access | P3 | SVG controls and selectors | Focus labels, Enter/Space activation and full current/eddy selectors remain available. |
| HARBOR | Mobile users need the same evidence and navigation | P3 | Inline card reflow | 320px card/map access and no horizontal document overflow checked. No automatic playback introduced. |
| KEEL | State links must match the actual generated join | P3 | Route-state browser check | All 99 candidate/state pairs verified including component-specific counts and state names. |
| KEEL | New eddy links need source-level checks beyond rendered counts | P3 | Eddy-state browser check | All four provider detections checked against released observation rows; admitted named-eddy assessment rows preserved and unresolved rows excluded. All 140 eddy cards exercised. |
| KEEL | Optional join failure must preserve usable cards | P3 | Atlas loader | 503 route/state inventory fallback tested; map and record remain available. Full clean-checkout offline suite remains a release gate, not claimed here. |
| LOGBOOK | Coverage counts must distinguish names, paths and links | P3 | Status record | 47 candidates/45 names; 99 current route/state links; 131 scoped eddy-state links documented separately. |
| LOGBOOK | Local review must not imply dataset publication | P3 | Publication boundary | Canonical release is not republished or scientifically certified by this UI review. No push or remote release performed. |
| LOGBOOK | Validation commands should be discoverable | P3 | README | Focused scripts listed in the current progress entry; broader scientific and publication work remains open. |

21 findings: 0 P1 / 3 P2 resolved / 18 P3 conditions or observations.
APPROVED-WITH-CONDITIONS for local research inspection. Full-current lengths,
seasonal footprints, independent scientific review, rights clearance and the
clean-checkout release suite remain outside this UI approval.

Three amendments: preserve component selection in share links; put projection
and coastline fidelity beside the map; retain typed, dated, source-linked state
evidence rather than generic intersection language. CURRENT, SOUNDER, CHART
and BEACON agree that visual navigation must preserve the evidence class.

Verification: seven dashboard unit checks; atlas browser check (100 current
selectors, 140 eddy selectors, local fit, component share, keyboard, pan and
mobile); record round-trip browser check; all 99 route/state pairs and optional
503 fallback; all 140 eddy cards and 131 state-evidence links with released
observation comparison. No whole-repository test result is asserted.
