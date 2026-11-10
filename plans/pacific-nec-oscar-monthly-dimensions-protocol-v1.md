# Pacific NEC monthly regional dimensions from OSCAR

## Purpose and scope

Fill the missing temporal depth of the Pacific North Equatorial Current with
reproducible monthly regional-axis lengths and section spans. These are OSW
diagnostics of one source product, pending physical review and admission. They
do not replace the whole-current length gap or the installed nominal width.
Follow M01–M13 and the current width protocol; preserve every failed case.

The primary-source review is recorded in
`research/pacific-nec-monthly-dimensions-source-review-v1.json`. Liu and Zhou's
8–18N integration window provides named-flow context. Their surface and
depth-integrated axes remain distinct. OSCAR is a separate product and the
operator below is an OSW choice, not a reproduction of their calculations.

## Source and fixed gates

Use only NOAA ERDDAP's OSCAR2017.0 archive, dataset
`yearly_336c_0b32_9cd3`, variables u/v in m/s, nominal15m coordinate, native
one-third-degree grid. Request2013 only, all five-day samples, latitude4–26N
and longitude130–240E (120W). Keep the dateline unwrapped during calculations.
130E is an open-ocean regional gate east of the bifurcation, not a termination.
120W is an editorial gate associated with the paper's stable westward-flow
discussion, not an inferred origin. Neither crop boundary establishes a
whole-current endpoint. This pilot is one year, not a seasonal climatology.

Run acquisition and processing in one low-priority cloud CPU. Bound the provider
CSV to256MiB and1,596,744 rows (72×67×331). Keep originals on cloud; return
only compact receipts, derived diagnostics and images. No local field processing,
native/WASM build, browser automation, packet/index changes or main update.
Record exact URL, response hash/size, complete license and actual time samples.
Reject changed units/version/grid, duplicate coordinates, incomplete cubes,
infinite values or missing months. Preserve provider NaNs.

## Monthly mean and regional axis

Group samples by their UTC timestamp month and take equal-sample means at each
grid point, retaining count and missing-count fields. A monthly mean is valid
only when all that month's samples are finite in both vector components.
It is neither a daily time-weighted mean nor a mean of instantaneous lengths.

At each longitude, calculate a trapezoidal latitude centroid of westward-only
zonal speed, w=max(-u,0), in8–18N. This gives an explicitly windowed diagnostic
axis; it is not a streamline, fastest-core ridge or whole-width centroid.
Require all window cells, positive integrated speed, a westward share of at
least0.8 of integrated |u|, mean westward speed at least0.02m/s, and interpolated
u at the centroid below zero. Record interpolated u/v for interpretation.
Do not bridge missing or rejected columns. Withhold the full regional length
unless every longitude and both fixed gates qualify and adjacent axis latitudes
differ by no more than1degree. Retain partial traces and rejection reasons.
Use WGS84 shortest geodesic legs, normalizing longitude only at export/display;
no ambiguous180degree leg is present. Round valid nominal lengths to100km.

Retain all108 sensitivity cases: three latitude windows (8–18N nominal,
7–19N,9–17N) crossed with maximum adjacent jumps0.5,1,2degrees, for12months.
They are numerical/operator sensitivity, not physical error bars or independent
observations. Do not choose the best-looking outcome after calculation.

## Section spans and range meanings

At137E,180E and220E, choose the largest westward peak within8–18N, requiring
at least0.05m/s; ties are ambiguous and withheld. Follow that connected westward
component toward both sides within the4–26N halo. Interpolate the first zero
crossings. Missing cells or the halo boundary before a crossing produce an
explicitly censored/withheld paired span, never zero or an extrapolated edge.
Compute WGS84 meridional edge-to-edge distance. This is a fixed-meridian zonal
velocity component span, not diagnosed flow-normal width or uniform current width.
Retain threshold-core sensitivity spans at0.025 and0.05m/s with the same peak;
they are distinct operators, not physical uncertainty. Preserve peak/vector
values, coordinates, source month and every failure. Round spans to10km.

Only twelve valid nominal months can establish a complete2013 monthly-mean
regional length range or a complete corresponding section-span range. Otherwise
label the observed valid-month span partial and list omitted months. No annual
whole-current range, climatological bounds or numerical uncertainty is inferred.
Playback may show only the available dated product diagnostics and visibly mark
missing months. It cannot invent monthly routes from endpoint interpolation.

## Required visualization and delivery

Generate a standalone diagnostic figure with all12 dated regional traces on a
longitude/latitude grid, qualified and failed outcomes, and monthly section
spans or missing markers at all three meridians. Show source, layer, year,
regional gates and range meaning. Inspect the actual figure before admission.
After source/physical review, integrate the same immutable coordinates and
readings into Rust/WASM query collections, current cards, dashboard coverage and
the OSW atlas with month selection; validate source links and both viewports.
This acquisition job alone admits no measurements and installs no data.
