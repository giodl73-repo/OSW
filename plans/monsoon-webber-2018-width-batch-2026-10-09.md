# Monsoon Current: two distinct July 2016 width descriptions

This batch follows draft PR72. The complete unchanged CC BY 4.0 original of
Webber et al. (2018), doi:10.1175/JPO-D-17-0215.1, is retained with attribution,
acquisition receipt, byte count and SHA256. Selected original pages were
visually inspected; no figure was digitized and the study was not reproduced.

## Evidence admitted

- Original PDF p8 reports approximately 300 km for the northward near-surface
  Southwest Monsoon Current near 8 N in July 2016.
- Original p9 describes approximately 150 km **conditional on interpreting a
  subsurface salinity maximum as Arabian Sea origin**. Some water recirculates;
  the paper does not establish a clean separating boundary.
- These are different feature definitions, not endpoints of a 150–300 km range.
  They remain separate scoped descriptions with separate metrics and captions.
- No exact paired edges, numerical width observation dates, fixed depth bounds,
  width uncertainty, annual extrema or repeated monthly widths are extracted.
- Earlier 100–200 km scaling assumptions, ±4 Sv transport uncertainty and a
  110 m model display depth cannot supply those missing width fields.
- The southern Bay of Bengal descriptions do not inherit the existing eastward
  Sri Lanka editorial routes or create an observed current/eddy footprint.

The inventory now has 116 scoped descriptions across 63 of 100 current owners,
28 unassessed owners and six source-reviewed owners without numeric widths.
Monsoon's whole-current width remains unknown. Two pending derived-width
owners and one unresolved Loop diagnostic retain their previous decisions.

## Integration and visualization

Both descriptions appear as separate point graphics in the atlas and seasonal
evidence page, with accessible text, source-inspection links and query access.
Dashboard width evidence uses the same source-bound inventory. Audit, original,
protocol and checker are pinned in the generated query/dashboard artifacts.
Native Rust and WASM reject coherent source/collection mutations against the
approved original extraction, including context erasure and owner reassignment.

Playback now checks eligibility of the selected phase. A descriptive width or
exception cannot start playback of unrelated phases. The existing two Monsoon
editorial route states and eligible New Guinea direction phases still animate.
The navigation regression selects the Monsoon route by its checked identity,
rather than assuming it is dropdown option zero after new evidence is added.
Git declares PDFs binary, and the staged original was verified against the
acquisition checksum without altering its bytes.

## Reproduce

```powershell
python analysis/check_monsoon_webber_widths.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_monsoon_webber_widths_browser.py
python analysis/test_ngcc_seasonal_direction_browser.py
python analysis/test_seasonal_atlas_navigation_browser.py
python analysis/test_rust_collection_coverage_browser.py
python analysis/check_almanac_javascript.py
```

Use the established local server and Chrome configuration. Native and WASM
builds run serially. The new primary original is shipped; its tests require no
provider download. Other historical source fixtures retain their existing
acquisition requirements.

## Publication and remaining scope

This is an internal editorial extraction, not external scientific peer review.
Draft publication is stacked above PR72, separate from CI and mainline.
PR72's push offline job failed during Qiu/Chen paper acquisition after three
connection timeouts; it did not reach code validation. Its companion job was
still running when inspected. No success is inferred from elapsed time.

The full goal remains active: 89 whole-current length gaps, 28 missing editorial
reference routes, annual width/length margins and most named-eddy physical
footprints remain. This batch adds scoped evidence and its visual/query joins.

## Local validation receipt

- Full Python suite: 1,203 tests and 918 subtests passed in 582.94 seconds.
- Native Rust: 41 tests passed; serialized native and WASM builds passed.
- New browser: both separate mobile cards, source-pointer/native parity,
  widths-query parity and six intended native/WASM scope rejections passed.
- Monsoon's two existing editorial route phases still play; its two new width
  descriptions cannot initiate playback. New Guinea direction/exception
  regression passed after requiring an eligible phase to initiate animation.
- All 40 collections passed native/WASM first/last-page and record inspection;
  canonical imports and 240 contextual object map marks remain complete.
- All 49 JavaScript modules, 14 page assignments and whitespace checks passed.
- Source index: 142 documents, 5,466,635 compressed bytes. WASM: 2,178,691 bytes.
  Query bundle: 46,554,906 bytes.
- Atlas/seasonal browser passed: 100 current links, 64 route-card links,
  124 phase deep links, six seasonal atlas round trips, sharing, reset and
  mobile reflow. The route-identity assertion replaced a positional assumption.

PR72 companion CI now confirms native and both Python suite steps passed;
its shipped WASM browser step is still in progress. The separate push failure
is the confirmed Qiu/Chen download timeout described above.
