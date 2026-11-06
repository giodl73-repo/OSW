# Three southern-basin seasonal data sets

Continues branch `codex/current-measurement-gaps` and draft PR83 from f7dbdeb.
No separate gap PR and no merge. The objective remains filling core data gaps
with their required information and visualizations.

## What changed

The existing South Atlantic 30 W, South Pacific 100 W and South Indian 80 E
near-surface component diagnostics now have a separate 1995–2016 climatology
and all 22 yearly monthly results. The preflight freezes the original section
geography, peak windows and thresholds before acquisition. Old 2013 series
remain available independently; no new location was selected from the results.

| Section | Native cells | Original times | Year-month profiles | Resolved climatological months |
| --- | ---: | ---: | ---: | ---: |
| South Atlantic, 30 W | 55 | 1,584 | 264 | 11 / 12 |
| South Pacific, 100 W | 61 | 1,584 | 264 | 12 / 12 |
| South Indian, 80 E | 55 | 1,584 | 264 | 10 / 12 |

There are 270,864 paired source vectors, no missing vector pairs and no unexpected
time gaps. Original returned 2017-01-01 boundary rows remain in the CSVs but are
excluded from the declared period. All overlapping 2013 vectors and monthly
profiles match the independent prior acquisition exactly.

Every yearly nominal section resolves, while three climatological sections do
not. Averaging vectors before measuring a span is a different nonlinear operator
from averaging measured spans. Connected climatological flow may combine jets
or eddies. A broader climatological span does not establish a broader named
current. All profiles, thresholds, brackets and contextual crossing flags remain
available for review. Interannual spread is conditional on the finite results,
not measurement error, a confidence interval or physical annual extrema.

## Data and presentation

The source directory contains original licensed CSVs, metadata and a checksum
receipt. The root data retain yearly and climatological profiles; three derived
documents retain distinct diagnostic IDs and source-year pointers. Three monthly
profile SVGs and one numerical year/month heatmap accompany the tables.

Each actual current atlas card links directly to its climatology. Querying an
owner shows both original and climatological panels. Monthly controls, reduced
motion, local section maps, resolution warnings, source-year/profile queries and
320 px inspectors retain the source scope. The generic inspector distinguishes
these geographic windows from the Indian SECC source-frequency window.

No physical named-current width, whole-current length, footprint, physical annual
range, width rank or state-area intersection is admitted. Current association and
flow-normal boundaries still need independent physical validation.

## Preservation and totals

All 235 earlier samples, 28 diagnostics, 143 width definitions, 75 routes and
canonical scientific arrays compare equal. Seasonal frames are unchanged apart
from the width-inventory receipt. Exactly three dashboard owners change.

Totals: 257 indexed JSON sources, 271 scoped samples, 31 diagnostics, 23 series,
44 collections, 100 canonical current cards and 143 scoped width definitions
across 75 owners. Core physical identification and measurement gaps remain open.

## Reproduce

With the pinned source bytes already present:

```powershell
python analysis/build_southern_basin_oscar_climatology.py
python analysis/build_southern_basin_climatology_figures.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
```

Acquisition is explicit (`--acquire`) and refuses to overwrite its source
directory. Regeneration must agree with the frozen document pins; do not renew
pins merely to accept different data. Do not rebuild executables during tests.

## Verification

Six new reconstruction/averaging tests and 47 Rust tests passed. The dedicated
three-card browser passed manual playback, real inspectors, source-year queries,
native/WASM parity, mobile layout and nine coherent rejection cases. The older
sample and one-year basin browser checks also passed. Four independent figures
were visually reviewed. Complete default suite: 1,424 tests / 1,061 subtests passed in 2,003.17 seconds (33m23s).
All 44 collection UI checks and all 100 current cards / 143 widths pass.
The seven-role internal review approves editorial delivery; independent physical
current identification and dimension admission remain open.


The final verification commands are:

```powershell
python -m pytest -q
python analysis/test_southern_basin_climatology_browser.py
python analysis/test_rust_width_samples.py
python analysis/test_basin_surface_sections_browser.py
python analysis/test_rust_collection_coverage_browser.py
python analysis/test_atlas_inline_width_browser.py
```

Browser checks use `OSW_TEST_BROWSER` pointing to the local Chrome executable
and the existing local server. The older sample browser's assertions verified
271 samples and 24 missing readings; its stale success-message counts were
corrected to derive from the actual data instead of fixed numbers.
