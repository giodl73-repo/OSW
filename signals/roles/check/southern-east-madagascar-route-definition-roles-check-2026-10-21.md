---
skill: roles-check
topic: southern-east-madagascar-route-definition
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal functional review: route-definition experiment

Review data/protocol, operator, Rust contract and current-card figure through
the seven applicable installed roles. ORBIT is omitted because no planetary
claim is made. This is internal editorial review, not independent scientific
approval. Publication scope is the existing draft PR83; main merge is excluded.

| Role | Finding | Severity | Resolution / condition |
|---|---|---|---|
| CURRENT | An offshore polyline is not a layer-specific current axis. | P2 resolved | Keep route/physical-axis admission false; no new route row. |
| CURRENT | A26.1S offshore approach differs from the source25.5S coast. | P2 resolved | Both endpoint conventions visible; current termination remains unresolved. |
| CURRENT | No date or seasonal support can be borrowed from the April2001 width. | P2 resolved | Undated contextual geometry; no seasonal playback or annual extrema. |
| SOUNDER | All27 failed coastal conventions must remain accessible. | P2 resolved | Original input, full rejection list and reproduction retained. |
| SOUNDER | Publisher HTML is read; original figure/checksum unavailable. | P3 | Explicit access mode and linked citation, no invented checksum. |
| SOUNDER | Retain the source650km report independently of the new calculation. | P2 resolved | Published measurement and rank unchanged;218.574km difference is arithmetic only. |
| CHART | Coarse land clearance does not verify bathymetry or shelf correspondence. | P2 resolved | V2 remains diagnostic, with next required evidence stated. |
| CHART | A diagnostic must not silently add a mapped current. | P2 resolved | Current map features stay empty; reference-route catalogue remains76. |
| CHART | Route sensitivities can be mistaken for a current width or physical range. | P2 resolved | Legend and adjacent text identify arbitrary cartographic sensitivity; no width/area. |
| BEACON |900km versus650km can suggest a correction to the paper. | P2 resolved | Distinct definitions/endpoints and no calibration stated beside figure. |
| BEACON | A failed experiment can look like completed gap filling. | P3 | Route remains unresolved in heading, data status and batch plan. |
| BEACON | Short route-to-source path is needed. | P3 | Exact query link and source citation on current card. |
| HARBOR | Figure meaning must not depend on color. | P3 | Text, descriptive alt/title and exact data alternative. |
| HARBOR | Keyboard activation should reach the diagnostic directly. | P3 | Focus/Enter browser gate required. |
| HARBOR |320px reflow must retain the scope explanation. | P3 | Responsive image plus adjacent prose; phone browser/visual gate required. |
| KEEL | Missing successful/failed alternatives can bias the range. | P2 resolved | Python recomputes all27+27 cases and negative mutation tests. |
| KEEL | Rehashed mutations must not promote geometry or dimensions. | P2 resolved | Rust binds exact diagnostic and dependency pins; negative admission/erasure checks. |
| KEEL | Complete new-head local suite is not available under current disk guard. | P2 open before merge | Retain774e466 full-suite evidence; report focused gates and CI separately. Draft publication only. |
| LOGBOOK | Source datasets and unrelated report bytes must remain unchanged. | P3 | Baseline preservation gate required before push. |
| LOGBOOK | Do not create a PR per experiment. | P3 | Continue branch and draft PR83, no main merge. |
| LOGBOOK | Counts and remaining work must describe actual admission state. | P3 | Diagnostics51; route inventory76, current101, ranked lengths12, widths157 unchanged. |

Roles reviewed:7. P1 blockers:0. Open P2:1 before merge (complete new-head
suite);11 other P2 findings resolved by retaining diagnostic-only scope.
P3 notes:9. Verdict: APPROVED-WITH-CONDITIONS for draft-branch publication,
subject to focused build/browser, preservation and staged-pin gates. This
verdict does not approve a scientific route or merge.

Top finding: the experiments expose an unresolved endpoint/geometry definition,
not a recovered current path. CURRENT, CHART and SOUNDER agree. Amendments:
retain every rejected attempt; isolate the offshore experiment from the route
catalogue; place the650/900km definition difference next to the figure.

Executed gates:10 Python tests;91 Rust tests; native/WASM and native atlas;
exact diagnostic browser query, keyboard link and320px reflow; desktop/phone
visual inspection;818 complete staged dependency pins;65-file JS syntax and
14 page validation assignments. All54 attempts retained. Preservation confirms
50 prior diagnostics,46 other collections,19 scientific reports, historical
release and all101 seasonal plans unchanged (bundle hash necessarily changes).
Complete new-head suite remains the one open P2 condition before merge.
Prior711e22d scientific reproduction/NetCDF checks passed; offline acquisition
timed out before tests on both Hawaii Qiu–Chen2010 URLs. Draft branch only.
