---
skill: roles-check
topic: hydrographic-core-width-integration
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Hydrographic core width integration: internal editorial review

Artifacts: six source-extraction records, width validator, dashboard presence,
seasonal explorer, protocol and tests. Selected roles cover physical scope,
provenance, display grammar, explanation, accessibility, engineering and status.
ORBIT excluded: no planetary analogy. This review is not independent science
admission or a release gate.

| Role | Finding | Severity | Section / resolution or condition |
|---|---|---|---|
| CURRENT | Hydrographic width differs from velocity envelope. | P2 resolved | New metric and boundary equation; velocity threshold null. |
| CURRENT | Mixed locations could be animated as seasons. | P2 resolved | Comparability restriction disables playback; no annual range. |
| CURRENT | Local core cannot represent the entire current. | P3 condition | Whole-current and rank eligibility false. |
| SOUNDER | Width values must match pinned source extraction. | P3 verified | Audit SHA256 and matching section groups checked. |
| SOUNDER | Source range could acquire a fabricated midpoint. | P3 verified | Range retains null approximate value; validator rejects midpoint. |
| SOUNDER | Exact occupation dates and layer cannot be inferred. | P3 condition | Combined period and fixed layer null; campaign context labeled. |
| CHART | Bar might imply uniform full-current width. | P3 verified | Omitted for hydrographic-core records. |
| CHART | Missing geometry must not produce a route. | P3 verified | No section geometry or route drawn. |
| CHART | Selected section must remain identifiable. | P3 verified | Section labels appear in select, value and scope. |
| BEACON | Presence light could imply measurement admission. | P3 condition | Existing dashboard presence explanation retained; editorial status explicit. |
| BEACON | New range label could be generic or wrong. | P3 verified | Inventory table says local salinity-core span, not annual extrema. |
| BEACON | Source must remain accessible from measurement. | P3 verified | Source citation and locator retained on recorded view. |
| HARBOR | Every record needs text access. | P3 verified | Six selectable views plus common inventory rows. |
| HARBOR | Disabled playback must explain the reason. | P3 verified | Comparability text states mixed sections/occupations, not seasonal sequence. |
| HARBOR | Narrow view and return navigation need verification. | P3 verified | 320 px reflow, reload and atlas return pass. |
| KEEL | Boundary/provenance relabeling needs rejection. | P3 verified | Adversarial equation, hash, section and annual fixtures fail validation. |
| KEEL | Protocol checksum was stale after prior protocol edit. | P2 resolved | Updated inventory hash; standalone checker passes. |
| KEEL | Focused checks are not the full release gate. | P3 condition | Full clean-checkout repository suite not rerun. |
| LOGBOOK | Counts must reconcile all current decisions. | P3 verified | 100 decisions; 25 records / 16 names / 79 unassessed / four nonnumeric / one derived. |
| LOGBOOK | Canonical inventory must remain unchanged. | P3 verified | SHA256 retained; no new canonical measurement or ranking. |
| LOGBOOK | Method revision must accompany records. | P3 verified | Protocol v1.13, README and coverage note updated. |

## Synthesis and amendments

Seven roles / 21 findings: zero P1, three addressed P2 and 18 P3 verified notes or
conditions. APPROVED-WITH-CONDITIONS for scoped editorial integration.
CURRENT/SOUNDER/CHART agree that the property-core metric and mixed sampling
cannot become an annual velocity-width curve.

Three amendments: introduce and pin the metric-specific records; suppress
unsupported playback/width-bar/geometry and label ranges precisely; refresh
protocol checksum with offline validation. Width checker, 18 width tests,
15 dashboard tests and focused six-record browser pass. Screenshot inspected.
Canonical SHA256 remains
6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e.
Independent scientific admission and complete seasonal geometry remain open.
