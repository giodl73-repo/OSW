# AzCC saved-engine browser verification

Reuse candidate artifact 12847976218 from run 40756436860, without native or
WebAssembly compilation or installation. Its 261 Rust tests, 129 main and 50
source whole-response comparisons and three complete API comparisons passed.

The first browser harness stopped after five valid desktop captures because a
671.765625px article could not fit inside the atlas scroll ancestor. Preserve
that failure and harness. The v2 harness changes only that capture target into
three actual visible parts: heading, width chart and source link. Each is
scrolled into view and checked by the same clipping rejection. Do not remove
the sidebar scroll limit, change styles, or count a clipped image as reviewed.

Complete all prior semantic checks and both desktop/narrow viewports, now with
22 captures. Require exact source navigation, preserved 2009 section, disabled
seasonal playback and the dashboard updated badge. Individually review all
actual images after automated success. All scientific data, WASM, runtime
assets and the engine manifest must remain byte-identical to the saved engine.

One cloud job, one CPU/numerical worker, shared non-cancelling delivery queue.
All 85 older requests stay disabled. Main and local bulk preview stay unchanged.
