---
skill: roles-check
topic: pelagos-projection-laboratory
date: 2026-08-29
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED
---

# PELAGOS projection laboratory native-role review

Source commits: `92345ec` (`Add PELAGOS projection laboratory`) and
`dbe8165` (`Project defined heatmass areas in bakeoff`)

## Artifact identification

- Type: experimental cartographic projection bakeoff, deterministic SVG
  generator, responsive comparison page, method, provenance, and tests.
- Domain: physical oceanography, geodesy, conceptual cartography,
  accessibility, reproducibility, and release-state governance.
- Scope: compare Spilhaus, Oceanic Interrupted Goode Homolosine, and an
  experimental South-Pacific-centered Lambert equal-area aspect named
  PELAGOS using one shared schematic fluid overlay.

## Role selection

All eight native roles are selected. CURRENT reviews the pathway vocabulary;
SOUNDER the source and transformation boundary; CHART the projection claims;
BEACON the “new projection” language; HARBOR the non-visual comparison; KEEL
the generator and tests; LOGBOOK the private-experiment status; and ORBIT the
risk that circular belts invite an unsupported gas-giant analogy.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every candidate receives the same schematic warm pools, anomaly, currents, buried inflow, gates, and ACC, so the comparison does not tune mechanisms to favor PELAGOS. | P3 | generator | Keep shared geographic inputs locked across candidates. |
| 2 | The closed ACC ring expresses connectivity but is explicitly not observed transport, a material wall, or a heat budget. | P3 | SVG metadata and method | Retain the evidence firewall in exported crops. |
| 3 | Arctic inflow and tropical gateways are now included, making the declared pathway criteria physically relevant to the compared maps. | P3 | shared overlay | Review any added pathway against depth and mechanism before inclusion. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Natural Earth geometry is pinned by commit, URL, public-domain status, and source-response SHA-256. | P3 | builder and SVG metadata | Preserve checksum rejection on regeneration. |
| 2 | Projection specifications are registered separately from ocean evidence, preventing mathematical sources from being misread as support for heat claims. | P3 | Source Register P1–P3 | Maintain this source-class separation. |
| 3 | The three projected overlays are labeled schematic rather than observational, modeled, or threshold-derived. | P3 | page method | Add a distinct data receipt before projecting observed rasters. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Spilhaus is correctly presented as conformal and Oceanic Goode and PELAGOS as equal-area, with their different failure modes adjacent. | P3 | cards and scorecard | Keep area, shape, and continuity as separate properties. |
| 2 | PELAGOS declares its exact center and Sahara antipode rather than hiding the projection singularity. | P3 | method firewall | Add distortion indicatrices before public promotion. |
| 3 | Square, interrupted-wide, and circular frames now correspond to the actual candidate geometries, and all use ghost coastlines plus redundant feature styles. | P3 | generated SVGs | Add numeric reference-point fixtures before changing orientation. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The page leads with the design question before branding PELAGOS as the leading hypothesis. | P3 | hero | Preserve problem-before-name ordering. |
| 2 | “New viewpoint, established mathematics” and “not a newly derived projection equation” accurately bound the novelty claim. | P3 | method | Repeat this qualification in public summaries. |
| 3 | Each candidate pairs what it reveals with where it fails, so the bakeoff reads as inquiry rather than a staged victory. | P3 | candidate verdicts | Keep both halves together in excerpts. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Projection properties and tradeoffs are available in headings, prose, and a semantic table independently of the maps. | P3 | page structure | Preserve the textual comparison as candidates evolve. |
| 2 | Each SVG has title/description metadata and each embedded image has candidate-specific alternative text. | P3 | SVG and HTML | Update both descriptions with feature changes. |
| 3 | Candidate links have visible focus, legend categories use shape and dash as well as color, and the layout collapses to one column. | P3 | CSS and legend | Add automated keyboard and zoom coverage later. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | One pinned Python environment and command regenerate all three SVG artifacts from the same verified input. | P3 | requirements and analysis README | Record PROJ version if byte-for-byte portability becomes required. |
| 2 | The default suite passes 65 tests and locks files, operators, source hash, novelty language, and shared feature classes. | P3 | `test_atlas.py` | Add projected coordinate fixtures and a checksum-failure fixture. |
| 3 | Python compilation, JavaScript syntax, relative-link validation, diff checks, and Edge rendering pass. | P3 | local gate | Add an offline HTML validator when available. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | PELAGOS is labeled a private experiment and leading hypothesis, not an adopted atlas projection or new observational result. | P3 | status and footer | Require a separate promotion decision. |
| 2 | README navigation, analysis instructions, source register, atlas route, generator, outputs, and tests changed together in the source commit. | P3 | repository diff | Keep future projection increments atomic. |
| 3 | No screenshot, downloaded Natural Earth source, local machine path, secret, remote change, or new incompatible license entered the repository. | P3 | public boundary | Recheck before any push. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The circular PELAGOS composition can resemble planetary bands, but the artifact makes no claim that the ACC or tropical reservoirs are gas-giant jets. | P3 | scope | Review planetary reuse as a separate comparison artifact. |
| 2 | Equal-area projection is an Earth cartographic property and is not offered as a dynamical similarity metric. | P3 | scorecard | Keep map geometry separate from nondimensional physics. |
| 3 | The useful transfer is visual—continuous bands and hidden depth—not evidence of shared forcing, stratification, or material boundaries. | P3 | future use | State the compared property and falsifier before linking to OCEANBELTS. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 0 | P3 notes: 24

Verdict: **APPROVED**

Top finding: PELAGOS is a defensible leading projection hypothesis because it
preserves relative area and moves the unavoidable singular edge onto land,
while declaring both that choice and the resulting African shape distortion.

Cross-role consensus: CURRENT, CHART, BEACON, HARBOR, and KEEL agree that the
strength of the experiment is not the circular beauty alone; it is the shared
overlay, explicit projection properties, visible failure modes, and textual
equivalent. Those controls must precede any default-atlas promotion.

## Amend

The highest-severity findings are non-blocking P3 hardening opportunities:

1. Add numeric projection reference points and local distortion diagnostics
   before changing the PELAGOS center or promoting it publicly.
2. Specify interaction, labels, hit testing, keyboard use, and observed-raster
   resampling before integrating PELAGOS into the primary atlas map modes.
3. Treat any OCEANBELTS reuse as a new mechanism comparison, not an automatic
   consequence of the circular projection.

## Owner-feedback amendment — defined areas

Owner review found that the first projection bakeoff encoded heatmasses as
wide centerline strokes rather than defined areas. Commit `dbe8165` replaces
that shortcut with shared irregular geographic polygons and inset shelf
contours. A focused recheck through all eight native lenses found:

| Role | Recheck | Severity |
|---|---|---|
| CURRENT | Polygon boundaries remain explicitly schematic and do not become fronts, walls, heat content, or transport. | P3 |
| SOUNDER | The change adds no observational data and leaves the pinned coastline and evidence classes intact. | P3 |
| CHART | Area-preserving candidates now compare actual filled areas; Spilhaus visibly exposes its areal distortion. | P3 |
| BEACON | “Defined area” no longer conflicts with a ribbon mark, and the method states that boundaries are not observed thresholds. | P3 |
| HARBOR | Filled silhouette, solid edge, and dashed inset shelf provide redundant non-color structure. | P3 |
| KEEL | Tests require three polygons and shelves in every candidate and reject the former 45-pixel stroke encoding. | P3 |
| LOGBOOK | The corrective source commit is named here and in `PREVIEW-STATUS.md`; experiment status is unchanged. | P3 |
| ORBIT | The correction changes Earth-side cartographic grammar only and adds no planetary mechanism claim. | P3 |

Focused verdict: **APPROVED** with 0 P1 and 0 P2 findings. The original
24-finding review and its promotion conditions otherwise remain in force.
