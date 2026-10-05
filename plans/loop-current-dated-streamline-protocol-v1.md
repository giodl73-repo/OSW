# Loop Current dated surface streamline experiment

Status: local diagnostic experiment; scientific, endpoint, source-use and canonical
admission reviews remain open. This implements the general current measurement
protocol's source, layer, time, gate and sensitivity rules.

## Quantity and source

Use the checksum-pinned NOAA LSA RADS daily absolute surface geostrophic
`ugos` and `vgos` fields for each explicitly pinned date, using its source time
bounds. Baseline: 25 September 2026 UTC (26 September excluded). Repeat selection:
15 January, April, July and October 2025, declared before tracing. Apply identical
gates, seed selection, step sizes, thresholds and missing-cell rules on every date;
retain failures and do not substitute a successful neighboring seed.
Decode the original packed values, preserve missing cells, and bilinearly sample
only when all four contributing cells are finite. The 0.25-degree grid is an
analysis grid, not a claim of independently resolved features at that spacing.
The product is Experimental. No subsurface or ageostrophic current is inferred.

Manta et al. (2023), doi:10.3389/fmars.2023.1156159, sections 2.2, 3.1 and 4.1,
describe open Loop Current paths connecting the Yucatan Channel and Florida
Straits, comparing a demeaned 0.17 m contour with a maximum-velocity streamline.
The NOAA file has SLA and absolute velocity, but lacks absolute dynamic
topography. Do not apply the 0.17 m method to SLA or label this experiment a
reproduction of the study's maximum-velocity contour algorithm.

## Editorial gateway and integration choices

The initial Yucatan gate is 21.875 N, 86.875–85.125 W, sampled at native
0.25-degree longitude centers. Select the largest northward velocity among
finite northward samples before tracing; never choose the seed by whether its
trace succeeds. This near-channel gate is an OSW numerical convention, not a
published endpoint coordinate. The downstream gate is the first eastward crossing
of 81.5 W within 23–25 N in the Florida Straits. These regional gates require
review against channel bathymetry and alternative section conventions.

Integrate the normalized velocity direction with a WGS84 geodesic midpoint
step of 10 km. Test 5 and 20 km steps and seed longitude offsets -0.25, -0.125,
+0.125, +0.25 degrees; retain every result, including failures. Nominal minimum
speed is 0.10 m/s; also test 0.05 and 0.15 m/s. Stop on missing source cells,
weak current, return south through the initial gate, leaving the declared
regional field, or a 4000 km integration cap. Crossing outside the Florida gate
does not establish a connected route. Clip the successful final step to the
gate using linear longitude/latitude interpolation; measure every stored
coordinate leg with the WGS84 geodesic inverse.

## Measurement and limits

Record raw diagnostic length at 0.1 km; display a successful nominal trace rounded
to 100 km. A failed trace has a travelled diagnostic distance but no open-path
length. Failed neighboring seeds cannot be discarded to manufacture an uncertainty
range. No confidence interval, seasonal range, annual extrema, width, footprint,
named-eddy match or whole-current length is admitted. One frozen-time streamline
is not a particle trajectory and selecting the strongest inflow does not prove
maximum mean speed along the full path. Closed recirculations are excluded by
the gateway test/cap; no ring is appended to complete a route.

Before admission: inspect the geographic path and gateway sensitivity, compare
an independently sourced ADT maximum-velocity contour, repeat dates and retained
failures, verify effective resolution, and complete scientific and source-use
review. Keep published study statistics separate from this dated diagnostic.

## Recorded-date extension v1.1

Quarterly-spaced snapshots cover four days, not the year. Report each method
and failure by its actual date. Do not infer phases, interpolate missing days,
call their numerical spread an annual range, or pool dates into a ranked length.
Source product/version changes must be visible alongside recorded dates.
