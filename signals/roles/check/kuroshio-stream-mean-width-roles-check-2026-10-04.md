---
skill: roles-check
topic: kuroshio-stream-mean-width
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 5
p2_remaining: 0
p3_count: 16
verdict: APPROVED-WITH-CONDITIONS
---

# Kuroshio regional stream-mean width review

Artifacts: published-layout PDF custody; source scope audit; protocol v1.19; three width records; validators; inspector/atlas/dash join. CURRENT checks physical scope, SOUNDER custody, CHART encoding, BEACON prose, HARBOR access, KEEL reproduction and LOGBOOK status. ORBIT does not apply. Seven internal role lenses, not independent scientific admission. Role definitions were inspected in this conversation.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Regional winter/summer averages can conceal opposite local trends. | P2 | Seasonal meaning | Preserve the Taiwan/Kyushu reversal note; do not inflate a regional mean into current-wide geometry. Addressed. |
| 2 | The stream cutoff is 0.1 m/s along-axis velocity. | P3 | Boundary | Retain perpendicular sections and exclude 0.4 m/s sensitivity boundaries. |
| 3 | 200 m isobath and transport vertical assumptions do not fix width depth. | P3 | Layer | Surface geostrophic field; fixed layer remains null. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Seasonal widths and mean-field widths have different averaging order. | P2 | Method | Preserve weekly boundary diagnosis before temporal/spatial summaries; weights remain unresolved. Addressed. |
| 2 | The paper gives three numerical means, not three seasons. | P3 | Values | Keep winter 218, summer 207 and study-period 210 distinct. |
| 3 | Interpolating one-third-degree data to 0.1 degree does not add observations. | P3 | Product | Record both grids and weekly smoothing; no confidence interval inferred. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Scalar means could create a 207-218 km animated route buffer. | P2 | Map grammar | Omit width bar/locator and retain null edges plus disabled seasonal playback. Addressed. |
| 2 | Intrusion reach of 313/269 km has another orientation and feature. | P3 | Dimension | Keep it separate from mainstream cross-flow width. |
| 3 | All recorded phases must stay inspectable on map cards. | P3 | Navigation | Three-record atlas/inspector roundtrip and reload checks pass. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Regional mean could be read as entire Kuroshio width. | P3 | Title/scope | Regional surface stream-mean width with explicit ECS domain. |
| 2 | Exact season calendar membership is unreported. | P3 | Time labels | Do not invent DJF/JJA dates; preserve study years as context. |
| 3 | 210 km study-period mean must not become a seasonal state. | P3 | Explanation | Expose temporal statistic and explain mean separately from winter/summer. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | No width bar means text must carry the measurement. | P3 | Equivalent access | Values, method, quality and source stay visible in inspector and expandable card. |
| 2 | Narrow screens require reflow and inspectable source links. | P3 | Reflow | 320 px and keyboard disclosure checks; human assistive-technology review remains pending. |
| 3 | Navigation assertions can read before data finishes loading. | P3 | Browser evidence | Wait for the rendered inspector value instead of an immediate read; do not add arbitrary sleeps. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | New evidence class could admit changed values or invented depth/calendar support. | P2 | Validator | Bind three values to pinned audit/PDF, reject mutated threshold, averaging, dates, layer, width range and current identity. Addressed. |
| 2 | Dashboard build could skip width validation. | P2 | Pipeline | Run width inventory validation before generating coverage and pin actual stream scope audit contents. Addressed. |
| 3 | General protocol hash refresh changes GS provenance only. | P3 | Regeneration | Update general hash/candidate checksum; seventeen numerical frame validator passes. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Coverage receipts must agree with the current inventory. | P3 | Status | 37 records/24 currents; 69 unassessed, five reviewed nonnumeric, two derived candidates. |
| 2 | University-hosted PDF does not establish redistribution permission. | P3 | Custody | Use external publisher links, retain local acquisition receipt; no public release. |
| 3 | Canonical admission and full publication gate remain incomplete. | P3 | Release | Verify frozen canonical checksum; retain independent science and clean-checkout gates. |

## Synthesis

Seven roles, 21 findings: zero P1, five addressed P2, sixteen P3. APPROVED-WITH-CONDITIONS for local editorial scalar display. Top finding: regional temporal/spatial means cannot supply whole-current seasonal map edges. CURRENT, SOUNDER and CHART agree that mean width, averaged field width, seasonal physical bounds and intrusion reach are separate quantities.

## Three amendments

1. Pin source PDF/acquisition and scope audit; preserve product grids, threshold/orientation, diagnosis-before-averaging and unresolved weights/month conventions.
2. Add strict stream-mean evidence class and three independently inspectable records; omit unsupported width geometry/playback and distinguish study mean from seasonal means.
3. Validate width inputs in dashboard generation, fingerprint the audit, count two seasonal samples, refresh general protocol provenance and verify inspector links.

## Evidence and limits

Passed: width validator; 24 width unit tests; 20 dashboard unit tests; 17-frame GS width validator; Kuroshio browser checks (all three records, source definition, route/inspector links, reload, 320 px); JavaScript syntax. Source method page 26 and seasonal page 29 visually inspected, as was figures/kuroshio-stream-mean-width-review.png. Full current-card verification is recorded after its final run in the coverage plan. Canonical hash remains 6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e. Independent scientific admission, human assistive-technology review, full clean-checkout and public release remain open.
