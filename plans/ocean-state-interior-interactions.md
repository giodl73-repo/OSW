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

That absence is now backed by a provider-catalogue
[capability audit](../research/ocean-state-sant-current-geometry-oras5-capability-audit-2026-09-12.json):
the public ICDC ORCA025 listing has T/S, horizontal-current, surface, and
storage products but no vertical-velocity product, and the candidate
`vovecrtz` files/subcatalog return not found. A vertical term now requires a
separately sourced and compatibly custodial product, rather than another
reinterpretation of the existing fields.

The follow-on [vertical-process source audit](../research/ocean-state-sant-vertical-process-source-audit-2026-09-12.json)
finds no directly joinable 2018 native-`w` source. Copernicus’ current global
analysis/forecast product documents `wo`, but it is a distinct grid and
configuration; the 2018 multiyear alternative documents a reconstructed, not
distributed native, vertical velocity. Both are bridge or sensitivity
candidates only, never additive ORAS5 budget terms. The next actual vertical
experiment therefore needs a user-custodied source receipt and an explicit
geometry/time/variable/assimilation bridge review.

The same manifest now includes twelve monthly native fields for net downward
surface heat flux, net upward freshwater mass flux, and column heat content.
The [open surface/storage account](../research/ocean-state-sant-current-geometry-surface-storage-2018.json)
area-integrates them over current SANT membership and retains every successive
column-heat-content difference without forming a residual. It is useful
forcing and storage evidence, not a closed control volume: matched lateral and
vertical fluxes, mixing/diffusion, and compatible temporal conventions remain
required before any convergence or closure statement.

A [partial native perimeter screen](../research/ocean-state-sant-current-geometry-partial-perimeter-2018.json)
now measures every available in-domain SANT membership face (474 faces; 26,587
wet face-levels in each sampled month) with adjacent T/S collocation. It also
reports the 176 SANT sides cut by the north, west, and east Drake-subset edges.
Those missing sides rule out a closed lateral account, so the recorded gross
exchange and signed partial fluxes must not be called convergence or a state
budget.

For a horizontal term that really is bounded, a geometry-only
[16×16 closed interior box](../research/ocean-state-sant-closed-box-selection-current-geometry-v1.json)
and three one-cell controls were selected before any fields were inspected.
Its [horizontal account](../research/ocean-state-sant-closed-box-horizontal-account-2018.json)
uses all 64 native U/V faces, plus co-located T/S and the local surface/storage
context. This admits horizontal advective convergence as *one term* (the
negative of net outward horizontal flux), not total convergence: vertical
velocity, mixing/diffusion, model tendencies, assimilation/restoring, and
compatible storage intervals remain absent.

The same fixed geometry now has a distinct [inventory-endpoint screen](../research/ocean-state-sant-closed-box-inventory-change-screen-2018.json): four
column-heat-content snapshots and three endpoint differences for the primary
box and each one-cell control. This makes the observed stock changes explicit,
but does not convert them to tendencies or compare them to fluxes: the
monthly-field timestamp and averaging convention have not been shown to define
a matched tendency interval. It is therefore an inventory record, not a
residual or closure calculation.

A [provider time-metadata audit](../research/ocean-state-sant-temporal-support-audit-2018.json)
now checks seven source fields for all four sampled months against their
custodied URLs. They share midmonth time coordinates and `ave(x)` metadata, in
line with the [ICDC ORAS5 monthly-field inventory](https://icdc.cen.uni-hamburg.de/thredds/fileServer/ftpthredds/EASYInit/oras5/DOCS/ORAS5_ICDC_variable_list_1x1.pdf).
The local derivatives dropped those time coordinates. The probed source
metadata have no explicit time-bounds field, and `interval_write` reports 31
days even in February 2018. Thus the inventory's so-called endpoints are
monthly-mean samples, not instantaneous endpoint states. Their differences
remain descriptive changes between monthly means, not matched tendencies.

A matching [density-stratum inventory](../research/ocean-state-sant-closed-box-density-inventory-2018.json) now computes TEOS-10 sigma-zero on every valid native
T-cell volume in those boxes, then records the occupancy of four predeclared
numeric density bins and their endpoint differences. These are property-space
inventory observations, not water-mass labels or transformation rates: no
density-class boundary flux, vertical transfer, or mixing term is available.

The paired [density-boundary screen](../research/ocean-state-sant-closed-box-density-boundary-screen-2018.json) partitions all 64 native horizontal faces by
those same bins using adjacent-cell T/S face means. It supplies the horizontal
density-bin boundary terms needed for a future class budget, but is not itself
a class-conversion result: vertical and mixing density-class terms, matched
temporal support, and assimilation/restoring treatment remain missing.

The [density-boundary collocation challenge](../research/ocean-state-sant-density-boundary-collocation-sensitivity-2018.json)
repeats that screen on the identical native faces, wet levels, velocities, and
fixed bins, assigning face density from the upstream T cell instead of the
adjacent-cell mean. Across the primary box's four sampled months, 0.21–0.65% of
valid face levels change bin. The largest primary bin-wise net-flux change is
0.848 Sv (August 2018), even though the total flux is unchanged by bin
reassignment. The three displaced controls are included in the receipt. Thus
the centered class flux is a method-dependent screen, especially when a small
net bin flux is compared with much larger opposing gross flows. Neither
collocation yields a transformation rate or resolves the missing vertical,
mixing, assimilation, and matched-time terms.

A compact [twelve-month native field archive](../research/ocean-state-sant-closed-box-monthly-fields-2018.json)
now extends the fixed box and all three controls through every month of 2018.
It stores only the 20×19-cell neighborhood needed for their faces and
reproduces the four earlier custodied months exactly. The resulting
[monthly density-boundary series](../research/ocean-state-sant-density-boundary-monthly-series-2018.json)
shows why the four-month pilot was insufficient for a seasonal claim. In July,
the primary 27.0–27.5 sigma-zero bin has +1.539 Sv net outward under centered
collocation and +1.168 Sv under upstream collocation; all three displaced
controls retain outward centered signs. In August, that bin's small centered
+0.048 Sv becomes about −0.800 Sv upstream. These are monthly-mean products of
velocity and tracer fields on a fixed horizontal perimeter. The result is a
descriptive method-sensitive flux series, not a native mean advective flux,
density-class conversion, matched inventory tendency, or total budget. July's
control agreement also means it is a neighborhood-scale screen, not evidence
that the primary box marks a uniquely defined physical boundary.

The same compact source now drives a [twelve-month density inventory](../research/ocean-state-sant-density-inventory-monthly-series-2018.json)
for the fixed box and controls, with exact reproduction of the four earlier
inventory samples. The primary 26.5–27.0 sigma-zero bin is empty from July
through October; the 27.0–27.5 bin occupies 13.60–16.40% of valid box volume
across the year. The Observatory places these stock shares beside the separate
horizontal boundary screen. Differences between monthly means and products
of monthly-mean velocity and tracer fields still cannot be combined as a
class-volume budget or attributed to a density transformation.

A post hoc [density-cutoff challenge](../research/ocean-state-sant-density-cutoff-sensitivity-2018.json)
shifts all three numerical σ₀ cutoffs together by −0.1 and +0.1 kg/m³ while
keeping the boxes, native fields, faces, and collocation choices fixed. The
zero-shift run reproduces the annual inventory and boundary receipts. July's
middle-high bin stays net outward in every shifted scheme, under both
collocation choices, for the primary box and all three controls. In the
primary box its centered July flux ranges from +1.066 to +2.075 Sv across the
cutoffs. August remains sign-sensitive. The baseline 26.5–27.0 bin's July–
October absence is cutoff-dependent: raising the cutoffs gives that shifted
bin positive occupancy in each of those months. This challenge strengthens
the bounded July horizontal-screen result but does not identify a water mass,
transformation mechanism, or closed budget.

The next fixed [July repeat-year selection](../research/ocean-state-sant-july-repeat-selection-v1.json)
chose the two nearest earlier Julys in the same ICDC ORAS5 monthly archive,
2016 and 2017, before reading their T/S/U/V values. A compact
[source receipt](../research/ocean-state-sant-july-repeat-fields-2016-2017.json)
keeps the same native box neighborhood, and the
[three-July sign screen](../research/ocean-state-sant-july-repeat-sign-screen-2016-2018.json)
applies every existing cutoff shift and collocation method to the primary box
and three controls. The strict predeclared rule **fails**: July 2016 and 2018
pass, while the 2017 east control has −0.021 Sv under upstream collocation at
the baseline cutoffs. The primary box itself remains outward in all three
Julys under the tested choices. This one near-zero control failure prevents a
claim that the sign uniformly repeats across the neighborhood. Three Julys
from one assimilative product also cannot validate a persistent physical
boundary or explain a density transformation.

The [preselected July 2017 ensemble challenge](../research/ocean-state-sant-2017-july-ensemble-selection-v1.json)
then fixed all four remaining ORAS5 members before reading their native
T/S/U/V values. The [compact member source](../research/ocean-state-sant-2017-july-ensemble-fields.json)
and [five-member sign screen](../research/ocean-state-sant-2017-july-ensemble-sign-screen.json)
apply the same four boxes, three cutoff schemes, and two collocation choices.
**Zero of five members pass** the strict rule. Opa0 and opa3 have outward
primary baseline fluxes but each fails one east-control case; opa1, opa2, and
opa4 have inward primary baseline fluxes. The east-control baseline upstream
flux ranges from −0.892 to +1.343 Sv and changes sign across members. This
exposes substantial within-product sensitivity, including the primary-box
baseline sign, so the July 2017 outward result cannot be treated as an
ensemble-stable feature. Members of one assimilative reanalysis are not
independent-product replication or a formal uncertainty interval.

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
