# Kuroshio Extension regional plotted pathlength v2

## Explicit PDF operator correction

V1 remains frozen atf323484. Its first original extraction rejected a cubic
PDF operator before any km/year calibration or output. A retained diagnostic
found1532 line and4 cubic commands in three selected drawing objects, with
maximum control-to-chord separation0.518663 PDF point. No calibrated target
range or series was inspected. V2 changes vector support, not axis facts,
regional gates, reading allowances or selection according to a result.

Freeze v2 producer/tests/protocol/preflight and the exact v1 dependencies in
Git before extraction. All v1 source custody, red-panel selector, labelled
axis calibration, approximate time and scientific scope remain applicable.
The original and failed log stay private; publish only factual graph geometry,
attribution, derived graph readings and an accessible length chart.

## Raw commands and graph readings

Keep every selected original line and cubic command, including all four cubic
control/end points at six PDF-point decimals. Split runs at endpoint gaps
over1e-4 point. Sort runs by first x; require no overlap or reversed x.
Preserve distinct equal-x readings and explicit breaks. Require positive
stroke width at most0.5 point, finite coordinates within the reviewed frame,
no fill/closed path, and no operator other than line/cubic.

A line contributes its original endpoints. A cubic contributes its endpoint,
all internal y-derivative roots and a deterministic equal-parameter mesh,
starting at16 intervals. Double the mesh until the conservative linear
interpolation deviation bound is at most0.01 PDF point, failing above1024
intervals. For cubic Bezier B, use max(norm(B''(0)),norm(B''(1)))/(8*n*n).
The bound follows from linear interpolation's second-derivative error bound;
B'' is affine, so its norm maximum is bounded by endpoint norms. All interior
y-stationary points are retained separately to preserve curve extrema.
Require nonnegative x derivative everywhere: check the quadratic derivative
at both ends and at its internal minimum. Reject nonmonotone time curves.

Each reading records the source segment, parameter and whether it is an
original graph knot, cubic interpolation or cubic stationary point. Cubic
control points are not observations. Added graph readings are never counted
as recovered observed samples, daily samples or original graph vertices.
The trace retains original commands; the report records original line/cubic
counts, original-knot count, derived-reading count and run count separately.

Reuse frozen v1 piecewise year calibration, zero/4000km calibration with the
2000km cross-check, positive-half-up10km rounding, +/-50km and +/-0.1year
editorial reading allowances. Store calibrated values to six decimals.
These are graph-reading allowances, not physical errors or confidence limits.
No precise calendar dates, verified source sampling cadence, geographic axis,
width, whole-current rank, seasonal playback or physical annual extrema follow.
The plotted reading range includes exact cubic y-stationary points; it remains
the range of the published graphic, not of all underlying observations.

## Reproduction and delivery

Default build/check replay from the public factual raw-command mirror, offline.
Original extraction/replay separately verifies all original bytes, page count
and PyMuPDF1.28.2. Never overwrite a scientific output. Use a new version for
any numerical correction after actual extraction.

Synthetic tests must include hand-computable linear and curved cubics,
analytic internal extrema, nonmonotone x rejection, adequate mesh error bound,
control-point exclusion, equal-x preservation, multiple runs, line-only v1
agreement and source-scope preservation before actual extraction. Afterward
check original replay, JSON/SVG byte replay and independent actual calibration
and command/readings accounting. Native/WASM query and source/card/chart/table
access still require integration and focused browser proof. Keep one heavy
local job at a time; retain the same branch and PR83. Broad full regression
runs alone only as the final batch gate.
