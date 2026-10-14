# Aleutian monthly section gap batch

Continues existing draft PR #83 / `codex/current-measurement-gaps`. Previous
turn was progress: four NGCC source descriptors were verified and pushed as
9269151. This batch adds actual archived vectors and monthly diagnostics for
the eastward Subarctic/Aleutian current convention.

## Data and fixed method

Predeclared 160 W meridional domain 40–56 N and eastward peak-search window
46–51 N before acquisition. Favorite (1967), Figure 27 and the retained naming
audit provide historical circulation context; OSW chooses the investigation
window. Neither source schematic nor OSW reference-route waypoints establish
observed edges or a 2013 surface axis. Westward Alaskan Stream, Bering-side
Aleutian North Slope Current, North Pacific exchange and eddies stay distinct.
Cold-water correspondence and named-current association remain unverified.

Original OSCAR 2017.0 CSV: 303,287 bytes, SHA256
`6f827bd51225f2ba822ddb58b9fe009074680e354fd6caa3883f184b1fb35f7a`.
72 actual 2013 timestamps × 49 native cells = 3,528 vector positions; 144
missing pairs in two masked cells per frame. Keep both components and actual
cadence, including four six-day gaps. No missing values are replaced with zero.

The unchanged operator averages complete pairs by UTC month, requires five
pairs per cell and a positive eastward peak ≥0.02 m/s, then finds the first
connected 40/50/60% crossings. No bridging holes or disjoint bands. WGS84
boundary separation is rounded to 10 km. Preserve native sampling brackets,
threshold sensitivity and unknown measurement uncertainty separately.

All twelve nominal spans resolve, about 90–320 km across local monthly-mean
profiles. March, May and September have fewer than four native spacings;
none has a peak at the search-window edge. Different peak positions may
identify different features. These are fixed-orientation component spans,
not flow-normal widths, tracked current evolution, climatology or annual
physical extrema. No full-current width, area or NASA identification inferred.

## Integration and retained evidence

Width worklist: 14 unassessed owners; six section-diagnostic owners with
current width unresolved. Published scoped evidence remains 136 records /
72 owners. Canonical identities, 11 ranked lengths, 89 length gaps and all
73 reference routes remain unchanged.

The raw vector inventory becomes 21,096 positions across five sections. The
previous four provider CSVs, profiles, numerical results and SVG sheets stay
unchanged; four shared dependency receipts are renewed in each report.
Exactly those four dashboard owners plus Aleutian change fingerprints; all
observation dates are preserved. The seasonal route file refreshes only its
width-inventory checksum, with identical frames.

Query corpus: 204 exact JSON documents, 187 source-bound samples, including
60 basin-section samples. Native/WASM queries, monthly chart inspection,
section endpoint maps, source links and a twelve-panel profile sheet expose
the new data. Playback highlights recorded readings, without interpolation
or geographic current animation. Five frozen Rust source receipts guard
rebound originals and sample projections. Owner selection is explicit for
each section; unknown frozen source IDs cannot inherit another owner.

## Verification

Focused source/operator/inventory tests passed: 42 tests / 546 subtests.
Full offline, serialized Rust/native/WASM and browser/index results follow.
Internal CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL and LOGBOOK review
covers editorial diagnostic publication, not scientific current-width admission.

Reproduce with retained provider-byte verification, span and figure builders,
width validation, dashboard/index/query builders, serialized engine build,
default offline pytest and basin/sample/index browser checks. Use the existing
localhost:8788 server; acquire data explicitly only when refreshing originals.
Original published paper pins and scientific data are unchanged.

## Final publication gate

**1,337 tests and 958 subtests passed in 1380.57 seconds (23m00s).**
All 46 Rust tests and serialized locked native/WASM builds passed. Focused
operator/source/inventory gate: 42 tests / 546 subtests. Browser passed all
five contexts / 60 monthly samples, native/WASM parity, pagination-independent
charts/maps, keyboard/month inspection, source links, 320 px reflow, five
native and three WASM rejection cases. The legacy sample check retained all
127 original samples and five missing readings. Index-store browser passed
204 exact documents, 12 seasonal snapshots, independent NOAA oracle,
native/WASM parity and checked-input failures. All 61 engine / 204 source
pins verified; profile sheet and representative UI captures visually reviewed.
Previous source widths, four earlier numeric sections, observation dates and
seasonal route frames preserved. Internal editorial publication conditions
satisfied; named-current association and physical annual widths remain open.
