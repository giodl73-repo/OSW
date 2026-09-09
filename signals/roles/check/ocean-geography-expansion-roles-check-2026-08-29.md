---
skill: roles-check
topic: ocean-geography-expansion
date: 2026-08-29
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK, ORBIT]
p1_count: 0
verdict: APPROVED
---

# Ocean-geography expansion — native-role implementation review

Source commit: `aa91cb8` (`Expand atlas into ocean geography`)
Plan review: `signals/roles/check/ocean-geography-expansion-plan-roles-check-2026-08-29.md`

## Artifact identification

- Type: interactive atlas implementation, catalog, export, and documentation
- Domain signals: physical oceanography, hydrography, cartography, bathymetry,
  biogeochemistry, public-science UI, accessibility, provenance
- Roles: all eight OCEANLINES roles

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Volume, flow, edge, floor, biogeochemical province, and event are no longer conflated as heat blobs. | P3 | six lenses | Preserve the primary-lens distinction. |
| 2 | Every new feature states an identifying or maintaining basis and a depth class. | P3 | catalog | Add formation detail only with feature-specific review. |
| 3 | Fronts, gyres, water masses, and OMZs explicitly reject fixed, uniform, or impermeable interpretation. | P3 | boundaries | Keep these caveats adjacent. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | All 24 new records carry OG source IDs, URLs, basis, evidence, and inferential boundary. | P3 | catalog / source register | Tighten OG08 and OG17–20 with feature-specific datasets before polygons. |
| 2 | The CSV is deterministically regenerated from the application catalog and contains the new schema fields. | P3 | exporter | Preserve ordered parity. |
| 3 | No new mark is represented as an observed threshold or footprint. | P3 | scientific firewall | Require source receipts before diagnosed geometry. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Seven basin labels provide quiet base geography for water formerly left visually unnamed. | P3 | conceptual map | Keep them subordinate to feature selection. |
| 2 | WATERS is the uncluttered default; ALL FEATURES remains an optional stress view with offsets and a text route. | P3 | controls | Do not make all markers the default. |
| 3 | Six marker classes use shape, border, label, and color; the legend exposes the grammar. | P3 | marker legend | Preserve redundant encoding. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The hero explains overlapping geographies instead of presenting a bag of new names. | P3 | hero | Keep this as the public takeaway. |
| 2 | `ALL FEATURES` and “36 curated records” avoid claiming exhaustive ocean coverage. | P3 | scope | Retain curated language. |
| 3 | Original HEATMASS, OCEANREALMS, and OCEANBELTS studies remain linked without governing the new taxonomy. | P3 | legacy links | Preserve the history. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Lens buttons and labeled selects are keyboard-native and filter state is announced live. | P3 | controls | Add browser-driven keyboard regression later. |
| 2 | Unmatched markers are hidden and removed from tab order; matching records remain in the text directory. | P3 | filter behavior | Preserve semantic hiding. |
| 3 | Narrow inspection retains all lenses, filters, caveats, and the legacy route. | P3 | responsive layout | Add a 400% zoom capture harness later. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The offline suite passes 67 tests and locks 36 unique ordered records. | P3 | tests | Keep exact cardinality until a reviewed expansion. |
| 2 | Tests require combined filter machinery, bookmark parameters, keyboard hiding, source/boundary fields, and CSV parity. | P3 | tests | Add direct DOM interaction tests when a browser harness exists. |
| 3 | JavaScript syntax, Python compilation, deterministic export, and diff checks pass. | P3 | validation | Keep the same local gate in CI. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Plan approval `412af37` precedes implementation `aa91cb8`, preserving decision traceability. | P3 | Git history | Record this final verdict in preview status. |
| 2 | README, atlas method, research page, source register, application, tests, and CSV agree on 36 records. | P3 | repository state | Update them together on future expansion. |
| 3 | Work remains local on the private-preview branch and no public release claim was changed. | P3 | release state | Run publication governance separately. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new taxonomy is explicitly Earth-ocean geography, not a gas-giant band analogy. | P3 | scope | Preserve the separation. |
| 2 | OCEANBELTS remains a legacy study link rather than a primary Earth feature class. | P3 | legacy route | Require ORBIT review before transfer. |
| 3 | Separating volumes, flows, and edges improves any later mechanism-based planetary comparison. | P3 | architecture | Compare dynamics, not visual shapes. |

## Synthesis

Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 24

Verdict: APPROVED

Top finding: the atlas now names much more of the ocean without pretending that
overlapping, three-dimensional, moving features form exclusive surface countries.

Cross-role consensus: the six-lens model is an honest improvement because the
catalog carries depth, basis, property, clock, evidence, source, and limitation,
while the map restricts new records to clearly labeled index points.

## Amend

1. Replace grouped/general source support with feature-specific observational
   products before drawing water-mass or seafloor polygons.
2. Add direct browser tests for combined filters, keyboard selection, URL restore,
   narrow layout, and 400% zoom when a stable harness is introduced.
3. Expand beyond 36 only through another curated source-and-role review; do not
   let catalog growth imply exhaustiveness.

