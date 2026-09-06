# Life, Oxygen, Nutrients, and Carbon

*The ocean carries living communities and chemical inventories, but a coloured
concentration map is not automatically a body, event, pool, or flux.*

**Evidence class:** diagrams and cards are concepts. Detected biological or
chemical objects require named variables, methods, depth support, time support,
units, thresholds, uncertainty, and—in ecological cases—taxonomic or impact
evidence.

## Object cards

| Object | Identity test | Typical geometry | Not equivalent to |
|---|---|---|---|
| Oxygen minimum zone | persistent vertical dissolved-oxygen minimum | subsurface volume/layer | every temporary hypoxic event |
| Hypoxic event | oxygen below a declared threshold for a stated time and habitat | event volume | one universal biological limit |
| Anoxic event | oxygen effectively absent under a declared method/rule | event volume | merely low oxygen |
| Nutrient pool | concentration integrated over a declared control volume | budget construct | nutrient concentration at one depth |
| Deep chlorophyll maximum | subsurface local maximum in chlorophyll | evolving layer | necessarily maximum biomass or production |
| Phytoplankton community | organisms classified by composition and abundance | advecting material population | satellite chlorophyll alone |
| Phytoplankton bloom | unusual accumulation under a stated baseline/rule | event field | permanent province |
| Harmful algal bloom | bloom qualified by toxin, nuisance, or harmful impact | impact-classified event | every dense or discoloured bloom |
| DIC pool | dissolved inorganic carbon integrated over a volume | budget construct | pH, pCO₂, alkalinity, or flux |
| Air–sea CO₂ flux | carbon crossing the ocean surface per area and time | signed surface flux | ocean carbon concentration |
| Primary production | rate of organic matter formation by photosynthesis | transformation process | chlorophyll concentration |
| Biological carbon pump | coupled production, export, remineralization, and circulation | process network | particles simply sinking everywhere |

## Field, body, event, pool, and flux

```text
CONCENTRATION FIELD       MATERIAL BODY        EVENT           POOL             FLUX
µmol kg⁻¹ or mg m⁻³       water/community      rule + time     ∫ C dV           crosses boundary
       │                        │                  │            mol or kg         mol m⁻² s⁻¹
       └── can diagnose ────────┴── can enter ────┴── integrates ──┴── changes ───►
```

A field reports a value at sampled locations. A material body requires coherent
property or community identity. An event requires a threshold, baseline, or
impact rule over time. A pool is an inventory integrated over declared volume.
A flux crosses a declared boundary per time. Similar colours cannot erase these
dimensional differences.

GOOS likewise specifies oxygen, nutrients, inorganic carbon, particulate matter,
and biological abundance/diversity as distinct Essential Ocean Variables
([GOOS EOVs](https://goosocean.org/what-we-do/framework/essential-ocean-variables/)).

## Oxygen structure versus oxygen event

```text
surface oxygenated water
────────────────────────────────
        upper oxycline
     OXYGEN MINIMUM ZONE       persistent vertical structure
        lower oxycline
────────────────────────────────
deeper oxygenated water

hypoxia contour = cells below declared O₂ threshold at declared time/depth
anoxia contour  = near-zero O₂ under method-specific detection rule
```

NOAA describes oxygen minimum zones as persistent water-column layers shaped by
physical, chemical, and biological processes. Coastal hypoxia is commonly mapped
at dissolved oxygen below 2 mg/L, but organism responses vary and other studies
use different thresholds and units. Therefore an OMZ can contain, overlap, or
feed a hypoxic event without being synonymous with it.

[NOAA OMZ explanation](https://oceanexplorer.noaa.gov/ocean-fact/omz/) ·
[NOAA hypoxia definition](https://www.ncei.noaa.gov/archive/archive-management-system/OAS/bin/prd/jquery/datatype/details/743)

## Chlorophyll is a proxy, not the whole ecosystem

```text
ocean colour radiance
        ↓ algorithm
surface chlorophyll-a ──proxy──► phytoplankton biomass
        │                              │
        │ + light + temperature        ├── taxonomy/diversity needs more evidence
        ▼                              ▼
modeled primary production          community composition

bloom = time-dependent accumulation rule; harmful = toxin/impact qualification
```

Chlorophyll changes with organisms and physiological state. Satellites mostly
sample the near surface and can miss a deep chlorophyll maximum. Production is
a rate, biomass is an amount, community is taxonomic composition, and a bloom is
an event. Advection, grazing, sinking, mortality, and dilution mean high
production need not create a local biomass maximum.

NOAA calls chlorophyll-a a commonly used biomass proxy and calculates primary
production using additional inputs
([NOAA Northeast assessment](https://www.integratedecosystemassessment.noaa.gov/regions/northeast/northeast-phytoplankton)).
NOAA also stresses that not all blooms are harmful; toxicity or other impact
requires separate evidence
([NOAA bloom guide](https://oceanservice.noaa.gov/facts/habharm.html)).

## The carbonate system is not one carbon layer

```text
DIC = dissolved CO₂ + bicarbonate + carbonate       concentration
TA  = acid-buffering capacity                       concentration-like property
pH  = hydrogen-ion activity scale                   logarithmic state
pCO₂ = CO₂ partial pressure                         exchange driver component
Ω   = mineral saturation state                      derived state

air–sea CO₂ flux = gas transfer × (ocean–air disequilibrium)  + formulation
DIC pool = ∫ρ · DIC dV over a declared ocean volume
```

DIC, total alkalinity, pH, and pCO₂ jointly constrain carbonate chemistry but
remain different observables with different meanings. Common calculations use
two measured carbon-system parameters plus temperature, salinity, pressure,
nutrients, constants, and a stated scale. Air–sea flux additionally needs a gas
transfer formulation, wind/forcing information, area, direction, and uncertainty.

[NOAA PMEL carbon measurements](https://www.pmel.noaa.gov/co2/story/Laboratory%2BAnalysis) ·
[NOAA OCADS methods](https://www.ncei.noaa.gov/products/ocean-carbon-acidification-data-system)

## The biological carbon pump is a network

```text
surface nutrients + DIC
          │ photosynthesis
          ▼
phytoplankton biomass ─► grazing / particles / dissolved organic matter
          │                              │
          └── respiration ◄──────────────┤
                                         ▼ export
                                remineralization at depth
                                         │
                          circulation returns transformed water
```

The biological carbon pump is not one sinking blob. It is a coupled set of
production, food-web transfer, particle and dissolved export, respiration,
remineralization, mixing, and circulation pathways. Its strength depends on the
chosen boundary and metric: export below one depth, sequestration duration, and
change in full-ocean inventory are different quantities.

## The decisive tests

1. Name the measurand and units: concentration, saturation, abundance, biomass,
   production rate, vertically integrated inventory, or boundary flux.
2. Declare depth range, spatial support, sampling time, resolution, missingness,
   detection limit, and uncertainty.
3. For oxygen events, state threshold, units, duration, habitat, and whether the
   rule is chemical, ecological, or regulatory.
4. For blooms, state baseline, accumulation rule, organism/taxon evidence, and
   whether “harmful” means toxin, mortality, nuisance, or another impact.
5. Treat chlorophyll as a proxy with algorithm and validation, not a direct
   census or production measurement.
6. For carbon chemistry, identify measured versus calculated parameters, pH
   scale, constants, temperature, salinity, pressure, and uncertainty propagation.
7. For pools and fluxes, declare integration volume, boundaries, orientation,
   reference time, and budget closure.
8. Test physical alternatives: advection, mixing, stratification, upwelling,
   air–sea exchange, sinking, and lateral import/export.
9. For a nutrient pool, name each chemical species and unit; nitrate, nitrite,
   ammonium, phosphate, silicate, and a model's aggregated tracer are not interchangeable.

## OSW consequences

The 56 provinces can index ecological observations, but they do not make oxygen,
nutrient, chlorophyll, or carbon fields uniform within each state. A dynamic
seascape class, persistent OMZ, bloom event, water mass, and DIC inventory can
all overlap one province because they answer different questions.

Future OSW biological maps should expose at least five switchable evidence
classes: measured concentration, derived proxy, classified event, integrated
pool, and boundary flux. A “carbon state” map without those labels would repeat
the exact confusion the heat work has been correcting.

[Return to provinces and seascapes](06-PROVINCES-SEASCAPES-AND-HEATWAVES.md) ·
[return to gates and budgets](04-GATES-TRANSPORTS-AND-RELAYS.md) ·
[inspect Guide 12 evidence](../signals/discover/websearch/biological-chemical-ocean-objects-websearch-2026-09-05.md)

## Planetary connection

Gas giants have chemical tracers, clouds, photochemistry, and disequilibrium,
but an Earth phytoplankton bloom or biological carbon pump has no automatic
counterpart. A coloured atmospheric tracer field may reveal transport or
chemistry without being a living community. Any astrobiological comparison must
separate remotely observed composition, physical disequilibrium, metabolism,
and direct evidence of life.

## Common mistakes

- Calling every low-oxygen observation an oxygen minimum zone.
- Applying 2 mg/L hypoxia as a universal biological threshold.
- Treating chlorophyll as direct biomass, production, taxonomy, or toxicity.
- Calling every bloom harmful or every harmful bloom visibly discoloured.
- Mapping a point concentration as a full-depth inventory.
- Treating pH, pCO₂, DIC, alkalinity, saturation, and CO₂ flux as synonyms.
- Calling production a pool or particle sinking the complete biological pump.
- Ignoring horizontal transport when explaining a local chemical change.
- Letting province boundaries imply biological or chemical impermeability.

## Next

The registry now has a compact [visual matrix and decision path](13-HOW-TO-NAME-AN-OCEAN-PATCH.md).
Its companion [evidence receipts](14-EVIDENCE-RECEIPTS.md) show how an actual
field passes—or does not yet test—the identity requirements behind these names.

[Field Guide index](README.md) · [Sea Ice, Polynyas, and Ocean Cavities](11-SEA-ICE-POLYNYAS-AND-OCEAN-CAVITIES.md) · [Classification](../CLASSIFICATION.md)
