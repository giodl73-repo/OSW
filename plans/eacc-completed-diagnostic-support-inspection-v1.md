# EACC completed diagnostic: next support inspection

Prospective metadata projection, not a new measurement method. The completed
source/diagnostic case is run40117999392 attempt2, artifact12570726941,
eacc-source-resume-v2. The source acquisition gap is closed; the regional width
gap remains open. The full source year must not be acquired or compiled again.

## Exact question

Why do66 retained cases lack a seed-refinement search endpoint, and which
original axis checks fail in the January primary cases? The January/July maps
suggest a coastal-mask interaction, but the exact endpoint coordinates and
support status have not been extracted. Do not claim that cause is proven.

## Input and output

Use the existing cloud diagnostic JSON, SHA256
acc14e75d4cbfb6287d2db99e3eb71b01736e7d2693ad45c7a5a91d609e3d9e7.
Bind run/attempt/source commit, artifact API identity/digest, original executed
preflight and the retained result before reading it. Preserve all52 executed
continuation inputs and all40 original scientific inputs byte unchanged.

A new, separately versioned cloud projection should copy for all72 cases:

- Exact case identity, original status, anchor, seed and refined-seed metadata.
- Original initial-refinement peak object.
- Original initial-refinement sample rows within the declared40km search window
  plus the first retained unsupported sample on either side, when present.
- Whether each exact -40/+40km row is present and its original support status.
- Existing station origins, peak/axis failures and threshold statuses/scalars,
  without normal-profile arrays outside the search inspection.
- Source diagnostic SHA256 and provenance for every copied case.

This is a projection of existing output. Do not rerun seed selection, normal
sampling, width estimation, diagnostic cases or geographic producers. No new
velocity request, alternate row/month, narrowed search, imputed land velocity,
changed threshold, skipped failed case or parameter tuning is part of it.

## Sequential execution

Prepare tiny synthetic parser/provenance fixtures and a separately pinned
projection request/workflow. Keep the main source-review hold and use the shared
osw-current-gap-delivery concurrency group. Use a new operational entry point;
do not edit either executed parent controller now bound in the52-input freeze.
Only one cloud review job runs; there are no local source-array, native/WASM or
browser stages. Restore/read the existing diagnostic only in cloud, and retrieve
only the resulting bounded metadata locally.

Inspect the projected support before proposing any separately justified method
revision. A revised method would require its own prospective protocol, synthetic
validation and complete comparison to the retained failed case. It cannot turn
this completed case into an admitted seasonal current-width series.

## Implemented prospective entry point

`analysis/eacc_diagnostic_support_inspection_v1.py` uses only the standard library
for the projection. Its workflow is
`.github/workflows/eacc-diagnostic-support-inspection-v1.yml`. A committed request
and its own preflight bind the projection code/test, workflow, protocol, internal
review, two small pinned test/parser dependencies and retained scientific basis
metadata. The request stays disabled during preparation; source-review-only-v1
continues to prohibit heavy work. An explicit metadata-only request can enable
this separate one-CPU cloud review without altering either executed parent.

The workflow verifies the complete source/method gate before downloading an
artifact. It binds the exact successful run/attempt/source commit and artifact
id/name/size/digest/expiry, then verifies five retained file fingerprints in cloud
before projecting the diagnostic. It never reads the original response files or
monthly velocity grids. No numerical producer is imported or called.

The two CLI verification actions are `--verify-cloud-gate` and
`--verify-source-identity`. The sole projection action is `--cloud-project --basis
<restored-run-directory>`. Synthetic tests run with
`python -m pytest -q analysis/test_eacc_diagnostic_support_inspection_v1.py` under
one actual CPU and one worker. The same limits apply to the cloud projection.

The output includes every case, copied endpoint rows/statuses, first unsupported
rows, original station failures and source diagnostic fingerprints. It excludes
full normal-profile arrays, streamlines and original grids. JSON is capped at
512KiB. Bounded local readback of this small audit does not run any ocean-data
operator, native/WASM build or browser. It admits no current dimensions.
