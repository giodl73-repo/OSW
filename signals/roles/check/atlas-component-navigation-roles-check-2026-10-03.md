---
skill: roles-check
topic: atlas-component-navigation
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Family and system navigation

Internal installed role lenses review the code and its browser evidence;
this is not independent scientific approval. These seven roles cover the
scientific scope, provenance, visual grammar, explanation, access, engineering
and project record. ORBIT is not relevant to this navigation change.

| Role | Finding | Severity | Section | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | Connected display could imply a continuous system route | P2 | Family preview | Explicitly deny aggregate continuity and additive length. |
| CURRENT | Component layers and time conventions differ | P3 | Preview | Preserve each component's separate card and scope. |
| CURRENT | Known members are not a complete current census | P3 | List | Incomplete inventory coverage stated beside links. |
| SOUNDER | Published lengths must not be labelled unknown | P2 | Pending cards | Reported-length capability now distinguishes unavailable route geometry from existing length evidence. |
| SOUNDER | Membership must come from the taxonomy inventory | P3 | Code | Uses catalog known_component_currents, without deriving physical membership from map proximity. |
| SOUNDER | No new quantitative measurement is justified | P3 | Data | Route counts and canonical measurements unchanged. |
| CHART | Member highlights need a distinct visual grammar | P3 | CSS | Dashed pale routes identify components; selected current remains gold. |
| CHART | A family fit can span multiple basins | P3 | Map | Fits all declared component paths or locators, not an invented connecting line. |
| CHART | Highlights must clear on exit | P3 | Selection | Global reset and child selection clear related classes; browser verified. |
| BEACON | Names must lead to visual records | P3 | Links | Component links choose the atlas feature and its available card. |
| BEACON | System lengths cannot be summed casually | P3 | Explanation | Overlapping-route sum warning displayed in preview. |
| BEACON | Unbuilt geometry needs a specific status | P3 | List | Distinguishes source-reported length, route pending, and available reference cards. |
| HARBOR | Selection must work with keyboard | P3 | Anchors | Enter descent and parent return tested for all 17 links. |
| HARBOR | Relation cannot be encoded by color alone | P3 | Preview | Equivalent textual list and status identify highlighted components. |
| HARBOR | Narrow layout must retain card navigation | P3 | Reflow | 320 px family and selected component route checks pass. |
| KEEL | Nested families require navigation in both directions | P3 | Links | Equatorial family hierarchy tested through its immediate members. |
| KEEL | Existing atlas controls must still work | P3 | Regression | 100-current/140-eddy zoom, pan, card return and mobile test passes. |
| KEEL | Browser links must preserve normal browser behavior | P3 | Handler | Modified clicks retain standard URL navigation; local unmodified click selects feature. |
| LOGBOOK | UI coverage does not increase route measurements | P3 | Status | Seven family/system records, 17 component links; route coverage unchanged. |
| LOGBOOK | Claims of official taxonomy remain premature | P3 | Evidence | Existing editorial taxonomy used; no official scientific endorsement claimed. |
| LOGBOOK | Verification must be reproducible | P3 | Test | analysis/test_atlas_component_navigation_browser.py records complete link enumeration. |

21 findings: 0 P1, 2 P2 resolved, 19 P3 notes. Approved with conditions for
editorial navigation. Scientific completeness and system continuity remain
unestablished. Amendments: explicit nonadditive scope, distinguish published
length from absent geometry, and verify every component descent/return.
CURRENT, CHART and SOUNDER agree that membership links cannot establish
continuous flow. No full repository suite claim.
