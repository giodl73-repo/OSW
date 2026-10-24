---
skill: roles-check
topic: antilles-shipboard-component-spans
date: 2026-10-14
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Antilles shipboard diagnostics internal review

Reviewed against base 3a4af0fe94af443be5a42b6e383faf937e02c2f1.
This internal review does not confer scientific admission. ORBIT is not
applicable to these Earth observations.

| Role | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| CURRENT | A zonal survey span is not a flow-normal current width. | P2 | Association and flow-normal eligibility remain false; full width null. |
| CURRENT | The nearshore peak gate excludes an offshore lobe. | P2 | Predeclared gate is explicitly editorial; first connected crossings only. |
| CURRENT | Two occupations do not establish annual variation. | P2 | Annual range and seasonal playback eligibility remain null/false. |
| SOUNDER | Original velocities are cm/s. | P2 | Exact original check verifies every value converted by 0.01. |
| SOUNDER | 10 m exported spacing is not 16 m native resolution. | P2 | Both retained; 395 m never renamed 400 m or 400 dbar. |
| SOUNDER | Timezone and tidal correction are not documented. | P2 | No UTC suffix or borrowed LADCP tide-correction assertion. |
| CHART | Missing bins must break the plotted profile. | P2 | SVG starts a new subpath after each missing bin. |
| CHART | Dashed crossings could imply physical current edges. | P2 | SVG accessible description identifies diagnostic crossings. |
| CHART | The profile must fit narrow screens. | P3 | Real browser check at 320 px passed. |
| BEACON | Approximate spans could be repeated as admitted widths. | P2 | Chart title and adjacent scope identify local component survey spans. |
| BEACON | Scenario sensitivity is not measurement error. | P2 | Envelope text says operator sensitivity, not error or annual extrema. |
| BEACON | Partial envelopes would hide open boundaries. | P2 | Repeat 95 m envelope null despite two resolved scenarios. |
| HARBOR | Meaning cannot depend on teal/amber colors. | P2 | Numeric title, threshold text, units, scope and raw records supplied. |
| HARBOR | Source navigation needs a direct control. | P3 | Inspect buttons and source links pass real browser navigation. |
| HARBOR | Missing-depth results need explicit language. | P2 | No valid samples and unresolved, not zero, displayed and checked. |
| KEEL | Extraction needs an independent original comparison. | P2 | All 1,327 retained observations verified against pinned MAT. |
| KEEL | Rebinding or promotion must fail at load time. | P2 | Five native mutation cases reject current, depth, width, annual range and association changes. |
| KEEL | Full offline suite and shipped collection checks are required. | P2 | 1,379 tests / 1,034 subtests passed in 1,308.96 s; all 43 collections passed native/WASM UI coverage. |
| LOGBOOK | One PR per gap would fragment the work. | P3 | Same existing branch and draft PR83. |
| LOGBOOK | Original binary should remain outside tracked files. | P2 | Exact ignored path; numerical subset and acquisition receipt tracked. |
| LOGBOOK | Scientific gaps must remain visible. | P2 | Whole-current inventory counts and physical map bands unchanged. |

Three amendments applied: add original-file verification; require complete
three-scenario envelopes; supply direct source navigation and missing-depth
browser coverage. Final local gates passed: original-file verification of
1,327 observations; focused 3 tests / 5 mutation subtests; 46 Rust tests;
native/WASM profile parity, direct source navigation and 320 px display;
all 43 collection checks; complete offline suite above. Staged bytes match
working files, and only the Antilles dashboard entry changed. Remote CI
results must be reported separately; this review does not claim they passed.
