# West Spitsbergen Current: six synoptic stream-tube widths

2026-10-08. Editorial source extraction; scientific admission pending.
Working base: 817683a9a140c431214a46aab3332394409a33ad (draft PR43).

## Original source

Kolås and Fer (2018), *Hydrography, transport and mixing of the West
Spitsbergen Current: the Svalbard Branch in summer 2015*, Ocean Science 14,
1603–1618, doi:10.5194/os-14-1603-2018. Original PDF retained unmodified under
CC BY 4.0 with attribution, acquisition byte count and SHA-256. Original
pages 1603, 1607 and 1611 were rendered and visually inspected; numerical
methods and scope were read from the full article.

Table 2, p.1611, has six width cells:

| Section | Tube 1, 0.04 m/s | 0.02 m/s case | 0.08 m/s case | Tube 2 |
|---|---:|---:|---:|---:|
| A | 24 km | 29 km | 17 km | 24 km |
| B | 21 km | 24 km | 11 km | 61 km |
| C | 35 km | 37 km | 32 km | 10 km |

The two bracketed cases retain their source threshold association; they are
not confidence bounds, observation extrema or seasonal ranges. A1 and A2 use
the same tube; these are six source table cells, not six independent surveys.
Tube 2 constrains approximately 1.3 Sv transport within 10%; that tolerance
does not quantify width uncertainty. Section B is shelf-limited. Section C's
tube 1 offshore boundary uses SADCP because coarse LADCP spacing poorly
resolved the lateral decay. These exceptions remain attached to their sections.

## Rules and identity

The new source-specific protocol supplements the existing width protocol;
the latter's bytes remain unchanged. Preserve the two stream-tube definitions
and section IDs. Do not average or sum them. Width is an along-section span
of a property-defined Atlantic Water stream tube, not a fixed-depth envelope.
The observed AW depth span, comparison velocity layer, geostrophic reference
pressure and smoothing parameters retain their distinct contextual roles.

The cruise ran 12–21 August 2015 and the three sections span approximately
five days. Exact section occupation dates remain unextracted. Cruise dates
are not assigned to each record as its measurement interval; calendar months,
exact width observation dates, fixed layers and geographic edges remain null.
No whole-current width, annual extrema, seasonal playback, width ranking or
occupied footprint is admitted. Study distances along the 500 m isobath are
local heat-budget coordinates, not the whole-current length.

Assign the source's WSC records to the existing `west-spitsbergen` identity.
Do not automatically transfer them to the separate ledger entry
`spitsbergen-atlantic`; resolving that naming relationship remains open.
Canonical length records and identities remain unchanged.

## Integration and visualization

Python validates original PDF/acquisition/protocol receipts, table cells,
threshold mappings, context exclusions and complete inventory copies.
Rust binds each row to the exact compiled source-audit extraction and rejects
coherently rewritten seasonal receipts with invented ranges, layers or playback.
The validator module is included in the engine manifest.

The shared chart appears on the atlas card and evidence inspector. Circles
show tube 1 nominal widths, dashed segments its threshold cases, squares
tube 2 widths. A textual table supplies every value and threshold. The legend
states the non-temporal meaning and shared section-A observation. A direct
query link returns all six full records through the Rust query UI.

Inventory becomes 85 scoped width records across 41 owners, with 52 currents
unassessed. Source index becomes 86 documents. All previous 79 width records
are retained unchanged. Seasonal frame objects retain their contents; their
width-inventory receipt is refreshed. This does not establish full annual
coverage or close the remaining length and eddy footprint gaps.

## Verification

Initial focused tests: two tests and 84 subtests pass. Native/WASM build
passes 40 Rust tests. Syntax checks pass all 40 JavaScript files; 14 pages
retain their validation assignments. Full suite: 829 tests and 913 subtests pass in 258.18 seconds. Source-index
browser passes with 86 exact documents, twelve seasonal snapshots and
native/WASM parity. Atlas snapshot passes with 78 exact source documents,
eighteen loader rejections, 100 current/140 eddy selectors and 63 cards.
The final expanded regional browser passes mobile text/reflow, all six query
records, native/WASM parity, atlas-card navigation and three coherent WSC
scope-rewrite rejections. The mobile chart screenshot was visually inspected.
Initial regional attempts exposed its stale 79-record total and the shared
CSS table minimum width. The expectation is now 85 and the new table
explicitly permits mobile reflow.

Reproduce:

```powershell
python analysis/check_west_spitsbergen_stream_tubes.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_black_sea_regional_width_browser.py
python analysis/test_rust_index_store_browser.py
python analysis/test_rust_atlas_snapshot_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Browser checks use Playwright Chromium or OSW_TEST_BROWSER. Other original
paper fixtures remain separately acquired where licenses prohibit inclusion.
Publication is separate from local verification. PR30 remains open at
78a831d with verified running protected-main jobs; this batch is based on
the subsequent draft PR43.
