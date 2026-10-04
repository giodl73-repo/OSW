---
skill: roles-check
topic: reported-month-section-locator
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Reported month-section locator review

Internal editorial review of `current-section-locator.js`, atlas integration and focused browser fixtures. Seven roles cover physical support, provenance, cartography, explanation, accessibility, reproducibility and repository status. ORBIT is inapplicable: no planetary analogy. No independent scientific admission implied.

## CURRENT

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Reported 6-8 S geography does not establish a full-depth current axis. | P3 | section locator / browser / source audit | Dashed section locator and explicit depth counterflow context. |
| 2 | Exact sampling days remain unknown. | P3 | section locator / browser / source audit | March 1994 is retained at month precision. |
| 3 | Longitudinal and annual coverage remain missing. | P3 | section locator / browser / source audit | No route, full-width bar, buffer or annual interpolation added. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Reported limits must be distinguished from computed conversion limits. | P3 | section locator / browser / source audit | Only explicit source latitude limits accepted; old center/span-only NEUC rejected. |
| 2 | Midpoint must not become a source center. | P3 | section locator / browser / source audit | Source center null and computed role validated; forged-center fixture rejected. |
| 3 | Raw velocity edges and exact local days are unacquired. | P3 | section locator / browser / source audit | Existing source audit retains these admission gates. |

## CHART

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | A band bracket must not resemble an observed trajectory. | P3 | section locator / browser / source audit | Section map uses a blue bracket; atlas uses dashed locator, separate route class. |
| 2 | Zoom must include both reported limits. | P3 | section locator / browser / source audit | Browser asserts 30 W and both -8/-6 latitude points inside selected view. |
| 3 | Map date/depth/source meaning must survive close view. | P3 | section locator / browser / source audit | Card labels month precision and depth context; source link and coarse equirectangular display stated. |

## BEACON

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | A mapped number can be repeated as a whole-current width. | P3 | section locator / browser / source audit | About 220 km described meridional band span stays beside map. |
| 2 | Month precision can be mistaken for a March-long continuous survey. | P3 | section locator / browser / source audit | Exact days unresolved shown in visible text and SVG accessible description. |
| 3 | Navigation must lead from visual insight to evidence. | P3 | section locator / browser / source audit | Atlas card links source, audit, seasonal evidence and distinct SEUC record. |

## HARBOR

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Map-only activation must work on keyboard. | P3 | section locator / browser / source audit | Enter on section locator selects correct current; global reset exercised. |
| 2 | Long scope text must reflow. | P3 | section locator / browser / source audit | Focused browser checks 320 px without horizontal overflow. |
| 3 | Locator meaning cannot rely on color alone. | P3 | section locator / browser / source audit | Accessible SVG description and adjacent text state limits, date precision and evidence class. |

## KEEL

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Malformed month/center/edge claims could silently generate geography. | P3 | section locator / browser / source audit | Mutation fixtures reject invalid month, invented days, source center, reverse limits and observed-edge relabeling. |
| 2 | Existing day-dated Indian locator must remain valid. | P3 | section locator / browser / source audit | Indian EUC focused browser passes map, deep-link restore, global return and stale-section reset. |
| 3 | New map must not invalidate phase navigation. | P3 | section locator / browser / source audit | 100 current links, 62 route cards, 27 phases and six seasonal round trips checked separately. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation / evidence |
|---|---|---|---|---|
| 1 | Local display work must not increment route or scientific measurement counts. | P3 | section locator / browser / source audit | 19 width records / 15 names; 62 candidates / 59 names remain unchanged. |
| 2 | Independent scientific approval has not occurred. | P3 | section locator / browser / source audit | Internal editorial review only; raw-field and independent admission conditions retained. |
| 3 | Documentation and screenshots should describe current rendered state. | P3 | section locator / browser / source audit | Both Atlantic screenshots inspected; updated test and coverage note recorded. |

## Synthesis and amendments

Seven roles / 21 findings; zero P1, zero outstanding P2, 21 P3 verified notes or scientific admission conditions. APPROVED-WITH-CONDITIONS for local display. CURRENT, SOUNDER and CHART agree that geographic section support is distinct from a current axis or paired velocity edges.

Three amendments implemented:

1. Accept author-reported limits with explicit computed-center semantics; reject center/span-only normalization and forged edge claims.
2. Carry day/month precision into headings, SVG descriptions, selected status and atlas legend.
3. Add restore, keyboard/global return, coordinate-fit, invalid-input and stale-section browser checks; preserve Indian day-dated behavior.

Validation: focused Atlantic SECC and Indian EUC browser checks pass; Atlantic atlas and explorer screenshots inspected. Shared navigation test covers 100 current links, 62 route cards, 27 phase links and six seasonal round trips. Canonical almanac and scientific measurements unchanged. Full repository suite not rerun. Source pinning, raw-field recovery, layer-specific boundaries, seasonal axes and independent scientific admission remain open.
