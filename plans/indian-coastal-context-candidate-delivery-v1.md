# Indian coastal context candidate delivery

Status: implementation prepared, not executed or delivered. The committed
metadata contract is unchanged. No new physical measurements are admitted.

## Parent and candidate

Use the exact installed Baffin packet with logical SHA256
`045d6fd80b871ba7a9863154f390d7c84a450f4b3e960b3f5f4e27b8d6a009b0`.
Verify its installed proof (SHA256
`54b54ab66c0fe4d418c6da3a73542c075c61b99b0c3eba80a93e59f55488005d`)
and all packet/index/dashboard descriptors before reading transport parts.
The proof and packet descriptor were checked against remote source commit
`d5d9c5dbc9216ed09d11998cc7423b8abeb41bd3` without reading any packet parts.

The candidate appends seven exact context/provenance rows: two typed regional
descriptions, three sources and two claims. Preserve all existing rows and all
244 unrelated owners exactly; update only the two relevant owners' context,
claims, source references and associated fingerprints. Preserve their physical
fields and physical capabilities. Expected inventory: 108551 rows, 246 objects,
106 named currents, 172 scoped width records. No extra ranked length, paired
width, observation array, annual range, geographic route or state join follows.

The exporter requires explicit cloud opt-in, at least 3 GiB free disk and 6 GiB
available memory before opening the parent. It extends the existing source
index, preserving every historical source string except the declared dashboard
refresh. No historical scientific producer is replayed.

## Verification state

- 35 source-context synthetic checks passed previously; unchanged contract and
  inputs remain pinned.
- 18 new candidate preservation/receipt checks and six export/resource refusal
  checks pass locally on one CPU with BelowNormal priority (24 tests, 0.36 s).
- Seven Rust guard tests are written but **have not run**. They cover exact rows,
  source pins, source catalogue, partial admissions, owner references, navigation,
  scope/date/review corruption and physical/foreign-object promotion.
- The exporter has **not run** against a real packet. Its refusal tests do not
  prove actual export correctness.
- No local build, original-array processing or browser automation was performed.

## Remaining serialized cloud gates

1. Add a workflow using shared concurrency group `osw-current-gap-delivery`,
   with cancellation disabled. Confirm no other heavy cloud job is running.
2. Format only changed operational Rust sources, then export one candidate in
   an isolated checkout. Pin the actual formatted runtime bytes in its receipts.
3. Run native tests and complete-candidate query checks, then compile WASM.
4. Compare native/WASM queries and both object views. Verify six preserved
   source documents and exact source-index custody, including the pre-existing
   EACC acquisition receipt.
5. Check both card values, region, proxy, separate time supports, source locator
   and query links with keyboard navigation and 320/390 px reflow. Preserve the
   absence of fabricated geographic marks or seasonal polygons.
6. Run existing source matrix/current-card/atlas gates against this same saved
   candidate. Reuse it for presentation fixes rather than replaying science.
7. Record actual results and inspect rendered screenshots before installing the
   verified working packet. Keep the existing PR; no main merge or scientific
   release is part of this batch. Rotschi1972 remains a separate unresolved gate.

The phase remains `source-review-only-v1` until that workflow and its focused
browser gates are ready. Prepared implementations do not establish delivery.
