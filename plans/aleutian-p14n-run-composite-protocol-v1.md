# P14N conditional underway-run composite v1.0

Declared 2026-10-18 after inspection of the native and hourly vectors,
the earlier 126 unresolved averaging scenarios, run durations/positions and
their intervening time gaps. This is exploratory, not a blinded test.
Whole-run means and the following composite crossings have not been computed
at declaration. Preserve all earlier operators and results unchanged.

## Object and assumption

Estimate an **eastward-component span of a conditional run composite**,
using the same native July1993 P14N 100–300m supported layer means. This is
not an instantaneous transect or independently identified physical current
width. Combining separated underway runs assumes their flow is sufficiently
comparable in time. A permitted inter-run gap does not verify that assumption
or bound temporal variability during the whole crossing.

Keep every original 1/2/3m/s speed-cutoff run and source acquisition order.
Never sort latitude, merge runs, add excluded low-speed profiles as velocity
samples, alter source flags, fill missing source values or substitute hourly
archive spans. Preserve each scenario's original eligibility: a source CTD
event overlap is context, not a new occupation classifier or quality flag.

## Whole-run summaries

For each complete original run, compute union-time-weighted u/v and
ensemble-end positions over its first nominal start through last nominal end.
Reuse the retained overlap integrator: overlapping source intervals contribute
their mean once. Preserve contributor indices, coverage, overlap, time extent,
latitude/longitude footprints and endpoint distance.

A run can support boundaries only with at least one hour of covered time,
at least80% coverage of its full interval, no northward contributor steps and
every contributor latitude inside the unchanged northern44–46N or southern
41–43N window. The one-hour floor is an editorial representation rule, not a
calibrated velocity-error claim. Short or unsupported runs remain explicit
barriers; never jump over them to reach another summary.

## Conditional links

Evaluate **3,6,12hour** maximum unobserved-time gaps separately. The primary
reported assumption is6hours with2m/s eligibility. These caps are editorial
assumption tests selected after the source timing was known, not physical
decorrelation times or evidence that each run samples a steady current.

Two consecutive run summaries may be linked only if both are eligible in
the same branch, their complete latitude footprints remain southward and
nonoverlapping, the unobserved gap does not exceed the scenario cap, and the
WGS84 distance from the first run's final ensemble-end position to the next
run's first position does not exceed25km. In addition, every intervening
source index must exist with supported joint layer means and increasing
timestamps no more than450seconds apart. Missing/unsupported source profiles
are hard barriers. Retain counts and CTD-event overlap as context; a low-speed
gap is not automatically identified as a CTD occupation.

These links explicitly relax the earlier no-cross-run-interpolation rule.
They interpolate between *summary positions* under a declared assumption;
they do not add measured velocities or physical observations within the gap.

## Boundaries and sensitivity

For every speed/cap/branch, select the largest eligible eastward run mean;
ties use earliest original run. Require at least0.02m/s. Walk consecutive
eligible, conditionally linked summaries on each side until the first value
at or below40/50/60% of the selected mean. Also retain50% thresholds displaced
by−0.06/−0.02/+0.02/+0.06m/s. Thresholds outside(0,peak) are ineligible.
Never change the selected peak to obtain complete boundaries.

Interpolate latitude/longitude linearly inside the first bracketing summary
pair. Preserve both summary references, the interpolation fraction, source
footprints, mean-position separation, inter-run time/distance gap and full
observation time span. Only two resolved sides yield WGS84 endpoint
separation. Missing sides remain null with stopping reasons. Retain all
54 relative-threshold and72 velocity-displacement scenarios, including
unresolved outcomes. Round displayed separations to10km; raw precision is
calculation precision. No sensitivity range is a confidence interval.

## Limits and display

The result remains an unrotated eastward component. Source GPS-averaging
estimates do not calibrate its total errors. Mean locations summarize moving
footprints. An inter-run cap does not make the complete multi-hour crossing
synoptic, resolve eddy/branch identity, or establish flow-normal boundaries.

The figure must distinguish observed run summaries, their spatial footprints,
short/ineligible summaries and dashed conditional links. Show missing sides
and stopping reasons. Supply the full numeric cases, text and source links.
Never present assumed links as a continuous observed velocity section.

No inventory width, whole-current dimension, annual extrema, seasonal
playback, physical edge geometry, state intersection or ranking is admitted.
This operator does not replace the earlier negative averaging result.
