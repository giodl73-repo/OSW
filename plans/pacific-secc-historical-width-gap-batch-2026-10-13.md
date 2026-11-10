# Pacific SECC historical width gap batch

2026-10-13. Continuing draft PR #83 / `codex/current-measurement-gaps`.
Previous goal turn was progress: cfd27bb added three basin-section diagnostics.
This batch adds a primary-source width range for the Pacific South Equatorial
Countercurrent, closing one missing source-width assessment.

## Result and source support

Rotschi, Hisard and Jarrige (1972), Survey Paper No. 15, reports a 300–900 km
geostrophic-current width range near 10 S at 170 E (printed p10 / PDF13).
The complete 120-page English adaptation is retained outside Git: 4,021,588
bytes, SHA256 `f2d8d1c8ba9655146319829b942278a13ac792b4a634e6d547a2cd17bc6b24fe`.
The title, preface, cruise table, direct-current method and width passage were
visually reviewed (PDF1,2,7,9,13). Copyright ORSTOM is preserved; no original
figure or PDF is published. Acquisition/annotation receipts are tracked.

The source distinguishes the near-10 S SECC from the South Tropical
Countercurrent south of 15 S and from the equatorial/subsurface Cromwell
extensions. Contemporary Wu et al. (2026), DOI 10.1029/2025JC023053, published
abstract and Crossref metadata provide naming context only; full article not
obtained. No contemporary season, layer, range or transport is transferred.

The eleven Bora/Cyclone cruises span November 1965–May 1968. The author does
not assign the range endpoints to particular occupations in this passage.
This is not an annual range, uncertainty interval or recurring seasonal pair.
No 600 km midpoint, exact width dates, monthly profile or full-parent width
is invented. The speed-above-10 cm/s upper-300 m statement is separate from
width depth support. The direct equatorial current-meter 500 m no-motion
reference is not applied to the geostrophic width. Width reference level,
paired-edge criterion and fixed-depth support remain unresolved.

## Integration

Source-width evidence becomes 132 records / 71 owners; 17 owners remain
unassessed. Prior 131 rows and all other owner decisions remain unchanged.
Exactly the Pacific SECC owner fingerprint changes; its observation date
remains null. No source value is assigned to the generic family, SSCC/Tsuchiya,
STCC or a neighbouring current.

Native/WASM and Python validate the frozen original descriptor independently
of mutable incoming owner/context fields. The original-source interval chart,
source-query access and static inspector retain no midpoint or mapped edges.
Atlas has no new current route/width footprint; seasonal playback remains
unavailable. Canonical inventory, published lengths, all 73 reference routes
and the 163 earlier query samples remain unchanged. Seasonal route data changes
only its width-inventory dependency receipt. Lossless corpus becomes 200 JSON
documents; the original report joins the strict local-fixture hydrator (30).

## Verification

46 Rust tests and serialized locked native/WASM builds passed. Five focused
source/scope tests and 12 mutation subtests passed. Browser passed query parity,
atlas interval, static inspector, source metadata, 320 px reflow and three
native/WASM scope rejections (midpoint, uniform depth, family reassignment).
Exact index-store and complete offline gate results follow after completion.

Reproduce by hydrating originals, validating the width inventory and frozen
scope audit, reviewing the single seasonal receipt refresh, rebuilding dashboard,
index corpus, query bundle and serialized Rust engine; then run complete offline
and registered browser checks. Never rebuild executables while tests use them.
Remote CI is distinct from local validation; previous-head acquisition failures
must not be described as scientific test failures or resolved by substituting
another paper edition.

## Final gate receipt

**1,331 tests and 943 subtests passed in 1204.84 seconds (20m04s).** Exact index-store browser passed 200 documents / 12 seasonal snapshots / independent NOAA oracle / native-WASM parity and checked-input rejections. Final historical-range browser passed atlas/static inspector, source metadata, mobile and three native/WASM scope rejections. High endpoint label alignment corrected and visually checked. All 30 local originals and 61 engine pins verified. Earlier 131 measurements and all other owner decisions preserved; no canonical, length, route or 163 sample change. Editorial publication conditions satisfied; physical/annual/canonical admission limits remain. Prior-head remote run 38484171709 stopped at Qiu institutional download timeout before tests.
