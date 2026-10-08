# Norwegian Coastal Current: Halten Bank regional width

2026-10-08. Editorial extraction; scientific and canonical admission pending.

Saetre (1999), *Features of the central Norwegian shelf circulation*,
doi:10.1016/S0278-4343(99)00041-2, Introduction reports 20–30 km for the
coastal current east of Halten Bank, north of 64 N. The publisher-indexed
introduction was inspected. Direct publisher access returned HTTP 403;
the full original article and Fig. 1 have not been inspected. This limitation
is visible beside the chart and retained in the complete query record.

## Measurement rules

The existing protocol's v1.2 regional range rules apply: store [20,30] km,
keep the single value null, and do not infer a midpoint, temporal range or
confidence interval. This is coastal-branch regional prose support, distinct
from the offshore shelf-break branch and the Norwegian Atlantic Current.
Adjacent winter/spring hydrography does not establish width occupation dates.
The >200 km shelf width, 80 km coastal-water extent, 100–150 m Atlantic-water
depth and 40 cm/s drifter display filter do not define this width's boundaries.
Keep geometry, fixed depth, dates and months null. Ranking, annual extrema,
full-width inference and playback remain false. No new metric or aggregation
rule is introduced; the protocol bytes remain unchanged.

## Integration

Source audit binds the complete row and five contextual exclusions. Python
rejects source/branch relabeling and invented boundaries, layers or seasons.
Rust rejects numeric/temporal promotion even after coherent receipt rewriting.
The existing regional chart and atlas card expose the record, source and limits;
chart labels were enlarged for narrow screens. The registered source index
includes the audit. Native/WASM bundles and dashboard were regenerated.

Inventory: 79 scoped records, 40 current owners, 53 unassessed currents.
Source index: 82 documents. Previous 78 measurement rows and six seasonal
frame objects remain unchanged; the frame inventory receipt is rebound.
These counts do not establish whole-current dimensions or seasonal coverage.

## Verification

Final local suite: 824 tests and 745 subtests passed in 281.14 seconds.
Final native/WASM build: 38 Rust tests passed. Expanded regional-range browser
passed 320 px reflow, effective text size, visible source limits, direct atlas
card, complete native/WASM row parity and four coherent-rewrite rejections.
Final mobile screenshot was visually inspected. General query browser passed
43 scoped-capability objects; atlas snapshot passed 78 exact source documents
and 18 loader rejections. Source-index browser passed 82 exact sources and
all twelve seasonal snapshots. All 39 JavaScript syntax checks and fourteen
page assignments pass; page assignments alone are not test results.

The first regional browser attempt failed because its newly generated test
string had an encoding error. It was corrected and final checks rerun.
An optional standalone screenshot diagnostic was interrupted after stalling;
the actual registered browser check completed and supplied the inspected image.
No live server or publication job was restarted. Existing PR30 remains open;
its 0ff10d0 CI run 37749997604 failed on index-support slider keyboard handling
(month 1 to 2 wait), separately from this batch's passing local checks.

Reproduce:

```powershell
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_black_sea_regional_width_browser.py
python analysis/test_rust_query_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Browser checks use Playwright Chromium or OSW_TEST_BROWSER. Original local paper
fixtures are required by other offline tests; acquisition remains separate.
Publication is pending protected-main checks; local passes are separate evidence.
