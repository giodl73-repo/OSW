# WSC selected-core width and variability batch

## Required outcome

Integrate the published 28 km selected-core width and separate 7 km standard deviation from Dundas and Fer (2026) into the atlas width inventory and shared Rust/WASM current-card, seasons and query presentation. Preserve existing 2015 stream-tube records and every other current. Keep whole-current width, annual physical range, geographic edge coordinates and ranking unknown/ineligible. This is part of draft PR 83, not a new PR.

## Source work completed

Final 19-page publisher PDF retained unmodified (9,421,023 bytes, SHA256 b19a8eab70d72c12f55335d70950a1722283b330b1d805f9b82af1a1ff649fbf). License visually checked; width paragraph p.1008 and Table 1 p.1006 visually inspected. The extraction records one published statistic and the three exact target-section sampling windows. Protocol distinguishes full-column Q from water-mass QAW and section-selection percentile from peak-fraction thresholds. It retains mapping scales, satellite current reference and prior known DAC problems.

Dataset DOI 10.21335/NMDC-1222822416 resolves to current NMDC metadata. DataCite and provider landing snapshots are retained and pinned; three HEAD responses establish available file sizes. Native glider fields are not acquired. Exact reproduction would require the authors selection/threshold and satellite reference fields; those are not invented.

Four tests and ten subtests pass (0.50 s): original/exact scope, SD promotion rejection, operator/reference rejection and date-window rejection. Two successive figure generations yield identical SVG/PNG hashes. The new figure was visually inspected. The source package has a seven-role direct review with integration conditions.

## Integration still required

1. Add one scoped width row: 149 to 150 records, still 79 owners. Keep the reported SD separate from width_range_km.
2. Extend WSC validation so the existing six stream-tube rows remain exact while the new known ID uses its own source/metric contract; reject unknown WSC rows and identity transfer.
3. Bind source audit and measurement in compiled Rust; expose point, SD definition and observation windows consistently in query/cards/seasons. Add accessible numeric alternative and source inspection.
4. Register source/audit/figure documents and update dashboard fingerprint only for the WSC owner.
5. Verify preservation, native/WASM parity and corruption rejection, source inspection, keyboard/320px/reduced motion, then run a clean combined offline gate.
6. Publish all commits to the existing branch/PR after checking the in-flight upload. No main merge.

The separate be51979 annual model UI candidate is undergoing its own clean full offline suite in another worktree. That test result cannot be used as a full gate for this new source package or its future integration.
