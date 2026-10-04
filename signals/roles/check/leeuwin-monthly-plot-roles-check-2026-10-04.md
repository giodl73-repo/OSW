---
skill: roles-check
topic: leeuwin-monthly-plot
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 5
p2_remaining: 0
p3_count: 16
verdict: APPROVED-WITH-CONDITIONS
---

# Leeuwin monthly graph and atlas card review

Artifacts: pinned graph extraction, local protocol, generator, atlas chart, dashboard join and regression checks. Seven local role lenses; these are internal reviews, not independent scientific admission. CURRENT checks physical scope; SOUNDER provenance; CHART visual meaning; BEACON wording; HARBOR access; KEEL reproducibility; LOGBOOK status. ORBIT is inapplicable. Role definitions were inspected.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Graph readings could imply full-current seasonal dimensions. | P2 | Source scope | Keep single a101 crossing, historical monthly composite and false geometry/ranking flags. Addressed. |
| 2 | The 1.89 coefficient is source-defined approximate half maximum. | P3 | Method | Retain coefficient, angle and per-cycle-then-month averaging. |
| 3 | July and September readings cannot identify a unique minimum. | P3 | Reading overlap | Keep overlap note and prose values separate. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Reading allowance could be mistaken for source uncertainty. | P2 | Chart bars | State ±3 km editorial reading allowance, not confidence or temporal spread. Addressed. |
| 2 | Calibration includes manual choices and December inset. | P3 | Extraction config | Preserve pixel locations, decoded raster hash and sample strip metadata. |
| 3 | July/August 2002 period discrepancy remains unresolved. | P3 | Time scope | Retain both labels; do not invent occupied dates. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Month playback could morph the editorial reference route. | P2 | Atlas integration | Chart helper never writes map geometry; browser asserts unchanged view during playback. Addressed. |
| 2 | Discrete points do not support intermediate-month interpolation. | P3 | Chart | Render twelve points with allowances; explicit steps stop at December. |
| 3 | Primary card must retain source evidence. | P3 | Source links | Keep source PDF page, protocol, JSON and twelve-row table beside chart. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earlier inspector said other months were unextracted. | P2 | Inspector wording | Explain two prose records versus separate twelve graph readings and link the matching month. Addressed. |
| 2 | Source provenance is dense for a compact card. | P3 | Copy | Use short value status plus explicit method and source links. |
| 3 | Local historical series may be read as live currents. | P3 | Title | Keep Historical monthly widths and crossing a101 in title/status. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Color alone cannot convey selected width. | P3 | Equivalent access | Month select, live text status and table repeat selected value and interval. |
| 2 | Playback requires explicit control and cleanup. | P3 | Motion | Start only on Play; pause, stop in December, stop when hidden or card replaced. |
| 3 | Desktop scroller can clip a screenshot of a long card. | P3 | Visual review | Inspect stacked 860 px card screenshot and retain 320 px reflow test; human assistive-technology review pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Changed graph or scope could bypass dashboard evidence custody. | P2 | Dashboard builder | Require equality to regeneration from pinned PDF/config/protocol; mutation tests reject changes. Addressed. |
| 2 | Prose anchors could inflate monthly evidence count to fourteen. | P3 | Capabilities | Count twelve graph months; preserve two prose measurement records as separate scoped evidence. |
| 3 | New month query must survive sharing and be cleared on selection changes. | P3 | Lifecycle | Capture requested month, preserve it on same-card sharing and clear it on new feature/global selection. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earlier prose extraction audit is a historical receipt. | P3 | Audit history | Keep it immutable; full-curve extraction has a separate status and protocol. |
| 2 | Chart extraction does not change canonical admission. | P3 | Release | Keep canonical ledger unchanged and independent scientific admission pending. |
| 3 | Local checks do not prove full publication readiness. | P3 | Verification | Record focused checks; clean-checkout, independent science and human accessibility remain open. |

## Synthesis

Seven roles, 21 findings: zero P1, five addressed P2, sixteen P3. APPROVED-WITH-CONDITIONS for local editorial graph display. Top finding: the chart shows monthly fitted widths at one historical crossing, and its bars show reading allowance. CURRENT, SOUNDER and CHART agree that neither encoding warrants an annual map-width footprint.

## Three amendments

1. Keep immutable prose extraction and new complete curve distinct; pin PDF/raster/config/protocol and validate deterministic regeneration.
2. Show explicit monthly stepping, source coefficient/averaging, reading margin and overlapping minima; leave atlas geometry unchanged.
3. Share the selected month, dispose playback when leaving, replace stale inspector wording, and count twelve months without double-counting prose anchors.

## Evidence and limits

Passed: three source-regeneration/mutation tests, nineteen dashboard tests, inline monthly-width browser checks, prose inspector roundtrip, map-first presentation checks and JavaScript syntax. Browser checks cover discrete December stop, unchanged map view, new-card timer disposal, shared month reload, invalid scope fail-soft and 320 px layout. Visual review uses figures/leeuwin-monthly-plot-review.png at stacked 860 px to avoid desktop aside clipping. Canonical ledger is unchanged. No independent scientific admission, human assistive-technology certification, full clean-checkout gate or public redistribution is claimed.
