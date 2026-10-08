# Black Sea Rim Current width gap batch

Working branch: `codex/black-sea-rim-width-evidence`, based on the Atlantic
2018 resolution branch. Editorial evidence; independent scientific admission
and protected-main publication remain pending.

## Added evidence and presentation

Korotaev et al. (2011), doi:10.5194/os-7-629-2011, section 3.1, printed page
632, explicitly describes a 40–80 km Rim Current width above the continental
slope. Original text and rendered page were inspected. The unmodified CC BY
3.0 publisher PDF is retained with author attribution, license link and exact
acquisition checksum, under a scoped ignore exception.

The inventory preserves a range-only regional description, null midpoint,
unknown observation window, null fixed measurement layer and null edges.
The adjacent pycnocline depth and seasonal intensity text do not establish a
width layer or annual extrema. No current footprint or physical state join
is added. Existing protocol range rules apply without a new metric definition.

The seasonal inspector now draws an accessible regional-range chart with
endpoints, a zero-based numeric axis, text equivalent and nearby range meaning.
It refreshes Gaspé's existing regional range too. Scalar bars, unsupported
edge locators and seasonal playback remain hidden/unavailable for this record.
The current links to its atlas card and exact Rust/WASM query record.

Dashboard source/measurement fingerprints include the new audit. The Rust
query builder validates the extraction and binds the original PDF checksum;
the separate source index exposes both the audit and acquisition receipt.
No copyrighted closed-license fixture is redistributed.

## Inventory state

- 72 width records for 36 current owners; 57 unassessed owners.
- Two derived-width candidates and five reviewed nonnumeric owners remain.
- All 71 prior width measurement contents exactly match the parent commit.
- 75 source-index documents and all 240 object records remain available.
- No new canonical length, rank, annual envelope, dated eddy footprint or
  current-boundary admission is claimed.

## Validation completed

- Full local suite: **811 tests and 611 subtests passed**, 256.04 seconds.
- Native/WASM build and all **38 Rust unit tests passed**.
- Dedicated Black Sea browser check passed after final heading change:
  endpoints, null midpoint, source link, layer caveat, disabled playback,
  absent annual/edge inference, 320 px reflow, switching cleanup, Gaspé range,
  atlas navigation, all 72 table rows and complete native/WASM query-row parity.
- General Rust query browser check passed: 39 objects with scoped-width
  capability (includes other derived capabilities), joins, pagination, export,
  sharing, invalid queries, integrity failure and mobile layout.
- Dashboard browser passed: exact native/WASM parity, four source/projection
  rejection cases, 240 objects, update lights, keyboard, outage retention/mobile.
- Original source page and desktop/mobile range screenshots visually inspected.
- 39 JavaScript modules pass syntax checking. All 14 page validation assignments
  pass; assignments do not prove all 51 declared browser checks ran this batch.
- Whitespace check passed with Windows CRLF policy.

Reproduction:

```powershell
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_black_sea_regional_width_browser.py
python analysis/test_rust_query_browser.py
python analysis/test_motion_dashboard_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Browser checks require the checkout server on port 8788 and `OSW_TEST_BROWSER`
pointing to the installed browser. The review receipt is
`signals/roles/check/black-sea-rim-width-roles-check-2026-10-07.md`.

## Remaining full-goal work

89 currents still lack published ranked lengths. Regional width evidence is
not complete-current seasonal geometry. Most named eddy footprints, compatible
seasonal dimension series, and physical state membership remain unresolved.
The prior protected-publication stack is still pending. This batch advances
one data gap and its required query/visual support; it does not finish the goal.
