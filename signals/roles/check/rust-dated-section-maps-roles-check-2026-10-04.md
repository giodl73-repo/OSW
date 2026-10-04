---
skill: roles-check
topic: rust-dated-section-maps
date: 2026-10-04
source_commit: 759246d4fcab441a77eb965fbcea80bc91f08968
working_branch: codex/dated-section-maps
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Dated local section map review

Internal functional review of Rust scene generation, portable SVG, browser
navigation, source scope and access. CURRENT checks physical support; SOUNDER
checks provenance; CHART checks geographic fidelity; BEACON checks explanation;
HARBOR checks equivalent access; KEEL checks reproducibility; LOGBOOK checks
delivery status. ORBIT is excluded because there is no planetary comparison.
This is not independent scientific peer review.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | A meridional component section is not a flow-normal current width. | P3, verified | Scene, card and SVG identify the nominal surface diagnostic at 70 W. Preserve the metric. |
| 2 | CURRENT | Section spans cannot become axes, buffers or occupied footprints. | P3, verified | Rust emits only the source-endpoint LineString; object geometry/state inventory unchanged. No state containment follows. |
| 3 | CURRENT | System identity cannot transfer to the separate Gulf Stream current. | P3, verified | Each mark retains current:gulf-stream-system as owner and the sample ID as inspection target. Keep identities separate. |
| 4 | SOUNDER | Source sample copies must control geographic endpoints. | P3, verified | Existing loader binds the original sample/longitude; tests check all 17 resulting endpoint pairs. Do not accept browser-supplied geometry. |
| 5 | SOUNDER | Dates and processing versions belong beside the geometry. | P3, verified | Scene/export retain observation day, RADS algorithm, subset checksum and sample pointer. Preserve exact receipts. |
| 6 | SOUNDER | Other sample methods lack compatible endpoint support here. | P3, verified | All-width query maps 17 and retains 88 unmapped; Leeuwin-only map remains null. Avoid invented locators. |
| 7 | CHART | Object-scale zoom obscures local sections. | P2, resolved | Sample fit/selection uses a 4-degree minimum; object minimum remains 20. Coordinate display bounds identify the offshore close-up. |
| 8 | CHART | Multiple dates coincide on a fixed meridian. | P3, verified | Separate marks, keyboard targets and table records retained; overlap disclosed, no spatial jitter. Filtering isolates dates. |
| 9 | CHART | Missing or reversed endpoints cannot form a plausible line. | P3, verified | Rust test covers null, reversed, out-of-range and unresolved values. Keep records without rendered geography. |
| 10 | BEACON | Map names should remain on hover/focus. | P3, verified | No persistent line labels; accessible names and selection announcements retained. Source scope is visible text. |
| 11 | BEACON | Mark selection previously assumed an object ID. | P2, resolved | Explicit width_samples inspection target opens the exact dated sample. Card link returns to a one-sample map query. |
| 12 | BEACON | Export could imply a current route. | P3, verified | SVG legend and description explicitly identify local nominal spans; receipt preserves metric/range fields. Export remains a global display. |
| 13 | HARBOR | Hidden selector was overridden by label display CSS. | P2, resolved | Added [hidden] display rule; test confirms day selector and playback controls are hidden for sample maps. Visual screenshot inspected. |
| 14 | HARBOR | Coincident marks still need access without a pointer. | P3, verified | Every mark focusable; Enter opens its card, and table provides all original records. Keep redundant access. |
| 15 | HARBOR | Local fit must retain small-screen reflow. | P3, verified | Updated dated-map check passes at 320 px; source captions and coordinate bounds remain text. Preserve normal zoom/pan. |
| 16 | KEEL | Scene inventory must precede table pagination. | P3, verified | One-row queries retain all 17 scene marks; mixed collection reports 105 records and 88 unmapped. Keep completeness counts. |
| 17 | KEEL | Native and WASM map/export behavior must agree. | P3, verified | Query parity and SVG byte identity pass for dated samples; export receipts match native features. Keep source metadata deterministic. |
| 18 | KEEL | New sample maps must preserve object map behavior. | P3, verified | Existing object query/spatial/integrity/mobile regression passes; all-width regression and SVG object tests pass. Controls restore when switching back. |
| 19 | LOGBOOK | Canonical scientific admission remains distinct. | P3, verified | No canonical release, diagnostic source or query-data edits in this slice. Scientific boundary/resolution validation remains pending. |
| 20 | LOGBOOK | Local checks must not be reported as remote CI. | P3, verified | 22 Rust tests and dated-map, width-query, SVG and object browser/native/WASM checks passed; full CI has not run for this new slice. Keep publication gate open. |
| 21 | LOGBOOK | Previous main merge does not publish subsequent work. | P3, verified | Slice remains local on codex/dated-section-maps, based on PR16 merge. No new publication claimed. |

Synthesis: seven roles, zero open P1/P2 issues, 18 P3 notes. Conditional approval
for local editorial presentation. CURRENT/CHART/SOUNDER agree that the visual
must remain a source-supported local section, not a current footprint.

Amendments: add local fit and coordinate bounds; bind mark navigation to the
exact sample and add reciprocal card links; hide incompatible playback controls
and fix CSS visibility. Evidence: 22 Rust tests, native/WASM dated-map and SVG
parity, source endpoint checks, width-query and object regressions, keyboard and
mobile tests, inspected screenshot. Full default CI and independent scientific
boundary/resolution admission remain open. No new lengths or annual ranges.
