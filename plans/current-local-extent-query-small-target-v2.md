# Dedicated local extent query target v2

Status: source preparation. Compilation and runtime parity for this target have
not yet run. The installed atlas, query worker and data packet are unchanged.

## Reason and compatibility baseline

The verified general engine from run40131603572/attempt2 is59201757bytes.
Retain artifact12574929493 as the reference; its compiled WASM hash is
e5d119b8978e24469ed31fa2f9e0fb826c76df40dc8c7c51f93a74cef179486f.
It remains cloud-only. Preserve the v1 preflight, executed reports and source
history; this is a new operational build case, not a numerical-method rerun.

## Shared source and dedicated crate

`rust/osw-query/src/scalar_query.rs` contains field discovery, exact numeric
equality, scalar predicates and sorting. The complete atlas query engine uses
these same helpers, preserving its physical selection and rendering branches.
The local extent store uses the scalar store directly, removing its dependency
on the atlas bundle, empty objects, spatial index and workspace journal.

`rust/osw-local-extents` imports that scalar module and the same local extent
store by source path. Its dependencies are the existing locked serde,
serde_json/float_roundtrip and sha2 versions. The initial dependency lock is the
reachable subset of the already verified lock, preserving registry checksums;
`cargo --locked` must verify it in cloud before any artifact is accepted.

The dedicated crate supplies the same local-extent CLI flags and WASM
allocation/result/load/metadata/query/record ABI. Exact metadata, supported
query results, unresolved rows, original case context and known refusal behavior
must match the recorded general engine. Full-atlas loading, physical joins,
workspace changes and whole-current width admission remain unavailable here.

Pagination counts use u32 in the scalar-only request type so native and wasm32
agree on overflow refusal. The valid WASM count range is unchanged. Extended
overflow tests require both new native and WASM code to reject values above
u32::MAX; the baseline must also reject them, with its older error wording
allowed. Ordinary atlas Query fields retain their existing types.

## Data and physical scope

The data remain835839bytes, SHA256
e4ca7c532c39d22efc2d6600a89424f48558669fe6e6682b1c6ec9442d00cdf8:
72 cases/864 attempts on2013 daily00Z monthly mean fields at15m. No velocities,
distance calculations, source refreshes, peak changes or physical measurements
are added. All83 executed scientific inputs must remain byte identical. Runtime
files may change under this new case while their v1 Git/artifact history remains
preserved; do not overwrite the executed v1 preflight/report records.

## Delivery budgets and serial verification

Dedicated raw WASM must be at most2MiB. Its WASM memory after the scoped checks
must be at most64MiB. These are software delivery budgets, not geophysical error
bounds. Do not download/install a failed or oversized target locally.

Use the existing acquisition hold plus a separate default-disabled build-only
v2 request. Shared concurrency:osw-current-gap-delivery, cancel-in-progress=false.
One actual cloud CPU, nice15, one Cargo job/test thread/numerical worker. Keep
local work to source formatting and small metadata/control checks.

Order: source gate and83-input verification; pinned1.95.0 formatting; locked
dependencies; dedicated native tests; targeted atlas scalar/schema tests;
native CLI builds; dedicated WASM build; exact baseline artifact custody and
cloud-only restoration; then native/WASM/baseline parity. No complete atlas
runtime packet or provider data is loaded.

Parity covers the original ten queries plus existence, inequality, text,
numeric bounds, sorting, invalid operators/types and maximum valid pagination.
Compare both native CLIs with the dedicated WASM and recorded general WASM.
Check three record-to-case resolutions, failed reload/recovery, normalized
pagination overflow and delivery budgets. Retain compact reports, compiler and
binary fingerprints; upload only the dedicated binary and reports, excluding
the59MB baseline and build directories.

## Remaining delivery

After actual checks, wire the existing worker/UI to this explicitly selected
small research dataset and matching engine. Verify filters, shared queries,
case inspection, missing outcomes, source navigation and evidence chart in
serial cloud browser checks. Preserve ordinary atlas assets and physical width
coverage. Wider current/eddy measurements, uncertainty and state joins remain
active gap work.

## Initial execution and operational correction

Run40135768056, attempt2, source857382e5e6d51505e11bb0c178ac5dc4cd8116a2
passed all11 dedicated native tests and verified the locked dependency closure.
The atlas-side build then stopped because index_store still calls
`crate::compare`; the extracted comparator needed a root re-export. No WASM or
parity stage ran. The failed run/source and original v2 preflight remain in Git
and the retained cloud artifact. The request was disabled before correction.

Operational revision2 restores that comparator alias without changing its
implementation, the scalar dataset or any83-input scientific file. Native,
WASM, size/memory and baseline parity verification must be rerun on the newly
bound source. The failed case is not represented as a passing build.

Revision2 run40136912099, attempt1, sourcefb6e30c4fd2b505f6f2dd2fe2cc37c2cc1035486
passed11 dedicated tests,6 shared atlas scalar tests and1 null-versus-zero test.
The normal native CLI build then found `filter_equal` gated by `cfg(test)` even
though index_store uses it in production. Revision3 makes the shared import
unconditional. A source-wide audit of root references to the extracted helpers
found index_store uses `field`, `compare` and `filter_equal`; all three are now
unconditional aliases. No helper implementation or scientific data changes.
Normal native and WASM builds, budgets and reference parity remain unverified.

Revision3 run40137555025, attempt2, source31769db0d862432cde14c8aa01a941451bd0e955
stopped before compilation because checkout depth8 excluded the reviewed parent.
GitHub comparison confirms that source is8 commits ahead of the parent, so the
parent requires a ninth history entry. Revision4 changes checkout depth to32;
the existing ancestry, source hash and allowed-change gates remain intact.
No code compilation result is claimed for revision3. Execution is disabled
while this workflow-only correction is frozen and backed up.
