# Antarctic Slope evidence coverage batch

This follows the M6 velocity ingestion in draft PR71. It connects the approved
local observations to the coverage dashboard and records the missing-width
source review using the original 2024 paper.

## Evidence and data changes

- Complete original: Darelius, Fer, Janout, Daae and Steiger (2024),
  [doi:10.1029/2023JC020666](https://doi.org/10.1029/2023JC020666), CC BY as
  printed on PDF p1. Unchanged 16-page PDF shipped with attribution and SHA.
- Original pp3–4 define the stations and depth bins. Their 5 km and 80 km
  distances are mooring separations. Original p13 uses 10 km as a dynamical
  scale and, separately, a curvature estimate. None provides current width.
- The width inventory moves Antarctic Slope from unassessed to source-reviewed
  without comparable numeric width. Unassessed owners: 30 → 29. Reviews: 5 → 6.
  Numeric coverage remains 114 scoped descriptions across 62 owners.
- Dashboard observed velocity: 61 summaries, comprising 49 monthly means and
  12 equal-year seasonal composites from 16,393 paired source readings at nominal
  228 m. Existing time evidence also lights up; width and geometry do not.
- Latest observation date: 2021-02-13, the released data endpoint. It is not
  the source's publication or acquisition date.
- Source and time fingerprints include the actual dataset and scope review,
  so content changes can trigger the existing update indicators.
- Dashboard, query filters, Beck station coverage, record cards and chart
  navigation use the same Rust source-bound evidence projection.

## Verification correction

The first new coherent browser metadata mutations rebuilt the entire bundle
through JavaScript JSON parsing/stringifying. That altered unrelated scientific
number representations and caused an earlier section binding rejection. They
therefore did not prove the M6 metadata check.

The replacement helper constructs Python fixtures, verifies the intended
native rejection, then supplies exactly those bytes to WASM. Count, date and
depth mutations reject at the M6 checks. The older six M6 record mutations now
use the same helper and require a velocity-specific or missing-collection error.
This corrects the strength of the earlier test evidence without relaxing source
validation or accepting numerically changed bundles.

## Reproduction

```powershell
python analysis/check_antarctic_slope_scope.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_antarctic_slope_coverage_browser.py
python analysis/test_antarctic_slope_m6_velocity_browser.py
python analysis/test_motion_dashboard_browser.py
python analysis/test_rust_collection_coverage_browser.py
```

Use the established local browser/server configuration. New primary data and
paper are licensed, pinned and shipped; their checks need no fresh provider
download. Existing paper fixtures elsewhere in the stack remain separate.

## Unresolved work and publication

Whole-current widths, annual width extrema, current-route geometry gaps,
89 whole-current length gaps and most named-eddy physical footprints remain
unresolved. This batch supplies a source-review decision and the missing
coverage/navigation join; it does not close the broader goal.

Draft publication is above PR71. Local validation, remote CI and mainline
publication are distinct receipts. At initial writing, PR71's two offline jobs
and PR70's companion browser job were confirmed running; neither is presumed
successful or terminal from elapsed time.

## Final local receipt

- Full offline Python suite: 1,183 tests / 918 subtests passed in 510.50 seconds.
- Focused source/coverage tests: all five passed after replacing global-count
  assertions with the owner-specific width decision, allowing unrelated future reviews.
- Native Rust: 41 tests passed; serialized native and WASM builds passed.
- New dashboard browser: native/WASM selected coverage, Beck light, 320 px card,
  actual observation date, chart navigation and three coherent metadata rejections passed.
- Existing M6 browser: all six native-verified source-record mutation cases
  reject at M6 velocity or missing-collection checks; charts/navigation/playback pass.
- Existing dashboard browser: receipt/projection rejections, coverage lights,
  content-based updates, outage retention and mobile layout passed.
- Generic browser: all 40 collections, first/last pages and record inspection passed.
- All 49 JavaScript files, 14 page assignments and whitespace checks passed.
- Source index: 140 documents. WASM: 2,165,443 bytes. Query bundle: 46,529,998 bytes.

Internal roles review retains only the remote CI/publication condition.
