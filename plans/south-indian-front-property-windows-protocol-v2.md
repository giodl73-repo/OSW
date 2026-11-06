# South Indian monthly property-window assessment, v2

Declare this operator before calculating its results. The existing source values
have already been acquired, plotted and inspected; this is an exploratory
assessment, not a blinded test or reproduction of Sparrow et al.'s climatology.
Keep all earlier sources, protocols, diagnostics and views unchanged.

## Inputs and criteria

Use the retained 2013 HYCOM monthly products at 15 m, 100 m and 200 m on all
326 native latitudes and all three meridians around 80 E, for all twelve months.
Use the already independently reproduced daily-before-monthly conditional
potential-temperature report. Pin the complete upstream dependency graph and
the original source products in a separate preflight before this calculation.
Do not substitute raw in-situ temperature or Absolute Salinity for the quantities
in the historical criteria.

Sparrow et al. (1996), Table 1, motivates four **native-node property masks**:

1. At 100 m, potential temperature in the inclusive interval 10–12 C.
2. At 100 m, Practical Salinity in the inclusive interval 34.6–35.0.
3. The intersection of masks 1 and 2 on the same eligible native node.
4. At 200 m, potential temperature in the inclusive interval 12–16 C.

The first three relate to the published STF property description; the last
relates to the ARF description. They are not identified fronts. The input
potential temperature still assumes ITS-90 and approximate depth-derived
pressure; the source does not independently verify that temperature scale or
its equivalence to historical measurements. No SAF criterion is applied:
these depths cannot resolve the descent of a vertical salinity minimum.

Evaluate monthly means, not daily membership. A mask says nothing about the
fraction of individual days satisfying the criterion. Retain the original
ceil(80% of calendar days) eligibility. Missing/ineligible values produce null,
not false, and split runs. Infinite or malformed values are errors. Do not add
numerical tolerances, margins, smoothing, interpolation or chosen latitude
search boxes after seeing the results.

## Native support and flow comparisons

Retain every contiguous true run, including isolated nodes and runs touching a
domain boundary. Record the complete mask, all member indices, first/last native
latitudes and both adjacent-node states. These describe discrete sampling
support, not interpolated property crossings, physical boundaries or a width.
Do not compute a run's span and label it a current width.

At 15 m, retain every positive eastward-velocity local maximum using the frozen
v2 plateau/censored-flank operator. Do not choose the strongest peak, discard
secondary peaks or select a preferred property run. Compare every peak with
every property run; preserve zero matches, multiple matches and all failures.
Closed native supports overlap when their latitude intervals overlap. Otherwise
report their WGS84 meridional separation using the existing Decimal70 operator.
The distance is a separation between sampling supports, never a current width.

Prove identical temporal support before making each cross-depth comparison:
the two frozen source selections must have identical ordered daily time indices
for every month, and every compared peak/run node must have common-valid counts
equal to the full available daily count. Equal but incomplete counts do not
prove the same days were sampled. Preserve noncomparable pairs with null
distance and an explicit reason; do not silently reduce the cohort.

## Interpretation, presentation and verification

Produce all 36 month/meridian cases, four masks per case, all runs, all surface
peaks and all pairwise relations. Overlap or zero separation is not named-front
or South Indian Current identification, a confidence score or evidence that
the strongest eastward feature is distinct from the ACC. No current width,
axis, length, annual envelope, seasonal climatology, geographic footprint,
state intersection or ranked measurement is admitted.

Provide an interactive section comparison with direct case links, keyboard and
phone controls, equivalent tables and full lossless query access. Clearly label
sampling supports and the conditional temperature reference. Show absent and
multiple runs rather than forcing a continuous front through the year.

Test inclusive bounds, separate/joint criteria, missingness, isolated and
boundary-censored runs, plateau maxima, all-pairs retention and incomplete-day
comparison refusal. Require exact complete report replay on Windows and Linux;
never round or weaken the byte gate. Preserve all earlier scientific reports,
source custody, physical measurements and default validation gates. Continue
the same branch and draft PR83.


## Explicit generator correction

Version1's first actual report omitted the first three criterion groups because
case construction appended only after its criterion loop. The source audit
retains its exact result hash,36-case omission and unchanged frozen method.
No v1 result was integrated or admitted. V2 changes the case-construction path,
not the property criteria, source values, arithmetic or physical interpretation.
A directly tested evaluate_windows function must return the exact four groups
for every case. Validate all36 actual cases and all four IDs before publication.
V1 is not rewritten and no failed output is silently replaced. V2 remains
exploratory on already observed data; publish its declaration before calculation.
