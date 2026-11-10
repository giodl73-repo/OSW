# Kuroshio Extension regional plotted pathlength v4

V1 atf323484, v2 atc82442e and v3 at5da1cae stay frozen. All three
extraction failures occurred before target year/km calibration or products.
V3 retained cubic geometry and actual0.6-point source strokes but rejected
two tiny run-boundary coordinate overlaps. The raw topology diagnostic finds
16 runs with no internal reversed x, and two inter-run overlaps of0.001572
and0.001007 PDF point. Source drawing order differs from chronological order.
No calibrated target series or length range was inspected in this diagnostic.

## Explicit coordinate-precision correction

Preserve all exact original commands and retained run breaks. Sort runs by
their first x, retain original drawing/run ownership, and require strictly
nonreversed x within each run (equal x allowed). Permit inter-run overlap only
within the already declared0.02-point PDF coordinate tolerance. Do not shift,
average, drop, join or sort individual readings to hide the overlap. Report
each permitted boundary overlap and its magnitude explicitly; larger overlaps
still reject. The endpoint records on either side of a run boundary remain
distinct; graph-knot count includes shared endpoint instances, not a claim of
unique observations or source samples.

This corrects a graphics-coordinate contract, not a physical current result.
The0.02-point allowance is far smaller than the declared50km/0.1year reading
allowances. Every other v3/v2 rule remains unchanged:0.75-point maximum source
stroke with actual width preserved, all original line/cubic commands, analytic
cubic y-extrema and bounded0.01-point tessellation, reviewed labelled-axis
calibration,10km half-up rounding, approximate graph years, explicit error
type and regional141E–153E support. Do not infer physical width, geographic
axis, whole-current ranks, observed cadence, precise dates, seasonal playback
or physical annual extrema. Cubic readings are not additional observations.

Freeze v4 producer/tests/protocol/preflight and all exact dependencies in Git
before original extraction. Never edit prior frozen methods or overwrite
products. Optional exact-original replay and default offline command-mirror
replay remain separate. Synthetic checks must now also prove small boundary
overlaps remain exact and large overlaps reject, alongside the existing
calibration, curves, topology and scientific-scope checks. After extraction,
verify all commands/knots/readings, independent actual calibration, exact
JSON/SVG replay and actual chart rendering. Full numeric table/query/map-card
access, native/WASM equality and keyboard/phone proof remain delivery gates.
One heavy local job at a time, below-normal priority, one logical CPU; retain
the existing branch and draftPR83.
