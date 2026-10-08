# Norwegian Atlantic branches: scoped width evidence

2026-10-08. Editorial extraction; identity and scientific admission pending.
Working base: 78a831d8c17a008a164e4ca39052f341068b0869.

## Sources and values

Orvik, Skagseth and Mork (2001), doi:10.1016/S0967-0637(00)00038-8,
publisher-indexed abstract reports 30–50 km for each eastern and western
branch at the Svinøy section. The full original article and figures remain
unreviewed. Store two separate ranges without a midpoint.

Mork and Skagseth (2010), doi:10.5194/os-6-901-2010, section 3, printed
page 904, describes an approximately 50 km wide slope branch in the surface
ADT field. Original pages 901, 903, 904 and 906 were rendered and inspected;
methods and discussion were read. The unmodified original PDF is retained
under CC BY 3.0 with attribution, byte count and SHA-256 acquisition receipt.
The western mean flow is discussed as broader than the earlier reported
range, but no new numerical mean width is supplied. Keep it null.

## Identity and measurement rules

Attach these three records to the existing proposed Norwegian Atlantic
slope/front identities and their proposed parent system. Canonical
`norwegian` remains ambiguous with the coastal system. Neither canonical
`norwegian` nor `norwegian-coastal` receives these records. Inventory remains
100 canonical current names and 28 proposed additions.

The existing width protocol applies without a new aggregation convention.
Do not sum branches, select range midpoints, infer a temporal trend from
publication years, or treat these as annual extrema or confidence intervals.
The approximate 2010 scalar has no numerical uncertainty supplied.

Mooring dates, bathymetry, frontal jet depth, ADT series dates, smoothing,
resolution and independent validation depth are contextual metadata. They
do not establish exact width occupation dates, a fixed width layer, paired
edges or an annual cycle. Geometry, width observation interval, calendar
months and fixed layer remain null. Ranking, annual extrema, full-width
inference and seasonal playback remain false. The ADT width is not labelled
a temporal mean or mean of measured widths.

## Integration and presentation

The source audit binds all three records. Python checks original PDF bytes,
rights receipt, protocol receipt, contextual exclusions and exact proposal
copies. Rust checks numeric scope, branch ownership, parent links, dates,
depth and temporal eligibility. Coherent atlas rewrites are also tested.
The Rust engine manifest now includes the new validator module.

Each proposed branch card shows a labelled range or point chart, definitions,
source-access limitations and a direct Rust source-query link. Methods are
separate rows, without a line suggesting a temporal trend. The system card
links its branches and leaves system width unknown. No occupied map buffer
or state-containment claim is created from these dimensions.

Canonical width inventory remains 79 scoped records across 40 owners, with
53 unassessed currents. This batch adds three proposed-branch records across
two proposed owners. The source index grows from 82 to 84 documents; the
query bundle remains at 39 collections. Existing canonical widths, routes,
seasonal frames and extracted branching values remain unchanged.

Changing the proposal inventory invalidated the equatorial endpoint audit's
input receipt. That receipt and its two dependent monthly-extraction receipts
were refreshed. The numerical extraction values remain unchanged.

## Verification and publication

Initial full suite: 826 tests and 824 subtests passed; one test failed on the
stale endpoint input receipt. Initial regional browser failed its mobile text
size check. Both defects were corrected. A second regional attempt caught a null DOM
read in its parent-card wait; the test now waits for the asynchronously loaded
card. The final regional browser passes mobile text/reflow, both branch-query
links, full native/WASM parity and three coherent branch-scope rejections.
Both mobile branch-chart screenshots were visually inspected. The final full
suite passes: 827 tests and 829 subtests in 290.79 seconds. The final atlas
snapshot browser passes: 78 exact source documents, eighteen loader
rejections, native/WASM parity, 100 current/140 eddy selectors and 63 cards.
Final build: 39 Rust tests pass, native and WASM compile. JavaScript syntax
checks pass for 39 files; all 14 pages have validation assignments. Final source
index browser passed with 84 exact sources; atlas snapshot browser passes
after receipt refresh as recorded above.
These passes do not establish mainline publication.

Reproduce (set OSW_TEST_BROWSER when using installed Chrome):

```powershell
python analysis/check_norwegian_atlantic_branch_widths.py
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

Original fixtures used by other tests must be acquired separately where their
licenses prevent redistribution. Source downloads are not a default test gate.
PR30 protected-main checks remain in progress at head 78a831d. This batch's
review and publication are separate from that running mainline gate.

## Remaining work

Review the original 2001 methods and figures, resolve canonical identities,
and obtain compatible dated sections with explicit edge definitions before
seasonal width, branch footprints or state intersection can be admitted.
Most canonical length, annual width and eddy footprint gaps remain open.
