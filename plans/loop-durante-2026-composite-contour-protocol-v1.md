# Loop Current composite contour-path measurement v1

20 October 2026. Exploratory protocol recorded after source intake and the
surface speed/coordinate/clock sheet were inspected, before contour extraction
or geometric length calculations. Source means and masks are already known;
this is not a blinded study. Same continuing branch and draft PR83.

## Object and evidence

Measure the open northern-gulf arc of an absolute dynamic topography (ADT)
contour between two explicitly editorial gateways, separately in the positive
and negative author surface composites. This is a composite contour path,
not the length of a daily current, a mean of daily path lengths, a velocity
axis, a seasonal range, a width or a whole-current ranked estimate.

Use the already retained Durante2026 v0 original
`research/source-data/loop-durante-2026-v0/Figures2_4_processed.mat`, SHA256
`316daa53a45fc6b2817abfa4ba8da76344323d20c84c781bfa8705163235e073`.
Run the source verifier; preserve its exact shape/mask/coordinate association.
Use ADTmax/Umax/Vmax/Cmax and ADTmin/Umin/Vmin/Cmin on xduf/yduf. Do not use
ADT*_a anomalies or the incomplete CurAxis means as a route. No other MAT
member is selected. Source means do not supply per-member uncertainty or
effective resolution. Documentary license/version disagreements remain visible.

The retained plotting.zip, SHA256
`ef9e395e0d422be37f460c0b95a290fe7ba31258f60218754dd911f9ccfe94aa`,
`plotting/plot_Figures2_4.m`, function plotCompositeMap, plots absolute ADT at
0.55m. The source dictionary identifies absolute ADT in metres. This supports
a fixed plotted guide, not independent validation of its physical interpretation.
Do not borrow the demeaned daily0.17m or maximum-velocity methods as its name.

## Fixed experiment: all54 cases

Use both phases and absolute contour levels **0.50,0.55,0.60m**. The nominal
level is the author's0.55m guide; neighbours are editorial sensitivity, not
uncertainty or an optimized search. Do not choose a level after seeing lengths.

Retain the existing OSW experimental gateway convention as the nominal:
Yucatan horizontal gate21.875N,86.875–85.125W; Florida vertical gate81.5W,
23–25N. These are regional measurement conventions, not verified named-flow
origins/terminations, bathymetric gates or instrument sections.

Independently shift the Yucatan latitude by−0.125,0,+0.125degrees and Florida
longitude by−0.125,0,+0.125degrees. These are one supplied-grid interval
perturbations; they do not describe boundary error or effective resolution.
Keep longitude bounds of the Yucatan gate and latitude bounds of the Florida
gate fixed. Thus2phases×3levels×3Yucatan×3Florida=54cases, including every
failure. No substitute gate after a failed connection.

## Contours, clipping and geometry

Use pinned contourpy1.3.3 serial algorithm, Separate lines, corner_mask=False
on the native finite ADT array. Every quadrilateral with a missing ADT corner
is excluded. No filling, smoothing, regridding or contour joining. Clip every
line to98W–the selected Florida longitude and the selected Yucatan latitude–31N.
Keep all line parts, including failed/disconnected/closed parts, with original
contour index, source closure and clipping counts. Point-only touches are
counted separately. A clipped closed ring is not a gateway path. A gateway
arc clipped from a source closed contour may be measured as an open arc;
record the source closure and never add its southern return or detached ring.

Eligible open parts must have one endpoint on each selected gate (tolerance
1e−7degrees) and satisfy the fixed gate bounds. Orient Yucatan to Florida and
retain coordinates rounded to six decimals. No endpoint extrapolation,
bridge across masks, simplification, shortest-path choice or manual edit.
Each connected component remains separate. More than one eligible component
in a case is ambiguous: retain all, do not silently select one.

Sum WGS84 shortest geodesic legs over exactly the stored coordinates. Retain
calculation readback to0.1km, public path lengths to100km. Any displayed
geodesic densification is at most10km. Intersect that same densified route
against the pinned coarse OSW land mask and retain any positive-length
intersection. A coarse land crossing blocks a supported path; a clear result
does not establish high-resolution coastal or bathymetric clearance.

## Velocity support

At both endpoints require strict four-corner joint finite U/V bilinear
support, northward entry V>0 and eastward exit U>0. Split every geodesic leg
into equal pieces of at most10km and sample their midpoints with the same
strict four-corner rule. Save source row/column, weights, interpolated U/V,
piece length, geodesic tangent and along-path component for every sample.
Never drop missing or opposing samples to improve a mean. Require all sampled
along-path components positive and length-weighted vector speed≥0.10m/s.
This is a declared consistency test, not validation of a physical current core.
Keep original mean C separately; never substitute it for hypot(mean U,mean V).

Retain all rejection reasons, every geometric path length and every sample;
only a uniquely supported path gets a supported contour-path length. Failed
and ambiguous cases keep that field null. Do not report a partial failed trace
as a successful full gate-to-gate path.

## Reporting and integration

Show all54outcomes in the atlas source evidence with a visible nominal case
per phase and selectors/tables for every contour/gateway case. Use the shared
map/card/query interface and retain complete records in the checked index.
Plot both phases, all levels, gates, rejected components and failure counts;
provide accessible descriptions and source/method links. Color alone cannot
carry eligibility. Display source speed with a common scale; source masks
are missing data, not coastline. Preserve other owners and old measurements.

Report separate phase and gate/level sensitivity, including failure counts.
An all-case min/max is only an experiment envelope, not annual variability,
confidence bounds or evidence the two phases bound all current configurations.
If either nominal case is unresolved, say so. Do not manufacture an envelope
by ignoring failures or treating correlated composites as independent samples.

Pin all source, protocol, generator, sampler and atlas-mask bytes. Verify
synthetic gateway ambiguity, masks, reversed paths, tangential direction and
geodesic length, then actual native/WASM records and corruptions before shared
UI delivery. Review scientific scope and evidence through .roles. New data
remain support-only diagnostics; rank, width, reference-route admission,
annual range and physical state intersections remain false until separate
scientific, endpoint and source-use review. Internal roles are not external
scientific review. Keep the live combined full-suite checkout undisturbed.
