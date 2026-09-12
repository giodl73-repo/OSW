# Ocean-state interiors and interactions

Status: sparse contents ledger plus a separately versioned bounded kinematic pathway screen

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
inspection. The pilot now adds the SANT static bathymetric-column profile as a
separately timed reference overlay; it may otherwise add only:

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

## Current source-custody gate and separate pathway result

The archived Drake ORAS5 state files contain native `u` and `v`, but the
native-grid province assignment used for the contents pilot was not retained.
On 2026-09-12 the live Marine Regions WFS response hashed to
`a67485038ad698b304ed60d721cf8e5295f9fff01762e8591db6b04dae73198e`, not the
`0b8439605ff29d07f8c11f98e32c4f9ff5f0dc11df03b6c400f298c5c1544b77` response
recorded by that pilot. Therefore no SANT internal-pathway calculation may be
generated from the live geometry and presented as compatible with the 2018
contents account. The exact [source-custody audit](../research/ocean-state-interior-source-custody-audit-2026-09-12.json)
sets the two admissible recovery paths.

One of those paths is now implemented as a **separate, unjoined source
family**: a pinned current-geometry native SANT assignment and a bounded
surface, monthly-mean ORAS5 kinematic screen. The assignment retains a
run-length native-cell membership derivative, source and mesh checksums, and a
one-cell cardinal interior guard. It selects three longitudinal seeds at the
median guarded latitude *before velocity inspection*, together with every
available one-cell cardinal control. It advances those fourteen starts for
five days in February, May, August, and November 2018 using a declared
T-cell velocity proxy.

All 14 starts remained within the guarded discrete SANT support for each of
the four monthly screens; the three primary trajectories have nonzero
continuous five-day displacements and retain co-located Eulerian surface
temperature samples. The same predeclared cardinal controls supply local
relative-separation and temperature-contrast records: for example, the western
May screen contracts by 0.375 km on average while the central controls separate
by 10.728 km. These are local kinematic screen outcomes, not horizontal flux
divergence or convergence. This establishes only that these declared
monthly-mean kinematic and temperature-co-occurrence supports can be evaluated
in the new source family. It does not establish parcel thermodynamics, material
retention, transport, a persistent pathway, vertical exchange, or a bridge to
the archived contents account. The precise
[native assignment](../research/ocean-state-interior-sant-current-geometry-assignment-2026-09-12.json)
and [pathway screen](../research/ocean-state-interior-sant-pathways-current-geometry-2018.json)
are the evidence records.

The same assignment now supports a local [vertical-structure screen](../research/ocean-state-interior-sant-vertical-structure-current-geometry-2018.json): the
three fixed seeds are sampled at the nearest native 0, 100, 200, and 1,000 m
T-level midpoints in each month. The screen records vertical temperature
contrasts and horizontal-velocity differences per metre; e.g., the central
seed's February 0--100 m contrast is 3.351 °C. This completes the supported
`overlies`/vertical-structure relation, not `transfers_between_layers`.

The [dynamics synthesis](../research/ocean-state-intra-state-dynamics-synthesis-sant-2018.json)
is the completion record for this research slice. It covers occupancy,
co-occurrence, vertical structure, lateral paths, and local relative motion as
bounded supported relations; it records vertical transfer, interior
convergence, transformation, and event perturbation as unsupported with their
specific acquisition gates. It validates the two source families without
numerically joining them.

## Physical-source-family expansion

The current-geometry SANT family now has matching four-season ORAS5 native
T/S/U/V support: the existing custodied temperature and horizontal velocities
are checksum-bound to the new assignment, and newly receipted practical
salinity is added on the same T cells. Its
[source-family manifest](../research/ocean-state-sant-current-geometry-physical-source-family-2018.json)
records finite salinity support and the negative vertical-velocity probe.

The resulting [TEOS-10 density-structure screen](../research/ocean-state-interior-sant-density-structure-current-geometry-2018.json)
uses local latitude/longitude, midpoint-depth pressure, absolute salinity,
conservative temperature, and sigma-zero. It supports numeric density-stratum
occupancy and vertical density structure only. Its fixed bins are not named
water masses, and without class-volume fluxes it does not establish
transformation. The ICDC source has no probed native `vovecrtz` file, so it
still cannot support vertical transfer.

The same manifest now includes twelve monthly native fields for net downward
surface heat flux, net upward freshwater mass flux, and column heat content.
The [open surface/storage account](../research/ocean-state-sant-current-geometry-surface-storage-2018.json)
area-integrates them over current SANT membership and retains every successive
column-heat-content difference without forming a residual. It is useful
forcing and storage evidence, not a closed control volume: matched lateral and
vertical fluxes, mixing/diffusion, and compatible temporal conventions remain
required before any convergence or closure statement.

## Exit evidence for the first slice

- [x] a machine-readable [state-interior ledger schema](../research/ocean-state-interior-ledger-schema-v1.json)
  and local fixture;
- [x] one pre-registered [SANT × 0–200 m × August 2018 pilot receipt](../research/ocean-state-interior-ledger-sant-201808.json);
- [x] a textual [State Interior stage](../exchange/?stage=interior) that
  distinguishes contents, overlays, internal links, boundary links, and
  unknowns without color-only meaning;
- [x] tests that reject incompatible geometry, depth, time, source, or evidence
  class joins; and
- [x] a separately versioned, checksum-bound native membership assignment and
  velocity-independent seed/control pathway screen; and
- [x] a separately versioned local vertical temperature-structure and
  horizontal-velocity-shear screen, explicitly excluding vertical transfer; and
- [x] a checksum-validated relation-by-relation dynamics synthesis that retains
  all unsupported mechanisms and their evidence gates; and
- [x] an explicit no-closure/no-causation boundary next to every transfer-like
  result.
