# West Greenland upper-slope core: prospective method decisions

**Draft, not an execution freeze.** No original width is calculated by this
document. The successful sample-support case remains immutable. Actual source
arrays stay in the saved cloud artifact. This draft identifies the choices and
checks needed to turn that support into defensible regional measurements.

## Target and evidence

Target a regional upper-slope velocity core associated with the West Greenland
Current. Do not combine it with the coastal current or deep boundary current.
Do not call the array's full occupied span a current width. A future half-maximum
core diagnostic would be a new OSW metric, not a published whole-current width.

The processing review at
`research/west-greenland-pacini-2020-processing-visual-review-v1.json` confirms
the source flow reference as **318.1° true** by visual inspection. Adoption as
a fixed reference for this deployment must be explicit. A projected transverse
section span would retain that name; it would not become a measured local
axis-normal width merely through a coordinate rotation.

## Decisions to fix before computation

1. **Identity and peak selection.** Review the paper's actual upper-slope core
   discussion/section figures before naming eligible core moorings. A coastal
   or offshore secondary maximum must not be substituted to force a width.
   Preserve missing, merged and ambiguous-core outcomes.
2. **Physical layer.** Assess a candidate 50–100 m layer from supplied ADCP
   time-varying depths, with no surface/vertical extrapolation. This is an OSW
   candidate, not a source-prescribed layer. Require observed bracketing of
   both layer boundaries and a declared maximum vertical gap. Negative depths
   and nominal bin labels cannot supply the missing layer. Pressure is not
   silently converted to depth, and deep nominal point meters are not mixed
   into a surface-layer series.
3. **Time normalization.** Preserve decoded original times and any alignment
   offsets. Fix an hourly alignment tolerance before examining width results;
   reject duplicates or off-grid rows rather than merging them silently. The
   existing audit's microsecond month assignments remain unchanged. Explain
   how a later alignment treats calendar boundaries.
4. **Processing.** Confirm deposited velocity direction and processing metadata.
   If choosing a 36-hour filter, specify filter order, cutoff convention,
   sampling interval, segment length, edge trimming and missing-value rules.
   Label it filtered velocity, not a reproduced harmonic-detided source field.
   Never filter across missing segments or extrapolate a blown-down layer.
5. **Monthly support.** Require synchronized eligible observations, explicit
   timestamp/day/month denominators and predeclared coverage thresholds.
   Report losses caused by moving depth, masking and filter edges separately.
   Strong-flow blowdown can make missingness informative; a monthly conditional
   mean must not be described as an unbiased seasonal climatology.
6. **Metric and censoring.** A prospective relative half-maximum core span needs
   two observed threshold brackets around the selected peak, a declared
   interpolation method, physical section coordinates and an orientation label.
   Missing brackets produce a censored result. Do not double a one-sided span,
   use the coast as a fabricated edge, or interpolate through missing stations.
7. **Sensitivity and uncertainty.** Predeclare alternative relative thresholds
   and processing choices. Keep their spread separate from sampling variation,
   measurement accuracy and confidence intervals. Preserve every failed or
   censored alternative alongside successful values.
8. **Seasonal reporting.** Retain individual calendar months and year-specific
   support. Partial boundary months and missing months stay explicit. A range
   of supported monthly mean core spans is not an annual range of instantaneous
   physical current width. No seasonal geometry animation follows from these
   scalar diagnostics alone.

## Required synthetic cases and delivery

Before a committed freeze, test changing-depth bracketing, masked components,
calendar-boundary normalization, irregular/duplicate time, filter segment
boundaries, two/one/no threshold brackets, multiple cores and missing stations.
Verify rotation signs and section-distance units independently.

Execute only after the viewer queue clears, in one bounded cloud stage reusing
the exact source artifact and first custody. Review the actual outputs and
source/diagnostic figures before admission. Later query records must retain
current identity, layer, month, metric, support, edge brackets, censoring,
sensitivity and provenance. Full-current ranks and occupied geometry remain
outside this regional diagnostic's scope.
