# South Indian Current: paired hydrography source batch

Continue `codex/current-measurement-gaps`, draft PR #83. No per-gap PR and
no main merge. This is the next source prerequisite for the unresolved South
Indian Current width, after the finer-grid Indian SECC investigation.

## What changed

- Completed a visual review of all ten pages of Stramma (1992), original
  checksum recorded in the new full-paper review. Earlier historical access
  records remain unchanged. The paper supplies no defensible width estimate.
- Declared a source selection before downloading its new field values:
  HYCOM 2013, 48–30°S, native 80°E and its immediate neighbors, exact native
  15 m and 1000 m depths, paired U/V/in-situ temperature/salinity.
- Added strict four-field/depth response validation and common-time monthly
  averaging, retaining the missing dates and native missing-value masks.
- Added original-response packaging and exact offline reconstruction, using
  the already tested portable stored-NPZ writer without changing it.
- Added a profile viewer for all 12 months, two depths and three meridians,
  with four plots and a native-value/count table. This is a section view,
  not a map of a diagnosed current footprint.

## Commands

```powershell
python analysis/acquire_south_indian_hycom_hydrography.py plan
python analysis/acquire_south_indian_hycom_hydrography.py acquire
python analysis/package_south_indian_hycom_hydrography.py package
python analysis/package_south_indian_hycom_hydrography.py reproduce
python analysis/build_south_indian_hydrography_view.py
python -m pytest analysis/test_south_indian_hycom_hydrography.py -q
python analysis/test_south_indian_hydrography_browser.py
```

The plan is idempotent only for the exact declared selection/operator bytes.
Acquisition retains successful originals and resumes missing requests; it
records failures instead of modifying the sampling rules. Packaging requires
every frozen request. Original global metadata/coordinate acquisition receipts
are retained from the previous source archive, with their actual old times.

## Verification status at foundation

Eleven focused parser, metadata and arithmetic tests passed. The first actual
response passed every field, packing, depth and coordinate check. Full-year
acquisition is in progress, with timeout failures recorded. Packaging,
full-original reconstruction, generated-view browser checks and query/index
integration remain pending until all source responses validate. Viewer code
is not a claim of a published or browser-verified result.

The profile JavaScript passes Node syntax checking. The explicit browser gate
checks all 72 selections against retained native arrays/JSON, every table row,
fixed scales, missing-data path breaks, keyboard controls, links and 320 px
reflow. That gate is implemented but awaits the complete retained dataset.

Profile URLs now retain the calendar month, native depth and exact native
longitude. The same gate covers reloadable permalinks, Back/Forward and an
explanation when unsupported URL selections fall back to defaults. Node
syntax checking passes for the updated viewer; actual browser checks remain
pending the complete source. The view is not linked as a finished atlas result.

Local disk headroom was recovered through lossless NTFS compression of derived
Rust outputs, current generated query parts and generated scientific reports.
All affected content hashes were checked before and after and remain exact.
No file was deleted and no provider original was changed. The disk preflight
and all source/scientific checks remain in force; this is not a full-suite pass.

The previous batch's 33 scientific report/operator pairs, 170 scoped width
rows and 78 reference routes are not changed by this source foundation.
The unresolved whole-project offline bootstrap currently encounters the
institutional Stramma PDF HTTP 403; the historical Rotschi blocker was from
an earlier run. Existing local paper access does not make that CI green.

## Admission rules

No physical width, axis, length, annual extrema, seasonal footprint, NASA
match or state passage is admitted by this source step. A strong eastward
peak might be ACC, and a hydrographic front alone is insufficient to name
the flow. Three nearby native meridians are correlated sensitivities, not
independent observations or a longitudinal axis survey. Two levels do not
establish a vertical mean or a historical deep geostrophic reference.

Next: finish exact source reconstruction, inspect all monthly paired profiles,
then declare a separate feature-association/edge protocol before estimating
a named-current width. Preserve negative and unresolved outcomes.

## Paired-profile diagnostic declaration

While acquisition remains live, a second frozen protocol now defines all
native adjacent gradients and positive salinity-gradient/eastward-component
peak candidates. It was declared before new field values or profiles were
interpreted. It uses actual WGS84 cell separation, keeps full plateau supports,
missing/domain-end censoring, every candidate and all nearest-support ties.
The 1000 m diagnostics remain deep context. A nearest gradient is not a named
current association or width, and gradients of monthly means are not means
of daily gradients when cell valid-date sets differ.

The combined focused suite passes **22 tests**. Run the new diagnostic after
complete source reconstruction:

```powershell
python analysis/south_indian_paired_profiles.py
python -m pytest analysis/test_south_indian_paired_profiles.py -q
```

All 72 selections must remain in the eventual report. Source acquisition,
report generation, actual profile rendering and atlas integration are still
pending; no new measurement or gap-count reduction is claimed by this declaration.

## Native-cell query adapter prepared

`analysis/south_indian_hydrography_query.py` prepares the future
`hydrography_samples` collection: **23,472 rows**, covering all 12 months,
two depths, 326 latitude nodes and three meridians. Every row retains its
native source indices, full-precision U/V/in-situ-temperature/salinity means,
common sample count, eligibility and missing means. Its owner field is
`investigation_current_id`, with current association and width admission false;
these are model source cells, not a named-current footprint or width sample.

The adapter rejects changed source units/year/grid, repeated months, invalid
counts, missingness inconsistent with the common-calendar threshold and false
association. Its retained-source entry point checks manifest/dependency pins
and exact source JSON/NPZ correspondence. A synthetic full-grid test checks
every coordinate axis and every numeric bit, including negative zero; that
is adapter verification, not validation of the still-incomplete actual source.
The combined focused suite passes **34 tests**.

This module is **not wired into the current atlas bundle**. Main collection
counts remain unchanged. After complete acquisition/reconstruction, generate
the actual rows, add source/query/card links and run exact native/WASM readback
against all 23,472 retained cells. The source-profile browser gate remains
pending. No physical measurement is admitted by preparing the adapter.

## Additional primary-source review: classification support

Acquired the author-deposited Sparrow et al. (1996) original from the UEA
repository and visually read all 15 scanned pages. The printed title, authors,
DOI and pages identify the article despite a different repository title.
Acquisition and paraphrased review are versioned; the copyrighted PDF and
private renders remain ignored. This is an additional source, not a replacement
for the blocked Stramma institutional fixture; that CI bootstrap remains open.

The new review identifies support missing from our present source: criteria
at 100/200 m and subsurface salinity-minimum structure. Neither a raw in-situ
temperature substitution nor interpolation between 15 m and 1000 m can establish
that support. The viewer now states this limit. The new evidence strengthens
the requirement to distinguish nearby flow bands before measuring a named
current; it does not invalidate the retained source as exploratory context.

Existing frozen acquisition/diagnostic protocols and their checksums are
unchanged. Finish their complete results first. Any subsequent depth extension
or thermodynamic conversion requires its own declared support and method.
No compatible published SIOC width was admitted from this paper review.

## Transport retry and regression status

The first pass retained **70/82** responses with 12 socket timeouts. The
second pass retained **77/82**, leaving five repeated timeout failures. Both
processes were collected as terminal before starting the next pass. An
explicit operational declaration now freezes the 77 successful original and
receipt checksums, unchanged source selection, missing five filenames and
helper/protocol hashes before a **180-second** socket-timeout retry. The
original two-worker/20 MB bounds, exact URLs, sampled dates, variable/depth
support, parsers and every scientific check remain unchanged. No original is
replaced, and failures remain in the source record. The packager now retains
this declaration and its dependencies alongside the original source archive.
The longer-timeout process is in progress; full source reconstruction is pending.

Fresh Linux verification at source commit
`4a3a151272853ab986b778007b8b1728180fd181`, run **39779202007**:

- All **33 existing encoded scientific report bytes** reproduce exactly.
  The Kuroshio in-memory diagnostic sees JSON string-key/list versus Python
  integer-key/tuple representation differences; its encoded report and all
  numeric leaves are exact. No producer or gate was changed for that diagnostic.
- The previous Indian SECC source reconstruction passes with 173 checked archive
  members, 82 responses and zero network requests. The NetCDF fixture job passes.
- The offline job fails before tests while acquiring the Stramma1992 original:
  both recorded institutional URLs return HTTP 403. Full tests/browser gates
  have not passed for this source foundation; no overall green status claimed.

After the longer-timeout pass, collect its terminal result and verify preservation
before packaging. Then generate the three products, reproduce them from retained
originals, build the 72-selection view and diagnostic, wire query/card/index
integration, and exercise all actual native cells in native/WASM readback.

## Same-cohort single-date recovery

The longer-timeout pass recovered four more requests, bringing the retained
set to **81 original responses**. The one April query still timed out on a
subsequent isolated attempt. Both processes were collected terminal before the
next transport change. The new single-date declaration freezes all81 raw and
receipt hashes and mechanically expands only that query's six original native
time indices into six single-date requests. Every field, depth and spatial
node is unchanged. The full **363 timestamps** remain in the same order with
no omission or duplicate; the focused suite passes **44 tests**.

The original 82-request selection, unavailable six-date URL and its failures
remain intact. The actual response inventory will be **87 physical originals
covering 82 logical request groups**, if all six new requests succeed. No
concatenated text or invented response is presented as a provider original.
The new pinned compiler checks complete monthly timestamp vectors and reuses
the unchanged common mask/arithmetic/portable-array writer. Its transport
declaration and all original inputs must survive exact offline reconstruction.

```powershell
python analysis/south_indian_hycom_single_date_resume.py declare
python analysis/south_indian_hycom_single_date_resume.py acquire
python analysis/package_south_indian_hycom_hydrography.py package
python analysis/package_south_indian_hycom_hydrography.py reproduce
```

Declaration is one-time and must not be overwritten. Acquisition resumes genuine
missing single-date responses while preserving existing originals. The packager
selects the explicitly declared compiler when this declaration exists. This is
an unchanged-cohort transport recovery, not a smaller source selection or relaxed
numeric gate. Full products, source-profile browser checks and query integration
remain pending. Existing 33 scientific reports and their producers are unchanged.

## Source/results verification milestone

The single-date retry completed successfully. The source now contains **87
genuine physical responses**, covering all82 logical request groups and the
original **363 daily00Z timestamps**. The original larger April URL remains
documented as a failed transport attempt; it has not been synthesized or relabeled
successful. All81 earlier raw/receipt checksums remain unchanged.

- **710,028** common-valid four-field daily samples at the two native levels.
- **23,472** monthly native cells, all meeting the frozen calendar threshold.
- Full source archive: **183 checked members**, including both operational
  declarations, the original selection, acquisition receipts and failure log.
- Exact offline reconstruction passes with **zero network requests** for
  `quality.json`, `monthly.npz` and `monthly-fields.json`.
- Canonical stored NPZ: 802,774 bytes, SHA256
  `7cf2a12b30561d1534737c23e92c672a9a28ed0f4877859fef7dd85fb00db343`.
- Full-precision JSON: 1,978,281 bytes, SHA256
  `161fa7c6db5539d74087af09aae290fa16d7d3041ac9235ad6523cde9e8bb4ef`.
- Original-response ZIP: 9,039,377 bytes, SHA256
  `74ca943139da5885b6654f150f5e06558d72d62c6483857aed39270f74f28677`.
- Actual source JSON/NPZ correspondence and all23,472 query-adapter rows pass.
- All72 diagnostic cases generated under the frozen preflight: 1,230 positive
  eastward-component peak candidates and 3,894 positive salinity-gradient
  maxima. These are unassigned diagnostic events, not named currents/fronts,
  independent observations or admitted widths. All candidates remain available.

The standalone view is available at
`figures/south-indian-hydrography-2013/index.html`. Actual Chrome checks all72
selections, 288 profiles and 23,472 native table rows, plus fixed scales,
missing-path behavior, keyboard controls, permalinks, history, invalid URL
fallback, local links and320px reflow. No automatic raw ZIP/NPZ download occurs.
Desktop/phone renders were inspected. Small phone-axis labels were enlarged;
the repeated final gate requires at least10 CSS pixels for axis text and passes.

This completes source retention/reconstruction and the standalone profile
milestone, **not atlas integration or a physical measurement**. Main native/WASM
collection wiring, full row readback, current-card/index integration and fresh
Linux reconstruction for these new products remain pending. Current width,
length, reference-geometry and canonical identity counts remain unchanged.

## Canonical diagnostic v2 portability correction

Fresh Linux run39791437671 exposed platform-dependent PROJ meridian rounding
in the new v1 diagnostic: 74,168 distance-derived leaves differed, maximum
about1.8e-12km. All33 older scientific reports remained byte exact. The job
stopped at that34th report, before the new source-replay step; its full result
must not be called green.

The original v1 operator, preflight and report remain unchanged. A separate
v2 declaration and operator compute the same WGS84 meridian metric with pinned
70-digit Decimal arithmetic, fixed sine/cosine and eccentricity-series terms,
then one final conversion to binary64. No published numeric value is rounded
to make a test pass; the exact encoded-report byte gate remains mandatory.
Independent curvature quadrature and PROJ accuracy comparisons pass. Those
test tolerances are computational checks, not replay tolerances or physical
measurement uncertainty.

All72 cases retain the same candidate counts, latitude supports, censoring,
native source values, nearest-gradient IDs and false admission flags. Only
distance-derived numbers and version/provenance metadata change. The source
archive, monthly JSON/NPZ, time cohort and earlier scientific artifacts are
unchanged. The focused suite passes **67 tests**. The v2 report is
`research/south-indian-hycom-2013-paired-profile-candidates-v2.json` and replaces
v1 as the canonical34th reconstruction target. Linux exact replay remains
required; no alternative success condition is substituted.
