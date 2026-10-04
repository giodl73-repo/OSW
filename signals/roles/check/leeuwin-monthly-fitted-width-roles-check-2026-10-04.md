---
skill: roles-check
topic: leeuwin-monthly-fitted-width
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 3
p2_remaining: 0
p3_count: 18
verdict: APPROVED-WITH-CONDITIONS
---

# Leeuwin monthly fitted width review

Artifact: PDF acquisition/scope audit, protocol v1.18, two editorial monthly
records, validator, atlas/inspector and dashboard. CURRENT checks physics;
SOUNDER custody; CHART meaning; BEACON prose; HARBOR access; KEEL reproduction;
LOGBOOK status. ORBIT is inapplicable. Internal role lenses are not independent
scientific admission. Role definitions were inspected in this session.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A source coefficient described as about half maximum could be silently replaced by an exact threshold. | P2 | Boundary rule | Preserve 1.89 and 43.45-degree correction; mutation checks reject changed conventions. Addressed. |
| 2 | Monthly averages of fitted widths are not widths of averaged velocity fields. | P3 | Averaging order | Retain fit-per-cycle then monthly averaging in audit and inspector. |
| 3 | The 80 m transport layer does not define width depth. | P3 | Layer | Keep fixed measurement layer null and reject transport-layer promotion. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Repository/web titles did not reliably identify the document version. | P2 | Custody | Acquire published-layout PDF, inspect title/pages and pin bytes/DOI/acquisition receipt. Addressed. |
| 2 | Section and caption disagree at July/August 2002. | P3 | Time scope | Retain all source period labels; exact combined averaging period remains unresolved. |
| 3 | Only two monthly prose values have been extracted. | P3 | Coverage | Keep full monthly curve false and remaining ten values unfilled. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Two month values could appear to form a complete annual movie. | P2 | Inspector | Disable playback, omit edge locator/full-width bar and state remaining months unextracted. Addressed. |
| 2 | Source mean axis is not monthly lateral geometry. | P3 | Audit/map | Keep mean-axis coordinates in source context; do not draw width edges from them. |
| 3 | 50 km filter window and table RMS do not create current-width intervals. | P3 | Encoding | Keep filter length and RMS separate from width/confidence. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Generic seasonal state wording could imply one observed year. | P3 | Title | Use Monthly climatological fitted width and explicit calendar-month composite description. |
| 2 | Time scope was repeated in both value and definition. | P3 | Inspector | Remove duplicate definition text; regenerated browser screenshot. Addressed. |
| 3 | Prose extrema only apply to the source crossing. | P3 | Scope | State a101 near 26 S; no full-current annual extrema or ranked width inferred. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Scope must be available without perceiving a width bar. | P3 | Text | Retain value, boundary, layer and missing-month information as text. |
| 2 | Each month requires an independently shareable record. | P3 | Navigation | April and September query/reload and atlas-inspector roundtrips pass. |
| 3 | Narrow reflow must preserve evidence class. | P3 | Reflow | 320 px no-overflow check passes; human assistive-technology review remains pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | New evidence class must bind values to month and source bytes. | P3 | Validator | Pinned audit/PDF hashes and semantic mutation checks pass. |
| 2 | Protocol update changes derived provenance without changing existing numerical frames. | P3 | Hashes | Refresh width inventory and GS provenance; 17-frame validator passes. |
| 3 | Dashboard time samples must not imply an animation or an exact date. | P3 | Capabilities | Count two phase records, no series; dashboard test passes. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Current coverage differs from earlier dated receipts. | P3 | Counts | Record 34 scoped records, 23 names, 70 unassessed, five reviewed nonnumeric, two derived candidates. |
| 2 | Acquiring a source PDF does not authorize public redistribution. | P3 | Boundary | Use external source link; local custody only, no public release promoted. |
| 3 | Canonical admission and full release remain unproven. | P3 | Release | Retain canonical checksum; independent science, human accessibility and clean-checkout gates pending. |

## Synthesis

Seven roles, 21 findings: zero P1, three addressed P2, 18 P3.
APPROVED-WITH-CONDITIONS for local editorial source display. Top finding:
preserve fitted-width boundary and averaging conventions. CURRENT, SOUNDER
and CHART agree that two local monthly composites do not establish a full
annual field or complete current width. Independent science admission, human
accessibility and full clean-checkout/publication gates remain pending.

## Three amendments

1. Pin the published PDF and audit; preserve source coefficient, angle and
   unresolved period labels rather than correcting them silently.
2. Add monthly climatological fit class with averaging-order metadata, null
   occupied geometry/layer/dates and false annual/ranking/playback flags.
3. Show each month as inspectable source evidence; reject unsupported curve,
   confidence and layer promotion; verify all-current atlas disclosures.

## Checks and limits

Passed: width-inventory validator, 23 width unit tests, 19 dashboard unit tests,
17-frame section-series validator, Leeuwin browser test and all100-current
inline-width test (34 unique records). Node syntax passes. Visual checks:
local source PDF pages 138, 143, 144; figures/leeuwin-monthly-fit-width-review.png.
Publisher full-page/web screenshot requests failed; manuscript direct download
returned non-PDF. Published-layout mirror download succeeded and is pinned.
No raw altimetry reprocessing, full monthly curve digitization or release gate
claimed. Canonical almanac SHA256 unchanged.

Commands: `python analysis/check_current_width_inventory.py`,
`python analysis/test_current_width_inventory.py`,
`python analysis/test_motion_dashboard.py`,
`python analysis/check_current_section_width_series.py`,
`python analysis/test_leeuwin_monthly_fit_browser.py`,
`python analysis/test_atlas_inline_width_browser.py`.
Browser checks use OSW_TEST_BROWSER and the existing local preview.
