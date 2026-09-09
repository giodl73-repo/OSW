# OSW — Causal Heat Experiments

**Status:** qualitative perturbation matrix · observation-class synthesis

**Purpose:** ask what should change when one control on the Southern Ocean heat
pathway is perturbed, while refusing universal signs where coupled feedbacks
permit opposite regional responses.

## The causal object

A useful experiment must distinguish the imposed change from the response:

```text
external control
  -> density / pressure / geometry response
  -> current and front response
  -> heat-transport response
  -> storage and water-mass response
  -> sea-ice / land-ice interaction
  -> feedback onto density and circulation
```

Temperature is only one node. A surface cooling can coexist with subsurface
warming; increased local melting can produce freshwater that suppresses melting
downstream; a stronger wind can energize eddies instead of proportionally
accelerating the mean current.

## Experiment 1 — Shift the westerly winds poleward

**Perturbation:** move the Southern Hemisphere westerly-wind maximum toward
Antarctica while holding the initial ocean geometry fixed.

**Candidate chain:**

```text
poleward wind shift
  -> altered Ekman transport and coastal sea-surface slope
  -> Antarctic Slope Front shoals or weakens in susceptible sectors
  -> warmer deep water reaches shallower shelf depths
  -> subsurface shelf heat content rises
  -> greater opportunity for ice-shelf heat delivery
```

An idealized ocean-model experiment produced subsurface coastal warming of as
much as 4 °C in selected sectors, mostly through horizontal and vertical
advection, after a poleward wind shift
([Spence et al., 2014](https://doi.org/10.1002/2014GL060613)). This is a
mechanism demonstration, not a circumpolar forecast: coastline, slope-current
structure, bathymetry, sea ice, and the background density field determine the
regional response.

**Discriminating observations:** wind-stress latitude, coastal dynamic height,
slope-current velocity, isopycnal depth, 200–700 m temperature, and cross-shelf
heat transport measured together.

**Failed shortcut:** `stronger/poleward wind -> uniformly stronger ACC -> one
temperature response`.

## Experiment 2 — Add cold, fresh meltwater

**Perturbation:** add freshwater with its physically consistent latent and
sensible heat exchanges at the location and depth where ice melts.

The first-order density effect can be counterintuitive:

```text
cold + fresh water rises toward the surface
  -> salinity reduction can dominate density
  -> lighter surface cap and stronger stratification
  -> less vertical exchange with warmer water below
  -> surface remains cool while subsurface heat accumulates
```

There is no violation of thermodynamics. Melting consumes heat locally. The
later subsurface warming arises because the freshwater changes circulation and
reduces upward heat loss, not because cold water creates energy.

But the sign is geographically conditional. A 2026 circumpolar
ocean–sea-ice–interactive-ice-shelf model found competing feedbacks:

- in dense-shelf regions, warming lightened shelf water, admitted more warm
  water beneath ice shelves, and amplified melting;
- westward-transported meltwater freshened downstream shelves and obstructed
  some warm-water intrusions, producing a negative feedback.

In that model the positive melt feedback accounted for about two-thirds of the
increase in total ice-shelf melt, but the regional negative feedback remained
essential ([Youngs et al., 2026](https://doi.org/10.1038/s41561-026-01975-6)).
That fraction belongs to the experiment, not to Antarctica under every forcing
scenario.

**Discriminating observations:** freshwater source and depth, salinity and
density profiles, mixed-layer depth, vertical heat flux, dense shelf-water
formation, along-shelf freshwater transport, and warm-water intrusion rate.

**Failed shortcut:** `freshwater always insulates` or `freshwater always opens
the warm-water gate`.

## Experiment 3 — Strengthen or weaken stratification directly

**Perturbation:** change the vertical density gradient without initially moving
the coast or shelf break.

| Change | Immediate tendency | Possible heat consequence | Why the sign can reverse |
|---|---|---|---|
| stronger near-surface stratification | suppress vertical mixing and convection | retain heat below; cool/freshen surface | altered currents may also reduce offshore heat supply |
| weaker stratification | increase vertical exchange | vent subsurface heat upward | mixing can also deliver heat toward an ice boundary |
| stronger dense-water production | increase sinking and bottom-water export | ventilate/cool shelves | compensating exchange can draw warmer deep water shoreward |
| weaker dense-water production | reduce deep ventilation | retain subsurface heat | reduced overflow exchange may also weaken on-shelf heat supply |

The outcome cannot be inferred from a temperature profile alone. Salt, density,
velocity, sea-ice formation, and boundary transports are part of the same
experiment.

## Experiment 4 — Alter a ridge, trough, or canyon

**Perturbation:** deepen, shoal, add, or remove one resolved bathymetric feature
while holding the external forcing fixed.

```text
bathymetric change
  -> altered pressure support and potential-vorticity pathway
  -> jet steering / overflow / eddy-generation change
  -> localized change in cross-front or cross-shelf transport
  -> downstream heat-content response
```

A trough aligned across the shelf break can provide a route for warm deep
water; a ridge can block one depth range while generating eddies or internal
waves that enhance exchange elsewhere. “Barrier” and “mixing source” are not
mutually exclusive descriptions of topography.

**Discriminating observations:** full-depth velocity and hydrography upstream,
over, and downstream of the feature; bottom pressure; turbulence; and a closed
section heat budget.

**Failed shortcut:** `ridge blocks heat` or `canyon admits heat` without depth,
flow direction, stratification, and time dependence.

## Experiment 5 — Close Drake Passage

**Perturbation:** install an idealized continent-scale, full-depth barrier. A
surface boom, shallow sill, or partial-depth obstruction is a different
experiment.

```text
topology changes from circumpolar to bounded
  -> continuous ACC path becomes impossible
  -> fronts and gyres reorganize
  -> overturning, winds, sea ice, and heat pathways adjust
  -> regional ice forcing changes over decades
  -> grounded ice integrates the forcing over centuries to millennia
```

This perturbation changes almost every downstream control simultaneously. It
is therefore powerful for demonstrating the importance of topology but weak
for isolating one local heat-transfer mechanism.

**Discriminating model hierarchy:** ocean-only, ocean–sea-ice,
ocean–atmosphere–sea-ice, and finally coupled dynamic-ice-sheet experiments
using the same barrier geometry. Differences between levels are part of the
result.

**Failed shortcut:** `no ACC -> tropical water directly reaches the ice -> all
Antarctica melts`.

## Perturbation matrix

| Lever | Front geometry | Cross-front exchange | Subsurface storage | Ice response | Confidence ceiling |
|---|---|---|---|---|---|
| poleward wind shift | sector-dependent slope/front displacement | eddy + mean flow both adjust | can rise rapidly on susceptible shelves | increased exposure is plausible | regional model mechanism |
| more meltwater | stronger surface stratification in many regimes | vertical exchange often weakens; lateral pathways change | often increases below surface | positive locally, negative downstream possible | competing coupled feedbacks |
| weaker stratification | weaker vertical barrier | vertical mixing increases | may vent or redistribute | sign depends on destination of mixed heat | budget required |
| bathymetric change | jet/pathway relocates | concentrated at feature and downstream | regional redistribution | depends on shelf/cavity connection | geometry-specific |
| Drake closure | circumpolar fronts cease to be circumpolar | global reorganization | large regional changes | warming and ice loss likely; total melt unresolved | idealized climate counterfactual |

## Required controls

Every experiment should freeze:

1. the perturbation geometry, amplitude, ramp time, and duration;
2. the reference climate and initial stratification;
3. which components are interactive: atmosphere, sea ice, ice shelves,
   icebergs, and grounded ice;
4. conservation of freshwater, salt, momentum, and latent/sensible heat;
5. grid resolution and representation of eddies, troughs, cavities, and mixing;
6. diagnostic sections and volume boundaries before outcomes are viewed;
7. regional results separately from circumpolar means.

## Reversal tests

A causal interpretation is stronger if it survives these sign challenges:

- Can the surface cool while the subsurface warms?
- Can melt increase locally but decline downstream?
- Can a stronger wind increase eddy energy more than mean transport?
- Can a blocking ridge also create a mixing hot spot?
- Can sea ice retreat rapidly while grounded land ice remains for millennia?

If the answer is forced to “no” by the vocabulary rather than determined from
the coupled budget, the model of the heat zone is too simple.

## Working conclusion

> The sign of an Antarctic heat feedback belongs to a location, depth, pathway,
> and time interval—not to the word “warming,” “freshening,” or “barrier” by
> itself.
