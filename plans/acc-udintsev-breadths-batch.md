# ACC Udintsev distinct breadths

## Original and method

Park et al. (2019), JGR Oceans 124, 4511-4528,
doi:10.1029/2019JC015024. Institutional original:
https://repository.kopri.re.kr/bitstream/201206/10947/1/2019-0214.pdf

18 pages / 10,224,104 bytes / SHA256
`a9fbd7d9f0094c4ab94f6434b4428ad7000e68cb6cc74c53d550eadbe94253ef`.
Selected PDF pages 1,3,5,6,7,8,16,17 visually reviewed, including Figure 5.
No full numerical reproduction or source-field/edge digitization claimed.
CC BY-NC-ND printed on p1; original remains unchanged locally and ignored.
Receipt and attributed factual scope annotations ship.

Detailed printed p4517 separates approximately **170 km SAF-SACCF separation**
from approximately **500 km NB-SB breadth** at 144 degrees W, Udintsev entrance.
The abstract/key point uses compressed ACC width phrasing for 170 km. The two
quantities are retained separately with explicit metric names and contour pairs.
Figure 5 plots meridional separation from PF, not a recovered flow-normal transect.

CNES-CLS18 MDT reference period 1993-2012 is distinct from assimilation spanning
1993-2016, Argo validation 2001-2017, 2016/2017 cruises and synthetic-particle months.
No numerical uncertainty, exact paired coordinates, fixed-depth slab, pooled
170-500 km range, seasonal extrema/playback, route buffer, ranking or physical
state intersection inferred. Drake's 270 km comparison stays separate.

## Implementation and scope

**114 scoped descriptions / 62 current owners / 30 unassessed**. This adds
local contour-defined quantities; it does not establish 62 whole-current widths.
All 112 preceding descriptions, other current decisions/dashboard entries,
canonical ledger/routes and naming audit unchanged. Seasonal frames refresh only
their inventory dependency. Length, seasonal geometry and named eddy footprint
work remain within the full core-data objective.

Separate atlas graphics and inspector titles retain approximate values, contours,
reference period and unresolved supports. Exact source pointers, native/query
parity and coherent native/WASM identity/scope rejection tested. Source index
now has 136 documents. New browser check registered in shipped WASM runner.

Internal seven-role review is editorial review, not independent scientific review.
Publication is a stacked draft above PR69, not a merge to main.

## Rendering correction discovered in remote CI

PR67 push run 37908835254 failed the existing Atlantic EUC section-properties
SVG text-containment assertion in the Linux browser. Chart titles and units now
use wrapping HTML headings above each SVG; SVG alternate text explicitly retains
the units. The existing containment assertion is unchanged. Its browser test
passed locally after the correction; remote Linux confirmation remains pending.
Section values, unresolved date conflicts and all source records are unchanged.

## Regeneration

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_acc_udintsev_breadths_browser.py
python analysis/test_seasonal_atlas_navigation_browser.py
```

## Executed validation

- 41 Rust tests and native/WASM builds passed.
- WASM 2,066,944 bytes; query bundle 46,450,483 bytes.
- Source index: 136 documents, 76,458,260 original JSON bytes,
  5,455,727 compressed bytes.
- Fresh registered acquisition reproduced the 10,224,104-byte original/checksum.
- ACC browser: both 320 px cards, inspector/source/query parity and seven
  coherent native/WASM scope rejections passed. Both screenshots visually reviewed.
- Dependency comparison, all 48 JavaScript modules, all 14 page assignments,
  Python compilation and whitespace checks passed.
- Atlas: 100 current links, 64 route-card links, 122 phase deep links, six seasonal
  round trips, share/update/reset and mobile reflow passed.
- Atlantic EUC section-properties browser passed after the heading correction.

- Full Python suite: **1175 passed, 918 subtests passed in 499.58 seconds**.
- Final ACC browser rerun passed after the Python identity guard and inspector
  encoding correction; seven coherent native/WASM rejections remain enforced.

Remote CI reported separately: PR69 push acquisition timed out at Qiu/Chen;
its first companion attempt failed at GEOMAR HTTP 403. Retry also failed during
fixture acquisition. This does not establish a passing remote test suite.
