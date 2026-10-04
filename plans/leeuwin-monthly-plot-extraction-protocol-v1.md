# Leeuwin a101 monthly graph extraction v1

Editorial reading of Deng et al. (2008), Figure 7d, printed page 144.
It is a historical monthly composite at one crossing, not a current footprint.

1. Pin the published PDF bytes and embedded image object 40 (2126 by 1487).
   Convert its CMYK image to RGB, then luminance. Retain the decoded image hash.
2. Use Figure 7d only: solid a101 curve. Plot calibration is y=780.5 at 140 km
   and y=1392.5 at 40 km. Source x tick centers for months 1-12 are stored in
   the extraction configuration. They were checked against the native raster.
3. Read a five-column strip centered at each month tick, dark luminance <100,
   y=790..1139. Exclude the upper-right legend. For December use x=2092, inside
   the plot border; its offset from the month tick is recorded. Select the
   contiguous y band with most dark pixels; this excludes the right-axis tick.
4. Convert the median selected y to km with the linear axis calibration. Round
   display values to the nearest kilometre. Preserve raw pixel bands and values.
5. Use a conservative 3 km reading margin covering line thickness, strip width,
   calibration and rounding. This is a graph-extraction allowance, not a
   confidence interval, source fitting error, temporal spread or physical bound.
   Revisit it if image, calibration, curve, threshold or sampling method changes.
6. Keep April ~132 km and September ~89 km prose claims separately and check
   that they fall inside their graph-reading intervals. Do not substitute them
   into the extracted curve. July/September intervals overlap, so do not infer
   a uniquely narrowest month from the graph readings.
7. Preserve w=1.89*L*cos(theta), theta=43.45 degrees, mean of per-cycle fitted
   widths and the July/August 2002 source-period discrepancy. No exact FWHM,
   occupied date, fixed layer or lateral-edge coordinates are inferred.
8. A chart may step through the 12 extracted values with explicit play/pause.
   Show the reading interval and historical/local scope. Do not morph map
   geometry, interpolate intermediate months, wrap years or call this live data.
9. Full-current width/ranking, annual physical extrema and confidence flags stay
   false. Source measurements retain their separate review and admission gates.
   Regenerate deterministically offline; acquire no source during regeneration.
