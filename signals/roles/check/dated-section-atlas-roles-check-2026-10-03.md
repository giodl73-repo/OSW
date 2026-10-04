---
skill: roles-check
topic: dated-section-atlas
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Dated section atlas review

Internal installed-role review of the shared section locator, atlas integration,
background generator, seasonal view and browser evidence. Seven lenses apply;
ORBIT does not. Scientific dimensions and canonical admission are unchanged.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Section line could imply a longitudinal current axis | P2 | Bracket/dashed locator explicitly represents latitude support, not axis. |
| CURRENT | Band limits could become diagnosed velocity edges | P3 | Runtime refuses paired-edge relabeling; source definition retained. |
| CURRENT | Depth range could imply occupied volume | P3 | No polygon, extrusion or depth-uniform width depicted. |
| SOUNDER | Display coordinates need direct source support | P3 | Source longitude and latitude limits used without route vertices. |
| SOUNDER | Dated evidence needs nearby provenance | P3 | Dates, depth, boundary rule and source link in the card. |
| SOUNDER | Source locator must remain distinct from release geometry | P3 | Frontend support only; no new canonical geometry. |
| CHART | Default focus outline obscured the close-up line | P2 | Explicit stroke/shadow focus replaces oversized SVG outline. |
| CHART | Inherited labels/graticules overcrowded the local background | P3 | Coastline-only derivative for section closeups; same projection. |
| CHART | A very tight ocean-only view lacked regional context | P3 | Minimum regional viewport expanded; no measurement extent changed. |
| BEACON | Approximate span could be repeated as full width | P3 | Local band definition and exclusions accompany map. |
| BEACON | Map availability could imply route resolved | P3 | Axis, length and full width explicitly unresolved. |
| BEACON | Selection status must describe actual map mode | P3 | Dated section status replaces name-locator-only status. |
| HARBOR | Pointer selection alone is insufficient | P3 | Map line has button role and Enter/Space handling. |
| HARBOR | Accessible label was shortened during update rendering | P3 | Source role/date retained in dataset atlas label. |
| HARBOR | Mobile layout and global return need verification | P3 | 320 px reflow, reset and exact deep-link restore checked. |
| KEEL | Optional width failure could block atlas | P3 | Width loader returns null on failure; existing route views continue. |
| KEEL | Section could persist when switching phase/current | P3 | Seasonal container cleared on each phase render. |
| KEEL | Background must regenerate deterministically | P3 | Existing generator writes same-coastline derivative. |
| LOGBOOK | New visual should not imply more measured currents | P3 | Existing counts unchanged; visual support only. |
| LOGBOOK | Review needs evidence beyond DOM counts | P3 | Screenshots inspected; visual defects repaired and checks rerun. |
| LOGBOOK | Verification must not imply full repository certification | P3 | Focused checks documented; independent admission remains open. |

21 findings: 0 P1, 2 addressed P2, 19 P3 conditions. Approved for editorial
inspection. CURRENT, CHART and BEACON agree that source support must remain
visually distinct from current axes and footprints.

Amendments: typed source locator; explicit focus/background repair; contextual
viewport and visible source/date/depth meaning. Verified focused section maps,
coordinates, share reload, keyboard selection, global reset, stale view cleanup,
invalid role rejection and mobile reflow; 100-current/140-eddy atlas regression,
29 source previews and ten dashboard tests. Final screenshots inspected.
