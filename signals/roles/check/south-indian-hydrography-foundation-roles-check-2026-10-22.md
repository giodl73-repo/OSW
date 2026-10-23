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

## Addendum: Sparrow primary-source classification review

Seven role lenses applied to the additional 15-page review and its impact on
the source investigation. This does not change any frozen scientific protocol.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | Some front criteria require 100/200 m properties. | P1 resolved for present claims | State that the current two-depth source cannot test those criteria; no front classification admitted. |
| CURRENT | In-situ and potential temperature are not interchangeable. | P1 resolved | No substitution/conversion performed; future conversion needs declared support and method. |
| CURRENT | A stronger neighboring jet may belong to ACC rather than SIOC. | P1 resolved | Source review supports the existing no-association gate; strongest peak is not a classifier. |
| SOUNDER | Repository and printed article titles differ. | P2 resolved | Verify original title page, authors, DOI and page range; retain both titles in provenance. |
| SOUNDER | Historical atlas and model averages differ from 2013 sampling. | P1 resolved | Record support mismatch; do not call the new HYCOM section a reproduction of HASO/FRAM. |
| SOUNDER | Original rights do not imply redistribution permission. | P1 resolved | Retain only acquisition metadata and our review publicly; raw PDF/renders remain ignored. |
| CHART | Schematic fronts do not supply current-width geometry. | P1 resolved | No figure digitization, drawn axis, polygon or width produced. |
| CHART | Property brackets cannot become velocity edges. | P1 resolved | Explicit false property-bracket/width equivalence in assessment. |
| CHART | The same latitude need not carry the same named front in both products. | P2 resolved | Preserve source disagreement; no fixed identity assigned by latitude. |
| BEACON | A new source could be advertised as filling a width gap. | P1 resolved | No compatible SIOC width admitted; plan explains classification support only. |
| BEACON | Front names could become automatic current aliases. | P1 resolved | Explicitly reject automatic aliases and preserve naming ambiguity. |
| BEACON | Additional source access is not a fix for the blocked paper fixture. | P2 resolved | Stramma fixture remains a separate unresolved CI bootstrap condition. |
| HARBOR | The new limitation must be visible near the profiles. | P2 resolved in code | Plain text paragraph plus descriptive review link before controls. |
| HARBOR | Meaning must not depend on colors or hover. | P2 resolved | Source limitation is textual; no new color encoding or hover dependency introduced. |
| HARBOR | New link and page reflow need actual-data browser execution. | P2 open | Existing source-profile gate will check every local link and 320 px layout after acquisition. |
| KEEL | Scanned pages yielded no extractable text. | P2 resolved | All fifteen rendered pages visually reviewed; no nonexistent OCR support claimed. |
| KEEL | New findings could tempt a post-acquisition protocol change. | P1 resolved | Source/diagnostic protocols and their pinned operators unchanged; later support extension requires separate declaration. |
| KEEL | Local paper reading does not establish overall CI success. | P2 open | Preserve current fixture failure and pending source/native/browser gates. |
| LOGBOOK | The additional original must not leak through staging. | P1 resolved | Git ignore checks confirm PDF and private renders excluded; stage exact metadata/review paths only. |
| LOGBOOK | Source review is an incremental record, not rewritten history. | P2 resolved | New acquisition/review files; previous Stramma access records unchanged. |
| LOGBOOK | PR workflow must stay continuous. | P1 resolved | Same branch/draft PR83; no new PR or main merge. |

Review addendum: 21 findings, no unresolved P1 for publishing this bounded
source review. Actual source reconstruction, browser/native readback and CI
bootstrap conditions remain open; no physical measurement is approved.

## Addendum: unchanged-source transport resume

Review covers the explicit operational declaration, longer-timeout helper and
packager retention, while the declared retry is running. No completion verdict
is issued for the still-pending new source products.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | A transport failure must not remove a sampled date. | P1 resolved | Exact original request set retained; no source dimension or averaging change. |
| CURRENT | Operational success does not prove current identity. | P1 resolved | Association/width admission remain false throughout the declaration and products. |
| CURRENT | Existing vertical-support limitations remain. | P2 resolved in scope | No change to the 15/1000 m interpretation or earlier front-definition review. |
| SOUNDER | Successful originals must not be replaced by later responses. | P1 resolved in helper | Freeze all77 raw/receipt hashes; retain existing pairs and verify preservation again afterward. |
| SOUNDER | A longer wait needs visible acquisition provenance. | P2 resolved in code | New successes record declaration hash, timeout, UTC, final URL and headers. |
| SOUNDER | Operational dependencies must travel with originals. | P1 resolved in packager | Retain declaration in the archive and pin helper/protocol/declaration in manifest. Actual package gate pending. |
| CHART | No fresh source map or footprint is justified by a successful download. | P1 resolved | No geometry produced by the retry; current view remains source context. |
| CHART | Timeout handling must not create absent-mean zeros. | P1 resolved | No mean product generated until complete; original mask/arithmetic code unchanged. |
| CHART | New visual outcomes still require actual source rendering. | P2 open | Existing 72-selection view gate remains required. |
| BEACON | A successful second pass could be overstated as complete. | P2 resolved | Plan states 77/82 with five pending, not complete. |
| BEACON | Transport changes could be confused with measurement-rule tuning. | P1 resolved | State socket timeout only; scientific selection and gates remain fixed. |
| BEACON | Passing scientific jobs do not make the full workflow green. | P2 resolved | Explicit offline-bootstrap HTTP403 and skipped tests/browser checks remain visible. |
| HARBOR | Incomplete products must not be linked as finished results. | P1 resolved | No new live card/query integration until reconstruction and browser checks. |
| HARBOR | Failure status must have a textual record. | P2 resolved | Retained JSONL failures and declared exact pending filenames. |
| HARBOR | Actual query/table accessibility remains unverified for the new source. | P2 open | Keep full-source browser gate pending. |
| KEEL | Restarting an unobserved process could duplicate downloads. | P1 resolved | Both earlier sessions collected terminal, PIDs absent, then new resume started. |
| KEEL | Retry must retain parser, coordinates and response-size bounds. | P1 resolved in code | Reuse unchanged validators/LIMIT, exact frozen URLs, two workers; no successful-response overwrite. |
| KEEL | New helper/storage provenance has not yet passed complete-source replay. | P2 open | Run full archive reconstruction after all82 requests, retaining exact product byte checks. |
| LOGBOOK | Declaration must precede the operational change. | P1 resolved | Record UTC, old selection, existing originals and new helper/protocol hashes before longer-timeout requests. |
| LOGBOOK | Copyright-paper and provider-original boundaries remain distinct. | P1 resolved | Model originals remain under NAVO distribution statement; paper PDFs/renders stay ignored. |
| LOGBOOK | Existing PR continuity remains required. | P1 resolved | Same draft PR83, no new PR or main merge. |

Transport addendum: 21 findings, no unresolved P1 for publishing this declared
operational step. Actual successful completion, source replay and integration
remain P2 conditions. Previous numeric/byte gates are retained in full.

## Addendum: same-cohort single-date transport

Seven role lenses applied to the declaration, genuine-response acquisition,
compiler, packager dispatch and focused tests. Source recovery is still running.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | Omitting the inaccessible dates would change the intended sample. | P1 resolved in method | Six native time indices expand mechanically; complete363-date cohort/order required. |
| CURRENT | Transport partitioning must not alter valid-time pairing or means. | P1 resolved in code/tests | Reuse original four-field mask, Int64 sums, scale/offset, calendar thresholds and Float64 means; partition arithmetic bytes tested. |
| CURRENT | Recovering source cells cannot identify the current or its edges. | P1 resolved | Association/width/axis/length/footprint admission remain false. |
| SOUNDER | A fabricated six-date text response would destroy provenance. | P1 resolved | Retain six genuine provider originals separately; no synthetic provider response written. |
| SOUNDER | Existing81 raw/receipt pairs must survive unchanged. | P1 resolved in declaration | Freeze every pair and check before/after acquisition and during reconstruction. |
| SOUNDER | Physical-response counts differ from logical-request counts. | P2 resolved | Report87 physical originals covering82 logical groups; old unavailable URL remains a documented failure. |
| CHART | An incomplete source must not look like an annual footprint. | P1 resolved | No current outline or annual extrema generated by this step; monthly products require full cohort. |
| CHART | Partitioning must preserve every coordinate node. | P1 resolved | Unchanged exact four-field/depth/latitude/longitude validator reused; URL invariance test passes. |
| CHART | Eventual profiles still require actual rendering. | P2 open | Existing 72-selection view gate and visual inspection remain required. |
| BEACON | A revised acquisition path could be mistaken for a new scientific selection. | P2 resolved | Explain unchanged cohort, extra physical responses and original failed URL explicitly. |
| BEACON | A partial April mean could be overstated as full-year completion. | P1 resolved | Compiler requires exact complete monthly timestamp vectors before products. |
| BEACON | Passing synthetic tests is not actual-source success. | P2 resolved | Plan labels acquisition/reconstruction/browser/integration pending despite44 focused tests. |
| HARBOR | Source exceptions need a textual, navigable explanation. | P2 resolved in records | Declaration retains exact old/new URLs, fields and source support, with batch-plan commands. |
| HARBOR | Data alternatives must retain missing values rather than color-only signals. | P1 resolved | Same nullable fields/counts and native query schema; no masks filled. |
| HARBOR | Query/card accessibility remains a later gate. | P2 open | Actual native/WASM and320px checks remain pending. |
| KEEL | A subset or duplicate time index could silently bias means. | P1 resolved in tests | Effective-request union/order must equal original exactly; missing/duplicate/reordered/changed-time requests rejected. |
| KEEL | Field/depth changes could hide inside new URLs. | P1 resolved in tests | Compare full mechanically generated subrequests; altered variable/depth/parent rejected. |
| KEEL | Compiler/storage dispatch must reproduce from genuine originals. | P2 open | Separate pinned compiler and archive declaration implemented; exact full-source offline gate retained and pending. |
| LOGBOOK | Operational history must not be overwritten. | P1 resolved | Keep original selection, both declarations, previous helper and all failure records. |
| LOGBOOK | The new declaration must precede new requests. | P1 resolved | UTC and all81 raw/receipt/operator/protocol pins written before single-date acquisition starts. |
| LOGBOOK | One continuing PR and original-data boundary remain required. | P1 resolved | Same PR83; only permitted model originals, metadata/reviews and code; paper PDFs/renders ignored. |

Subdivision addendum: 21 findings, no unresolved P1 for this full-cohort recovery
method. Actual completion, exact source replay, presentation and query integration
remain P2 conditions. No measurement or whole-project approval is implied.

## Results/source-view verification addendum

The complete cohort has now been recovered and reconstructed; source/context
publication remains separate from named-current measurement admission.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | Thousands of unsmoothed local extrema are not thousands of identified currents/fronts. | P1 resolved in reporting | Retain all1,230 eastward and3,894 salinity-gradient events as unassigned diagnostics; no identity/width admission. |
| CURRENT | All monthly means must retain layer/time support. | P1 resolved | Exact15/1000m, daily00Z2013 and original363-timestamp cohort retained; no climatology/layer mean claimed. |
| CURRENT | Full source coverage does not resolve 100/200m front criteria or along-current axis support. | P2 retained | Source limitations remain beside profiles; physical measurement assessment still pending. |
| SOUNDER | Operational recovery must preserve old originals and complete sampling. | P1 resolved | All81 old raw/receipt hashes match;87 genuine responses cover all82 logical groups/363 timestamps. |
| SOUNDER | Full products need exact original-based replay. | P1 resolved locally |183 archive members verified; all3 product byte hashes reconstructed offline with0 network requests. |
| SOUNDER | Native-cell query values must retain unrounded source means. | P1 resolved in adapter readback | Actual JSON/NPZ equality and23,472 rows pass; native/WASM bundle integration still pending. |
| CHART | Profiles need stable scales and clear sign/units. | P2 resolved | Final Chrome gate checks all72 selections; fixed depth-specific scales and textual sign/units retained. |
| CHART | Phone axis text was too small in actual render. | P2 resolved | Enlarged labels and left axis margin; repeated gate checks minimum10 CSS-pixel axis text. |
| CHART | Source geography must not become an occupied current footprint. | P1 resolved | Section profiles only; no source-derived current polygon, axis or state join generated. |
| BEACON | Availability could be mistaken for a filled measurement gap. | P1 resolved | Milestone explicitly separates source/view completion from width/axis/length/identity admission and atlas integration. |
| BEACON | The failed six-date request must remain visible in provenance. | P2 resolved | Both declarations and full failure history archived;87 physical responses reported honestly. |
| BEACON | One model year must not become annual extrema or seasonal climatology. | P1 resolved | Prominent2013/sample-year limitations preserved. |
| HARBOR | Every selection needs an equivalent data table. | P2 resolved | Actual Chrome validates23,472 table rows and full-precision download alternative. |
| HARBOR | Keyboard/link/share state must survive rendering. | P2 resolved | Native selects, visible focus, history/reload/invalid-route tests and local links pass. |
| HARBOR | Phone usability must extend beyond page reflow. | P2 resolved |320px render inspected; axis sizing corrected and tested; contained focusable table scroll remains. |
| KEEL | A passing mock cannot establish actual source arithmetic. | P1 resolved locally | Actual raw-original reconstruction and actual NPZ/JSON/table correspondence pass, beyond44 focused tests. |
| KEEL | Cross-platform/source and main native/WASM gates remain outstanding. | P2 open | Fresh Linux replay and exact complete native/WASM collection readback required after integration. |
| KEEL | Full offline suite remains unproven. | P2 open | Stramma fixture HTTP403 and local full-suite disk guard remain visible; no overall green claim. |
| LOGBOOK | Source artifacts must be publishable without copyrighted papers. | P1 resolved | NAVO metadata/distribution statement retained; only model archive and our artifacts staged; PDF/renders ignored. |
| LOGBOOK | Source-view milestone must not overwrite earlier status history. | P2 resolved | Append dated/ordered milestone with exact hashes and remaining work. |
| LOGBOOK | Existing branch/PR and all old measurements must remain intact. | P1 resolved in scope | Same PR83; no new widths, lengths, geometries or canonical identities added. |

Results addendum: 21 findings, no unresolved P1 for complete source/context
publication. Native/WASM/index/card integration, fresh Linux replay and broader
project gates remain P2 conditions. No physical measurement approval implied.

## Addendum: canonical v2 meridian arithmetic

Review addresses a real Linux exact-byte failure, not a hypothetical precision
issue. The original33 report gates and source arithmetic remain unchanged.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | Reproducible arithmetic must preserve the WGS84 metric. | P1 resolved in method/tests | Same ellipsoid and meridian-curvature integral; independent quadrature/PROJ comparisons pass. |
| CURRENT | Numerical nanometre-scale differences are not physical uncertainty. | P1 resolved | Protocol separates computational validation from model/measurement uncertainty. |
| CURRENT | The correction must not promote current identity or dimensions. | P1 resolved | All cases retain false association/width/axis/length/annual-extrema admission. |
| SOUNDER | Replacing v1 in place would erase provenance. | P1 resolved | Keep v1 code/preflight/report byte unchanged; versioned operator/protocol/preflight/report supersedes it explicitly. |
| SOUNDER | Canonical arithmetic must pin constants and evaluation order. | P1 resolved |70-digit Decimal context, fixed π,16 eccentricity-series order,70 trig terms and exact binary64 input conversion. |
| SOUNDER | Source arrays and common-time support must remain exact. | P1 resolved | No source producer or source product changed; original manifests retained. |
| CHART | Plotted source values must not change with the gradient-distance fix. | P1 resolved | Raw monthly profile values unchanged; only unassigned derived distance/gradient numbers revised. |
| CHART | Event support could shift under tiny changes. | P2 resolved locally | All72 case counts, native supports, flank states and nearest-gradient IDs compared equal. |
| CHART | Updated diagnostic links need actual browser readback. | P2 open | Native/WASM/card/index integration gate remains required. |
| BEACON | A green older job cannot stand in for new-product Linux success. | P1 resolved | Record actual failure and skipped new-source replay; no overall green claim. |
| BEACON | A numerical implementation revision must be distinguished from a new dataset. | P2 resolved | Same source/cohort; versioned canonical diagnostic only. |
| BEACON | Canonical status must not hide the superseded result. | P2 resolved | v2 metadata links the old report/checksum and failing run. |
| HARBOR | Revised metadata must remain accessible through source queries. | P2 conditional | Both historical and canonical documents retained in the index registry. |
| HARBOR | Full source tables remain the visual alternative. | P1 resolved in scope |23,472 unrounded cells unchanged; no masking/rounding introduced. |
| HARBOR | New canonical navigation needs keyboard/phone verification. | P2 open | Actual integrated browser gate pending. |
| KEEL | Loosening replay tolerance would conceal the failure. | P1 resolved | Exact encoded byte gate retained for the v2 target; no rounding or approximate replay. |
| KEEL | Correctness needs an independent geometric check. | P1 resolved locally | Gauss-Legendre curvature integration, PROJ and symmetry/additivity/domain tests pass; combined67 focused tests. |
| KEEL | Cross-platform equivalence is still unproven until CI runs. | P2 open | Fresh Linux34-target replay and source reconstruction required after publication. |
| LOGBOOK | Frozen older source artifacts must remain inspectable. | P1 resolved | v1 operator/preflight/report and all33 earlier reports/producers unchanged. |
| LOGBOOK | Public status must record the actual platform failure. | P2 resolved | Batch plan includes run/job context, numeric magnitude, correction and remaining gates. |
| LOGBOOK | Continue existing PR without main merge. | P1 resolved | Same branch/draft PR83. |

Numerical addendum: 21 findings, no unresolved P1 for publishing the versioned
correction. Fresh exact Linux replay and integrated UI/native/WASM verification
remain P2 conditions; no new physical-measurement approval is implied.


## Addendum: source collection, atlas navigation and query equality

Internal review of the integrated source/context artifact through the same seven
installed roles. ORBIT is inapplicable: no space or planetary comparison is made.
This review does not independently establish current boundaries or dimensions.

| Role | Finding | Severity | Resolution / required action |
|---|---|---|---|
| CURRENT | Available model cells must not become identified current occupancy. | P1 resolved | Every source row retains false association/width flags; card labels this as paired source context. |
| CURRENT | Depth, year and thermal variable require explicit support. | P1 resolved | Exact15/1000m,2013 common-day monthly samples and in-situ temperature retained in rows, units and profile text. |
| CURRENT | Current width and annual extrema remain physically unresolved. | P2 retained limit | No new width/length/axis/footprint or annual range admitted; source only samples three nearby meridians. |
| SOUNDER | Query flattening could alter means, masks or counts. | P1 resolved in adapter/source gates | All23,472 rows retain native coordinates, unrounded values, counts and explicit eligibility;67 focused tests pass. |
| SOUNDER | Canonical and superseded diagnostics must stay distinguishable. | P1 resolved | Both v1 and v2 documents indexed; current links select v2; protected v1 artifacts remain byte exact. |
| SOUNDER | Provenance must follow the source row into the query UI. | P2 resolved | Source ID resolves to the model record with acquisition and full source paths, fields, units, sampling and rights. |
| CHART | Repeated selections need consistent plotting scales and sign. | P2 resolved | Final actual browser checks72 selections/288 profiles, fixed scales, zero line, missing breaks and units. |
| CHART | Source section geography cannot imply a mapped current boundary. | P1 resolved | Profile explicitly identifies a section; no new geographic flow outline or physical state intersection. |
| CHART | Phone text needs measured readability. | P2 resolved | Final320px profile gate checks minimum10 CSS-pixel axis text and reflow; table is an equivalent textual view. |
| BEACON | Source completion could be mistaken for measurement completion. | P1 resolved | Plan and nearby profile notices keep named-current dimensions unresolved. |
| BEACON | Evidence navigation should start from the current card. | P2 conditional | Four direct profile/query links added; integrated keyboard card/profile/query gate required. |
| BEACON | Partial CI success must not become an overall green claim. | P1 resolved |34 exact Linux reports and both source replays pass at3dc355c; separate offline fixture403 and skipped later steps recorded. |
| HARBOR | Chart access must include the complete values and controls. | P1 resolved | Native selects, full326-row section table, source JSON and structured query alternative retained. |
| HARBOR | Selection/share/history should remain keyboard operable. | P2 resolved for profile | Final72-selection browser gate passes keyboard, reload/history, invalid-input explanation and phone reflow. |
| HARBOR | Cross-page selection must survive without pointer input. | P2 conditional | Integrated320px card-to-profile-to-exact-section query gate required; no automatic originals permitted. |
| KEEL | Numeric equality incorrectly distinguished15 from15.0. | P1 resolved in regression/build | Scalar eq/ne compare exact equal integral values;133 Rust tests include query regression, type separation and large signed/unsigned boundaries. |
| KEEL | Full source values must agree through actual native and WASM engines. | P2 conditional | Paginated48-query complete-cell readback plus full72-case/12-month source checks running; no sampled success substituted. |
| KEEL | Versioned arithmetic needs exact cross-platform evidence. | P1 resolved | Fresh Linux job120157339543 passes all34 encoded reports and both zero-network HYCOM source reconstructions. |
| LOGBOOK | Existing measurements and source history must survive integration. | P1 resolved |59,865 old rows checked, only South Indian object metadata/links changed;69 protected files and458 old source descriptors exact;170 widths/78 routes retained. |
| LOGBOOK | Build recovery must not damage originals or weaken gates. | P1 resolved | Source originals preserved; only verified superseded generated parts/derived compiler artifacts retired;512MiB engine guard and all133 Rust tests retained. |
| LOGBOOK | Publication must follow the agreed continuing batch. | P1 resolved in scope | Same open draft PR83, no new PR or main merge; integration assets remain pending final browser evidence and commit. |

Integration addendum:21 findings. No unresolved P1 in the implementation reviewed.
The three conditional integration areas remain required before this milestone is
reported complete. Broader offline/full-suite conditions and physical measurement
limits remain visible; this is an internal source/context review.
