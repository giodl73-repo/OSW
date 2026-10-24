# Angola: complete native Nansen source sections

Continuing branch `codex/current-measurement-gaps`, draft PR83. Frozen source-method commit469160f precedes actual array processing. This is exploratory: provider indexes, all NetCDF headers and selected thesis methods were inspected before declaration; sample values and width statistics were not.

## Source gap filled

PANGAEA.868683 had previously been a source lead. The complete licensed original EAF_Nansen archive and provider index are now retained with acquisition metadata and hashes. It contains11 native ADCP section files and one separate CTD file. The inventory covers all6148 velocity profiles and1022160 cells per component (2044320 U/V cells including missing values). It preserves all native time, position, depth and velocity arrays, both120/240-bin depth grids, ordering, signed finite zeros and NaNs as explicit nulls. No profiles are silently discarded or missing cells filled.

The unmodified5,131,290-byte archive and index are CC-BY-3.0, credited to Kopte, Tchipalanga, Macueria and Ostrowski (2016), doi:10.1594/PANGAEA.868683. Derived JSON/gzip files are separately labelled. The dedicated source report and all eleven field files reproduce byte for byte locally.

The author's institutional thesis original was also recovered (151 pages; SHA25625b5d8aefb9ab6fd6485bbc850ba41d8791ce76df337d81a01e6afd61b954fe3). Only selected methods pages36/37/39 (printed20/21/23) were visually inspected. Original PDF and renders remain private; public metadata and factual paraphrases identify precisely what was reviewed. Publisher retrieval returned403; no publisher-original or full-thesis review claim is made.

## Scientific boundary

The11 Nansen sections are nominally near12S, separate from the two Meteor sections and moorings near11S. The published transport reconstruction rearranges sections to reference bathymetry and fills gaps using model-assisted patterns. This batch preserves native observations without that reconstruction. The15-90km by30-200m transport integration box is not a75km current width.

No alongshore rotation, time filtering, vertical or horizontal interpolation, current-edge extraction, annual range, geometry, state join, whole-current length or canonical Angola identity is admitted. Source quality flags and an explicit time zone/calendar are absent in these native files. Finite values are not independently quality approved. Raw TIME and its original epoch remain visible without an invented UTC conversion. Uneven ship occupations are not a complete annual cycle.

## Visual and query delivery

The standalone source view selects all11 sections and both native velocity variables. It uses a fixed range across sections for each variable, patterned missing cells, native profile/bin axes and exact cell tables, with keyboard controls and shareable cell URLs. Profile index is not offshore distance. Derived files load on demand; provider originals are only downloaded on explicit navigation.

The main source catalogue, diagnostic query and dashboard pending-current source list are being integrated. Eleven lossless JSON transport mirrors preserve the exact decoded bytes of the frozen field products, allowing the Rust/WASM source store to query every native variable and cell. A separate mirror manifest binds their hashes; no scientific transformation is introduced. The diagnostic has a proposed_current_id and null current/entity IDs; it must not invent an accepted current object or measurement capability. All prior rows, original sources and frozen scientific inputs must remain unchanged. Local v2 data integration is verified: 522 source documents, 106816 query rows across 52 collections, 64 diagnostics, and 633 engine pins. All106815 previous rows,501 previous source descriptors/bytes and570 protected inputs remain exact. Widths170, reference routes78 and hydrography samples46944 are unchanged. The v2 generated WASM is 47,993,601 bytes. Publication and fresh remote verification remain pending.

## Checks and retained failures

12 synthetic kernel/schema checks were frozen before actual array processing. One independent actual-source test compares every coordinate, velocity and mask to the original NetCDF files, including signed zeros:13 focused tests pass. Two additional transport-mirror checks verify complete decoded-byte equality and rejection of changed bytes; the combined15-test gate passed in1.37 seconds. The source-view browser compares every complete field,22 variable render cases, selected cells, keyboard/permalink, invalid URLs, corrupt payload rejection, no automatic original downloads and320px reflow.

A local-server absence caused the first browser invocation to fail; the server was restarted. A hidden details text accessor was corrected in the test. A later phone check exposed a long provider filename overflowing320px; short section IDs and wrapping full filenames fix it. The delivery build was intentionally terminated before changing its consumed view inputs, its log retained, and is rerunning against the corrected view. No frozen scientific producer, protocol, preflight or numerical report was changed to make these checks pass.

The clean full offline run at f49cf4d was intentionally stopped at approximately23% when the user requested reduced computer load. No failures had been emitted at that point; this is an incomplete run, not a pass. It predates this batch and cannot establish full coverage here. Prior36-report Linux reproduction, conformance and the full source/browser job pass at af7e317. Fresh37-report replay, actual source/query UI CI and a complete successor offline gate remain required. Remote offline original-paper acquisition still returns403 before tests. No overall-green or release claim.

## Reproduce

```
python analysis/angola_nansen_portable_sections_v2.py check
python -m pytest analysis/test_angola_nansen_native_sections.py analysis/test_angola_nansen_native_report.py analysis/test_angola_nansen_query_mirrors.py analysis/test_angola_nansen_portable_sections_v2.py analysis/test_angola_nansen_portable_report.py -q
python analysis/prepare_angola_query_sources.py
python analysis/build_angola_nansen_sections_view.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_angola_nansen_sections_browser.py
python analysis/test_angola_nansen_query_browser.py
python analysis/inspect_scientific_reproduction.py
```

Set OSW_TEST_BROWSER to the installed Chromium path for direct browser invocations; the regular browser runner manages it in CI. Run from the repository with its local HTTP server. Build mode refuses existing scientific products; use check, retain failures and version any correction.

## Terminal local verification

The serial delivery pipeline and subsequent serial checks both passed. Native Rust:134 tests. Independent source and mirror checks:15 tests. The standalone browser verifies all11 complete fields and22 variable render cases, masks, cell values, keyboard/permalink, invalid URLs, corrupt-payload clearing and320px layout. The main query browser verifies all2044320 velocity cells through the shipped source store, native/WASM equality for both120/240 depth grids, absence of a canonical Angola object, and keyboard dashboard → source view → exact cell query navigation. No automatic provider-original downloads occurred. The final phone rendering was visually inspected. These are local focused results; the full regression and fresh37-report/UI CI remain open.

## Resource sequencing

Run one heavy local job at a time. The delivery order is dashboard, source index, query packet, then Rust/WASM engine. Each child runs at below-normal priority on one logical CPU, with one Cargo and numerical-library worker. Verification follows only after the build terminates: preservation, focused source tests, standalone source browser, then main query browser. Native CLI expectations finish before Chromium starts. The full regression remains stopped during this batch and must run alone as the eventual final batch gate. No build/browser/full-suite overlap.

## Next measurement work

Define and freeze a separate, consistent cross-current width extraction using the observed coordinates, depth/time support and missing-data coverage. Preserve unresolved shoreward/offshore edges. Do not infer a width from the transport box, model-filled reconstruction or the finite sample extent. Review Angola identity separately before attaching its observations or widths to an accepted catalogue object.

## Fresh CI dependency correction

At9e95a3b the conformance job failed during collection because its smaller dependency environment omitted netCDF4. All three new Angola test modules were affected. Add the same netCDF4==1.7.4 pin already used by scientific reconstruction and label the15 Angola checks separately from REDSOX. This changes CI setup only; frozen methods, tests, source arrays, numerical reports and all engine/source pins remain unchanged. The separate offline job again fails during checksum-pinned original-paper acquisition with HTTP403 before its tests. Fresh successful conformance is still required.

## Cross-platform compressed-field replay investigation

Linux replay at9e95a3b rejects the first frozen gzip field before comparing the report. The engine build rejects the same bytes. All36 previous report replays remain exact. A read-only diagnostic now compares every complete decoded field, compressed headers/hashes/sizes, and the full report after isolating only compressed SHA256/byte-length fields. It preserves the strict failing replay gate, v1 compiler/protocol/preflight and all retained products. Local Windows replay is exact in both compressed and decoded bytes; the Linux classification is pending. No compressed-only or numerical-difference conclusion is admitted before that evidence. Any transport correction requires a separate version, retained v1 products and equivalent complete array checks.

## Verified classification and prospective v2 correction

Linux job120484726051 atbe89af8 confirms all11 complete decoded fields exact and all report metadata exact except compressed hashes/sizes. Headers are equal; the first payload difference is offset38. Windows uses zlib-ng1.3.1 and Linux zlib1.3. The complete diagnostic is retained publicly. The original strict v1 replay failure remains reproducible and the frozen v1 producer/protocol/preflight/report/fields remain unchanged.

Freeze commit8ea807a declares an identity-JSON transport v2 before compilation. It compares every native decoded byte, all report metadata, all retained gzip hashes and the existing query mirrors, then points the new report directly at the existing exact JSON files. No new full-size field copies, numeric transformations or dimension admissions. Fourteen prospective synthetic checks and one independent actual-report chain check pass locally, alongside the15 previous source checks. V2 report build/check pass locally. Active-edition reconstruction now targets v2 explicitly; v1 history and its strict-failure diagnostic remain available. Main view/source/query integration is being rebuilt and is not yet verified or published.

The original Thompson2009 Labrador article was separately recovered from its institutional repository and selected pages6-7 visually inspected. A new custody follow-up records its exact hash and retains the earlier source-scope audit unchanged. No Labrador length calculation or new width is admitted in this increment.

Historical strict v1 check: `python analysis/angola_nansen_native_sections.py check`. It remains compression-library dependent and is intentionally not claimed as a portable success. Use the explicit v2 command above for the active source inventory.

V2 preservation is anchored to f49cf4d: all106815 pre-Angola query rows,501 original source descriptors/bytes and570 protected inputs remain exact. Additionally32 v1 source/method/report/gzip/JSON paths match Git9e95a3b exactly. The sole Angola diagnostic now explicitly references the v2 edition; v1 numerical records are retained. The active coverage remains13 rank-eligible published lengths among102 assessments, with70 having no numeric length and89 unranked overall. This transport correction does not reduce those measurement gaps.

## Terminal v2 local delivery

The corrected serial pipeline and all subsequent serial checks passed. Native Rust:134 tests. Source checks:30 tests. Standalone browser: all11 complete fields,22 variable cases, current v2 inventory/download links, retained-v1 decoded-byte equality, keyboard/permalink, corruption clearing and320px reflow. Main browser: every native field through the shipped WASM source store,2044320 velocity cells including missing values, both120/240-bin native/WASM parity cases, and keyboard dashboard-to-view-to-cell-query navigation. No automatic provider originals downloaded. Final phone rendering visually inspected. All source and engine pins match the working files. Fresh Linux v2 byte-exact report/UI evidence and the broad offline gate remain open; no overall-green or program-complete claim.

Staged-byte proof: all956 unique engine/source Git index blobs match the633 engine pins and522 source descriptors. Diff whitespace checks pass. Publication proceeds only to the continuing draft PR83; fresh remote v2 results remain pending.
