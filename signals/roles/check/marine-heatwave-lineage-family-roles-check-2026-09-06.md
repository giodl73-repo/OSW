---
skill: roles-check
topic: marine heatwave lineage family
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D7 lineage family

## Artifact

OSW-D7's exact-overlap family-graph JSON, OER011, generators, tests,
documentation, and lineage-tree SVG. Reviewed as the current uncommitted
working-tree snapshot. Final offline gate: python -m pytest analysis -q →
**436 passed, 10 subtests passed**. The SVG was rendered in Edge at 1200 × 800
and visually inspected.

## Role selection

All eight OSW roles apply because the artifact changes scientific object
representation, uses observation-derived components, and introduces a public
graph grammar that may later transfer to planetary imagery.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Family” and “genealogy” can imply material descent. | P2 | Public claim | **Resolved:** qualify nodes as threshold-state footprints and deny parcel genealogy. |
| 2 | Split and merge topology does not identify a physical mechanism. | P3 | Boundary | Keep forcing and advection outside this receipt. |
| 3 | D3 remains a valid primary path, but not the complete reachable topology. | P3 | Interpretation | Preserve both statements together. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every family node needs an exact, stable identity. | P2 | Result schema | **Resolved:** store date-scoped component hashes and native-grid summaries. |
| 2 | The graph must reproduce every D3 primary component. | P2 | Cross-artifact contract | **Resolved:** fail generation unless all 21 match cell for cell. |
| 3 | Source product, version, grid, dates, connectivity, and pruning remain declared. | P3 | Provenance | Retain the figure footer and method block. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Variable line width was an unexplained quantitative encoding. | P2 | Legend | **Resolved:** declare width as logarithmic in shared pixels. |
| 2 | Direction must be legible without arrowheads on every edge. | P3 | Time axis | Add and retain the explicit left-to-right time arrow. |
| 3 | Side-node pixel labels and primary-trunk styling distinguish hierarchy. | P3 | Graph | Preserve redundant shape, label, and color encodings. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Readers need to know why the graph is better than one selected path. | P2 | Summary cards | **Resolved:** state that it records what the useful trunk omits. |
| 2 | “Complete” must be scoped to the declared reachability rule and source window. | P2 | OER011 | **Resolved:** say complete exact-overlap family around the anchor, not complete natural event. |
| 3 | The five-terminal/two-merge-back summary makes the topology repeatable. | P3 | Public explanation | Retain exact counts. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Branch fate cannot depend on orange curves alone. | P2 | Accessible meaning | **Resolved:** label every side node and state fate counts in text and SVG description. |
| 2 | Primary and side nodes use shape outlines plus labels beyond color. | P3 | Graph encoding | Preserve the redundant distinction. |
| 3 | The SVG title and description summarize topology without requiring vision. | P3 | Alternative text | Keep node, edge, split, merge, and fate counts. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Stored summary counts could drift from actual graph degrees. | P2 | Contract test | **Resolved:** recompute split and merge degrees from edges offline. |
| 2 | A graph edge must move strictly forward in date and reference existing nodes. | P2 | Structural test | **Resolved:** validate node references and chronological direction. |
| 3 | Live NOAA refresh remains explicit and checksum-verified. | P3 | Acquisition | Keep the default suite offline. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | OER011 is a tracked representation, not a new taxonomy term. | P3 | Registry | Keep 110 objects separate from eleven receipts. |
| 2 | Eleven-receipt counts and D7 links must agree across entry points. | P2 | Documentation | **Resolved:** synchronize README, Guide 14, history, analysis docs, and receipt collection. |
| 3 | No remote release occurred. | P3 | Repository state | Keep the work local and uncommitted. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Cloud-feature family graphs face the same split/merge identity problem. | P3 | Transfer | Transfer the explicit graph grammar, not Earth's cell rules. |
| 2 | Planetary cadence and resolution can create or erase branches. | P3 | Falsification | Resample before comparing topology. |
| 3 | Image-feature genealogy is not atmospheric parcel genealogy. | P3 | Analogy boundary | Preserve the material-continuity denial. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 10 (all resolved) | P3 notes: 14  
Verdict: APPROVED  
Top finding: the exact-overlap evidence is a 28-node family with a useful 21-node trunk, not a single natural chain.  
Cross-role consensus: graph completeness must remain scoped to declared grid, cadence, connectivity, reachability, pruning, and source window.

## Amendments applied

1. Scoped “family” and “complete” to threshold-state reachability and retained
   the material and mechanism boundaries.
2. Defined line width, time direction, branch sizes, and branch fates directly
   in the visual and its accessible description.
3. Added structural edge/degree tests, OER011, and synchronized the
   eleven-receipt documentation.

Remaining non-blocking work: test graph pruning and explicitly typed temporal
gap edges, then investigate physical drivers without treating topology as
causal evidence.
