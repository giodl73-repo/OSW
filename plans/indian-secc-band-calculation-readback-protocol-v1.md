# Indian SECC band calculations: distance readback v1

Declared2026-10-21 after inspecting failed Linux scientific reconstruction
run39715841797 at4709940 and before revising the report. The original source
cube, historical section report and their producer bytes remain immutable.

The new band producer called the existing WGS84 meridional section operator.
Windows/Linux geodesic results differ by at most3.410605131648481e-13km in
reported spans in this run. Comparing these raw derived floats to historical
stored values incorrectly changed eleven comparisons into supposed domain
differences. Neither topology nor source boundaries changed in those cases.

For newly computed `span_km` and `grid_bracket_span_km` values, retain six
decimal kilometres, normalizing rounded negative zero to0.0. Apply this only
to new section-operator returns and their summary/compact copies. Do not round
original vectors, coordinates, interpolation fractions, native brackets or
any historically stored numbers. Do not modify the shared section operator,
the global readback rules, the historical report or any previous producer.

Separate the comparisons:

1. `boundary_coordinates_and_status_exact` compares boundary coordinates,
   edge statuses, section status and the threshold fraction exactly. It does
   not compare a distance evaluated in different runtime environments.
2. `span_readback_matches` compares the retained historical distance at the
   same six-decimal-kilometre readback to the new readback, preserving nulls.
   The original historical distance remains stored at its original precision.
3. `comparison_kind` identifies unchanged boundaries or a domain-support
   difference, independently of numerical distance readback. Monthly recovered
   counts require an old missing northern crossing and a new resolved northern
   crossing; a numeric discrepancy cannot create a recovered boundary.

Use schema `osw.indian-secc-positive-band-connectivity.v2` to expose the
corrected semantics. Replace the misleading exact-comparison/count names;
retain all72 historical cases and every band/node/edge. Expected actual source
result:63 unchanged boundary/status cases, nine northern domain extensions,
with all nine original southern boundaries unchanged. This expectation must
be independently tested, not used to force matching values.

The rounding is numerical readback only. It is not physical uncertainty,
source resolution, a confidence interval, a changed width definition or new
current admission. Synthetic tests must distinguish sub-readback numerical
drift from an actual changed boundary/status or a genuine changed distance.
Rebuild and inspect the final report, source index, bundle and actual WASM UI;
require a fresh Linux reconstruction before claiming cross-platform repair.
