# Guiana Current: mapped regional reach

Continues `codex/current-measurement-gaps` and draft PR83. No separate PR or
merge to main.

## Result and scope

The Guiana Current now has an editorial route through the Guianas survey
region, from an offshore Maroni approach to eastern Trinidad. The selected
polyline measures approximately **900 km**, with a rounded **700-900 km**
envelope across **54 declared editorial scenarios**. A shorter ending near
the Orinoco approach and independent endpoint/longitude shifts describe
convention sensitivity, not observed position errors or seasonal variability.

This is a regional reference-path calculation, not an observed current axis,
named-current origin/termination, whole-current length or parcel trajectory.
It remains in the studied-reach group, excluded from both published length
rankings and the whole-route comparison order. Width and annual extrema are
not derived from this line. All vertices are OSW choices; no station positions
or source curves were digitized.

## Source basis

[H. Gade's hydrography chapter](https://www.fao.org/4/x6078e/x6078e03.htm)
in the IMR/NORAD/UNDP/FAO survey report supplies regional context and named
sections. [Report front matter](https://www.fao.org/4/x6078e/x6078e00.htm)
dates publication to November 1989 and identifies the 1988 programme.
[NOAA's glossary](https://www.tidesandcurrents.noaa.gov/glossary.html) supports
the Guiana name and northwestward direction. None supplies the selected
vertices or a numeric along-current length.

The publisher HTML is OCR-derived; original print/page-image review is not
claimed. The geographic interpretation does not resolve Guiana versus North
Brazil naming limits, temporally continuous flow, deeper counterflow, ring
paths or freshwater-plume boundaries. Original survey charts, bathymetry and
appropriate velocity fields remain necessary for stronger axis claims.

## Atlas, query and joins

- [Open the current map/card](../almanac/reference-routes.html?atlas-feature=current%3Aguiana#route-atlas)
- [Standalone OSW route map](../figures/guiana-reference-path-candidate.svg)
- [Input and assumptions](../research/guiana-reference-path-input.json)
- [All calculated scenarios](../research/guiana-reference-path-candidate.json)

The map uses the existing equirectangular OSW ground. All 54 geodesically
densified routes avoid its coarse land mask; this does not verify shelf-break
alignment or fine land/reef clearance. The selected route crosses GUIA in
the display atlas. NASA crop `level2_B_3` contains every retained scenario.
These are navigation joins, not physical current passage or NASA detection.

The existing atlas supports direct selection, card links and the route image.
Rust/WASM queries expose the route plus both exact JSON source documents.
Guiana's route coverage light changes; no new dated velocity observation is
created by adding editorial geography.

## Preservation and coverage

Route coverage grows **69 to 70 owners**, **75 to 76 candidates**. Of the 89
names lacking a published ranked length, **19 still lack any route candidate**.
The studied-reach group grows 36 to 37. This does not mean 70 whole-current
lengths have been measured. The 11 published lengths and their ranking, all
75 earlier route reports, all 155 scoped width rows and seasonal-frame bytes
remain unchanged. All 239 other dashboard entries and every latest
observation date remain unchanged.

The exact source index contains **332 documents**. All **91 engine pins** and
**166 research dependency pins** match. Root HTTP serves the exact packet,
engine, index and figure. Production generation uses the same Rust source;
native and WASM engines were rebuilt against the updated stores.

The equatorial family inventory's catalog dependency is refreshed to the new
catalog after checking that its basin proposals and scientific decisions are
unchanged. The protocol checker passes with the final basis. The refresh
does not reclassify Guiana or add a family member.

## Verification

Focused route geometry, catalog, state-join and seasonal-frame gate:
**22 tests / 33 subtests PASS**. Locked offline build and all **61 Rust tests
PASS**. The first focused browser invocation could not launch because the
optional Playwright browser cache is absent; it executed no UI assertions.
The next invocation uses the already-installed Chrome executable. Browser
checks pass for map/card navigation, all 100 selectable current names,
studied-reach ranking exclusion, exact route-query native/WASM parity, both
indexed source documents, keyboard, 320 px and reduced motion. Both native
and actual WASM reject changed source hashes and route projections. No
original PDFs, NetCDFs or archives are fetched automatically.

Initial visual review found a legend/endpoint-label overlap. The final map
extent moves north while all vertices and numerical scenarios stay unchanged;
the dependency chain is rebuilt. A separate final display/source check and
visual review pass for that correction, including both exact source documents,
native/WASM route-query parity, keyboard navigation and 320 px reflow. A final
family-context formatting preservation changes only its reviewed catalog SHA
in the original document bytes; the source index and engines are rebuilt.

Two affected dashboard scope tests pass in **44.84 seconds**. Guiana's test
now verifies its own regional geometry and checks that it does not borrow the
North Brazil route. The earlier native-stage failure was independently
reproduced at 25b286e: a legacy typed-connectivity test still expected no
Aleutian observation date. Its successor expects the directly observed
1993-07-18 date and additionally removes all typed links, proving that dates
and dimension capabilities for every owner remain unchanged. Original null
junction/transport and noncanonical-link assertions are retained.

The separate clean full suite at **25b286e** remains a predecessor gate; it
does not certify this route addition or the later underway-averaging operator.
Keep their successor combined validation pending until actually completed.
That live run has reported a failure marker; its final summary is still
pending. The independently reproduced stale-date assertion is fixed and
targeted checks pass at the successor, but the full predecessor is not passing.

### Terminal predecessor and publication receipt

The 25b286e run finished at **2026-10-18 14:13:05 UTC**: **1 failed,
1,712 passed, 1,152 subtests passed in 2,344.34 seconds**. Start/end are clean;
the test process has exited. The sole failure is the independently reproduced
legacy Aleutian-date assertion above. It remains a recorded failure, not a
retroactively passing gate. The successor fixes it with stronger invariance
checks and still requires its own complete run.

Scientific/UI commit **55fc722** passes working-file and committed-blob checks
for all **91 engine pins, 166 research pins and 332 indexed source documents**
(527 unique blobs). Normal root HTTP serves exact final assets; the final
native CLI returns the new Guiana route and the exact family-context source
after index rebuilding and completed compiler-cache cleanup. This does not
certify the pending complete successor suite or make hosted CI green.

## Reproduction

```text
python analysis/build_current_reference_path_candidate.py --input research/guiana-reference-path-input.json
python analysis/build_current_reference_path_catalog.py
python analysis/build_reference_route_state_join.py
python analysis/check_current_seasonal_route_frames.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis/test_current_reference_path_candidate.py analysis/test_current_reference_path_catalog.py analysis/test_reference_route_state_join.py analysis/test_current_seasonal_route_frames.py -q
```
