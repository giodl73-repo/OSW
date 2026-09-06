---
skill: roles-check
topic: osw-22-region-polar-inset
date: 2026-08-29
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 2
verdict: NEEDS-WORK
---

# Roles check — 22-region Mollweide with polar inset

Source commit at review: `556edac` (working tree contains the reviewed,
uncommitted Atlas 08 changes).

## Artifact identification

- Type: cartographic design plus deterministic SVG generator and documentation.
- Primary artifact: `figures/osw-state-projection-mollweide-oceanic.svg`.
- Supporting artifacts: `analysis/build_projection_bakeoff.py`,
  `analysis/build_province_cartogram.py`, `projections/index.html`, `README.md`,
  `HISTORY.md`, and `analysis/test_atlas.py`.
- Domain signals: physical oceanography, derived classification, geographic
  projection, accessibility, public-science communication, provenance, and
  reproducible generation.

## Role selection

| Role | Why selected |
|---|---|
| CURRENT | The artifact names ecological realms and polar/ocean regions. |
| SOUNDER | The map combines derived topology, pinned coastlines, and two projections. |
| CHART | Projection seams, polar insets, boundaries, colors, and labels are central. |
| BEACON | The 11 → 22 → 56 hierarchy is intended as a public explanatory hook. |
| HARBOR | Twenty-two colors, small codes, and hairline modes require redundant access. |
| KEEL | SVGs are generated and the no-multipart promise is an executable contract. |
| LOGBOOK | The vocabulary and milestone are becoming repository-level public claims. |

ORBIT was not selected because this artifact makes no Earth–gas-giant analogy.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The 22 names and boundaries are original subdivisions of approximate nearest-seed cells, but the headline can read as an observed ecological regionalization. | P1 | SVG hierarchy headline; README | Call them **22 contiguous schematic regions** everywhere and state that the names are provisional OSW cartographic constructs, not published Longhurst regions. |
| 2 | “Ecological realm” is not operationally defined; basin × biome membership is categorical rather than a diagnosed physical budget or boundary. | P2 | README; projection page | Define realm as an organizational intersection of the catalog’s basin and biome fields, not a dynamically bounded water mass. |
| 3 | Paired north/south views correctly resist treating all polar water as one geographically continuous cap. | P3 | Polar inset | Preserve the paired views and three-region distinction. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | SVG metadata records the main Mollweide PROJ string but omits the inset Lambert azimuthal equal-area definitions and the 48°N/45°S display cutoffs. | P2 | SVG metadata | Record both inset PROJ strings, central meridians, latitude cutoffs, and the fact that cutoff choice is cartographic. |
| 2 | The 22-region membership, codes, colors, label anchors, realm parentage, and derivation status exist only in Python constants. | P2 | Generator/data contract | Export a versioned CSV or JSON registry and link it from the SVG metadata and repository documentation. |
| 3 | Natural Earth land is pinned by commit and SHA-256, and the map explicitly says it does not reproduce published Longhurst boundary geometry. | P3 | SVG metadata/footer | Keep these receipts adjacent to every generated edition. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The “contiguous” validator checks adjacency in unmasked geographic Voronoi cells, while the displayed map is cut by land and interrupted-projection seams. A continuous source region can therefore appear multipart on the plate. | P1 | Connectivity validator; Mollweide rendering | Either implement land- and seam-aware displayed-component validation or qualify the claim as “topologically contiguous before land masking and projection interruption.” |
| 2 | Twenty-two legend entries at 8 px are too compressed to function as the primary decoding key at normal display size. | P2 | Bottom legend | Increase the legend type and spacing, group it by the 11 parent realms, or provide a companion full-size key. |
| 3 | The 92 px polar circles materially improve orientation but are too small for coastline and state-boundary inspection. | P2 | Polar inset | Increase each polar view and label the projection and latitude extent inside the frame. |
| 4 | Distinct colors plus region codes are substantially clearer than the prior five-ocean and four-biome overlays. | P3 | Main map | Keep the categorical-color experiment as the leading visual grammar. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The plate presents “realm,” “region,” and “state” without defining the difference where readers first encounter them. | P2 | Polar frame and legend heading | Add one short definition: realm = categorical family; region = continuous schematic territory; state = classic province identity. |
| 2 | “Three continuous regions at two ends of Earth” omits that continuity and boundaries are properties of an approximate cartogram. | P2 | Polar inset subtitle | Change to “Three continuous schematic regions in the OSW topology” and retain the two-ends explanation below it. |
| 3 | The 11 → 22 → 56 formulation is memorable and gives the project a much clearer explanatory spine. | P3 | Overall narrative | Preserve this hierarchy after tightening its scientific status language. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Legend text at 8 px and inset labels at 8–9 px are not reliably legible without browser zoom. | P2 | Legend; polar frame | Raise the minimum annotation size and test the SVG at its default rendered width and 200% zoom. |
| 2 | The SVG description mentions only 56 transformed states and white land; it omits the 11/22 hierarchy, polar inset, categorical colors, and hairline state. | P2 | `<desc>` | Provide a concise but complete data-oriented description that differs for hairlines on/off. |
| 3 | Codes redundantly encode color, but no nearby textual alternative lists all 22 regions, their parent realms, and member states in reading order. | P2 | SVG/page alternative | Add an HTML/CSV region directory linked immediately beside the figure. |
| 4 | The existing hairlines on/off mode is a useful redundant comparison and does not rely on animation. | P3 | Projection controls | Preserve it and announce the changed image description when toggled. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Connectivity validation does not test the final land-masked, seam-clipped SVG components, so it cannot enforce the user-visible “no multipart regions” promise. | P2 | `geographic_state_geometry` | Add a rendered-topology test for each region under each projection and explicitly classify seam-created pieces. |
| 2 | Tests assert 22 unique `data-region` values but do not verify 22 unique colors, one marker per region, exact parent realm, or complete registry/schema agreement. | P2 | `analysis/test_atlas.py` | Add a region-contract fixture and cross-check generator constants, SVG attributes, legend entries, colors, markers, and 56 memberships. |
| 3 | Polar tests only search for strings and clip IDs; they do not validate cap projection parameters, cutoff bounds, or nonempty north/south geometry. | P2 | Polar inset tests | Add structural assertions for LAEA parameters, cutoffs, labels, and path counts. |
| 4 | The current suite passes 79 tests; Python compiles cleanly and browser JavaScript syntax-checks. | P3 | Validation run | Keep the offline suite as the default gate and add the new topology checks to it. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new 22-region vocabulary has no dedicated versioned registry or provenance note, making later renames difficult to audit. | P2 | Repository history/data | Add a provisional region registry with version, rationale, parent realm, member states, and replacement policy. |
| 2 | The reviewed work remains uncommitted and includes new untracked generated SVGs; it is not yet a reproducible public release state. | P2 | Git/release state | Keep Atlas 08 labeled private preview until generated files, review, registry, and tests are committed together. |
| 3 | README and history now state the 11 → 22 → 56 hierarchy, but they do not yet foreground that the 22 names are provisional OSW constructs. | P2 | README; HISTORY | Add the provisional naming/evidence class beside the first hierarchy statement. |
| 4 | Project history preserves the path from 11 multipart categories to 22 continuous map units instead of silently rewriting the milestone. | P3 | HISTORY | Retain that decision record. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 2  |  P2 issues: 16  |  P3 notes: 7

Verdict: **NEEDS-WORK**

Top finding: “22 contiguous regions” currently overstates both scientific
status and rendered-map continuity; it is only guaranteed in the unmasked,
pre-projection nearest-seed topology.

Cross-role consensus: CURRENT, CHART, BEACON, HARBOR, KEEL, and LOGBOOK all
require the map to distinguish a provisional schematic topology from observed
or published ecological geography.

## Amendments

1. Add a versioned 22-region registry and change every public claim to **11
   organizational realms → 22 contiguous schematic regions → 56 classic
   province identities**, with the derivation and provisional status adjacent.
2. Make the no-multipart contract match the rendered artifact: validate land
   masking and projection seams, or disclose seam-created visual pieces and
   limit “contiguous” to the pre-projection topology.
3. Enlarge and document the legend/polar views, record both polar LAEA
   projections and latitude cutoffs, and provide a complete text alternative
   for the 22-region membership.
