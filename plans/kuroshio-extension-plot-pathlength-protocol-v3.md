# Kuroshio Extension regional plotted pathlength v3

## Explicit source-stroke correction

V1 remains frozen atf323484; it rejected unsupported cubic operators before
target calibration. V2 remains frozen atc82442e; it added all cubic geometry
but rejected the original0.600000024-point strokes against its declared
0.5-point maximum, again before any target year/km calibration or products.
Both failures and complete original remain retained privately. The diagnostic
records all three selected drawing objects and their true stroke widths.

V3 preserves v2's entire operator selector, raw command retention, cubic
interpolation/analytic-extrema algorithm, run topology and calibration. The
only numerical-contract correction is a declared maximum0.75-point stroke.
No width is clamped or rewritten: retain each exact original stroke width.
No target calibrated length range or series has been inspected before this
declaration. Freeze v3 producer/tests/protocol/preflight and all exact v1/v2
dependencies in Git before actual extraction.

## Reading-allowance justification

At the independently inspected labelled axes, half a0.75-point stroke is
under31km and under0.067year. Add5km rounding, the sub-1km cubic graphic
approximation bound, calibration tolerances and finite PDF precision:
the unchanged +/-50km and +/-0.1year editorial graph-reading allowances
still cover this declared graphics contract. These are not source-provided
errors, physical measurement uncertainties or confidence intervals.

Everything else follows the explicit frozen v2 protocol: keep every original
line/cubic command, original graph knot, derived curve reading and explicit
break; no arbitrary decimation, gap bridging, sample-cadence inference,
calendar timestamps, geographic centerline, physical width, full-current
rank, seasonal playback or physical annual extrema. The plotted range is the
range of the published regional graphic between141E and153E.

Default replay uses the public factual raw-command mirror offline. Optional
original replay requires all pinned private original bytes and PyMuPDF1.28.2.
Never overwrite products; any post-extraction correction requires a new
version. Run synthetic tests before extraction and independent actual
calibration/all-command accounting afterward. Inspect the actual chart;
query/table/map-card integration, native/WASM equality, keyboard/phone access
and fresh remote replay remain required before completed delivery. Local work
is sequential, below-normal priority, one logical CPU; retain branch/PR83.
