---
skill: validate-design
topic: atlas-feature-silhouettes
date: 2026-08-29
reviewer_count: 10
p1_count: 0
p2_count: 18
p3_count: 22
domain_roles_active: [Ocean Cartographer, Physical Oceanographer, Scientific Visualization Designer, Accessibility Specialist]
---

# Atlas feature silhouettes — design review

Reviewed artifacts: `plans/province-atlas-shape-system.md`,
`analysis/build_atlas_feature_overlay.py`, the generated feature overlay, the
fluid-geography map, and HEATPLATES. The review addresses the owner's finding
that the first 36-shape overlay reads as generic symbols rather than serious
ocean geography.

## BLOCK 0 — CONTENT SIGNAL CATALOGUE

| Signal phrase | Domain category |
|---|---|
| “geographically placed, mechanism-specific shapes” | ocean cartography |
| water masses, currents, fronts, gyres, and seafloor features | physical oceanography |
| “shape first” and memorable silhouettes | scientific visualization |
| selectable, keyboard-focusable SVG geography | accessibility |
| schematic indexes rather than observed boundaries | provenance and scientific communication |

## BLOCK 1 — EXPERT ROSTER

| Reviewer | Role |
|---|---|
| Architect | Stock |
| Code-Quality | Stock |
| Documentation | Stock |
| Testing | Stock |
| Process | Stock |
| Implementation | Stock |

| Signal detected | Expert added | Reason |
|---|---|---|
| “geographically placed, mechanism-specific shapes” | Ocean Cartographer | Geographic character and coast/basin relationships require a cartographic silhouette grammar. |
| water masses, currents, fronts, gyres, and seafloor features | Physical Oceanographer | Each mechanism needs a form consistent with its actual spatial organization. |
| “shape first” and memorable silhouettes | Scientific Visualization Designer | Visual hierarchy and family differentiation determine whether the map reads as an atlas or icon sheet. |
| selectable, keyboard-focusable SVG geography | Accessibility Specialist | Complex non-point hit areas must retain usable focus and interaction behavior. |
| schematic indexes rather than observed boundaries | No expert needed | Documentation and scientific-visualization review jointly cover the existing provenance firewall. |

BLOCK 1 domain count = 4

## BLOCK 1.5 — ROSTER COMMITMENT TABLE

| Reviewer | Role | Source |
|---|---|---|
| Ocean Cartographer | Domain expert | Domain |
| Physical Oceanographer | Domain expert | Domain |
| Scientific Visualization Designer | Domain expert | Domain |
| Accessibility Specialist | Domain expert | Domain |
| Architect | Stock discipline | Stock |
| Code-Quality | Stock discipline | Stock |
| Documentation | Stock discipline | Stock |
| Testing | Stock discipline | Stock |
| Process | Stock discipline | Stock |
| Implementation | Stock discipline | Stock |

Conformance: 4 domain rows equal the BLOCK 1 count; every domain reviewer name
matches the expert roster.

## BLOCK 2 — PER-REVIEWER FINDINGS

### Ocean Cartographer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| OC-1 | Elliptical gyres look like diagram symbols, not basin circulation. | P2 | Flows | Use asymmetric basin-fitted loops with pinches and open current structure. |
| OC-2 | Several water masses are smooth capsules unrelated to coast or basin shape. | P2 | Waters | Give each a source neck, spreading tongue, and basin-constrained edge. |
| OC-3 | Diamond gates discard the recognizable geometry of Drake and the Indonesian archipelago. | P2 | Edges | Draw short section bars and multiple passage cuts instead of badges. |
| OC-4 | Fronts are single generic waves with no distinction from current paths. | P3 | Edges | Use paired meandering frontal traces and different dash rhythm. |

### Physical Oceanographer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| PO-1 | AABW is rendered as one zonal Southern Ocean slab, hiding its abyssal tongues. | P2 | Waters | Show three northward basin tongues emerging from an Antarctic source belt. |
| PO-2 | NADW lacks a northern source and deep western-boundary spreading character. | P2 | Waters | Draw a narrow source-fed plume that broadens and branches southward. |
| PO-3 | Subtropical gyres omit western intensification and directional flow. | P2 | Flows | Vary stroke weight or add arrowed basin loops with tight western turns. |
| PO-4 | OMZs appear as freestanding green islands rather than subsurface coastal wedges. | P2 | Life | Use coast-hugging tapered fields and oxygen-specific hatching. |

### Scientific Visualization Designer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| SV-1 | Repeated ellipses and rounded quadrilaterals erase object identity. | P2 | Whole overlay | Require a unique silhouette signature for every one of the 36 objects. |
| SV-2 | Uniform stroke treatment makes area, path, boundary, and relief objects feel interchangeable. | P2 | Visual grammar | Give each family a distinct edge, fill, and internal texture grammar. |
| SV-3 | The first 12 rich forms and later 24 primitives create an obvious quality cliff. | P2 | Catalog sequence | Bring later objects to the same control-point density and asymmetry. |
| SV-4 | The all-features view can become a tangle without depth hierarchy. | P3 | Layering | Use lower resting opacity, family texture, and strong selected-state emphasis. |

### Accessibility Specialist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| AX-1 | Thin paths can be difficult pointer targets even when visually appropriate. | P2 | Flows / floor | Preserve transparent wide hit paths for every line object. |
| AX-2 | Shape family cannot depend on hue alone. | P2 | Legend / SVG | Retain dash, texture, tooth, and fill-pattern differences. |
| AX-3 | Focus should reveal the entire selected object, including multi-part geometry. | P3 | Interaction | Apply focus styling at the feature group level. |
| AX-4 | Complex shapes still require concise accessible names. | P3 | SVG groups | Preserve role, tabindex, title, and `aria-label` for all 36 groups. |

### Architect

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| AR-1 | Raw geometry tuples mix data, visual grammar, and SVG implementation. | P2 | Generator | Introduce helper constructors or named geometry constants by mechanism. |
| AR-2 | Reusable path conventions are not encoded centrally. | P3 | Generator | Add common hit-path and arrow conventions in defs/styles. |
| AR-3 | The design contract covers provinces more deeply than crossing features. | P2 | Plan | Add a feature-silhouette contract covering identity, mechanism, and caveats. |
| AR-4 | The overlay should remain independent of observed-mode rendering. | P3 | Atlas architecture | Keep the feature layer conceptual-only and hidden for observed fields. |

### Code-Quality

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| CQ-1 | Long inline SVG strings are hard to audit. | P3 | Generator | Format complex multi-part geometry as named constants or adjacent strings. |
| CQ-2 | Geometry class vocabulary lacks validation. | P2 | Generator / tests | Test presence of family-specific signatures and ban primitive gyre ellipses. |
| CQ-3 | A typo in one SVG path could silently degrade a feature. | P3 | Generation | Parse the generated SVG in tests. |
| CQ-4 | Visual descriptions do not state the new silhouette rules. | P3 | Module docstring | Document source necks, branching tongues, loops, seams, and relief marks. |

### Documentation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| DO-1 | “Mechanism-specific” currently overstates the primitive geometry. | P2 | Atlas method | Define exactly what each family’s form communicates. |
| DO-2 | The caveat is correct but too generic to explain local inaccuracies. | P3 | Map note | State that placement and form are interpretive indexes, not extents. |
| DO-3 | The relationship to HEATPLATES is not explicit. | P3 | Atlas README | Identify HEATPLATES and fluid geography as the silhouette precedent. |
| DO-4 | The history should distinguish the first overlay from the character redraw. | P3 | History | Record the redraw after owner approval rather than rewriting prior history. |

### Testing

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| TE-1 | Counting 36 groups does not test visual character. | P2 | Tests | Assert signature classes and multi-part geometries for each family. |
| TE-2 | No test prevents regression to ellipses for all gyres. | P2 | Tests | Assert gyres use paths and directional markers. |
| TE-3 | No test checks every line object has a wide hit target. | P3 | Tests | Compare line-feature groups with `hit` geometry counts. |
| TE-4 | Generated SVG accessibility should be mechanically checked. | P3 | Tests | Assert 36 roles, tab indices, labels, and titles. |

### Process

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| PR-1 | The prior stage was committed before owner visual acceptance. | P3 | Workflow | Treat this redraw as an additive private-preview correction. |
| PR-2 | Visual acceptance criteria were implicit. | P2 | Plan | Define “serious” as distinct, basin-aware, mechanism-readable silhouettes. |
| PR-3 | The richest precedent was not used consistently across the catalog. | P2 | Workflow | Compare every family against fluid geography and HEATPLATES before commit. |
| PR-4 | Browser review should exercise every lens, not only flows. | P3 | Verification | Capture or inspect waters, flows, edges, floor, life, and events. |

### Implementation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| IM-1 | Most improvement can happen entirely in the generated overlay. | P3 | Scope | Preserve Atlas selection and filter code while replacing geometry. |
| IM-2 | Multi-part objects need group-level hover without per-part inconsistency. | P3 | SVG CSS | Style child geometry through the parent feature state. |
| IM-3 | Current line geometry lacks directional variation. | P2 | SVG defs | Add warm/cold arrows and family-specific symbols such as trench teeth. |
| IM-4 | Areas need internal structure to avoid sticker-like fills. | P2 | SVG defs | Add source cores, hatching, shelves, or nested contours by family. |

## BLOCK 3 — SYNTHESIS

```
Overall verdict: NEEDS-WORK

P1 blockers (must resolve before implementation):
  (None -- proceed to implementation)

P2 conditions (must resolve before sign-off):
  - OC-1/PO-3/SV-1 — replace elliptical gyres with directional basin loops.
  - OC-2/PO-1/PO-2/SV-3 — rebuild water masses as source-fed, branching forms.
  - OC-3 — replace diamond gates with geographic section/passage geometry.
  - PO-4 — rebuild OMZs as coast-hugging subsurface wedges.
  - SV-2/AX-2/IM-3/IM-4 — establish family-specific texture and line grammar.
  - AX-1 — preserve generous invisible hit targets for paths.
  - AR-1/AR-3/PR-2 — encode and document the silhouette design contract.
  - CQ-2/TE-1/TE-2 — add structural tests against primitive regression.
  - DO-1/PR-3 — align claims with the richer precedents.

Cross-reviewer consensus:
  The first overlay is geographically located but visually generic. Reviewers
  agree that serious character comes from mechanism-specific topology—source
  necks, spreading tongues, western-intensified loops, meandering seams,
  coast-hugging wedges, and conventional relief marks—not from extra color.

Strongest signal:
  Replace repeated primitives with a unique silhouette signature for every
  feature while retaining the explicit schematic-boundary firewall.
```

## AMEND

1. Add a “Feature silhouette contract” to the province shape-system plan:
   define unique identity, basin/coast relationship, and mechanism-readable
   topology as acceptance requirements. This resolves AR-3 and PR-2.
2. Replace primitive gyres, water-mass capsules, gate diamonds, and OMZ islands
   in `build_atlas_feature_overlay.py` with multi-part, asymmetric geographic
   constructions. This resolves the central cartographic and oceanographic P2s.
3. Extend `analysis/test_atlas.py` with family-signature, accessibility, XML,
   hit-target, and no-elliptical-gyre checks. This prevents the same visual
   regression from returning.
