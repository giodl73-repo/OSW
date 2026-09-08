# Ocean Column Address

*A surface place tells us where a water parcel is horizontally. An ocean-column
address adds where it is vertically without pretending that depth alone tells
us what kind of water it is.*

## The address

OSW uses two coordinates for every valid wet volume:

```text
OCEAN COLUMN ADDRESS = HORIZONTAL REFERENCE × DEPTH BAND

horizontal reference                 vertical reference
Longhurst province (or declared H)   one declared pelagic depth band
              │                                  │
              └──────────── address ─────────────┘

example: NADR × mesopelagic [200, 1,000 m)
```

This is **reference geography**, not a detected water mass, current, habitat,
or heat state. The horizontal coordinate may use the 56-province directory or
another explicitly named partition. Extending a surface province downward is
an OSW indexing operation; it does not assert that the province's surface
ecology remains valid at depth.

## OSW pelagic-depth edition 1

OSW adopts this familiar five-band convention for its first complete vertical
reference. Depth is positive downward from the dataset's declared vertical
reference surface. The exact machine-readable contract is
[ocean-column-address-v1.json](../research/ocean-column-address-v1.json).

| Band | OSW interval | Plain-language cue |
|---|---:|---|
| Epipelagic | 0–<200 m | sunlit upper ocean |
| Mesopelagic | 200–<1,000 m | twilight ocean |
| Bathypelagic | 1,000–<4,000 m | deep ocean |
| Abyssopelagic | 4,000–<6,000 m | abyssal ocean |
| Hadalpelagic | ≥6,000 m to seafloor | trenches and deepest water |

These names and cutoffs follow the five-zone presentation used by
[NOAA Ocean Exploration](https://oceanexplorer.noaa.gov/static/news/exploration-extras/24-national-ocean-month/welcome.html)
and NOAA's [light-zone explainer](https://oceanservice.noaa.gov/facts/light_travel.html).
They are useful reference bands, not universal physical discontinuities.
Published schemes differ: one recent global three-dimensional assessment uses
1,000–3,500 m and 3,500–6,000 m for its bathypelagic and abyssopelagic realms
([Friedman et al. 2024](https://www.nature.com/articles/s41467-024-47975-1)).
Every OSW layer must therefore record the vertical edition or its exact bounds.

## A complete covering, precisely stated

For a wet point at depth `z`, edition 1 assigns exactly one depth band using
half-open intervals. The final interval includes the local seafloor limit.
Shallow columns simply end: a 90 m shelf column contains only epipelagic water.
Land, ice, and solid seabed are not silently converted to ocean, and a missing
or invalid cell remains unclassified rather than being filled from its neighbor.
A **wet voxel** is one three-dimensional data cell that the declared land,
bathymetry, and validity masks identify as ocean water.

This gives OSW the state-map property we wanted:

```text
every valid wet voxel
        │
        ├── exactly one declared horizontal reference membership
        └── exactly one edition-1 depth-band membership
                         ↓
                  one column address
```

The sea surface and seafloor are zero-thickness boundaries, not additional
water-volume bands. A dataset's vertical coordinate may use depth, pressure,
or model levels; conversion and cell bounds must be declared, and pressure is
not silently relabeled as an equal number of metres. CF conventions
likewise distinguish dimensional vertical coordinates and require their units
and positive direction to be identifiable
([CF vertical coordinates](https://cfconventions.org/Data/cf-conventions/cf-conventions-1.2/build/ch04s03.html)).

## The physical ocean overlays the address

An address answers **where**. A column regime answers **what the water is doing
there**. Several regimes may occupy or cross one address:

| Overlay | Diagnosed from | Why it cannot replace the address |
|---|---|---|
| Mixed layer | small property difference from a reference depth | depth changes with season, forcing, and criterion |
| Thermocline | strong vertical temperature gradient | may be weak, multiple, seasonal, or displaced |
| Halocline | strong salinity gradient | need not coincide with the thermocline |
| Pycnocline | strong density gradient | depends on temperature, salinity, and equation of state |
| Isopycnal layer | chosen density surfaces | surfaces slope through fixed depth bands |
| Water mass | property/tracer signature and history | may cross bands and occur in disconnected patches |
| Bottom boundary layer | flow and mixing influenced by the seabed | follows bathymetry rather than one fixed depth |

Mixed-layer depth is explicitly method-dependent. A widely used climatology,
for example, diagnoses it relative to 10 m using either a 0.2 °C temperature
difference or a 0.03 kg m⁻³ potential-density difference
([de Boyer Montégut et al. 2004](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004JC002378)).
The criterion, reference depth, variable, and observation time belong beside
any mixed-layer map.

Near the bottom, friction and turbulence mediate exchanges of momentum, heat,
and material between the seabed and ocean interior; the layer depends on
currents, waves, tides, buoyancy forcing, and stratification
([Trowbridge and Lentz 2018](https://www.annualreviews.org/content/journals/10.1146/annurev-marine-121916-063351)).
It is therefore a diagnosed physical overlay, not “the deepest depth band.”

## Object card

| Attribute | Ocean column address |
|---|---|
| Defined by | one declared horizontal partition plus one declared depth-band edition |
| Geometry | three-dimensional reference volume, locally truncated by bathymetry |
| Boundary | conventional horizontal edges and exact depth intervals |
| Coverage | exhaustive over valid wet volume under the declared inputs |
| Time behavior | fixed until its horizontal or vertical edition changes |
| Does not establish | water-mass identity, ecological continuity at depth, motion, heat content, transport, or mechanism |

## Decisive tests

1. Name the horizontal partition and version.
2. Name the vertical edition and give exact bounds and endpoint rules.
3. Declare vertical datum or coordinate, bathymetry, wet mask, and treatment of
   partial cells.
4. Demonstrate exactly one address for every valid wet voxel and none for land
   or solid seabed.
5. Keep missing/unobserved separate from a scientifically classified state.
6. Attach physical overlays with their own variables, thresholds, times, and
   uncertainty.

## Common mistakes

| Mistake | Correction |
|---|---|
| The five bands are natural walls. | They are a declared reference convention. |
| A Longhurst province continues ecologically to the seabed. | Only its label is extruded for indexing. |
| Mesopelagic means thermocline. | One is a depth address; the other is a diagnosed temperature-gradient structure. |
| Every column contains all five bands. | Bathymetry truncates the stack. |
| “No detected regime” means empty ocean. | It means the selected evidence did not earn a regime label. |
| A depth-address heat map proves transport. | Transport still requires velocity, temperature, geometry, and a reference convention. |

## What OSW can build next

The first implementation should be a section and voxel inspector, not another
flat political map. Selecting a surface province should reveal its bathymetry-
truncated depth bands; selecting a band should reveal measured properties and
physical overlays with missing data visible. The address remains stable while
mixed layers, water masses, anomalies, and currents change through it.

[Open the Ocean Column Address workbench](../column/). It compares one measured
GEBCO_2026 cell nearest the selected approximate province seed with shelf,
basin, and trench teaching columns. The single cell is not province-wide
bathymetry; the other seabeds and all regime overlays remain conceptual.

## Planetary boundary

Edition 1 is Earth ocean geography. Its sunlight labels, metre cutoffs, solid
seafloor truncation, and surface-province coordinate do not transfer directly
to a deep, rotating, compressible gas-giant atmosphere. A planetary comparison
may transfer questions about stratification, jets, mixing, and tracer-defined
layers only after defining a different vertical coordinate and lower-boundary
model.

## Next

[Water Masses and Layers](01-WATER-MASSES-AND-LAYERS.md) explains property and
gradient overlays. [Provinces, Seascapes, and Heatwaves](06-PROVINCES-SEASCAPES-AND-HEATWAVES.md)
explains the horizontal reference. [Evidence Receipts](14-EVIDENCE-RECEIPTS.md)
defines what a particular dataset may claim.
