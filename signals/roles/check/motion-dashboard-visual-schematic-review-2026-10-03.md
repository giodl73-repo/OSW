---
skill: roles-check
topic: motion-dashboard-visual-schematic
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1: 0
p2: 2
p3: 19
---
# Visual dashboard review

Internal role perspectives using the previously read role definitions; no
independent scientific approval is claimed. Review scope: visual map, schematic
and compact cards. ORBIT excluded: no planetary analogy.

| Role | Finding | Severity | Resolution / remaining condition |
| --- | --- | --- | --- |
| CURRENT | Route coverage is incomplete | P2 | 100 stations retained; isolated stations have no invented route. Physical network admission remains open. |
| CURRENT | Diagram bends cannot support length or width | P3 | Display geometry excluded from measurements and labeled schematic. |
| CURRENT | Eddy gateway cannot establish containment | P3 | Explicit regional inventory scope; no new current–eddy connections. |
| SOUNDER | Map origins must be reconstructable | P3 | Source geography, Loop context, candidate files and OSW SVG pinned. |
| SOUNDER | Dated outlines need dates | P3 | Geometry observation dates included in map scope note where recorded. |
| SOUNDER | Build time must not cause false recency | P3 | Object content baseline retained; observation-date rule unchanged. |
| CHART | First coastline view hid OSW states | P3 | Actual province field, mask and labels reused in OSW view. |
| CHART | Closely spaced world labels compete | P2 | Collision placement, regional scale and complete station index; dense areas still require regional inspection. |
| CHART | Path crossings can look like interchanges | P3 | No shared interchange symbols; crossing meaning explicitly disclaimed. |
| BEACON | Green is stored evidence, not active flow | P3 | Selected evidence meaning retained in all views. |
| BEACON | Gateway aggregation can overstate individual coverage | P3 | Aggregate counts and member records distinguish covered names. |
| BEACON | Schematic prototype could imply reviewed taxonomy | P3 | Browsing groups and geometry described as editorial; no canonical admission. |
| HARBOR | All currents must be discoverable | P3 | 100 world stations and 100 named index stations verified. |
| HARBOR | SVG requires keyboard equivalents | P3 | Enter/Space selection, accessible names, full text cards and index. |
| HARBOR | Cards consumed too much space | P3 | Five desktop columns, reduced padding and expandable evidence. |
| KEEL | Basemap must rebuild | P3 | Builder regenerates ground SVG from pinned OSW SVG. |
| KEEL | Changed records must also light on map | P3 | Amber markers tested with synthetic content change. |
| KEEL | Failure must retain usable inventory | P3 | Snapshot retention and narrow layout browser checks pass. |
| LOGBOOK | 100/136/4 must remain separate identities | P3 | Counts reconcile; eddy grouping opens source-scoped member records. |
| LOGBOOK | Source-specific route gates remain candidates | P3 | Route links preserve scope; diagram creates no canonical metrics. |
| LOGBOOK | Browser baseline is not global edit history | P3 | Existing browser-local update semantics retained. |

21 findings: 0 P1 / 2 P2 / 19 P3. Acceptable for local prototype inspection
with incomplete physical connectivity and dense-world-label conditions retained.
Verification: three unit tests and expanded browser test pass; atlas, Beck world,
compact-card and mobile images inspected. No publishing or external admission.

## Follow-up amendments

CHART/HARBOR: station overlap addressed using bounded 30-unit separation,
numbered stations 1–100, paint-layer separation and a matching text index.
Names are hidden until hover/focus, removing simultaneous-label clutter.
KEEL: browser checks prove number completeness, pairwise spacing and guarded
frame positions, not just DOM presence. The actual world render was inspected.
CURRENT/SOUNDER: two NOAA source-text continuation candidates retain null
physical junctions, fixed-depth intervals and transport estimates. Dashed
identity links expose their source and preserve the canonical boundary; naming
distinctions and regional membership are not silently converted to flow joins.
