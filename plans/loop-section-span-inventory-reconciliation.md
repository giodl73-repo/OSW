# Loop component-span inventory reconciliation

2026-10-08. Editorial inventory correction; no new scientific measurement.

## Gap addressed

The Loop width decision said `width_not_assessed` despite two pinned component-span diagnostics already stored and rendered in the Rust/WASM query engine. Both diagnose the zonal half-peak northward-velocity span at the Yucatan gate, not flow-normal current width.

## Classification rule

Use `section_span_diagnostic_present_width_unresolved` when pinned local component-span diagnostics exist but do not establish a comparable current width. Keep these receipts in `section_span_diagnostics`, separate from published measurements and derived width candidates. Count distinct current owners, not products or dates.

Loop retains null whole-current width and annual width range, and remains excluded from width ranking and annual extrema. Both products can share altimetry inputs. Scientific identity and boundary review remain open. This correction does not reduce the number of unknown whole-current dimensions.

## Presentation

The width-decision table and atlas card link directly to the existing `width_samples` query, filtered to Loop and sorted by observation date. The query preserves both products, five days per product, source context, threshold sensitivity, grid brackets and mapped local sections. No route buffering or annual animation is added.

## Verification

Inventory mutation checks reject numeric whole-current width, annual ranges, ranking, metric changes, stale source receipts and an inconsistent decision. The existing registered dashboard-navigation browser check follows the atlas link and verifies all ten unranked Loop rows and their map scene. Rebuild dashboard, query corpus, source index and Rust native/WASM manifests in dependency order.

## Remaining data work

Local validation completed: 836 Python tests and 918 subtests; 40 Rust tests; native and WASM builds; registered dashboard/navigation browser checks including exact native/WASM parity for the linked Loop query; JavaScript syntax and whitespace checks. All 90 published width records and all seasonal frame content are unchanged. A separate attempted live-source almanac check could not resolve its remote host in this sandbox; it is not reported as passed.

90 scoped published width records cover 46 current owners; 46 currents remain unassessed, two have derived width candidates, five have reviewed sources without comparable numeric widths, and Loop has component spans with width unresolved. Published length coverage and named eddy footprint coverage remain separate gaps. Additional dimensions need source evidence, layer, spatial support, boundary definition and sampling period under the existing protocols.
