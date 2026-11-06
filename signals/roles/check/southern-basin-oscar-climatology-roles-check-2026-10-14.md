---
skill: roles-check
topic: southern-basin-oscar-climatology
date: 2026-10-14
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED
---

# Three southern-basin climatologies: internal review

Base commit: f7dbdebd867ca933cfaa06a974bfe22ebb7b60b6. Data/code/atlas review.
Seven installed lenses apply: physics, stewardship, mapping, explanation,
accessibility, reproduction and publication. ORBIT has no planetary comparison
to review. This is internal editorial review, not independent scientific admission.

| Role | Finding | Severity | Evidence and action |
| --- | --- | --- | --- |
| CURRENT | Surface peaks cannot inherit historical transport or float-route identity. | P2 resolved | Separate contextual audits retained; association false and named-current width unresolved in all three documents. |
| CURRENT | Width of a climatological mean is not mean yearly width. | P2 resolved | Both operators retained: 792 yearly monthly profiles, 36 climatological profiles, with separate conditional ranges. |
| CURRENT | Strongest peaks, search-edge peaks and broad connected flow can include other jets or eddies. | P2 resolved | Existing geography frozen before acquisition; all profiles and crossing brackets retained; no flow-normal/whole-current width, footprint, rank or physical annual extrema admitted. |
| SOUNDER | Multi-year weighting can silently change the operator. | P2 resolved | Five paired vectors per year-month cell, at least 18 paired valid years, equal year weights, explicit valid-year lists; independent tests distinguish pooled weighting. |
| SOUNDER | A nearest-time query can return a 2017 boundary sample. | P2 resolved | Original bytes retained, 2017-01-01 explicitly excluded at all three sections; no unexpected time gaps or missing vector pairs. |
| SOUNDER | A refreshed provider can differ from the old archive. | P2 resolved | Every 2013 vector and monthly vector profile matches the independently acquired existing archive; original metadata, CSVs, URLs, license and hashes retained. |
| CHART | A section line can be mistaken for a current footprint. | P2 resolved | Existing local-section map grammar, false association flag and explicit climatology period; no buffered corridors or physical area joins. |
| CHART | Missing climatological spans cannot become zero. | P2 resolved | Three of 36 remain null; figures show unresolved panels and queries expose missing marks. All yearly nominal sections happen to resolve; no rule forces this result. |
| CHART | Different basins and source layers must remain separate. | P2 resolved | Three panels, distinct diagnostic IDs and source pointers; original 2013 panels remain alongside the new climatologies. |
| BEACON | A source-frequency label would be false for these geographic windows. | P2 resolved | New explicit context-window label; generic UI preserves the Indian SECC frequency-window label for its own source. |
| BEACON | Interannual spread could be presented as an error bar or annual extrema. | P2 resolved | Inspector labels resolved-year count and conditional finite span; uncertainty and annual physical dimension fields remain null. |
| BEACON | More source rows do not mean more measured currents. | P2 resolved | 143 source-width definitions and 75 width owners unchanged; 36 additional local samples and three diagnostics counted separately. |
| HARBOR | Charts need numerical alternatives and non-color missing marks. | P2 resolved | SVG descriptions, numbered year/month heatmap cells, source query tables and unresolved text accompany color. |
| HARBOR | Seasonal controls must work without motion and at narrow widths. | P2 resolved | Dedicated browser checks 12 manual month choices, reduced-motion playback, real inspectors and 320 px reflow at all three owners. |
| HARBOR | Current cards need direct routes into the evidence. | P2 resolved | Actual atlas-card links tested separately for each climatology, with 44 px source links and exact per-section source-year pointers. |
| KEEL | Derived data must reconstruct from pinned original vectors. | P2 resolved | Six new tests passed, including full reconstruction, independent CSV means, shared masks and unchanged 2013 operator. |
| KEEL | Rehashing edited metadata must not admit new scientific claims. | P2 resolved | Frozen Python/Rust document pins; nine coherent native/WASM rejection cases cover invented zero, pooling, longitude, annual ranges, uncertainty, deletion, root pin, year and association. |
| KEEL | Complete default suite and final built assets need verification. | P2 resolved | Final engine has 47 passing Rust tests and exact dependency hashes; complete Python gate and scoped UI regressions required below. |
| LOGBOOK | Older data and owner fingerprints must be preserved. | P2 resolved | Only the three target dashboard owners change; prior 143 width definitions and seasonal frames compare equal. |
| LOGBOOK | Keep a single accumulation PR and accurate remote status. | P2 resolved | Same branch/draft PR83; no merge. Earlier-head CI results are separate from this batch's local gates. |
| LOGBOOK | Redistribution and public provenance require explicit scope. | P2 resolved | Provider-licensed original vector CSVs/metadata retained; no additional paper PDFs, copied figures or restricted fields packaged. |

## Amendments

1. Use a geographic search-window label, preserving the different Indian SECC
   frequency context and avoiding an unsupported source claim.
2. Keep original and climatological diagnostics under distinct IDs. Scope older
   one-year browser assertions to the original diagnostic instead of treating every
   future owner query as a single series.
3. Bind the root data and all derived documents in both Python and Rust. Preserve
   nulls, exact source navigation and scientific admission limits across the UI.

## Validation

Complete local gate: 1,424 tests / 1,061 subtests passed in 2,003.17 seconds (33m23s). All 47 Rust tests pass.
All 44 collection UI checks and all 100 current cards / 143 widths pass.
New native/WASM source and nine rejection cases, older 271-sample query checks
and all 84 original monthly basin samples pass. Staged source bytes and engine
dependencies match. Remote CI is reported separately. Four independent figures
were visually reviewed: three monthly profile sheets and a 22-year numerical
heatmap. Profile curves, signed values, context shading, paired crossings, missing
cases, legends and captions are visible. Physical current identification and
flow-normal width admission remain open.


## Synthesis

Roles reviewed: 7. Open P1 blockers: 0. Open P2 issues: 0.
Verdict: APPROVED for editorial derived-data delivery.
Top finding: climatological span is not mean yearly span. CURRENT and BEACON
agree that longer temporal support cannot establish named-current identity or
physical annual width extrema. These scientific admission limits remain explicit.
