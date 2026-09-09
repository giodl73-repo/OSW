---
skill: roles-check
topic: marine-heatwave-upper-ocean-storage-screen
date: 2026-09-06
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D13 fixed-column upper-ocean storage screen

**Artifact type:** operational-model profile extraction, fixed-depth storage
diagnostic, static scientific map, evidence receipt, and documentation update  
**Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b` plus reviewed working-tree changes  
**Reviewed artifacts:** `atlas/data/rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json`,
`research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json`, and
`figures/osw-d13-rtofs-mhw-upper-ocean-storage-2026.svg`

## Role selection

CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK were selected for
physical-budget meaning, modeled-profile provenance, signed cartography,
public claims, accessible redundancy, deterministic generation, and repository
alignment. ORBIT was not selected because D13 makes no planetary comparison.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Standard-depth potential-temperature integration is a storage proxy, not native-layer heat content. | P2 | Declare constant `ρCp`, interpolation, fixed bounds, and the native-layer limitation. **Resolved.** |
| 2 | Positive 0–50 m storage does not distinguish horizontal transport, vertical exchange, mixing, or assimilation. | P2 | Preserve those mechanisms as the next tests rather than naming the residual. **Resolved.** |
| 3 | Surface-minus-column warming diagnoses intensification, not mixed-layer shoaling itself. | P2 | Keep the distinction in the finding and boundary. **Resolved.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Depth support must be exact and comparable across dates. | P2 | Assert the same fifteen 0–50 m standard depths in all six files. **Resolved.** |
| 2 | The new cube reuses remote objects but needs its own extraction identity. | P2 | Preserve six URLs/ETags and a canonical-row SHA-256. **Resolved.** |
| 3 | RTOFS remains operational assimilative model output. | P2 | Use the governed origin and deny observed-storage status. **Resolved.** |

### CHART — ocean cartography

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Surface, column, and their difference need separate symmetric limits. | P2 | Use zero-centered diverging scales with each clipping limit printed. **Resolved.** |
| 2 | Field tails exceed display ranges. | P2 | Add extended colorbar ends rather than silently implying no extremes. **Resolved.** |
| 3 | Depth behavior is essential and cannot be inferred from maps. | P2 | Add all five daily vertical profiles and cumulative fixed-column bars. **Resolved.** |

### BEACON — public-science editing

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | “Surface flux explains 48%” sounds like closure. | P2 | Say it is 48% of a cross-system storage magnitude, not an accounted budget share. **Resolved.** |
| 2 | “Upper ocean gains heat” needs its exact depth. | P2 | Repeat fixed 0–50 m support in title, callout, guide, and receipt. **Resolved.** |
| 3 | The anchor extreme could be sensationalized. | P2 | Use it only to reject local surface-flux sufficiency and name transport/assimilation alternatives. **Resolved.** |

### HARBOR — accessibility

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Warming/cooling cannot rely on hue. | P2 | Add zero contours, signed axes, explicit words, and numeric summaries. **Resolved.** |
| 2 | Three maps alone do not expose depth ordering. | P2 | Add a labeled depth axis and ordered column-limit bars. **Resolved.** |
| 3 | Small caveats need a textual equivalent. | P3 | Pair SVG live text with guide prose and machine-readable JSON. **Resolved.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Fixed-column calculations require exact integration endpoints. | P2 | Test the complete depth vector and reported 10/20/30/50 m values. **Resolved.** |
| 2 | Network refresh must remain optional. | P2 | Keep the compact cube committed and all analysis/visual tests offline. **Resolved.** |
| 3 | Derived headline values could drift silently. | P2 | Lock source hash, storage values, anchor result, SVG tokens, and deterministic regeneration. **Resolved.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | The seventeenth receipt and fiftieth source row must agree. | P2 | Add OER017/D50 and regenerate the collection. **Resolved.** |
| 2 | The historical milestone is a change in scientific interpretation. | P2 | Record surface intensification plus column gain, including the open budget. **Resolved.** |
| 3 | No commit, push, or publication was authorized. | P3 | Retain local validated changes and make no release claim. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 19  |  P3 notes: 2

Verdict: APPROVED

Top finding: the bridge is neither an unchanged column with a hot skin nor a
surface-flux-closed warming event. It combines strong surface intensification
with genuine modeled fixed-column storage, leaving transport and analysis terms open.
```

No external peer review is implied by this repository role check.
