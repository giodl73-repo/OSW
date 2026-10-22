---
skill: roles-check
topic: south-indian-hydrography-foundation
date: 2026-10-22
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# South Indian paired-source foundation: internal role review

Scope: declared acquisition, parser/averaging, retained-source packager,
profile-view code and full-paper review. Internal application of installed
role lenses; no independent external review or merge approval implied.
CURRENT/SOUNDER own physical interpretation and provenance; CHART/BEACON
the profile's meaning; HARBOR accessibility; KEEL reproducibility; LOGBOOK
the public status. ORBIT does not apply: no planetary analogy or extrapolation.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | The neighboring ACC can dominate an eastward maximum. | P1 resolved for foundation | No current association or width admitted; explicit notice in protocol and viewer. Separate association assessment required. |
| CURRENT | Two z levels are not a layer mean or historical geostrophic reference. | P1 resolved for foundation | Retain exact provider depths, total-velocity class and in-situ temperature convention. |
| CURRENT | Front station brackets and schematic transport paths do not define current edges. | P1 resolved | Full ten-page review records page-specific rejection; no digitized geometry or width promoted. |
| SOUNDER | Different variable masks could mix dates between hydrography and velocity. | P1 resolved | Four-field common valid mask, calendar-day threshold and Int64 sums; targeted missing-salinity test. |
| SOUNDER | Reused global metadata must not acquire a fictitious new timestamp. | P2 resolved in code | Packager copies original metadata/coordinate receipts from the pinned previous archive. Await actual packaging check. |
| SOUNDER | Complete source retention has not yet finished. | P2 open | Finish every frozen request, retain errors, check original archive and exact product reconstruction. |
| CHART | A section plot could be mistaken for a current-boundary map. | P1 resolved in design | Explicit section/profile wording; no footprint polygon or named-current edge. |
| CHART | Per-month autoscaling could conceal temporal changes. | P2 resolved in code | Fixed field/depth range across all months and meridians; symmetric velocity scales and dotted zero. Verify in browser. |
| CHART | Missing means must not be connected as continuous flow. | P2 resolved in code | SVG paths break at nulls; native table says Missing. Browser/source checks pending. |
| BEACON | A single model year is not a seasonal climatology. | P1 resolved in copy | Year and sample convention beside controls; explicit climatology limitation. |
| BEACON | Warm water is not heat content or transport. | P2 resolved | Temperature remains in-situ temperature with units; no inferred heat budget. |
| BEACON | A completed paper review is different from a newly admitted measurement. | P2 resolved | Review and batch plan state no defensible reported width found and retain earlier records. |
| HARBOR | Color alone must not carry sign or values. | P2 resolved in code | Axis labels, sign explanation, zero line, native table and full-precision JSON. |
| HARBOR | Changing profiles should remain keyboard accessible. | P2 conditional | Native labeled selects, visible focus and polite status updates implemented; actual keyboard/browser gate pending. |
| HARBOR | Wide tables must not break phone reflow. | P2 conditional | Contained focusable horizontal scroll, responsive plots; 320 px browser check pending. |
| KEEL | Packed field identity and depth maps must be checked together. | P1 resolved | Strict Int16/row order/field identity/coordinate checks; eleven focused tests pass and pilot actual response validates. |
| KEEL | Platform-dependent compression must not change derived NPZ bytes. | P1 resolved in design | Existing unchanged sorted ZIP_STORED/NPY1.0 writer reused. Exact whole-product offline gate retained. |
| KEEL | Neither full-source reconstruction nor whole-project gates have passed for this batch. | P2 open | Run source reconstruction and view gate once acquisition completes; do not claim overall green. Existing CI bootstrap HTTP 403 and local disk constraint remain visible. |
| LOGBOOK | One continuing PR is required. | P1 resolved | Same branch and draft PR83, no new PR and no main merge. |
| LOGBOOK | Original article redistribution permission is not established. | P1 resolved | Only our paraphrased review is published; original PDF and review renders remain private/ignored. |
| LOGBOOK | Pending source/view work must remain distinguishable from verified results. | P2 resolved for foundation | Batch plan labels acquisition in progress and packaging/browser/index integration pending; no gap-count reduction claimed. |

## Synthesis

Seven roles, 21 findings. No unresolved P1 for committing a clearly labeled
foundation. P2 conditions remain: full source retention/reconstruction, actual
view checks, query/index integration and broader project gates. Verdict is
APPROVED-WITH-CONDITIONS for the foundation only, not a finished measurement.

Top finding: stronger eastward flow does not establish South Indian Current
identity. CURRENT/CHART/BEACON agree the view must preserve that distinction.

## Amendments

1. Retain paired hydrography and both velocity components at exact depth/time
   support before feature-association work; reject width admission at this stage.
2. Preserve old acquisition receipts and portable array serialization; reconstruct
   all products from the pinned original archive without a network request.
3. Keep year, layer and unresolved identity beside the plots, with fixed scales,
   missing-data breaks, native table, keyboard controls and a narrow-screen gate.
