# Tasman Front occupied-band evidence batch

This follows draft PR73. The source is the original 1980 RAN Research
Laboratory interim report, Internal Technical Memorandum 3/80, retained by
[NASA NTRS](https://ntrs.nasa.gov/api/citations/19800022345/downloads/19800022345.pdf).
The complete 73-page microfiche reproduction is locally pinned at 6,188,044
bytes and SHA256 `6bcc15747fc95fa9aa4e35767d2a713425c73ab4529434240a77c04d543a4aaa`.
Original selected pages were visually inspected; no figure was copied or
digitized and no experiment was reproduced.

## Scope and taxonomy

Original PDF p27 / printed p23 explicitly describes an approximately 600 km
zonal band occupied by a meandering front extending across the Tasman Sea.
This supports `author_reported_meander_occupied_band_breadth`, a distinct
measurement metric. It is neither an individual jet width nor the thickness
of a thermal transition. Existing 2019 continuity qualifications remain in the
atlas scope review; historical band breadth does not establish a persistent
narrow jet or a simultaneous connecting axis.

Original p26 / printed p22 discusses a maximum dynamical breadth of 600 or
700 km. That is contextual, not a 600–700 km interval. Original p15 / printed
p11 describes approximately 30 km surface thermal fronts and up to 120 km in
the thermocline around particular anticyclonic structures. They do not replace
this band or imply seasonal width extrema. The earlier postulated 500 km flow
is also excluded from a pooled range.

No paired edges, cutoff, fixed numerical layer, width observation dates,
uncertainty, annual extrema, route buffer or current/eddy footprint is admitted.
The approximate band-center description is geographic context, not a polygon.
All prior width records remain unchanged; Tasman Front gains one scoped
description and its whole-current width stays null.

## Data, query and visualization

- Width inventory: 117 descriptions across 64 of 100 current owners; 27 owners
  remain unassessed. Other pending and reviewed decisions are unchanged.
- Separate point graphic in the atlas and seasonal evidence page, with the band
  definition, historical scope, uncertainty and source inspector beside it.
- Dashboard width evidence, query record, source index and Rust/WASM receipts
  share the same source-bound row. Geometry and time coverage stay absent.
- Playback stays disabled for this historical synthesis. No dated route is added.
- New original-source guard freezes the extraction and rejects changes in both
  native and WASM, including erased context, transferred ownership, substituted
  thermal width and generic jet-width relabeling.

## Source acquisition and reproduction

The original prints Commonwealth of Australia copyright. NASA hosting is not
treated as redistribution permission. Only the factual extraction, protocol
and acquisition receipt are versioned; the original PDF remains ignored.
The explicit acquisition workflow includes the new original. A fresh NASA
download was verified against the same pinned checksum before publication.

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/check_tasman_front_band.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_tasman_front_band_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Use the established local server and Chrome configuration. Builds are serialized.
Acquisition is an explicit network step; default tests use pinned local originals.

## Review and publication

Seven installed functional roles reviewed the batch internally. External
scientific review, terminal remote CI and mainline publication remain separate.
PR73's push job failed before validation while acquiring the older Qiu/Chen
paper after three connection timeouts. Its companion was still running at
inspection; both NetCDF fixture jobs passed. No remote success is inferred.

The full goal remains active. Twenty-eight reference-route gaps, 89 missing
whole-current published length estimates, annual dimension margins and most
named-eddy footprints remain unresolved. Adding this historical band does not
reduce those geometry or time gaps.

## Local validation receipt

- Full Python suite: 1,216 tests and 918 subtests passed in 579.69 seconds.
- Native Rust: 41 tests passed; serialized native and WASM builds passed.
- New browser: mobile point graphic, alternative text, source-inspector/native
  parity, widths-query parity and eight native-first coherent WASM rejections
  passed. Thermal-width substitution and jet-metric relabeling are explicit cases.
- Dashboard browser: native/WASM selections agree. Width evidence lights up;
  geometry and time evidence stay unlit. Mobile card opens the exact atlas card.
- Original reacquisition from NASA matched pinned SHA and byte count.
- All 116 preceding width record contents are unchanged.
- All 49 JavaScript files and 14 page assignments passed their checks.
- Source index: 144 documents, 5,468,397 compressed bytes. WASM: 2,185,787 bytes.
  Query bundle: 46,567,011 bytes.
- A duplicated word in checker error text was cleaned up after the full suite;
  generated receipts were refreshed and all 13 focused source tests passed. The scientific
  audit, measurement records and rendering code were unchanged by that cleanup.

Remote CI and mainline remain separate publication conditions. The full core
coverage goal is still active.
