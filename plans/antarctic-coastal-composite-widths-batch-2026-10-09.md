# Antarctic Coastal Current composite-width evidence batch

This batch follows draft PR74 / parent `3a20b86`. It uses the final
[Schubert et al. (2021) article](https://doi.org/10.5194/tc-15-4179-2021),
The Cryosphere 15, 4179–4199. The unchanged 21-page CC BY 4.0 original is
11,522,211 bytes, SHA256
`ed082152e25690716393b11210d3a4512b08ecfa4d713ad879d10f625b46a479`.
Selected original pages 1, 4, 5, 11, 12 and 13 were visually inspected.

## Measurement scope

Seven Table 2 widths, east to west: **28.4, 23.8, 75.1, 60.9, 89.8, 160.9
and 111.9 km**. The metric is coastline or ice-shelf face to the offshore
15% depth-integrated velocity edge. The current center is identified by the
maximum gradient of net transport. Geostrophic reference is 400 m; integration
runs from the surface to a variable 34.4 psu isohaline.

These are seven spatial composites from historical seal profiles. No annual
range, fixed depth layer, numerical width error or continuous observation
period is supplied. Table 1 cross-shelf transect lengths are not along-current
lengths. Table 2 depth ranges and transport bootstrap errors are not width
uncertainty. Signed transport and geostrophic velocity diagnostics retain
westward-negative convention and source locators.

Published Table 1 counts show summer dominance in sections 1 and 6. Section 6
has 117 winter and 150 summer profiles, contradicting the prose assertion
that all sections except 1 are winter-dominated. Counts and discrepancy are
retained. Sampling seasons do not become observed width phases.

The evidence concerns the regional Antarctic Coastal Current. It does not
establish equivalence with the Antarctic Slope Current or a new naming alias.
No current edge coordinates, connecting route, physical state intersection,
whole-current width or current length is added.

## Data and presentation

- Width inventory: 124 descriptions across 65 of 100 current owners;
  26 owners remain unassessed. All 117 previous record contents are unchanged.
- One Rust scene supplies query, atlas and evidence-page comparison: shared
  0–175 km axis, seven spatial sections, original properties and query context.
- Figure 3 gives published profile-location geography. The extracted original
  embedded raster has no added marks, recoloring, resampling or geographic
  digitization. It is not a current footprint. Browser verification checks
  image SHA and byte count before displaying it.
- A numbered table preserves width, mean/range depth, signed transport,
  seasonal profile counts, transect/bin lengths and diagnostic velocities.
- The dashboard gains seven scoped-width records. Geometry, time samples and
  observed-velocity capabilities remain zero. Composite playback is disabled.
- Query inspection and audit source pointers expose source values and scope.
  Source index contains 147 documents; native/WASM use identical checked data.
- Group validation requires the complete seven-section inventory; individual
  source guards preserve every reviewed row and inference flag.

## Reproduction

```powershell
# Optional reconstruction of the shipped, credited source figure:
python -m pip install -r requirements-figures.txt
python analysis/build_antarctic_coastal_source_figure.py

python analysis/check_antarctic_coastal_composites.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_antarctic_coastal_composites_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Reuse the established local checkout server on port 8788. Default tests use
pinned local source files; the licensed original and source image ship with
attribution. Raw MEOP profiles and numerical reproduction of geostrophy are
still required for independently reproduced measurements.

## Review and publication

Seven installed functional roles reviewed the batch internally, with 21
findings addressed. Independent scientific admission remains pending.
Publication is a stacked draft above PR74; local checks do not establish
mainline coverage. Parent PR74 runs 37925654527 and 37925668397 both failed
before code validation during older fixture acquisition: the former timed out
on Qiu/Chen after three attempts; the latter received HTTP 403. Both NetCDF
fixture jobs passed. Those terminal states were inspected directly.

The broader goal remains active: 89 missing whole-current published lengths,
28 reference-route gaps, annual dimension margins and most named-eddy physical
footprints remain unresolved. This batch supplies scoped width evidence only.

## Validation receipt

- Complete offline Python suite: **1,230 tests and 918 subtests passed** in
  665.37 seconds. New focused source tests: 14 passed.
- Native Rust: **42 tests passed**; serialized native and WASM builds passed.
- New browser: shared atlas/seasons/query scene, complete seven-section context
  under query pagination, source-index/native parity, keyboard section links,
  320 px reflow, readable fixed-size charts, source image verification and
  corruption rejection passed. Nine coherent native-first fixtures were
  rejected by the same scientific checks in shipped WASM.
- Dashboard: scoped-width indicator is lit; geometry, time samples and observed
  velocity remain unlit. Only this owner's measurement fingerprint changed.
- Existing query browser: native/WASM parity, sharing/export, invalid queries,
  pagination, mobile and integrity failure handling passed.
- All 40 shipped query collections: first/last pages, record inspection,
  complete canonical imports and 240 object map marks passed.
- All 50 JavaScript modules and 14 page validation assignments passed.
- Original Figure 3 reconstruction reproduced the reviewed PNG exactly.
- All 117 previous width records remain content-equal. Every build manifest
  checksum matches the shipped artifacts.
- Source index: 147 documents, 5,475,186 compressed bytes. WASM: 2,311,439 bytes.
  Query bundle: 46,664,621 bytes.

- Navigation: 100 current links, 64 route-card links, 132 phase deep links,
  six seasonal atlas round trips, share/update/reset and mobile reflow passed.
- Seasonal snapshot: four exact source documents, eight loader rejections,
  native/WASM parity, all 100 phase plans and first-load failure handling passed.
- Atlas snapshot: 83 exact source documents, eighteen loader rejections,
  native/WASM parity, 100 current/140 eddy selectors, all 64 cards, mobile and
  optional/unavailable source handling passed.
- A direct link to the unchanged shipped original PDF was added after the
  complete suite; JavaScript syntax and original PDF bytes were verified.

Publication target: `codex/antarctic-coastal-composite-widths`, stacked draft
above `codex/tasman-front-meander-band` / PR74. The draft PR is linked in the
publication update. Remote CI and mainline publication are not claimed.
