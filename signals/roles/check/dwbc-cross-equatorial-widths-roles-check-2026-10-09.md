---
skill: roles-check
topic: dwbc-cross-equatorial-widths
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# DWBC float-composite width: internal review

Source commit: parent `81fe79c8ed92fe084fb11a0d128f926700604dea` / draft PR75.
Reviewed working-tree batch on `codex/dwbc-cross-equatorial-widths`.
Seven installed functional lenses apply to scientific extraction, provenance,
native Rust scenes and browser presentation. ORBIT has no planetary comparison
to assess. This review is internal; independent scientific admission remains
pending. Validation and publication outcomes belong to the batch receipt.

| Role | Finding | Severity | Resolution and evidence |
|---|---|---|---|
| CURRENT | Nominal float depth is not a fixed measurement layer. | P2 | Failed depth control/reporting and estimated 230 m sinking remain explicit; fixed bounds null. Neither 1800 m nor the separate 900–2800 m transport integration becomes a width layer. |
| CURRENT | Four overlapping Table 2 rows cannot supply four independent widths or annual margins. | P2 | One composite width owns four auxiliary rows; recurring months, annual extrema, independent edge extraction and playback remain false/null. |
| CURRENT | Velocity and transport standard errors, 10 km bins and 90–130 km sampling gap have distinct roles. | P2 | Whiskers label velocity/transport errors only; width uncertainty null. First-subset warning that width/transport could be larger retained; gap endpoints never become a width interval. |
| SOUNDER | Hosting by WHOI does not license republication of the original. | P2 | Original p1 copyright recorded; ignored original PDF acquired explicitly and pinned. No source figure copied into the atlas. |
| SOUNDER | Source selection labels and counts disagree. | P2 | Table 2's 2 S–12 N west of 43 W and prose 0–7 N / 12 months remain separate. Subsets total 489 observations versus composite 500; no missing observations invented or normalization applied. |
| SOUNDER | Rounded transport and alternate errors could be combined incorrectly. | P2 | Table 2 14 ±3, prose 13.8 and alternative SE about 4 retain separate descriptions. Composite 15 Sv construction and assumed elliptical profile explained; subset Sv remains null. |
| CHART | A study viewport could imply a measured footprint. | P2 | Native OSW equirectangular view uses source Figure 2 bounds only. Caption and role deny inferred trajectories, axis, width edges or physical footprint. |
| CHART | Existing North Atlantic reference reach could be mistaken for tropical measurement support. | P2 | Separate reach noted beside the tropical map; no new route geometry or physical state intersections inferred. |
| CHART | Paginated global width queries could silently omit one comparison. | P2 | Rust emits both coastal and DWBC comparison scenes when both match, even with limit 1; browser verifies both panels and full native/WASM equality. |
| BEACON | A season page could suggest an annual cycle. | P2 | Upper-core float-composite title and unequal historical subset explanation; disabled playback and no invented month selection. |
| BEACON | Published speed summaries might look like an ingested velocity series. | P2 | Explicit source-estimate description and separate table; observed-velocity and time-sample capabilities remain zero. |
| BEACON | Caveats without source navigation are hard to verify. | P2 | Width inspector, source-row pointers and published-paper link sit beside the charts; source index includes audit and acquisition receipt. |
| HARBOR | Thin map labels need readable contrast and size. | P2 | White text with dark halo, native map frame and effective-font checks at 320 px. Geography also described in text. |
| HARBOR | Fixed-size charts can hide points in the initial mobile viewport. | P2 | Local keyboard-focusable scrolling, visible scroll instructions and approximate 100 km in the heading. No page-wide overflow; table supplies all numerical alternatives. |
| HARBOR | Source navigation must work without pointer or palette. | P2 | Keyboard atlas-to-record test, 44 px source-link targets, semantic table headers and explicit numeric values. |
| KEEL | Recomputed receipts could conceal changed scientific support. | P2 | Frozen original/audit/protocol and exact source record; ten coherent native-first fixtures reused byte-for-byte in WASM, requiring the intended scientific errors. |
| KEEL | Removing the width with dependent joins could silently erase coverage. | P2 | Protected-ID group guard requires exactly one admitted row when audit pin exists; deletion fixture removes dependent joins and refreshes receipts before rejection. |
| KEEL | Shared scene changes need existing-page regression checks. | P2 | Focused browser plus prior coastal, query, all-collection, navigation, season and atlas regressions; final outcomes recorded in the batch receipt. |
| LOGBOOK | New source summaries must not light unrelated dashboard capabilities. | P2 | One scoped-width record and unchanged reference-route count; geometry, observed velocity and time samples remain zero. Browser verifies indicator behavior. |
| LOGBOOK | A growing inventory needs stable measurement rules and old-row preservation. | P2 | Versioned nine-rule protocol, pinned source audit and batch receipt; all 124 prior width records remain content-equal. |
| LOGBOOK | Local validation and a stacked draft do not establish mainline coverage. | P2 | Parent PR75 remote failures recorded separately; current draft, remote checks and independent scientific admission remain distinct publication conditions. |

Roles reviewed: 7. Findings: 21 P2, addressed in the batch; 0 P1 blockers.
Verdict: **APPROVED-WITH-CONDITIONS**. Conditions: complete local regression
gates, record remote outcome truthfully, and preserve pending independent
scientific admission and mainline publication. This review does not claim CI
success or a release.

Three amendments implemented: preserve nominal drifting depth and all source
sampling discrepancies; render separately labeled width and auxiliary-error
charts with geographic context from one Rust scene; protect complete source
identity against coherent native/WASM edits and expose mobile scroll controls.

Top finding and CURRENT/SOUNDER consensus: overlapping historical subsets and
their speed/transport errors cannot establish annual width margins.
CHART/HARBOR consensus: study geography needs its evidence class and a readable
textual alternative beside the map.
