# EACC HYCOM velocity-response compilation v1

Status: prospective scientific implementation, exercised with synthetic packed
payloads only. No original velocity response has been acquired under this
method. This protocol and its operators still require a committed original-case
preflight, guarded sequential cloud acquisition and actual-source verification.
The source-review phase remains in force with heavy work disabled.

## Inputs and exact selection

Use the source and core definitions already recorded in
`plans/eacc-regional-model-core-width-protocol-v2.md` and the candidate
`research/eacc-hycom-2013-source-selection-candidate-v1.json`. The metadata-only
selection identifies the exact provider15m index,100x76 remapped output cells
and363 daily00Z samples in2013. It proposes82 bounded requests, no more than six
daily samples each, one request at a time. The candidate does not authorize
velocity acquisition by itself. Preserve the missing August14/December25
timestamps and source metadata bytes.

`analysis/eacc_hycom_source_compilation_v1.py` first reproduces the entire
selection with `make_selection` against the three original metadata byte
responses. Changed request URLs, coordinates, time indices, packing conventions,
thresholds or response limits fail before payload loading. The declared complete
response inventory must contain exactly one file for every planned request.
An incomplete download is a custody failure; it is not another provider time gap
that can silently reduce monthly coverage requirements.

## Response and custody validation

Each retained response requires the receipt schema
`osw.eacc-hycom.velocity-response-receipt.v1`, with exactly:

- request filename, requested URL and actual final URL;
- HTTP200 and a text/plain content type;
- UTC start/end timestamps, ordered within and across requests;
- response byte count and SHA256;
- the SHA256 of the canonical source selection.

The requested and final URLs must equal the exact selection URL. Do not silently
substitute another endpoint or follow a changed resource into compilation. The
cloud acquirer must retain failures and enforce the same8MiB cap while reading,
not merely after buffering. The offline compiler checks the cap before hashing
or parsing. Unexpected receipt fields, missing bindings, corrupt bytes, changed
selection identity or overlapping/out-of-order acquisition intervals fail.

Canonical JSON uses sorted keys, compact separators, no NaN and one final
newline. `canonical_receipt` hashes refer to this normalized receipt encoding;
they do not claim to hash arbitrary original receipt-file whitespace. Original
provider payload hashes always refer to unchanged response bytes. The future
acquirer must retain original responses and receipts rather than regenerate
provider payloads from decoded arrays.

Reuse the unchanged `parse_ascii` in
`analysis/acquire_south_australian_hycom_2d.py`. It requires both Int16 packed
components, declared time/depth/latitude/longitude shape, complete ordered
indexed rows, integer values in the Int16 range, and all eight coordinate maps.
Paired U/V maps must agree. The new validator additionally requires every map
to equal the exact separately pinned selection values, including the actual
depth and requested timestamps. No coordinate tolerance or axis swapping is
used. A structurally valid array at another location/depth/time is rejected.
Pin this helper and its complete imported dependency graph before original use.

## Streaming monthly calculation

Process requests in selection order, one response at a time. At each grid cell,
a pair is valid only when both components differ from the declared -30000 fill
value. Preserve the original mask; do not apply an external mask, discard dates,
fill missing vectors or classify a source mask as land. The compiler accumulates
paired counts and each component's packed sums in integer arrays, using Int64
sums. It does not concatenate an entire year or maintain all raw responses in
memory. Retain source hours and assert unique ordered monthly samples.

For month m, require ceil(0.8 × Gregorian calendar days) valid pairs. Missing
provider times do not lower this threshold. Decode the declared Float32 scale
0.001 to its exact binary32 value promoted to Float64; multiply the integer sum
by that scale before division by the paired count. Retain Float64 means without
display rounding. Insufficient support gives null for both components and
retains the actual count. Every one of the12 months remains in the output,
including months with no requests or eligible cells. Zero samples do not become
zero flow.

The output records all original-response/canonical-receipt bindings, metadata
hashes, selection hash, exact coordinates, units, standard output depth,
timestamps, paired counts, minimum thresholds and eligible-cell counts. It is a
source field on a remapped model grid, not a current outline or observation.

## Coupling to the diagnostic and visualization

The monthly latitude/longitude and nullable vector arrays feed the separately
frozen v2 `Field`/`diagnose_year` path. Nulls become unsupported paired corners;
they must not be converted to zero velocities. Retain all72 diagnostic cases,
including tied or missing seeds and every failed station/edge.

The original cloud case must retain complete source fields for reconstruction,
but local verification should retrieve only bounded reports and rendered
figures. The full source neighborhood, missing-support mask,12 monthly maps,
normal profiles, semantic support tables and later query/card/atlas links remain
required. No original field or full packet synchronization to this computer is
part of preparation.

## Remaining original-case gates

1. Implement a cloud-only acquisition runner that verifies branch/phase,
   committed source-request/preflight pins and resource limits before IO.
2. Retain exact HTTP responses, successes and failures with one request/worker
   at a time. Never overwrite an executed source or restart a live run merely
   because observing it timed out.
3. Pin source logic, tests, complete imported scientific dependencies,
   environment, metadata/selection, core v2 method and required visualization
   producers in a new preflight before any original velocity response.
4. Execute source acquisition, compilation and the declared diagnostic in the
   cloud sequence; inspect actual neighborhood/axis/edge figures before any
   named-current measurement admission. Preserve zero-support outcomes.
5. Deliver only the reviewed evidence class through query/native/WASM/cards and
   semantic presentation, with those heavy gates running sequentially in cloud.

Passing receipt binding proves internal byte/coordinate consistency, not
independent verification that the provider/model is physically accurate.
Whole-current widths/lengths, physical annual extrema, measurement uncertainty,
rank eligibility, state joins and named-current association remain unadmitted.
The separate Rotschi1972 offline-source/release gate remains unresolved; focused
synthetic checks do not establish main merge, full regression or release status.
