---
skill: roles-check
topic: guide 12 life oxygen nutrients and carbon
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — Guide 12

## Artifact

Public-science guide plus 106-object, 13-type classification and 101-edge
relation graph. Source commit: `556edacd5c5b9ca0b1829e804ae05384635a730b`;
reviewed artifact is the current uncommitted working-tree snapshot. Full gate:
`python -m pytest analysis -q` → 389 passed, 10 subtests passed.

All eight OSW roles apply: physical coupling (CURRENT), variable identity
(SOUNDER), map semantics (CHART), public explanation (BEACON), text equivalence
(HARBOR), contracts (KEEL), repository truth (LOGBOOK), and planetary transfer
(ORBIT).

## Review findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Concentration, body, event, pool, and flux are physically and dimensionally separated. | P3 | Opening grammar | Preserve this chain in map modes. |
| 2 | OMZ was initially typed as a material body although persistence does not imply parcel coherence. | P2 | OBJ097 | **Resolved:** retyped as `layer_interface`. |
| 3 | Physical transport and biological transformation are connected without making upwelling sufficient for blooms. | P3 | Carbon pump / relations | Retain the stated light, loss, and transport conditions. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Hypoxia was initially assigned an anomaly test despite common absolute oxygen thresholds. | P2 | OBJ051/098 | **Resolved:** added `absolute_threshold`. |
| 2 | Carbon parameters, measured versus calculated status, pH scale, constants, and uncertainty are required. | P3 | Carbon system | Enforce these in data receipts. |
| 3 | Nutrient pool could hide incompatible species. | P2 | Decisive tests | **Resolved:** added explicit species-and-unit requirement. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Evidence classes provide a sound legend grammar for future maps. | P3 | Field/body/event/pool/flux | Encode class redundantly, not by colour alone. |
| 2 | Depth is essential for OMZs and deep chlorophyll maxima. | P3 | Oxygen / chlorophyll | Never publish these as depthless surface footprints. |
| 3 | Province boundaries are correctly denied biological impermeability. | P3 | OSW consequences | Overlay rather than clip dynamic fields. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “A coloured concentration map is not automatically a body, event, pool, or flux” is supported and repeatable. | P3 | Opening | Use as the public summary. |
| 2 | Proxy and harm caveats sit beside chlorophyll and bloom explanations. | P3 | Chlorophyll | Preserve adjacency in visual versions. |
| 3 | Technical carbon distinctions remain readable through one diagram and plain definitions. | P3 | Carbon system | Keep formulas subordinate to meanings. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every diagram has an equivalent prose explanation. | P3 | All diagrams | Preserve canonical text with future SVGs. |
| 2 | No conclusion depends on colour or pointer interaction. | P3 | Whole guide | Maintain redundant labels in maps. |
| 3 | Units and object classes are written explicitly. | P3 | Cards / tests | Provide structured data alternatives later. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | New identity tests and Guide 12 links are schema checked. | P3 | Tests | Add per-edge evidence keys next. |
| 2 | Counts, names, IDs, endpoints, and source IDs are executable contracts. | P3 | Registries | Keep network refresh outside offline tests. |
| 3 | Full suite passes 389 tests and 10 subtests. | P3 | Validation | Preserve as merge gate. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, history, classification, index, sources, and tests agree on counts. | P3 | Companion files | Update together on growth. |
| 2 | History states integration rather than scientific priority. | P3 | History | Preserve this boundary publicly. |
| 3 | Review names an uncommitted snapshot and does not claim release. | P3 | Artifact | Commit/push only when authorized. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Chemical disequilibrium is not equated with life. | P3 | Planetary connection | Preserve evidence ladder. |
| 2 | Atmospheric tracer colour is not called a community. | P3 | Planetary connection | Match observation methods before analogy. |
| 3 | No Earth biological pump is projected automatically onto gas giants. | P3 | Planetary connection | Require direct biological evidence. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0 | P2 issues: 3 (all resolved) | P3 notes: 21
Verdict: APPROVED
Top finding: map evidence class before mapping the phenomenon.
Cross-role consensus: proxy, depth, units, threshold, integration geometry,
and boundary orientation determine what a biological or chemical colour means.
```

## Amendments applied

1. Retyped OMZ as persistent vertical layer rather than coherent material body.
2. Added absolute-threshold identity for hypoxic and anoxic events.
3. Required named nutrient species and units for any nutrient pool.

Remaining non-blocking work: exact vocabulary IDs, per-edge citations, and a
visual matrix/decision-path synthesis for the full registry.

