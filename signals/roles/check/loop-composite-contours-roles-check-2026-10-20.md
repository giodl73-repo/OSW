---
skill: roles-check
topic: loop-composite-contours
date: 2026-10-20
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Composite contour-path review

Baseline ece1c14a0b3a7fce7a365164dc0034ccdab1e2b7. Internal functional lenses,
not independent scientific peer review. Artifact: measurement operator, pinned
full records, scientific sheet and shared Rust/WASM source-evidence integration.
Seven roles apply; no planetary analogy or release requiring ORBIT is present.

| Role | Finding | Severity | Evidence / disposition |
|---|---|---|---|
| CURRENT | Composite contour length is not mean daily current length. | P2 | Metric names conditional ADT arc; whole-current length, rank, reference-route, width, annual range and footprint admission remain false/null. |
| CURRENT | Gate placement is still an editorial convention. | P2 | Nominal older OSW gates plus independent one-grid shifts are declared before extraction; no physical origin/termination or instrument-section claim. |
| CURRENT | Ring closure must not complete the route. | P3 | Every closed/disconnected part remains rejected;18closed components are retained separately and no eddy identity is invented. |
| SOUNDER | ADT datum and velocity statistics must stay distinct. | P3 | Absolute ADT fields use source0.55m guide; anomalies, demeaned0.17m and maximum-velocity algorithms are not substituted. Mean C remains separate from hypot(mean U,mean V). |
| SOUNDER | Missing support could bias a path mean. | P3 | All four corners required even at zero weight; every midpoint, missing value and rejection remains retained, never a wet-only mean. |
| SOUNDER | Source composites do not supply member uncertainty. | P2 | Layer and conditional phase declared; no independent sample counts, timestamps, seasons, effective resolution or confidence interval inferred. |
| CHART | Legend originally overlapped panel titles. | P2 | Rendered inspection caught overlap; layout/legend placement amended and rendered again. |
| CHART | Similar adjacent curves need redundant encoding. | P3 | Central path black/white outline; alternative shifts white; rejected components dashed; gates separate. Table reports every case. |
| CHART | Missing speed cells could appear to be land. | P3 | Gray explicitly denotes missing source values, not coastline. Coarse land test is a separate recorded check with limited resolution. |
| BEACON | New numbers could be mistaken for the requested canonical current lengths. | P2 | All public values say composite contour paths and unranked; text explains the remaining whole-current measurement gap. |
| BEACON | Spread between phases could be mistaken for annual variability. | P2 | Two conditional source configurations are not seasons; min/max fields are experiment sensitivity only, not all observed extrema. |
| BEACON | Readback decimals imply unsupported accuracy. | P3 | Public table rounds to100km;0.1km values are calculation readback only. |
| HARBOR | A dense scientific plate needs a textual equivalent. | P3 | SVG semantic title/description, nominal facts, full54-row table, source links and explicit full-size figure link retained. |
| HARBOR | Color alone cannot show support. | P3 | Dashed rejected components, line outlines, outcome words and source tables supply non-color encodings. |
| HARBOR | Added figure/table require actual phone/keyboard verification. | P3 | Publication condition: all3shipped views at320px, keyboard details and loaded additional SVG, with complete source parity. |
| KEEL | More than one supported component must not become an arbitrary selection. | P3 | Synthetic two-path case remains ambiguous and supported length null; no shortest/desired-length choice. |
| KEEL | Geometry and velocity samples must measure the same retained path. | P3 | Independent WGS84 line_length and summed piece-length checks cover every54case; source-cell corners and tangent support retained. |
| KEEL | Full-suite predecessor is still running in an isolated checkout. | P3 | Leave live ece1c14 job/CLI untouched. Latest contour full gate remains pending; prior passes do not certify this batch. |
| LOGBOOK | Delivery must remain on the continuing draft. | P3 | Same branch/PR83; no main merge, no per-gap PR. |
| LOGBOOK | New source report must not silently alter older catalog content. | P3 | Publication condition:48other diagnostics,239other owners,5other scenes, original Loop source bytes, existing dimensions/routes/series and all dates unchanged. |
| LOGBOOK | Local success and remote provider failures are different states. | P3 | Record focused/browser/pins and exact full-suite state separately from remote CI; no remote-green claim without evidence. |

## Synthesis

Roles reviewed:7. Open P1:0. Open P2:0. P3 notes:15. Six P2 findings corrected.
Verdict: **APPROVED-WITH-CONDITIONS** for draft delivery only.
Top finding: retain the measured object as a conditional composite contour arc.
CURRENT, SOUNDER and BEACON agree that two numbers and an envelope cannot
establish whole-current or annual measurements. CHART/HARBOR require those
limits beside every visual and value.

## Amendments and conditions

1. Preserve strict object/datum/member/gateway scope and all54cases, including
   any future unresolved case; never add rejected ring lengths.
2. Before commit, pass source/geometry tests, exact preservation, staged pins
   and actual shipped-browser matrix including complete native/WASM case data.
3. Keep PR83 draft. Retain the live full gate and start a latest successor only
   after it is terminal; physical endpoint and independent scientific review
   remain separate from this internal approval.
