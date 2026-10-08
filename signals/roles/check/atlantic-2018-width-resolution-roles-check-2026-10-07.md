---
skill: roles-check
topic: atlantic-2018-width-resolution
date: 2026-10-07
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Atlantic 2018 width resolution review

Internal seven-role review of the new protocol, two published scalar records, independent cruise identity evidence, source/query integration and visual context. Role selection covers physics, stewardship, cartography, public explanation, accessibility, reproducibility and publication. This is not independent scientific peer review.

| Role | Finding | Severity | Disposition |
|---|---|---|---|
| CURRENT | Two scalar distances are transport-selected local section spans. | P3 | Keep geometry null and whole-current/rank/annual/playback flags false. |
| CURRENT | Nominal latitude correction does not recover measurement endpoints. | P2 | Resolved: separate cruise correspondence from unresolved station pairings. |
| CURRENT | Cruise year grouping is not a decade mean or annual range. | P3 | Retain original cruise window and density-layer support. |
| SOUNDER | Publisher Table 1 and Table 2 nominal labels conflict. | P2 | Resolved: preserve original 19 S cell and attach independently checked A09.5_24S identity evidence. |
| SOUNDER | The independent source must not become the width source. | P3 | Keep the 47/108 km values transcribed from publisher Table 2 only. |
| SOUNDER | Additional source dependencies need checked provenance. | P3 | Bind source/acquisition/parser hashes into extraction and query bundle. |
| CHART | Sampling maps do not encode a 47/108 km geographic edge. | P3 | Continue unconnected cruise context points and explicit unresolved boundaries. |
| CHART | Independent bars require a common zero base and units. | P3 | Retain existing scalar chart and display exact published values. |
| CHART | Original nominal label and corrected context should be visible together. | P3 | Add nearby 2018 correction explanation and primary archive link. |
| BEACON | A correction could appear to repair the original paper. | P3 | Say the original cell is retained; explain the independent correspondence. |
| BEACON | More records do not mean more current owners. | P3 | Report 71 records for 35 owners; unassessed owner count remains 58. |
| BEACON | No new seasonal width range is established. | P3 | Keep separate sections/years/layers and unreported uncertainty explicit. |
| HARBOR | Correction evidence must be discoverable without hover. | P3 | Use visible paragraph, semantic primary-source link and query details. |
| HARBOR | New bar/table rows must remain readable at narrow widths. | P3 | Retain 320 px scrollable charts/tables and keyboard support. |
| HARBOR | Direct record links need the new rows selectable. | P3 | Exercise all 32 records in source cards, query and sampling maps. |
| KEEL | Updating an extraction could alter previously sourced measurements. | P2 | Resolved: exact comparison preserves all previous 30 cruise and 39 other measurement contents. |
| KEEL | Invented reconciliation evidence must fail validation. | P3 | Add a mutation test and require pinned independent archive identity. |
| KEEL | All generated dependencies must refresh coherently. | P3 | Rebuild inventory, frames, dashboard, query, source index and native/WASM manifest. |
| LOGBOOK | Protected-main publication is not established by local tests. | P2 | Open condition: require exact-head checks and protected landing. |
| LOGBOOK | v1 protocol and earlier batch receipts are historical. | P3 | Keep them; add a v2 protocol and a distinct correction-batch receipt. |
| LOGBOOK | Station pairing remains an external evidence limitation. | P3 | Record the paper availability statement and preserve its unresolved gate. |

## Synthesis

Seven roles. P1: 0. P2: 4 (three resolved, publication open). P3: 17. APPROVED-WITH-CONDITIONS. CURRENT and CHART agree that the nominal-label resolution must not become endpoint geometry. SOUNDER and KEEL require independently checked identity evidence and unchanged prior measurement contents.

## Amendments

1. Preserve original cells and attach narrowly scoped nominal-section evidence.
2. Show the correction and primary source beside affected records.
3. Verify all previous values, both new values, exact query/source maps, and protected publication separately.
