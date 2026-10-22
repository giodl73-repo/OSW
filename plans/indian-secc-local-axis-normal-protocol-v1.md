# Indian SECC investigation: local candidate axis and normal spans v1

Declared2026-10-21 before this calculation. The2013 source fields, historical
meridians and positive-band topology are known. This is exploratory. Native
positive-u connectivity is not used as the named-current outline or axis.

Use unchanged monthly paired OSCAR2017.0 vectors, nominal15m mapped upper-ocean
support. At80⅓/80⅔E use each month's previously selected strongest eastward
native cell in2.5–6S. Retain both original anchors, including weak or ambiguous
cases. Add native latitude offsets−1/0/+1 as seed-choice scenarios, not new
independent observations. Require finite paired bilinear support, eastward
velocity and speed at least0.02m/s at a seed. No source smoothing, missing fill
or extrapolation; all four corners must be finite even at zero weights.

At a point use its local east/north velocity bearing. Construct a WGS84 geodesic
normal with increasing signed distance at bearing+90 degrees. At each normal
sample parallel-transport the tangent perpendicular to the local geodesic
normal; project the interpolated vector onto it. Do not use scalar speed as
the signed component or hold geographic bearing fixed along a curved geodesic.
Use profiles at5km and10km spacing, at most600km on either side. Stop each
side at its first unsupported sample/rectangle or viewport exit; retain that
failed sample. Do not bridge missing cells or close edges at the profile limit.

Refine the initial seed once to the strongest projected-velocity sample within
±40km. Keep equal maxima; do not choose a tied peak. Require the peak to be
interior and at least1% stronger than both search endpoints; otherwise retain
flat/ambiguous/search-edge status. Recompute local velocity orientation at the
refined point. Refinement is not an independently diagnosed physical axis.

For the central native seed, trace the monthly static vector field both ways
to arc-parameter stations−100,−50,0,+50,+100km. Reuse the existing adaptive RK4
stage/trial operator with maximum10km step, minimum0.1km, local step-doubling
tolerance0.01km and stage speed guard0.005m/s. Retain actual geodesic chord sums,
partial paths, stage errors and every failure; this is a short mean-field
streamline, not a particle trajectory, named-current length or global error
bound. Offset seeds receive only the central section as seed sensitivity.

At each station independently recompute the local normal profile. A local
candidate axis check requires a unique interior peak within40km,1% endpoint
contrast, peak displacement at most10km from the streamline, and local vector
direction within15 degrees of the transported tangent at the peak. The200km
candidate segment passes only if all five stations pass. Offset cases cannot
pass this five-station test. Record all intermediate margins and failure codes.
These chosen tolerances are method gates, not source uncertainty or proof of
named-current identity; distinguish candidate axes from admitted physical axes.

For every supported peak, find the first sampled crossing on both sides of0.4/0.5/0.6
of its positive projected component. Interpolate within the retained adjacent
sample bracket; never jump over a missing sample. Record edge positions,
distance parameters, geodesic separation, crossing interpolation residual,
inner/outer bracket separation and
whether the edges reach equator/north. A peak or one edge alone gives null
paired span. Do not require the local axis gate to pass to retain a diagnostic
span, but label its axis support and failed gates explicitly. Resolution is
judged against actual native source-cell support, not the5/10km display steps.

Keep5/10km differences separate from seed-choice and0.4/0.6 threshold changes.
None is a confidence interval, independent repeat, physical seasonal range or
whole-current representative width. Original source numbers stay exact;
derived positions use8 decimal degrees, velocities8 decimal m/s, distances6
decimal km, bearings6 decimal degrees. Decision arithmetic precedes readback
rounding. Reader-facing approximate spans round to10km; this is numerical
readback and display precision, not a physical error bound.

Required outputs: all cases including failed seeds/stations/edges, labelled
monthly summaries, step/seed comparisons, normal-profile sample columns and
source-cell indices, twelve geographic maps plus a semantic data alternative,
exact native/WASM queries and current-card navigation. Verify analytical and
synthetic orientation/peak/missing/boundary cases, source reconstruction,
preservation of all25 prior reports/producers and typed scientific rows, source
pins, keyboard/mobile use, and staged dependency hashes. Complete-suite status
is separate. No canonical length/width, physical annual range, state join or
NASA identification is admitted solely by these diagnostics.
