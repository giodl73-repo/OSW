---
skill: roles-check
topic: ocean-column-address
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Ocean Column Address edition 1

**Artifact type:** scientific vocabulary, reference-geography contract, and
public field guide

**Source commit:** `c921664e43f3c3107993829f7916435acdcb00e2`

**Reviewed artifact SHA-256:**

- guide: `BF0651B607AF697A8CCDFA55F787B2FA699F06E7B6771A6DC2CFD4B73349F4EA`
- contract: `A7D43722F5BA3F9B2AD3F7D4CBD0150FA31FC7E85976B7695AFDD5B222E24118`
- object registry: `9449163F49149AB5BE2A6CCDDA037F37F89605AADAD01E37082ED824F341CBF2`
- relation registry: `143EAD91C7CAB8C49378D624A176E7971BEF7B7E6E7625023BDAEE6409C98997`

All eight native roles review this addition because it defines physical limits,
data-coordinate requirements, future cartographic behavior, reader language,
testable contracts, repository state, and a planetary non-transfer boundary.

## Findings

### CURRENT

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Fixed depth bands could be mistaken for mixed-layer, thermocline, or water-mass boundaries. | P2 | Make the address/regime distinction central and keep physical overlays non-exclusive. **Resolved.** |
| 2 | A bottom boundary layer is not synonymous with the deepest pelagic band. | P2 | Define it by seabed-influenced flow and mixing and cite a boundary-layer review. **Resolved.** |
| 3 | Half-open, bathymetry-truncated bands provide an exhaustive reference without asserting physical walls. | P3 | Preserve this contract in later voxel and section views. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | “Depth” is ambiguous without vertical reference, direction, and units. | P2 | Require dataset vertical reference, positive direction, units, and cell bounds. **Resolved.** |
| 2 | Pressure, model levels, and metres cannot be silently treated as interchangeable. | P2 | Require declared conversion and prohibit numeric relabeling. **Resolved.** |
| 3 | The contract preserves invalid and missing cells outside classified wet volume. | P3 | Carry source masks and partial-cell rules into any implementation receipt. **Accepted.** |

### CHART

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | A flat surface map alone cannot show a three-dimensional address honestly. | P2 | Make a section or voxel inspector the first visualization target. **Resolved in roadmap language.** |
| 2 | Horizontal extrusion can visually imply full-depth ecological validity. | P2 | Label it as an indexing operation and place the ecological non-claim beside it. **Resolved.** |
| 3 | Stable reference bands can support comparable overlays without forcing the overlays into one legend. | P3 | Keep reference and diagnosed styles visibly distinct in implementation. **Accepted.** |

### BEACON

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | “Wet voxel” is necessary but unfamiliar public language. | P2 | Define it immediately as a three-dimensional ocean data cell. **Resolved.** |
| 2 | “Complete covering” could be repeated as a complete physical classification. | P2 | State repeatedly that completeness is cartographic and rule-bound. **Resolved.** |
| 3 | The address analogy gives readers a compact answer to horizontal × vertical location. | P3 | Keep the example tuple and common-mistakes table. **Accepted.** |

### HARBOR

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | A future 3-D interaction cannot be the only way to recover the address. | P2 | Require an equivalent textual tuple and selected-cell details. **Deferred implementation condition.** |
| 2 | Depth categories must not depend on color alone. | P2 | Use names, exact numeric intervals, and ordered position as redundant encodings. **Resolved in the definition.** |
| 3 | Tables and prose provide the full meaning of the explanatory ASCII diagrams. | P3 | Preserve the guide as the nonvisual reference. **Accepted.** |

### KEEL

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Prose bounds can drift or acquire gaps when edited. | P2 | Add a machine-readable edition contract and test contiguity and endpoints. **Resolved.** |
| 2 | Registry totals, guide discovery, and generated matrix can drift together. | P2 | Update focused tests and regenerate the matrix deterministically. **Resolved.** |
| 3 | The address object and five band objects use existing controlled enum values. | P3 | Keep registry validation in the offline default suite. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Adding six objects makes all published editorial totals stale. | P2 | Update classification, guide index, README, generated matrix, summary, tests, and history together. **Resolved.** |
| 2 | A new definition could be mistaken for a finished data layer. | P2 | Record it as edition-1 reference vocabulary and identify the section/voxel viewer as next work. **Resolved.** |
| 3 | The history records why coverage is useful and where the claim stops. | P3 | Commit definition and review together without remote publication. **Accepted.** |

### ORBIT

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Earth sunlight zones and metre cutoffs do not transfer directly to gas giants. | P2 | Add an explicit planetary non-transfer section. **Resolved.** |
| 2 | Solid-seafloor truncation fails for an atmosphere without the same lower boundary. | P2 | Require a new vertical coordinate and lower-boundary model for comparison. **Resolved.** |
| 3 | Stratification, jets, mixing, and tracer-layer questions may still be compared at mechanism level. | P3 | Keep any later analogy conditional and separately tested. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: an exhaustive address is a reference-coordinate achievement,
not evidence that the ocean's physical regimes form one exhaustive partition.

Cross-role consensus: freeze exact intervals and masks in a tested contract,
keep diagnosed overlays independent, and make the first view a section/voxel
inspector with equivalent text rather than another surface-only map.
```

Fifteen P2 findings are resolved in this definition stage. The remaining HARBOR
condition belongs to the future interactive implementation: it must expose the
selected address and overlay evidence without requiring color, pointer input,
or spatial vision.

## Amendments

1. Added a machine-readable five-band contract with interval, datum, mask, and
   bathymetry rules plus an offline semantic test.
2. Defined wet voxel, prohibited pressure-to-metre relabeling, and made the
   horizontal extrusion's ecological non-claim explicit.
3. Added bottom-boundary and planetary transfer limits and selected a section /
   voxel inspector as the next visualization target.

Fixed-point decision: approve Ocean Column Address edition 1 as reference
vocabulary. No observed 3-D field, water-mass classification, transport claim,
atlas promotion, deployment, or remote publication is authorized by this review.
