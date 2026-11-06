# EICC route-inventory correction

Status: source preparation; no new cloud case activated or data installed.

## Evidence

Cloud run40389475234 attempt1 compiled the native engine and passed all six
planning tests. Its first native query failed at the Madagascar coastal
validator's complete route-table comparison. The NwASC validator has the same
independent omission. Both previously expected only the original78 routes.
The observed failure and source diagnosis are preserved in
`research/eicc-reference-delivery-failure-review-v3.json`.

## Correction

Both validators retain their original route projection, then append only rows
returned by `planning::eicc_reference_routes`. That function checks the complete
immutable EICC query contract and source receipts. No scientific admission
rules, measurements, source documents, route geometries or data projection
change. Original runtime sources are archived byte for byte in
`research/eicc-reference-runtime-history-v4/`.

Two `eicc_extension_` Rust tests combine the existing small NwASC, coastal and
Indian/EICC fixtures. They check the original78-route prefix plus the two
verified additions, both global validators, planning and cohort validation,
and rejection of changed routes, omitted routes, duplicates and bad receipts.
These tests have not yet been compiled or executed. Source-only checks found
compatible receipts across154 dependencies and80 distinct expected route IDs.

## Next sequential cloud stage

1. Prepare a disabled v4 controller, matching-engine overlay and preflight.
   Use `research/eicc-reference-runtime-scope-v4.json`: six changed Rust
   sources, two existing UI changes, original98-source compiler inventory,
   and all historical source archives and relocations retained.
2. Preserve all v3 source files, evidence and its disabled request. Do not
   modify or reactivate the executed v3 controller.
3. Require the six existing planning tests and both new `eicc_extension_`
   tests before the native smoke and WASM build. Require exactly the same
   candidate bytes as v3 (190404811 bytes; SHA256 recorded in the v4 scope).
4. Retain full parent/candidate atlas and seasons preservation checks, all
   native/WASM query and source parity checks, index mismatch refusal and
   browser review. Emit small parent/candidate catalogue counts as evidence.
5. Commit and back up only the exact source delta through the established
   guarded GitTree overlay; preserve remote generated data. Prove the held
   workflow skips all execution stages before activating one cloud case.
6. Observe only that case while it is live. Disable its request after it
   reaches a terminal state, then inspect evidence and actual screenshots.
   Install only after all required matching-engine and presentation checks.

No local native/WASM build, full packet/index load, original observation
processing, browser automation, main merge or new PR is part of this stage.
This work adds regional references; it does not close a whole-current
physical length, width or seasonal-range gap.
