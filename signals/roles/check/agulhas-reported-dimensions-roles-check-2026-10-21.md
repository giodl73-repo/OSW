---
skill: roles-check
topic: agulhas-reported-dimensions
date: 2026-10-21
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Agulhas reported-dimensions review

Internal application of the installed CURRENT, SOUNDER, CHART, BEACON,
HARBOR, KEEL and LOGBOOK lenses to source bytes, extraction, typed records,
shared UI and tests. This is not independent external scientific approval.

| Role / reason | Finding | Severity | Resolution |
|---|---|---|---|
| CURRENT / dimension scope | C01: The rediscovered 1000 km statement is already an unranked coastal variant. | P2 | Resolved: no new length claim or rank; preserve broader geographic support separately. |
| CURRENT | C02: A typical core description is not the ACT time-mean section width. | P2 | Resolved: separate 200/219 km metrics, related citation, no combined range or independent-observation count. |
| CURRENT | C03: Nearby speed, shelf and transport statements do not define width edges/layer/error. | P2 | Resolved: explicit unspecified fields; no physical envelope, annual extrema or width rank. |
| SOUNDER / provenance | S01: Original custody was missing for this review's dimension context. | P2 | Resolved: original PDF/XML, CC BY attribution, receipt, exact pins and offline acquisition verifier. |
| SOUNDER | S02: Prose extraction needs an independently checked original locator. | P2 | Resolved: rendered printed5970–5971/PDF4–5 and independent PDF text tests agree with XML. |
| SOUNDER | S03: Publication metadata previously described link-only use. | P2 | Resolved: reuse source ID and update original path, redistribution/license and checksums. |
| CHART / visual scope | M01: Drawing length by width would imply an unsupported area. | P2 | Resolved: separated scalar summaries; no rectangle, geographic width or source-figure tracing. |
| CHART | M02: Old route geometry must not appear recalibrated by 1000 km. | P2 | Resolved: geographic scopes stated; every geometry/reference/state row preserved. |
| CHART | M03: Seasonal width bar could turn an undated description into spatial evidence. | P2 | Resolved: undated phase non-playable; width bar hidden and actual UI checked. |
| BEACON / wording | B01: Source capture could be misreported as a newly discovered length. | P2 | Resolved: batch records the rediscovery and existing variant. |
| BEACON | B02: Measurement and publication dates could be confused. | P2 | Resolved: observation/averaging period unspecified in data and adjacent text. |
| BEACON | B03: Counts could imply an uncovered owner or annual range was filled. | P2 | Resolved: 158 records/83 owners; 18 uncovered owners and 89 unranked names remain. |
| HARBOR / equivalent access | H01: Scalar SVG text shrinks on phones. | P2 | Resolved: complete semantic definition list repeats facts and limitations at readable size. |
| HARBOR | H02: Query and map navigation need keyboard access. | P2 | Resolved: named links, Enter navigation and native/WASM record equality verified. |
| HARBOR | H03: Narrow card and source text could overflow. | P2 | Resolved: 320 px reflow passes; desktop and phone screenshots inspected. |
| KEEL / reconstruction | K01: Partial or coherently rebound editions could evade a simple hash gate. | P2 | Resolved: native exact row/source/owner/diagnostic checks and mutation cases; unknowns preserved. |
| KEEL | K02: Reference page still hardcoded a single supplemental width. | P2 | Resolved: regression exposed it; table uses native supplemental arrays and calculated counts/links. |
| KEEL | K03: Complete clean offline suite is still a release requirement. | P2 | Open release gate: focused Python, 106 Rust and actual UI gates; no fresh full-suite claim below disk guard. |
| LOGBOOK / operational truth | L01: Earlier source proof must not be represented as new integration CI. | P2 | Resolved: 23 reports/producers remain unchanged; fresh CI status recorded separately. |
| LOGBOOK | L02: Prior measurement export must not silently change meaning. | P2 | Resolved: immutable earlier export plus a named effective export, with old ranks/records retained. |
| LOGBOOK | L03: Work must accumulate without a PR per gap or loss of originals. | P2 | Resolved: same branch/draft PR83; only obsolete generated parts retired; originals preserved. |

Seven roles, 21 findings: zero P1; 21 P2 (20 resolved, one open release gate);
zero P3. **APPROVED-WITH-CONDITIONS for the continuing draft increment.**
Main merge/release remains gated. CURRENT, SOUNDER and BEACON agree that
source-custody and scoped-core coverage do not establish physical inventory
completion. Main remaining actions are the broader current measurement gaps
and a fresh complete validation run when storage permits.

Amendments applied: preserve the existing length variant's unranked support;
separate the core description from ACT and unknown edges; replace the hardcoded
width-table supplement with source-bound native records and verify the UI.
