# Aleutian/Subarctic region: direct velocity support

Parent aec3c7f95c740dec1dfd1230df3e5fee6ce1d0df. Continue `codex/current-measurement-gaps` and draft PR #83; no separate PR or main merge.

## Data gap addressed

Add the original, directly observed JASADCP P14N velocity section to the Aleutian/Subarctic card, seasons evidence, query and source store. This supplies measured u/v and sampling support alongside the earlier, separately retained 2013 OSCAR product diagnostic. A newly acquired observational section improves the measurement evidence without automatically resolving physical width.

The original archive gateway identifies SAC_ID 00016, TT9306, P14N, EXPOCODE 325023_1, Gunnar Roden / University of Washington; processing by E. Kestenare and E. Firing / University of Hawaii. Original reduced NetCDF SHA256: `5dd5e1dbaa52630294fa905f35c7262cb6522d4c82bcf4daf4f736459af40132`, 320,512 bytes. Exact provider gateway, cruise metadata and format template are retained with their individual acquisition hashes. This is a public institutional data archive; attribution is retained and no broader copyright license or source-panel reuse is inferred.

Preflight: `plans/aleutian-p14n-1993-vector-section-preflight-v1.md`. It was written after reading source metadata and the published regional context, before inspecting newly acquired velocity values. No blinded or externally timestamped preregistration is claimed. Context: Chen and Firing (2006), doi:10.1029/2005JC003064, introduction and section 3 paragraph 7.

## Fixed support and calculation

- Selection: 40–48 N, 178–180 E, 7–18 July 1993. The resulting 132 hourly profiles are dated 13–18 July.
- Retain all 31 reduced-product depth levels, 30–330 m: 4,092 paired positions, 4,030 jointly valid. Preserve component-specific masks and provider units; neither speed magnitude nor zero replaces missing u/v.
- For the primary 100–300 m comparison, use midpoint-cell thickness clipped to the layer, joint u/v validity and at least 160 m valid support. Exactly 131 profiles meet that rule. This is a layer mean of the reduced product, not a native-ensemble reconstruction.
- Preserve original source time indices, timestamps, hourly mean positions and acquisition order. Report time gaps and WGS84 straight distances/bearings between those mean positions; they are neither sailed distances nor a flow/current axis.
- The track contains 16 northward latitude steps and one two-hour gap. The plot breaks at gaps over 90 minutes and missing means. Do not silently reorder by latitude or interpolate a new crossing.
- Fixed northern and southern search windows, 44–46 N and 41–43 N, follow published branch context. They are not measured edges; matching cold-water support remains unavailable in this batch.

## Shared delivery and limits

One source-bound observed-section diagnostic is added. Inventory remains 155 scoped width records across 81 owners; all earlier width values remain unchanged. There are 43 diagnostics, five shared research scenes, 321 indexed JSON documents and 89 engine dependency pins. Earlier four research scenes and 42 diagnostic records remain equal. Whole-current width, annual ranges, physical-edge geometry and seasonal playback remain unknown or disabled for this section.

The figure shows original paired components by latitude/depth, the declared layer means and unconnected sample positions. It is an OSW plot from archived data, not a copied paper panel. Source queries expose all profiles, branch windows, sampling legs, acquisition and figure provenance. The same renderer supplies cards, seasonal evidence, direct diagnostic queries and record inspection.

## Verification and gate conditions

Initial source and shared-registry gate: 12 tests and 10 subtests passed in 3.78 seconds. Initial dashboard scope-link gate: one test and five subtests passed in 89.32 seconds. The existing NumPy binary-size warning remains visible. Initial engine build: 59 Rust tests passed in 2.43 seconds. Final source, figure, track-support and Rust additions require the final rebuild and focused rerun; record results in a follow-up receipt rather than treating initial passes as final.

Actual browser coverage exercises five owners across cards/seasons/query/source/inspector/mobile, the source documents and mixed diagnostics. The original 22 native/WASM corruption scenarios are retained and ten observed-section cases are added, including coherent source rehashing, unit/mask/layer changes, false association/annual range, reordered sampling, missing/duplicate records and changed raw NetCDF pin. Do not claim the final browser gate passed until its process finishes successfully.

The clean full suite at aec3c7f remains a separate running gate for the prior combined head. A new clean combined gate is required on this committed batch; a prior or running gate cannot certify the new source. Latest inspected aec3c7f CI runs failed during acquisition of older paper fixtures: one GEOMAR 403 for Stramma (1992), and one Reading connection refusal for Van Aken (2003). Those failures do not invalidate the retained local originals, and remote CI is not green.
