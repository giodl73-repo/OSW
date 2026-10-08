---
skill: roles-check
topic: norwegian-atlantic-branch-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Norwegian Atlantic branch width review

Internal review of data, Rust/Python guards, source index and branch cards,
against working base 78a831d8c17a008a164e4ca39052f341068b0869. This is not
independent peer review or canonical identity admission. Seven roles cover
physical scope, provenance, visual encoding, explanation, access, offline
reproduction and publication. ORBIT is excluded: no planetary analogy occurs.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Canonical Norwegian naming overlaps the coastal system. | P2 | Ownership | Addressed: retain proposed Atlantic branch IDs, no canonical transfer. |
| 2 | Jet depth, bathymetry and instrument depth do not define the width layer. | P2 | Sampling context | Addressed: null fixed layer, explicit exclusions and mutation guards. |
| 3 | Different methods do not establish an annual width cycle. | P2 | Temporal eligibility | Addressed: playback/extrema false, actual width observation dates null. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | 2001 evidence is an indexed abstract; original methods remain unread. | P2 | Source access | Addressed: retain this distinction in records and card details. Acquire original before stronger claims. |
| 2 | A 30–50 km prose span supplies no preferred scalar or confidence level. | P2 | Numeric semantics | Addressed: null scalar, scoped range, no confidence interval or midpoint. |
| 3 | The 2010 original must be reproducible and lawfully retained. | P2 | Acquisition | Addressed: fixed PDF hash/bytes, CC BY 3.0 attribution and unmodified-source receipt. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Connecting publication years would imply a width trend. | P2 | SVG | Addressed: independent range/point rows and an explicit method-comparison caption. |
| 2 | Width evidence does not supply mapped paired edges. | P2 | Geometry | Addressed: no invented buffer, route footprint or containment. |
| 3 | A study-section locator would improve geographic context. | P3 | Navigation | Add only with separately scoped source coordinates; do not reinterpret as measured branch edges. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | ADT needs a definition beside the chart. | P2 | Card prose | Addressed: absolute dynamic topography and surface geostrophic interpretation supplied. |
| 2 | The 2010 broader frontal mean discussion has no new numeric width. | P2 | Front card | Addressed: explicit unknown mean; no invented value or interval. |
| 3 | System width cannot be found by adding branch spans. | P2 | Parent card | Addressed: system unknown and branch links instead of an aggregate chart. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Default figure margins made labels too small at 320 px. | P2 | Mobile SVG | Addressed: remove side margins, enlarge labels; final regional browser passes at 320 px. |
| 2 | Color alone must not distinguish point and range semantics. | P2 | SVG/text | Addressed: different marks, labelled endpoints and complete textual details. |
| 3 | Every visual claim needs a keyboard-accessible source path. | P3 | Navigation | Preserve semantic links/details, SVG description and direct query link. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Proposal edits stale dependent endpoint receipts. | P2 | Input hashes | Addressed: refresh endpoint and dependent monthly-extraction receipts without changing values; final suite passes 827 tests and 829 subtests. |
| 2 | Consistently rewritten hashes alone cannot enforce scientific scope. | P2 | Rust loader | Addressed: semantic guards and three coherent atlas rewrite rejection checks. |
| 3 | New Rust code must be covered by the engine manifest. | P2 | Build | Addressed: proposed_widths.rs included; native/WASM build passes 39 Rust tests. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Proposed evidence must not inflate canonical coverage totals. | P2 | Batch status | Addressed: canonical totals unchanged; three proposed records and two proposed owners stated separately. |
| 2 | Local passes do not establish a successful mainline merge. | P2 | Publication | Addressed: PR30 pending status distinguished from local evidence; verify final remote status. |
| 3 | Source rights and failed attempts belong in the operational record. | P3 | Plan/acquisition | Preserve CC attribution, initial stale-receipt failure and mobile failure with final outcomes. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. P2 findings: 18, corrected in the working
artifact; corrected full suite and regional browser pass. P3 notes: 3. Verdict:
APPROVED-WITH-CONDITIONS. Final atlas snapshot browser passes with 78 exact sources and eighteen
loader rejections. Protected-main checks remain pending. Canonical admission and seasonal geometry remain
outside the evidence supplied by this batch.

Top finding: unresolved Norwegian naming must not transfer offshore branch
measurements into a coastal or ambiguous canonical owner. CURRENT, SOUNDER
and LOGBOOK agree on separate proposed ownership and coverage accounting.

## Three amendments

1. Bind all records to proposed branch identities and null system dimensions.
2. Keep method, time and depth exclusions beside the chart; avoid trend lines.
3. Refresh dependent receipts and verify mobile reflow plus native/WASM parity
   before recording a passing publication gate.
