# EACC existing-record presentation check

The reviewed regional distance already exists in the installed Indian coastal
context cohort. Reuse its exact record and source IDs. The new SVG and card
image are presentation only; do not add a query record, source, route or length.

Use the exact remote parent `1d98d9768959f1a357f3aa9933b86f203a4290bd` with
engine manifest SHA256 `61a430e3db980104bfe6ec80a08192d04d00d9742d4a68b6276421a93bb04a63`.
Read and verify all existing manifest files in the cloud before overlaying
the display. Change only `almanac/current-source-evidence-ui.js`, add only
`figures/eacc-regional-connection-v1.svg`, and retain all other manifest fields,
data pins, native/WASM assets and earlier presentation metadata. Record the
overlay in its own namespace. No packet restoration or processing locally.

The manual workflow uses the shared `osw-current-gap-delivery` concurrency
group, cancel-in-progress false, one cloud job, one CPU and low priority.
Its explicit request is disabled during preparation. Activate only this
request after confirming no live heavy cloud job; keep the global phase and
all older requests disabled. Freeze the producer/checker/tests/visual/source
contract pins before executing. No native or WASM build is required.

Verify the exact installed EACC row through the saved WASM object view,
rendered SVG loading, no page errors, no horizontal overflow at 320/390 px,
two retained card screenshots and keyboard navigation to the existing exact
query. Stream-verify all inherited files again afterward. Retain compact
receipts plus the UI, SVG and overlay manifest; never download the packet or
WASM locally. Source record counts and coverage must remain unchanged.

Actual screenshots must be visually reviewed before a separate guarded
working-branch presentation installation. No installation, main merge or
scientific release is performed by this workflow. Preserve failed receipts
and disable the request after its actual case terminates.
