# AX08 core-velocity runtime delivery

Runtime implementation is prepared in
`rust/osw-query/src/published_seasonal_core_velocities.rs`, with pure Python
projection and lossless source-index extension. The separate query collection is
`current_core_velocity_estimates`; it preserves the fifteen Pemba rows in
`current_speed_statistics`. The shared renderer dispatches both scene types in
query, atlas and seasons views. Seven previous runtime sources are retained with
hashes in `research/atlantic-ax08-core-velocity-runtime-history-v1/` and match the
saved installed engine manifest. Entry pages use revised cache versions.

The [source-preparation plan](atlantic-ax08-published-seasonal-speeds-delivery-v1.md)
and its frozen receipt remain unchanged. Ten lightweight Python checks and three
JavaScript DOM checks passed sequentially on one CPU at BelowNormal priority.
Rust source was formatted, but its new tests have not been compiled or executed.
The cloud query/browser contract is
`research/atlantic-ax08-core-velocity-query-contract-v1.json`.

The Python projector requires the exact installed logical parent and only adds
six rows, three object joins and its source/manifest bindings. Its index adapter
requires the exact installed catalog, preserves every old document string and
adds one new document: 628 to 629. The adapter has been exercised only on tiny
fixtures. Installed packet/index files were not opened locally.

Rust validates complete source-bound rows and owner joins on bundle load. Query
scenes use all filtered matches before pagination. Unknown owners yield no scene.
Atlas and seasons snapshots reuse the existing speed-scene map, adding three
owners while preserving the existing Pemba scene. The UI keeps points, prose
intervals and greater-than thresholds distinct, with exact source-record links
and no invented dates, errors or geometry.

Next, prepare a separately scoped cloud build against installed logical parent
`037ef0045d75dac4b8893df9bf200bd55e049d4708ceaa56195df9d6da9f5cc4`.
Use the retained runtime archives to preserve historical source contracts, extend
the source index before compiling its catalog, and generate a matching engine
manifest. Execute the query contract, complete atlas/seasons comparisons and
desktop/narrow browser checks in one sequential cloud job. Independently inspect
its evidence before installation, then verify exact installed bytes and disable
the request. Preserve unrelated measurements, source strings, main and the local
preview. Do not claim updated coverage until installation is verified.

Browser rendering, native/WASM parity, whole-index preservation and installation
remain unverified. No cloud job is requested by this source-only change. The
existing one-job sequence and source-review-only phase remain in force.
