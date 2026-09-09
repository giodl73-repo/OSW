---
skill: roles-check
topic: heat-continent-grammar
date: 2026-08-29
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED
---

# Heat-continent visual-grammar role review

Source commit: `454c79c` (`Redraw heat reservoirs as fluid continents`)

## Artifact identification

- Type: conceptual cartographic design, generated SVG artifacts, alternative
  text, method documentation, and regression test.
- Domain: physical oceanography, explanatory cartography, accessibility,
  reproducibility, and repository governance.
- Scope: redraw the persistent Indo-Pacific and seasonal Western Hemisphere
  warm-pool reservoirs as irregular fluid territories while retaining the
  round, dashed treatment of the transient Northeast Pacific Blob.

## Role selection

All eight installed roles are selected because the conceptual map is the
atlas's interpretive foundation. CURRENT checks whether the sharper boundary
overstates physical permanence; SOUNDER checks the evidence boundary; CHART
checks the new visual grammar; BEACON checks the continent metaphor; HARBOR
checks non-visual equivalents; KEEL checks deterministic generation; LOGBOOK
checks repository truth; and ORBIT checks that the Earth-side vocabulary does
not silently strengthen a planetary analogy.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The sharper reservoir outlines improve categorical recognition but could be mistaken for fronts or material boundaries if detached from their caveats. | P3 | SVG and atlas panel | Keep “schematic, permeable, moving regions” on the map and the moving-edge limit beside each selected reservoir. |
| 2 | The redraw changes only the explanatory shape grammar; it does not alter the assigned depth, clock, mechanism, or evidence class. | P3 | builder and zone catalog | Require a separate evidence review before deriving any footprint from observations. |
| 3 | The inset shelf contour suggests internal structure without asserting a thermocline depth, temperature threshold, or integrated heat content. | P3 | reservoir symbols | Do not label the contour with physical units unless it becomes a measured layer. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The Natural Earth geometry remains pinned to the same commit and SHA-256; only original conceptual overlays changed. | P3 | SVG metadata and method | Preserve the checksum test and rebuild command. |
| 2 | Documentation explicitly says that the reservoir edges were not measured or thresholded. | P3 | atlas method | Add a new source receipt if a future version derives boundaries from SST or heat content. |
| 3 | The observational OISST and Argo artifacts are untouched, preventing a design change from being mistaken for new data. | P3 | Git diff | Continue reviewing conceptual and observed layers as distinct evidence classes. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Irregular silhouettes, firmer edges, and inset contours now distinguish reservoirs from the soft circular anomaly at map-reading scale. | P3 | conceptual map | Preserve this shape distinction independently of color. |
| 2 | Removing the reservoir glow makes the designed coastline legible without changing the equirectangular basemap or seam treatment. | P3 | SVG render | Recheck antimeridian continuity whenever either split Pacific path changes. |
| 3 | Land remains drawn above the reservoir layer, making archipelagos and basin separation visually legible. | P3 | layer order | Keep the land-over-overlay ordering in regenerated figures. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Heat continent” now has a visual referent rather than applying the same circular form used for a heat blob. | P3 | headline, map, and selected-zone panel | Retain “continent-like reservoir” rather than presenting heat continent as a formal oceanographic class. |
| 2 | The method immediately qualifies the metaphor as a mechanism vocabulary, not a fixed or impermeable geography. | P3 | atlas README | Keep the qualification near any exported map caption. |
| 3 | The round dashed anomaly provides a simple contrast a non-specialist can repeat accurately: reservoir versus event. | P3 | legend and map | Avoid equating persistence with immobility. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Reservoir and anomaly categories differ by silhouette, edge style, and fill treatment rather than color alone. | P3 | SVG visual grammar | Preserve all three redundant encodings. |
| 2 | The image alternative text now names irregular reservoirs and round dashed anomalies. | P3 | atlas HTML | Keep the text directory as the detailed non-visual route. |
| 3 | The full-size SVG remains linked below the responsive embedded map. | P3 | conceptual actions | Test the full-size route at high zoom after future layout changes. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Both static and interactive SVGs are generated from one builder and the same pinned coastline input. | P3 | build pipeline | Never hand-edit only one generated SVG. |
| 2 | A regression test requires named heat-continent groups, multiple irregular paths and shelves, and preservation of the transient Blob ellipse. | P3 | `test_atlas.py` | Extend the test if new reservoir classes are introduced. |
| 3 | The complete offline suite passes 63 tests; JavaScript syntax, Python compilation, and diff checks pass. | P3 | local gate | Keep these checks in the documented release path. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The change is recorded as a conceptual-grammar refinement rather than a new observational result or numbered data release. | P3 | commit and review | Mention it in the next release summary without relabeling the evidence. |
| 2 | The method, generated artifacts, HTML alternative text, and regression test changed together. | P3 | source commit | Keep generated outputs and their source in one commit. |
| 3 | No local path, private-project reference, screenshot, downloaded source file, or new license obligation enters the repository. | P3 | public boundary | Preserve that boundary before pushing. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The redraw makes no new claim about gas-giant belts, atmospheric depth, or material boundaries. | P3 | scope | Review any planetary reuse separately. |
| 2 | A stronger Earth-side metaphor could invite false equivalence if shown beside Jupiter without the mechanism limits. | P3 | future comparison | Compare rotation, stratification, forcing, and boundary conditions before transferring the symbol. |
| 3 | The useful transferable idea remains categorical visual grammar, not that ocean reservoirs and gas-giant bands are physically identical objects. | P3 | interpretation | State the compared property in any future cross-planet figure. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 0 | P3 notes: 24

Verdict: **APPROVED**

Top finding: the new irregular silhouettes make persistent or seasonal
reservoirs legibly different from transient blobs, while repeated nearby
language prevents the sharper outline from becoming a claim of a measured,
fixed, or impermeable boundary.

Cross-role consensus: CURRENT, CHART, BEACON, and HARBOR agree that the gain
comes from redundant shape grammar plus an adjacent permeability caveat; both
must travel with the map.

## Amend

The highest-severity findings are non-blocking P3 hardening opportunities:

1. Preserve the map-level “schematic, permeable, moving” line and zone-level
   moving-edge caveat in every export or crop.
2. Add an explicit measured-boundary evidence contract before replacing any
   conceptual reservoir silhouette with a data-derived threshold.
3. Recheck antimeridian continuity, land-over-overlay order, alternative text,
   and non-color distinction whenever the conceptual SVG grammar changes.
