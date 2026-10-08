---
skill: roles-check
topic: black-sea-rim-width
date: 2026-10-07
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Black Sea Rim Current width review

Internal review of the primary-source extraction, range chart, source index,
dashboard fingerprints and query integration. Selected roles cover physical
scope, evidence stewardship, cartography, public explanation, accessibility,
reproduction and publication. This is not independent scientific peer review.

| Role | Finding | Severity | Section / recommendation |
|---|---|---|---|
| CURRENT | 40–80 km is descriptive regional support, not yearly extrema. | P2 | Resolved: annual eligibility false; no seasonal assignment or midpoint. |
| CURRENT | Pycnocline depth cannot define the width measurement layer. | P2 | Resolved: fixed layer null; explicit context flag and mutation rejection. |
| CURRENT | No paired velocity boundary is supplied. | P3 | Source audit: retain null geometry and unresolved observation gate. |
| SOUNDER | Original source needs an exact, offline receipt. | P2 | Resolved: pinned unmodified CC BY 3.0 PDF, bytes, checksum and attribution. |
| SOUNDER | Publication year differs from measurement time. | P3 | Inventory: no observed period or calendar months; visible convention. |
| SOUNDER | The audit must affect discovery and update signals. | P3 | Index declares audit and acquisition; query and dashboard bind audit. |
| CHART | Range graphic could imply an uncertainty interval. | P2 | Resolved: explicit chart description and visible range-meaning caption. |
| CHART | Range chart must not draw geographic boundaries. | P3 | Seasons: static scalar range with zero axis; section locator hidden. |
| CHART | Switching currents must clear obsolete range evidence. | P3 | Browser check verifies Labrador hides and Gaspé refreshes the chart. |
| BEACON | Regional range should be named beside its numbers. | P3 | Heading and values label regional width; publication date is qualified. |
| BEACON | Unknown full-current width remains meaningful. | P3 | Inventory decision retains null representative width and admission flags. |
| BEACON | Source and method must be reachable. | P3 | Original PDF link and exact locator available beside evidence and in queries. |
| HARBOR | Meaning cannot rely on the turquoise mark alone. | P3 | SVG accessible name, numeric labels and visible caption repeat meaning. |
| HARBOR | Narrow viewport must preserve endpoints and text. | P3 | Responsive SVG; 320 px browser reflow check. |
| HARBOR | Unsupported playback must remain unavailable. | P3 | Browser asserts disabled playback and missing annual range. |
| KEEL | Invented midpoint, edges, months or layer must fail. | P2 | Resolved: mutation tests enforce the source range and scope. |
| KEEL | Existing records could drift during inventory update. | P3 | Exact comparison verified all 71 prior measurement contents unchanged. |
| KEEL | Native and shipped WASM must return the same record. | P3 | Dedicated browser check compares complete query rows; register in CI runner. |
| LOGBOOK | Local checks do not establish protected-main publication. | P2 | Open condition: exact commit CI and protected landing remain required. |
| LOGBOOK | PDF redistribution needs a narrow documented exception. | P3 | Source README and scoped ignore exception preserve author/license attribution. |
| LOGBOOK | Wider goal remains incomplete. | P3 | Batch receipt retains missing lengths, unassessed widths and eddy footprints. |

## Synthesis

Seven roles. P1: 0. P2: 6 (five resolved; publication remains open). P3: 15.
APPROVED-WITH-CONDITIONS. CURRENT and CHART agree that descriptive width
must not become seasonal or geographic boundaries. SOUNDER and KEEL require
the source and scoped extraction to remain reproducible offline.

## Amendments

1. Preserve range-only values and reject invented temporal, layer or edge support.
2. Add an accessible range chart with an explicit meaning and source path.
3. Preserve prior records and verify regenerated native/WASM data; track protected
   publication separately from local validation.
