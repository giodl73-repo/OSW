---
skill: roles-check
topic: east-australian-regional-width
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 3
p2_remaining: 0
p3_count: 18
verdict: APPROVED-WITH-CONDITIONS
---

# East Australian regional width review

Artifact: institutional source audit, protocol v1.17, editorial scalar record,
validator, inspector/atlas display and coverage snapshot. CURRENT checks physical
support; SOUNDER source custody; CHART map meaning; BEACON explanations; HARBOR
access; KEEL reproducibility; LOGBOOK repository status. ORBIT is inapplicable.
These are internal role lenses, not independent scientific reviewers.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The 30 km typical current width and 100 km strong-influence scale could be mistaken for seasonal endpoints. | P2 | Audit/record | Preserve the institutional 30 km scalar only; separate influence scale and reject substituted value/range. Addressed. |
| 2 | A typical 200 m depth extent does not specify a measurement layer. | P2 | Protocol/context | Keep fixed layer null and reject promotion of depth extent. Addressed. |
| 3 | Downstream extension, branches and eddies are not a uniform current envelope. | P3 | Scope | Keep regional support and whole-current/ranking flags false. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Plan title dates and edited date differ from observations. | P3 | Provenance | Record 2015-25 plan and 25 September 2014 date; observation period remains null. |
| 2 | Underlying Mata and Ridgway/Dunn studies remain uninspected for this width. | P3 | Source quality | Identify institutional synthesis and retain original-study gate. |
| 3 | PDF text was inspected but screenshot fetch failed. | P3 | Source access | Disclose text-only inspection; do not claim raw data or pixel extraction. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Scalar prose does not justify a route buffer. | P3 | Map | Leave route geometry untouched; hide full-width bar and edge locator. |
| 2 | Zoom cannot supply missing section edges. | P3 | Atlas card | Keep source boundary rule and about 30 km text alongside route context. |
| 3 | 240 km array and 200 km eddy diameter have other geometric meanings. | P3 | Audit | Preserve exclusions without drawing them as current width. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Generic measurement wording could obscure summary support. | P3 | Title/metric | Use Regional width summary and institutional regional prose label. |
| 2 | Seasonal strength statements do not provide seasonal width samples. | P3 | Protocol | State distinction; do not enable annual range or playback. |
| 3 | Readers need a direct path to exact source context. | P3 | Links | Retain source citation, printed page 23, section 3.3.1 and inspector link. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Meaning must survive without a bar or color. | P3 | Definitions | Values, support, limits and source remain visible text. |
| 2 | Disclosure must expose the same source through keyboard. | P3 | Atlas width disclosure | All-current Enter expansion/source checks pass for 32 records. |
| 3 | Narrow-screen card must retain scope and source. | P3 | Reflow | 320 px no-overflow check passes; human assistive-technology review remains pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Atlas evidence regression froze the prior count at 31. | P2 | Browser check | Check current inventory count and unique IDs while retaining per-current assertions. Addressed. |
| 2 | New audit allowance must remain identity-specific. | P3 | Validator | Permit exact Labrador/EAC audit map; reject swapped audit, altered values and hashes. |
| 3 | Protocol revision affects derived provenance. | P3 | Hashes | Refresh general-protocol and series hashes; 17-frame numerical/provenance validator passes. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Coverage now differs from earlier milestones. | P3 | Status | Record 32 records/22 names/71 unassessed; earlier dated receipts remain historical. |
| 2 | Canonical length and width admission has not changed. | P3 | Ledger | Retain canonical checksum and existing published length ranks. |
| 3 | Focused local checks do not prove a public release. | P3 | Release | Full clean-checkout gate, independent scientific admission and human accessibility review remain pending. |

## Synthesis

Seven roles, 21 findings: no P1, three addressed P2, 18 P3.
APPROVED-WITH-CONDITIONS for local editorial summary display. Top finding:
current width and influence scale must not become seasonal endpoints. CURRENT,
SOUNDER and CHART agree that prose scales do not establish occupied section
geometry or annual variation. No public-release or canonical-admission claim.

## Three amendments

1. Pin 30 km to the institutional source and keep 100 km influence, array span
   and eddy diameters separate; reject substituted scalars and seasonal ranges.
2. Preserve null dates, geometry and fixed layer; make contextual depth explicit
   and reject fixed-layer inference. Retain underlying-study and access gates.
3. Replace frozen width count with exact current inventory coverage, verify card
   and inspector rendering, and refresh derived protocol provenance.

## Checks and limits

Passed: width validator; 22 width unit tests; 18 dashboard unit tests;
17-frame section-series validator; EAC browser test; all100-current inline-width
browser test (32 unique records). Screenshot inspected:
`figures/east-australian-regional-width-review.png`.
Initial browser assertions expected a source note in the citation element and
an unavailable-range message instead of the explicit comparability caveat;
corrected to check the actual definition and range text. Initial main validator
reported a stale inventory protocol checksum; refreshed and revalidated before
rebuilding the dashboard. No full-suite gate asserted.

Commands: `python analysis/check_current_width_inventory.py`,
`python analysis/test_current_width_inventory.py`,
`python analysis/test_motion_dashboard.py`,
`python analysis/check_current_section_width_series.py`,
`python analysis/test_east_australian_regional_width_browser.py`,
`python analysis/test_atlas_inline_width_browser.py`.
Browser checks use OSW_TEST_BROWSER and the existing local preview.
