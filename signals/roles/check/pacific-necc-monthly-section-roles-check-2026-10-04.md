---
skill: roles-check
topic: pacific-necc-monthly-section
date: 2026-10-04
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Pacific NECC monthly surface-section review

Artifacts: explicit source acquisition, pinned section inventory, draft protocol,
monthly diagnostic, profile figure, review page, width decision and dashboard.
CURRENT/SOUNDER cover science and source stewardship; CHART/BEACON/HARBOR cover
visual meaning, explanation and access; KEEL/LOGBOOK cover reproducibility and
repository accuracy. ORBIT is inapplicable. This is internal editorial review,
not independent scientific identity or measurement admission.

| Role | Finding | Severity | Artifact | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | Width of monthly mean flow differs from mean instantaneous width | P3 | Diagnostic | Metric and false mean-of-instantaneous flag preserve averaging order. |
| CURRENT | Largest eligible eastward peak is an operational component rule | P3 | Protocol | 2–10 N peak search and 0.1 m/s eligibility declared; branch identity review remains open. |
| CURRENT | One 2013 section cannot supply climatology or whole-current extrema | P3 | Scope flags | Annual whole-current dimensions null; Hsin/Qiu grid and period explicitly different. |
| SOUNDER | Nearest-date request returned an out-of-year sample | P2 | Acquisition | Addressed: parser rejected January 2014 before save; corrected end request acquired only 2013. |
| SOUNDER | Surface product coordinate can be mistaken for an instrument depth | P3 | Layer | Nominal 15 m recorded as product coordinate; no measured depth-resolved slice claimed. |
| SOUNDER | Saved source needs exact query, units, version and license | P3 | Manifest | Public query, metadata, source checksums, version 2017.0 and m/s units retained; no silent source replacement. |
| CHART | Axis and footer collided in the initial figure | P2 | SVG | Addressed: explicit label position and plotting margins; regenerated screenshot inspected. |
| CHART | Boundary lines can imply precision finer than the grid | P3 | Figure/table | Draft status and coarse sampling stated; 10 km display rounding separate from bracket coordinates. |
| CHART | Separate eastward components must not be bridged | P3 | Boundary method | First crossing encloses only peak-connected flow; no polygon or current axis inferred. |
| BEACON | Diagnostic range can be mistaken for an annual confidence interval | P3 | Summary | Range role states resolved local monthly means; uncertainty remains unresolved. |
| BEACON | Threshold alternatives are definitions, not error bars | P3 | Table | 0.05/0.1 m/s sensitivities labeled separately from zero-crossing span. |
| BEACON | Reader needs a short path from result to methods | P3 | Review page | Calculation brackets, sample timestamps, protocol and provider metadata linked. |
| HARBOR | Static figure needs a numeric alternative | P3 | Review page | Semantic twelve-row table accompanies descriptive image alternative text. |
| HARBOR | Monthly evidence should remain accessible without motion | P3 | Page | All profiles/table available together; no automatic playback. |
| HARBOR | Atlas and width-decision paths must work on small screens | P3 | Browser test | Both entry paths, selected-current return and 320 px document reflow pass; wide table scrolls locally. |
| KEEL | Missing or open boundaries must not become numeric full widths | P2 | Parser/measure | Addressed: no missing-value averaging or interpolation; null full span for missing/domain-stop cases; tests enforce. |
| KEEL | Derived artifacts need deterministic offline regeneration | P3 | Builder | JSON and SVG byte-identical rebuild verified; source version/query/hash drift rejected. |
| KEEL | Dashboard must pin calculation contents rather than frame counts | P3 | Builder/tests | Full diagnostic recomputed from pinned inputs; measurement/time fingerprints include evidence; false annual admission mutation rejected. |
| LOGBOOK | Acquired data and derived evidence need distinct status | P3 | Inventory | Source acquired; monthly widths derived pending scientific review; canonical ledger unchanged. |
| LOGBOOK | Counts should reflect a second derived series | P3 | Coverage | 27 source records/18 identities/75 unassessed/5 reviewed nonnumeric/2 derived pending recorded. |
| LOGBOOK | Focused validation cannot establish full release readiness | P3 | Review | Named checks only; no clean checkout, full suite, commit or publication claim. |

## Synthesis

Roles reviewed: 7. P1: 0. P2: 3 addressed. P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for the local review diagnostic.
Top finding: this is an explicitly selected surface-product component in monthly
means, not an official current envelope. CURRENT, SOUNDER and BEACON agree that
one year, one section and one boundary definition cannot establish representative
annual dimensions. Source coverage and definition sensitivity remain visible.

## Three amendments

1. Validate year, grid, units, product version and temporal coverage before
   saving provider responses; preserve the corrected exact request and checksums.
2. Stop boundary searches at missing samples and unclosed domain limits; never
   average away missing data or bridge westward gaps. Add adversarial fixtures.
3. Correct figure axis/footer spacing, supply a numerical table and test both
   atlas/width-decision navigation paths and narrow reflow before delivery.

## Verification and remaining gates

Passed: five diagnostic tests, 19 width-inventory tests, 18 dashboard tests,
offline source/width provenance checks, deterministic JSON/SVG regeneration,
and desktop/mobile review-page navigation. Figure screenshot inspected.
Canonical SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

Open: independent component/boundary admission, product-error assessment,
repeat years/sections, compatible products and representative seasonal dimensions.
No full current axis, ranked length, canonical width or annual whole-current
extrema admitted. The page currently shows saved profiles together; selected
monthly atlas playback is further interface work, not claimed complete here.
