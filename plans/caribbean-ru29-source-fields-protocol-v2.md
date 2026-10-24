# Caribbean RU29 source fields: prospective protocol v2

All physical interpretation limits, custody, raw-value retention, masks,
source discrepancies, figure method and resource rules in frozen protocol v1
remain applicable. V2 imports the unchanged v1 attribute encoder, scalar
encoder, raw summary and current visualization functions.

## Retained v1 failure and correction

Frozen v1 commit 7a867da began source array readback, then rejected nested
groups in the first correspondence file, before any public mirror, report
or figure was emitted. Do not edit that producer, tests, protocol or preflight.
The failure is retained in `caribbean-ru29-v1-nested-group-diagnostic.json`.

A subsequent complete recursive **metadata-only** inspection found two
groups in each correspondence file: LastVirtualObs and LastPreviousVirtualObs.
These contain terminal tracking state with additional original fields; they
are required parts of the selected member inventory. Source metadata review
must include group structure in future NetCDF feasibility checks.

V2 recursively retains all groups, their exact paths, local dimensions,
attributes, variables, original dimension references, raw values and decoded
masks. Parent dimension references remain resolvable through the group tree.
Both root and child variables follow identical packing/retention rules.
Raw/mask shape disagreement fails. Summaries recursively cover every group.
The four current panels use the same untouched v1 display operator.
Terminal virtual state is not a new observation or current-width measurement.

Freeze v2, its tests, this protocol, the recursive schema, diagnostic and
preflight before running actual complete recursive readback. The preflight
does not claim that v1 never accessed actual arrays; only v2 has not run yet.
No transport, physical contour reconstruction or seasonal inference is added.
