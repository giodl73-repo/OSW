# Antilles cruise-span integration

Continuing draft PR #83 and branch `codex/current-measurement-gaps`; no new PR or main merge. Source checkpoint d782c3d retains the original published evidence and six source tests. This integration delivers three scoped transport-selected section spans, not physical whole-current widths.

## Data and provenance

Original Table 2 rows 51-53 report 125, 38, 39 km. Table 1 joins those rows to 1992, 2004, 2011 A05 cruises. Three original CCHDO summaries independently identify those cruise sections and retain 101, 114, 153 compatible dated hydrographic cast positions. The actual western station tracks deviate from nominal 24.5 N. Neither model station boundary pairing nor exact current-edge coordinates are recovered.

The Cape Hatteras phrase in section 3.1.7 remains an unresolved publication wording conflict. Table identity and independent A05 sampling context support the scoped table extraction without using that place name as a geographic endpoint. The third table value 39 km is retained beside the prose's approximate 38 km. No author correction, fully blinded declaration or independent scientific review is claimed.

The table defines a transport-diagnosed station span with density-layer support. Reported depth extents 0-736, 0-758, 0-704 m are not uniform fixed-depth slices. Width error, whole-current width and annual range remain unknown. The three cruises cannot establish seasonal extrema, a width trend, physical map bands or current/state intersections. The earlier 49.4 km fixed transport-domain caution remains in the inventory and beside the new chart.

## Shared delivery

- Inventory candidate: 153 scoped rows / 80 owners, with all 150 prior rows and historical source reviews preserved by value. The source-specific Meinen caution can coexist with later scoped evidence from another paper; it is no longer counted as a current with no numeric scoped record.
- Existing cards, seasonal evidence and query charts use one renderer, independent bars and numeric table. The Antilles chart uses year labels to fit narrow cards; full cruise identifiers, dates and depth context remain in the table and record inspector. No interpolation or seasonal playback is introduced.
- Existing station-context renderer queries the checked Antilles source document and uses Rust cartography for unconnected cast points. It does not substitute these points for model boundary station indices.
- Compiled Rust validates exactly three rows, source/dependency/generator pins and scope fields. Nine native/WASM mutations cover altered values, annual ranges, identity, invented geometry, deleted conflict, missing/duplicate rows and rebound source/original pins. HTTP fixture success is mandatory and every WASM test page is closed after its assertion.
- 316 indexed JSON sources and 86 verified engine dependencies. The query corpus has 45 collections, 42 diagnostics and 153 widths. Only widths, objects and seasonal-route receipts change; no prior diagnostic or scientific geometry changes.

## Verification state

56 Rust unit tests pass (2.40 s); native/WASM builds pass. 63 focused source/inventory/earlier-Atlantic tests and 538 subtests pass (424.92 s). The seven-scene combined width comparison and dashboard caution checks pass (2 tests, 30.17 s). One existing NumPy binary-size warning was emitted; no test failed.

The initial browser run passed cards/seasons/query/source/inspector, all three station contexts, mobile/keyboard/reduced motion and all nine native/WASM corruption cases without automatic original downloads. Visual inspection then found that the old wide chart hid the bars on mobile. A compact Antilles chart and an assertion that the SVG fits the viewport are implemented; its focused browser rerun is pending at this checkpoint.

Preservation proof passes: all 150 earlier width records, both earlier review assessments and all seasonal geometry values unchanged. Four seasonal owners (Davidson, Indian SECC, Monsoon, Somali) refresh only inventory-related source fingerprints; Antilles receives scientific record additions. Earlier 32 Atlantic extraction records remain unchanged; their dedicated browser query now explicitly selects that original source rather than accidentally including the new three-row extension.

The previous clean f3a6bce full suite passed 1,656 tests / 1,099 subtests in 2,268.11 s. It does not cover this integration. A clean combined gate on the committed Antilles integration is still required. Record that result separately before claiming a passing new-head full suite.
