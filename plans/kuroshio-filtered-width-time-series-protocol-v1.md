# Kuroshio filtered width curve readings v1

Declared 2026-10-18 after the original Figure7 and caption, vector-path
metadata and axis locations were inspected, before new width readings were
calculated. This is an editorial plot extraction, not a blinded experiment.

## Source and measured quantity

Use the retained published Liu and Gan (2012) PDF, SHA256
`a452007ff7f3b0051f811ba8172e9ae7932642ed1916a29c779db6335772203b`.
Figure7a is on printed page30/PDF6. Its quantity is the source's half-year
filtered mean section width along the East China Sea stream from122–130E.
Retain the existing source method: weekly surface geostrophic diagnosis,
axis-normal boundaries at0.1m/s, then spatial/temporal summaries. This is
not a fixed-depth current width, raw monthly observation or whole-current
dimension. It remains separate from the four seasonal spatial profiles and
the three regional prose means already extracted.

The caption specifies half-year filtering; kernel, exact window alignment,
endpoint treatment and detailed averaging weights are unresolved. Do not
infer them, undo the filter, or calculate an unfiltered monthly width.

## Vector extraction and calibration

1. Pin the source PDF, retained scope audit, acquisition receipt, this
   protocol and the new configuration. Select only Figure7a paths474–476
   on page index5: solid, unfilled dark strokes of width approximately
   1.711PDF points with113/576/66 straight segments. Other panels, axis
   ticks, thin grid strokes and text are excluded.
2. Preserve path/segment order and strictly increasing x within each
   segment. Test adjacent endpoints within0.0001 PDF points; retain any
   failed connection as an explicit source-path break, with no added link.
   Readings within intact segments remain possible. A missing or ambiguous
   crossing is unresolved; never connect separate curves or sort points.
3. The frame is approximately x150.258–456.107 and y313.295–373.373 PDF
   points. Top/bottom correspond to230/180km. Recover and validate all17
   printed-year grid stems1993–2009. Use piecewise interpolation between
   adjacent labeled-year ticks, preserving their actual spacing rather
   than assuming UTC calendar-day spacing from the plot.
4. Read all192 month-midpoint *plot coordinates*: year+(month−0.5)/12 for
   1993–2008. Month names label positions between printed-year ticks.
   They are not exact original observation timestamps or proof of a monthly
   mean. Keep decimal plot year, approximate year/month label, target PDF
   coordinate, source bracketing segments and interpolation fraction.
5. At each target x, interpolate only within a source line segment.
   A shared endpoint is one reading if both segments agree within0.0001
   PDF points; multiple distinct y values remain unresolved. No smoothing,
   gap filling, peak selection or curve replacement is permitted.
6. Convert y using the declared230–180km calibration. Round displayed
   width to5km. Retain the unrounded calculation and a conservative±5km
   editorial graph-reading allowance for stroke extent, calibration and
   rounding. Also retain±0.05 plot years as a graphical coordinate
   allowance, not exact timestamp precision or filter-window support.

## Interpretation, display and admission

These are monthly samples of a published half-year-filtered curve, not192
independent observations or raw monthly means. Unknown kernel, weights,
physical error and geographic boundary positions stay unknown. Reading
allowances are not source uncertainty, physical variability or confidence.

Show all readings and missing statuses in a time plot, a data table and
queryable source record. Keep source filtering beside the values. Do not
pool them into an annual seasonal climatology, calculate annual extrema,
invent seasonal months, buffer a geographic route or infer map edges.
Do not replace the existing218/207/210km prose summaries or average these
samples to claim their reproduction. No physical ranking or whole-current
dimension follows. Original source images remain private local evidence;
publish only OSW-derived data/figures and provenance.
