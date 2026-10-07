---
skill: roles-check
topic: equatorial-basin-family-inventory
date: 2026-10-07
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_remaining: 1
implementation_p2_remaining: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Equatorial basin-family inventory — internal role review

Scope: five editorial proposals, one held naming convention, source-index integration, validation and generated bundles. This is an internal review of data handling and presentation, not independent oceanographic approval or canonical admission. ORBIT is omitted because no planetary comparison is involved.

Severity below records review concerns. “Resolved” means the candidate now addresses the concern; deferred physical evidence remains an admission gate. Required remote CI is a publication condition.

| Role / finding | Severity | Evidence and disposition |
|---|---|---|
| CURRENT: family names do not establish physical axes | P2 resolved | Five proposals retain null geometry, length and width; validation rejects promotion. |
| CURRENT: layer and time support cannot be inferred from a glossary | P2 resolved | Explicit null layer/time fields and worklist gates; no measured object added. |
| CURRENT: Indian NEC terminology may overlap Monsoon identity | P2 resolved | Held source-convention case records unresolved correspondence; no sixth proposal. |
| SOUNDER: source terms and OSW identifiers need separate provenance | P2 resolved | Audit preserves unqualified source term, basin, OSW proposed label, locator and inspection date. |
| SOUNDER: naming calendars must not become observed annual ranges | P2 resolved | Approximate source naming calendar has false annual-geometry support; negative test rejects promotion. |
| SOUNDER: live HTML is not an immutable measurement fixture | P3 deferred | Access is declared; source URLs/locators/date are retained. Acquire versioned geometry/data support before measuring. |
| CHART: proposal identities could inflate mapped current coverage | P2 resolved | Browser check preserves 100 map stations and 101 selector options while checking five separate proposal cards. |
| CHART: no supported routes for the proposed members | P3 deferred | Geometry remains null; map construction awaits layer, time and endpoint gates. |
| CHART: generic family lines cannot supply regional widths | P3 deferred | Width remains null; independent width and seasonal support required. |
| BEACON: qualified names could be mistaken for source-exact labels | P2 resolved | Cards explicitly describe OSW basin qualification and shared source family term. |
| BEACON: inventory counts could imply discoveries or admission | P2 resolved | Cards say pending review; work plan distinguishes proposals from newly discovered or admitted objects. |
| BEACON: unresolved naming convention should remain visible in evidence | P2 resolved | Held case is preserved in the separately queryable audit and explained in the plan. |
| HARBOR: new records need the same textual evidence as existing cards | P2 resolved | Existing semantic headings, source links and remaining-gate lists render each new record. |
| HARBOR: proposal access must not depend on map color or hover | P2 resolved | Inventory cards are textual and have individual fragment links; no new color-only encoding introduced. |
| HARBOR: selection and return behavior must survive a larger card list | P2 resolved | Atlas browser check includes mobile reflow and map/card navigation; current identities remain unchanged. |
| KEEL: new records must reach checked stores, not only loose JSON | P2 resolved | Both new audit and expansion worklist added to explicit source registry; corpus/bundles/engine rebuilt. |
| KEEL: inventory/audit mismatch needs an executable failure | P2 resolved | Protocol validator rejects differing parent, basin, label, dimensions, eligibility and input hashes; negative tests exercise mismatched inventory. |
| KEEL: stale fixed inventory expectations could hide regressions | P2 resolved | Changed expectations to 28 proposals and 65 sources; original geographic, monthly and source-byte checks retained. |
| LOGBOOK: local work must not be described as published | P2 resolved | Plan labels this a local candidate; no mainline receipt is rewritten. |
| LOGBOOK: frozen release facts must retain historical meaning | P2 resolved | Canonical 100-name ledger and frozen release files are untouched; 38 collections and 240 admitted objects remain. |
| LOGBOOK: required remote gate is not yet proven for this candidate | P2 publication condition | Open a reviewable PR after local verification; wait for both strict required CI contexts before merging. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. Implementation P2 issues remaining: 0. Publication condition: protected CI for the submitted commit. Physical admission gates remain open and are explicitly excluded from this editorial verdict.

Cross-role consensus: CURRENT, SOUNDER, CHART and BEACON require separation between names, identities, mapped geometry and measured dimensions. The audit, cards, checked source queries and validators preserve that separation.

## Amendments made

1. Preserve source terms and qualified proposals separately, and hold the Indian naming/calendar case rather than admitting an unresolved alias.
2. Add the evidence documents to the checked source corpus and validate inventory/audit agreement and physical-scope restrictions.
3. Keep the admitted-current map count fixed and exercise proposal cards, source queries and existing map/monthly interactions.

## Verification receipt

Confirmed so far: protocol audit passes (62 candidates, 4113 scenarios, 28 proposals); 9 protocol unit tests pass; 36 Rust unit tests pass; atlas, monthly-section, source-store and index-page browser checks pass. The source store checks all 65 original documents and native/WASM parity, including queries for the new proposals. The complete pytest suite passes with 768 tests and 585 subtests. Dashboard browser coverage also passes (240 records, update lights, rejection/outage behavior and mobile layout). All 28 proposal-card direct links, Back/focus restoration and mobile reflow pass. The standard-library baseline is still running at this receipt revision. Remote CI has not yet run for this candidate.
