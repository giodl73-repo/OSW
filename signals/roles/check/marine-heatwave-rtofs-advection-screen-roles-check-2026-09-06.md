---
skill: roles-check
topic: marine-heatwave-rtofs-advection-screen
date: 2026-09-06
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D11 RTOFS horizontal-advection screen

**Artifact type:** operational-model source extraction, partial physical
diagnostic, static scientific map, evidence receipt, and documentation update  
**Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b` plus the reviewed working-tree changes  
**Reviewed artifacts:** `atlas/data/rtofs-mhw-bridge-north-atlantic-20260807-20260812.json`,
`research/osw-d11-rtofs-mhw-horizontal-advection-2026.json`, and
`figures/osw-d11-rtofs-mhw-horizontal-advection-2026.svg`

## Role selection

| Role | Why selected |
|---|---|
| CURRENT | D11 estimates one physical tendency term and leaves a large residual. |
| SOUNDER | Operational nowcasts are range-read, transformed, and identified by remote metadata. |
| CHART | Three signed curvilinear fields and a five-interval comparison carry the result. |
| BEACON | “Not the main term” must not become atmospheric attribution. |
| HARBOR | Sign and term identity require redundant encodings beyond the diverging palette. |
| KEEL | Remote refresh dependencies and extracted-value integrity require separate gates. |
| LOGBOOK | Source register, receipt vocabulary, history, guide, and commands must agree. |

ORBIT was not selected because this artifact makes no planetary comparison.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Surface `-u∇T` is not a mixed-layer or model-native tracer tendency. | P2 | Method/boundary | Label it an offline Eulerian screen and enumerate omitted vertical, mixing, diffusive, assimilative, and numerical terms. **Resolved.** |
| 2 | Calling the residual atmospheric forcing would be physically unsupported. | P2 | Finding/next evidence | Keep it “unresolved remainder” until flux and vertical terms are measured. **Resolved.** |
| 3 | Mixed-layer shoaling is relevant context but not an entrainment term or cause. | P3 | Callout | State that interpretation directly beside the 19.5→7.8 m change. **Resolved.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | RTOFS is operational assimilative model output, not retrospective reanalysis. | P2 | Evidence origin | Add `operational_assimilative_model` to the governed vocabulary and use it for OER015. **Resolved.** |
| 2 | HTTP range reads do not retain complete source-file bytes locally. | P2 | Provenance | Preserve URL, content length, ETag, last-modified time, extraction scale, and extracted-row SHA-256; state checksum scope. **Resolved.** |
| 3 | N024, valid time, depth, units, grid, and interval must remain explicit. | P3 | Source JSON | Store 00 UTC daily support, surface depth, field IDs, scaling, and source filename class. **Resolved.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Signed tendencies require a meaningful zero-centered common scale. | P2 | Three maps | Use the same ±2°C/day diverging scale and a white zero contour. **Resolved.** |
| 2 | The first colorbar layout collided with panel C's heading. | P2 | Figure hierarchy | Move the bar upward and place its explanatory label above it. **Resolved.** |
| 3 | Curvilinear source coordinates do not name the rendered map projection. | P3 | Figure footer | Add “Plate Carrée display” and retain source-grid class separately. **Resolved.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Advection supplies 13%” sounds like causal budget closure. | P2 | Deck/guide/history | Say the signed diagnostic term “is 13% of” the modeled tendency. **Resolved.** |
| 2 | “Not the main term” could be repeated as “the atmosphere caused it.” | P2 | Figure/footer | Put unresolved processes in the primary visual and refuse to rename the remainder. **Resolved.** |
| 3 | Anchor and box conclusions differ and both are important. | P3 | Callout/deck | Report box +0.071°C/day and anchor −0.109°C/day together. **Resolved.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Cooling/warming cannot depend on blue/orange perception. | P2 | Figure | Add zero contours, signed numeric callout, bar positions around zero, and textual sign labels. **Resolved.** |
| 2 | The three panels need explicit term names and ordering. | P2 | Map titles | Prefix panels A/B/C and spell out modeled tendency, advection, and remainder. **Resolved.** |
| 3 | SVG caveats are small at display size. | P3 | Alternative path | Preserve live SVG text and pair it with machine-readable JSON, guide prose, and receipt. **Resolved.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Live S3 reads and optional HDF5 dependencies cannot be default offline gates. | P2 | Acquisition | Keep refresh explicit and pin optional packages in `requirements-observations.txt`. **Resolved.** |
| 2 | The compact cube needs tamper and dimensional checks. | P2 | Tests | Recompute canonical-row SHA-256 and assert 6×67×63 support with 4,221 valid cells and twelve ETags. **Resolved.** |
| 3 | Gradient choice could manufacture a box result. | P3 | Sensitivity | Retain four- versus eight-neighbor means and lock bridge difference below 0.002°C/day. **Resolved.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A new source class requires register and receipt-vocabulary alignment. | P2 | Source register/OER015 | Add D48 and `operational_assimilative_model`; regenerate fifteen receipts. **Resolved.** |
| 2 | Public documentation must preserve the unresolved-term boundary. | P2 | README/guide/history/signal | Record D11 numbers and omissions consistently. **Resolved.** |
| 3 | No commit, push, or publication was authorized in this continuation. | P3 | Repository state | Validate locally and report the dirty working-tree state without release claims. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 14  |  P3 notes: 7

Verdict: APPROVED

Top finding: RTOFS must be represented as operational assimilative model output,
and its offline advection residual must remain physically unresolved.

Cross-role consensus: CURRENT, SOUNDER, and BEACON reject both reanalysis
mislabeling and atmospheric attribution. CHART and HARBOR require sign to be
carried by contours, numbers, and position as well as color. KEEL and LOGBOOK
require explicit network refresh with deterministic offline evidence gates.
```

## Amendments completed

1. Added a precise operational-assimilative evidence origin and retained full
   source-object/extraction provenance.
2. Replaced causal-sounding “supplies” language, preserved the unresolved
   remainder, and labeled mixed-layer shoaling as context only.
3. Fixed the colorbar hierarchy, named the Plate Carrée display, added stencil
   sensitivity, and aligned tests, receipt, register, history, guide, and signal.

No external peer review is implied by this repository role check.
