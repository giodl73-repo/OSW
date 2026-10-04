---
skill: roles-check
topic: navo-detection-detail
date: 2026-10-02
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Dated detection detail: implementation review

Reviewed the full-candidate object page, atlas navigation, download packet,
methods, source receipt, and browser tests. Selected CURRENT (identity and
time), SOUNDER (source closure), CHART (plot meaning), BEACON (interpretation),
HARBOR (equivalent access), KEEL (validation), LOGBOOK (release boundary).
Applied the installed `.roles` lenses in this task, not independent human
scientific or accessibility approval.

| Role | Finding | Severity | Evidence and recommendation |
| --- | --- | --- | --- |
| CURRENT | The page identifies one dated detection. | P3 | Date and provider code appear in heading/identity. Keep lifetime and historical-name equivalence unresolved. |
| CURRENT | Polygon support is restricted to the provider product. | P3 | No depth, transport, permanence, or flow mechanism is inferred. Preserve those limits. |
| CURRENT | NASA context is spatial regional navigation. | P3 | Text excludes detection identity and temporal match. Do not infer event correspondence from crop overlap. |
| SOUNDER | Full source rings drive the detail view. | P3 | Geometry table supplies coordinates; source ZIP digest is visible. Do not substitute a simplified display ring for evidence. |
| SOUNDER | The packet carries source and method references. | P3 | It includes detection/state claims, snapshot and join sources, and crop/state context claims/sources. Keep source closure when adding fields. |
| SOUNDER | Source reuse remains pending. | P2 | Candidate status is visible and screening still excludes records. Resolve the specific decision before public release. |
| CHART | Plot coordinates have uncertain datum. | P2 | The plot and identity text say exact datum/position uncertainty unspecified. Obtain metadata before promoting precision. |
| CHART | The inset is an equal angular plot without a basemap. | P3 | Caption states projection, north orientation, symbols, and absent state/coast lines. State containment is textual evidence computed separately. |
| CHART | Outline and center have distinct symbols. | P3 | Cross is labeled provider center; polygon is labeled full source ring. Preserve semantic descriptions. |
| BEACON | Dated IDs connect the reading surfaces. | P3 | Atlas outline, state reading, and object search navigate to the same ID. Keep names separate from codes. |
| BEACON | Giant coordinate dumps obscure geometry interpretation. | P3 | Identity now summarizes vertex count/role instead of dumping polygon coordinates. Full coordinates remain downloadable. |
| BEACON | Scientific review status remains visible. | P3 | State-evidence disclosure and packet retain unreviewed status. Candidate presentation does not certify a claim. |
| HARBOR | Footprint meaning is available without perceiving the graphic. | P3 | SVG label gives bounds/date/datum; text supplies state relation, symbols, and limits. Preserve this alternative. |
| HARBOR | Map links need pointer and keyboard operation. | P3 | SVG anchors have labels/focus styling; pointer-events are enabled on anchors despite the noninteractive overlay default. Browser checks target the link. |
| HARBOR | Human screen-reader review remains open. | P2 | Narrow layout and semantic assertions do not prove complete accessibility. Keep the publication gate. |
| KEEL | Browser exercises a real navigation path and download. | P3 | State link opens C26001; test reads the downloaded packet and checks canonical IDs, polygon, sources, context, and pending status. Retain this behavioral test. |
| KEEL | Four new links change the broad SVG anchor total. | P3 | The test now counts 181 anchors and separately checks four detection anchors. Existing locator behavior remains checked. |
| KEEL | Packet URLs must not accumulate across rendering. | P3 | Previous Blob URL is revoked before another render. Keep this resource lifecycle if in-page routing is introduced. |
| LOGBOOK | This is full research presentation. | P3 | Candidate banner/source status distinguish it from screened review. No deployment or publication is performed. |
| LOGBOOK | Methods and changelog record the navigation join. | P3 | Documentation distinguishes canonical footprint from regional context. Rebuild manifest-covered copies after editing. |
| LOGBOOK | The broader release remains unfinished. | P3 | Source-use, scientific and accessibility decisions remain pending. Do not equate this feature with completed atlas coverage. |

Roles reviewed: 7. P1: 0; P2: 3; P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for internal candidate presentation.
CURRENT/BEACON agree that NASA regional overlap is not a detection match;
CHART/SOUNDER agree that source coordinates have unresolved datum.

Three amendments implemented: source-closed review packet with contextual
claims; explicit geometry/projection/date/identity limits; usable atlas anchors
with focus and pointer handling. Initial browser verification passed the new
detail navigation/download/reflow. An earlier assertion counted 177 anchors
and failed after four new links were introduced; it now checks the new total
and detection anchors separately. Final verification is recorded below.

Final full browser check passes, including atlas pointer targetability,
state-to-detection navigation, canonical footprint, immediate state relation,
packet download and source references, NASA regional-context disclosure, and
390-pixel detail layout. JavaScript syntax checks and the motion almanac data
check pass. The full release check passed after documentation changes; the
final regenerated full manifest also passes. Rights-screened preview and
isolated site checks pass (217 entities, 8,635 claims, 267 files, 70 crops);
pending NAVO detections and polygons remain excluded.
