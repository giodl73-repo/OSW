---
skill: roles-check
topic: nwasc-mean-core-widths
date: 2026-10-21
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal review: Norwegian slope branch mean-core extents

Artifact: original-source readback, proposed measurement records, typed
native/WASM validation and query/card scalar presentation. Seven installed
roles apply; ORBIT is outside this physical-data scope. This is an internal
editorial review, not independent scientific approval or current-name admission.

| Role | Finding | Severity | Resolution / evidence |
| --- | --- | --- | --- |
| CURRENT | Static mean-field extent is not mean instantaneous width. | P2 | Separate metric flags, mean-field period, protocol4; no seasonal samples. |
| CURRENT | Svinøy50m plane and Gimsøy projection have different support. | P2 | Separate metrics, plane field50/null, maximum depths460/530 retained as shape context. |
| CURRENT | Transport-core fraction is not a50% speed threshold. | P2 | Explicit50%-mean-transport operator and35.16g/kg AW domain; no velocity-threshold substitution. |
| SOUNDER | Original edition and rights need exact custody. | P2 | Original publisher PDF/XML hashes, actual UTC acquisitions, citation, CC BY4.0 and tracked-PDF exception. |
| SOUNDER | Isobaths cannot become measurement depths or errors. | P2 | Separate scope_isobath_m, false layer flag, fixed-layer/error/paired-edge nulls. |
| SOUNDER | Study property interpolation does not date numerical widths. | P2 | Year-range mean support, no monthly values; curated-section acquisition/reproduction explicitly false. |
| CHART | Scalar extents do not locate edges on the world map. | P2 | Independent text/scalar SVG, no geographic scene, edge coordinates or physical atlas join. |
| CHART | The same50km number cannot imply matching depth geometry. | P2 | Both supports printed in figure and details; no averaged width or merged rectangle. |
| CHART | Figure readability and mobile reflow need inspection. | P2 | Desktop/phone browser renders visually inspected; text equivalents remain readable at320px. |
| BEACON | Proposed branch must stay distinct from broad Norwegian name. | P2 | Proposed IDs only, no canonical current_id; explicit card and query owner language. |
| BEACON | The box-model50km is a different assumption. | P2 | Separate explanatory note and protocol6; no new750km whole-current length. |
| BEACON | Source and exact record should be one action away. | P2 | Card→typed query, per-row source pointers and retained original links; keyboard navigation passed. |
| HARBOR | Diagram needs a semantic data equivalent. | P2 | Two details/summary records with layer, operator, salinity and temporal text; no color-only meaning. |
| HARBOR | New navigation must work without pointer use. | P2 | Keyboard details, typed-record and exact-source navigation passed in the actual browser. |
| HARBOR |320px layout must preserve the scientific qualifications. | P2 | Actual320px render and overflow checks passed; semantic details preserve support and source meaning. |
| KEEL | Partial edition, source rebinding and owner transfer must reject. | P2 | 109 Rust tests/native/WASM builds passed; three new and eight prior actual native/WASM mutations rejected. |
| KEEL | Previous admitted/proposed science must remain exact. | P2 | All prior59,826 typed rows exact, all23 reports/producers exact; prior snapshot and108 atlas sources remain readable/exact. |
| KEEL | Full clean offline/browser gate remains unproven. | P2 | Open release gate: IRD403 before tests at c01c980; disk below local4GiB guard. Scientific-reproduction and NetCDF jobs passed. No overall green claim. |
| LOGBOOK | Publication stays on the continuing draft. | P2 | Existing branch/PR83; no separate PR or main merge authorized here. |
| LOGBOOK | New proposed evidence must not inflate accepted-width coverage. | P2 |158 admitted widths/83 owners unchanged; proposed_widths5→7 only. Eighteen uncovered entries include families/systems. |
| LOGBOOK | Repository source assets and reproducibility must be reviewable. | P2 | Versioned protocol, producer, report, figure, receipt and tests. All372 staged engine hashes match, including the licensed original. |

Roles reviewed:7. P1 blockers:0. Findings:21 P2,20 resolved and one full-suite release gate open. The remaining whole-project
gate does not supply a scientific measurement or permission to reinterpret
missing evidence. The focused delivery gates passed; terminal tests, source preservation and
visual review are recorded in the batch plan. The complete project remains
incomplete and the continuing PR remains a draft.

Three applied amendments: keep the two vertical supports distinct; preserve
mean geometry versus width-series meaning in every view; require native/WASM
and source-pointer/keyboard/phone checks before publishing this increment.
