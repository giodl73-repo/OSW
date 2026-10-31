# ASCA100m dated component-span protocol v1

Declared2026-10-18 before computing the following spans. Existing source fields,
missing-value totals, monthly profiles and source-method/correction limitations
have already been inspected. This is exploratory analysis, not a blinded test.

## Frozen inputs and question

Use all931retained profiles, all601array-distance cells at source100m depth
from `research/agulhas-asca-100m-observed-profiles.json`, verified against the
existing query contract and original HTTP-range reconstruction. Product2.0,
DOI10.5281/zenodo.20515068, supplies corrected, processed observational fields.
The original file's complete checksum remains unverified. No independent repair
of ADCP rotation is made. Full2022corrigenda remain unreviewed; original published
transport values and old boundaries cannot validate these new diagnostics.

Question: how often is a paired, peak-connected southwestward **v-component
section span** resolved at100m on this fixed array? This is not total-speed,
flow-normal, transport or whole-current width. Geographic current edges,
annual extrema, current identity away from the line and state intersections
remain unestablished.

## Operator

1. Preserve supplied timestamps, source indices, distance order and nulls.
   Distance is the source array coordinate in metres, not longitude/latitude.
2. Set q=-v for southwestward flow. Select its global finite maximum across
   the entire source section; ties use the smallest original cell index. Do
   not select a more convenient peak after a failed crossing. No finite values,
   or a peak below0.3m/s, leave all cases unresolved with an explicit reason.
3. For each fraction0.4,0.5(primary),0.6of that same peak, walk independently
   towards smaller and larger array distances. The first finite q<=threshold
   and its adjacent interior q>threshold bracket the crossing. An exact
   threshold at the first outside cell gives that cell's coordinate. Do not
   smooth, fill a null, jump to another lobe, extrapolate to coast/domain,
   merge peaks or subtract a background.
4. A null encountered before a boundary blocks that side. A domain endpoint
   above threshold is unresolved. Keep a resolved single side as a one-sided
   result; never double it. Both sides are required for a span.
5. Within an intact adjacent pair, interpolate q linearly in source distance.
   Retain both original indices, distances, velocities and interpolation weight.
   Report raw numerical span in kilometres and a whole-kilometre display value
   rounded half upward. This rounding does not establish kilometre resolution.
6. Keep each boundary's full500m grid bracket and the corresponding minimum/
   maximum separation of those brackets as an interpolation-support interval.
   It is not a measurement error, confidence interval or physical width range.
   The500m grid is interpolated and not independent instrument resolution.
7. Retain source U and v at the selected peak. If both are finite, report
   atan2(abs(U),q) in degrees as a local alignment indicator. It is not a
   section-wide axis, edge rotation or permission for a geometric correction.
   Missing U stays null and does not block a v-only component diagnostic.
8. Retain every profile and all three threshold outcomes, including failures.
   Fractions are sensitivity assumptions, not error bars or three observations.

## Time summaries and visualization

Group by original UTC year/month, keeping all27bins and the existing monthly
calendar-completeness flags. For each fraction report attempted/resolved counts,
failure reasons and min/median/max of resolved numerical spans only. Mark
conditional-on-resolved summaries; missing cases are not zero. Do not interpolate
through missing dates, annual-wrap playback or call these a climatology.
Twenty-hour subsampling of40-hour-filtered fields is temporally dependent.

The standalone figure shows all931primary outcomes chronologically, all27monthly
resolved-count summaries, and original v sections at fixed indices0,465,930
with the same peak/crossings and visible null gaps. Report and figure put source
processing, metric, bracket meaning and incomplete scientific admission beside
the values. No physical map polygon or geographic seasonal animation is added.

## Verification and stopping rule

Pin protocol, source packets, contract and operator. Test independently known
crossings, equality, ties, disjoint lobes, weak/absent flow, missing barriers,
one-sided/domain truncation, nonmonotone coordinates, rounding and monthly
failure accounting. Reconstruct actual source results offline. Preserve existing
width inventory, route/length records, source timestamps and velocity values.
If no cases resolve, publish that result without tuning thresholds or barriers.
Physical-width admission requires source correction review, paired geographic
geometry, flow-normal validity and suitable instrument/mapping uncertainty.
