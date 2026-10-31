# EICC planning-source correction and compatible delivery v2

The first cloud case compiled both engines and verified candidate preservation,
but its first native query exited2 before a response. Its diagnostic omitted the
42-byte stderr text. Source inspection identifies inconsistent planning bindings:
the top-level source URL changed while the nested projection retained the original
URL, and Rust only accepted the original worklist as the source catalog.

## Correction

- Preserve every executed v1 source and preflight. Retain its failed execution and
  compact artifact identity. The failed request is disabled and nothing was installed.
- Apply the v1 science-preservation projection, then make the EICC nested source URL
  agree with its new source. Carry exact candidate source bytes/hash and exact prior
  decision bytes in an explicit planning-revision receipt.
- Change only `rust/osw-query/src/planning.rs`. Archive its original bytes at
  `research/eicc-reference-planning-original-v1.rs`. Declare before/after hashes in
  `research/eicc-reference-planning-runtime-scope-v2.json`; preserve the other97
  Rust/Cargo sources and all143 noncatalog compiled data inputs.
- Rust accepts this revision only for EICC and the exact reviewed candidate-source
  hash, with both source-bound regional reference records, no physical/rank/annual
  admission, exact prior decision and unchanged unrelated planning fields. The
  ordinary source rules continue to apply to all other records.
- Capture bounded stderr text and its full hash for native failures.

## Sequential cloud verification

Use the same installed Loop parent, data extension, 24 main-store comparisons,
25 source comparisons and browser/map/phone checks specified in v1. Add four Rust
planning unit tests, and run a complete native single-route smoke check **before**
building WASM. The smoke check must inspect the exact source record and rendered
route feature; its success is separate from full native/WASM parity.

The source index still adds only the eight declared EICC documents. No new physical
dimensions, ranked lengths, seasonal extrema or canonical state links are admitted.

Prepare and verify a disabled held workflow before activation. One cloud CPU,
nice15, one worker and shared concurrency; no local builds, full packet/index load
or browser work. Preserve all18 earlier requests disabled. Disable the v2 request
after a terminal run, then inspect actual screenshots before separately installing
the exact saved artifacts on the existing branch. No main merge or scientific release.

Rust test and native/WASM/browser completion remain unproven until their actual
cloud receipts exist. This correction alone does not close a physical measurement gap.
