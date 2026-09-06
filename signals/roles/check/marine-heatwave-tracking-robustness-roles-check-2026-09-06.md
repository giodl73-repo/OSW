---
skill: roles-check
topic: marine heatwave tracking robustness
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D5 tracking robustness

## Artifact

OSW-D5's connectivity-by-overlap sensitivity JSON, OER009, analysis and view
generators, contract tests, documentation, and policy-matrix SVG. Reviewed as
the current uncommitted working-tree snapshot. Final offline gate:
`python -m pytest analysis -q` → **428 passed, 10 subtests passed**. The SVG was
rendered in Edge at 1200 × 800 and visually inspected.

## Role selection

All eight project roles apply because D5 joins an observationally derived
scientific claim, a public explanatory graphic, generated evidence artifacts,
and a planetary-transfer boundary.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Equal lifetimes do not imply equal daily geometry. | P2 | Cross-connectivity claim | **Resolved:** compare cell-set hashes and report three one-cell differences. |
| 2 | Threshold-state continuity is not water-parcel continuity. | P3 | Boundary | Retain the explicit material-identity denial. |
| 3 | The sweep does not diagnose forcing, advection, or impacts. | P3 | Next evidence | Keep mechanism work separate from identity sensitivity. |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Derived comparisons must remain tied to the checksum-pinned 32-file source chain. | P2 | Provenance | **Resolved:** validate source, D3, and D4 hashes offline. |
| 2 | Connectivity equality needs cell-level evidence, not matching summary numbers. | P2 | Result schema | **Resolved:** store a SHA-256 for every daily component and both gap footprints. |
| 3 | The climatology, native grid, interval, and product version must remain visible. | P3 | Figure footer | Preserve the NOAA CRW v1.0.1 source line. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first headline overstated adjacency invariance. | P2 | Headline | **Resolved:** state that adjacency changes shape but not tested lifetime. |
| 2 | The post-gap timeline segment was visually unexplained. | P2 | Timeline | **Resolved:** label stable plateau, permissive tail, gap, and post-gap run. |
| 3 | Matrix color cannot carry the outcome alone. | P3 | Policy cells | Keep duration and dates printed in every tile. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | IoU was unexplained specialist shorthand. | P2 | Public key | **Resolved:** define it as shared cells divided by the union. |
| 2 | “Stable core” could falsely mean agreement across all ten policies. | P2 | Lead | **Resolved:** call the 18-day result a moderate-threshold plateau. |
| 3 | The public sentence should identify both invariance and sensitivity. | P3 | Summary | Retain “three shapes differ by one cell; all five lifetimes match.” |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Duration classes cannot rely on teal and orange. | P3 | Matrix | Text redundantly states days and date ranges. |
| 2 | The SVG needs a complete nonvisual conclusion. | P2 | Accessible description | **Resolved:** title and description state geometry differences, all policy outcomes, and IoU meaning. |
| 3 | The gap needs a non-color distinction. | P3 | Timeline | Preserve the hatched gap and printed label. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Live NOAA access cannot be a default test dependency. | P3 | Acquisition | Keep refresh explicit and the committed-artifact contracts offline. |
| 2 | The baseline must reproduce both D3 and D4 exactly. | P2 | Cross-artifact contract | **Resolved:** fail generation on any baseline lineage or bridge mismatch. |
| 3 | A future silent geometry drift must fail tests. | P2 | Test gate | **Resolved:** assert hashes, exact lifetimes, disputed-edge metrics, and cross-connectivity counts. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | OER009 is an identity-sensitivity stage, not a new registry object. | P3 | Registry | Keep the taxonomy at 110 objects. |
| 2 | Receipt totals and links must agree across repository entry points. | P2 | Documentation | **Resolved:** synchronize README, Guide 14, history, analysis docs, and generated collection at nine receipts. |
| 3 | No publication action occurred. | P3 | Repository state | Continue to describe the work as local and uncommitted. |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Pixel adjacency is instrument-grid logic, not a universal fluid-object law. | P3 | Transfer | Recalibrate connectivity for each planetary observation geometry. |
| 2 | Equal tracked lifetime does not establish equal atmospheric material. | P3 | Analogy | Transfer the identity-policy grammar only. |
| 3 | Cadence and resolution can move both IoU and apparent gaps. | P3 | Falsification | Resample before comparing Earth and cloud-top objects. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0 | P2 issues: 11 (all resolved) | P3 notes: 13
Verdict: APPROVED
Top finding: adjacency changes three daily shapes by one cell each, while every tested lifetime and both exact gap footprints remain unchanged.
Cross-role consensus: robustness must name the output that stayed invariant; it cannot be promoted to material or mechanistic continuity.
```

## Amendments applied

1. Added exact daily-component and gap-footprint hashes, exposing the three
   one-cell adjacency differences and correcting the headline.
2. Defined IoU, labeled every timeline interval, and added product, grid,
   interval, and evidentiary-boundary text to the SVG.
3. Marked the overlap sweep illustrative, expanded OER009's limits, and added
   offline cross-artifact and deterministic-view contracts.

Remaining non-blocking work: test alternative split/merge branch selection,
then compare atmospheric forcing and ocean advection around August 7–12 without
treating either as established from threshold geometry alone.
