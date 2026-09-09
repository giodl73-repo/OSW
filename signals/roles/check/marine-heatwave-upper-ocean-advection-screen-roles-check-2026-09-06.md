---
skill: roles-check
topic: marine-heatwave-upper-ocean-advection-screen
date: 2026-09-06
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D14 depth-integrated horizontal-advection screen

**Artifact type:** operational-model mechanism diagnostic, cross-system partial
budget, static scientific map, evidence receipt, and documentation update  
**Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b` plus reviewed working-tree changes  
**Reviewed artifacts:** `research/osw-d14-rtofs-mhw-upper-ocean-advection-2026.json`
and `figures/osw-d14-rtofs-mhw-upper-ocean-advection-2026.svg`

## Role selection

CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK were selected.
ORBIT was not selected because D14 makes no planetary comparison.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Local `−u·∇T` is advective temperature tendency, not conservative native tracer convergence. | P2 | Name it an offline Eulerian diagnostic everywhere. **Resolved.** |
| 2 | The 13.1% surface ratio and 72.5% column ratio have different supports and denominators. | P2 | State that explicitly instead of narrating one fraction growing with depth. **Resolved.** |
| 3 | A −47.79 W/m² residual cannot identify vertical cooling or mixing. | P2 | Retain all vertical, assimilative, numerical, and cross-system alternatives. **Resolved.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Velocity and temperature must be collocated at all fifteen depths. | P2 | Store and test both velocity components beside temperature in the same cube. **Resolved.** |
| 2 | Four gradient-invalid edge cells reduce support from 4,221 to 4,217. | P2 | Report the valid count rather than silently carrying the source-grid count. **Resolved.** |
| 3 | GFS surface forcing remains a separate model lineage. | P2 | Preserve all three source hashes and `cross_system` in status and representation. **Resolved.** |

### CHART — ocean cartography

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Storage, advection, and residual require a common signed scale for comparison. | P2 | Use one zero-centered ±3000 W/m² display scale. **Resolved.** |
| 2 | Robust clipping hides real field tails. | P2 | Add extended colorbar ends and print the clipping limit. **Resolved.** |
| 3 | Depth emergence is not legible in three maps alone. | P2 | Add cumulative 10/20/30/50 m storage and advection curves. **Resolved.** |

### BEACON — public-science editing

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | “120% closure” would imply incompatible terms form a budget. | P2 | Say resolved scales total 120.2% and the magnitude is close, not closed. **Resolved.** |
| 2 | “Motion was hiding” is memorable but needs the diagnostic boundary immediately below. | P2 | Put both supports, denominators, and percentages in the deck. **Resolved.** |
| 3 | The anchor and box reach different conclusions. | P2 | Preserve the box near-balance and anchor 53.8% unresolved result together. **Resolved.** |

### HARBOR — accessibility

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Term sign cannot depend on blue/orange. | P2 | Add zero contours, signed callout values, zero axes, and warming/convergence words. **Resolved.** |
| 2 | Four bar series need direct legend identities. | P2 | Keep ordered legend labels and distinct positions around zero. **Resolved.** |
| 3 | Map detail needs a data-oriented alternative. | P3 | Pair SVG with JSON maps, interval tables, guide prose, and receipt. **Resolved.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Depthwise gradients multiply the D11 numerical surface area. | P2 | Reuse the tested tangent-plane kernel and assert cumulative depth results. **Resolved.** |
| 2 | Gradient stencil choice could manufacture the mean. | P2 | Retain the four-neighbor result; eight-minus-four is only 1.07 W/m² at 50 m. **Resolved.** |
| 3 | The partial-budget maps and claims must regenerate offline. | P2 | Lock headline, anchor, depth-ladder, SVG, and receipt values in tests. **Resolved.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | D14 requires OER018 and D51 alignment. | P2 | Regenerate eighteen receipts and update register, history, README, guide, and commands. **Resolved.** |
| 2 | The historical lesson changes the earlier D11 interpretation. | P2 | Record that surface-only motion was incomplete, not simply disproven. **Resolved.** |
| 3 | No commit, push, or publication was authorized. | P3 | Retain local validated changes without a release claim. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 19  |  P3 notes: 2

Verdict: APPROVED

Top finding: a small surface advection diagnostic and a large fixed-column
advection diagnostic legitimately coexist. The near-balanced box magnitudes
are scientifically promising but do not form a native or cross-model closure.
```

No external peer review is implied by this repository role check.
