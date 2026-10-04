---
skill: roles-check
topic: labrador-regional-width
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 3
p2_remaining: 0
p3_count: 18
verdict: APPROVED-WITH-CONDITIONS
---

# Labrador regional width review

Artifact: source-scope audit, width protocol v1.15, editorial record, validator,
seasonal explorer rendering and dashboard integration. CURRENT checks physical
scope; SOUNDER source custody; CHART visual meaning; BEACON wording; HARBOR
access; KEEL reproducibility; LOGBOOK repository status. ORBIT is inapplicable:
no planetary analogy. Internal role lenses are not independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Bathymetric contours were at risk of becoming an averaging-depth interval. | P2 | Inventory/audit | Keep 300–1000 m as bathymetry only; fixed layer remains null. Addressed. |
| 2 | Regional main slope width does not describe all branches. | P3 | Scope | Retain onshore branches and Flemish Cap bifurcation caveat. |
| 3 | 60 N–43 N extent cannot supply measured along-current length or width edges. | P3 | Audit | Keep length and section geometry null; ranking unchanged. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Publisher full-text index access could be overstated as acquired article evidence. | P2 | Access receipt | Explicit indexed-section/403/no-PDF statement included. Addressed. |
| 2 | Approximate 50 km comes from introductory regional prose, not new map extraction. | P3 | Metric | Preserve scalar summary class and paragraph 29 locator. |
| 3 | Underlying Lazier and Wright observations were not independently reviewed. | P3 | Remaining gates | Keep source/measurement admission pending. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A full-width bar would imply paired lateral boundaries. | P3 | Explorer | Omit bar and edge locator for regional scalar summaries. |
| 2 | Existing editorial route supplies geographic context only. | P3 | Map | Keep Static route context label; do not buffer the line. |
| 3 | Approximate regional scale does not gain precision from map zoom. | P3 | Display | Keep about 50 km and unresolved edges. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Generic recorded-evidence title obscured regional support. | P3 | Explorer title | Use Regional width summary; implemented. |
| 2 | Source-access note was appended twice during integration. | P2 | Definition | Remove duplicate and regenerate screenshot. Addressed. |
| 3 | Nearby speed range does not define boundary threshold. | P3 | Audit | Retain speed as context and boundary rule unresolved. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Text must carry evidence scope without a bar or palette. | P3 | Definition/source | Regional prose, bathymetry, dates and source remain text. |
| 2 | Single summary cannot support seasonal playback. | P3 | Controls | Playback disabled; annual range unavailable. |
| 3 | Current-to-atlas and width-table paths must work at narrow widths. | P3 | Navigation | 320 px test and browser links pass; human review pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | New evidence class needs semantic mutation checks. | P3 | Validator/tests | Reject invented edges, range, time, layer, eligibility and changed source audit. |
| 2 | Protocol hash refresh must preserve existing Gulf Stream numbers. | P3 | Derived metadata | Only general hash refreshed; 17-frame recomputation validator passes. |
| 3 | Growing width inventory invalidated a frozen row-count assertion. | P3 | Tsuchiya browser test | Use current saved inventory count; existing regression passes. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Coverage claims must match 28 records/19 names/74 unassessed. | P3 | README/coverage | Updated with five reviewed nonnumeric and two derived pending. |
| 2 | Canonical ledger and published length ranking remain separate. | P3 | Status | SHA256 unchanged; no ranked length added. |
| 3 | Local checks do not satisfy public publication gates. | P3 | Release | Record focused checks and pending independent reviews; no release promotion. |

## Synthesis

Seven roles, 21 findings: zero P1, three addressed P2, 18 P3.
APPROVED-WITH-CONDITIONS for local source summary display. Top finding:
retain the source's regional prose support without turning bottom contours into
measurement depths. CURRENT, SOUNDER and CHART agree that a prose width is not
a paired occupied section or a route buffer. Independent scientific admission,
human accessibility review and the complete publication gate remain pending.

## Three amendments

1. Add regional scalar class with null range, geometry, fixed layer and dates;
   pin source audit and reject semantic promotion through mutation tests.
2. State indexed-publisher access and incomplete PDF/underlying-source review;
   preserve approximately 50 km as a regional description, with no ranked length.
3. Label regional support, omit bar/edge inference/playback, remove duplicated
   access note and verify mobile, mapped-card and width-table navigation.

## Checks and limits

Passed: 20 width unit tests; 18 dashboard unit tests; width-inventory and
17-frame section-series provenance validators; Labrador browser test; Tsuchiya
browser regression. Initial module-style unittest invocation failed because
these scripts use sibling imports; their documented direct-script commands pass.
No full-suite/clean-checkout public-release result asserted.

Commands: `python analysis/test_current_width_inventory.py`,
`python analysis/test_motion_dashboard.py`,
`python analysis/check_current_width_inventory.py`,
`python analysis/check_current_section_width_series.py`,
`python analysis/test_labrador_regional_width_browser.py`,
`python analysis/test_tsuchiya_angular_width_browser.py`.
Browser commands use the existing preview and an installed Chromium executable
through `OSW_TEST_BROWSER`. Visual receipt:
`figures/labrador-regional-width-review.png`.
Canonical ledger SHA256 unchanged:
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.
