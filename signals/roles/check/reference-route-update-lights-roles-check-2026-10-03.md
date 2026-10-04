---
skill: roles-check
topic: reference-route-update-lights
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Global atlas update indicators and return navigation

Internal installed role perspectives, not independent scientific approval.
CURRENT/SOUNDER cover update meaning and provenance; CHART/BEACON/HARBOR
cover visual interpretation and access; KEEL/LOGBOOK cover consistency and
verification. ORBIT is irrelevant to this navigation/data-presence interface.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Update light could imply live ocean change | P2 | Summary explicitly inventory edits, not live ocean activity. |
| CURRENT | Historical evidence updates do not refresh observation date | P3 | Uses content fingerprint; scientific dates and geometry roles unchanged. |
| CURRENT | Update state does not constitute scientific approval | P3 | Existing route and source caveats retained. |
| SOUNDER | Build timestamps should not cause spurious updates | P3 | Fingerprints exclude build time; changed-timestamp browser fixture remains zero. |
| SOUNDER | Baseline must match dashboard evidence | P3 | Shared version-2 localStorage fingerprint/section receipts and storage event. |
| SOUNDER | Fresh visit has no known prior content | P3 | Establish initial baseline; no claim of detecting historical unseen changes. |
| CHART | Shared gateway represents many unresolved locations | P3 | Changed marker means one or more underlying records; accessible count and selection list. |
| CHART | Selected and updated markers have different meanings | P3 | Selected fill and update outline; text status provides exact change scope. |
| CHART | Source route meaning must survive highlight | P3 | Paths remain editorial geometry; amber adds inventory state, no flow or dimension. |
| BEACON | A count alone does not explain what changed | P3 | Identity/source/claims/measurements/routes/media/time group labels retained. |
| BEACON | Current selection scrolls beyond update summary | P3 | Each changed current's map card gets its group-specific note. |
| BEACON | Refresh should reload joined artifacts consistently | P3 | Full page refresh reloads catalog/reports/snapshot rather than mixing old routes with new indicators. |
| HARBOR | Change detection cannot rely on color | P3 | Live count summary, accessible marker names, selection text and card notes. |
| HARBOR | Native return could leave wrong content on screen | P2 | Global return uses explicit focus/scroll; browser verifies actual atlas position. |
| HARBOR | Added controls might overflow narrow viewport | P3 | Wrapping controls pass 320px reflow check. |
| KEEL | Cross-tab acknowledgement could leave stale outlines | P2 | Storage listener rerenders marks and removes notes; two-tab browser test passes. |
| KEEL | Corrupt snapshot must not overwrite baseline blindly | P3 | Schema/version/identity/fingerprint/map-feature validation before establishing baseline. |
| KEEL | Current and eddy navigation must survive new controls | P3 | Existing 100-current/140-eddy selection and direct-card tests pass. |
| LOGBOOK | Seen baseline is browser-local, not a global data revision | P3 | Language states saved baseline; no server acknowledgement or scientific review mutation. |
| LOGBOOK | Screenshot must show actual intended state | P3 | First screenshot exposed return bug; repaired, recaptured and inspected atlas view. |
| LOGBOOK | Full data inventory remains unfinished | P3 | No completion claim for remaining 48 routes, dimensions, seasonal geometry or eddy footprints. |

21 findings: 0 P1 / 3 P2 / 18 P3. APPROVED-WITH-CONDITIONS for local atlas
inspection. Amendments: inventory-change interpretation; actual atlas return
focus/scroll; shared-tab acknowledgement. Cross-role consensus: evidence edits
need a visible explanation without implying physical ocean motion or approval.

Verification: update-indicator browser test covers initial baseline, content
changes, current/eddy/group indicators, measurement/claim labels, card notes,
refresh, acknowledgement across tabs, build-time stability and mobile reflow.
Existing atlas and direct-card navigation checks pass. Screenshot visually
inspected after repairing return behavior. No full default-suite claim.


Visual follow-up: the refreshed screenshot exposed invalid SVG serialization
with duplicated xmlns declarations when a route module registered the default
namespace. Repaired the ground builder to use a namespaced root and one serializer
namespace. Added a regression test that parses the generated SVG and checks both
province field and labels. Seven dashboard unit tests and update browser check
pass; screenshot recaptured with recognizable geographic/province ground.
