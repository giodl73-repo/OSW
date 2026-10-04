---
skill: roles-check
topic: antilles-section-locator-correction
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 1
verdict: APPROVED-WITH-CONDITIONS
---
# Antilles section provenance correction

Internal review through installed role lenses, not independent science approval.
Seven lenses cover physics, provenance, maps, explanation, access, engineering
and status. ORBIT is not applicable. Reviewed source text, audit, planning
records, width inventory, regenerated dashboard and browser checks.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Cross-stream span cannot become along-current length | P3 | 49.4 km explicitly rejected as length. |
| CURRENT | Transport domain is not instantaneous current width | P3 | Site B is not admitted as a diagnosed edge. |
| CURRENT | Pressure-local peak cannot define whole-current layer | P3 | 400/900 dbar local mean context marked without whole-layer inference. |
| SOUNDER | Source locator incorrectly named Table 5 | P2 | Corrected active locators to Table 3; previous value retained only in correction history. |
| SOUNDER | Instrument coordinates are not axis endpoints | P3 | Table 1 A/A2/B/C coordinates carry nominal-instrument role. |
| SOUNDER | Access claims must describe actual recheck | P3 | Repository and AOML table text checked; failed web screenshot not used as image evidence. |
| CHART | Local section does not support an along-stream map | P3 | No candidate route manufactured; map stays a named locator. |
| CHART | Coastline domain is not a closed footprint | P3 | No source polygon or containment inferred. |
| CHART | General northwestward description leaves numeric gates unresolved | P3 | Endpoint review remains required. |
| BEACON | Transport seasonality might imply animated geometry | P3 | August-September transport months explicitly not geometry-playback eligible. |
| BEACON | Modern mean and historical surface results need separate scopes | P3 | Original naming distinction retained. |
| BEACON | Unresolved dimensions must be visible in card | P3 | Card summary explains section span and endpoint limits. |
| HARBOR | Source review must remain accessible from atlas | P3 | All 21 scope review cards and audit links pass browser check. |
| HARBOR | Longer source note could disrupt narrow cards | P3 | Existing mobile source-review regression passes. |
| HARBOR | Science caveats must accompany available evidence | P3 | Public summary keeps span-versus-width boundary beside source link. |
| KEEL | Correction must reach generated dashboard and planning index | P3 | Catalog, state join and dashboard regenerated; exact card locator inspected. |
| KEEL | Regeneration must preserve route coverage | P3 | Protocol audit passes 55 candidates / 3870 cases; 53 of 89 / 36 pending unchanged. |
| KEEL | Width validator must still accept inventory boundaries | P3 | 100-name inventory / 13 scoped records validate; 27 focused unit tests pass. |
| LOGBOOK | Correction is not new scientific admission | P3 | Canonical dimensions and release unchanged. |
| LOGBOOK | Old locator must remain auditable | P3 | Explicit dated previous/correct locator receipt added. |
| LOGBOOK | No length increase can be claimed from section documentation | P3 | Antilles retains zero route, reported-length and width capabilities. |

21 findings: 0 P1, 1 addressed P2, 20 P3 conditions. Approved for editorial
inspection with unresolved along-stream endpoints and physical width boundaries.
CURRENT and SOUNDER agree that a section domain cannot supply a current axis.

Primary source: Meinen et al. (2019), doi:10.1029/2018JC014836,
https://repository.library.noaa.gov/view/noaa/20909/noaa_20909_DS1.pdf .
Table 1 (PDF page 3), section 3.1, Table 3 (PDF page 15), seasonal discussion
and Fig. 11 (PDF pages 17-18) rechecked; AOML copy independently confirms
Table 3. No new curve digitization or velocity-array analysis.

Evidence: 27 focused unit tests (dashboard, width inventory, route catalog);
complete v1.2 route audit; width validation; all 21 scope-preview browser
checks with mobile reflow. Antilles still has no reference route, numeric
width, reported length or time frames. No full repository-suite claim.
