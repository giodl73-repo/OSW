# WSC selected-core width and variability batch

## Required outcome

Integrate the published 28 km selected-core width and separate 7 km standard deviation from Dundas and Fer (2026) into the atlas width inventory and shared Rust/WASM current-card, seasons and query presentation. Preserve existing 2015 stream-tube records and every other current. Keep whole-current width, annual physical range, geographic edge coordinates and ranking unknown/ineligible. This is part of draft PR 83, not a new PR.

## Source work completed

Final 19-page publisher PDF retained unmodified (9,421,023 bytes, SHA256 b19a8eab70d72c12f55335d70950a1722283b330b1d805f9b82af1a1ff649fbf). License visually checked; width paragraph p.1008 and Table 1 p.1006 visually inspected. The extraction records one published statistic and the three exact target-section sampling windows. Protocol distinguishes full-column Q from water-mass QAW and section-selection percentile from peak-fraction thresholds. It retains mapping scales, satellite current reference and prior known DAC problems.

Dataset DOI 10.21335/NMDC-1222822416 resolves to current NMDC metadata. DataCite and provider landing snapshots are retained and pinned; three HEAD responses establish available file sizes. Native glider fields are not acquired. Exact reproduction would require the authors selection/threshold and satellite reference fields; those are not invented.

Four tests and ten subtests pass (0.50 s): original/exact scope, SD promotion rejection, operator/reference rejection and date-window rejection. Two successive figure generations yield identical SVG/PNG hashes. The new figure was visually inspected. The source package has a seven-role direct review with integration conditions.

## Original integration checklist (implemented; release gates noted below)

1. Add one scoped width row: 149 to 150 records, still 79 owners. Keep the reported SD separate from width_range_km.
2. Extend WSC validation so the existing six stream-tube rows remain exact while the new known ID uses its own source/metric contract; reject unknown WSC rows and identity transfer.
3. Bind source audit and measurement in compiled Rust; expose point, SD definition and observation windows consistently in query/cards/seasons. Add accessible numeric alternative and source inspection.
4. Register source/audit/figure documents and update dashboard fingerprint only for the WSC owner.
5. Verify preservation, native/WASM parity and corruption rejection, source inspection, keyboard/320px/reduced motion, then run a clean combined offline gate.
6. Publish all commits to the existing branch/PR after checking the in-flight upload. No main merge.

The separate be51979 annual model UI candidate is undergoing its own clean full offline suite in another worktree. That test result cannot be used as a full gate for this new source package or its future integration.

## Integration candidate implemented

The prepared inventory now contains 150 scoped records for 79 owners. All 149 prior width records are equal by value. A compiled Rust module binds the new row, standard deviation, method, owner, source dependencies, figure and three observation windows, and requires the record whenever its owner/evidence is present. Unknown or transferred copies reject. The six existing tube rows and their chart remain separate.

One shared browser renderer presents the statistic, separately labelled SD, unknown whole-current/annual values, source figure, numeric mission table, source query and record inspection. Card details collapse by default; query and selected-record pages open them. Seasonal playback is disabled. All five new JSON sources are indexed (307 total).

Preservation proof: all 42 other collections remain equal; all earlier width rows remain equal; other objects and six seasonal route projections differ only in the required seasonal source fingerprint. All six original frame objects are unchanged, and only WSC's dashboard update fingerprint changes. Query returns no map geometry for the new record.

Build verification: all 53 Rust tests passed in 2.26 s; native and WASM compiled; JavaScript syntax passed. The focused browser path passed cards/seasons/query/inspector/source, 320 px/reduced motion, alias separation and the old six-method comparison. Four altered SD/range/identity/annual cases rejected in both engines before the final presentation-only compaction. The final UI-only path passed after compaction, including all five source documents; engine/data bytes were unchanged by that UI edit. A separate source-only run also passed all five documents. A broader Python validation run and clean combined suite remain tracked separately; do not treat historical be51979 results as this candidate's gate.

Focused Python gate: 48 tests and 658 subtests passed in 454.99 s, including the full width-inventory and seasonal-route validators.
