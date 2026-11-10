# Three southern-basin component climatologies

Declared 2026-10-14 before acquiring the multi-year fields. Extends the existing
South Atlantic 30 W, South Pacific 100 W and South Indian 80 E section diagnostics.
Their domains, peak-search windows, direction and contextual source audits are
copied from the checked 2013 preflight. No window is fitted to the new results.

1. Acquire the archived ESR OSCAR 2017.0 vectors from the NOAA PIFSC mirror,
   nominal 15 m coordinate, native one-third-degree grid, 1995–2016. Retain original
   CSVs, metadata, license, request URLs and checksums. This is a satellite-derived
   near-surface product, not direct observations at a fixed 15 m instrument depth.
2. Preserve any returned boundary record outside the analysis years in the raw
   source, exclude it from means, and list its actual timestamp. Report intervals
   other than five or six days. Do not interpolate missing time or vectors.
3. At each native cell, calculate each year-month vector mean from at least five
   paired u/v records. Both components use the same records. Retain source times,
   valid-pair counts and missing values.
4. Calculate each calendar-month climatological vector as the equal-weight mean
   of at least 18 valid year-month vector means. Both components use the same years.
   Retain valid-year lists. Do not pool all original samples with unequal weights.
5. Independently apply the existing contiguous component operator to each yearly
   monthly mean and each climatological mean. Choose the strongest eastward peak
   inside the declared search window, requiring 0.02 m/s. Find the nearest adjacent
   40%, 50% and 60% crossings on both sides. Missing data, disconnected peaks and
   domain edges must not be bridged. Search-window bounds are not velocity edges.
6. Preserve WGS84 distances, native crossing brackets and resolution flags. Display
   the nominal span to 10 km; retain threshold sensitivity separately. Flag crossings
   outside the contextual search window without diagnosing their physical identity.
7. Preserve every yearly result, including nulls. For each calendar month, report
   the number of resolved years and conditional finite min/max of rounded yearly
   monthly-mean spans. These are not confidence intervals, error bars, population
   extrema or physical annual width ranges. A climatological-mean span is not the
   mean of yearly spans. Do not pool different basins or their widths.
8. Cross-check all 2013 vectors and monthly profiles against the independently
   archived existing 2013 sections. Reconstruct the new outputs from original bytes.
9. Maps show local paired section boundaries only. Keep current association,
   flow-normal boundaries, whole-current dimensions, width ranks, physical annual
   extrema and seasonal footprint playback ineligible. A peak can reflect another
   current, an eddy or combined flow. Temporal coverage does not prove identity.

Each location retains its original geographical, layer and naming caveats. No
intermediate-depth float route or historical transport definition supplies the
identity of this near-surface model peak. Original 2013 diagnostics and all existing
published width records remain available unchanged.
