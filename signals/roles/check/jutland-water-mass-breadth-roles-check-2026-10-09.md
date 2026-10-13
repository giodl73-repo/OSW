---
skill: roles-check
topic: jutland-water-mass-breadth
date: 2026-10-09
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal review: Jutland water-mass breadth

Artifact: original-source extraction, protocol, inventory, source corpus, Python
and native/WASM guards, atlas/inspector display and validation. Seven installed
roles apply. ORBIT is excluded because this artifact introduces no analogy.
This is one agent applying the role lenses, not an independent scientific panel.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | A water-mass breadth can be mistaken for velocity-core width. | P2 | Protocol 1 / record | Quantity class, source method and visible caption explicitly retain surface-water-mass scope; no rank or full-width inference. |
| 2 | Surface wording does not supply fixed depth bounds. | P2 | Protocol 5 | Depth bounds remain null; 15–30 m habitat bathymetry excluded. |
| 3 | Temperature/salinity variability and bird seasons do not provide seasonal widths. | P2 | Protocol 5 | No calendar, occupations, annual extrema or playback; promotion tests reject these claims. |

## SOUNDER — provenance and uncertainty

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | The geographic synthesis cites an unreviewed underlying source. | P2 | Audit | Nielsen (1999) unresolved status retained in both record and display; independent scientific admission pending. |
| 2 | Mutable agency downloads require identity verification. | P2 | Acquisition / checker | PDF SHA256 and byte count pinned; strict acquisition helper and audit integrity checks. |
| 3 | The report's Open classification is not an explicit redistribution license. | P2 | Receipt | Original remains excluded from Git; only factual extraction, citation and annotations distributed. |

## CHART — cartography

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | No paired geographic edges support a route-width band. | P2 | Protocol 6 | Existing editorial route stays separate; no new geometry or width polygon. |
| 2 | The modeled December 2018 map can wrongly date the breadth. | P2 | Audit context | Map month retained as context with false width-support flags; no field digitization. |
| 3 | 10/20 km endpoint labels can collide on narrow cards. | P2 | Original regional chart | Close endpoints align outward; browser check measures disjoint text boxes at 320 px. |

## BEACON — public science

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | 40 km habitat and 100 km traceability can inflate the current span. | P2 | Caption / note | Distinct context with explicit exclusions; numeric substitutions rejected. |
| 2 | 10–20 km may be repeated as annual minimum/maximum. | P2 | Caption | No seasonal range, confidence interval or midpoint; all date/extrema fields unavailable. |
| 3 | North/South labels can be silently merged into a generic current. | P2 | Naming context | Report's Jutland label retained; naming audit unchanged and pinned; no canonical alias or downstream inheritance. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | A span bar alone does not communicate the water-mass limitation. | P2 | SVG description | Scoped aria label repeats quantity, geography and exclusions. |
| 2 | Reduced viewport width can make text unusable. | P2 | Browser validation | Reflow, minimum rendered text size and endpoint-box separation tested at 320 px. |
| 3 | Source access should not require pointer map interaction. | P2 | Source navigation | Existing semantic source link opens the exact audit array pointer; native/browser result parity checked. |

## KEEL — reproducibility

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Context erasure or owner transfer can bypass editable receipts. | P2 | Trusted Rust registry | Known ID checked independently of owner/context; coherent native and WASM mutations rejected. |
| 2 | Seasonal-frame and query inputs become stale after inventory edits. | P2 | Builders | Dependency SHA refreshed and dashboard/source/query/native/WASM artifacts regenerated. |
| 3 | Source acquisition failures must not be reported as test failures. | P2 | Batch parent validation | Exact failed run and failed acquisition step recorded; companion run's passed build/test gates identified; source pins retained. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| 1 | Scoped evidence coverage is not scientific completeness. | P2 | Batch | 106 records/58 owners/34 unassessed explicitly include summaries, not full dimensions. |
| 2 | Internal roles approval can be mistaken for independent admission. | P2 | Review heading / record | Internal scope and pending science stated throughout. |
| 3 | Indexed original excerpts are not inspected original figures. | P2 | Research lead | Rydberg original not acquired, figures uninspected, no width admitted; recovery action retained. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. P2 issues: 21 addressed through scope
restrictions, source pins, display changes and executable checks.

Verdict: APPROVED-WITH-CONDITIONS for editorial publication after validation.
Underlying water-mass boundary methods, alias relations, geographic edges and
seasonal widths remain unresolved scientific gates, visible in the record.

Top finding: Preserve the water-mass breadth class throughout storage and display.
CURRENT, SOUNDER, CHART and BEACON agree on that restriction.

Amendments applied:

1. Source, location, layer and time distinctions are bound in the complete audit row.
2. Native/WASM identity validation protects coherent edits and context deletion.
3. Close numeric labels align outward while scope remains visible and queryable.

Validation completed: 1,045 Python tests / 918 subtests and 41 Rust tests passed.
Jutland and existing Baffin shipped browser checks passed. New card screenshot
was visually inspected at 320 px; source acquisition and dependency pins passed.
Remote CI and independent scientific admission remain separate gates.
