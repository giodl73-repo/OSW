---
skill: roles-check
topic: heatplates-shape-atlas
date: 2026-08-29
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK, ORBIT]
p1_count: 0
verdict: APPROVED
---

# HEATPLATES shape-atlas native-role review

Source commit: `e91e67a` (`Add Equal Earth and HEATPLATES views`)

## Artifact identification

- Type: conceptual cartographic design, generated SVG, and projection-lab page
- Signals: schematic ocean heat features, local equal-area projections,
  panel-specific zoom, pinned coastline input, public-science explanation
- Selected roles: all eight OCEANLINES roles because this is a reviewable atlas
  milestone. ORBIT is included to confirm that no planetary analogy leaked into
  an Earth-only graphic.

## Findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The footer explicitly rejects interpreting the panels as heat content or transport. | P3 | HEATPLATES footer | Keep this limitation on every derivative graphic. |
| 2 | Feature subtitles distinguish reservoir, seasonal reservoir, transient anomaly, equatorial anomaly, buried heatmass, and annular heatmass. | P3 | panel headers | Preserve evidence-class labels as definitions improve. |
| 3 | Crisp outlines remain schematic and do not claim fronts are fixed or impermeable. | P3 | page method | Replace them only with declared observed, diagnosed, or modeled criteria. |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The graphic calls itself a conceptual shape directory and states “not observed thresholds.” | P3 | HEATPLATES footer | Do not attach dates, depths, or units until observational data actually drive the regions. |
| 2 | Coastline geometry remains checksum-pinned and the build aborts on a mismatched source. | P3 | generator | Preserve the checksum gate. |
| 3 | Generated and observational atlas artifacts remain separate. | P3 | repository structure | Add source-variable metadata before any measured boundary enters HEATPLATES. |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every local panel names Lambert equal-area and declares panel-specific zoom. | P3 | panel footers | Keep projection and zoom disclosure adjacent to the maps. |
| 2 | The prominent warning correctly forbids footprint-area comparison across panels. | P3 | warning band | Add a common-scale companion only when the regions become quantitatively defined. |
| 3 | Equal Earth adds a continuous flat equal-area control while all earlier global views remain available. | P3 | candidate grid | Keep its one-seam polar limitation visible in the verdict. |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The heading clearly explains why a second experiment exists: one world map cannot maximize every local silhouette. | P3 | experiment 02 | Retain this problem-first entry. |
| 2 | “Compare shape and context—not footprint area” gives a non-specialist a safe repeatable takeaway. | P3 | HEATPLATES copy | Reuse that exact limitation in external captions. |
| 3 | The page keeps “what it offers” beside “where it fails” for each global candidate. | P3 | candidate verdicts | Apply the same paired framing to future experiments. |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Panel number, name, class, shape, line treatment, and color redundantly encode the six objects. | P3 | HEATPLATES SVG | Preserve non-color distinctions. |
| 2 | The page supplies semantic headings, descriptive alternative text, and a direct full-size SVG link. | P3 | projection page | Keep alt text synchronized with the artifact. |
| 3 | Responsive layout collapses the experiment to one column without removing content. | P3 | CSS | Add automated keyboard and 400% zoom checks later. |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | One documented Python generator produces all global candidates and HEATPLATES. | P3 | analysis pipeline | Never hand-edit the generated SVGs. |
| 2 | The offline suite now has 66 passing tests and locks the new operators, names, warning, and artifacts. | P3 | tests | Add numeric coordinate fixtures before changing projection centers. |
| 3 | Python compilation, browser JavaScript syntax, and diff checks pass. | P3 | validation | Add browser regression captures when a stable harness is selected. |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, analysis instructions, source register, page, artifacts, and tests moved together in source commit `e91e67a`. | P3 | repository state | Record this review beside the milestone in preview status. |
| 2 | The work remains a private-preview experiment and no remote has been changed. | P3 | release state | Run publication governance separately before any push. |
| 3 | No private researcher name, RESONANCE reference, machine-specific path, or unlicensed asset appears in the deliverable. | P3 | public boundary | Recheck the boundary at release time. |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | HEATPLATES makes no gas-giant analogy; it first stabilizes the Earth-side geographic vocabulary. | P3 | scope | Keep planetary comparison in a separately labeled study. |
| 2 | The words belt, realm, and heatmass are not visually transferred to atmospheric bands without a mechanism comparison. | P3 | labels | Require forcing, stratification, rotation, depth, and observation-method comparisons before transfer. |
| 3 | The annular Southern Ocean mark is not presented as equivalent to a gas-giant jet. | P3 | panel 06 | Preserve the Earth-specific label and limits. |

## Synthesis

Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 24

Verdict: APPROVED

Top finding: HEATPLATES is scientifically legible only because its repeated
warning prevents viewers from comparing apparent area across differently
zoomed panels.

Cross-role consensus: CURRENT, SOUNDER, CHART, and BEACON agree that the crisp
shapes are useful conceptual geography only when “schematic—not observed
thresholds, heat content, or transport” remains adjacent and explicit.

## Amend

1. Add common-scale panels only after observational boundary rules, depth,
   interval, source, and uncertainty are defined.
2. Add machine-readable feature IDs and artifact provenance before downstream
   reuse or interaction.
3. Add automated narrow-screen, keyboard, and high-zoom browser checks when a
   regression harness is introduced.

