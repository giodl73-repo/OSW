# Kuroshio daily regional dimensions, protocol v1

Declared2026-10-21 before numerical extraction. Source: Wang, Chen, Mao and
Zhang (2026), doi:10.1038/s41597-026-07275-3; data edition
10.6084/m9.figshare.30267070.v1, CC BY4.0. Attribution accompanies derivatives.

## Selection and scope

Use the latest complete year,2024, all366 day groups, at source levels01,
23 and30 (nominal0.49,109.73 and380.21m). These are levels, not layer averages.
Check all366 groups contain all30 source levels. The other31 years and27 levels
are future extraction work; no32-year climatology is claimed. These are
publisher-identified GLORYS12V1 reanalysis curves, not observed daily boundaries.
No source program is executed. Preserve the complete original with MD5/SHA256
and a byte-exact compressed copy for independent offline reconstruction.

The source uses a30% local-axis-speed boundary along140km normal transects,
sampled7km apart. A farthest-valid-ocean fallback is used when no threshold
crossing occurs; its occurrence is not encoded in these coordinate variables.
Axis and boundaries are smoothed110km and land points excluded. The effective
boundary therefore includes smoothing and potentially censored searches.
No paired unsmoothed velocity threshold, error interval or source fallback flag
can be reconstructed from the coordinate file alone.

## Fixed conventions

1. Treat ordered source vertices as piecewise straight in longitude/latitude.
   Preserve missing vertices as breaks. Never reconnect across a missing point.
2. Intersect each curve with fixed latitude gates using linear interpolation in
   the source coordinate plane. Deduplicate a shared vertex intersection. A
   horizontal overlap, absent crossing or multiple distinct crossings is
   unresolved; do not select an attractive branch or extrapolate.
3. Compute regional axis length only between unique18N and30N crossings, in
   downstream source order. Reject a reversed gate order, missing internal
   vertex or any source segment longer than50km. Preserve rejection reasons
   and gate counts for every day/level. The50km connectivity guard is an OSW
   analysis choice, not a physical uncertainty bound.
4. Width-related measurements are fixed-latitude boundary separations at18.5,
   21.5,24.5,27.5 and29.5N. Require exactly one intersection per axis/left/right
   curve, finite adjacent source vertices and the axis between the two edges.
   Reject source segments longer than50km. Measure the WGS84 inverse geodesic
   between the boundary intersections. This is an oblique fixed-section span,
   not a perpendicular-to-flow width or a whole-current representative width.
   Do not pair separate boundary arrays by index.
5. Use all retained days for each section/level's annual and calendar-month
   sample min/median/max/count. Do not pool sections or levels. These are
   empirical extrema within one modeled year, not climate extrema, confidence
   intervals, annual uncertainty or an inferred physical seasonal envelope.
6. The visual panels use the first day of each calendar month, selected in
   advance, at0.49m. They are dated model snapshots, not monthly mean maps.
   Show axis and both boundaries separately; preserve gaps. Do not interpolate
   frames, buffer a line, or label a span as an occupied polygon.
7. Keep unrounded calculations for admission decisions; round retained km
   readbacks to six decimals and displayed dimensions to roughly10km. Coordinate
   precision does not establish accuracy. The product's1/12-degree velocity
   grid,7km sampling and smoothing prevent a sub-km accuracy claim.

## Admission limits

This report closes a source/reproducible regional time-series gap. It does not
change accepted identities, source-reported whole-current length ranking,
scoped-width inventory, physical state passage, NASA model identification or
seasonal playback eligibility. Integration into the native/WASM query and atlas
requires explicit typed records and UI verification; an unintegrated report
must not be described as shipped atlas coverage.
