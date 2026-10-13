---
skill: roles-check
topic: antarctic-coastal-composite-widths
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Antarctic coastal composite widths: internal review

Source commit: parent `3a20b86`; reviewed working-tree batch on
`codex/antarctic-coastal-composite-widths`. Seven installed functional lenses
apply to scientific extraction, source preservation, Rust scenes and browser
presentation. ORBIT has no planetary comparison to assess. This is internal
editorial review; independent scientific admission remains pending.

| Role | Finding | Severity | Resolution and evidence |
|---|---|---|---|
| CURRENT | The seven widths have spatial rather than temporal support. | P2 | Separate section IDs, east-to-west order, no annual range or playback; common native scene. |
| CURRENT | Reference depth and integration base have different roles. | P2 | Preserve 400 m geostrophic reference and surface-to-variable-34.4-psu integration; fixed layer remains null. |
| CURRENT | Section length, depth range and transport error are different quantities. | P2 | Auxiliary properties retain their units and source locators; none supplies current length or width uncertainty. |
| SOUNDER | Final published article must replace discussion-version evidence. | P2 | Final 21-page original pinned by bytes and SHA; original selected pages visually inspected. |
| SOUNDER | Source sampling prose contradicts section 6 counts. | P2 | Preserve 117 winter and 150 summer profiles; discrepancy explicit in audit, comparison and source inspector. |
| SOUNDER | Figure extraction needs reproducible identity and attribution. | P2 | CC BY 4.0 original and image receipt retained; pinned optional PyMuPDF reconstruction reproduces exact reviewed PNG. |
| CHART | Profile locations could be mistaken for current boundaries. | P2 | Figure role beside map and in alternative text; no edges, route, polygon or buffer inferred. |
| CHART | Widths need a common zero axis and distinct source context. | P2 | Rust supplies fixed 0–175 km axis, all seven sections and matching flags even for a one-record query. |
| CHART | Source map should preserve the publisher's geographic treatment. | P2 | Embedded raster extracted without reprojection, recoloring or added markings; no inferred projection or digitized geography. |
| BEACON | A season page can make composites sound seasonal. | P2 | Section-specific title, spatial scope explanation and disabled playback; no interpolated monthly sequence. |
| BEACON | Readers need a short route from picture to original values. | P2 | Section links, query inspection, audit source pointer and DOI beside the comparison. |
| BEACON | Depth, salinity and velocity notation need context. | P2 | Method distinguishes reference depth and salinity-defined integral; units in table; diagnostic-velocity caution preserved. |
| HARBOR | Selection cannot depend on palette alone. | P2 | Selected/query/context text in table, selected-row semantics and outlined active bars. |
| HARBOR | Seven-section graphics must remain readable on mobile. | P2 | Local keyboard-focusable horizontal scrolling, fixed readable chart size, 320 px reflow and effective-font checks. |
| HARBOR | Color-coded profile map needs an equivalent textual path. | P2 | Numbered sections, table, caption and descriptive image alternative; keyboard links reach section records. |
| KEEL | Coherent receipt and collection edits can still change scientific support. | P2 | Nine native-first fixtures reused byte-for-byte in WASM; intended source or complete-inventory errors required. |
| KEEL | A deleted source section must not silently become a six-section comparison. | P2 | Exact seven-ID native group guard; test removes dependent joins and refreshes receipts before expecting the scientific error. |
| KEEL | Altered image bytes must not display under the reviewed citation. | P2 | Browser SHA and byte-count verification; corrupt-image test shows a visible error and no image. |
| LOGBOOK | New width evidence must not light unrelated capabilities. | P2 | Seven scoped widths; geometry, time samples and observed velocity remain zero; dashboard browser verifies all four metrics. |
| LOGBOOK | A data batch needs durable rules and preservation of existing rows. | P2 | Frozen protocol/audit, source receipts and batch receipt; all 117 previous width records content-equal. |
| LOGBOOK | Draft publication and local tests must not imply mainline or terminal CI. | P2 | Stacked draft above PR74; parent download failures recorded separately; external admission and mainline remain conditions. |

Roles reviewed: 7. Findings: 21 P2, addressed locally; 0 P1 blockers.
Verdict: **APPROVED-WITH-CONDITIONS**. Full local validation outcomes are
recorded in the batch receipt; this review does not claim remote CI success.

Three amendments implemented: preserve a separate composite threshold metric
with signed auxiliary properties; show the credited profile map through a
shared native scene and verify its bytes; freeze complete section identity and
test coherent source changes in native Rust before using identical WASM inputs.

Top finding and CURRENT/SOUNDER consensus: section differences and sampling
composition cannot establish annual width margins. CHART/HARBOR consensus:
the source map needs its evidentiary class and an accessible numbered table.
