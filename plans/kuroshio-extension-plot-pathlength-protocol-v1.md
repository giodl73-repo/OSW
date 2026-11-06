# Kuroshio Extension regional plotted pathlength v1

## Prospective scope

Freeze this protocol, producer, synthetic tests, reviewed source facts and
preflight in Git before extracting/calibrating the red data trace. Original
pages1,3,4 and black axis strokes were inspected first; no numerical series
has yet been extracted. Retain failures; corrections require a new version.

Qiu, Chen and Oka2023, doi10.1029/2023GL103548, Figure2a, PDF page4,
plots upstream pathlength integrated between141E and153E. This is a regional
author-plotted length series, not a whole-current measurement or new
geographic centerline. Preserve the distinction from upstream Kuroshio,
the four-component KE index, width, transport and recirculation strength.

## Original and vector selector

Verify the complete private original's exact SHA256, byte count and nine-page
count. Use PyMuPDF1.28.2, top-left PDF-point coordinates. On page index3,
select red strokes (RGB1,0,0 within1e-6), no fill, whose entire bounds lie
inside the reviewed Figure2a frame with0.02-point tolerance. Refuse any
unsupported curve/rectangle operation, filled/closed path or nonfinite
coordinate. Require positive stroke width no greater than0.5 PDF point.
Keep every selected line segment, drawing/run identifier and
vertex; no decimation, peak picking, smoothing or gap bridging.

Split runs where successive segment endpoints differ by over1e-4 point.
Sort runs by their first x position; require nondecreasing x within
each run, no reversed/overlapping runs, and at least one run. Equal-x
vertices from finite plotting precision remain distinct readings. Retain an
explicit break between runs; never average duplicate x values or silently
repair topology. Fail rather than adapt the selector after seeing values.
Keep the factual vector trace and its original-source receipt publicly;
retain the complete article privately. Default numerical replay uses that
trace offline; optional original replay repeats extraction and compares bytes.

## Calibration and reading allowances

Source facts pin the six labelled year major ticks and three labelled length
ticks, located from black axis strokes separately from the red curve. Map y
linearly using0 and4000km; verify the2000km intermediate tick within1km.
Map x piecewise linearly between adjacent year ticks; use the nearest outer
pair only for extrapolation within the plot frame. Do not treat minor ticks
as verified calendar dates or infer a daily cadence from the underlying SSH
product. Retain PDF coordinates at six decimals and approximate fractional
years at six decimals, with an explicit +/-0.1-year editorial reading allowance.

Round each length reading to nearest10km, positive half up. Give each reading
an editorial +/-50km allowance covering stroke thickness, calibration and
rounding. At the reviewed axis scale, a0.5-point maximum stroke contributes
about21km half-width; coordinate/calibration tolerance and5km rounding remain
within50km. Its half-width in time is under0.05year, within0.1year. These
are declared editorial allowances; they are not physical measurement uncertainty, a confidence interval
or source-provided error. Retain unrounded calibrated length to six decimals.
The observed plotted-vertex minimum/maximum describe this figure's retained
trace only. Do not convert their reading allowances into physical annual
extrema, a seasonal envelope or whole-current length rank.

## Required products and verification

Produce a complete sample table with run/index, fractional-year reading,
unrounded and rounded km, explicit reading allowances and both rank and
seasonal eligibility false. Retain all points and breaks in an accessible SVG
with axes, regional gates, source, reading allowances and scope in title/desc
and visible text. The SVG is a length chart, never a mapped geographic path.
Native/WASM integration must expose the complete report and samples plus
source custody and chart links from the mapped current card.

Synthetic tests cover independent calibration anchors/interior points,
rounding ties, descending time, nonfinite/out-of-frame values, empty traces,
broken/overlapping runs, equal-x retention, unsupported PDF operators and scope preservation.
Freeze before actual extraction. Afterward verify original replay, exact
JSON/SVG reproduction, all-point retention, independent calibration checks,
native/WASM record equality and keyboard/phone chart access. Use one local
heavy job at a time, below-normal priority and one logical CPU. Amortize the
delivery rebuild across the batch; retain the continuing branch and PR83.
