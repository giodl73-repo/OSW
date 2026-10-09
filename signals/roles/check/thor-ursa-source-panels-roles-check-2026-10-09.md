---
skill: roles-check
topic: thor-ursa-source-panels
date: 2026-10-09
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Thor and Ursa dated source panels: internal review

Artifact: original-source inventory, scientific scope protocol, Rust and WASM
scene generation, atlas/object source viewers and source-index navigation.
This review supports the scoped editorial implementation. It does not constitute
independent scientific admission or a mainline release.

## Selected roles and findings

CURRENT reviews physical definitions and event attribution; SOUNDER reviews
provenance and transformations; CHART reviews source map meaning; BEACON reviews
public claims; HARBOR reviews equivalent interaction; KEEL reviews executable
guards; LOGBOOK reviews repository and publication status. ORBIT is inapplicable
because no planetary analogy is used.

| ID | Role | Finding | Severity | Evidence and disposition |
|---|---|---|---|---|
| 1 | CURRENT | Deep pressure colors can be mistaken for surface ring boundaries. | P2 | Resolved: field definition and crop descriptions explicitly separate SSH_ref colors from the bold surface Loop Current contour. |
| 2 | CURRENT | Dates during a shedding event do not identify a detached ring in every panel. | P2 | Resolved: every row is regional event support; `ring_identity_from_panel_alone=false`; no center, radius or state relation. |
| 3 | CURRENT | Methods print `0.65 cm`; silently substituting meters would invent a contour rule. | P2 | Physical unit remains unresolved. Scoped presentation preserves the literal, null normalization and no numerical contour reconstruction. Scientific contour admission remains conditional. |
| 4 | SOUNDER | Mutable publisher responses need archived original provenance. | P2 | Resolved: complete 90,312-byte JATS XML and both original WebP figures have fixed SHA-256/size pins, acquisition receipt and original source URLs. |
| 5 | SOUNDER | Image crops could be confused with spatial coordinates. | P2 | Resolved: source pixel rectangles and `source_image_pixels_no_geographic_geometry` role; all longitude/latitude geometry is null. |
| 6 | SOUNDER | Reproduction requires permission, author credit and changes notice. | P2 | Resolved: archived original license links CC BY 4.0; viewer retains author/copyright/DOI/license, discloses selected-panel cropping and provides unchanged complete images. |
| 7 | CHART | A frame edge is not a valid ring closure. | P2 | Resolved: protocol forbids closing curves along frames or filling patches; zero polygons admitted. |
| 8 | CHART | A selected crop omits geographic axes and the color legend. | P2 | Resolved: caption explains that omission and complete original figure is available adjacent to the crop in a keyboard-accessible local scrolling region and original-image link. |
| 9 | CHART | The 2021-03-07 closed-looking curve needs interpretation before digitization. | P3 | Retained research lead only; no complete-ring status, georeferencing or boundary measurement follows from visual closure alone. |
| 10 | BEACON | Fifty panels could be reported as fifty identified eddies or positions. | P2 | Resolved: two event owners and fifty regional field panels; explicit claim limit rejects independent-position and footprint counts. |
| 11 | BEACON | A recurring seasonal animation would overstate an irregular event sequence. | P2 | Resolved: manual previous/date/next controls only; no interpolation, seasonal playback or annual extrema. |
| 12 | BEACON | Readers need a short path from the image to its precise source record. | P2 | Resolved: per-date source-index pointer opens all fifteen panel fields. Browser testing found and corrected a one-field limit. |
| 13 | HARBOR | Selected date and boundary limits need text alternatives to the map. | P2 | Resolved: labeled native select, live date/panel/row/column status, SVG description and accompanying definitions/limits. |
| 14 | HARBOR | Fixed-width original figures can break mobile reflow. | P2 | Resolved: local horizontal region; browser verifies 320 px document containment for both atlas and object pages. |
| 15 | HARBOR | Source navigation must work without a pointer or animation. | P2 | Resolved: semantic buttons/select, keyboard Enter exercise, disabled boundary buttons, no auto motion. Human assistive-technology review remains a P3 follow-up. |
| 16 | KEEL | Re-signed source receipts can hide scientific promotions. | P2 | Resolved: immutable source audit SHA; nine native/WASM rejection cases cover dates, owners, crops, geometry, unit normalization, playback, missing proof, original XML and figure dependencies. |
| 17 | KEEL | Atlas and object renderers could diverge or fetch unchecked scientific JSON. | P2 | Resolved: identical Rust scene data in both views; source-index inspection uses archived original JSON. Existing atlas/object browser gates verify parity and no direct research JSON reads. |
| 18 | KEEL | Generated source-index and engine artifacts must agree with the checkout. | P2 | Resolved: index corpus and native/WASM engine rebuilt serially; Python, Rust, shipped browser, JavaScript and page-assignment gates recorded in the batch receipt. |
| 19 | LOGBOOK | Visual evidence must not silently upgrade current/eddy coverage counts. | P2 | Resolved: all 42 query collections are byte-equivalent as decoded JSON to the parent; one named footprint remains, zero new physical joins. Only audit, dependencies and scene outputs are added. |
| 20 | LOGBOOK | A local pass or draft PR is not evidence of mainline publication. | P3 | Retained: branch and draft status explicitly recorded; hosted gates separately tracked. No merge or published scientific-release claim. |
| 21 | LOGBOOK | Review outcomes must distinguish engineering guards from scientific review. | P3 | Retained: internal roles review only; boundary definition, unit reconciliation and independent scientific admission remain required. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. P2 findings: 18, with 17 resolved and one
physical-unit limitation retained under explicit presentation scope. P3 notes: 3.
HARBOR's human-review follow-up is included in finding 15's disposition.

Verdict: **APPROVED-WITH-CONDITIONS** for this source-panel viewer only.
Top finding: neither regional event panels nor closed-looking curves establish
the named ring's admitted physical footprint. CURRENT, CHART and SOUNDER agree
that source geometry, contour convention and temporal identity must be reviewed
before physical state joins or dimensions are calculated.

## Amendments applied

1. Preserve the source's printed contour unit with null normalization, and bind
   all dates/identity/scope to the frozen audit across loaders.
2. Separate selected source pixels from geography; provide original axes and
   legend plus text alternatives and prohibit inferred frame closures.
3. Correct source-row navigation to show all fifteen fields; retain explicit
   draft/internal-review status and zero new footprint/dimension claims.

Final gates: 1,272 offline Python tests plus 923 subtests, 45 Rust tests,
the new source-panel browser with nine native/WASM guards, existing atlas and
object browser gates, eight repaired standalone navigation checks, 54 JavaScript
modules and fourteen page assignments pass locally. A parent hosted run reached
the browser suite and failed on a title selector matching a new evidence
subheading. Direct feature-title selectors and a directory reload readiness
wait were corrected and all affected checks re-run. Hosted verification of this
branch remains pending.
