# Compatible Loop delivery: bounded object-response correction

## Observed first case

Run40160374637, attempt1, job121070473227, source
`a4876d9af75a45e046399c0048c06e1f19adbeda` is terminal failure. Its request was
disabled at remote `ddae2dff6cd2a8cc464f2c66b782e92ace1d2a09` before review.
No working-branch data installation or main merge occurred.

The compact artifact's complete length/hash was verified. Its preparation
receipt proves 108574 candidate rows and a lossless index extension: all597
original sources checked,596 strings preserved and only the dashboard replaced,
with four new sources for601total. Actual job logs show both native and release
WASM compilation finished. The next main-store query exited0 but exceeded the
shared test helper's131072-byte response bound. Its stderr was empty. The old
failure did not identify the exact request or record response size, so neither
that size nor a completed native/WASM parity run is claimed.

## Narrow correction

All executed v1 code, profile and workflow remain byte-for-byte unchanged.
The v2 controller/Node runner are separate, source-bound files. The exact same
candidate must reproduce:

- SHA256 `b4d60a69eeea0339e06088f0b1e737ef50ec2983521615dc96341dd69d736551`
- 189986194 logical bytes.

Keep131072bytes for main scalar queries. Permit at most2097152bytes for detailed
object queries and retain the existing2097152-byte source-query bound. Apply
the same rule to native and WASM. Do not truncate, omit fields, replace expected
rows, skip queries or relax any semantic comparison. Native exit codes, valid
JSON, explicit `ok:true` and a32768-byte stderr limit remain required.

Record every native request, exit code, stdout length/hash, allowed length,
stderr size and decode status before semantic assertions. Upload this compact
custody record even if a later query fails. The next actual case must confirm
which object response needed the larger bound; this is not inferred from the
first run's missing diagnostics.

Seven small v2 checks passed in0.819s on one BelowNormal CPU: local/environment
refusal, complete object retention above the old bound, unchanged scalar and
finite object bounds, failure/JSON/stderr handling and the planned query cases.
No local build, browser, real packet/index or compiled binary was opened.

## Execution and review

The initial v2 request is disabled. First back up source and verify its held
workflow; then activate only that request. Use the same single cloud job and
shared lock. All earlier requests, including failed v1, must remain disabled.
The complete v1 data/preservation, compiler dependencies, eleven main and
nineteen source comparisons, corpus-mismatch refusal, browser checks and actual
screenshot review remain required. Keep partial artifacts explicitly partial.

Retain the exact source/step/job identities and disable v2 at terminal status.
No local heavy work or overlapping cloud case. Install only reviewed saved
artifacts on the existing branch after all checks; no new PR or main merge.
