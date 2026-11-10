# Gulf Stream physical width definitions

Continues the existing current-gap branch/draft PR83 from `5d3458b`. Adds two
original-source regional width definitions and their information and visualization.
No new PR, whole-current ranking or merge.

| Definition | Source value | Support | Boundary operator |
| --- | --- | --- | --- |
|1967 transport-float campaign | Author mean135 km; three widths145,140,120 km; finite sample span120–145 km | Complete crossings1,3,4 off Cape Hatteras;30June–5July,11–15July,16–18July1967 | Smoothed, partly extrapolated zero-transport crossings along a fixed135-degree-true baseline; surface to variable local bottom |
| Historical climatology near70 W | About300 km | Isopycnal climatology; archive available April1990; exact local contribution dates unresolved |100/400 dbar pressure contours on sigma-theta26.50, not fixed-depth or velocity boundaries |

The three widths are subordinate occupations of the first record, not three
additional summary records. The mean is source reported, agrees with their
arithmetic mean and is not a fourth occupation. Partial crossing2 has no width.
Neither study supplies width uncertainty, geographic edge pairs or annual limits.
The different definitions do not form a135–300 km temporal range.

## Original source access

- Richardson and Knauss (1971), DOI 10.1016/0011-7471(71)90095-7. Institutional PDF:
  1,242,707 bytes, SHA256 `0bbe9c715e140af51575125c61aeae712912f283f15c1114646bc2b46c1ad31d`.
  Methods, Figure2, zero-boundary discussion, Table2 and conclusion reviewed;
  core pages visually inspected. First source clock timezone is unspecified.
- Lozier, Owens and Curry (1995), DOI 10.1016/0079-6611(95)00013-5. Institutional PDF:
  3,378,622 bytes, SHA256 `daadf0d96ac221ba65f9b70330dd563b26888f8aeacce57c75d23bde8ea0bcd8`.
  Abstract, data support and sigma-theta26.50 section/Figures7–8 reviewed. The
  500 km meander envelope and100 km smoothing scale stay separate contextual facts.

Both originals remain local and ignored. No redistribution license is assigned;
original figures and digitized curves are not packaged. Metadata, attributed
numerical facts and an independent two-panel SVG are published.

## Integration

New records attach to Gulf Stream only. The larger Gulf Stream System and its
17 surface-component diagnostics retain their existing identity and method.
The earlier256 km inverse-model cruise section stays unchanged. All three
definitions are visible on the Gulf Stream atlas card, in the real record
inspector and source queries. The1967 series links directly to its three-row
source table. Seasonal playback stays disabled; geography remains route context.

Totals:145 scoped width definitions /75 owners,260 indexed JSON sources,
32 diagnostics,24 series and44 query collections. Earlier271 width samples,
75 reference routes and canonical scientific arrays are preserved. No new named
current or physically admissible whole-current/annual dimension is counted.

## Reproduce

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/check_gulf_stream_published_widths.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_gulf_stream_published_widths_browser.py
python analysis/test_rust_collection_coverage_browser.py
python analysis/test_atlas_inline_width_browser.py
```

Acquisition is explicit; default tests use pinned local originals. Do not rebuild
executables while tests use them. Browser checks use the existing local server
and `OSW_TEST_BROWSER` pointing to a local Chrome executable.

## CI and source availability

The previous PR workflow38608488326 stopped during fixture acquisition: all
three verified GEOMAR URLs for the older Zenk newsletter returned403. This is
separate from local scientific validation. An inspected NOAA archive copy has
8,150,392 bytes / SHA256 `703b312a2a1169c5823687d4704562b2c8c81becaca561639086a73c40cf64e4`;
it does not match the frozen8,089,173-byte original and was not added as a fallback.

The previous push workflow38608477766 passed acquisition and its complete offline suite, then failed because the Atlantic SEUC browser test hardcoded Windows Chrome on Linux. Twenty-eight browser launchers now honor OSW_TEST_BROWSER (one is in the mainline runner). All28 compile and their executable expressions accept a POSIX override; Atlantic SEUC, Atlantic EUC and component-navigation browser flows pass. The EUC comparison count now comes from the catalog (39), replacing a stale37-row assertion.

No acquisition pin or validation step is relaxed. Provider availability remains
an external risk; new-head CI must be reported separately from the local gates.

## Validation

17 new source tests and47 Rust tests pass. Dedicated browser passes both source
definitions on atlas/seasons/inspectors, three exact occupation records,
native/WASM parity,320 px reflow, no PDF fetches or seasonal playback, and nine
source/admission rejection cases. Independent graphic visually reviewed.
Complete default suite:1441 tests /1061 subtests passed in1677.60 seconds.
All44 collections and100 current cards /145 width records pass. All64 engine
dependency hashes match. Earlier143 widths,271 samples,31 diagnostics,75 routes
and canonical scientific arrays are unchanged; only the Gulf Stream dashboard
entry changes. Remaining physical measurement and identity gaps stay open.
