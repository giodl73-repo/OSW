---
skill: roles-check
topic: alaska-coastal-gulf-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Gulf-of-Alaska typical width: internal role review

Artifact: source audit, width record, receipt/index integration, regional summary
UI and browser runner correction. Seven installed roles cover physics,
provenance, maps, public science, accessibility, verification and publication.
This is internal review, not independent scientific peer review.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Winter experiment dates do not date the prose width. | P2 | Time support | Resolved: dates/months null; no winter-width claim. |
| 2 | Seasonal variability is qualitative here. | P3 | Range | Preserve unknown annual and monthly bounds. |
| 3 | Similarly named currents have different identities. | P3 | Scope | Exclude offshore Alaska and Arctic/Bering flows. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Scalar source audits were not consistently bundle-bound. | P2 | Inputs | Resolved: bind all scalar audit files and boundary wording. |
| 2 | Original width observations remain unreviewed. | P3 | Source quality | Retain literature-summary status and remaining gate. |
| 3 | No PDF/source-field acquisition is proven. | P3 | Access | State HTML inspection accurately; retain DOI/locator. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Scalar must not produce a mapped width buffer. | P2 | Visualization | Resolved: existing summary hides bar and edge locator. |
| 2 | A regional scale does not locate the whole current. | P3 | Atlas | Keep unresolved route and physical footprint status. |
| 3 | Nearby bathymetry is not width measurement depth. | P3 | Layer | Fixed layer remains null. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Paper title could imply a winter width measurement. | P2 | Label | Resolved: typical regional summary label and explanation. |
| 2 | Approximately 35 is not a precise uniform width. | P3 | Value | Retain approximate scalar and no whole-current rank. |
| 3 | No uncertainty interval is given. | P3 | Range | Do not manufacture margins or a midpoint. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Numeric summary must remain usable without a map. | P3 | UI | Text, source and query row carry complete meaning. |
| 2 | New record needs narrow-screen verification. | P3 | Browser | Exercise 320 px and visually inspect screenshot. |
| 3 | Source evidence needs a direct query path. | P3 | Index | Register the new audit plus both prior scalar audits. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Stale frame checksum prevented bundle generation. | P2 | Dependencies | Resolved: unchanged frames reviewed and receipt refreshed. |
| 2 | Initialization assertion ran before WASM was ready. | P3 | Browser | Wait for the rendered summary before assertions. |
| 3 | CI children require a shared default browser. | P3 | Runner | Resolve installed Chromium centrally; preserve overrides. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Mainline publication is not established. | P2 | CI | Open condition: require exact-head checks and merge evidence. |
| 2 | Full core-gap goal remains unfinished. | P3 | Receipt | Keep all remaining route/width/eddy work explicit. |
| 3 | Earlier measurements must remain stable. | P3 | Data | Compare all 72 old records and six frame objects exactly. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. P2 issues: 6. P3 notes: 15.
Five P2 implementation findings addressed; final local validation is
recorded (818 tests, 628 subtests, 38 Rust tests and targeted browser checks;
two final runner tests also pass), and protected-main CI remains open. APPROVED-WITH-CONDITIONS.

Top finding: the approximately 35 km introduction scale cannot inherit the
winter experiment's dates, boundaries or layer. CURRENT, SOUNDER and BEACON agree.

Three amendments:

1. Preserve regional scalar scope and null temporal/layer/boundary support.
2. Bind searchable scalar source audits and reject altered source values or
   invented observation support.
3. Refresh reviewed dependencies, record actual validation outcomes and fix
   the CI browser environment before claiming publication.
