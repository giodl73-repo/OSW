# Aleutian regional reference reach

Date: 2026-10-08. Status: working editorial evidence, not scientific or canonical
measurement admission.

## Data and visual result

Favorite (1967), *The Alaskan Stream*, Bulletin 21, pp. 1–20, is hosted by NOAA.
The full PDF was retrieved; printed pp. 1–2, 11–12 and 18–19 were read, and
rendered pp. 12 and 19 inspected. The source response checksum and size are in
the input and scope audit. The original PDF and figures are not redistributed.

Figure 27 distinguishes eastward Subarctic/Aleutian flow from westward Alaskan
Stream and West Wind Drift. OSW selects a regional 175 E–140 W sketch from that
convention. Coordinates are editorial approximations, not calibrated figure
digitization or measured current cores. WGS84 leg lengths total approximately
**3,300 km**. Four path/gate choices and longitude/endpoint offsets give
**108 scenarios**, with a rounded **2,900–3,500 km** envelope.

This envelope is a sensitivity calculation, not observational uncertainty,
physical width or seasonal extrema. Source observations from May–August 1959
do not date the schematic. Whole-current length, width and annual ranges remain
unknown. The route is in the studied-reach group, excluded from published length
ranking and the general reference-route ordering.

The generated map, atlas card, source review, query route and object joins all
use the same input/report. Date-line display follows the existing periodic
geodesic policy. The global atlas fit retains a world view across the seam;
the card map shows the reach continuously. Display-state crossings are
illustrative line intersections, not physical current membership.

Coverage becomes **63 candidates for 60 of 89 unranked current owners**;
**29 owners** still lack candidates. The published ranked length count stays 11.
Width count stays 72; there are still 240 dashboard objects and 39 query
collections. The separate source index still has 76 documents.

## Integration corrections

The family inventory audit was rechecked against the new catalog: equatorial
decisions and five proposed basin members remain unchanged. Its basis checksum
was refreshed after final catalog generation. The dependent endpoint-context
audit and two monthly branching extractions were then rebuilt; their scientific
values and source observation support remain unchanged. Tests now expect the new route
count and the independently supplied Aleutian route capability; neighboring
identity, width and observation-date restrictions are preserved.

The first full test run had 814 passing tests and three failures: one stale
family-audit checksum and two old Aleutian route-capability expectations.
The first atlas browser run used an incorrect narrow-fit expectation for a
date-line crossing. These were corrected; final results are recorded below. A second full run had 816 passing tests
and one stale dependent endpoint-audit failure; refreshing the reviewed basis
and rebuilding the two monthly extractions corrected that dependency.
An intermediate rebuild correctly rejected the stale family basis and candidate
checksum. Final rebuilding followed dependency order before browser validation.

## Reproduction

Refresh the family audit against the current catalog before rebuilding when its
basis is stale; review family decisions before changing its checksum. After the
catalog changes, refresh that reviewed basis again before running protocol tests.

```powershell
python analysis/build_current_reference_path_candidate.py --input research/aleutian-reach-reference-path-input.json
python analysis/build_current_reference_path_catalog.py
python analysis/build_indian_sec_monthly_bifurcation.py
python analysis/build_pacific_nec_monthly_bifurcation.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_reference_route_atlas_browser.py
python analysis/test_rust_route_decisions.py
python analysis/test_rust_atlas_snapshot_browser.py
python analysis/test_rust_cartography_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Browser checks use the local checkout server and installed Chrome. Build the
native executable before starting checks that use it.

## Validation

Final native/WASM build passed, including 38 Rust tests. JavaScript syntax checks
passed for 39 modules; 14 page validation assignments passed. Assignments do not
establish that all 52 registered browser checks were run in this batch.

Final full Python suite: **817 tests and 619 subtests passed**, 219.71 seconds.
Final atlas navigation and all 89 route-decision checks passed. Checked-atlas
validation passed for all 78 atlas source documents, including 18 loader
rejections and full native/WASM parity. Cartography passed for 447 source
geometry requests, seam handling and five invalid requests. Black Sea regional
width and all nine recurrence-card checks passed with the local Chrome override.
The final checked-atlas browser validation was repeated after the dependent
branching receipts were rebuilt. Aleutian 320 px card reflow and original/source
map screenshots were visually inspected; no horizontal overflow.

All 62 prior catalog route records are exactly unchanged. Both monthly branching
extractions differ only in `scope_audit_sha256`.

Review: `signals/roles/check/aleutian-reference-reach-roles-check-2026-10-08.md`.

## Remaining work

Diagnose modern layer-compatible axes, named-flow gates and branching before
whole-current measurements. Acquire compatible monthly geometry and paired
velocity boundaries before seasonal dimensions. Many other current widths,
eddy footprints and physical state joins remain unresolved. Protected-main
publication of the prior consolidated batch is still pending.

## Publication portability correction

Consolidated PR 30 run 37740339413, job 113189340737, failed at
`test_black_sea_regional_width_browser.py` with `KeyError: OSW_TEST_BROWSER`.
The regional-width and recurrence checks now use the optional browser override
via `os.environ.get`, matching the other checks. CI supplies Playwright Chromium;
the local machine uses an explicit installed-Chrome path. Local default Chromium
is absent, so the default launch must be confirmed by CI, not claimed locally.

The separate CI portability correction was committed/pushed as `f0c3f40` to
the existing consolidated publication PR 30. Its new exact-head required checks
remain pending; no mainline landing is claimed.
