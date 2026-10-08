---
skill: roles-check
topic: black-sea-eddy-recurrence
date: 2026-10-07
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Named Black Sea recurrence review

Internal seven-role review of the source extraction, protocol, Rust collection,
object cards, query sorting and dashboard fingerprints. Physics, provenance,
cartography, editing, accessibility, reproducibility and publication are selected
because each affects this quantitative atlas addition. Not independent peer review.

| Role | Finding | Severity | Section / recommendation |
|---|---|---|---|
| CURRENT | Presence per year and event lifetime are distinct statistics. | P2 | Resolved: separate named fields, meter and lifetime text. |
| CURRENT | Batumi narrative bounds cannot become a numerical duration. | P3 | Null event lifetime; retain early March/end October prose. |
| CURRENT | Monthly lifetime is not a fixed number of days. | P3 | Preserve original month units and mean/typical distinctions. |
| SOUNDER | The source does not establish the averaging window. | P2 | Resolved: observation period and detection criterion remain unknown. |
| SOUNDER | Source passage crosses the PDF columns. | P3 | Correct locator and visual inspection of printed page 633. |
| SOUNDER | Named regions must use exact existing identities. | P3 | Generator checks region IDs and basin; Rust verifies owner and label. |
| CHART | Calendar bars could imply continuous occupancy. | P2 | Resolved: presence meter is a descriptive average-year total; no monthly vector. |
| CHART | Regional locators cannot become footprints. | P3 | Null geometry; no new map mark, state join or NASA generation claim. |
| CHART | Dated maps near prose do not date the statistics. | P3 | No observation dates copied from Figure 2. |
| BEACON | Crimea is a mean event period, not a typical statistic. | P2 | Resolved after rendered source inspection; mean retained. |
| BEACON | Approximate numbers should remain qualified. | P3 | All summaries labeled about/approximate and publication year in citation. |
| BEACON | Nine records are not the global inventory. | P3 | Explicit source scope and unquantified Danube record remain visible. |
| HARBOR | A visual meter needs equivalent text. | P3 | Native meter, associated label, numeric text and scale caption. |
| HARBOR | Mobile must retain source and statistic labels. | P3 | 320 px reflow and screenshot verified. |
| HARBOR | Unknown recurrence must not display stale values. | P3 | Danube object has no summary; all nine exact native/WASM cards checked. |
| KEEL | Receipt edits must not promote summaries into dated events. | P2 | Resolved: coherent-receipt rejection checks plus Python extraction mutations. |
| KEEL | Changed source contents should affect dashboard updates. | P3 | Source/time fingerprints bind each summary and evidence query link. |
| KEEL | CLI rebuilds conflict with concurrent native checks on Windows. | P2 | Resolved: serialized final rebuild after the active check terminated. |
| LOGBOOK | Protected landing remains a separate gate. | P2 | Open: exact-head CI and publication pending. |
| LOGBOOK | Source PDF already has a reuse receipt. | P3 | Reuse existing CC BY 3.0 original, unchanged bytes and attribution. |
| LOGBOOK | Remaining full-goal gaps are substantial. | P3 | Retain width, length, season and footprint gaps in batch receipt. |

## Synthesis

Seven roles; P1: 0, P2: 7 (six resolved; publication open), P3: 14.
APPROVED-WITH-CONDITIONS. Final build serialization passed. CURRENT
and CHART agree on avoiding fictitious monthly occupancy and dated footprints.
SOUNDER and KEEL require matching existing identity and immutable source receipts.

## Amendments

1. Separate annual presence, event lifetime, narrative seasons and unknown dates.
2. Correct the Crimea statistic and preserve original day/month units in data/UI.
3. Bind checked receipts, reject scope promotion, and serialize final build/checks.
