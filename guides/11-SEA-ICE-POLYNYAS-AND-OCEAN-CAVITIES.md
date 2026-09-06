# Sea Ice, Polynyas, and Ocean Cavities

*The polar ocean can be covered, cracked, exposed, roofed, and still moving
underneath.*

**Evidence class:** diagrams and object cards are concepts. A mapped ice field,
edge, opening, thickness, or cavity becomes a detected state only with a named
product, date, grid, threshold, vertical geometry, and uncertainty.

## Object cards

| Object | Identity test | Geometry and motion | Do not confuse with |
|---|---|---|---|
| Sea-ice cover | fraction of ocean surface occupied by frozen seawater | evolving surface field | thickness, volume, or an ice shelf |
| Sea-ice floe | discrete connected piece of sea ice | mobile surface body | a thresholded satellite pixel |
| Pack ice | assemblage of mobile sea-ice pieces | drifting partial cover | coast-attached fast ice |
| Fast ice | sea ice attached to coast, seabed, or grounded ice | relatively fixed cover | an ice shelf of land-glacier origin |
| Ice-edge front | strong transition at the cover margin | evolving curve or frontal zone | all of the marginal ice zone |
| Lead | elongated fracture/opening within compact ice | short-lived pathway | a broad persistent polynya |
| Polynya | persistent open-water or thin-ice area where cover is expected | event-like surface region | every temporary crack |
| Ice shelf | floating extension or composite of land-origin glacier ice | thick moving solid roof | sea ice formed from ocean water |
| Grounding line | transition from grounded to floating glacier ice | evolving boundary curve | coastline or calving front |
| Ice-shelf cavity | seawater volume beneath floating shelf ice | three-dimensional ocean room | the solid shelf itself |
| Brine rejection | salt transfer to seawater during ice formation | phase-change process | guaranteed deep-water formation |
| Basal melting | melt at the submerged underside of floating ice | boundary transformation | surface melt or calving |

## Cover is not amount

```text
one satellite cell

┌──────────────────────┐      concentration = ice-covered fraction
│██████████            │      area          = Σ(cell area × fraction)
│████████              │      extent        = Σ(full cells above threshold)
│                      │      thickness     = vertical ice dimension
└──────────────────────┘      volume         = area integrated with thickness

ice edge = contour chosen from a declared concentration threshold
```

These are related measurements, not synonyms. A common passive-microwave extent
rule counts a whole cell once concentration reaches 15%, so extent can include
open water inside qualifying cells. Thickness is a separate and generally less
complete observation. The threshold, sensor footprint, weather filters, coast
mask, melt ponds, thin ice, and pole gap all affect the apparent edge.

[NSIDC explains area versus extent](https://nsidc.org/learn/ask-scientist/what-difference-between-sea-ice-area-and-extent)
and reports that passive-microwave edge location can differ by tens of kilometres
from higher-resolution systems
([NSIDC data limits](https://nsidc.org/sea-ice-today/about-data)).

## A nested grammar of frozen cover

```text
SEA-ICE COVER
│
├── mobile assemblage ─────────► PACK ICE ── contains ──► FLOES
├── attached to boundary ──────► FAST ICE
├── narrow fracture/opening ───► LEAD
└── persistent opening ────────► POLYNYA
```

A floe is a material piece; pack and fast ice describe mobility and attachment;
lead and polynya describe openings. These labels can overlap in time without
being interchangeable. A lead can refreeze, widen, or close as ice deforms. A
polynya persists because winds export new ice or ocean heat prevents/erodes ice.

WMO nomenclature gives leads elongated fracture geometry and polynyas greater
stability. NSIDC likewise distinguishes narrow, mechanically opened leads from
larger, longer-lived polynyas
([NSIDC sea-ice science](https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice)).

## A polynya is both opening and process site

```text
LATENT-HEAT / ICE-PRODUCTION POLYNYA       SENSIBLE-HEAT / OCEAN-HEAT POLYNYA

cold air removes heat                       warmer water reaches surface
new ice forms ── wind exports it             ocean heat delays or melts ice
salt rejected to ocean                       open water vents heat upward
```

This distinction concerns the dominant maintenance mechanism, not two perfectly
sealed natural categories. Both expose ocean to atmosphere, exchange heat and
moisture, support ecosystems, and may contain new or thin ice. Brine production
can raise near-surface density, but whether convection reaches the bottom
depends on stratification, duration, freshwater, mixing, and geometry.

## The cavity is an ocean room

```text
 grounded ice        grounding line            floating ICE SHELF
█████████████████████│████████████████████████████████████  calving front
bedrock ____________ │\       moving roof / basal melt       │
                     │ \                                 ↕ gate
                     │  \  ICE-SHELF CAVITY                │ open ocean
                     │   \ current → mixing → plume ───────►│
seafloor ____________│____\______ridge / channel____________│
```

The shelf is solid floating ice; the cavity is liquid seawater beneath it. The
grounding line is where grounded glacier ice begins to float. The calving front
is the seaward shelf edge. A cavity may have narrow entrances, deep channels,
boundary layers, tides, intrusions, mixing, freezing, and melting—so it can be
studied with the same gates and control volumes used elsewhere in OSW, provided
the moving roof and phase-change fluxes are included.

Because an ice shelf is already floating, its loss does not directly add its
full displaced volume to sea level. Its larger sea-level importance is indirect:
the shelf can buttress grounded glacier flow, so shelf thinning or collapse can
allow land-origin ice to enter the ocean faster
([NSIDC ice-shelf significance](https://nsidc.org/learn/parts-cryosphere/ice-shelves/why-ice-shelves-matter)).

Direct Ross Ice Shelf observations resolve basal and benthic boundary layers,
interleaving, tidal modulation, mixing, melting, and refreezing
([Stewart et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7382223/)).
This is why a cavity cannot be represented as blank land or one temperature.

## Heat must complete a chain

```text
offshore reservoir
      │
      ▼
slope / shelf access ─► cavity entrance ─► internal circulation ─► boundary layer
      terrain + fronts       gate flux          tides + mixing          │
                                                                         ▼
                                                                  basal melt/freeze
```

Warm water outside a shelf is not yet melt delivered to ice. Heat must cross
slope and shelf barriers, enter the correct cavity, survive mixing and
transformation, reach the ice–ocean boundary layer, and transfer across it.
The result depends on water properties, volume transport, geometry, turbulence,
and the local pressure-dependent freezing point.

At Totten Ice Shelf, observations used warm-water inflow and cavity heat
transport to show sufficient support for measured basal melt
([Rintoul et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5161426/)).
The broader review literature emphasizes that ocean heat crosses multiple
dynamical barriers before the final boundary-layer exchange
([Davis & Nicholls 2025](https://www.annualreviews.org/content/journals/10.1146/annurev-marine-040323-074354)).

## Freezing and melting transform adjacent water

```text
FREEZING                             MELTING

seawater → fresher ice + brine       ice + ocean heat → fresher meltwater
                         ↓                                  ↑ buoyant mixture
                 saltier/denser water                 stratification can increase
```

Brine rejection is a salt flux, not a descending object and not automatic
bottom-water formation. It can promote convection if the density increase
overcomes ambient stratification. Melting supplies freshwater and consumes
heat; the resulting mixture can rise as a meltwater plume, entrain ambient
water, and spread laterally.

[NSIDC traces brine expulsion](https://nsidc.org/learn/parts-cryosphere/sea-ice/science-sea-ice),
while a NOAA-hosted ice-margin review shows why strong stratification can stop
deep convection
([Muench et al.](https://repository.library.noaa.gov/view/noaa/9516/noaa_9516_DS1.pdf)).

## The decisive tests

1. State ice origin: frozen seawater, land-origin glacier ice, or a composite.
2. Name the measured variable: concentration, area, extent, thickness, freeboard,
   draft, age, drift, or volume.
3. Declare the concentration threshold and spatial resolution used for any edge,
   extent, lead, or polynya detection.
4. For fast versus pack ice, test attachment and drift rather than visual texture.
5. For a polynya, record geometry, persistence, ice production/export, ocean
   heat, and uncertainty in the dominant maintenance mechanism.
6. For a cavity, map roof draft, seabed, grounding line, calving front, entrances,
   and every control-volume boundary.
7. For basal melt, close heat and freshwater terms or state which are missing;
   surface ice concentration is not subsurface heat delivery.
8. For brine-driven convection, test whether the density flux overcomes local
   stratification and reaches the claimed depth.

## OSW consequences

OSW's present Nordic seasonal-context layer uses monthly ORAS5 sea-ice
concentration, a 15% extent rule, and concentration-times-thickness as an
ice-volume proxy. Those three views answer different questions. Their weak
same-year correlations with the unresolved heat-budget remainder do not measure
ice–ocean heat exchange or prove that ice is dynamically irrelevant.

For Antarctica, an ocean-state map should treat ice shelves as roofs over ocean,
not continents painted white. A future cavity atlas needs bathymetric entrances,
ice draft, grounding-line provenance, water-column properties, velocity, tides,
and melt/freeze exchange. It should then apply OSW's gate and control-volume
contracts rather than drawing an arrow from offshore warmth directly to melt.

[See Nordic seasonal context](../figures/osw-m4-oras5-nordic-remainder-context-2018.svg) ·
[inspect its receipt](../research/osw-m4-oras5-nordic-remainder-context-2018.json) ·
[read the Antarctic mechanism boundary](../OCEANREALMS.md) ·
[inspect Guide 11 evidence](../signals/discover/websearch/sea-ice-polynyas-ocean-cavities-websearch-2026-09-05.md)

## Planetary connection

Icy moons can also contain oceans beneath solid ice, but Antarctica is not a
scale model of a global subsurface ocean. Earth has an atmosphere-facing ocean,
salty seawater, floating shelves attached to grounded continental ice, open
boundaries, and strong topographic gateways. An icy moon may have a global ice
shell, different gravity and rotation, distinct heat sources, and no open-air
ocean. Compare phase boundaries and heat budgets only after those differences
are explicit.

[Apply the planetary comparison protocol](07-OCEANS-AND-GAS-GIANTS.md).

## Common mistakes

- Treating concentration, extent, area, thickness, and volume as synonyms.
- Drawing a crisp ice edge without declaring threshold and resolution.
- Calling every opening a polynya or every linear opening a persistent lead.
- Confusing sea ice formed from seawater with a glacier-fed ice shelf.
- Treating fast ice as immobile forever rather than attached for the stated time.
- Painting an ice-shelf cavity as land or as missing ocean data.
- Assuming brine rejection always creates bottom water.
- Inferring basal melt from nearby SST or surface ice concentration alone.
- Treating calving, surface melt, and basal melt as one loss process.
- Ignoring the moving roof and pressure-dependent freezing point in a cavity budget.

## Next

The next guide should connect biological and chemical objects—oxygen layers,
hypoxia, carbon, nutrients, blooms, and ecosystems—to the physical carrier,
boundary, motion, and transformation grammar established here.

[Field Guide index](README.md) · [Plumes, Upwelling, and Vertical Exchange](10-PLUMES-UPWELLING-AND-VERTICAL-EXCHANGE.md) · [Classification](../CLASSIFICATION.md)
