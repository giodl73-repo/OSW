---
skill: roles-check
topic: loop-section-span-inventory
date: 2026-10-08
roles_used: [current, sounder, chart, harbor, keel]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal functional review

Selected CURRENT for metric interpretation, SOUNDER for provenance, CHART for mapped scope, HARBOR for equivalent navigation and KEEL for reproducibility. This is an internal review, not independent scientific admission.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | Component spans must not become flow-normal widths. | P2 | Inventory | Separate diagnostic category; measurements unchanged. |
| CURRENT | Five days per product do not establish annual extrema. | P2 | Diagnostic entry | Annual range null and eligibility false; negative tests. |
| CURRENT | Shared observations prevent treating products as independent confirmation. | P2 | Scope note | Explicit shared-altimetry limitation. |
| SOUNDER | Both product documents need immutable receipts. | P2 | Diagnostic sources | Exact paths and SHA-256 checks for both originals. |
| SOUNDER | A current must be counted once across products and dates. | P2 | Counts | One diagnostic owner; ten rows remain in query. |
| SOUNDER | Reclassification must preserve numerical observations. | P2 | Stored diagnostic documents | No diagnostic source or width measurement changed. |
| CHART | A map link could imply an observed full footprint. | P2 | Atlas card | Link named dated component spans; explicit scope beside it. |
| CHART | Query must isolate the intended current. | P2 | Visual URL | Loop current filter; browser verifies ten Loop rows. |
| CHART | Dates must remain distinguishable across products. | P2 | Query | Existing recorded-day query sorted by observation date; no seasonal interpolation. |
| HARBOR | Navigation must not depend on map color. | P2 | Table and card | Semantic text anchors in both locations. |
| HARBOR | Scope must be readable without opening JSON. | P2 | Table and card | Shared plain-text scope note. |
| HARBOR | Existing keyboard and mobile navigation must survive changes. | P2 | Registered browser check | Dashboard keyboard and 320 px reflow checks retained and passed. |
| KEEL | Inventory decision and counts must agree. | P2 | Validator | New decision correspondence and exact count validation. |
| KEEL | Bundles must reflect the new inventory receipt. | P2 | Generated data | Rebuilt dashboard, query corpus, index, native/WASM and engine manifest. |
| KEEL | Protected publication must retain default checks. | P3 | Publication | Local default tests and remote required gates; no bypass. |

Roles reviewed: 5. P1 blockers: 0. P2 issues: 14 addressed. P3 notes: 1 publication condition.

Verdict: APPROVED-WITH-CONDITIONS. The new category records existing diagnostics while retaining the physical width gap. Publication depends on required checks; broader current and eddy coverage remains incomplete.

Amendments made: separate diagnostic status and source receipts; direct mapped query links with explicit scope; inventory mutation checks and registered browser navigation assertions.
