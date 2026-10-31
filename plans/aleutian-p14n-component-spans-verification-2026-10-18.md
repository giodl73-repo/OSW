# P14N component-span verification

Baseline: `4f407bbce1b50c481a6ecd9e2fe74e8f6961f175`. Continuing draft PR #83.

## Completed checks

- **18 source/operator/registry tests and 18 subtests PASS**, 15.25 seconds.
  This includes eight new operator tests: geodesic/interpolation reference,
  nearest-lobe crossing, missing/window/time-gap stops (including the exact
  90-minute boundary), acquisition-order tie handling, weak-peak and invalid
  sensitivity outcomes, common-offset algebra and all five dependency pins.
- **60 Rust tests PASS**, 2.21 seconds. Locked offline native and release
  WASM builds pass. Final WASM: 21,905,343 bytes; query packet: 81,315,043 bytes.
- **Dashboard affected-owner check PASS**, 34.96 seconds, 22 unrelated tests
  deselected. The existing NumPy binary-size warning remains visible.
- Deterministic registry/dashboard/query/index/engine generation passes.
  There are **326 indexed JSON documents**, 45 query collections, 43
  diagnostics and five shared research scenes. All **91 engine pins** and
  **152 research dependency pins** match the working files.
- Preservation check passes: all 155 width rows, 42 other diagnostics,
  four other research scenes, original velocity/hydrography records and their
  custody/figure receipts, and seasonal route-frame bytes remain unchanged.
  Only Aleutian's object and diagnostic differ in the query collections.
- Final PNG visually inspected after correcting clipped scenario labels.
  Source-order vector curves, crossing brackets, distinct sensitivity rows,
  date/layer/units and the temporal-crossing caveat are visible.

## Actual browser delivery

Actual browser gate **PASS**: all five owners across cards, seasons, query,
source inspection, inspector, mixed diagnostics, keyboard, 320px and reduced
motion; all39research source documents queried. Both Aleutian companion views
load. All49native/actual-WASM corruptions reject, including all42earlier cases
and seven new span/bracket/scenario/metric/admission/envelope/protocol cases.
Every fixture loads successfully over HTTP; no automatic PDF/ZIP/MAT/NetCDF
original requests. Final figure and Aleutian mobile panel visually inspected.

Committed-pin and normal-root HTTP checks remain the publication condition
immediately after commit. A clean combined successor suite remains required.

### Publication check completed

Scientific/UI checkpoint `73de1a21d750fae1481b622a02eb5a8334a7b61e`
is committed and pushed to the same branch/PR. Normal port8788 HTTP serves
the exact WASM, query packet, source catalog/store and both new figures.
All91engine and152research dependency hashes match working files **and
committed blobs**. The rebuilt native CLI returns the100/80km component
spans and complete original17cast/132profile context; width admission remains
false. The remote branch hash matches. These checks satisfy the focused
publication conditions above; the clean successor full suite remains pending.

The clean full suite at baseline `4f407bb` **PASSED: 1,695 tests and 1,119
subtests in 2,215.36 seconds**, with clean start and end. It finished
2026-10-18 11:27:42 UTC and covers the prior hydrography join, not this new
component operator. A clean committed successor suite remains required.
Parent hosted CI failed before tests on
two separately inspected source-host failures; no green-CI claim is made.

No new inventory width, physical current edge, annual range or width rank
is admitted by passing these software checks. The 100 km and 80 km nominal
values remain exploratory local component endpoint separations, with the
temporal and velocity-sensitivity limitations recorded beside them.

## Completed clean combined gate

Committed head `9092076b12ba488e094a29f75d15efa6e73e3f52` passes the complete
Python suite: **1,703 tests and 1,127 subtests in 2,250.30 seconds**, clean
start/end, finished 2026-10-18 12:21:24 UTC. All60Rust tests and the required
native CLI build preceded this successful attempt. The first fresh-checkout
attempt was intentionally aborted after a confirmed missing-CLI prerequisite;
its original log and receipt remain retained. No scientific assertion or
case was removed. This result covers the component-span stage and does not
certify the subsequent native-support additions.
