# Pacific NEC nominal-width cloud verification harness

Status: prepared source; matching native/WASM execution and browser review pending.
This does not admit or install a new measurement.

The scientific candidate remains the reviewed nominal 8–17°N regional surface
band, converted on WGS84 and displayed as about 1,000 km. The related JPO
7–17°N description remains separate. Neither description supplies an annual
range, numerical uncertainty, full-current axis, or flow-normal paired edges.

## Complete query and source comparisons

`analysis/check_pacific_nec_nominal_width_parity_v1.mjs` retains the prior
complete-response and initialization-metadata comparisons, source-catalog
mismatch refusal, response budgets, and memory ceiling. Its fixed inventories
are two installed-parent speed captures, 215 main queries (195 historical plus
20 nominal-width cases), and 79 source queries (73 historical plus six new
document/pointer queries). No historical case is removed.

`analysis/pacific_nec_nominal_width_source_cases_v1.py` supplies the six new
source queries: complete roots of the three appended JSON documents, the
original nominal-surface-width facts, the exact admitted width record, and the
two publication identities. Each response must preserve document hash, request
identity, row pointers, total, and original content. Unknown ranges remain null.
The prepared-candidate document's historical pending-audit status is preserved
as provenance; the later duplicate audit and query contract determine admission.

## Complete current and family card comparisons

`analysis/check_pacific_nec_nominal_width_snapshots_v1.mjs` retains complete
atlas, seasons, and dashboard capture/parity. It additionally captures complete
installed object responses for all five basin-qualified equatorial currents and
the North/South Equatorial families, with a per-response hash and bundle hash.
The candidate phase compares the same exact seven IDs with complete native
responses. Files are created exclusively, so prior evidence cannot be overwritten.

The controller must run `pacific_nec_nominal_width_runtime_v1.verify_object`
on each actual parent/candidate pair before native/WASM parity. Native/WASM
agreement alone does not prove historical preservation. Likewise it must apply
`verify_snapshot` to all three parent/candidate global pairs and retain every
prior scientific semantic check alongside the new width/source cases.

## Remaining execution work

Assemble a versioned controller and disabled request/preflight/workflow using
the frozen runtime scope v2, installed parent, and exact inventories above.
Install pinned pyproj 3.7.2 before importing the scientific contract in cloud.
Prepare the browser harness for the nominal-width query, object evidence,
source pointers, atlas evidence, disabled seasonal playback, and only the Pacific
member's new width coverage indication. Retain the existing identity, navigation,
and narrow viewport checks.

Then execute one sequential cloud job on the shared delivery queue, one CPU,
nice 15, with one worker per runtime. No local native/WASM build, installed
packet/index load, browser automation, field processing, or bulk preview sync.
No installation is authorized by these harnesses. A separate verified delivery
and installation step must precede any coverage-counter increase.
