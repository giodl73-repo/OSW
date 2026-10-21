# Offshore source streamlines: fixed regional test v1

20 October 2026. Exploratory method, declared before running these traces.
The source fields, twelve-panel overview and old32S sections are already known.
This is a numerical regional-path investigation, not blinded selection,
whole-current length admission or proof of a named-current axis.

## Fixed fields and seeds

Use the pinned two-dimensional OSCAR2017.0 intake only:28–36S,60–116E,
nominal15m, all72retained2013times. Attempt the twelve existing paired monthly
means (at least five pairs/cell), plus a separate equal-record source-period
mean requiring all72pairs/cell. The latter is not a climatology, time-weighted
calendar mean, instantaneous field or independent observation.

For each of these13fields, select the maximum northward component on32S
within80–105E, exactly the old section's search window. Ties use the westernmost
source index. Require peak v>=0.02m/s. Use that native seed and its immediate
western/eastern native neighbours, retaining every failed/weak/missing seed.
Each seed must also have v>=0.02m/s; no alternate maximum or sign reversal.
Combine with nominal5,10,20km integration steps:13×3×3=117attempts.
The10km/central-seed case is primary, fixed before outcomes are calculated.

## Discrete trajectory and source support

At each state interpolate east/north monthly mean components bilinearly in
the native longitude/latitude grid. All four cell corners must have eligible
paired support, including zero-weight corners. Do not interpolate across a
missing corner, fill a component, extrapolate beyond the viewport or use a
different field for a failed case.

Advance a first-order Euler approximation in longitude/latitude, using local
WGS84 meridional/prime-vertical radii to convert a direction-normalized vector
and the nominal spatial step to angular increments. Integrate forward and
backward from the same seed. This is a discrete streamline of a fixed mean
field, not a particle trajectory, travel time or continuous-flow certification.
The between-state interpolation is linear in geographic coordinates; reported
distance sums WGS84 inverse-geodesic separations between successive states.
It is a polygonal approximation whose step dependence must remain visible.

For each proposed segment, conservatively require every source cell in its
longitude/latitude bounding rectangle to have finite paired corners. This
rectangle can reject a valid curve near a mask; it must never bridge an
unexamined masked cell. Preserve the first rejected support location/reason.
Require speed>=0.005m/s at accepted states and proposed endpoints. This is a
numerical stagnation guard, not an observational detection threshold; it does
not prove the continuous speed stays above that value between states.

Clip the first viewport crossing analytically on the angular segment. Forward
must reach28S and backward36S, with original-field v>0 at both matching gates.
An east/west exit, opposite latitude exit, non-northward endpoint, missing cell
or weak state fails that leg. Gate coordinates are analysis conventions, not
physical current endpoints. Never close at a missing or arbitrary map edge.

After300km on a leg, terminate a return within max(20km, twice the nominal
step) of its seed as a **seed-return guard**, not an identified closed eddy.
Terminate before a proposed step would exceed10,000km per leg; this is a
computational limit, not a physical upper bound. Keep all partial traces and
their distances/reasons. Do not select a different lobe or extend a failed trace.

## Length, precision and presentation

A conditional regional length exists only when both legs reach their matching
gates. Sum both full-precision polygonal distances, count the seed once in
the combined geometry, and preserve all117attempts. Partial traced distances
are diagnostic support only, never substitute current-length estimates.

Only derived trace readbacks are quantized: longitude/latitude8decimal places,
calculated distances6decimal places inkm and interpolated endpoint components
8decimal places inm/s. Source monthly fields/anchor values remain unchanged;
new source-period means retain their original computed values. Decisions and
length calculations precede quantization. Public length labels round to10km.
These digits are calculation precision, not physical resolving power. Nominal
integration steps smaller than the native one-third-degree grid do not add
observations or source resolution. Step/seed alternatives are sensitivity
assumptions, not a confidence interval, seasonal extrema or extra observations.

Show primary paths, gate/seed conventions and all failure categories, plus
separate step/seed outcomes. Do not imply that successful paths identify the
West Australian Current rather than another source-field branch or eddy flank.
Current association, full-current length/width, physical seasonal ranges,
geographic current footprints, eddy identities and OSW physical joins remain
unadmitted. Repeated failures mean this method lacks a supported candidate;
they do not establish that the current is absent or disconnected in nature.
