---
skill: roles-check
topic: north-brazil-guiana-oblique-widths
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 3
p2_remaining: 0
p3_count: 18
verdict: APPROVED-WITH-CONDITIONS
---

# North Brazil–Guyana oblique width integration

Artifact: source audit, protocol v1.16, three editorial width records, validator,
explorer and dashboard integration. Physical scope (CURRENT), provenance
(SOUNDER), geography (CHART), explanation (BEACON), equivalent access (HARBOR),
reproducibility (KEEL) and repository accuracy (LOGBOOK) are relevant. ORBIT is
inapplicable: no planetary comparison. Internal installed role lenses do not
constitute independent scientific identity or measurement admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Oblique latitude span cannot be read as meridional width. | P2 | Source audit / inventory / explorer | Keep author kilometre values and 45-degree rotation; fixed and tested. |
| 2 | Guyana continuation overlaps source NBC3 band around 10 N. | P3 | Source audit / inventory / explorer | Preserve source mapping, not hard boundary or alias merge. |
| 3 | Mean-field width is not instantaneous mean or annual extrema. | P3 | Source audit / inventory / explorer | Retain zero-contour/averaging order and false eligibility. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | NBC2 table 220 km conflicts with 20 km prose comparison. | P2 | Source audit / inventory / explorer | Retain both with unresolved discrepancy, not a range; implemented. |
| 2 | Exact section coordinates remain unextracted. | P3 | Source audit / inventory / explorer | Longitude, endpoints and observed geometry null; no fake locator. |
| 3 | Source access comprises relevant HTML and indexed PDF table, not acquired raw data. | P3 | Source audit / inventory / explorer | Record exact inspected source scope and remaining acquisition gates. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Hidden bar retained a visible bar-scale sentence. | P2 | Source audit / inventory / explorer | Use range interpretation when bar is hidden; fixed and screenshot regenerated. |
| 2 | Reference route geography must remain separate from section metric. | P3 | Source audit / inventory / explorer | Preserve context map labels; no route buffer or new current route. |
| 3 | Oblique mean evidence is not a seasonal phase animation. | P3 | Source audit / inventory / explorer | Disable playback and omit invented edge locator. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Mean oblique section title exposes the spatial support. | P3 | Source audit / inventory / explorer | Keep section and source-flow labels visible. |
| 2 | Source rotation and averaging period must accompany numeric width. | P3 | Source audit / inventory / explorer | Show 45 degrees and 1993–2017 month-period context. |
| 3 | Discrepancy must remain visible outside the audit file. | P3 | Source audit / inventory / explorer | Show source note in explorer and published-width table. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Omitted geometry needs an equivalent text description. | P3 | Source audit / inventory / explorer | Retain layer, boundary, rotation and naming text. |
| 2 | Playback disabled state should prevent fabricated seasonal motion. | P3 | Source audit / inventory / explorer | Three section selections and disabled control tested. |
| 3 | Saved records and atlas return must survive mobile reflow. | P3 | Source audit / inventory / explorer | All three records tested at 320 px; human review remains pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Oblique class could be reclassified as meridional with invented longitude. | P3 | Source audit / inventory / explorer | Validator rejects axis-kind escape and source-context mutations. |
| 2 | Metadata update must preserve existing 17 Gulf Stream profiles. | P3 | Source audit / inventory / explorer | General protocol hash only; source recomputation validator passes. |
| 3 | Guiana dashboard previously asserted zero scoped widths. | P3 | Source audit / inventory / explorer | Update to one scoped mean section while preserving zero routes/time samples. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Counts should distinguish three sections from two newly covered identities. | P3 | Source audit / inventory / explorer | 31 records across 21 names, 72 unassessed; document exact coverage. |
| 2 | Local source extraction must not promote public dataset or ranked lengths. | P3 | Source audit / inventory / explorer | Canonical SHA unchanged, 11 ranks and 62 routes unchanged. |
| 3 | Focused tests cannot be claimed as public release approval. | P3 | Source audit / inventory / explorer | Retain scientific/human review and full repository gate as pending. |

## Synthesis

Seven roles; 21 findings; zero P1; three P2 addressed; 18 P3 notes.
APPROVED-WITH-CONDITIONS for local evidence display. Top finding: a source
oblique section span cannot become a meridional locator or whole-current width.
CURRENT, SOUNDER and CHART agree on retaining unextracted geometry and the mean
field convention. Independent science/human accessibility review and the public
release gate remain pending.

## Three amendments

1. Add protocol v1.16 oblique-section support and pinned audit; reject invented
   location, axis convention, source labels, identity mapping and temporal support.
2. Preserve source 520/220/440 km section values and the unresolved 20 km prose
   discrepancy without a fabricated interval or canonical Guiana/NBC merge.
3. Display mean oblique evidence with no bar/edge/playback; remove stale scale
   text, verify source notes, saved views, atlas return and narrow-width layout.

## Verification

21 width tests and 18 dashboard tests passed; inventory and 17-frame width-series
provenance validators passed. Three-record oblique browser test passes, covering
all numeric values, orientation, conflict/naming notes, omitted bar/locator,
disabled playback, reload, atlas/table navigation and 320 px reflow. Existing
Labrador and Tsuchiya browser checks are recorded after the final render change.
`node --check almanac/seasons.js` passes. No full-suite/clean-checkout claim.

Commands: `python analysis/test_current_width_inventory.py`,
`python analysis/test_motion_dashboard.py`,
`python analysis/check_current_width_inventory.py`,
`python analysis/check_current_section_width_series.py`,
`python analysis/test_oblique_mean_width_browser.py`,
`python analysis/test_labrador_regional_width_browser.py`,
`python analysis/test_tsuchiya_angular_width_browser.py`.
The browser tests use the existing preview and installed Chromium selected by
`OSW_TEST_BROWSER`. Screenshot: `figures/guiana-oblique-mean-width-review.png`.
Canonical ledger SHA256:
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.
