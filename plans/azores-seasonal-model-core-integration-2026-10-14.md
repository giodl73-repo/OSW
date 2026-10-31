# Azores seasonal model-core integration

Continues PR83 and the same current gap branch. The two reviewed primary-source
core widths now join the live inventory, indexed source corpus, native/WASM
query, source inspector, seasonal cards and Azores dashboard evidence links.

Approximate spring 240 km and autumn 400 km values retain the >2 cm/s regional
inverse-model criterion at 19.5 W. WOA09 quarters are April–June and
October–December. The reported 240–400 km model-climatological seasonal
extremes are distinct from a whole-current annual physical range. Width errors,
fixed-depth width layers, geographic edges and monthly evolution remain
unknown. No mapped band, monthly interpolation or scientific admission added.
The earlier 110 km 2009 survey width remains separate. The standalone source
record retains its review-stage status as an immutable snapshot; the new audit
records the current editorial integration stage.

Source bindings: Python regenerates/compares the normalized rows against the
frozen reviewed extraction and protocol. Rust embeds the exact audit, checks
both mandatory identities and source pin, and compares complete row/context
values independently of editable owner fields. The legacy 2009 row remains
valid under its own scope. Native/WASM rejection checks cover substituted
quarters, promoted full-width inference, removed records and rebound sources.

Counts: **138 scoped width records / 72 canonical owners**, **218 exact indexed
source documents**. Existing 211 scoped query samples, 25 diagnostics, 17
series, 73 reference routes and eleven published ranked lengths unchanged.
All prior 136 width records and seasonal route frames are preserved; only the
Azores dashboard entry changes. Previous observation dates are unchanged.
Neither the broader physical gaps nor independent scientific admission is
complete.

Integration fixes discovered during validation:

- Added required seasonal-summary interpretation and a Python regression
  gate. The initial browser load exposed this missing runtime field. The
  initial full-suite attempt was stopped before rebuilding and is not counted.
- The preceding commit's remote CI passed acquisition, stdlib and full
  offline gates, then exposed old browser assertions for 72/99 samples/maps.
  The gate now requires 84 monthly component samples across seven owners,
  twelve per owner, and 111 mapped / 100 unmapped samples. It also uses the
  platform-aware CLI path and a guaranteed scratch directory.
- Browser quarter checks are keyed by source label, avoiding a dependence on
  query-result ordering. Prior JSON text and Unicode encoding are preserved.
- The comparison link appears on its own line in the mobile source card.

Focused Python: eight tests / fourteen subtests passed. Rust/native/WASM:
46 tests passed. Azores browser passed both quarter cards, atlas map-card navigation, source
pointers, mobile and parity, plus four native/WASM rejection cases. Updated scoped-sample
browser passed source/value/calendar/metric binding, card navigation, null-last
ordering and mobile. All 218 source hashes/byte counts and engine pins verified.
All 54 almanac JavaScript files syntax-check successfully.

Full offline and 218-source index-store browser gates passed. Final
results are recorded below. Remote status will be tracked separately
at the publication head. The same draft PR remains the destination.

## Final local verification

**1,366 tests / 1,009 subtests passed**, 1266.90 seconds (21m06s).
All 46 Rust tests passed with serialized native/WASM builds. Azores browser
passed both quarterly cards, atlas navigation, source pointers, mobile and
native/WASM parity, including four native/WASM source/promotion rejections.
The corrected width-sample browser passed. Index-store browser passed 218
exact sources, twelve seasonal snapshots, independent NOAA oracle, parity
and checked-input failures. All 218 source hashes/byte counts and engine
pins verified. Prior scientific arrays, routes, samples and geometry frames
are unchanged; seasonal route rows only refresh their inventory receipt.
Mobile source card and comparison figure visually reviewed. Internal role
review permits this editorial delivery; independent scientific admission
and the broader core-data objective remain open. Remote CI is tracked at
the new publication head; no green remote claim is made here.
