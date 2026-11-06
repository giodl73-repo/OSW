# Balearic regional width gap — 2026-10-14

## Source and quantity

Juza's SOCIB Regional Estimates, suggested citation year 2021 and document
version 13 November 2023, reports BC = Balearic Current in section 4, page 5.
The original table explicitly reports 20–35 km along the northern island
shelf. Mean geostrophic speed 0.2 m/s and northeastward direction are separate
context. The temporal-variability cell says seasonal maximum in autumn; it
does not explicitly say this is a width maximum or assign the 35 km endpoint
there. Neither 20 km nor 35 km is assigned to a calendar season.

The exact eight-page provider PDF is retained locally: 632,269 bytes,
SHA256 8810f7c2a72b3f12cf23755c7f898404193f14ccf45512d563458e2f7fd08b07.
Relevant pages 1–3, 5–7 were read; the page-5 table was visually inspected.
The page-2 license is CC BY 4.0 International. The original and page pixels
are excluded from Git; attributed source facts and an independent graphic
are packaged. Fresh source acquisition reproduced the exact original pin.

This adds a reported regional width range, with representative scalar null.
Sampling period, numeric uncertainty, fixed layer, paired boundaries, exact
product/version/grid and row-specific calculation are unspecified. No mean
speed cutoff, midpoint, confidence level, monthly interpolation, dated
occupation, mapped width band or full-current annual range is inferred.
Suggested bibliography and generic Copernicus credits do not resolve those
missing methods. Independent scientific admission remains open.

The earlier two-source Balearic assessment is preserved in the new audit as
historical review. Its qualitative current description and Storm Blas
upwelled-water band remain separate evidence. The active no-numeric-width
assessment is replaced by the new reported source range.

## Integration and invariants

139 scoped width records / 73 canonical owners, up from 138 / 72. Five owners
remain reviewed without comparable numeric widths, thirteen unassessed,
seven section-only and two derived pending review. No published whole-current
length or ranked-width admission changes. Routes remain 74 / 68 owners / 21
without a candidate. Source index now contains 227 exact documents; 211
samples, 25 diagnostics, 17 series and 42 query collections are unchanged.

Python validates the frozen complete audit, exact retained original,
acquisition and protocol, and requires the unique reviewed inventory record.
Rust embeds the same reviewed audit independently of editable owner/context,
requires the record for the represented Balearic owner and rejects coherent
source-receipt rebinding. The dedicated browser is in the mainline runner.

The range is drawn with two endpoints and no selected midpoint. The atlas
card, query and regional phase view expose source/method/unknowns and the
source inspector. The independent figure is
`figures/balearic-socib-2023-regional-width.svg`. Only the Balearic dashboard
owner changes. All prior 138 width records and scientific arrays are
preserved, as are observation dates and seasonal geometry frames; the frames
only refresh their width-inventory receipt.

## Verification

```
python analysis/check_balearic_socib_width.py
python analysis/check_current_width_inventory.py
python -m pytest -q analysis/test_balearic_socib_width.py analysis/test_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_balearic_socib_width_browser.py
python analysis/test_rust_index_store_browser.py
python -m pytest -q
```

Focused Python: 36 tests / 547 subtests passed. Locked Rust build: 46 tests
passed. Dedicated browser passed regional range scope, no invented
seasonal widths, atlas/source navigation, mobile reflow, native/WASM parity
and five rejection cases (midpoint, calendar, cutoff, missing record and
coherent source rebinding). Original table and independent range diagram
visually reviewed; mobile card screenshot retained for visual review.
Final full offline and 227-source index results passed; see below.

## Publication

Continue existing draft PR 83 on codex/current-measurement-gaps; no per-gap
PR and no merge. Base commit d6c3d07da2beafcdfda9001c98756b07d6fc2970.
At that head remote run 38541270456 failed Zenk paper acquisition with 403,
including verified institutional alternatives. Local test results do not
establish remote CI or mainline success. New-head status is reported
separately. Core physical measurement and annual-data gaps remain open.


## Final local verification

1,373 tests / 1,023 subtests passed in 1305.91 seconds (21m45s).
All 46 Rust tests and locked native/WASM builds passed. Dedicated browser
passed regional range, source/atlas navigation, 320 px mobile reflow,
native/WASM parity and five rejection cases. The 227-source index browser
passed exact source inventory, twelve seasonal snapshots, independent NOAA
oracle, parity and changed-input rejection. Source original/table,
independent figure and mobile graphic were visually reviewed. Fresh SOCIB
acquisition reproduced the exact 632269-byte original. All source/engine
pins and staged/workspace bytes verified. Previous 138 width records,
canonical arrays, routes, samples, geometry frames and observation dates
remain unchanged; seasonal frame receipt alone refreshed. Internal review
supports editorial delivery. Physical paired boundaries, exact width method,
annual ranges and independent admission remain open. The broader core-data
goal remains active. Publication stays in existing draft PR83, with no merge.
Earlier-head remote run 38541270456 failed Zenk acquisition with HTTP403;
new-head remote status is pending, not claimed green.
