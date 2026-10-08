---
skill: roles-check
topic: somali-premonsoon-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Somali seasonal regional width review

Internal seven-role review against ebe60e3 / CI correction 6002805.
No planetary comparison; ORBIT excluded. Not independent scientific admission.

| Role | Finding | Severity | Disposition |
|---|---|---|---|
| CURRENT | Northern coastal flow differs from southern EACC extension. | P2 | Scope explicit; 3–4 N turn-off not made a width edge. |
| CURRENT | Underlying southward current has a different layer/direction. | P2 | Excluded from shallow northward width record. |
| CURRENT | Seasonal prose is not a seasonal mean or occupied section. | P2 | New phase/metric, null exact dates, layer bounds and geometry. |
| SOUNDER | Original needs a verifiable access/rights record. | P2 | Hash/size/acquisition retained; copyrighted original ignored. |
| SOUNDER | March–May heading gives months but not individual measurements. | P2 | Calendar stored separately; no three repeated width observations. |
| SOUNDER | Source span supplies no probabilistic error or annual extrema. | P2 | Scalar null and inference flags false. |
| CHART | Range segment might imply seasonal minimum and maximum. | P2 | One seasonal synthesis caption, no midpoint or annual range. |
| CHART | Seasonal width could attach to unrelated route frames. | P2 | No geometry/width link; existing editorial playback separate. |
| CHART | Dated northern coastal sections would support a locator. | P3 | Recover before mapped edges or state intersections. |
| BEACON | Unknown months could be interpreted as absent flow. | P2 | Nine unknown cells explicitly do not imply zero width or absence. |
| BEACON | Calendar cells could look like three numerical readings. | P2 | Cells say seasonal span, with explicit one-statement caption. |
| BEACON | New phase needs a clear inspector title. | P2 | Seasonal regional width scale and source period visible. |
| HARBOR | Color alone cannot identify supported months. | P2 | Text labels distinguish seasonal statement from unknown. |
| HARBOR | Twelve cells and range labels must reflow at 320 px. | P2 | Three-column grid, readable SVG, narrow-viewport checks. |
| HARBOR | Preserve source/evidence navigation access. | P3 | Semantic atlas/record/source links retained. |
| KEEL | Unlinked evidence must not break independent route playback. | P2 | Explicit false width eligibility, separate route steps and regression checks. |
| KEEL | Coherent source receipts could alter months or midpoint. | P2 | Complete compiled audit binding and negative native checks. |
| KEEL | Native test ran before the CI build. | P2 | Moved to registered post-build browser gate; pre-build tests verified without CLI. |
| LOGBOOK | Local/source progress is not new mainline publication. | P2 | PR46 terminal failures/correction and pending gate recorded. |
| LOGBOOK | Coverage counts do not establish annual dimensions. | P2 | 44 scoped owners / 49 unassessed; remaining annual/length/footprint gaps explicit. |
| LOGBOOK | Underlying direct observations and scientific admission remain. | P3 | Next actions retained in audit/inventory/plan. |

## Synthesis and amendments

21 findings: zero P1, 18 P2 addressed, three P3 next-work notes.
APPROVED-WITH-CONDITIONS: independent scientific admission and protected-main
publication remain separate gates.

1. Preserve one source-defined seasonal span without monthly, annual or
   geographic inference; distinguish northern flow from southern components.
2. Keep width eligibility separate from editorial route playback and bind
   source/calendar semantics across Python, Rust and WASM.
3. Show evidence gaps visibly, verify narrow-screen calendar/navigation, and
   preserve native checks after the workflow's compilation step.

## Final verification

833 Python tests / 913 subtests and 40 Rust tests passed. Registered regional
width, source index, named eddy and NGCC browser gates passed. The NGCC gate
caught an initial default-selection regression; selecting the first playable
route fixed it, while explicit width deep links preserve evidence selection.
All 43 JavaScript modules pass syntax checks; old width rows and seasonal
frames remain unchanged. Remote PR46 publication remains pending.
