---
skill: roles-check
topic: rust-diagnostic-frame-import
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 4
p2_remaining: 0
p3_count: 17
verdict: APPROVED-WITH-CONDITIONS
---

# Diagnostic frame import review

Artifacts: bundle frame importer, Rust frame bindings, map/spatial provenance,
frame inspector, recorded-day playback and regional fit. CURRENT covers diagnostic
scope; SOUNDER source receipts; CHART geometry/display; BEACON wording; HARBOR
interaction; KEEL reproducibility; LOGBOOK status. Installed role definitions were
inspected during this work. ORBIT is inapplicable. Internal role lenses are not
independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Diagnostic trace distances could become ranked current lengths or widths. | P2 | Import | Keep research-only frame records, explicit diagnostic-distance label and null widths; published ranking remains unchanged. Addressed. |
| 2 | Selected daily samples do not establish monthly means or climatology. | P3 | Scope | Retain sampling notes, layer and limitations in frame records and inspector. |
| 3 | Integration datum and source grid datum are distinct. | P3 | Coordinates | State WGS84 integration while leaving source datum independently unresolved. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Frame geometry could drift from pinned source calculations. | P2 | Validation | Builder runs the existing validator, recomputing nominal/sensitivity traces and checking source/figure/algorithm hashes. Addressed. |
| 2 | Frame identity must survive map and spatial output. | P3 | Receipts | Retain frame/series IDs, source URL and subset/timeline hashes. |
| 3 | Processing versions must not be collapsed into one homogeneous source. | P3 | Source | Preserve each frame's RADS algorithm and experimental status. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Global map scale hides individual diagnostic paths. | P2 | Fit | Gulf preset fits selected geometry; zoom switches to existing OSW closeup coast to avoid oversized borders. Screenshot reviewed. Addressed. |
| 2 | A frozen streamline is not a current axis or parcel path. | P3 | Symbols | Retain diagnostic role, orange dated styling and method notes. |
| 3 | Different observations can overlay on one day. | P3 | Variants | Retain distinct frame IDs and original canonical variants; do not silently deduplicate differing geometry. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | One second per frame is not elapsed-time animation. | P3 | Playback | State observation sequence and unequal gaps beside controls. |
| 2 | A filtered object may lack evidence on a globally listed day. | P3 | Dates | Keep empty scenes; document global catalogue and no nearest-date substitution. |
| 3 | Stopped traces must remain visible. | P3 | Inspector | Preserve stop reason and gate flag; all five nominal failures retained. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Animation needs explicit play/pause. | P3 | Controls | Native button, aria-pressed state, no autoplay; pause test passes. |
| 2 | Background playback could continue unseen. | P3 | Visibility | Stop on hidden page, manual query, error or sequence end. |
| 3 | Frame controls/inspector can overflow small screens. | P3 | Reflow | Verify 320 px; source-frame groups are collapsible. Human usability review remains open. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A frame reference could point to another object or mismatched geometry/date. | P2 | Rust load | Validate FK ownership and matching date, coordinates and role; unit test rejects changed date. Addressed. |
| 2 | Runtime source-frame selection could diverge between native/WASM. | P3 | Parity | Compare actual frame queries and all-day source/index temporal oracle results. |
| 3 | New frame geometries change computed state contacts. | P3 | Topology | Recheck actual-state results against original SVG/Shapely oracle; 20 modes/states pass. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Updated bundle identity requires explicit proposal migration. | P3 | Workspace | Document new hash and retain existing rebase workflow; no implicit carryover. |
| 2 | Earlier three-day coverage statement became stale. | P3 | Documentation | Update to 25 dated features/19 days; source import includes 17 frames. |
| 3 | This import does not finish all-current seasonal coverage. | P3 | Remaining work | Keep seasonal geography, additional currents/eddies, admission and full release open. |

## Synthesis and three amendments

Seven roles, 21 findings: zero P1, four addressed P2 and seventeen P3. Approved
with conditions for research-only dated diagnostic import/playback. Top finding:
checked traces must remain diagnostics rather than whole-current dimensions.
CURRENT/CHART agree on geometry meaning; SOUNDER/KEEL agree on binding receipts.

1. Validate original source traces and preserve all stops, uncertainty and scope.
2. Bind frame records to map features and expose provenance through queries and
   inspector links without modifying source-ranked measurements.
3. Add explicit observation playback/pause and regional fit, retain sparse gaps,
   and use the existing closeup coast for readable regional display.

## Evidence and conditions

Seventeen Rust tests pass. Actual frame checks verify all 17 original payloads,
five retained stopped traces, null widths, receipts, native/WASM equality, map
identity, inspector links, play/pause, regional fit and 320 px reflow. Temporal
source-date/index checks cover the expanded catalogue, and 20 original-state oracle
queries pass. Full query regression passes. Regional screenshot viewed.
Canonical ledger SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

More verified frames, full-current seasonal dimensions, independent science,
human accessibility and public release remain open. Existing model-field subsets
and seasonal editorial routes are not admitted as occupied current footprints.
