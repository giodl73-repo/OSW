# Plumes, Upwelling, and Vertical Exchange

*A body can rise, a surface can rise, and water can change class—but those are
not the same event.*

**Evidence class:** the diagrams and object cards are concepts, not detected
features. Linked OSW figures are model-derived results with separate receipts.

## Object cards

| Object | What makes it exist? | Primary evidence | What it is not |
|---|---|---|---|
| Buoyant plume | source-tagged water with a density anomaly | source tracer, properties, and three-dimensional extent | every patch of vertical velocity |
| River plume | freshwater delivered from a river or estuary | salinity plus discharge/source context | merely a coastal current |
| Hydrothermal plume | vent-sourced fluid and tracers | temperature, particles, chemistry, and vent relation | all warm deep water |
| Meltwater plume | ice-derived freshwater in an ocean mixture | salinity, tracers, ice geometry, and circulation | any cold polar surface patch |
| Intrusion | property-tagged water spreading laterally near a level | coherent property anomaly and vertical position | the rising plume stem |
| Upwelling | organized upward motion from below | vertical velocity or a continuity-constrained diagnosis | a cold water mass |
| Coastal upwelling | upwelling tied to coast, wind, and offshore surface transport | wind stress, coast geometry, divergence, hydrography | every cold coastline |
| Equatorial upwelling | upwelling tied to cross-equatorial surface divergence | wind, divergence, vertical structure | one fixed water type |
| Ekman pumping | wind-stress-curl contribution to vertical motion | curl, rotation, and declared sign convention | all mechanisms of upwelling |
| Isopycnal heave | vertical displacement of a density surface | repeated density-surface depth | irreversible mixing |
| Turbidity current | downslope density flow involving sediment | velocity, turbidity, excess density, and terrain | a passive discoloration plume |

## Body, motion, and conversion

```text
SOURCE-TAGGED BODY           VERTICAL-MOTION FIELD          CLASS CONVERSION

river / vent / ice          water velocity has w > 0      parcel properties change
        │                           ▲                              │
        ▼                           │                              ▼
     PLUME                    UPWELLING                 TRANSFORMATION / MIXING

identify by origin          identify by motion         identify by property flux
and properties              and continuity             across a class boundary
```

A plume answers **which water is this?** Upwelling answers **how is water moving
vertically here?** Transformation answers **is water entering or leaving a
temperature, salinity, or density class?** The three may coincide, but no one
diagnosis proves the others.

NOAA explicitly defines upwelling as a process in which deeper water rises
toward the surface ([NOAA upwelling](https://oceanservice.noaa.gov/facts/upwelling.html)).
The source identity of a plume instead survives through freshwater, chemical,
particle, or other property signatures.

## The life of a buoyant plume

```text
 source            turbulent rise              neutral level       ambient current
   ●                    ▲ ▲ ▲                         ┌─────── intrusion ───────►
   │                   /  │  \                       │
   └── buoyancy ─────►/   │   \── entrains ─────────┘
                     ambient seawater
```

Buoyancy can make source water rise, but entrainment rapidly adds ambient
water, dilutes the source signature, and increases plume volume. In a stratified
ocean the mixture can reach neutral buoyancy and spread laterally as an
intrusion. The rising stem, neutral layer, and later advection are stages of one
history, not one interchangeable shape.

NOAA PMEL documents this sequence for hydrothermal plumes: buoyant rise,
ambient-water entrainment, neutral buoyancy, and lateral dispersal
([PMEL plume study](https://www.pmel.noaa.gov/pubs/outstand/bake1538/bake1538.shtml)).
River plumes have different source chemistry and boundary geometry and may
become rotating coastal currents in their far field
([Horner-Devine et al. review](https://www.annualreviews.org/doi/10.1146/annurev-fluid-010313-141408)).

## Three upwelling geometries

```text
COAST                         EQUATOR                       OPEN-OCEAN CURL

land │ surface ─────►         ◄──── surface   surface ────►       wind-stress curl
     │      ▲                       away from 0°                         │
     │      │                            ▲                              ▼
     │ deeper water                      │                        Ekman pumping
                                      subsurface                         ▲
```

- **Coastal upwelling** requires a coast-relative wind and surface-transport
  geometry. Which wind direction is favorable depends on hemisphere and coast
  orientation; a memorized compass arrow is not a portable test.
- **Equatorial upwelling** follows divergence of the near-surface Ekman response
  across the equator under suitable winds.
- **Ekman pumping or suction** is diagnosed from wind-stress curl with an
  explicit rotation and sign convention. It can occur away from both coast and
  equator.

Each can raise colder or nutrient-rich water, but the thermal response depends
on the source depth and stratification. A cold SST tongue is supporting evidence,
not the definition. Kessler's Pacific review makes the equatorial divergence and
stratification dependence explicit
([NOAA PMEL review](https://www.pmel.noaa.gov/pubs/outstand/kess2580/cycle.shtml)).

## Heave is not mixing

```text
BEFORE                         AFTER REVERSIBLE HEAVE

surface ───────────            surface ───────────
warm      ρ1                   warm  ρ1
ρ = 1026  ─────────            ρ = 1026  ───────       ↑ surface moved
cold      ρ2                   cold  ρ2

parcel stays on density surface        no necessary cross-density flux

DIAPYCNAL TRANSFORMATION

ρ1 parcel ── heat / freshwater / mixing ──► ρ2 class membership changes
```

An isopycnal can move vertically because of waves, eddies, or large-scale
adjustment while parcels remain approximately on that density surface. A sensor
at fixed depth then records a temperature change even without local irreversible
mixing. Conversely, transformation is diagnosed as flux across a property-class
boundary. Depth-coordinate vertical velocity, isopycnal displacement, and
diapycnal velocity must therefore be named separately.

Modern transformation budgets likewise separate surface forcing, interior
mixing, and isopycnal overturning
([NOAA-hosted Southern Ocean study](https://repository.library.noaa.gov/view/noaa/50558/noaa_50558_DS1.pdf)).
A recent decomposition frames the remaining attribution problem directly as
separating reversible isopycnal heave from irreversible diabatic transformation;
OSW uses that distinction conceptually, not as a claim that one operational
diagnostic has become universal
([Han 2026 preprint](https://arxiv.org/abs/2605.23277)).

## Turbidity current is a special warning

```text
slope / canyon head
      \   dense sediment-water mixture
       \████████████──────────────► downslope
        \       · · · suspended sediment plume above
         \________________________________ deep basin
```

A turbidity current is organized by excess density and gravity along terrain.
It can entrain water, suspend sediment, and produce an overlying plume, but the
entire event need not be a passive water plume. Monterey Canyon observations
found both moving water-saturated sediment and sediment-laden water
([USGS experiment](https://www.usgs.gov/news/large-underwater-experiment-shows-turbidity-currents-are-not-just-currents-involve-movement)).

## The decisive tests

1. Name the primary claim: source-tagged body, velocity structure, displaced
   interface, or property-class conversion.
2. For a plume, declare the source tracer, ambient endmember, dilution rule,
   three-dimensional boundary, and observation time.
3. For upwelling, state how vertical velocity was measured or inferred and how
   horizontal divergence and boundary conditions close continuity.
4. For Ekman pumping, provide wind stress, spatial curl, Coriolis convention,
   resolution, and uncertainty; do not substitute wind direction alone.
5. Track density-surface depth to separate heave from fixed-depth temperature
   change, and diagnose cross-isopycnal flux before claiming transformation.
6. For heat transport, combine temperature with mass or volume flux, area,
   reference temperature, and boundary orientation. `w > 0` alone is not watts.
7. Test whether terrain, tides, ambient currents, entrainment, and stratification
   alter the apparent object or split it into stages.

## OSW consequences

OSW should not paint every cold coastal anomaly as a fixed “coldmass.” A cold
surface band could reflect upwelling, lateral advection, surface heat loss,
isopycnal heave, or several mechanisms at once. The map can display the thermal
state immediately, but a mechanism layer needs the tests above.

The same rule protects the Nordic and Antarctic stories. Water may rise along a
slope or canyon, enter a meltwater plume, mix, spread as an intrusion, and cross
a gate; those are linked objects, not aliases. The present monthly ORAS5 Nordic
budget does not expose native mixing, diffusion, ice-ocean exchange, or
assimilation increments, so its unresolved remainder cannot be relabeled as
vertical transformation.

[See the Nordic remainder context](../figures/osw-m4-oras5-nordic-remainder-context-2018.svg) ·
[inspect its receipt](../research/osw-m4-oras5-nordic-remainder-context-2018.json) ·
[return to transformation and overturning](05-TRANSFORMATION-AND-OVERTURNING.md) ·
[inspect the Guide 10 evidence record](../signals/discover/websearch/ocean-plumes-upwelling-vertical-exchange-websearch-2026-09-05.md)

## Planetary connection

Buoyant plumes, convective motions, waves, and vertically displaced interfaces
also occur in other rotating fluids. But an atmospheric bright spot is not a
water-source tracer, pressure-coordinate ascent is not automatically
cross-isentropic transformation, and remote cloud motion need not reveal deep
vertical mass flux. Compare mechanisms only after matching coordinates,
stratification, forcing, and observables.

[Apply the planetary comparison protocol](07-OCEANS-AND-GAS-GIANTS.md).

## Common mistakes

- Calling upwelling a cold water mass instead of a motion field.
- Inferring vertical velocity from SST colour alone.
- Treating an upwelling index as direct observation of the whole circulation.
- Equating isopycnal heave with irreversible diapycnal mixing.
- Treating every plume as hot, fresh, rising, or surface-visible.
- Ignoring dilution when estimating a source flux from far-field plume volume.
- Calling a lateral intrusion the original undiluted source water.
- Treating a turbidity current as only a passive suspended-sediment patch.
- Converting `wT` to a heat-budget conclusion without geometry and closure.

## Next

[Sea Ice, Polynya, and Ocean Cavities](../CLASSIFICATION.md#next-research-layers)
will distinguish material phase, cover fraction, openings, and liquid rooms
beneath floating ice.

[Field Guide index](README.md) · [Waves, Tides, and Oscillations](09-WAVES-TIDES-AND-OSCILLATIONS.md) · [Classification](../CLASSIFICATION.md)
