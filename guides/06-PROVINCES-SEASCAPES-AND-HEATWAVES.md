# Provinces, Seascapes, and Heatwaves

*A province partitions space. A seascape class describes current habitat. A
heatwave identifies an anomaly through time.*

## Three maps that can occupy the same pixel

```text
REFERENCE GEOGRAPHY       CURRENT STATE             EVENT

Longhurst province        dynamic seascape          marine heatwave
"which region?"           "what habitat now?"       "how unusual now?"
fixed/mean boundary        moving class              threshold + duration
```

## Object cards

| Object | Membership rule | Coverage | Time behavior |
|---|---|---|---|
| Basin/sea | topography and geographic convention | exhaustive at chosen hierarchy | mostly fixed |
| Longhurst province | ecological/environmental reference | exhaustive pelagic partition | mean boundaries |
| Dynamic seascape | classified satellite/model state | exhaustive where data valid | changes frequently |
| Marine heatwave | temperature above a local percentile for a minimum duration | event pixels only | begins, moves, merges, ends |
| Heatmass | OSW exploratory label for spatially coherent heat state | not yet canonical | definition-dependent |

## The 56-province breakthrough—and its limit

Longhurst's classic system organizes four biomes into 56 biogeochemical
provinces. It provides the ocean with an intelligible, state-like reference
geography. The boundaries were designed as average ecological geography, not
permanent walls.

[Reygondeau et al. 2013](https://agupubs.onlinelibrary.wiley.com/doi/10.1002/gbc.20089)
made the partition dynamic using bathymetry, chlorophyll, surface temperature,
and salinity. [NOAA MBON Seascapes](https://coastwatch.star.nesdis.noaa.gov/cwn/products/seascape-pelagic-habitat-classification.html)
now routinely distributes dynamic pelagic habitat classes.

## Why every molecule cannot have one universal state

An exhaustive map requires mutually exclusive membership under one declared
rule. But scientific ocean objects overlap:

```text
pixel at 64°N, 13°W
├── Longhurst province       (reference ecology)
├── Atlantic Water           (properties)
├── Atlantic current core    (motion)
├── front                    (gradient)
├── heatwave                 (time anomaly, perhaps)
└── control volume           (budget geometry)
```

The answer is not to choose one forever. It is to make these selectable layers
with clear legends and object contracts.

## Marine heatwaves are events, not warm places

A persistently warm tropical sea is not necessarily experiencing a marine
heatwave. The threshold is local and seasonal: unusually warm relative to that
place and time, sustained for a declared duration. Subsurface heatwaves may have
vertical structures invisible in SST alone
([Elzahaby et al. 2023](https://www.nature.com/articles/s41467-023-42219-0)).

Eddies, fronts, boundary currents, surface forcing, and mixing can all shape
heatwave evolution. A heatwave atlas therefore needs event identity rules for
birth, adjacency, merger, split, and termination.

## The decisive tests

### Province map

- Does every valid ocean cell have exactly one membership?
- Are boundary gaps and overlaps absent?
- Is the hierarchy explicit?
- Is the map reference geography or detected current state?

### Event map

- What baseline, percentile, seasonality, and duration define the event?
- Is it surface-only or three-dimensional?
- How are connected pixels joined across time?
- How are splits and mergers handled?

## Common mistakes

- Treating a mean province boundary as a wall that water cannot cross.
- Calling every warm region a marine heatwave without a local baseline.
- Mixing ecological classes, physical water masses, and circulation regions in
  one legend without showing that their memberships overlap.
- Assuming an exhaustive partition is therefore the uniquely correct ocean map.
- Hiding invalid or unobserved cells by assigning them to the nearest class.

## OSW example

The Province Atlas supplies a recognizable exhaustive reference layer. The
Nordic jet maps supply transport objects that cross that reference geography.
They should be overlaid, not collapsed into one classification.

[Open the Province Atlas](../figures/osw-province-atlas-coastal-states.svg) ·
[open the Nordic face map](../figures/osw-m4-oras5-nordic-face-heat-map-2018.svg)

## Next

[Oceans and Gas Giants](07-OCEANS-AND-GAS-GIANTS.md) asks which of these object
ideas survive when the lower boundary and material change radically.
