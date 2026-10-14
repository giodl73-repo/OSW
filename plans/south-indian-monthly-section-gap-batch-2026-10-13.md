# South Indian monthly section gap batch

Continuing draft PR #83 on `codex/current-measurement-gaps`. All current gap
work accumulates here, without separate PRs for individual measurements.

## Result

Acquired the original OSCAR 2017.0 vector section at 80 E, 48–30 S, for
2013: 72 archived dates, 55 native cells each, 3,960 complete velocity pairs.
The provider CSV is 343,929 bytes, SHA256
`3be6749ea5b6b6a96cec1e2b8825c7df9b42f7f67db6381415f07d5708ac5b3d`.
The exact query, per-file acquisition time, license and source bytes accompany
the parsed inventory. Existing metadata and three original CSVs are unchanged.

The section, 43–37 S peak-search window and operator were declared before
acquisition. The twelve monthly means yield local half-peak eastward component
spans of about 120–180 km. Six nominal spans cover fewer than four native grid
spacings; June's peak is at the search-window edge. All three threshold scenarios
and boundary brackets remain available for each month. Unknown measurement
uncertainty stays null. These are spans of monthly-mean profiles, not averages
of instantaneous widths, a climatology, annual extrema or confidence intervals.

Stramma (1992), DOI 10.1175/1520-0485(1992)022<0421:TSIOC>2.0.CO;2,
published abstract identifies the SIOC near 40 S. Stramma and Lutjeharms
(1997), DOI 10.1029/96JC03455, section 3.2 and Figure 7, supplies historical
upper-1000 m geography and the eastern split near 90 E. The existing pinned
identity audit supplies those contexts; it does not establish correspondence
with a 2013 surface peak. ACC, northern frontal bands and eddies remain
competing associations. This batch makes no current-width admission.

## Data, query and visual integration

The width worklist moves South Indian from unassessed to section diagnostic /
current width unresolved. There are now 16 unassessed owners and five owners
with unresolved section diagnostics. Published scoped evidence remains
132 records across 71 owners; all 100 canonical identities, 11 ranked lengths,
89 length gaps and 73 reference-route candidates remain unchanged.

The existing Rust/WASM sample query, section endpoint map, chart, monthly
inspection and complete profile sheet now cover South Indian. The dashboard
links directly to its twelve monthly readings. The complete source corpus
becomes 201 JSON documents; query samples become 175, including 48 basin
section samples. No current polygon, tracked map animation, OSW state join
or NASA identification is inferred from local section boundaries.

Protocol v1.1 adds the eastern-longitude section. The original three source
queries, timestamp vectors, profiles, monthly numerical results and figures
remain unchanged. Four shared dependency hashes are renewed in their reports:
source inventory, configuration, protocol and acquisition code. Their three
dashboard fingerprints legitimately change because of the new provenance;
South Indian's changes for the new data. Other owner fingerprints and all
observation dates are unchanged. The seasonal route file refreshes only its
width-inventory checksum, with identical route frames.

## Reproduction and review

Run acquisition verification, span and figure builders, width checks, dashboard,
index and query builders, then the serialized Rust engine builder. Use the
browser tests with the stable final engine; run the complete default offline
suite with the repository publication-temp directory. Exact provider originals
are checked locally; acquisition is explicit and not needed by default tests.

Internal review uses CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL and LOGBOOK.
It assesses editorial diagnostic publication, not independent scientific
approval. Final gate results are appended after execution.

Run these generation commands in order, after verifying the local original
paper fixtures with `python analysis/acquire_local_paper_fixtures.py`:

```powershell
python analysis/acquire_basin_surface_sections.py
python analysis/build_basin_surface_section_spans.py
python analysis/build_basin_surface_section_figures.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
$env:TEMP='C:\src\OSW\.pytest_cache\publication-temp'
$env:TMP=$env:TEMP
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_basin_surface_sections_browser.py
python analysis/test_rust_width_samples.py
python analysis/test_rust_index_store_browser.py
```

The browser checks use the existing static server on localhost:8788. Explicit
live acquisition is separate from verification of the retained provider bytes.

## Final gate receipt

Complete offline suite: **1,332 tests and 944 subtests passed in 1278.92 seconds (21m18s).** All 46 Rust tests and locked native/WASM builds passed. The earlier sample browser retained all 127 original samples and five missing readings.

After the full suite, restored the original CRLF in two inventory files without changing any JSON values or route frames; refreshed their dependency hashes and rebuilt the final artifacts. Final browser checks passed all four contexts / 48 monthly samples, keyboard inspection, 320 px reflow, five native and three WASM rejection cases. Final index-store check passed all 201 exact documents, 12 seasonal snapshots, independent NOAA oracle, native/WASM parity and checked-input failures. All 61 engine pins and 201 source pins match final workspace bytes. Profile sheet and mobile capture were visually inspected. All 30 staged files match the workspace exactly; whitespace gate passed.

Editorial publication conditions are satisfied. Named-current association, flow-normal width, effective resolution, whole-current representativeness and annual extrema remain unresolved scientific gates. Prior-head remote run 38489198298 failed before tests when Melet source bytes differed from the original pin; local original fixture verification passed all 30 originals. No source edition or pin was substituted.
