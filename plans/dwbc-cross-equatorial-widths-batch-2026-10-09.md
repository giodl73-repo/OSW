# DWBC cross-equatorial float-composite evidence batch

Parent: draft PR75 / `81fe79c8ed92fe084fb11a0d128f926700604dea`.
Branch: `codex/dwbc-cross-equatorial-widths`.

## Original source and rules

Richardson, P. L. and Schmitz, W. J., Jr. (1993), *Deep Cross-Equatorial
Flow in the Atlantic Measured With SOFAR Floats*, Journal of Geophysical
Research 98(C5), 8371–8387. DOI: https://doi.org/10.1029/93JC00051.
Complete final 17-page original: 1,741,213 bytes, SHA256
`86f96a7853fee735c2ba24fca3ab64cf2232871941e1fc4a46b3b00079c2ce53`.
Fresh author-institution download reproduced those exact bytes. Original
pages 1, 2, 4, 5, 6, 7 and 8 were rendered and visually inspected.

Copyright 1993 American Geophysical Union appears on original p1. The original
is an ignored local fixture; WHOI hosting does not imply a redistribution
license. No original figure copied. Explicit local acquisition is registered
in `analysis/acquire_local_paper_fixtures.py` as `richardson-dwbc-1993`.

Nine rules are frozen in
`plans/dwbc-richardson-float-composite-width-protocol-v1.md`, SHA256
`227d23e678b21f56d6a52eeca56841f677b46f524cb99545d705cfe90ac5a0aa`.
Audit SHA256:
`d3e078458894787b8a812589c48cb96263f2d6a867656840e173410f73712515`.

## Measurement and auxiliary source data

One approximate **100 km** regional upper-core DWBC width between zero-velocity
points in a composite along-boundary velocity profile. Coordinates are distance
seaward of the 1800 m depth contour, with parallel/normal velocity components.
Ten-kilometre bins are averaging support, not width error. Nominal 1800 m floats
lost active depth control and pressure/temperature reporting; estimated sinking
about 230 m over 21 months means no fixed width layer is admitted.

All four original Table 2 rows (PDF p8 / printed 8378) remain auxiliary data
inside that one width record:

| Period | Floats in current | Observations | Individual peak cm/s | Maximum bin average ±SE cm/s | Transport per unit depth ±SE (10³ m²/s) | Total Sv |
|---|---:|---:|---:|---:|---:|---:|
| Composite Jan 1989–Oct 1990 | 8 | 500 | 50–60 | 26 ±5 | 14 ±3 | 15 |
| Jan 1989–Oct 1989 | 4 | 124 | 50–60 | 39 ±5 | 23 ±4 | Not supplied |
| Nov 1989–Apr 1990 | 3 | 188 | 40–50 | 30 ±4 | 16 ±3 | Not supplied |
| May 1990–Oct 1990 | 3 | 177 | 30–40 | 19 ±6 | 8 ±2 | Not supplied |

The composite overlaps the unequal subsets. All rows repeat 100 km, but no
independently tracked width edges or constant annual width is inferred.
Table 2's domain 2 S–12 N west of 43 W differs from section 3.2's 0–7 N /
12-month description. Subsets total 489 observations rather than composite
500; no reconciliation or missing observations invented. Float counts overlap.
Figure 6's larger regional observation population remains separate.

Table 2's first-subset footnote says current samples were January–March 1989,
with an offshore 90–130 km data gap; width/transport could be larger and transport
underestimated. Those gap endpoints are not a width interval. Figure 4's absence
of floats in the boundary current April–December 1989 does not establish absence
of the current. Source warns that sparse-sample time-variation conclusions are
somewhat subjective.

Velocity and transport standard errors do not supply width uncertainty. Table 2
rounds composite transport per unit depth to 14 ±3; prose gives 13.8 and an
alternative subset-based SE about 4. Total 15 Sv rounds 14.7 Sv, coupling floats
with an independent mooring and an assumed elliptical profile over 900–2800 m.
That integration range is not the width layer. No subset Sv inferred.

## Data and visualization

- Inventory: **125 scoped width records across 66 of 100 current owners**;
  25 owners unassessed. All 124 previous width records remain unchanged.
- One checked Rust scene supplies atlas, query and evidence pages: width point
  without width-error whiskers; two four-row diagnostic charts with reported
  speed/transport standard errors; full source table and qualifications.
- OSW equirectangular map uses Figure 2 longitude/latitude bounds only:
  −55 to −10 longitude, −5 to 15 latitude. This is study viewport context,
  without reconstructed trajectories, current axis or edges. The existing North
  Atlantic reference reach is separate. No physical current footprint or state
  intersection is added.
- Global width queries retain both coastal and DWBC comparisons even when the
  first result page contains one row. Auxiliary data stays source context rather
  than a newly ingested velocity-series collection.
- Mobile charts and table use local keyboard-focusable horizontal scrolling,
  explicit instructions, readable text and source links. Width ~100 km remains
  visible in the heading even when the point requires scrolling.
- Dashboard gains one scoped-width record. Reference route remains one;
  geometry, observed velocity and time samples remain zero. Only this current's
  measurement fingerprint changes. No seasonal playback or annual margins added.
- Source index: **149 documents**. Audit and acquisition source inspection
  use the same indexed records in native Rust and WASM.

## Reproduction

```powershell
# Explicit hydration of ignored originals if absent:
python analysis/acquire_local_paper_fixtures.py
python analysis/check_dwbc_float_composite.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_dwbc_float_composite_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Use the established checkout server on port 8788 for browser tests. Local default
tests remain offline once original fixtures are hydrated. Raw float records,
changing depths and original binning are not reprocessed by this batch.

An Abaco lead, Bryden et al. (2005), DOI 10.1357/0022240053693806, was not admitted:
the Yale original download returned HTTP 403, and NORA lists no repository full
text. Abstract-only instantaneous/mean scales do not pass full-original scope
review. No Abaco width or relationship was inferred from that abstract.

## Review and publication

Seven installed roles reviewed 21 findings internally; their resolutions are
recorded in the accompanying roles-check. Independent scientific admission
remains pending. This batch is a stacked draft above PR75; local validation
does not establish mainline coverage.

Parent PR75 terminal runs inspected: 37930512297 failed with HTTP 403 during
older paper acquisition; 37930545012 failed after three Qiu/Chen download timeout
attempts. Both NetCDF fixture jobs succeeded. Code validation did not run in
those failed paper jobs. Current publication checks are reported separately.

## Validation receipt

- Full offline Python suite: **1,246 tests and 918 subtests passed** in
  652.48 seconds. New focused source checks: 16 passed.
- Native Rust: **43 tests passed**; serialized native and WASM builds passed.
- New browser: shared atlas/seasons/query scene, four source rows, nominal depth
  and sampling cautions, native geography, 320 px reflow, effective readable
  fonts, local scrolling, keyboard record navigation and source-index parity
  passed. Ten coherent native-first fixtures were rejected by the intended
  scientific checks using identical bytes in WASM.
- Prior coastal browser passed, including seven-section comparison, verified
  source image and nine coherent native/WASM rejections.
- Existing query browser passed native/WASM parity, scoped joins, sharing/export,
  invalid queries, pagination, mobile and failed-integrity loading.
- All 40 query collections passed first/last pages, record inspection, complete
  canonical imports and 240 object map marks in the native/WASM UI.
- Navigation passed all 100 current links, 64 route-card links, 133 evidence
  phase deep links, six seasonal atlas round trips, share/update/reset and
  mobile reflow.
- Seasonal snapshot passed four exact source documents, eight loader rejections,
  native/WASM parity, all 100 phase plans and unavailable/invalid first loads.
- Atlas snapshot passed 83 exact source documents, eighteen loader rejections,
  native/WASM parity, 100 current/140 eddy selectors, all 64 cards, mobile and
  optional/unavailable source handling.
- Dashboard scoped-width indicator lit; time-sample and observed-velocity
  indicators unlit. Only DWBC fingerprint changes among 240 objects.
- All 124 previous width records are content-equal; all engine manifest hashes
  match shipped artifacts; original fixture remains ignored.
- **51 JavaScript modules** and **14 page validation assignments** pass.
- Source index: 149 documents, 5,480,178 compressed bytes. WASM: 2,344,042 bytes.
  Query bundle: 46,685,019 bytes.

Publication target: `codex/dwbc-cross-equatorial-widths`, stacked draft above
`codex/antarctic-coastal-composite-widths` / PR75. The draft and current remote
checks are linked in the publication update; no mainline release is claimed.

The broader goal remains active: 89 missing whole-current published lengths,
28 reference-route geometry gaps, annual dimension margins and most named-eddy
physical footprints remain unresolved. This batch adds scoped source evidence.
