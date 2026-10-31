---
skill: roles-check
topic: norkyst-continuous-months
date: 2026-10-17
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Continuous monthly section review

Artifact: prospective temporal-support declaration, source acquirer/parser, complete-month section analysis, figure, original archives and tests. Seven installed lenses applied directly, not seven independent reviewers. ORBIT does not apply.

| Role | # | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | 1 | Hourly snapshots cannot represent monthly distributions. | P2 resolved for two months | January/July each retain every 744 calendar hours and 36-hour halos. Ten target months remain. |
| CURRENT | 2 | A low-pass filter is not a full physical tide decomposition. | P2 resolved | Explicit kernel, missing support and non-tidal attenuation; no claim of complete tide removal. |
| CURRENT | 3 | Offshore model profiles do not establish physical current width. | P2 resolved | Layer, section, missing coastal boundary and unknown widths/ranges remain explicit; no inventory admission. |
| SOUNDER | 1 | Source metadata/packing can change across days. | P2 resolved | All daily metadata, arrays, cadence and coordinate axes validated; each original member byte-pinned. |
| SOUNDER | 2 | Newly fetched archive fields could differ from the earlier product. | P2 resolved | Both retained day-15 noon fields match all 2,400 packed cells and masks exactly. |
| SOUNDER | 3 | Cache-copy times are not acquisition times. | P2 resolved | Initial metadata probe uses its batch-completion bound with an explicit time basis; revalidation preserves original response times. |
| CHART | 1 | Different scales could exaggerate seasonal differences. | P2 resolved | Shared symmetric total/low-pass velocity colors, common velocity-profile and salinity comparison axes. |
| CHART | 2 | Interpolated display points could imply finer model resolution. | P2 resolved | 3.2 km retained grid spacing and display interpolation stated beside the figure and in the report. |
| CHART | 3 | A dashed reading marker might look like a physical boundary. | P3 addressed | Caption and profile legend explicitly identify the earlier noon reading. No map footprint is drawn. |
| BEACON | 1 | Two months could be oversold as an annual result. | P2 resolved | Completed months and remaining ten months explicit; complete-annual flag false. |
| BEACON | 2 | Temporal quantiles could be repeated as confidence intervals. | P2 resolved | Plot, report and plan identify sample quantiles and population standard deviation as model temporal variation. |
| BEACON | 3 | Model output could be described as an observation. | P2 resolved | Model/hindcast labels and source/layer/date throughout. |
| HARBOR | 1 | An image alone cannot supply the numerical evidence. | P2 resolved for research | Full support/statistics report and numeric raw/low-pass asset retained; SVG has title/description. UI integration remains pending. |
| HARBOR | 2 | Palette must not be the only way to recover sign or selection. | P2 resolved | Signed axes/colorbar, profile lines, zero line, text and data equivalents. |
| HARBOR | 3 | Future playback must respect time gaps and user motion settings. | P3 condition | Research figure is static; later UI must retain discrete actual times, keyboard controls and reduced-motion checks. |
| KEEL | 1 | Filtering can introduce phase shift or fill gaps silently. | P2 resolved | Constant/linear preservation, symmetric support, synthetic frequency response and full missing-support propagation tested. |
| KEEL | 2 | Source-byte and numerical reproducibility are different contracts. | P2 resolved | Exact original pins; tight numeric comparisons without rewriting retained assets; deterministic same-environment exports. |
| KEEL | 3 | A baseline full run cannot cover newly added research tests. | P2 condition | Dedicated source/filter/full-original reconstruction gate; 8130086 combined run reported separately. Final rolling release gate remains required. |
| LOGBOOK | 1 | Local declarations do not prove external preregistration. | P2 resolved | Prior snapshot exposure and local-timestamp/publication limits recorded; no fully blinded claim. |
| LOGBOOK | 2 | Existing measurements and physical geometry must remain intact. | P2 resolved | New research files only; inventory, routes, frames and indexed/compiled counts unchanged. |
| LOGBOOK | 3 | Publication destination must match the user's consolidated workflow. | P2 resolved | Same branch and draft PR 83; no additional PR or main merge. |

## Synthesis

Roles reviewed: 7. Findings: 21. Open P1: 0. Release conditions: complete remaining temporal acquisition, review/integrate its UI and run the final combined gate before release. **APPROVED-WITH-CONDITIONS** for retained two-month research/source preparation, not physical current-width admission or completed annual coverage.

CURRENT/BEACON agree that the whole-current and annual-width dimensions remain unresolved. SOUNDER/KEEL agree on exact original-source pins with separate numerical reproducibility tolerances. KEEL/LOGBOOK require honest candidate-specific gate reporting.

## Amendments applied

1. Retained complete month/halo support, source/noon continuity comparisons and the explicit filter's null propagation.
2. Qualified metadata timing and prior exposure; original bytes and older data remain intact.
3. Added common comparison axes, SVG description/numeric alternatives, non-mutating reconstruction tests and explicit remaining acquisition/UI work.

## Acquisition continuation review

The subsequent collector change preserves the earlier producer version in f3572c1. SOUNDER/KEEL checked known daily metadata across differing hourly cuts, exact ZIP-container preservation and local cache hydration. KEEL checked atomic progress and startup code bindings. LOGBOOK checked that the completed 8130086 gate is not claimed for this research extension. CURRENT's physical-admission limits, CHART's unchanged figure semantics, BEACON's incomplete-year language and HARBOR's later UI conditions continue to apply.

Three further amendments are implemented: local reuse of byte-pinned original archives; separate daily metadata and hourly-cut field identities; atomic journals and detection of code changes during acquisition. Four added collector tests join the sixteen source/filter/reconstruction tests: **20 tests and 20 subtests passed in 11.85 seconds**. Annual data, year visualization and shared UI integration remain incomplete; the approval scope is unchanged.
