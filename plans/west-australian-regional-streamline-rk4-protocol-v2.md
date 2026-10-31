# Offshore regional streamlines: numerical refinement v2

20 October 2026. Declared after the complete117-case Euler v1 baseline was
computed and inspected, before the refined solver is run. V1 found43matching
pairs and four primary monthly matches, but smaller steps changed some
connections and lengths substantially. Preserve that full baseline; its
primary values are provisional numerical results, not dependable measurements.

## Unchanged source and experiment

Keep exactly the13mean fields, original paired-support rules,32S peak search,
0.02m/s seed condition, native neighbour offsets,5/10/20km nominal maximum
steps,28/36S gates, mask rectangle rule,0.005m/s speed guards,300km seed-return
delay/radius convention and10,000km computational leg limit from v1. Retain
all117refined outcomes alongside the117baseline outcomes. No alternate seeds,
new months, changed gates, selected successful branches or source corrections.

## Refined integration

Use classical fourth-order Runge–Kutta in the same WGS84 geographic-coordinate
direction field. Compare one full step with two half steps; estimate the local
error of the two-half-step result by their endpoint WGS84 separation divided
by15. Accept the two half-step states only when that estimate is<=0.01km.
Halve a rejected trial, with0.1km minimum; double a successful step only when
the estimate is<0.01/32km, up to the declared nominal maximum. This is local
numerical error control, not source uncertainty, a global error guarantee,
continuous-flow certification or added observational resolution.

Every Runge–Kutta stage and proposed endpoint must have finite eligible paired
corners and pass the same minimum speed guard. Require the bounding rectangle
of all stage/endpoint coordinates to have finite paired corners. A failure
can reduce the step, never bridge a masked area or change the field/seed.
If an error/support guard persists at the minimum step, retain a failed leg.

Near a source-domain boundary, stage queries cannot extrapolate. If outside-
domain queries persist at0.1km, bisect the trial length (up to40iterations)
to find the longest fully supported, error-controlled two-half-step proposal.
Only if that accepted endpoint is within0.001km of a viewport side may a final
linear geographic-coordinate segment snap to that side. Check its full source
rectangle, endpoint speed and gate direction too. Otherwise retain a boundary
guard failure. Record the snap distance and all rejected-trial counts; the
one-metre closure is a separate numerical convention, not a physical margin.

Distances still sum WGS84 separations of accepted polygonal states. Count the
seed once. A matching pair is a conditional regional candidate only; all
unresolved partial paths, source-period mean failures and guard reasons remain.

## Numerical comparison and admission

For each field/seed, publish all three nominal-maximum-step outcomes. Describe
their relative length spread only when all three reach both matching gates.
Do not choose a pass threshold after looking at refined outcomes or call this
spread a physical uncertainty interval. Keep Euler/refined comparisons,
including cases that lose a previously reported numerical connection.

Use v1's derived readback precision, preserving original source values and
making every decision before quantization. Report current association,
whole-current length/width, annual physical ranges, eddy identities and OSW
physical joins as unresolved. A refined regional connection does not prove
that the selected source-field branch is the named West Australian Current.
