# EAC section-core calculation readback v1

This convention specifies final JSON precision for the derived fields in
`osw.eac-section-core-spans.v1`. It does not specify measurement accuracy,
instrument resolution, confidence, a new physical width or a correction to
the source. Keep all peak selection, threshold decisions, interpolation and
summaries at full precision before applying this final serialization step.

| Derived output | Decimal places |
|---|---:|
| Geometry cumulative distance; resolved edge distance and distance brackets, metres | 3 |
| Geometry bearings; peak-source component bearing, degrees | 6 |
| Section-normal velocity and projected supplied-component magnitudes, m/s | 8 |
| Scenario peak component, derived central normal/tangent component and threshold, m/s | 8 |
| Edge component brackets, m/s | 8 |
| Edge interpolation fraction; tangent/normal indicator | 8 |
| Section span and sampling-support separation interval, kilometres | 6 |
| Conditional minimum/median/maximum in overall and month summaries, kilometres | 6 |

Use Python `round` on only these final fields; normalize selected derived
zero values to positive zero. The operator's `geometry`, `project`, `edge`,
`measure` and `summarize` functions remain full precision. Never feed rounded
geometry or components back into boundary or peak decisions. Preserve all
status strings, peak/edge/bracket indices, masks, source dates, counts,
fractions defining the experiment and integer display spans exactly.

Original source longitude, latitude, depth, UCUR, VCUR and supplied uncertainty
arrays remain bit-exact in the source subset and source-profile JSON. In
particular, `peak_source_components.UCUR` and `.VCUR` are original source
values and are not rounded. The projected supplied magnitudes are derived
sensitivity allowances, not newly estimated confidence intervals.

The standalone calendar-distribution report reads the serialized section
spans and retains its own declared 0.001 km decimal quantile convention.
Audit any resulting quantile or extrema-membership changes rather than
asserting they cannot occur. The stored section report's summaries are
computed from full-precision spans before their own final readback.

Independent Linux reconstruction at fba615a found 609,263 changed numeric
leaves and zero changed other leaves. The largest distance difference was
4.831235855817795e-8 m; the largest span difference was
5.0881965307780774e-11 km. The helper enumerates supported fields explicitly;
all other fields retain their values. Require exact regenerated object and
encoded-byte equality after readback. Do not add comparison tolerances or
copy retained calculated values into a rebuild.
