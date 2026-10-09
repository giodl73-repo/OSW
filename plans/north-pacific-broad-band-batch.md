# North Pacific broad combined-flow band

## Source acquisition / page versions

Matthias Tomczak and J. Stuart Godfrey, *Regional Oceanography: An Introduction*,
original Pergamon edition 1994; university-hosted online PDF compilation.
Chapter 8, The Pacific Ocean, printed p125 / PDF p135 has page version
**1.1 March 2005**. Version/history and preface pages carry September 2002 and
earlier dates. The author explicitly describes per-page versioning and a fluid
web edition (PDF p8). Do not assign a single preface date to all chapters.

Original: https://ocg.aori.u-tokyo.ac.jp/member/eoka/documents/Tomczak_Godfrey.pdf

401 pages / **36,625,246 bytes** / SHA256
`35e36f9b834c9c31c2cee64abc36d0c687d71e3d388c2cf1c40bc026e613738b`.
Selected PDF pages **2,7,8,9,134,135,136** visually inspected for versions,
authorship, preface, relevant passage and neighboring current context. This is
not a full book review. No velocity field, map axis or paired width digitized.
Print/classroom uses in the preface do not establish an OSW redistribution
license; original is retained unchanged locally and ignored. Receipt and factual
annotations ship. A fresh registered-helper acquisition reproduced the checksum.
This 36 MB book has an explicit 40 MB cap; all prior fixture caps, source hashes,
format checks, timeouts and retries remain unchanged.

## Qualified description and naming

Printed p125 reports a broad band of eastward flow **more than 2000 km wide**
south of the Alaskan Stream, from 30°N to some 200 km off Alaska. The source
includes Kuroshio and Oyashio continuations in a combined North Pacific definition.
It discusses another convention separating North Pacific south of about 43°N
from Pacific Subarctic flow north of it, questioning persistence of this split
across the basin. This definition context is part of the record, not discarded.

The more-than reference scale remains qualified. Representative width, numerical
uncertainty, rigorous bound, finite interval, paired coordinates, flow-normal
transect, fixed depth and occupation dates are unknown. No 2000 km point or
annual range is admitted. Source geographic prose does not diagnose velocity
edges. The text warns that Figure 8.6 distorts distances at subpolar latitudes;
no map-derived width or buffered footprint is produced.

The neighboring 150–200 km Alaskan Stream span and upper-kilometer transport
context cite Royer/Emery (1987), a different flow and support. That original is
not reviewed here. The Aleutian/Subarctic Current is distinct from the westward
Alaskan Stream in the existing pinned naming audit. No span, layer or dimension
is inherited by Aleutian, Alaska, Kuroshio Extension or Oyashio. Canonical names
and flow-network taxonomy are unchanged. The broad source convention does not
resolve a narrower North Pacific-only width or provide independently additive
dimensions for overlapping named currents.

## Data and visualization

**112 scoped descriptions / 61 currents / 31 unassessed**. This assesses one
new owner for a qualified textbook description; it does not establish 61 full
measured widths. All 111 prior descriptions, other decisions/dashboard entries,
canonical ledger, reference routes and naming audit unchanged. Seasonal frames
refresh only their inventory dependency. Lengths, seasonal geometry and eddy
footprints remain separate outstanding parts of the core-data objective.

Atlas and inspector show a textual broad-band graphic, qualifier, definition,
page version, unknown dimensions and source link. No numeric point, span, width
bar, physical edge locator or seasonal playback. Constraint grammar adds a
scoped broad-band branch; the preceding coastal confinement branch remains
distinct. Python/Rust known-owner identity guards and complete source-row binding
reject coherent scope changes and deleted-context transfers to both a registered
owner (Alaska) and an unregistered one (Aleutian).

Source index grows to 134 documents. The new browser check is registered in the
shipped WASM runner. Internal roles review does not constitute independent
scientific admission or mainline publication.

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
python analysis/test_north_pacific_broad_band_browser.py
python analysis/test_solomon_coastal_confinement_browser.py
python analysis/test_seasonal_atlas_navigation_browser.py
```

Publication: draft above PR68; this batch is not merged to main.

## Executed validation

- Full Python suite: **1140 passed, 918 subtests passed in 456.31 seconds**.
- Rust: **41 tests passed**; native and WASM builds passed.
- WASM: 2,052,960 bytes; query bundle: 46,424,363 bytes.
- Source index: 134 documents, 76,444,175 original JSON bytes,
  5,453,925 compressed bytes.
- North Pacific browser: qualified definition, 320 px mobile reflow,
  inspector/source/query parity and coherent native/WASM mutation rejection passed.
- Solomon confinement browser: both distinct cards and scope guards passed.
- Atlas navigation: 100 current links, 64 route-card links, 120 phase deep links,
  six seasonal round trips, share/update/reset and mobile reflow passed.
- Fresh registered acquisition reproduced the original book bytes and checksum.
- Dependency comparison preserved all 111 previous descriptions, other current
  decisions/dashboard entries, canonical ledger, reference routes and naming audit.
- All 48 JavaScript modules, all 14 page assignments, Python compilation and
  whitespace checks passed. Mobile screenshot visually reviewed.

These are local results. Remote CI and merge status are reported separately.
