---
skill: roles-check
topic: jutland-reference-route
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Jutland reference route and naming audit

Internal seven-role review of source scope, input/report/SVG, catalog, naming
audit and browser coverage. Selected physical, data, cartographic, editorial,
accessibility, engineering and stewardship lenses. ORBIT excluded without
planetary analogy. Not independent scientific approval.

| Role | Finding | Severity | Amendment or remaining condition |
| --- | --- | --- | --- |
| CURRENT | Source describes circulation, not an observed current axis | P2 | Editorial vertices/gates stated; physical support review remains. |
| CURRENT | Norwegian continuation is a different named object | P3 | Candidate ends before continuation; no identity merge. |
| CURRENT | Sea-level seasonality is not current length variability | P3 | No seasonal frame or numerical width inferred. |
| SOUNDER | Point gazetteer record supplies no endpoints | P3 | Canonical unknown retained; new route has independent editorial scope. |
| SOUNDER | Primary-source locators must support scope | P3 | Full Lenz Section 1.3 and Passaro Section 2 read and cited. |
| SOUNDER | Route sensitivity does not quantify measurement error | P3 | 54 scenarios and source-vs-OSW coordinate attribution explicit. |
| CHART | Route overlapped its legend on initial view | P3 | View box revised and screenshot inspected. |
| CHART | Coarse land clearance cannot validate shelf/current position | P2 | Existing coarse-mask limitation and bathymetry gate retained. |
| CHART | NASA/state navigation is geographic context | P3 | NECS and level2_C_1 retain editorial/geographic meaning. |
| BEACON | Approximate 400 km can look source-reported | P3 | Candidate status, OSW-selected route and source limits visible. |
| BEACON | North/South labels need unresolved status | P3 | Naming audit records source labels without aliases or lengths. |
| BEACON | Coverage needs both names and routes | P3 | 31 routes/29 names/60 awaiting; three studied reaches separate. |
| HARBOR | Map labels need readable separation | P3 | Legend above route; endpoints legible in inspected SVG. |
| HARBOR | Route evidence must have a text alternative | P3 | Card includes scope, layer, time, coordinate rule and endpoints. |
| HARBOR | New row must work in existing mobile review | P3 | Full browser suite reuses 320 px checks. |
| KEEL | New route must meet existing provenance rules | P3 | Unchanged generator; input/map/tile hashes and scenario audit pass. |
| KEEL | Ordering changes can invalidate stale UI expectations | P3 | Shortest route and touching-envelope positions updated from actual catalog. |
| KEEL | Scientific gates must remain separate from test success | P3 | No canonical or published rank eligibility. |
| LOGBOOK | Named branches could silently expand canonical taxonomy | P2 | Source-label audit only; canonical identity graph unchanged. |
| LOGBOOK | Chronological counts should remain auditable | P3 | Header updated; dated entry added without changing prior milestones. |
| LOGBOOK | Review is internal, not independent science | P3 | Physical naming/core/bathymetric and admission gates remain open. |


Seven roles, 21 findings, zero P1, three P2, eighteen P3.
APPROVED-WITH-CONDITIONS for editorial route comparison. Top finding: source
regional context does not establish this current axis or its exact gates.
CURRENT and CHART agree that physical coastal correspondence needs review;
BEACON and LOGBOOK agree that branch labels cannot become aliases silently.

Three amendments: declare selected offshore gates and exclusions; preserve
North/South labels in an unresolved audit; move legend away from the route.
Implemented. Protocol audit covers 31 routes/2160 scenarios; 35 focused tests
pass. Revised SVG visually inspected. Canonical measurements/ranks unchanged.

Width inventory and derived-section series audits also pass unchanged; no new width or seasonal data inferred for Jutland.

Full Chromium browser suite passes Jutland scope/source/crop navigation, 31/29/60 coverage, 28 comparison rows, revised shortest-route ordering and touching-envelope bounds alongside all existing atlas checks.
