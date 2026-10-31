---
skill: roles-check
topic: indian-secc-oscar-climatology
date: 2026-10-14
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Indian SECC study-region data: internal review

Base: 82ded87675e984f31344d9c4cdda12248810c9b4. Seven applicable repository
lenses review the preflight, acquisition, averaging, diagnostics, query joins,
source navigation and figures. ORBIT does not apply. This review permits
editorial derived-data delivery, not independent scientific admission.

| Role | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| CURRENT | Frequency/phase classification limits are not paired velocity edges. | P2 | Search uses6–2.5 S; crossing search is not capped there; outside-context crossings flagged. |
| CURRENT | Eastward peaks can include other modes or eddies. | P2 | Current association remains false; no current width, footprint or annual extrema admitted. |
| CURRENT | Width of a climatological vector mean differs from mean yearly width. | P2 | Two operators retained separately; equal-year mean specified and independently tested. |
| SOUNDER | Source80.5 E is not a native archive column. | P2 | Two bracketing columns retained separately; no observed interpolation or longitude spread called uncertainty. |
| SOUNDER | Year weighting and vector masks can change the mean. | P2 | Minimum5 paired records/year-month and18 valid years/climatology cell; shared u,v masks and valid-year lists retained. |
| SOUNDER | Provider nearest-time selection includes a2017 boundary record. | P2 | Original CSV rows retained;2017-01-01 explicitly excluded from1995–2016 analysis; no timestamps rewritten. |
| CHART | Missing spans must not become zeroes. | P2 |16/24 climatological spans and269/528 yearly spans remain unresolved; separate missing strip and grey/dash cells. |
| CHART | Crossing outside context does not diagnose a physical mode. | P2 resolved | Plot label changed from mode overlap to outside context; interpretation remains pending. |
| CHART | Local section lines are different from current footprints. | P2 | Maps carry climatology period and local-section role; only paired boundaries mapped, no width corridor or seasonal footprint. |
| BEACON | Conditional year-to-year ranges can look like confidence intervals. | P2 | Each month displays resolved-profile count and conditional finite spread; threshold/grid/error quantities remain distinct. |
| BEACON | Data completion is different from width identification. | P2 |3168 gridded profiles,528 yearly monthly profiles and24 climatological profiles stated separately;143 prior scoped widths unchanged. |
| BEACON | Study season definitions differ. | P2 | Actual calendar months used; no shared winter/spring calendar or reconstructed EOF claim. |
| HARBOR | Color alone cannot explain missing values. | P2 | Heatmap numbers and dashes, source tables and accessible SVG descriptions supplement color. |
| HARBOR | Consecutive source links fused at narrow width. | P2 resolved | New links separated into block touch targets of at least44 px. |
| HARBOR | Playback must support reduced motion and exact record access. | P2 | Reduced-motion disables automatic playback; manual month selection, real inspectors, both column links and320 px reflow tested. |
| KEEL | Original-data reconstruction must be independently checkable. | P2 | Raw metadata/CSVs/requests/checksums retained; full reconstruction plus independent CSV-cell means and WGS84 checks pass. |
| KEEL | Edited rows and rehashed source receipts cannot redefine admission. | P2 | Frozen Rust diagnostic pins and Python source pins; nine coherent native/WASM rejection cases, including forged root dependency. |
| KEEL | Earlier data and final generated assets require publication gates. | P2 | Prior143 widths/211 samples/routes preserved; final complete suite and mainline browser results recorded below. |
| LOGBOOK | Old no-numeric literature review remains valid for that source. | P2 | Archived verbatim in new source audit; active decision now identifies derived section diagnostics. |
| LOGBOOK | Counts must reflect samples and support, not new canonical currents. | P2 |249 indexed JSON sources;28 diagnostics;235 width samples;20 series; canonical names,143 width definitions and75 routes unchanged. |
| LOGBOOK | One batch PR and accurate CI status are required. | P2 | Same branch/PR83, no merge; previous source-provider failures and Antilles platform-roundoff failure distinguished from final local tests. |

Amendments: use equal-year vector means; separate native longitudes and yearly
results; preserve weak/missing/domain-edge cases; correct the mode-identification
label; fix unresolved-resolution text and narrow-screen links; scope the old
Kuroshio calendar assertion to its own source rather than the first missing row.
Older one-year component assertions still cover all84 old component samples;
the new24 climatological samples have separate coverage and source assertions.

The preceding Linux CI run reached unit validation and exposed submicrometre
roundoff in an unrounded Antilles geodesic reconstruction. A shared comparison
now permits an absolute 1e-10 km difference only at the unrounded survey-span
field. Source hashes, coordinates, velocities, thresholds, displayed distances,
nulls and admission flags remain exact. Twelve targeted tests and twelve
subtests pass, including one-ULP acceptance and seven strict mutation guards.
The Antilles diagnostic bytes and twenty query rows remain unchanged.

An older Loop regression selected inventory entry zero; it now selects the Loop
entry by current identity, preserving all five source-mutation checks.

## Validation

Complete local publication gate: 1,418 tests and 1,061 subtests passed in
1,401.20 seconds (23m21s). All 47 Rust tests passed. Dedicated browser checks
passed for all 44 collections, all 100 current cards / 143 width records,
existing basin sections and dashboard navigation. Original staged/source bytes
and all 63 query-engine manifest hashes matched. Remote CI is separate. Native/WASM source/profile queries,
all528 yearly profiles,24 climatological samples, playback, missing marks,
exact37-cell source query and nine rejection cases have passed dedicated checks.
Scientific current identification, normal-flow boundaries, uncertainty and
whole-current/annual dimensions remain open.
