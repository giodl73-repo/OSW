---
skill: roles-check
topic: first detected marine-heatwave event and connected footprint receipts
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D1 event and OSW-D2 footprint

## Artifact

OER005 and OER006; the `OSW-D1` point-event and `OSW-D2` connected-footprint
JSON; the 32-day checksum-pinned NOAA CRW source series; acquisition,
detection, connectivity, and render code; contract tests; and both SVG evidence
receipts. Reviewed as the current uncommitted working-tree snapshot. Final
gate: `python -m pytest analysis -q` → **413 passed, 10 subtests passed**.
Both SVGs were rendered in Edge at native size and visually inspected.

## Review findings

### CURRENT

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | A threshold category is a surface thermal state, not heat content or transport. | P3 | Both JSON and SVG state these non-claims adjacent to the result. |
| 2 | The linked 27-day event contains one category-zero gap. | P2 | **Resolved:** call it a linked event, expose the gap in the timeline and counts, and declare the ≤2-day rule. |
| 3 | A daily thermal footprint is not a material water mass. | P3 | OSW-D2 is explicitly an evolving classified state; motion, content, and parcel identity are denied. |

### SOUNDER

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | NOAA CRW is a derived observation product, not a raw observation and not OISST itself. | P2 | **Resolved:** added `derived_observation_product` to the governed origin vocabulary. |
| 2 | Reproducibility requires provenance below the compact extracted series. | P2 | **Resolved:** record URL, issue date, product version, source description, and raw SHA-256 for all 32 NetCDF files. |
| 3 | Point selection after seeing the answer would weaken the test. | P3 | The point was selected from OSW's separate OISST anomaly snapshot and then tested in CRW. |

### CHART

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | A single orange band could conceal duration logic. | P2 | **Resolved:** use one cell per day, show the zero-category gap, bracket the linked event, and leave the rejected August 20 spike outside it. |
| 2 | The visual could still be mistaken for a spatial map. | P3 | Title, subtitle, and claim box repeat “one pixel”; no footprint geometry is shown. |
| 3 | The footprint should preserve measured shape character rather than smooth it into a generic blob. | P3 | OSW-D2 renders native 0.05° row runs and its grid-edge boundary directly. |

### BEACON

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | “A marine heatwave earns its name” makes the evidence-ladder advance legible. | P3 | Retained as the public entry point. |
| 2 | The meaningful result is not simply “warm water,” but a passed identity rule. | P3 | Lead with duration, maximum category, and PASS; follow immediately with non-claims. |

### HARBOR

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | Meaning must survive without category colour. | P3 | Text supplies dates, duration, maximum category, pass result, gap semantics, and boundaries; SVG includes title and description. |
| 2 | The JSON is the canonical complete equivalent. | P3 | Every displayed fact and the full daily series remain machine-readable. |
| 3 | Footprint area and composition must remain available without inspecting the map. | P3 | Text and JSON report area, pixel count, centroid, bounds, categories, method, and boundary. |

### KEEL

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | An isolated exceedance after an event must not be silently absorbed. | P2 | **Resolved:** tests verify qualifying runs are retained before the gap join; August 20 remains outside the event. |
| 2 | Leap-day, percentile, duration, gap, mask, checksum, and deterministic-build behavior are tested. | P3 | Preserved in focused and repository-wide gates. |
| 3 | NOAA PSL DAP did not complete the independent raw-SST baseline acquisition. | P3 | No incomplete series was admitted; the fetcher checkpoints honestly and the independent detector remains tested but unclaimed. |
| 4 | Geographic seam behavior must be intentional even when this component is far from it. | P3 | Longitude is periodic and tested; latitude is bounded; four-neighbor connectivity is explicit. |

### LOGBOOK

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | Guide 14 and README still described four receipts. | P2 | **Resolved:** updated them to five and added the new source-register and history entries. |
| 2 | This is a scientific milestone, not a registry-count change. | P3 | History records the first detected-object rung without changing the 110-object taxonomy. |
| 3 | A daily footprint must not be logged as a tracked full-event shape. | P2 | **Resolved:** OER006's next-evidence field requires overlap, split, merge, persistence, and minimum-area policy. |

### ORBIT

| # | Finding | Severity | Resolution |
|---|---|---|---|
| 1 | The duration grammar can transfer, but Earth's SST threshold and NOAA categories cannot. | P3 | Planetary transfer remains method-shaped only; an atmospheric observable needs its own threshold, support, and identity test. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0 | P2 issues: 8 (all resolved) | P3 notes: 17
Verdict: APPROVED
Top finding: OSW-D1 earns the event at a point; OSW-D2 earns one exact daily footprint.
Cross-role consensus: neither receipt yet earns a single shape tracked through the event's full lifetime.
```

## Amendments applied

1. Added a distinct derived-observation-product provenance class.
2. Pinned all 32 daily upstream NetCDF files by URL and raw SHA-256.
3. Encoded and tested the five-day, two-day-gap, mask, and run-order contract.
4. Exposed the linked gap and rejected isolated spike in the SVG.
5. Added OER005 to the guide, builder, README, source register, and project history.
6. Added the exact native-grid OSW-D2 footprint, area integration, seam test,
   visual plate, OER006, and spatiotemporal-tracking literature boundary.

Remaining non-blocking work: track daily components through overlap, splits,
merges, disappearances, and reappearances before assigning one footprint
identity across the complete event.
