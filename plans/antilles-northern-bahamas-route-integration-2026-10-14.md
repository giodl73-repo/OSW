# Antilles regional route delivery — 2026-10-14

## Evidence and scope

A conditional northern-Bahamas editorial reference route now connects the
selected offshore-Abaco 26.5 N gate to an OSW 28 N approach gate. These are
regional truncations, not observed origins, terminations or a Gulf Stream
junction. The nominal approximately 200 km and 200–300 km scenario envelope
refer only to this drawing; they are excluded from comparable route ordering
and published whole-current length ranking. All 81 predeclared drawing
scenarios passed the coarse atlas-land clearance check. This is not a
bathymetry, continuity or observed-axis validation.

Meinen et al. (2019), DOI 10.1029/2018JC014836, supplies regional naming and
local 26.5 N mean-flow context. Relevant PDF pages 1–3 and 18 were reviewed.
The 2005–2015 mean record does not date the full route. Its subsurface peak
near 400 dbar remains pressure, distinct from the earlier AB0505 400 m
section diagnostic. Its transport-integration span remains unadmitted width.

The KN-200-4 RAPID/MOCHA cruise report (13 April–3 May 2011), pages 1 and 10,
provides contrary local evidence: the characteristic Antilles Current was
absent off Abaco during the cruise while north-bank westward flow was found.
The modeled northwestward connection is conditional, not a continuous
observed axis. The route does not equate those two observed flows.

Both exact originals are retained locally and excluded from Git. The
Meinen article identifies U.S. public-domain government status; no worldwide
license is inferred. Cruise-report redistribution rights are unestablished.
Only acquisition receipts, attributed facts and an independent OSW map ship.
Supporting-original receipts are now checked alongside the primary original;
changed or missing contrary evidence fails the receipt gate. NOAA's exact
Antilles download returns 403 with an explicit User-Agent header; the downloader
now omits that header for this named source while retaining the original
checksum requirement. Both originals passed fresh-download verification.

## Integration

Atlas and query collections: 74 route candidates, 68 of 89 remaining owners
covered, 21 without routes. Published length admissions stay at 11; 138 scoped
width records and 211 source-bound samples are unchanged. The exact index
corpus now contains 225 documents. NASA overlap and OSW state crossings retain
their editorial display meaning; they do not assert depth/date matching or
physical current containment. Only the Antilles dashboard owner changed;
all observation dates and prior scientific arrays are preserved.

Reviewed route-catalog dependencies in the equatorial family and bifurcation
scope audits were refreshed. Existing monthly branching values, calendars and
interpretations are unchanged; only their audit receipts changed.

## Reproduction and verification

```
python analysis/build_current_reference_path_candidate.py --input research/antilles-northern-bahamas-reference-path-input.json
python analysis/build_current_reference_path_catalog.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_reference_route_atlas_browser.py
python analysis/test_rust_index_store_browser.py
```

After changing the route catalog, review and refresh the family/bifurcation
receipt chain before generating the query/index bundles. Browser gates use a
local server at port 8788 and OSW_TEST_BROWSER. Generated SVG and the 320 px
card were visually reviewed; map-card navigation and mobile reflow passed.
Protocol/receipt tests passed (17 tests / 48 subtests); serialized Rust build
passed 46 tests. Final full offline and index parity results passed; see below.
The initial focused run exposed stale family receipt and obsolete zero-route
Antilles assertions; these were corrected. An index-browser attempt during
receipt regeneration correctly rejected the changed catalog; it is not a
passing gate. The final parity run uses the rebuilt, pinned corpus.

## Publication and open work

Continue in existing draft PR 83 on codex/current-measurement-gaps. No new PR
and no merge. Earlier-head remote CI failed downloading the Hughes Hiri source
with HTTP 403; this does not prove an implementation regression. Remote status
must be reported at the publication head. Whole-current dimensions, seasonal
ranges, verified axes, bathymetry and independent scientific admission remain
open; the core-data goal is still active.


## Final local verification

1,370 tests / 1,014 subtests passed in 1298.33 seconds (21m38s).
All 46 Rust tests passed with serialized locked native/WASM builds. Atlas
map-card navigation, contrary-source caveats, studied-reach exclusion, pressure
units, direct-link/mobile rendering and the Antilles filtered-query native/WASM
check passed. The 225-source index browser passed exact source inventory,
twelve seasonal snapshots, independent NOAA oracle, parity and changed-input
rejection. Both new sources passed fresh checksum-pinned acquisition. Source
and engine pins and staged/workspace bytes were verified. Prior scientific
arrays, widths, samples, geometry frames and observation dates are unchanged;
monthly branching records only refresh reviewed audit receipts. Seven-role
internal review supports this editorial delivery. Whole-current dimensions,
annual ranges, physical axes, bathymetry and independent admission remain open.
Earlier-head remote CI failed Hughes Hiri acquisition with HTTP 403; validation
at the new publication head is pending and no green remote claim is made.
Continue existing draft PR 83; no per-gap PR and no merge.
