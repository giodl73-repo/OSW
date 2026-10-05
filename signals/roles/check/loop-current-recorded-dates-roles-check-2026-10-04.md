---
skill: roles-check
topic: loop-current-recorded-dates
date: 2026-10-04
source_commit: 05fdf5c457e47f4f3c0b5402e9cfd05ce6468696
working_branch: codex/loop-current-recorded-dates
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Recorded-date Loop Current review

Internal functional review of explicit acquisition, repeated scientific diagnostics,
Rust records/frames, date navigation and the recorded-day map. CURRENT checks physical
meaning, SOUNDER source identity, CHART maps, BEACON explanation, HARBOR equivalent
access, KEEL reproducibility and LOGBOOK repository state. ORBIT is excluded because
there is no planetary comparison. This is not independent scientific peer review.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | Four days cannot define seasons or annual extrema. | P3, verified | Date selection declared before tracing; no phases, annual ranges, pooled ranked lengths or widths admitted. |
| 2 | CURRENT | Stopped nominal traces must remain failures. | P2, resolved | January, July and October NOAA lengths/differences null; no connected query geometry frames; failed traces retained on the experiment map and in full diagnostics. |
| 3 | CURRENT | A successful alternate method does not fix seed sensitivity. | P3, verified | Separate NOAA/ADT records and failed scenario counts remain visible. Shared altimetry inputs disclosed. |
| 4 | SOUNDER | Additional dates need original field and mask readback. | P3, verified | Every value and missing cell in all eight regional snapshots matched original NetCDF; response SHA and receipt SHA retained. |
| 5 | SOUNDER | Rules must remain identical across dates. | P3, verified | Same seed criterion, gateway limits, step/threshold scenarios, ADT levels and strict missing-cell rules; source-bound reconstruction passed. |
| 6 | SOUNDER | Daily labels are not identical averaging support. | P3, verified | NOAA bounds retained; DUACS lack of time_bnds remains explicit. Same labelled date only. |
| 7 | CHART | Narrow map crop could hide a failed path. | P2, resolved | January reaches 91.62 W; map widened to 93 W and inspected with all retained path coordinates. |
| 8 | CHART | Method identity must survive color loss. | P3, verified | Solid connected NOAA, short-dashed gray failed NOAA and long-dashed cyan ADT; legend, titles and outcome table. |
| 9 | CHART | Playback must not invent intermediate geometry. | P3, verified | Only four stored paths; equal viewing intervals stated, without elapsed-time or particle-motion claim. |
| 10 | BEACON | Similar April numbers need precise meaning. | P3, verified | 19.5 km is method/product difference, not uncertainty; display lengths both rounded to 1600 km. |
| 11 | BEACON | Failure evidence must be near the controls. | P3, verified | Selected-day outcome reports unresolved NOAA values, stop reason and scenario failures; all dates in table. |
| 12 | BEACON | Direct links should preserve the selected date. | P2, resolved | Diagnostic link carries its observation_date; query links constrain the exact day; July card-to-map navigation tested. |
| 13 | HARBOR | Playback needs a manual alternative. | P3, verified | Native select, Previous/Next, keyboard activation, focus styles and semantic table; no automatic playback on load. |
| 14 | HARBOR | Reduced motion and page hiding must stop playback. | P3, verified | Reduced-motion preference disables play and retains manual controls; visibility/pagehide stops timer. |
| 15 | HARBOR | Date changes need accessible outcomes and narrow-screen reflow. | P3, verified | aria-live outcome and dated SVG title; 320 px page has no horizontal overflow, table scrolls locally. |
| 16 | KEEL | Paired methods must share a valid date. | P3, verified | Rust checks every date's NOAA/ADT pair, owner links, source JSON/receipts and same-date comparison path. |
| 17 | KEEL | Failed geometry cannot be promoted by import. | P3, verified | Four new loader rejection cases cover incomplete pair, invented failed frame, wrong date and changed source geometry; eight baseline cases still pass. |
| 18 | KEEL | New frames must preserve existing Gulf data. | P3, verified | 24 total frames: 17 Gulf and 7 Loop. Existing Gulf frame/playback test passed. |
| 19 | LOGBOOK | Local source snapshots have unresolved use conditions. | P3, open | New regional source-use flags retained; user authorized repository publication on 2026-10-04; scientific source-use review remains open. |
| 20 | LOGBOOK | Research progress cannot imply canonical admission. | P3, verified | 11 ranked lengths, 89 remaining names, 62 routes/59 names and 30 unbuilt unchanged; canonical v0.1.0 diff empty. |
| 21 | LOGBOOK | Scientific and full publication gates remain open. | P3, open | Original supplement, gateways, effective resolution, broader repeated regimes and full publication CI not represented as complete. |

## Synthesis

Seven roles, 21 findings; three P2 issues resolved, 18 P3 notes, no open P1/P2.
APPROVED-WITH-CONDITIONS for this local diagnostic/query slice. Top finding: method
failure on three of four repeat dates is substantive evidence against treating a
single successful NOAA trace as a robust current length. CURRENT, SOUNDER and BEACON
agree to retain failures and avoid annual-range language.

## Amendments

1. Retain failed NOAA records but forbid accepted geometry frames for them.
2. Widen the crop to include the January trace and show method identity by patterns.
3. Preserve observation_date in direct links, keep keyboard/manual controls and
   reduced-motion behavior, and use the protocol's 100 km rounding rule.

## Verification

36 focused Python tests and 29 subtests; 22 Rust tests; original field/mask readback
for eight new source receipts; native/WASM date queries; four new and eight baseline
loader rejection cases; exact-date card navigation, keyboard playback, reduced-motion
and 320 px reflow; existing Gulf frame/playback regression. Rendered map inspected.
Full publication CI and independent scientific admission were not claimed.
