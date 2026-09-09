---
skill: roles-check
topic: ocean-first-fluid-geography
date: 2026-08-28
source_commit: 762a7de
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK, ORBIT]
p1_count: 0
p2_count: 0
verdict: APPROVED
---

# Roles check: ocean-first fluid geography

## Artifact identification

- **Type:** conceptual scientific map, interactive atlas view, generator, and documentation.
- **Reviewed:** `figures/osw-fluid-geography.svg`, its interactive variant, `atlas/`, `analysis/build_fluid_geography.py`, source register, and Atlas README.
- **Evidence class:** explanatory synthesis. Natural Earth supplies geographic context; heat regions, currents, gates, and pathways are schematic rather than measured fields.
- **Approval scope:** private visual preview. This is not approval of an observational heat atlas or a public release.

## Role selection

All eight project roles apply. CURRENT, SOUNDER, and CHART govern the physical and geographic reading; BEACON and HARBOR govern public comprehension and equivalent access; KEEL and LOGBOOK govern generation and repository truth; ORBIT governs the explicitly bounded planetary-comparison lens.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The map identifies warm pools, anomaly regions, currents, fronts, and buried pathways as different mechanisms instead of presenting a single undifferentiated “heat” field. | P3 | Map legend and callouts | Preserve this separation when measured layers are added. |
| 2 | The title block and footer explicitly say the graphic is a conceptual geography and not a heat budget; this prevents temperature patterns from being read as diagnosed transport. | P3 | Figure header/footer | Keep the evidence-class statement visible in exports. |
| 3 | The ACC is drawn as a broad, permeable circumpolar flow rather than an impermeable wall, while Drake Passage is shown as a gate in a larger coupled system. | P3 | Southern Ocean | Retain language about mixing, overturning, atmosphere, sea ice, and bathymetry in any gateway counterfactual. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Natural Earth land geometry is identified by repository commit, raw-file URL, license class, and SHA-256 checksum. | P3 | Atlas README; source register D11 | Preserve the pin if the geometry is refreshed. |
| 2 | The generator verifies the source checksum before writing either SVG, separating acquired geography from authored overlays. | P3 | `analysis/build_fluid_geography.py` | Add any future measured products as separate registered sources, never as an extension of D11. |
| 3 | Documentation states that land geometry is sourced while the heat regions and flows are schematic; no observational provenance is implied for the overlays. | P3 | Figure metadata; source register | Keep the distinction in captions and email previews. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Real 1:110m coast geometry and a consistent equirectangular world frame materially improve geographic recognition without pretending to be a navigation map. | P3 | Basemap | Name the projection again if axis labels or quantitative spatial comparison are added. |
| 2 | Currents use directional strokes, gates use diamond marks, heat regions use filled forms, and buried pathways use dashed strokes; meaning is not carried by hue alone. | P3 | Mechanism key | Preserve these redundant encodings across future palettes. |
| 3 | The annotated standalone SVG and clean interactive SVG solve different density needs: one is a self-contained poster, while browser callouts remain selectable and uncluttered. | P3 | Static and interactive variants | Continue testing both forms whenever labels or coast geometry change. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “A fluid geography of heat” gives readers a useful organizing idea without claiming the regions are literal continents or permanent boundaries. | P3 | Figure title | Define any new project coinage beside its first appearance. |
| 2 | The subtitle and footer put “what this shows” beside “what this cannot establish,” including the distinction between conceptual geometry and a measured heat budget. | P3 | Figure header/footer | Keep both statements in cropped or social versions. |
| 3 | Compact numbered callouts provide a short reading path, while the Atlas directory contains fuller explanations for readers who want mechanism and caveat. | P3 | Callouts; Atlas side panel | Avoid expanding poster prose until it competes with the map. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Each SVG has a title and description, and the Atlas supplies a data-oriented text directory rather than treating the graphic as its own alternative text. | P3 | SVG metadata; Atlas directory | Update both whenever zones are renamed or reordered. |
| 2 | Interactive markers are keyboard-operable and connect to a side panel; category and selection are not communicated solely through color. | P3 | Atlas interaction | Retest focus order after any control additions. |
| 3 | Desktop and 390-pixel rendering preserve the map, text directory, and full-size static-map route without horizontal overflow. | P3 | Responsive layout | Keep the full-size link visible because fine map detail necessarily compresses on phones. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The checked-in SVGs are deterministically generated from a checksum-verified local source; regeneration produced stable output hashes. | P3 | Generator and SVG outputs | Keep network acquisition outside the default test path. |
| 2 | The Atlas test suite covers required files, source pinning, callout separation, and marker positions; browser JavaScript and both SVGs pass syntax/XML checks. | P3 | `analysis/test_atlas.py` | Add screenshot regression only if visual churn begins to evade structural tests. |
| 3 | Both desktop and narrow browser runs completed without script errors or horizontal overflow. | P3 | Browser verification | Repeat this smoke test before packaging a public release. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The root README, Atlas README, source register, and publication checklist describe the new map and its conceptual status consistently. | P3 | Repository documentation | Update all four together when evidence class changes. |
| 2 | The source commit and review scope are recorded here, allowing this decision to be compared with a later measured-atlas review. | P3 | Review frontmatter | Do not reuse this approval for later commits without review. |
| 3 | No private person, private project, machine-local source dependency, or unlicensed map asset appears in the preview content. | P3 | Public-boundary scan | Preserve the current neutral framing in any shared preview. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The Earth map stands on its own and does not use gas-giant imagery as evidence for its oceanographic regions. | P3 | Conceptual map | Keep planetary comparison in an optional interpretive layer. |
| 2 | The footer limits the analogy to a geometry-reading lens and explicitly rejects physical equivalence. | P3 | Figure footer | Retain the caveat wherever the comparison appears. |
| 3 | The atlas does not infer full-depth heat structure from visible bands on another planet. | P3 | Atlas copy | A future comparison should name the exact shared mechanism and a falsification test. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 24

Verdict: APPROVED

Top finding: The ocean-first graphic now combines recognizable geography with an explicit, repeated boundary between sourced coastline and schematic heat mechanisms.
Cross-role consensus: The map is fit for a private visual preview because its conceptual status remains visible in the figure, text alternative, provenance record, and generated artifacts.
```

## Amendments applied

1. Replaced abstract land silhouettes with pinned public-domain Natural Earth geometry and recorded the exact source checksum.
2. Split the visual into an annotated standalone poster and a clean browser-embedded variant so interaction does not duplicate or obscure callouts.
3. Repositioned all interactive markers on geographic anchors, added redundant mechanism symbols, and preserved a text directory plus full-size route for narrow screens.

