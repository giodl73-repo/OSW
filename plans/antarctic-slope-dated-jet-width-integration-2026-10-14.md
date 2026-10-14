# Antarctic Slope dated jet constraint — 2026-10-14

Base: f5b594601a65c59d18070a6d2bc87d5b194b7b59. Continue draft PR83.

## Source and quantity

Chavanne, Heywood, Nicholls and Fer (2010), DOI 10.1029/2010GL043603,
primary publisher indexed Introduction paragraphs 2–3, Observations 4–7
and Figure 1–3 captions were reviewed. Paragraph 5 describes a narrow
southwestward surface jet narrower than 28 km on 23 February 2009, embedded
in broader slower southwestward flow. This is a source-reported dated jet
constraint, not complete ASC width or a 28 km point. No lower bound, zero-to-28
interval, confidence guarantee, annual extrema or geographic band inferred.

The paragraph and Figure 1 use 100 m detided LADCP horizontal-current
context. No uniform vertical slab is created. The 3000 m isobath is bottom
topography, not observation depth. Peak 28 cm/s and background about 10 cm/s
are separate speed descriptions, not width cutoffs. January's 11 km is a
shoreward speed-decrease interval; approximately 30 km is front migration;
525 m describes a different northeastward undercurrent. None is this width.

Original PDF and figure pixels were not obtained. Publisher PDF returned
403; author institutional PDF link redirects to a general HTML page; UEA
repository explicitly has no full text and CiteSeer download returned 404.
Only attributed facts and an independent OSW graphic ship. Source fields,
original figures and a paired boundary calculation are not reproduced.
This access limit is present in the data, card, SVG description and source
inspector. Publication or retrieval dates are not substituted for sampling.

## Integration and preservation

140 scoped width records / 74 canonical owners; four reviewed without a
numeric width, thirteen unassessed, seven section-only unresolved and two
derived pending. This count includes qualified constraints, not 140 point
measurements. Source corpus: 228 exact documents. Width samples (211),
diagnostics (25), series (17), collections (42), reference routes (74),
route owners (68), route gaps (21) and published lengths (11) are unchanged.

Existing 139 width records, canonical scientific arrays, routes, source
samples, geometry frames and all latest observation dates are preserved.
Only the Antarctic Slope dashboard owner changes. Seasonal frame values
remain unchanged; only their width-inventory receipt refreshes. M6's 61
velocity summaries, 16393 paired readings, 228 m nominal depth and 2017–2021
source period remain separate and unchanged; latest date stays 2021-02-13.

The earlier Darelius source-specific no-width review remains frozen in its
original audit and is archived in the new source audit. Python and Rust
now scope that exclusion to M6/mooring scales instead of banning evidence
from an independent 2009 source. A unique frozen 2009 record is required;
operator, date, owner, depth, scalar, interval and coherent source rebinding
are rejected. No M6 velocity or spacing value becomes a width.

## Visualization and gates

The constraint graphic displays <28 km as a description, with no filled
zero-to-28 bar. Regional phase card, atlas and source inspector retain the
source access and temporal limits. SVG alt text is scoped to this source;
the old generic NGCU 20 km description is not inherited. Chart cache version
advanced to 8. Dedicated browser added to the mainline runner.

```
python analysis/check_antarctic_slope_jet_constraint.py
python analysis/check_current_width_inventory.py
python -m pytest -q analysis/test_antarctic_slope_jet_constraint.py analysis/test_antarctic_slope_coverage.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_antarctic_slope_jet_constraint_browser.py
python analysis/test_antarctic_slope_coverage_browser.py
python analysis/test_rust_index_store_browser.py
python -m pytest -q
```

Focused Python: 8 tests / 11 subtests passed. Locked Rust/native/WASM build:
46 tests passed. Dated-constraint browser passed source/atlas/mobile, parity
and seven rejection cases. M6 browser passed observed velocity lights,
selection parity, dates, chart navigation and three coherent metadata
rejections. Independent diagram and mobile constraint graphic visually
reviewed. Initial M6 browser assertion included an obsolete 'records' suffix
on the width-evidence label; fixed, and final run passed. Final full offline
and 228-source index results passed; see below.

## Publication and remaining work

One continuing PR; no per-gap PR and no merge. Prior-head remote runs
38545739774 and 38545746505 were confirmed live running full offline tests,
after progressing beyond paper acquisition. This is not a green remote
claim. New-head CI is tracked separately. Original figure/field acquisition,
paired width methods, broader ASC envelope, annual ranges and independent
scientific admission remain open. The full core-data objective remains active.


## Validation correction before publication

The first full offline attempt found five identity/error-contract failures
(1371 other tests / 1034 subtests passed). The new mandatory inventory selector
counted other source records reassigned to Antarctic Slope, and the Python
owner dispatch intercepted the ACC identity guard. Invalid data was rejected,
but the wrong source guard ran. The corrected selector requires the unique
frozen jet identifier; recognized legacy identifiers retain their own source
validation before an Antarctic owner fallback. Extra unknown Antarctic records
still pass through the frozen source guard. Source data and exclusions are
unchanged. The failed attempt is not a publication gate; targeted legacy
regressions, new browser and a fresh full suite verify the correction.


## Preceding-head remote UI regression

Run 38545739774 at f5b5946 passed checksum-pinned source acquisition and the
complete offline suite, then failed the shipped-WASM browser step. NGCC's
atlas check still waited for exactly 73 route cards although the catalog now
has 74. Pacific SECC's check had the same obsolete assertion. Both now bind
the expected card count to the declared route catalog. No scientific data,
threshold or acceptance gate was loosened. These two affected browser checks
are rerun locally; new-head CI remains separate from the earlier failure.


## Final local verification

1,377 tests / 1,034 subtests passed in 1220.92 seconds (20m20s), after the
identity-order correction. All 46 Rust tests and locked native/WASM builds
passed. Six affected legacy identity/native rejection checks passed; the new
extra-owner regression passed. Dated constraint browser passed parity,
source/atlas/mobile and seven rejection cases. M6 browser retained all
velocity/date/metadata protections. The rebuilt 228-source index passed
exact inventory, twelve snapshots, NOAA oracle, parity and changed inputs.

All 100 atlas current cards and all 140 unique scoped width records passed
source definitions/links, keyboard disclosure, inspector return, reset,
mobile and stored-data fallback checks. This all-current check is now in the
mainline runner. Five browser scripts with obsolete 64/73 route totals now
bind to the catalog: NGCC, Pacific SECC, monthly atlas sections, inline width
cards and Rust atlas snapshot. All five passed; snapshot verified 95 exact
atlas documents and eighteen loader rejections. Current catalog is 74 cards.

Diagram/mobile graphic visually reviewed. Source/engine pins and staged
bytes verified. Prior widths, canonical arrays, routes, samples, geometry,
M6 values and observation dates are unchanged. Source access, paired edge
methods, broader ASC dimensions, annual ranges and scientific admission
remain open. Earlier-head remote passed source acquisition/full offline
then failed obsolete browser count; this is corrected here, with new-head
remote status pending. Continue draft PR83, no merge. Core-data goal active.
