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
