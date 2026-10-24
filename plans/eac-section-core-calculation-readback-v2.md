# EAC section-core calculation readback v2

This replaces v1 for newly generated reports. The published v1 file and
commit3701397 remain unchanged. Only the final interpolation-fraction
precision changes; this revision does not change the measurement operator.

This convention specifies final JSON precision for derived fields in
`osw.eac-section-core-spans.v1`, without claiming measurement accuracy,
resolution, confidence or a new physical width. All peak selection, threshold
decisions, interpolation and summaries use full precision before serialization.

| Derived output | Decimal places |
|---|---:|
| Geometry cumulative distance; resolved edge distance and distance brackets, metres | 3 |
| Geometry bearings; peak-source component bearing, degrees | 6 |
| Section-normal velocity and projected supplied-component magnitudes, m/s | 8 |
| Scenario peak component, derived central normal/tangent component and threshold, m/s | 8 |
| Edge component brackets, m/s | 8 |
| Edge interpolation fraction | 7 |
| Tangent/normal indicator | 8 |
| Section span and sampling-support separation interval, kilometres | 6 |
| Conditional minimum/median/maximum in overall and month summaries, kilometres | 6 |

Use Python `round` only on these final fields and normalize selected derived
zeros to positive zero. Keep `geometry`, `project`, `edge`, `measure` and
`summarize` at full precision. Do not recalculate peaks, statuses, boundaries
or spans from serialized geometry, velocity or fractions. All status strings,
indices, masks, source dates, counts, experimental fractions and integer
display spans remain exact.

Original source coordinates, depths, UCUR/VCUR, supplied uncertainty and
source-profile JSON/NPZ bytes remain exact. In particular, original peak
UCUR/VCUR are never rounded. Projected supplied magnitudes are derived
sensitivity allowances, not newly estimated confidence intervals. Calendar
distributions read serialized spans and retain their own0.001km quantile
convention; audit any resulting values or extrema membership.

## Reason for revision

Linux run39557216015/job119079679024 at3701397 reproduced seventeen reports
exactly and found one remaining EAC numeric difference: profile3021, the
minus-supplied-magnitudes40% case's offshore interpolation fraction. v1
serialized it as0.24547311 on Windows and0.24547310 on Linux, across a rounding
boundary. Every other field, including all calculated edge distances and
spans, matched exactly. The fraction is an interpolation coordinate, not a
physical uncertainty or a new observation.

The maximum rounding displacement at seven fractional decimal places is
less than0.0002m at this section's maximum adjacent source spacing, below the half-millimetre edge
readback. The fraction is serialized only after the full-precision distance
and span have already been calculated. This changes no physical result or
admission decision. Verify that independent reconstruction is byte-exact;
retain strict comparisons without tolerances or copied calculated values.
