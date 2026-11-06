# Durante2026 source-view protocol v1

20 October 2026, after verified source intake and schema/finite-value/time
inspection, before generating source maps or deriving geometric distances.
This is exploratory source visualization. Source metadata/clock/composite
coordinates are already known; no blinded claim. Do not interpret a figure
as a new current measurement merely because it is geographic.

## Fixed views

1. Show both archived surface composites, Cmax/Umax/Vmax/CurAxisPositive and
   Cmin/Umin/Vmin/CurAxisNegative. Use their complete supplied xduf/yduf grid
   after the verified HDF5-to-MATLAB dimension reversal. Preserve source masks.
   Keep all source coordinate points in view; do not crop to the author's
   northern21.4N plotting window, which hides much of the supplied axes.
2. Use native-cell speed color, no interpolation or regridding; one common
   speed scale from0to the larger finite maximum of Cmax/Cmin. Gray denotes
   missing speed, not a coastline. No private coastline dependency. State
   longitude/latitude and local map aspect. No occupied-current polygon.
3. Direction-only arrows at fixed native stride4 use paired finite U/V;
   preserve absent vectors and zero velocity rather than assigning direction.
   Do not claim the coordinate grid step is effective observational resolution.
4. Show every paired finite source CurAxis coordinate as a separate point.
   Do not join points, measure their order, extrapolate endpoints or call them
   a complete Loop Current axis. They extend south of Yucatan and their source
   maximum latitude is below23.2N; that directly prevents treating these arrays
   as a Yucatan-to-Florida Loop path. The author uses pointwise omitnan means;
   underlying daily coordinates, member-specific support and independent clock
   association are not supplied here. Surface-composite membership support
   is also not supplied; the68/53source indices are axis-mean selection indices,
   not asserted numbers of independent surface-composite observations.
5. Show the three original source clocks separately using all finite native
   entries. Calendar timezone is unspecified. Contiguous daily blocks may be
   drawn only for adjacent source indices whose serial dates differ by exactly
   one day. Break on missing timestamps or calendar gaps; do not fill times
   from another clock. Retain the missing tisp index3462as an index-only note,
   with no calendar assigned. All11902htimefand4111tid/tispentries remain in
   source quality; one tisp time is nonfinite.

## Required evidence and limits

Pin the intake protocol/operator, exact source/metadata and source-quality
bytes, this view protocol, generator and output hashes. Preserve transformed
plot inputs in a machine-readable source-view record with explicit masks,
units, source field names, all source axis points and time-block indices. No
author source curves/images are reused. Source-defined conditional composites
are neither dated snapshots, seasons, forecasts, full-path tracks nor original
CMEMS/Canek observations. No new length, width, uncertainty/range, eddy identity,
route admission or OSW-state intersection is inferred from these views.

## Index-basis clarification after source checks

OSW JSON array positions and clock-block positions are zero-based. The missing
tisp position3462 therefore corresponds to MATLAB index3463. Original source
phase-selection and grid-mask indices remain one-based MATLAB indices; they
are not silently shifted. Encode each convention in the machine-readable
record. This clarification changes no source value, mask, date or selection.
The preceding view-protocol SHA256 was
`4a0c48f63fb7ba6573564ff173a4048a347d09a437f474579efabb9f3866eec7`.
