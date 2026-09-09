---
skill: roles-check
topic: interactive-province-atlas-ground
date: 2026-08-29
roles_used: 7
p1_count: 0
verdict: APPROVED
---

# Native-role review — interactive Province Atlas ground

## Artifact identification

- **Type:** interactive cartographic design, generated SVG, browser code, and observational-layer integration
- **Source commit:** `a72074d`
- **Scope:** use the coast-owned 56 provinces as the common Atlas 10 ground; retain six conceptual lenses and four observed modes; add selection, keyboard operation, URL state, zoom, and reset
- **Evidence boundary:** real public-domain Natural Earth coast edges; original approximate nearest-seed internal borders; classic 56-province vocabulary; no published Longhurst boundary geometry

## Role selection

- **SOUNDER** — observed fields remain visible below the new reference overlay.
- **CHART** — projection alignment, coastline ownership, and boundary meaning are central.
- **BEACON** — the state/lake metaphor needs visible limits.
- **HARBOR** — SVG selection and zoom require equivalent keyboard and non-color paths.
- **KEEL** — generated geometry and cross-mode behavior need an offline contract.
- **CURRENT** — crisp edges must not imply material walls or physical budgets.
- **LOGBOOK** — this change of geographic ground needs a durable record.

## Findings

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Province outlines are a presentation overlay and do not alter pinned OISST or Argo arrays. | P3 | observed modes | Preserve source metadata and product-specific text when zoomed. |
| 2 | Zoom crops display support but does not aggregate observations by province. | P3 | province zoom | Keep the coordinate probe product-native; label future province statistics as derived. |
| 3 | Natural Earth identity and checksum remain in generated SVG metadata. | P3 | generator | Retain checksum validation as a hard generation gate. |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | All modes share one equirectangular 1600×1050 frame, keeping borders registered with the observed canvas. | P3 | shared ground | Preserve the frame constants together if projection changes. |
| 2 | Coastal states inherit the coast they touch; continents read as negative-space lakes. | P3 | province SVG | Treat coast ownership as the defining visual contract. |
| 3 | Nearest-seed borders are crisp enough to be mistaken for diagnosed boundaries. | P3 | map note | Keep “approximate reference geometry” beside observed views and province details. |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “The coast belongs to the province” clearly explains the geometry. | P3 | primary concept | Pair it consistently with “internal borders are approximate.” |
| 2 | Readers can keep a province while changing the scientific lens, making overlap understandable. | P3 | interaction | Preserve the province status line across mode changes. |
| 3 | “States” can imply permanence if separated from its qualifier. | P3 | controls | Use “56 approximate ocean states” in the persistent strip. |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every province is a focusable SVG button and responds to Enter and Space. | P3 | SVG/JS | Keep the dropdown as a redundant keyboard and text route. |
| 2 | Selection appears through code, name, panel text, dropdown value, and URL—not color alone. | P3 | selection | Retain all redundant cues. |
| 3 | Zoom animation could create motion discomfort. | P3 | CSS | Disable the viewport transition under `prefers-reduced-motion`. |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Generation fails if any of the 56 identities lacks an approximate seed. | P3 | generator | Keep the completeness assertion and 56-count test. |
| 2 | Static tests cover controls, URL state, observed overlay, and zoom functions. | P3 | tests | Add automated browser geometry tests if a browser harness enters the default toolchain. |
| 3 | Manual Edge checks exercised overview, `province=ALSK`, and `province=ALSK&mode=anomaly`. | P3 | browser validation | Repeat these three states before public promotion. |

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Province identity is separated from water masses, currents, fronts, and observed fields that cross it. | P3 | lenses | Do not infer mechanism from province membership. |
| 2 | Zoom preserves each product's depth, date, and reference rather than presenting generic “heat.” | P3 | observed modes | Maintain the measurement firewall in close-ups. |
| 3 | Feature membership uses representative points inside schematic cells, not diagnosed physical overlap. | P3 | province detail | Keep that approximation explicit until geographic boundaries exist. |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Generated SVG, builder, interface, tests, and browser behavior are versioned together in `a72074d`. | P3 | repository | Cite this commit in history and preview status. |
| 2 | Old colored and punched-lake studies remain available, preserving design lineage. | P3 | figures | Continue treating them as experiments, not current truth. |
| 3 | Public promotion remains unauthorized and the branch remains private. | P3 | release state | Do not push or update release metadata yet. |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 21

Verdict: APPROVED

Top finding: The 56 provinces can serve as one stable geographic ground across
conceptual and observed views, provided crisp internal borders remain explicit
approximations.

Cross-role consensus: CHART, BEACON, CURRENT, and HARBOR agree that boundary
qualification must remain visible during selection and zoom; SOUNDER and KEEL
agree that zoom must not silently become province aggregation.
```

## Amendments applied

1. Added “56 approximate ocean states,” an `aria-live` status, a complete province dropdown, and reduced-motion handling.
2. Added an observed-mode note stating that province borders are approximate while preserving field metadata.
3. Added offline tests for 56 selectable groups, shared overlay, URL state, zoom/reset code, and generated-source contract.
