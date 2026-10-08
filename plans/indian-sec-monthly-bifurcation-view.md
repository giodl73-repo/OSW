# Indian SEC monthly branching view

Status: locally validated candidate; protected-main publication pending.

## Contract

Render the two checked historical monthly branching-latitude series from `research/indian-sec-monthly-bifurcation-extraction.json` on the almanac index. Use the shared Rust/WASM source store; no browser fallback to unchecked source files.

- Retain separate surface SSH and upper-400-m layers, their source support periods and unknown WOD09 contributing dates.
- Show all twelve months, both curves, a selected month/layer, graph-reading allowances and an equivalent table.
- Preserve the extraction's raw numeric values. Enable serde_json float roundtrip parsing rather than accepting altered source numbers.
- Rust validates scientific scope, layers, month order, units and reading intervals and produces chart coordinates. JavaScript paints the returned scene and handles controls.
- Keep route geometry, current length, current width, annual dimension ranges and geographic playback ineligible. This chart represents historical monthly cycles, not changing geographic current boundaries.
- Share selected month/layer through URL parameters; retain other page parameters.
- Playback requires an explicit click, advances monthly, stops at December, and stops on selection changes, hidden pages or changed reduced-motion preference. No transitions or autoplay.
- On a missing or invalid corpus, clear the chart and table, announce failure and disable controls.

## Verification

`analysis/test_rust_index_support_browser.py` is already registered in the full browser gate. Its additional checks compare every selected month against the independent source and native Rust output, verify both curves, table, source scope, shared links, playback ending, keyboard input, mobile reflow and unavailable corpus. Rust unit coverage rejects unsupported scope, missing/duplicate months and changed reading allowances and preserves the difficult raw float exactly.

Run the engine builder, the expanded support browser check, the index page and source-store checks, all-collection check after the numeric parser change, page assignments, syntax and full offline suite. Required remote CI remains the publication gate.

## Publication

The candidate follows the inventory, endpoint-scope and monthly-extraction commits in PRs #25–27. #25 is on main; #26–27 remain draft at this receipt. Sync with main and retain their scientific scope before publication. Do not label the new chart mainline until its exact commit lands with required checks.

## Local validation receipt

2026-10-07: complete offline suite 771 tests and 592 subtests passed; 37 Rust unit tests passed; all 36 JavaScript modules and all 14 page assignments passed. Expanded support browser validation passed, including all 24 independently checked samples, native/WASM parity, chart/share/playback/keyboard/mobile/error behavior, 44-pixel controls and stopping playback on reduced-motion preference changes. Existing index-page, exact 67-source store and all 38 query-collection checks passed. The mobile chart was visually inspected. Engine manifest hashes match the source and binary files. This receipt does not establish the pending remote gate or scientific measurement completeness.
