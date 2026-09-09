---
skill: roles-check
topic: marine-heatwave-separate-sst-crosscheck
date: 2026-09-06
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Roles check — OSW-D10 separate-product SST cross-check

**Artifact type:** observation-derived research analysis, static scientific map,
source artifact, evidence receipt, and documentation update  
**Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b` plus the reviewed working-tree changes  
**Reviewed artifacts:** `atlas/data/oisst-mhw-bridge-north-atlantic-20260807-20260812.json`,
`research/osw-d10-oisst-mhw-bridge-crosscheck-2026.json`, and
`figures/osw-d10-oisst-mhw-bridge-crosscheck-2026.svg`

## Role selection

| Role | Why selected |
|---|---|
| CURRENT | The result contrasts a threshold state with temperature evolution and points toward a future heat budget. |
| SOUNDER | Two processed SST products, grids, provenance chains, and an extracted DAP slice are compared. |
| CHART | Six gridded fields, contours, an anchor, a common scale, and a time series carry the claim. |
| BEACON | The headline must prevent readers from turning mismatch into causal explanation. |
| HARBOR | Category, temperature, and transition meaning must remain available without color alone. |
| KEEL | Network acquisition must remain outside deterministic tests while committed bytes and calculations are locked. |
| LOGBOOK | The fourteenth receipt, history, guide, and commands must agree with repository state. |

ORBIT was not selected: D10 makes no planetary comparison. The seven selected
roles cover every scientific, visual, accessibility, reproducibility, and
repository claim in this stage.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A CRW category is a threshold state, not SST itself; the headline could be misread as comparing like quantities. | P2 | Headline and interpretation | State the distinction beside the result and in the machine-readable boundary. **Resolved.** |
| 2 | A fixed-box mean is neither moving-object heat content nor a closed temperature budget. | P2 | Analysis boundary | Explicitly exclude heat content, advection, flux attribution, and causation. **Resolved.** |
| 3 | Opposite anchor and box tendencies admit spatial rearrangement, product processing, threshold evolution, and mixing; none is selected by D10. | P3 | Finding | Preserve all as live hypotheses and require collocated flux/current/MLD terms next. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Calling OISST “independent” overstates separation because SST products may share observing inputs. | P2 | Source class and all public prose | Replace with “separate-product,” disclose possible input overlap, and avoid statistical-independence language. **Resolved.** |
| 2 | A base DAP URL alone does not identify the extracted bytes. | P2 | Source artifact | Store variable, time indices, spatial index ranges, coordinate axes, retrieval time, and exact hyperslab. **Resolved.** |
| 3 | The checksum covers extracted values rather than raw transport bytes. | P3 | Provenance | State the checksum scope in the source boundary and validate it offline. **Resolved.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | All six panels require one fixed numeric scale for valid visual comparison. | P2 | Six field maps | Lock every panel to 15–27°C and provide one shared labeled colorbar. **Resolved.** |
| 2 | The map projection was not initially named. | P2 | Figure footer | Label the geographic grid as equirectangular / Plate Carrée. **Resolved.** |
| 3 | The anchor and warm contours need non-color encodings. | P3 | Field panels | Retain a white plus marker, numeric anchor temperature, and labeled 24/25°C contour key. **Resolved.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “The category returns” is memorable but must not imply physical reheating. | P2 | Headline/deck | Pair it immediately with “nearest cell keeps cooling” and “not a diagnosed cause.” **Resolved.** |
| 2 | Product mismatch can be mistaken for one product being wrong. | P2 | Guide | Explain that grid, inputs, processing, and threshold definitions differ and that D10 cannot adjudicate them. **Resolved.** |
| 3 | Readers need a direct quantitative takeaway. | P3 | Callout | Show category 0→1, anchor −0.13°C, and box +0.16°C together. **Resolved.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Palette alone cannot communicate the bridge result. | P2 | Figure | Redundantly encode it with contours, marker, daily numbers, line chart, and textual callout. **Resolved.** |
| 2 | Static SVG needs machine-readable textual meaning. | P2 | SVG and paired JSON | Preserve live SVG text plus a data-oriented JSON result and boundary. **Resolved.** |
| 3 | Small footer text is supplementary rather than the sole caveat route. | P3 | Figure/footer | Repeat the scientific limitation in the adjacent guide and receipt. **Resolved.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Live OPeNDAP availability must not become a default test dependency. | P2 | Acquisition/test split | Keep refresh explicit; test committed source bytes and deterministic transforms offline. **Resolved.** |
| 2 | A stored digest without recomputation would not detect edited field values. | P2 | Source test | Recompute SHA-256 from canonical compact JSON rows in the test. **Resolved.** |
| 3 | Shape, date count, coordinate selection, and key bridge numbers require regression locks. | P3 | Tests | Assert 6×12×17 support, exact hyperslab, category transition, and three tendencies. **Resolved.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Receipt count and descriptions must move together. | P2 | README/guide/collection | Update all public references from thirteen to fourteen and regenerate the collection. **Resolved.** |
| 2 | A new evidence stage needs commands and project-history interpretation. | P2 | Analysis README/history | Document fetch/analyze/render/receipt commands and record what D10 changed. **Resolved.** |
| 3 | The working tree is intentionally uncommitted and no release action was authorized. | P3 | Repository state | Report validation without claiming commit, push, or publication. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 14  |  P3 notes: 7

Verdict: APPROVED

Top finding: OISST is a separate analysis, not a statistically independent one;
the public claim and provenance now say so.

Cross-role consensus: CURRENT, SOUNDER, and BEACON agree that the category/SST
mismatch is a hypothesis discriminator, not mechanism attribution. CHART and
HARBOR agree that marker, contour, numeric, and textual encodings must carry the
result alongside color. KEEL and LOGBOOK agree that refresh stays explicit and
the committed extracted slice remains the offline evidence input.
```

## Amendments completed

1. Replaced “independent” with “separate-product” throughout D10 and disclosed
   possible shared observing inputs.
2. Added the exact DAP hyperslab/index contract, named the Plate Carrée
   projection, and expanded non-color encodings.
3. Added offline digest recomputation and dimensional/numerical regression
   locks, then aligned the fourteenth receipt, guide, README, history, and
   analysis commands.

No external peer review is implied by this repository role check.
