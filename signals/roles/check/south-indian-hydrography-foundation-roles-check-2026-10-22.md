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

## Addendum: paired-profile diagnostic declaration

Reviewed before applying the diagnostic to the new source values. The same
seven relevant roles were applied to the new protocol/operator/tests and
preflight. The original foundation verdict remains conditional; this addendum
does not clear pending data, browser, integration or whole-project gates.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | A nearest salinity gradient does not prove SIOC identity. | P1 resolved | Every event and the report retain current-association and width-admission false. |
| CURRENT | A 1000 m gradient is not a near-surface front. | P1 resolved | Each case records its exact depth and near-surface boolean; both supports remain separate. |
| CURRENT | Monthly gradients can combine different valid-date sets across latitude. | P2 resolved in protocol | Explicitly state gradient-of-monthly-means, not mean daily gradient or synoptic front. |
| SOUNDER | Native latitude spacing varies. | P1 resolved | Divide differences by actual WGS84 geodesic separation; unequal-spacing test passes. |
| SOUNDER | Missing values could create a false continuous gradient. | P1 resolved | Adjacent differences retain missing values; no gap bridging or smoothing. |
| SOUNDER | Runtime and methods must be recoverable before interpreting results. | P2 resolved | Preflight pins operator, protocol, review, source selection, requirements and numeric library versions. |
| CHART | A two-node gradient bracket could be mistaken for an observed front point. | P1 resolved | Retain latitude bracket, not an interpolated or drawn point. |
| CHART | A plateau midpoint could invent a geographic core. | P2 resolved | Preserve the entire native peak support and both flank states. |
| CHART | Domain-edge or missing-neighbor peaks could look resolved. | P1 resolved | Explicit censored flank states; no physical edges or width derived. |
| BEACON | All positive local candidates differ from reproducing the paper's selected front. | P2 resolved | Protocol labels exploration, explains source motivation and admits no paper reproduction. |
| BEACON | Diagnostic proximity could become a misleading identity score. | P1 resolved | Distance labeled support association aid; every candidate is retained and identity remains unresolved. |
| BEACON | An implemented diagnostic is not a completed result. | P2 resolved | Batch plan says generation awaits complete source; no decreased gap counts claimed. |
| HARBOR | Diagnostic values need a machine-readable alternative. | P2 conditional | Full JSON report planned with stable case/candidate IDs; not yet generated. |
| HARBOR | Sign and censoring must remain textual. | P2 resolved in schema | Positive-gradient/velocity names, flank strings, exact units and admission booleans are explicit. |
| HARBOR | Eventual presentation must not rely on identifying peaks by color. | P2 open for integration | Native table/source links remain available; inspect any future diagnostic overlays before publication. |
| KEEL | Ties and missing neighbors must not depend on accidental array iteration. | P1 resolved | Whole plateaus retained; all nearest ties within 1e-9 km retained; targeted tie/censor tests pass. |
| KEEL | Cell-difference arithmetic must not silently assume a uniform grid. | P1 resolved | Separate spacing array and finite/increasing-coordinate guards; tests cover reversed, repeated, missing and short coordinates. |
| KEEL | No complete data-backed reproduction exists yet. | P2 open | Combined 22 unit tests pass; actual 72-case report and source-original reconstruction remain required. |
| LOGBOOK | New diagnosis must not alter historical operators or measurements. | P1 resolved | New files only, except batch documentation/attributes/review; previous scientific operators unchanged. |
| LOGBOOK | Source acquisition progress must not be presented as an admitted measurement. | P1 resolved | No width, axis, length or annual range added; foundation remains labeled incomplete. |
| LOGBOOK | Branch/PR scope must stay consistent. | P1 resolved | Existing branch and draft PR83; no new PR or main merge. |

Addendum: 21 findings, no unresolved P1 for publishing the frozen declaration;
P2 conditions remain for data-backed reproduction, presentation and integration.

Navigation/resource follow-up: CHART/HARBOR/LOGBOOK reviewed the month/depth/
native-meridian URL state, explicit invalid-selection fallback and browser
history coverage. No scientific field, classification or width is changed.
Actual data-backed browser execution remains pending. KEEL/SOUNDER reviewed
the lossless compression receipts: affected derived-file content hashes remain
identical, provider originals were not touched, and no files were removed.
Existing whole-project gates remain unresolved; disk recovery does not clear them.

## Addendum: native-cell query adapter preparation

Same seven role lenses; review covers the adapter and its synthetic full-grid
tests, not an actual published collection. It is not yet called by the atlas
builder. All original source, integration and whole-project conditions persist.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | A cell at 80 E is not an identified named-current sample. | P1 resolved | Use investigation_current_id and explicit false association/admission, not a current footprint. |
| CURRENT | Total model velocity must retain its reference and units. | P1 resolved | Source record explains total velocity; scalar field names retain m/s and native depth. |
| CURRENT | Exact levels must not imply a layer mean or climatology. | P1 resolved | Every row carries model year/month/depth and source record states the limits. |
| SOUNDER | Flattening could transpose latitude, depth or longitude. | P1 resolved in tests | Every synthetic row's native indices and coordinates are checked across all axes. |
| SOUNDER | Rounded JSON or null dropping could lose source evidence. | P1 resolved | Full numeric bits and negative zero retained; all 23,472 cells include ineligible null rows. |
| SOUNDER | Counts must match the four-field common support. | P1 resolved in adapter | Reject invalid counts, changed calendar threshold, wrong sample days and inconsistent nulls. |
| CHART | These points cannot be rendered as a current outline. | P1 resolved | No geometry/current boundary is produced by the adapter. |
| CHART | Source indices are provenance rather than physical distance. | P2 resolved | Indices and degree coordinates have distinct explicit names. |
| CHART | Eventual plot/query linking needs actual browser verification. | P2 open | Link and test only after source reconstruction and bundle integration. |
| BEACON | Source rows could inflate reported measurement coverage. | P1 resolved | Plan says current collection counts and physical measurement gaps remain unchanged. |
| BEACON | In-situ temperature must not become a density or heat field. | P1 resolved | Named in_situ_temperature_c; no derived density/heat field. |
| BEACON | Preparation must not be described as finished atlas integration. | P2 resolved | Plan and module explicitly state that builder wiring is pending. |
| HARBOR | A filterable value table supplies a data-oriented alternative. | P2 conditional | Planned native rows retain scalar values and missingness; actual UI readback pending. |
| HARBOR | Missing values and selection must remain textual. | P2 resolved in schema | Null means, eligibility flag, source fields and counts are separate; no color-only meaning. |
| HARBOR | Native query navigation requires keyboard and phone checks. | P2 open | Existing explicit browser gate remains required after integration. |
| KEEL | Numeric corruption must fail before query publication. | P1 resolved in adapter | Manifest/dependency pins and JSON/NPZ equality checked at retained-source entry point. Actual source execution pending. |
| KEEL | A few sample values would not prove full-axis preservation. | P1 resolved in tests | Every synthetic axis/value bit checked, plus source/schema/mask corruption cases; combined 34 tests pass. |
| KEEL | Native/WASM equivalence has not been established for new rows. | P2 open | Compare all actual rows after acquisition and bundle rebuild. |
| LOGBOOK | Source rights and model origin must travel with the collection. | P1 resolved in code | Source record retains provider URL, acquisition file, variables, units and NAVO distribution statement. |
| LOGBOOK | Pending integration must stay visible. | P2 resolved | Adapter is unused by the existing builder; source and browser conditions are explicit. |
| LOGBOOK | No per-gap PR or main merge is authorized. | P1 resolved | Continue existing branch and draft PR83. |

Adapter addendum: 21 findings, no unresolved P1 for publishing preparation;
actual retained-source execution, native/WASM row verification and UI integration
remain P2 conditions. No physical-width or whole-project approval is implied.
