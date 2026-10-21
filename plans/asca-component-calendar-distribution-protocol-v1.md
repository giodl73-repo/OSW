# ASCA source-sample calendar distributions v1

Declare before calculating the distributions. Source:
`research/agulhas-asca-100m-dated-component-spans.json`, SHA256
`59c839aa4ed6363ddfa75af01a2932d73763424c19cb04cd075ee1a9b2ea3e3a`.
Preserve all931 profiles and2,793 threshold attempts, their original timestamps,
statuses and source values. Do not recalculate boundaries, fill failures,
change the peak rule, rotate the velocity or select a better-resolving threshold.
Primary fraction remains the source-declared50%;40/50/60% remain separate.

## Cohorts and statistic

Retain the entire source period, each UTC calendar year touched by it, and
twelve pooled calendar months. Every timestamp belongs once to each applicable
cohort; thresholds are never pooled. Each mapped timestamp has one vote, not
each year or each month. The40hour low-pass product sampled nominally every
20hours does not provide independent observations or a climatology.

For each cohort/threshold, retain attempted, resolved and unresolved counts,
every outcome status count and source-index membership. Use only finite,
resolved **unrounded** `span_km` values for minimum,25th percentile, median,
75th percentile and maximum. No resolved values means all statistics are null.
Use type7 quantiles: h=(n-1)p, linear interpolation between adjacent order
statistics, with p=0.25/0.5/0.75. Calculate with Decimal from the stored JSON
numbers; read back final kilometre statistics to6decimal places, half up.
Percentiles and min/max are conditional source-sample summaries, not confidence
intervals, measurement uncertainty or annual physical extrema.

## Coverage and source clock

Source timestamps alternate20hours plus/minus64seconds in the retained report.
Preserve them exactly. Do not snap them onto a reconstructed20hour clock or
invent absent timestamps. Carry the original monthly completeness flags.
Call a calendar year complete in nominal calendar support only when all12
source month bins exist and all12 retain their completeness flag. This does
not mean all width attempts resolve, nor that physical extrema were observed.
Show partial endpoint years explicitly. Pooled month summaries retain their
contributing year/month bins and partial-support counts.

## Interpretation and presentation

This remains a fixed-array100m **−v component-span** diagnostic. It supplies no
flow-normal whole-current width, geographic edge coordinates, annual physical
range or seasonal map playback. No observation date, source mask, uncertainty
array, current identity, width-inventory row or existing series changes.

Plot the predeclared primary50% convention, with min/max, interquartile span
and median distinguished and finite/attempted counts beside every group. Label
partial years and pooled months. Retain all thresholds in queryable records,
with an equivalent text/table view and links to original cases. Never hide
failed dates to suggest complete annual measurement support.

Verification must account for every case in all three cohort partitions,
preserve all failures and timestamps, distinguish calendar support from resolved
measurement support, reject altered membership/quantiles/eligibility and
reproduce the derived JSON byte-exactly on an independent platform.
