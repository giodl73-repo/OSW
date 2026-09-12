# Ocean-state interiors and interactions

Status: definition and first-pilot contract; no interior process is yet admitted

Date: 2026-09-12

## The missing concept

An **ocean state** is a versioned horizontal reference geography. An **ocean
column address** is that geography crossed with one declared depth interval.
Neither is a water mass, a sealed container, or a dynamically uniform volume.

**Intra-state interaction** means a declared relationship, transfer, or
co-occurrence *within one named state × depth support × time support*. It must
not mean “anything visible inside the polygon.” Every record has a type,
direction where applicable, support, method, evidence class, and limitation.

The state is the stable address; dynamic objects and processes are overlays.

```text
state reference × depth address × valid time
        ├── contents          what is sampled inside
        ├── overlays          what feature/regime intersects it
        ├── internal links    how two interior supports relate
        └── boundary links    what crosses a declared edge or gate
```

## What is already complete enough to reuse

| Layer | Current admitted result | What it does not supply |
|---|---|---|
| Horizontal row | 54 source-backed Longhurst V4 footprints, 128 shared linear edges, and a separate legacy 56-name directory | physical state identity or material boundaries |
| Vertical column | five bathymetry-truncated address bands, sampled volume ledger, and hypsometric fingerprints | water-mass, mixed-layer, or dynamical-regime identity |
| State contents | 96 ORAS5 temperature distribution passports for six Drake-sector states × four depth bands × four 2018 months | salinity, density, oxygen, heat content, or state-wide dynamics |
| Cross-state interaction | one preselected 16-face `SANT--SSTC` model pilot, with 127 other edges still physically unknown | a general exchange network or zoning revision |
| Event occupancy | a surface heatwave footprint/lineage can be located in state addresses | heat delivery, inventory change, or internal causal pathway |

Thus row and column are finished as **reference and geometric-accounting
primitives**. They are not finished as a physical ocean-state model.

## Interaction vocabulary

Do not collapse these into one generic “interaction” edge.

| Class | Relation | Minimal evidence | Explicit non-claim |
|---|---|---|---|
| Occupancy | `overlays` / `contains` | feature geometry and state/depth/time intersection | material containment or cause |
| Co-occurrence | `coexists_with` | matched supports for two observed/derived fields | coupling or delivery |
| Vertical structure | `overlies` / `intersects` | declared depth supports or measured profile intersection | vertical exchange |
| Vertical transfer | `transfers_between_layers` | vertical velocity/diapycnal flux or a closed, compatible budget | that a residual is mixing or entrainment |
| Lateral interior pathway | `connects_within` | trajectory, tracer, or velocity field plus declared seeds/destinations/control | retention, transport, or causation |
| Interior convergence | `accumulates_in` / `diverges_from` | closed control-volume geometry with matched terms | open-edge transport or temperature tendency |
| Transformation | `changes_class` | property-space class definition and a diagnosed volume flux | merely changing temperature at fixed depth |
| Event interaction | `perturbs` | matched before/during/after account with a declared event identity | permanent state revision or event causation |

`moves_across` remains a boundary relation. A feature that spans a state edge
gets two occupancy records and, only with independent evidence, a boundary
transfer record.

## First implementable interior account

Start with a **state interior ledger**, not a fluid-dynamics claim. Its unit is
one immutable record:

```text
geometry edition × state × depth support × valid interval × source/method
```

For each unit, record separately:

1. **inventory/contents:** property distribution and support;
2. **overlay memberships:** dynamic feature, water-mass candidate, front,
   eddy, event, or regime intersection, with intersection type;
3. **internal links:** only relations whose support is wholly inside the state;
4. **boundary links:** separately receipted edge/gate records; and
5. **change/shock/revision:** compatible time comparison, event attachment, or
   source/method revision lineage.

No scalar “state health,” “interaction score,” or composite dynamism index is
permitted. Unknown is a valid result. Different depth, time, source, or
geometry editions cannot be joined without an explicit bridge.

## First data-backed pilot

Use the already custodied Drake ORAS5 subset before acquiring another global
product. Pre-register one of the six supported states and one month before
inspection. The pilot may add only:

- temperature contents by the existing four depth supports;
- static bathymetry/column overlays;
- any declared interior velocity/pathway screen whose seeds, termination,
  temporal support, and displaced controls stay inside the state; and
- explicit links from the state to its separately bounded `SANT--SSTC` edge
  pilot where applicable.

It may not call a temperature distribution a water mass, infer vertical mixing
from a tendency/residual, infer convergence from one open edge, or publish an
interior transport total without closed geometry and compatible native fields.

## Required decisions before a dynamic interior pilot

1. Choose the canonical quantitative state edition: retain the 54-footprint
   address as canonical, or define a governed 56/54 bridge. `NPSE` and `OCAL`
   cannot receive invented V4 footprints.
2. Define the smallest permitted interior support: native cell, declared
   subregion, trajectory seed/destination set, or closed control volume.
3. Define whether an internal pathway is a kinematic screen, tracer pathway,
   or measured transport; each has a different evidence class.
4. Choose a property progression: temperature first; salinity then density;
   oxygen and heat content only with their missing inputs and conventions.
5. Declare controls for any internal pathway or convergence claim: displaced
   seeds/regions, time alternatives, and where possible a second product.

## Exit evidence for the first slice

- a machine-readable state-interior ledger schema and local fixture;
- one pre-registered pilot state/month/support with a receipt;
- a textual state page that distinguishes contents, overlays, internal links,
  boundary links, and unknowns without color-only meaning;
- tests that reject incompatible geometry, depth, time, source, or evidence
  class joins; and
- an explicit no-closure/no-causation boundary next to every transfer-like
  result.
