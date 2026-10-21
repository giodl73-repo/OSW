# Kuroshio axis-normal boundary spans, v1

Declared 2026-10-21 before computing these normal intersections. The earlier
latitude spans and source curves have been inspected; this is an exploratory
operator declaration, not a blinded registration or external scientific review.

## Source and target

Use the unchanged Wang et al. (2026) dataset edition
10.6084/m9.figshare.30267070.v1, CC BY 4.0, complete 2024 original. Reuse all
366 days, nominal levels 1/23/30 (0.49/109.73/380.21 m), and axis gates
18.5/21.5/24.5/27.5/29.5 N. Preserve the existing latitude-span report and
all inventories. The other 31 years and 27 levels remain outside this edition.

Estimate geometric boundary separation perpendicular to the reconstructed
model axis. The file has no velocity vectors: axis normal is not independently
verified as the instantaneous velocity normal. This is a separate metric from
fixed-latitude spans and published physical current widths.

## Fixed operator

1. Locate the axis with the existing unique latitude-intersection rule. Keep
   missing vertices as breaks, deduplicate shared vertices, reject overlaps,
   multiple/missing gates, reversed local latitude direction and source legs
   longer than 50 km. Never interpolate across a source gap.
2. Walk 7, 14 and 28 km upstream/downstream from that gate in original source
   order. The primary half-window is 14 km; retain all three. Source segment
   lengths use WGS84 inverse geodesics and positions use linear longitude/
   latitude interpolation within the original segment, as an explicit geometric
   approximation. Stop at missing/long segments or endpoints. The WGS84 bearing
   between the two tangent points defines the reconstructed downstream tangent.
   Specifically, use its inverse initial azimuth and apply that geographic
   heading at the gate; this is an explicit local tangent approximation.
3. Construct its WGS84 geodesic normal through the gate. Project boundary points
   into azimuthal equidistant east/north coordinates centred on the gate, then
   resolve along-tangent and right-normal components. Each boundary is processed
   independently; array indices are never paired.
4. Subdivide each valid boundary source segment into ceil(endpoint-distance-km)
   equal source-coordinate pieces (at least one), a nominal 1 km subdivision.
   Detect all sign changes of the
   along-tangent coordinate. Refine each crossing by 40 bisections on the
   original linear longitude/latitude source segment. Deduplicate the same
   source vertex; retain distinct crossings even if they coincide spatially.
   Numerical overlap/touch tolerance is 1e-8 km and source-index deduplication
   tolerance 1e-9. A normal overlap or multiple/absent crossings is unresolved.
   Long source segments are not silently removed: any candidate on one rejects
   the result. Missing vertices have no invented connecting segment.
5. Require the provider left edge on the negative side and right edge on the
   positive side of the reconstructed downstream normal. Do not reverse labels
   or directions to obtain a result. Require both edge distances <=200 km from
   the gate; this is a declared local search guard, not a measured boundary.
6. Measure the WGS84 distance between the two intersections. Retain tangent
   endpoints, direction, original edge indices/fractions, signed offsets,
   intersection positions, crossing counts and numerical normal residuals.
   Residuals must be <=0.001 m. Report six-decimal-km numerical readbacks;
   display about 10 km precision. Numerical residual is not physical accuracy.
7. Retain every date/depth/gate/window attempt, including all rejection reasons.
   Stable IDs use source edition/date/level/gate/tangent half-window/operator
   version, never a row ordinal. Keep old latitude spans as comparisons without
   inheriting their success/failure mask or modifying their values.

## Ranges and interpretation

For each level/gate/window retain annual and calendar-month sample counts,
min/median/max. Never pool levels, sections or windows. Compare the three
tangent scales only where all resolve on the same date/depth/gate. Their
envelope is method sensitivity, not an uncertainty interval. No interpolation
between missing dates and no annual climatology from this single model year.

Source boundary selection uses a 30% axis-speed criterion with a farthest-ocean
fallback when the search fails. That flag is absent in the coordinates. Source
smoothing and censoring remain relevant. Retain unknown fallback occurrence,
threshold attainment and physical uncertainty as null. Flag widths over the
source's nominal 140 km transect length without clipping them; the flag cannot
determine whether fallback occurred. No whole-current width, annual physical
range, length rank, footprint or physical state passage is admitted.

## Delivery and checks

Produce a pinned scientific report, all attempts, monthly/annual summaries and
a standalone figure showing model-normal spans, coverage and the comparison
with latitude spans. Geometry tests must include oblique axes, independent
boundary sampling, missing breaks, repeated crossings, overlaps, reversed
side labels, long segments, endpoint-limited tangents and source identity.
Rebuild the entire report from original bytes. Native/WASM query and atlas
integration is subsequent required work and must not be claimed before tested.

Implementation clarification: the initial-azimuth and nominal-subdivision
wording was made explicit during code review after the first exploratory
extraction. Neither calculation nor acceptance thresholds were changed. A
retained first-pass comparison checks that all span values/statuses survive.
