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
