# Kuroshio filtered width time-series gap batch

Baseline `c749116b20acddc9d22dc9732275648222621f94`; continuing the same
`codex/current-measurement-gaps` branch and draft PR83. No separate gap PR.

## Source and measurement contract

Liu and Gan (2012), doi:10.1016/j.dsr.2011.10.008, Figure7a supplies a
half-year-filtered East China Sea regional width curve (122–130°E).
The retained original PDF, acquisition, source-method audit, plot calibration,
protocol and operator are pinned. The original PDF is not redistributed.

The declared protocol samples 192 month-midpoint positions across the printed
1993–2008 year axis. All targets resolve within original PDF vector segments.
An original tiny stroke break is recorded without adding a bridge. Printed
year stems are calibrated piecewise. Values round to5km; ±5km is an editorial
graphical reading allowance, not measurement error, confidence, annual extrema
or physical variability. The sampled values span190–225km, not a whole-current
width range. Plot-coordinate allowance is ±0.05years, not UTC timing accuracy.

Calendar observation dates, months and years remain null. Separate plot labels
do not imply independent monthly observations. Filter kernel, alignment,
endpoint treatment and exact averaging weights remain unknown. Surface
geostrophic diagnoses exclude ageostrophic flow; interpolation from the original
1/3° grid to0.1° creates no independent observational resolution. This protocol
was declared after viewing source methods and graphic metadata, before these
numerical readings; it is not a blinded experiment.

## Data and visualization

Width samples grow271→463, diagnostics43→44 and series25→26 within the existing
45collections. The shared Rust/WASM scene supplies a complete curve figure,
annotated year/month matrix, 16-year selector, 12-row annual table, individual
reading inspectors and all192 queryable rows. Cards, seasons and diagnostic
queries share this presentation; the sample query has a plot-year axis.

The original three prose means and64seasonal spatial samples are unchanged.
There is no admission to the headline width inventory, physical map edges,
annual extrema or seasonal map animation.155width rows/81owners,11lengths,
76routes, geometry, observation dates and all239other dashboard owners remain
unchanged. All271earlier width samples remain identical by value.

## Verification and release state

The focused Python gate passes10tests/3subtests; all66Rust tests pass. Actual
native/WASM browser gates pass card, seasons, diagnostic and all192sample
query, three exact source documents and eight corruptions, including coherent
source rebinding, erased samples and forbidden inventory promotion. Keyboard
year selection, row inspection,320px reflow, table scrolling and reduced motion
pass. Final source figure and UI screenshots are reviewed. No page errors or
automatic original downloads occur.

Working hashes match102engine pins,180research pins and353indexed documents.
Served packet/WASM/index/figure bytes match disk. Committed-byte verification
and a clean complete successor run follow the batch commit.

The preceding clean complete run at c749116 passed **1,741tests and1,159
subtests in2,687.78seconds**, ending2026-10-18T17:18:57UTC. It does not cover
this new Kuroshio batch. Main release requires a complete clean latest pass.
