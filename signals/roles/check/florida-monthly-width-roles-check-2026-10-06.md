---
skill: roles-check
topic: florida-monthly-width
date: 2026-10-06
source_commit: e65b2c1c51024a1ca779ec545d4c039bcc31b2b9
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Florida monthly width curve and chart playback

Artifact: original-source acquisition receipt, Figure 9b extraction protocol,
builder, query diagnostic/sample projection, Rust charts and browser controls.
Seven functional lenses apply; ORBIT excluded because no planetary analogy is
present. This is an internal review, not independent scientific peer review.

| # | Role | Finding | Severity/status | Evidence and action |
|---|---|---|---|---|
| 1 | CURRENT | Local surface jet support stays explicit. | P3 verified | 25.42 N, nominal 0.75 m sensing depth, half-core-speed criterion and 40 h metric filter retained. |
| 2 | CURRENT | Curve is a historical monthly average. | P3 verified | Gray overall curve kept distinct from red 2006 and blue 2005; weighting remains unresolved. |
| 3 | CURRENT | Graph readings cannot supply geographic edges. | P3 verified | No endpoints, footprint, fixed layer, whole-current dimension or annual extrema admitted. |
| 4 | SOUNDER | Original source must be identifiable. | P3 verified | NOAA PDF SHA256 matches repository checksum; original remains ignored. |
| 5 | SOUNDER | Figure shading and reading allowance must be distinct. | P2 resolved | Source shading is within-month standard deviation; +/-1 km allowance is extraction support only. Shading values not extracted. |
| 6 | SOUNDER | Calibration and selection must be reproducible. | P3 verified | Embedded image, RGB checksum, grid-line/tick coordinates, selection band/count and median preserved. |
| 7 | CHART | Axis interference at endpoint months matters. | P3 verified | January/December strips move eight pixels inward, with both locations recorded and allowance retained. |
| 8 | CHART | Selected month must match the inspected sample. | P2 resolved | Card inspection synchronizes dropdown/highlight; shared April reload selects April. |
| 9 | CHART | Narrow displays retain all source months. | P3 verified | Scrollable chart and manual selection; 320 px page reflow checked. |
| 10 | BEACON | Label the source period and geographic scope. | P3 verified | Historical 2005-2006 surface-jet widths at 25.42 N in title and scope note. |
| 11 | BEACON | Give readers a direct path from current to monthly chart. | P2 resolved | Atlas width card links directly to Florida samples, sorted by month. |
| 12 | BEACON | Approximate readings do not resolve all variation. | P3 open | Recover year-specific curves and within-month envelope next; no confidence or physical range claim. |
| 13 | HARBOR | Motion must be optional. | P3 verified | Playback respects reduced motion, stops when hidden or rerendered; manual controls remain. |
| 14 | HARBOR | Selected reading must be textual. | P3 verified | Live text gives month, value and reading allowance; semantic select/buttons and SVG marks retained. |
| 15 | HARBOR | Full manual assistive-technology review is outstanding. | P3 open | Automated keyboard/mobile/reduced-motion checks are not a screen-reader audit. |
| 16 | KEEL | Source refresh must not be an offline hidden network call. | P3 verified | Explicit fixture acquisition with checksum and per-paper size cap; generator reads local original. |
| 17 | KEEL | Reprojection must retain the exact source record. | P3 verified | Native/WASM equality and loader rejection of changed value, latitude or annual range. |
| 18 | KEEL | Corpus-wide charts must remain complete. | P3 verified | 127 samples, ten panels, five missing readings; chart test updated from its stale pre-Loop baseline. |
| 19 | LOGBOOK | Coverage should avoid duplicate statistics-as-months. | P3 verified | One statistical width record plus twelve separate source samples; no new named current or canonical admission. |
| 20 | LOGBOOK | Publication state remains local. | P3 open | Follow-up uncommitted on codex/florida-width-series-summary; PR21 remains the prior merged milestone. |
| 21 | LOGBOOK | Original image redistribution is not implied by acquisition. | P3 verified | PDF and scratch figure pixels ignored; repository contains derived readings, protocol and review chart only. |

## Synthesis

Seven roles, 21 findings: zero open P1/P2; three P2 findings resolved; 18 P3
notes. APPROVED-WITH-CONDITIONS for local editorial graph readings and chart
playback. CURRENT, SOUNDER and CHART agree that monthly scalar readings are
insufficient for physical boundary animation or annual extrema.

Three amendments implemented: separate graph allowance from source variability;
synchronize highlight with inspected/shared sample; add direct current-card
chart navigation. Geographic boundary recovery, year-specific curve/variability
extraction, manual accessibility review and scientific admission remain open.

Verification: 52 focused Python tests and 413 subtests; 23 Rust tests;
three malformed loader rejections; native/WASM equality; playback/pause,
manual reduced-motion controls, card links, shared record reload and 320 px
reflow. Original figure and generated chart inspected. Florida statistics and
existing Leeuwin atlas browser checks pass. Canonical release unchanged.
