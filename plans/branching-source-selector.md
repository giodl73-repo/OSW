# Historical branching source selector

Status: local candidate based on PR #30 head `3e935f7`; protected-main publication pending.

## Contract

Provide one monthly chart workspace for Indian South Equatorial and Pacific North Equatorial inventory proposals. This extends the historical branching view without admitting either proposal as a measured whole-current route.

1. Load each original extraction through the checked Rust source store. `current_id` selects exactly one known source; omitted owner remains Indian for existing shared URLs. Owner and month fields are only accepted by the monthly-bifurcation support section.
2. Indian surface SSH and upper-400-m hydrographic series retain separate layers and periods. Unknown WOD09 observation dates stay unknown. Pacific accepts only surface SSH from October 1992 through December 2009; changing from the Indian upper layer selects surface SSH.
3. Rust validates twelve ordered months, signed degrees north, source scope, graph-reading allowances, available layers and band semantics. It returns chart coordinates on separate Indian (-19 to -15) and Pacific (8 to 18) latitude axes. Axes and status display the correct N/S hemisphere; no cross-basin visual magnitude comparison is implied.
4. Pacific shading reproduces the source-caption-labelled standard-deviation range. Each mean and each band boundary retains its independent +/-0.1-degree editorial graph-reading allowance. The source denominator, standard-deviation multiplier and confidence probability remain unresolved. The band is not a confidence interval, full observation envelope, annual extrema, width, length or occupied footprint. Indian variability is not extracted and receives no shaded band.
5. The complete selected series and separate band endpoint allowances appear in a semantic table. Source locator, period, scope, proposed card and share links follow the selected owner. Clear the scene, table, legend and navigable links on failure; use no unchecked fallback.
6. URLs persist owner/layer/month while preserving state and other page parameters. Playback remains explicit, stops at December, and stops on owner/layer/month changes, hidden pages and reduced-motion preference changes. Controls provide keyboard input, named slider values and at least 44-pixel targets; the 320-pixel layout reflows.
7. Source JSONs, the 38 imported query collections, candidate geometry and frozen release exports remain unchanged. Rebuild the common WASM binary and manifest after Rust changes.

## Verification and publication

Run `python analysis/build_rust_query_engine.py`, the already registered `analysis/test_rust_index_support_browser.py`, source-store and index-page checks, all-collection parity, JavaScript syntax, page assignments and the complete offline suite. The support check compares all 36 months to original source rows and native Rust, independently checks Pacific polygon coordinates, owner/layer rejections, signed labels, links, shared state, mobile layout, keyboard input, playback and corpus failure. Rust rejects altered band metadata, invented dimensions and invalid boundary reading allowances.

Review through all seven relevant project roles. Preserve PR #30 as its own frozen publication candidate while its 48-check gate runs. This selector needs its own complete protected-main gate after dependencies land; local success is not publication or scientific peer review.

## Initial local validation

2026-10-07: Rust test/build and WASM build passed (38 unit tests); the complete offline suite passed 773 tests and 598 subtests. The expanded source support browser check passed all 36 original monthly rows and native/WASM parity, signed labels, band coordinates, owner/layer switching, shared state, keyboard, playback and unavailable corpus. Index page and all 68 exact source-store checks passed. All 37 JavaScript modules and all 14 page assignments passed; all engine hashes match.

Visual mobile inspection then found small axis labels. At narrow widths, chart labels now use larger text and omit unnecessary decimal places on integer ticks; selected readings retain tenths. The wide table is explicitly keyboard-focusable with a visible focus outline. The final support check includes this label size, horizontal keyboard scrolling, stopping playback during owner switching and clearing links on failure. Its final result and the remaining collection/UI regression will be recorded below.

## Final local validation

The final expanded support browser check passed after the mobile amendments. It verified all 36 original monthly rows and native/WASM parity, separate source periods/layers and band allowances, original polygon coordinates, both owner round trips, shared state, playback completion, stopping on an owner change, keyboard month controls, 22-pixel SVG label fonts at 320 pixels, keyboard horizontal table scrolling, all six controls at least 44 pixels tall, and clearing chart/table/links on source failure. The Pacific mobile chart was visually inspected. Its band boundary now has a non-scaling outline with a calculated 4.20:1 sRGB contrast against the plot background; source coordinates and band semantics are unchanged.

The existing index page, all 68 exact source-store records, all 38 imported query collections (including first/last pages, inspection and 240 object marks), and the source-query UI passed with the rebuilt engine. All 37 JavaScript modules, 14 page assignments, manifest hashes and whitespace checks pass. The complete offline suite passed 773 tests and 598 subtests against the final Rust engine before the subsequent presentation-only mobile amendments; those amendments were checked through syntax and the final browser check. All 38 Rust tests and native/WASM builds passed. Original source, source catalog/corpus, query bundle and frozen export bytes are unchanged. Protected-main publication and scientific peer review remain unproven.
