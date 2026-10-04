---
skill: roles-check
topic: rust-width-query-charts
date: 2026-10-04
source_commit: 913a8457dde0338f2807606d7a220fff85ae783d
working_branch: codex/seasonal-query-map
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Source width chart review

Internal functional review of Rust chart scenes, browser rendering and executable
checks. Source admission remains pending. ORBIT is excluded because this change
introduces no planetary comparison. Each row is a distinct finding.

| Role | Finding | Status and evidence |
|---|---|---|
| CURRENT | Different width methods require separate panels. | Verified: diagnostic and source-phase grouping produces six panels. |
| CURRENT | Extraction margins do not measure physical uncertainty. | Verified: whiskers explicitly labelled plot-reading allowances; uncertainty remains unresolved. |
| CURRENT | Annual evolution cannot be inferred from disconnected historical samples. | Verified: no interpolation, annual extrema, map footprint or cross-method ranking. |
| SOUNDER | Values must retain exact sample identity. | Verified: all 88 chart marks agree with imported source sample values and intervals. |
| SOUNDER | Missing readings must remain visible. | Verified: five unresolved Kuroshio readings retain original sample IDs and null values. |
| SOUNDER | Source period ambiguity must survive visualization. | Verified: Leeuwin period conflict and Kuroshio calendar uncertainty remain visible. |
| CHART | Filtered axes could exaggerate apparent changes. | Verified: domains use the full original diagnostic; single-point queries retain domains and coordinates. |
| CHART | Missing values must not appear at zero. | Verified: missing crosses occupy a separate strip below the numeric plot. |
| CHART | Seasonal profiles need comparable scales. | Verified: four Kuroshio panels use the full diagnostic's common width domain. |
| BEACON | Chart counts must explain table pagination. | Verified: scope states all matches before pagination; limit-one query still draws 88 marks. |
| BEACON | Selection needs a direct evidence path. | Verified: marks open original sample cards, whose parent/source links remain available. |
| BEACON | Empty queries need an explicit state. | Verified: empty chart message distinguishes missing coverage from zero width. |
| HARBOR | Interactive descendants must be exposed accessibly. | Resolved: outer SVG uses group role; marks are individually labelled keyboard buttons. |
| HARBOR | Missing marks need a keyboard path. | Verified: Enter opens an unresolved sample card; numeric points also respond to Enter/Space. |
| HARBOR | Narrow layouts must preserve readable axes. | Verified: 320 px page reflows, chart scrolls inside its frame, table remains the text alternative. |
| KEEL | Native and browser engines could diverge. | Verified: six representative queries compare full native/WASM results including chart primitives. |
| KEEL | Invalid queries could leave stale charts. | Verified: collection switches and invalid filters hide and clear chart state. |
| KEEL | Axis and missing semantics need executable checks. | Verified: Rust chart unit test plus standalone browser/source comparison pass. |
| LOGBOOK | Chart generation must be reproducible. | Verified: charts.rs is included in the engine SHA manifest; all manifest hashes match. |
| LOGBOOK | Local paper fixtures must not be redistributed. | Verified: ignored source PDFs remain outside the change set. |
| LOGBOOK | Implementation review must not imply scientific admission. | Verified: source status and existing canonical release remain unchanged. |

Evidence: 20 Rust tests; four width projection tests; standalone width-chart,
width-sample and seasonal-map browser checks; JavaScript syntax checks; chart
screenshots inspected. Conditions: source review/admission remains pending and
further scientific coverage remains part of the broader project.
