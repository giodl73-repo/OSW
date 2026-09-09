---
skill: roles-check
topic: five-band-water-atlas
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Five-band water atlas

**Artifact type:** responsive scientific small multiples, cross-band
concentration comparison, textual data summary, and public documentation

**Source commit:** `082a889`

**Reviewed artifact SHA-256:**

- browser logic: `039A295603A2F33DBFB87891E3D31DA9BFF1AFAFD65C926AC367977AF510F3DD`
- browser HTML: `90FCCD627CEB6A6A67902F1415FC19FE072213FD961DCF5AD908DAF2F043862B`
- scientific tests: `189B7434A4046C676C1D3CB206E3345BC7E38C7564534E0C80439C8115E53229`
- viewer tests: `AD48131DB5DED1C395C59729248DCBF069E322558052AA9BCA26056D7B9992EE`
- workbench method: `C3517913D8FD7D4E73E543C084C042A9F0FE4BA43121BF199AD0C431C6DCABED`
- address guide: `07E0D920BACC2E326209304F2452FD7F39A89608BB55B2BF36EEAEDAFF457F45`

## Role selection

All eight OSW roles apply. The plate compares five depth supports using one
visual scale, adds concentration statistics, changes layout responsively, and
could be misread as absolute-volume, heat, habitat, or planetary-layer maps.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Cross-band concentration describes the spatial partition of reference volume, not heat, transport, life, or water masses. | P2 | Scientific interpretation | State the excluded mechanisms directly below the plate. **Resolved.** |
| 2 | A state's percentage uses a different global band denominator in each panel. | P2 | Cross-band comparison | Keep absolute band totals in subtitles and say equal color does not mean equal km³ across panels. **Resolved.** |
| 3 | Increasing concentration with depth is a descriptive geometry result under this partition. | P3 | Main finding | Do not assign a causal mechanism from the plate alone. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every map and statistic must derive from D53 rather than duplicated prose values. | P2 | Data lineage | Compute shares, leaders, counts, and top-five totals at runtime from the committed payload. **Resolved.** |
| 2 | Reported concentration values need regression protection. | P2 | Quantitative claims | Test the five leaders, leader shares, and top-five shares exactly at displayed precision. **Resolved.** |
| 3 | The five panels inherit the same geometry, sampling, mask, and edition limitations. | P3 | Provenance | Use one source-aligned assignment grid and keep D53/D55 boundaries adjacent. **Resolved.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Within-band ranks would not be visually comparable across five panels with different eligibility counts. | P2 | Shared scale | Map fixed shares of global band volume: <1, 1–<2, 2–<5, 5–<10, and ≥10%. **Resolved.** |
| 2 | Projection and extent must remain identical for true small-multiple comparison. | P2 | Geography | Reuse the same Oceanic Mollweide assignment grid and panel dimensions. **Resolved.** |
| 3 | Absolute band magnitude must not be encoded with the within-band percentage palette. | P3 | Panel annotation | Print total million km³ and positive-state count in every panel subtitle. **Resolved.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Hadal is concentrated” needs its declared denominator and partition. | P2 | Public claim | Say the top five hold 68.09% of sampled hadal volume under the 54-state reference. **Resolved.** |
| 2 | The gradual 36.02%–40.33% upper-to-abyssal pattern and hadal jump are more informative than five winner labels. | P2 | Narrative | Report all five top-five shares in order. **Resolved.** |
| 3 | “Water atlas” must not become shorthand for observed dynamic ocean state. | P3 | Terminology | Keep “sampled volume geography” and the evidence boundary in the reading path. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A fixed 3+2 raster becomes unreadable postage stamps on narrow screens. | P2 | Responsive layout | Switch below 700 px to five full-width vertically stacked panels and rerender on media-query changes. **Resolved.** |
| 2 | Five canvas maps need a complete nonvisual equivalent. | P2 | Alternative content | Provide an ordered text list with total, state count, leader/share, and top-five share for every band. **Resolved.** |
| 3 | Selection and zero support cannot depend on gold and gray alone. | P3 | Legend | Define both marks in text and retain selected-province and band facts in the passport. **Resolved.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Five maps must not multiply full-resolution point-in-polygon work in the browser. | P2 | Rendering | Reuse the cached projected assignment and sample it into five smaller image buffers. **Resolved.** |
| 2 | Concentration statistics can drift independently of basic band-total closure tests. | P2 | Regression | Add exact leader and top-five percentage assertions. **Resolved.** |
| 3 | Responsive behavior needs browser inspection in both layouts. | P3 | Visual verification | Inspect 1440 px desktop and 390 px Edge captures with the hadal selection active. **Resolved.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new comparative claim requires a source-register identity. | P2 | Evidence record | Add D56 with scale semantics, all five concentrations, and limitations. **Resolved.** |
| 2 | README, roadmap, method, guide, history, and data notes must tell the same story. | P2 | Repository record | Update them together before commit. **Resolved.** |
| 3 | The plate remains private preview and does not authorize publication. | P3 | Release state | Commit locally only after the full suite. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earth depth-band volume concentration cannot be compared directly with visible gas-giant bands. | P2 | Planetary scope | Keep the five maps Earth-only. **Resolved.** |
| 2 | A gas-giant analogue would require pressure/mass weighting and independent domain boundaries. | P2 | Analogy contract | Do not reuse the metre-depth volume result. **Accepted.** |
| 3 | Same-scale small multiples are transferable as visual method after defining a valid planetary measure. | P3 | Method transfer | Transfer comparison discipline, not the present bands or values. **Accepted.** |

## Synthesis

Roles reviewed: 8

P1 blockers: 0 | P2 issues: 16 | P3 notes: 8

**Verdict: APPROVED-WITH-CONDITIONS**

**Top finding:** The fixed palette compares within-band global shares; absolute
volume differs sharply and must remain separately labeled in every panel.

**Cross-role consensus:** CURRENT, CHART, BEACON, and HARBOR agree that the
five maps are valid only with one projection, one declared percentage scale,
absolute subtitles, and a complete text equivalent.

## Amendments

1. Replace within-band rank colors with one fixed global-band-share scale.
   **Applied across all five panels.**
2. Add per-panel absolute totals and complete ordered textual equivalents.
   **Applied beside the canvas and in its accessible description.**
3. Reflow 3+2 desktop panels into five full-width mobile panels.
   **Applied and visually checked at 1440 px and 390 px in Edge.**

The five-band atlas may be committed to the private-preview branch after the
full suite. Causal interpretation, heat/ecology overlays, public promotion,
and the 54/56 edition decision remain separate gates.
