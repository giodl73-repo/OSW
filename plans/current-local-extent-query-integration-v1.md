# Local extent query integration v1

Status: Rust source and native/WASM entry points prepared; compilation and
runtime checks remain outstanding. The installed query engine is unchanged.

Source preparation checks: the edited files were parsed/formatted with the
installed1.95.0 formatter on one BelowNormal CPU. Six fictional cloud-gate
checks passed in2.908s; workflow structure, embedded request-reader Python and
Node parity-script syntax were checked separately. No Rust compilation, native
query execution or WASM execution has occurred locally.

## Dataset and scope

Load only `research/eacc-local-extent-evidence-bundle-v1.json`:835839bytes,
SHA256 e4ca7c532c39d22efc2d6600a89424f48558669fe6e6682b1c6ec9442d00cdf8.
The two public collections are `current_local_extent_cases`(72) and
`current_local_extents`(864). Exact-byte custody precedes parsing. A changed
snapshot needs an explicit reviewed version; semantic similarity is insufficient.

`LocalExtentStore` constructs a small internal query store and reuses the
existing Rust filter, field validation, sorting, offset/limit and record code.
It does not load the full atlas packet, its spatial features or a workspace
journal. Its internal empty objects array is not exposed as a current catalog.
Dataset metadata and every response identify the research scope. Existing
whole-current width counters and the main atlas store are unaffected.

Queries accept the established `Query` JSON with explicit collection, scalar
filters, text, sort, offset and limit. Existing limits remain1–500 rows,
20 filters and1000 text bytes; the outer request cap is20000bytes. Unknown
fields/operators and physical state, geometry, seasonal, taxonomy, evidence or
network joins are rejected. Null physical widths are not zero. Failed and
unresolved cases remain queryable. Record inspection of an extent includes its
original seed case; that point is not a shore or physical current boundary.

## Interfaces

Native:

```text
osw-query-cli --local-extents research/eacc-local-extent-evidence-bundle-v1.json
osw-query-cli --local-extents research/eacc-local-extent-evidence-bundle-v1.json QUERY.json
osw-query-cli --local-extents research/eacc-local-extent-evidence-bundle-v1.json -
osw-query-cli --local-extents research/eacc-local-extent-evidence-bundle-v1.json --record -
```

The record request is `{ "collection": "current_local_extents", "id": "..." }`.

WASM uses the existing allocation/result ABI plus separate
`osw_local_extents_load`, `osw_local_extents_metadata`,
`osw_local_extents_query` and `osw_local_extents_record` exports. Its store is
separate from the complete atlas and index stores. A failed local-extent reload
clears that store so subsequent queries cannot silently use an older snapshot.

## Serial verification

Local work remains source edits, one-CPU source formatting and small metadata
checks. No local native/WASM compilation, full index load, provider refresh or
browser automation is permitted at this stage. All83 executed scientific inputs
remain unchanged.

The dedicated cloud check must be held behind an execution-disabled request
until source preparation is frozen and backed up. Keep the acquisition phase
at source-review-only-v1; a build-only request does not enable scientific data
acquisition, old producers, physical measurement admission or packet installation.
Use the existing shared `osw-current-gap-delivery` concurrency group, one job,
one actual CPU, nice15, one Cargo job/test thread and one numerical worker.

Order: committed-source/custody gate, pinned1.95.0 formatter check, locked Cargo
dependencies, targeted native tests, native CLI build, WASM library build, then
native/WASM parity on only the small reviewed snapshot. Do not invoke the full
atlas build helper. Preserve exact source SHA, tool versions, test results and
compiled output fingerprints. Do not install any artifact on a failed gate.

The seven native tests cover exact data custody, unchanged research scope,
primary monthly scalar queries, six coarse primary failures, null-versus-zero,
complete pagination, record-to-case resolution and rejected physical/unknown
queries. Native/WASM parity and failed-reload checks remain required in cloud.

## Delivery still required

After actual checks, connect the worker and existing query UI to this dataset
explicitly. The small path must fetch only its scalar snapshot and matching
compiled engine, not assemble the complete atlas packet. Keep workspace and
physical-join controls unavailable for this scope; show source/model support and
the monthly bracket figure. Verify source navigation, record inspection, shared
queries, missing outcomes and admission labels before claiming installed UI
coverage. Preserve all wider current/eddy, dimension and OSW state-join gaps.
