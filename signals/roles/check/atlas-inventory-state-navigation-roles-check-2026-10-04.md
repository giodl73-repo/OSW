---
skill: roles-check
topic: atlas-inventory-state-navigation
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 5
p2_remaining: 0
p3_count: 16
verdict: APPROVED-WITH-CONDITIONS
---

# Atlas inventory and state navigation review

## Artifact and scope

Code/interface review of `atlas-directory.js`, `atlas-state-navigation.js`,
`reference-route-atlas.js`, `reference-routes.js` and their HTML controls, saved
route-state join and dashboard eddy state evidence. These interfaces expose the
existing 100 currents, 136 named eddies, four dated detections and 56 OSW states.
They do not admit measurements, source claims or physical state membership.
This is an internal review using installed role lenses, not independent
scientific review or a completed public release gate.

## Role selection

CURRENT: physical scope of route and eddy relations. SOUNDER: saved evidence,
missing inputs and source/display distinction. CHART: cartogram geometry,
coast clipping and hit areas. BEACON: evidence labels and source navigation.
HARBOR: keyboard, focus, status and textual alternatives. KEEL: lifecycle,
parsing and regression coverage. LOGBOOK: project status and reproducibility.
ORBIT is inapplicable: no planetary comparison introduced.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C1 | State filters expose editorial scenario crossings, not a diagnosed whole-current footprint. | P3 | Directory state context and card | Retain nominal/alternative labels and route scope. Implemented. |
| C2 | Shared gateways represent unresolved individual centers and do not establish containment. | P3 | Eddy index and state evidence | Preserve gateway wording and use existing scoped cards. Implemented. |
| C3 | No matching record is an evidence gap, not physical absence; subsurface and time scopes remain in cards. | P3 | Empty filter and state context | Preserve absence statement and layer/time details. Implemented. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | Schema and group counts alone accepted empty province path strings. | P2 | State geometry parser | Reject missing names/paths and empty path data before installing the layer. Fixed; malformed fixture passes. |
| S2 | Route-state source failure could otherwise look like a complete zero-current result. | P3 | Directory fallback | Explicitly label unavailable current links while keeping saved eddy relations. Verified. |
| S3 | Multiple component routes and eddy relations share an identity; they are not independent physical observations. | P3 | State identity sets | Deduplicate identity display, retain original relation labels/date and source receipts in cards. Verified across all states. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| T1 | Ocean masking alone is not sufficient to exclude land from pointer hit regions. | P3 | State layer | Keep both saved ocean mask and even-odd clip; three inland test points excluded. Implemented. |
| T2 | Seam-split province geometry must remain identical to saved atlas geography. | P3 | All 56 state paths | Compare exact path strings rather than infer polygons from bounding boxes. Verified. |
| T3 | The state filter narrows the index while the map retains other geography; zoom does not add geographic precision. | P3 | State context and map caption | Preserve navigation-only/cartogram semantics; no new intersection claims. Implemented. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | Index route, locator, reported center, dated outline and gateway classes could be conflated. | P3 | Compact entries | Keep evidence class visible next to each name and preserve detailed card classification. Implemented. |
| B2 | Update lights may be read as live ocean activity. | P3 | Update filter and captions | State inventory-edit baseline meaning beside controls. Implemented. |
| B3 | State names and scope must lead directly to methods and receipts. | P3 | State context/card links | Retain state passport link and existing route/eddy receipts. Verified. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| H1 | State keyboard activation scrolled to the index while leaving focus on the offscreen SVG region. | P2 | Region activation | Move focus to the state selector on deliberate activation and announce state loading/errors. Fixed; all 56 keyboard selections verified. |
| H2 | Late initial route/proposal rendering could reset and focus the atlas after user interaction. | P2 | Initial deep-link callbacks | Guard initial reveal callbacks with the original address and pointer/keyboard interaction state; keep explicit anchor/hash navigation. Fixed; state-focus and monthly-link checks pass. |
| H3 | Visual update/selection colors require a textual equivalent and mobile reflow. | P3 | Index buttons and controls | Preserve aria-pressed, evidence text, update labels, visible focus and dropdown alternatives. 320 px checks pass; independent human accessibility review remains pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | Awaiting optional state-shape fetch delayed map control binding and deep-link restoration. | P2 | Atlas initialization | Initialize state layer independently; keep map controls and cards usable while pending. Fixed; held-request test verifies zoom and current selection before response, with no late reset. |
| K2 | Slow/unavailable/malformed geometry must preserve the 240-entry directory. | P3 | State navigation fallback | Exercise held request, 503 and empty-path fixtures. Verified. |
| K3 | Full clean-checkout/offline publication validation has not been run for this local increment. | P3 | Release gate | Report only focused browser and syntax evidence; retain public gate requirement. Unresolved release condition. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | Changing the state dropdown with an open card left its share link at the prior state. | P2 | Shared atlas view | Synchronize the existing share anchor after state changes while retaining selected feature/month parameters. Fixed; selected-card state-change/reload checks pass. |
| L2 | Current documentation must distinguish identity coverage from route/measurement completeness. | P3 | README and coverage plan | Retain 100/136/4 index coverage, scoped evidence labels, unchanged canonical data and pending science/release gates. Updated. |
| L3 | Review receipt and runnable commands should accompany the affected interfaces. | P3 | This receipt | Record source files, commands, results and three amendments. Implemented below. |

## Synthesis

Roles reviewed: 7. Findings: 21. P1: 0. P2: 5, all addressed. P3: 16.
Verdict: APPROVED-WITH-CONDITIONS for the local atlas interface.
Top finding: optional state-shape acquisition must not block core current/card
navigation. HARBOR and KEEL agree that asynchronous initial work must preserve
explicit user focus and selection. CURRENT, SOUNDER and CHART agree that a
state link is only as strong as its retained geometry, time and evidence class.

Conditions remaining: independent scientific claim admission, independent human
accessibility review and the complete clean-checkout repository publication gate.
The frozen public dataset is not promoted by this review. Canonical SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

## Three amendments applied

1. Decouple optional state geometry from core control initialization; reject
   empty geometry and verify delayed/503/malformed fallback without selection loss.
2. Correct activation focus and guard delayed initial deep-link reveals after
   user interaction; preserve keyboard access and existing monthly restoration.
3. Synchronize state-dependent share links and retain evidence/date/scope labels
   alongside updated README, coverage plan and verification receipts.

## Verification

Run locally against the existing preview with `OSW_TEST_BROWSER` pointing to an
installed Playwright Chromium executable:

```
python analysis/test_atlas_state_navigation_browser.py
python analysis/test_atlas_directory_states_browser.py
python analysis/test_atlas_monthly_section_browser.py
node --check almanac/atlas-directory.js
node --check almanac/atlas-state-navigation.js
node --check almanac/reference-route-atlas.js
node --check almanac/reference-routes.js
```

All seven commands passed after amendments. The prior complete index test also
passed before these review amendments; no full-suite or clean-release claim.
Saved visual receipts: `figures/atlas-directory-review.png`,
`figures/atlas-state-directory-review.png`,
`figures/atlas-clickable-states-review.png`. No live source refresh performed.
