---
skill: roles-check
topic: south-indian-front-level-source
date: 2026-10-22
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Supplementary source and conditional temperature-conversion review

Internal review through the seven relevant installed role lenses: CURRENT for
physical support, SOUNDER for custody, CHART for source-versus-boundary meaning,
BEACON for interpretation, HARBOR for later equivalent access, KEEL for exact
reproduction, LOGBOOK for the continuing batch. ORBIT is inapplicable. This is
not an independent scientific review or approval of a measured current width.

| Role | Finding | Severity | Resolution / condition |
|---|---|---|---|
| CURRENT |100m/200m criteria cannot be inferred from15m/1000m. | P1 resolved in selection | Exact native indices19/22 supplement the original source without changing it. |
| CURRENT | Pressure and temperature reference are not directly observed by this source. | P1 resolved in method/scope | Use negative depth, explicit zero dynamic height/geopotential, and recorded ITS-90 assumption; no historical scale equivalence claimed. |
| CURRENT | Property brackets do not identify velocity edges or SAF salinity-minimum descent. | P2 retained limit | No named front/current, width, length, axis or footprint admitted; later classification requires its own method. |
| SOUNDER | New source values require an earlier immutable declaration. | P1 resolved | Selection/preflight and operator/protocol/dependency pins precede field acquisition; existing values prevent declaration. |
| SOUNDER | Additional layers could silently alter dates or packing. | P1 resolved in tests | Same363 timestamps, earlier grid, masks, Float32 packing and calendar quota enforced; wrong support rejected. |
| SOUNDER | GSW can silently clamp invalid negative salinity. | P1 resolved in tests | Reject negative common-valid SP before conversion; retain missing cells and record units/assumptions. |
| CHART | A new profile could be mistaken for current occupancy. | P1 resolved in scope | No current outline or occupied-state geometry generated. |
| CHART | Raw and derived temperature need distinct labels/units. | P2 condition for presentation | Raw remains in-situ; derived key explicitly names0dbar and the ITS-90 assumption. Actual later visual checks required. |
| CHART | Existing profiles must not silently change source or depths. | P1 resolved | Separate selection, operator, schemas and directory; old15m/1000m view unchanged. |
| BEACON | Filling vertical support could look like filling a physical width. | P1 resolved | Protocol and batch retain all physical-admission gates closed. |
| BEACON | An old climatology is not reproduced by a2013 model year. | P1 resolved | Explicit model-year comparison and historical/reference limitations. |
| BEACON | Declaration/tests alone cannot prove acquisition success. | P2 condition | Batch separates fourteen passing focused tests from pending actual source/derived/UI results. |
| HARBOR | Added depth/derived choices need equivalent text and tables. | P2 condition for presentation | Require updated native-depth controls, units and complete values before claiming visual delivery. |
| HARBOR | Failure and missingness must stay visible beyond color. | P1 resolved in contract | Nullable means, common-day counts, eligibility and explicit failure status retained. |
| HARBOR | New-layer keyboard/phone behavior is unverified. | P2 condition | Existing view remains unchanged; new actual browser/navigation/reflow gates required later. |
| KEEL | Partition changes could drop or duplicate days. | P1 resolved in tests/operator | Entire cohort compared to the old selection; at most three dates per request; exact monthly time vector required. |
| KEEL | Converting monthly mean inputs is not mean daily conversion. | P1 resolved in tests | Daily paired conversion before means; nonlinear counterexample and common-mask/eligibility regression pass. |
| KEEL | Old GSW web values are not exact references for a newer salinity atlas. | P1 resolved in test | Use3.6.23's full MATLAB check cast and supplied conformance bound; strict canonical replay remains a distinct future gate. |
| LOGBOOK | Existing published source/diagnostic custody must survive new work. | P1 resolved in declaration | Pin both earlier diagnostics and old source/dependencies; no back-edit or reacquisition. |
| LOGBOOK | Resource recovery must preserve original inputs. | P1 resolved in policy |1GiB acquisition floor; no original deletion or weakened engine/full-suite gates. |
| LOGBOOK | User requested one continuing review batch. | P1 resolved in scope | Same branch/draft PR83; no separate PR or main merge. |

Twenty-one findings, no unresolved P1 for the declared supplementary acquisition.
Verdict: **APPROVED-WITH-CONDITIONS** for acquisition and source-method work.
Actual source completion, offline reconstruction, derived portability and
accessible presentation remain required before those milestones can be claimed.
Physical measurement limits remain open across all roles.

Source-packaging follow-up:16 focused tests now pass, including wrong-selection
provider-response rejection before publication and public-path containment. The
first actual supplementary response passes validation; complete acquisition is
live. KEEL/SOUNDER actual original-based full replay and CHART/HARBOR new-layer
presentation conditions remain open. No full-cohort or physical claim added.


## Derived consumer and prepared query/view review

Same seven installed lenses; review concerns source context, not physical
measurement admission. The actual source acquisition is still active.

| Role | Finding | Severity | Resolution / condition |
|---|---|---|---|
| CURRENT | A monthly mean conversion can differ from mean daily conversion. | P1 resolved in method/tests | Frozen daily operator runs before averaging on the unchanged four-field cohort. |
| CURRENT | Pressure and input temperature-scale assumptions survive into derived values. | P1 resolved | Report, row keys, source metadata and viewer explicitly retain0dbar reference and unverified ITS-90 assumption. |
| CURRENT | New layers do not automatically identify fronts or physical edges. | P2 retained limit | No criterion application or identity/width/axis/length/annual footprint admission. |
| SOUNDER | Raw monthly products must match genuine daily originals. | P1 resolved in consumer contract/tests | Check raw pins, NPZ/JSON/coordinates, exact monthly times and all four independently reconstructed means/counts before conversion. |
| SOUNDER | Supplementary IDs could overwrite existing native levels. | P1 resolved in tests | Separate source/profile/row prefixes;46,944 combined rows have distinct IDs at all four depths. |
| SOUNDER | Synthetic conformance is not actual-source replay. | P2 condition | Linux exact synthetic pass recorded separately; full original-based source/derived replay remains mandatory. |
| CHART | Different temperature axes could exaggerate a small pressure correction. | P2 resolved in template | Raw and derived temperature panels share one depth-specific scale across months/meridians. |
| CHART | Conditional derived values must remain visually distinct. | P1 resolved in labels | Separate fifth panel and table column name potential temperature,0dbar reference and ITS-90 assumption; in-situ retained. |
| CHART | Real rendering cannot be established by syntax/tests alone. | P2 condition | Actual72-selection/360-profile browser and visual check prepared; not run or claimed. |
| BEACON | Derivation could be mistaken for an independent measurement. | P1 resolved | Viewer explicitly describes a pressure-reference conversion and source context, not a new observation or current boundary. |
| BEACON | Evidence should remain reachable from the current card and selected section. | P2 condition | Link factory and exact source-specific query route prepared; actual atlas link/native/WASM navigation pending. |
| BEACON | A partial download must not be labeled full-year success. | P1 resolved in status | Acquisition remains live; publication gated on complete originals and replay. |
| HARBOR | A fifth chart needs equivalent complete textual values. | P1 resolved in template | Seven-column table retains raw fields, derived temperature and counts, with complete JSON alternatives. |
| HARBOR | New controls and captions need actual keyboard/phone testing. | P2 condition | Existing semantic controls/focus/history pattern retained; new source browser gate remains required. |
| HARBOR | Missing samples must not become interpolated chart segments. | P1 resolved in contract | Nullable means and line breaks retained; derived/raw support must match before display. |
| KEEL | Thermodynamic backend portability was uncertain. | P1 resolved for the synthetic probe only | Linux job120173481020 passes all six exact arrays and whole stored NPZ; actual-source derived byte gate still required. |
| KEEL | UI link edits should not change scientific producer provenance. | P2 resolved in dependency design | Derived producer independently verifies source products; it does not depend on the presentation/query adapter code. |
| KEEL | Corrupt support or raw means must fail closed. | P1 resolved in focused tests | Empty, missing, duplicate/reordered, wrong-count and changed-mean cases reject;40 focused tests pass locally. |
| LOGBOOK | Prepared pages are not delivered atlas features. | P1 resolved in status | No generated page, index, packet or existing atlas change; actual complete-source integration remains pending. |
| LOGBOOK | The active acquisition graph must stay frozen. | P1 resolved in checks | Only independent consumers/UI/tests/CI changed; declared producer/protocol/conversion and older dependencies still check exactly. |
| LOGBOOK | Batch and CI status must match remote evidence. | P1 resolved | Same PR83; exact Linux conformance and34-report/old-source success separated from offline paper403 and pending new-source gates. |

Twenty-one additional findings. No unresolved P1 for publishing the prepared
consumer code. Verdict: **APPROVED-WITH-CONDITIONS** for source/context tooling.
Actual full-source/derived replay, generated views, accessibility and atlas
native/WASM checks remain required before those milestones can be called done.

KEEL follow-up:job120178967847/run39881273814 at11e54ed passes the exact
synthetic stored NPZ and all40 focused tests on Linux (2.82s). This resolves
focused cross-platform method/query conditions only. Actual new-source and
derived report replay, all72 rendered selections and main native/WASM atlas
integration remain required; the acquisition is still active.


## Actual source and profile conditions update

SOUNDER/KEEL: all135 actual responses and277 retained archive members pass
strict offline replay of all three raw products. Complete actual-source daily
GSW report is byte-exact locally; the separate actual-source Linux gate remains
pending. CURRENT: unverified ITS-90, pressure approximation and all physical
admission limits remain explicit. CHART/HARBOR: actual72-selection/360-chart
browser gate passes, including23,472 native rows, shared temperature scales,
keyboard/history and320px reflow; desktop/phone screenshots visually inspected.
BEACON/LOGBOOK: this is complete source/profile delivery in the same PR83, not
a physical measurement or delivered main-atlas query integration. Main-card
links, lossless indexing and full native/WASM readback remain required.


### Complete actual-source Linux result

At4d0bf3247a596fd0d79173df73917ddf2deac0c1, independent run39886838991/
job120196871730 is terminal PASS. It checks the synthetic probe,40 focused
tests (2.88s), all277 archive members/135 genuine responses and all three raw
products, then the complete actual-source derived JSON byte for byte. Both
retained/rebuilt report SHA256 values are
90b122ddfa9da60d2c3d02437f50b2ae7045b420f8672029d3611ad8f74198f8.
Both source and derived checks use zero network requests. This resolves the
actual-source portability condition without a tolerance or changed report.
The separate offline job fails upstream at the paper fixture; no full-suite
green claim is made. Main-atlas integration/readback remains pending.
