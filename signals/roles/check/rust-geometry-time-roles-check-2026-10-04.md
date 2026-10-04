---
skill: roles-check
topic: rust-geometry-time
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 4
p2_remaining: 0
p3_count: 17
verdict: APPROVED-WITH-CONDITIONS
---

# Recorded geometry time review

Artifacts: Rust observation-window query, spatial composition, filtered scenes,
calendar controls, date catalogue, shared links and SVG metadata. Installed roles
were inspected during this work. CURRENT covers scientific time, SOUNDER custody,
CHART geography, BEACON wording, HARBOR access, KEEL query correctness and LOGBOOK
status. ORBIT is inapplicable. This is an internal lens review, not independent
scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | An observation could be assumed to persist until the next frame. | P2 | Time | Select exact recorded inclusive days; no carry-forward, interpolation or seasonal inference. Addressed. |
| 2 | Undated routes could be mistaken for dated occupancy. | P3 | Context | Exclude by default; explicit inclusion is dimmed, labeled undated context. |
| 3 | Observation date differs from acquisition or transaction time. | P3 | Contract | Filter only map feature observation_date and retain source notes. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Exported maps could lose temporal scope. | P2 | SVG | Embed window in receipt and show dates in visible caption. Actual download check passes. Addressed. |
| 2 | Complete source records need to remain inspectable. | P3 | Rows | Retain original map_features in result rows; loaded-row preservation passes. |
| 3 | Invalid/non-day source time cannot be silently reclassified. | P3 | Dates | Exclude malformed values even when undated context is requested; Rust test covers this. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | An old state crossing could qualify a later dated map. | P2 | Composition | Filter spatial relations by original feature index and time before selecting objects. Source-index oracle checks pass. Addressed. |
| 2 | Filtering might renumber feature indices and corrupt joins. | P3 | Scene | Enumerate original features before filtering; verify each rendered index against source. |
| 3 | Empty days could substitute the nearest available frame. | P3 | Gaps | Return an empty scene; no nearest-day substitution. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Three sparse observation days are not seasonal animation. | P3 | Status | State eight features/three days and keep frame acquisition pending. |
| 2 | Map selection differs from full inspector records. | P3 | Copy | Document selected features versus complete source records. |
| 3 | A date catalogue could suggest continuous coverage. | P3 | Selector | Call it recorded geometry days; explain gaps are not interpolated. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Time selection needs keyboard-compatible labeled controls. | P3 | Forms | Use native date inputs, checkbox and select with labels. |
| 2 | Additional controls can overflow narrow layouts. | P3 | Reflow | Verify at 320 px; screenshot viewed. Align context checkbox with its label. |
| 3 | Dim context requires wording beyond opacity. | P3 | Marks | Include undated context in focus/hover labels and map status. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Lexical comparison alone could accept impossible calendar dates. | P2 | Validation | Validate exact Gregorian day syntax/calendar and ordered bounds before comparison. Leap-day tests pass. Addressed. |
| 2 | Native and browser could use different temporal logic. | P3 | Parity | Rust owns selection and catalogue; actual native/WASM results match. |
| 3 | Python/Rust float parsing differs for some source coordinates. | P3 | Oracle | Qualify by exact source dates/indices; verify row preservation against unfiltered loaded Rust rows. Observed mismatch is one ULP. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Shared URLs must reproduce selected time. | P3 | Navigation | Include geometry_time in query and verify replay. |
| 2 | Source artifacts must not change during display filtering. | P3 | Custody | Keep canonical hash unchanged and source rows complete. |
| 3 | Time query support leaves seasonal frame ingestion unfinished. | P3 | Remaining work | Record that gap explicitly in README and contract. |

## Synthesis

Seven roles, 21 findings: zero P1, four addressed P2 and seventeen P3. Approved
with conditions for exact observation-day queries. Top finding: time and state
must qualify the same stored feature. CURRENT/CHART agree on avoiding inferred
occupancy; SOUNDER/LOGBOOK agree on reproducible scope and unchanged source records.

## Three amendments

1. Validate inclusive calendar windows and exclude unknown times by default.
2. Filter spatial relations and map features by original indices before selection;
   retain full source rows and mark optional undated context.
3. Preserve time in controls, shared URLs and visible/embedded SVG receipts; verify
   native/WASM equality and sparse-source scope.

## Evidence and remaining conditions

Sixteen Rust tests pass. Temporal browser/native checks cover the three real recorded
days, inclusive window with context, original source-date/index qualification,
time/state correspondence, loaded-row preservation, controls, share replay, SVG
caption, invalid dates and 320 px reflow. Full query and SVG export regressions pass.
Mobile screenshot viewed. Canonical ledger SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

More verified source frames, seasonal geometry, independent domain admission,
human accessibility and full public release remain open. Sparse dated marks do
not provide continuous occupancy or whole-current seasonal dimensions.
