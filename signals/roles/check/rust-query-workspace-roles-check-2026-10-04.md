---
skill: roles-check
topic: rust-query-workspace
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 5
p2_remaining: 0
p3_count: 16
verdict: APPROVED-WITH-CONDITIONS
---

# Rust query workspace and map review

Artifacts: Rust native/WASM store and display geometry, versioned bundle builder,
worker, query UI, OSW map, integration test and storage contract. Selected CURRENT
for measurement and state scope, SOUNDER for custody, CHART for geography, BEACON
for language/navigation, HARBOR for access, KEEL for reproducibility and LOGBOOK
for repository status. Definitions were read; ORBIT is inapplicable. This is an
internal review using role lenses, not independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Mixed regional width records cannot supply a uniform whole-current width ranking. | P3 | Query/value | Retain source scope, phase, layer, boundary rule and ranking eligibility in record inspection. |
| 2 | State membership is recorded evidence, including shared gateways; it is not an intersection calculation. | P3 | State filter | Preserve relation kind and warn beside controls. Spatial intersection remains future work. |
| 3 | Display projection must not create numeric length or width estimates. | P3 | Rust map | Equirectangular display coordinates are isolated from source measurements. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Snapshot changes could silently mismatch the compiled browser engine. | P2 | Custody | Pin source inputs plus bundle/engine SHA256; reject changed bundle before loading. Browser failure test passes. Addressed. |
| 2 | Canonical and working evidence have different admission status. | P3 | Manifest | Declare canonical and editorial collections, preserve original IDs/fields and canonical checksum. |
| 3 | Two diagnostic width capabilities increase current evidence coverage beyond the 24 names with scalar width records. | P3 | Counts | Expose 26 currents with width evidence separately from 37 scalar records across 24 names; do not collapse these counts. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Paginating the table could hide half the currents on the map. | P2 | Map scene | Rust projects all matches before pagination; tests cover 100 currents and all 240 objects. Addressed. |
| 2 | Closing polygons across the longitude seam would invent a transglobal footprint. | P2 | Path generation | Split line paths; omit unsupported seam polygons with explicit reason, retaining raw geometry. Unit check passes. Addressed. |
| 3 | Many named eddies share the same gateway coordinates. | P3 | Encoding | Hollow dashed gateway marks, hover evidence labels and equivalent result list; avoid invented positions or footprints. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Calling an indexed imported snapshot a completed storage migration would overstate the result. | P3 | Architecture | Describe read-only persisted bundle and Rust indexes; revisioned writes remain the next layer. |
| 2 | Inherited broad object IDs could send state or NASA records to an unsupported current card. | P2 | Record navigation | Restrict card links to motion IDs/classes; keep other records inspectable as JSON and evidence. Addressed. |
| 3 | Integrity hashes are not signatures or independent scientific validation. | P3 | Contract | Use explicit mismatch wording, document authenticity and admission limits. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Native fieldset minimum size caused 320 px horizontal overflow. | P2 | Reflow | Set min-inline-size:0 and label min-width:0; narrow-screen test and screenshot pass. Addressed. |
| 2 | Hover alone would make names inaccessible by keyboard. | P3 | Map | Focusable SVG buttons announce names and accept Enter/Space; result table supplies equivalent records. |
| 3 | Color alone cannot distinguish geometry evidence. | P3 | Legend | Use circles, dashed gateways, line styles, polygons and role labels; human assistive-technology review remains pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Native and browser engines could drift in sorting, null handling or joins. | P3 | Verification | Same Rust functions plus actual-bundle parity across eight queries; six Rust tests cover validation and geometry. |
| 2 | Snapshot generation or rebuild order could be nondeterministic. | P3 | Build | Pinned Cargo.lock, offline locked builds, source manifest and deterministic bundle comparison; rebuild manifest after bundle. |
| 3 | Full 21 MB import and scan-based text queries will grow costly. | P3 | Performance | Worker keeps rendering independent; plan collection shards, caching and search/spatial indexes before scale claims. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Local apportionment map inspection is not a shared library integration. | P3 | Reuse | Record inspected projection/renderer/dependencies; OSW local projection implemented, shared crate and PNG export pending. |
| 2 | Local browser validation is not a clean-checkout/public release gate. | P3 | Status | Report focused checks only; no publication or canonical scientific admission. |
| 3 | Build commands depend on an installed WASM target and browser executable. | P3 | Maintainer notes | Document target, OSW_TEST_BROWSER, local preview port, native CLI and manifest rebuild sequence. |

## Synthesis

Seven roles, 21 findings: zero P1, five addressed P2 and sixteen P3. Approved with
conditions for local read-only query and map use. Top finding: pagination must not
silently hide matching map records. CHART and HARBOR agree on complete textual
access; CURRENT and SOUNDER agree that an indexed evidence join does not promote
an editorial locator/gateway to measured containment.

## Three amendments

1. Generate the complete matching map scene in Rust before applying table pagination;
   retain original evidence classes and report unsupported geometry explicitly.
2. Pin input/bundle/module checksums, share one Rust implementation and verify actual
   native/WASM parity and a rejected integrity load.
3. Repair narrow-screen fieldset sizing and restrict atlas links to supported motion
   records; retain the full record and equivalent keyboard/table access.

## Evidence and remaining conditions

Six Rust tests pass; actual-bundle browser/native parity, all 100 current marks,
all 240 motion marks, scoped Kuroshio joins, sharing/download, invalid query,
pagination, mobile overflow and corrupted-bundle load checks pass. Deterministic
bundle comparison and JS syntax pass. Desktop map/mobile screenshots were viewed.
Canonical almanac SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

Revisioned write transactions, graph traversal, spatial intersection/containment,
global polygon clipping, shared map crate, PNG export and collection caching remain
implementation work. Independent science, human accessibility, full clean-checkout
validation and public release are separate gates.
