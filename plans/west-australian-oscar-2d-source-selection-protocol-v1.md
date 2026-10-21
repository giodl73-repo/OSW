# Offshore West Australian context: two-dimensional OSCAR intake v1

20 October 2026. Declared before requesting this surrounding velocity cube.
The existing 32 S 2013 section and its diagnostics have been inspected.
This is an exploratory extension, not blinded selection or physical admission.

## Fixed support

Use the same NOAA OceanWatch ERDDAP dataset `yearly_336c_0b32_9cd3`, OSCAR
version2017.0, variables u/v, nominal depth15 m, and every original timestamp
from2013-01-01 through2013-12-28. Preserve all72 timestamps, including the
source's nonuniform five/six-day gaps. Do not fabricate a73rd record.

Request latitude28–36 S and longitude60–116 E at every native one-third-degree
grid position:25 latitudes by169 longitudes per time. This is an8-degree
surrounding latitude window around the already retained32 S section, using
its exact longitude range. Bounds are an analysis viewport, not named-current
endpoints or edges. Keep the modern broad offshore northward definition
separate from the coastal southward Leeuwin, historical cyclonic-stream naming
and deeper undercurrents. No claim that this viewport covers the whole current.

Retain the exact CSV and metadata response in a deterministic ZIP with an
acquisition receipt, original byte counts/checksums, requested/resolved URLs,
HTTP status and UTC acquisition times. Metadata must retain the same version,
depth, component units and explicit permission for free redistribution.
Do not redistribute glossary prose, source maps or copyrighted article figures.

## Required checks

- Reject unexpected headers, coordinates, duplicate/missing rows or infinities.
  Require all72 original times, the full25 by169 rectangular native grid and
  the same coordinate sequence for both components.
- Missing u/v remain individually missing. Record finite-pair, one-component
  missing and both-missing counts. Do not fill one component from the other.
- The32 S slice must reproduce every retained section u/v value, finite float64
  bits (including signed zero), mask, time and coordinate. A changed provider
  value is a discrepancy requiring inspection, not permission to repin history.
- Preserve all source rows, including southern/eastern edges and missing cells.
  Reading a plotted vector does not establish a connected current corridor.

## Derived source comparison

For an independent twelve-panel context figure only, calculate cellwise monthly
means from dates with both components finite, requiring at least five pairs
in that month, matching the prior32 S operator. Missing months/cells remain
null; retain paired counts and all contributing source times. Check the derived
central row against the prior twelve monthly profiles. A monthly mean field
does not mean an instantaneous observation, independent sample, width or axis.

Use the same fixed northward-component color scale of -0.2 to+0.2m/s in all
panels, explicitly marking out-of-scale values; show east/north vector direction
with a fixed0.1m/s key and a prespecified4-column/2-row display stride. Mark32 S
as the comparison section. Display thinning does not change calculations or
source resolution. Axis degrees are geographic coordinates, not equal-distance
Cartesian metres. No current footprint or geographical state membership follows.

This intake supplies source context for a later, separately declared corridor
or axis method. It admits no numeric length, current width, seasonal range,
centerline, mask-derived boundary or canonical current identity/measurement.
