---
skill: roles-check
topic: guide 11 sea ice polynyas and ocean cavities
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — Guide 11: Sea Ice, Polynyas, and Ocean Cavities

## Artifact identification

- **Artifact type:** public-science guide, controlled ontology, relation graph,
  evidence record, and executable documentation contract
- **Primary artifact:** `guides/11-SEA-ICE-POLYNYAS-AND-OCEAN-CAVITIES.md`
- **Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b`
- **Review target:** current working-tree snapshot on
  `atlas-08-private-preview`; the source commit predates these additions
- **Validation:** `python -m pytest analysis -q` → 389 passed, 10 subtests passed

## Role selection

All eight OSW roles apply. CURRENT reviews phase-change and heat-delivery
physics; SOUNDER reviews measured ice variables and thresholds; CHART reviews
polar boundaries and masked ocean; BEACON reviews public interpretation; HARBOR
reviews text equivalence; KEEL reviews schemas and gates; LOGBOOK reviews status
and history; ORBIT reviews the icy-world comparison.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The guide correctly makes basal melt the end of a multistage heat-delivery chain rather than an inference from nearby warmth. | P3 | Heat must complete a chain | Preserve reservoir, access, gate, circulation, and boundary-layer terms in future budgets. |
| 2 | Initial `fixed` mobility for fast ice and a cavity overstated permanence despite detachment, roof change, and grounding-line migration. | P2 | OBJ072 / OBJ090 | **Resolved:** both now use `evolves`; attachment remains the fast-ice identity test. |
| 3 | Brine rejection is correctly conditional on stratification and is not equated with universal bottom-water formation. | P3 | Freezing and melting | Require depth-resolved density response for any regional formation claim. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Concentration, area, extent, thickness, volume, and edge are explicitly non-interchangeable. | P3 | Cover is not amount | Require product variable IDs and threshold metadata for future detected layers. |
| 2 | Passive-microwave footprint, weather, coast, melt-pond, thin-ice, and pole-gap limitations are visible beside the metric definitions. | P3 | Cover is not amount | Retain native quality flags and masks in implementation receipts. |
| 3 | External anchors remain vocabulary families rather than exact concept identifiers. | P3 | Classification registry | Complete governed IDs before claiming machine interoperability. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The cavity cross-section prevents a floating-shelf footprint from becoming land or missing ocean by default. | P3 | The cavity is an ocean room | Give shelf roof, seabed, and open boundary distinct symbology in maps. |
| 2 | The initial ice-shelf record used surface geometry although a shelf is a thick solid body whose draft roofs a cavity. | P2 | OBJ093 | **Resolved:** geometry changed from `surface` to `volume`. |
| 3 | Ice-edge sharpness is tied to a declared threshold and sensor resolution rather than rendered as a natural hairline. | P3 | Cover is not amount | Show marginal uncertainty or pixel support in polar map views. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “The cavity is an ocean room” is memorable and supported by linked observations and the cross-section. | P3 | The cavity is an ocean room | Use it as the public entry point while keeping the moving-roof qualification adjacent. |
| 2 | Floating shelf loss could be misread as direct full-volume sea-level addition without an explicit distinction from grounded ice. | P2 | Cavity section | **Resolved:** added the floating-displacement and grounded-ice buttressing explanation. |
| 3 | Each mechanism section pairs what the concept shows with what it cannot establish. | P3 | Whole guide | Preserve this structure in future biological/chemical guides. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | All diagrams have adjacent prose that carries the same object relations without relying on layout or colour. | P3 | All schematics | Preserve these canonical alternatives if converted to SVG. |
| 2 | Tables explicitly name identity, geometry, motion, and counterexample fields. | P3 | Object cards | Keep column semantics available at narrow viewport widths. |
| 3 | Symbols, arrows, and shading reinforce but do not solely encode scientific meaning. | P3 | Cross-sections | Provide structured data alternatives for eventual interactive polar layers. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Guide 11 is covered by existence, section, and link-resolution tests. | P3 | `analysis/test_guides.py` | Continue adding guide pages through the shared page registry. |
| 2 | The new `contact_boundary` type and `opens_within` predicate are schema-checked. | P3 | Registry tests | Add relation evidence keys before machine map logic consumes the graph. |
| 3 | The complete offline suite passes: 389 tests and 10 subtests. | P3 | Validation | Keep web refresh outside the default deterministic gate. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, guide index, classification, history, sources, tests, and registries agree on 11 guides, 96 objects, 13 types, and 85 relations. | P3 | Companion artifacts | Update all count-bearing surfaces in one increment. |
| 2 | The history explains why the thirteenth type exists rather than presenting taxonomy growth as arbitrary. | P3 | Project history | Preserve the grounding-line example as evidence the classification can evolve. |
| 3 | No publication, commit, or remote-state claim is made by the guide increment. | P3 | Review scope | Leave release status unchanged until separately authorized. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The analogy compares phase boundaries and heat budgets, not surface appearance alone. | P3 | Planetary connection | Add nondimensional and forcing comparisons before a stronger transfer claim. |
| 2 | Earth’s floating shelves are distinguished from a global icy-moon shell. | P3 | Planetary connection | Keep gravity, rotation, salinity, heat source, and boundary topology explicit. |
| 3 | The comparison defers to Guide 07’s falsifiable protocol. | P3 | Planetary connection | Preserve Guide 07 as the controlling contract. |

## Cross-ontology finding

The initial registry classified the grounding line as a `gradient_boundary`.
CURRENT, CHART, and LOGBOOK converged that this was ontologically false: a
grounded-to-floating contact can be mapped through flexure, hydrostatic, and
remote-sensing evidence, but it is not fundamentally a rapid water-property
gradient. The registry now has a thirteenth type, `contact_boundary`, and the
classification explains why.

Likewise, a lead or polynya is not materially `part_of` the ice. The relation is
now `opens_within`, preserving the topology without calling open water ice.

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 4 (all resolved)  |  P3 notes: 20

Verdict: APPROVED

Top finding: An ice-shelf cavity must be represented as a liquid ocean room
             with an evolving solid roof and an explicit heat-delivery chain.
Cross-role consensus: Polar maps must distinguish material origin, cover
                      measurement, thresholded boundary, and physical process.
```

## Amendments applied

1. Added `contact_boundary` for the grounding line and `opens_within` for leads
   and polynyas, correcting both ontology and topology.
2. Changed cavity and fast-ice mobility to `evolves`, changed ice-shelf geometry
   to `volume`, and clarified that attachment—not permanence—defines fast ice.
3. Added the floating-shelf versus grounded-ice sea-level explanation and kept
   buttressing separate from direct displacement.

## Remaining non-blocking work

- Populate exact governed vocabulary identifiers and per-relation evidence keys.
- Specify a polar map contract before loading concentration, thickness, drift,
  ice draft, grounding-line, or cavity data.
- Require regional observations or validated models for every cavity heat claim;
  Guide 11 is a conceptual grammar, not an Antarctic melt atlas.

