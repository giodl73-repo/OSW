# Atlantic 2018 width resolution batch

Parent: 70bdf699e3b3e25a87c7c4f2fc18238025323563 (#34).
Branch: codex/atlantic-2018-width-resolution.

## Data change

Admit publisher Table 2 rows 14 and 32 as editorial source extractions:
Brazil 47 km and Benguela 108 km for cruise 740H20180228, nominal 24 S.
Preserve Table 1's original 19 S cell. The independent CCHDO summary verifies
exact cruise identity and A09.5_24S; source bytes, acquisition and parser hashes
are attached to the nominal-label reconciliation. Width values come only from
the unchanged publisher workbook, not from archive geometry.

The new v2 protocol preserves v1's scope and inference restrictions. All 30
prior cruise measurement records and all 39 other width measurement contents
are exactly unchanged. The extraction receipt and its dependent hashes update.
Current decisions now identify unresolved boundary pairing as the next gate.

The working inventory contains 71 records across the same 35 owners. There are
still 58 unassessed widths, two derived candidates and five reviewed owners
without numeric widths. All 32 cruise spans have separately scoped sampling
maps. No annual ranges, whole-current widths, rankings, footprints or state
intersections are admitted. Width uncertainty remains unreported.

## Source and visual access

Affected cards show the original/corrected label explanation and an independent
cruise archive link. Exact source/query records retain original cells, cruise
windows, layer support and the evidence receipt. Dashboard and native/WASM query
snapshots update together. The source index still contains 73 documents.

## Station mapping investigation

The paper's Data availability statement says inverse solutions can be provided
on request: https://os.copernicus.org/articles/19/1009/2023/.
Public station labels and paper station-range labels do not consistently agree.
Examples: the Pelagia summary's station 34 is at -22.816 degrees east, whereas
Table 2 uses station label 47 as its North Atlantic western limit at -22.8.
The public CTD archive was inspected and contains the same 46 profile identities,
without recovering the unpublished model-index correspondence. No inferred
pairing or state intersection is created from numerical similarity alone.
The availability statement is the evidence limitation, not an authorization to
contact authors. No external messages were sent.

## Reproduction

```powershell
python analysis/build_atlantic_cruise_widths.py --update-inventory
python analysis/build_atlantic_station_context.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_atlantic_cruise_widths_browser.py
python analysis/test_atlantic_station_context_browser.py
python analysis/test_motion_dashboard_browser.py
```

## Validation

- Full offline suite: 810 tests and 598 subtests passed.
- Affected source/width suite: 63 tests and 396 subtests passed.
- All 38 Rust tests passed; native and shipped WASM rebuilt.
- Card/query browser: all 32 records, source windows/layers, primary correction
  link, individual bars, direct record links and native/WASM parity passed.
- Station browser: all 32 exact context joins/maps, corrected timestamps,
  source query, mobile keyboard scrolling and changed-source rejection passed.
  One earlier parallel run timed out during initialization; source hashes and
  fresh page initialization with direct JSON reads blocked were verified, and
  the serialized complete rerun passed. No coverage claim is based on timeout.
- All 39 JavaScript files and all 14 page validation assignments passed.
- Exact comparison with the parent proves prior measurement contents unchanged.
- Dashboard browser passed exact native/WASM parity, all 240 records, coverage
  lights/update isolation, four receipt/projection rejections, navigation,
  keyboard selection, outage retention and mobile layout.
- Internal seven-role review: zero P1, three resolved P2, protected publication
  remains open. Independent scientific review is not implied.

## Publication and remaining scope

Protected main publication and required exact-head CI remain pending. Parent
#34's push check failed during acquisition of an external paper, while its PR
check remained live at the last inspection. Do not restart a live check because
an observation expires. No complete mainline coverage is claimed here.

Remaining core work includes 89 missing published lengths, 58 unassessed widths,
most named-eddy footprints and independently verified current boundary pairing.
