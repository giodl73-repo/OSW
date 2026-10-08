# Atlantic station context gap batch

## Result

Recovered 17 original CCHDO integrated Dataset summaries (684,251 source
bytes), preserving 4,629 events, source line numbers, station/cast labels,
instruments, navigation codes, raw coordinates, date/time fields and trailing
metadata. The generated audit provides 26 dated cruise sampling maps for 30
published section-span records across eight currents with maps.

Three measurement contexts remain unmapped because the 2007 source prints
2005 dates. The Gulf Stream's 2005 BODC station source remains unrecovered.
The 2018 archive establishes a nominal 24 S section despite Table 1's 19 S
label; this batch records that resolution without admitting the two held-out
widths or fabricating boundary station pairings.

Cruise events are sampling context, not current axes or edges. All 30 context
records retain unresolved boundary pairing and false footprint, state
intersection and annual-series eligibility. Coordinate datum and uncertainty
remain null. Original reported widths, length rankings, frozen release records
and state memberships are unchanged.

## Interface and query support

On seasons.html, a current's Cruise-section spans panel includes a collapsible
sampling map with a measurement selector, OSW equirectangular basemap,
unconnected station points, semantic station table and exact-source query
link. Map projection/fit runs in the shipped Rust WASM cartography engine.
Source bytes load lazily through the integrity-checked Rust index store, with
no direct JSON fallback. The checked index catalog now includes 71 documents.
The browser gate declares 50 checks; registration alone is not a passing gate.

The broad query browser check's stale width-capability expectation was updated
from 29 to 38 and now verifies inclusion of all nine newly sourced owners.
This capability count differs from the 35 owners with inventory measurements;
it must not be presented as new numeric or full-current width coverage.

## Reproduction

```powershell
python analysis/build_atlantic_station_context.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_atlantic_station_context_browser.py
python analysis/test_atlantic_cruise_widths_browser.py
python analysis/test_rust_query_browser.py
python analysis/test_rust_source_query_browser.py
python analysis/test_rust_index_support_browser.py
python analysis/check_almanac_page_coverage.py
```

Set OSW_TEST_BROWSER to an installed supported Chromium executable when needed.
The browser checks use the local checkout server on port 8788. The archive
extractor performs no network reads and requires no new scientific dependency.

## Validation and review

- Six station provenance/parser/scope tests passed.
- All 38 Rust unit tests passed; native and shipped WASM builds succeeded.
- Station browser check passed all 30 exact source joins, 26 map views, four
  explicit gaps, source-query/native parity, 320 px keyboard table scrolling,
  current-switch cleanup, and changed-corpus rejection.
- Existing broad query and Atlantic width browser checks passed.
- All almanac JavaScript syntax checks and all 14 page assignments passed.
- Full offline regression passed: 802 tests and 598 subtests.
- Existing checked source-query browser passed exact native/WASM source equality,
  sharing, downloads, mobile controls and isolated integrity failures.
- Index support browser passed source decisions, 24 display spans, 56 state
  diagnostic joins, all 36 branching samples, owner/layer switching, monthly
  playback/share/keyboard/mobile and unavailable-corpus handling.
- Internal seven-role review: zero P1, three resolved P2 findings, one open
  publication condition. This is not independent scientific admission.

## Publication and remaining core gaps

Branch: codex/atlantic-station-geography; parent width batch 87c4ac432b36223577cd75565a476b5984ab37ae.
Protected main publication remains pending. A parent CI run failed on the
now-fixed stale width count; another failed during external paper acquisition.
This document does not claim passing exact-head CI or mainline coverage.

Next: independently reconcile the 2007 dates, recover the BODC section, map
paper model station indices to archive station/cast identities, and then
review actual current edge geometries. The 89 missing published lengths, 58
unassessed widths and most named-eddy footprints remain core inventory gaps.
