---
skill: roles-check
topic: guiana-regional-route
date: 2026-10-18
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Guiana regional route review

Seven functional lenses applied directly to the new source-linked input,
generated route/figure, catalog/state joins and query/dashboard integration.
This is internal editorial review, not independent oceanographic peer review.
ORBIT is excluded: there is no planetary comparison.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | Survey geography does not supply whole-current endpoints. | P3 | Input scope explicitly selects a regional corridor; preserve the studied-reach group and both ranking exclusions. |
| CURRENT | Surface current, deeper counterflow and freshwater bands must remain distinct. | P3 | Input layer/scope excludes counterflow and plume boundaries. No inferred flow-normal width, axis or transport. |
| CURRENT | Repeated 1988 surveys do not establish this line as a dated trajectory. | P3 | Time convention states geographic context only. Latest observation dates remain unchanged. |
| SOUNDER | Publisher HTML is OCR-derived; original print was not reviewed. | P2, open | Input locator and batch document disclose access limits. Inspect original survey charts before stronger station/axis claims. |
| SOUNDER | Every vertex and coordinate offset needs explicit authorship. | P3 | Input labels all vertices OSW-selected and scenarios editorial. Both source URLs and retrieval date are retained. |
| SOUNDER | Source-context dependency became stale after adding the catalog row. | P2, resolved | Rebind only the family audit's catalog hash, retain its scientific decisions and rerun protocol validation. No basin identity is added or reclassified. |
| CHART | Initial legend overlapped the eastern endpoint label. | P2, resolved | Move the map's northern display extent; leave vertices, 54 scenarios and all numeric distances unchanged. Final figure check separates legend and endpoint text. |
| CHART | Land clearance and GUIA contact use coarse display geography. | P3 | Existing geodesic densification/mask check and state relation role remain explicit; no physical passage claim. |
| CHART | NASA crop overlap is navigation context. | P3 | All scenarios fit level2_B_3; report labels display-route coverage rather than current identification. |
| BEACON | The 900 km figure could be mistaken for a whole-current length. | P3 | Card says 'Studied reach only' and excludes route ordering. Scope and method sit beside the number. |
| BEACON | The 700-900 km envelope is an assumption sensitivity. | P3 | Input, card and standalone legend distinguish finite scenarios from statistical/seasonal variability. |
| BEACON | Route coverage is different from completed measurements. | P3 | Batch states 70 owners/76 candidates but retains 11 published ranked lengths and 155 scoped widths unchanged. |
| HARBOR | The route must be reachable through keyboard navigation. | P3 | Actual browser covers map-to-card link, Enter activation and focused card. Preserve the existing focus contract. |
| HARBOR | A narrow embedded map needs a readable alternative. | P3 | 320 px card reflows, full-size SVG link and complete textual scope/scenario/source information remain present. |
| HARBOR | Color alone cannot communicate method. | P3 | Dashed nominal line, pale scenarios, endpoint labels and SVG title/description distinguish evidence classes in text as well. |
| KEEL | Optional Playwright cache was absent. | P2, resolved | Initial launch ran no assertions. Use the existing installed Chrome; subsequent complete focused browser gate passes without removing cases. |
| KEEL | Source/projection mismatch must fail in both runtimes. | P3 | Actual native and WASM reject both changed source hash and route projection; fixtures are served over HTTP. |
| KEEL | Predecessor full run is still live and has a failure marker. | P2, open | Independently reproduced the stale Aleutian-date assertion and fixed its successor with stronger link-removal invariance checks. Both affected dashboard cases pass. Preserve the full terminal result; successor combined gate remains required before release. |
| LOGBOOK | This work belongs in the continuing PR. | P3 | Branch codex/current-measurement-gaps / draft PR83; no new PR or merge. |
| LOGBOOK | Coverage lights should change only for the new route owner. | P3 | Preservation check finds only Guiana changes; all 239 other dashboard entries and all observation dates are unchanged. |
| LOGBOOK | Existing scientific evidence must remain reproducible. | P3 | All 75 earlier route files, 11 published lengths, 155 widths and seasonal-frame bytes unchanged; 91 engine and 166 research pins match. |

Roles reviewed: 7. P1: 0. P2: 5 (3 resolved, 2 open). P3: 16.
**APPROVED-WITH-CONDITIONS for editorial regional-route publication**.
No physical width or whole-current length admission and no main release.

CURRENT and BEACON agree that regional coverage must not imply a completed
whole-current measurement. SOUNDER and KEEL agree on preserving exact source
scope and dependency checks. The three applied amendments are the disclosed
OCR/vertex limitations, corrected legend extent and reviewed family-context
hash refresh. Open conditions concern stronger original-source/axis review
and a later complete combined gate; both remain visible in the batch record.
