---
skill: discover-websearch
topic: ocean-geography-ontology
date: 2026-08-29
claims_checked: 4
confirmed: 4
---

# Web evidence — a broader OCEANLINES ocean-geography ontology

## PHASE 1 — CLAIMS TO GROUND

| # | Claim | Source of claim | Why it needs grounding |
|---|---|---|---|
| 1 | Heatmasses are only one subset of larger named ocean-water volumes. | owner observation / repo vocabulary | A heat-only directory leaves most of the ocean conceptually blank. |
| 2 | Water masses cannot be classified by warm versus cold alone. | assumed oceanographic practice | A temperature-only ontology would misidentify layered and mixed waters. |
| 3 | Currents, gyres, eddies, fronts, and upwelling zones are different feature types from water masses. | existing atlas grammar | Combining volumes and motions as “blobs” would imply false boundaries. |
| 4 | A useful ocean atlas needs several variable and depth lenses, plus seafloor geography. | proposed product direction | The UI architecture depends on whether this is a real scientific distinction. |

## PHASE 2 — WEB EVIDENCE

### Claim 1 — Heatmasses are only one subset of larger named ocean-water volumes

- Query: `site:noaa.gov ocean water masses temperature salinity definition water mass`
  - Source: https://repository.library.noaa.gov/view/noaa/9306/noaa_9306_DS1.pdf
  - Direct quote: “A water mass is simply water with certain rather narrowly defined salinity and temperature characteristics.”
  - Relevance: NOAA's definition makes temperature one property, not the whole category.
- Query: `site:whoi.edu ocean water masses Antarctic Bottom Water Antarctic Intermediate Water`
  - Source: https://divediscover.whoi.edu/polar-regions/antarctic-ocean-circulation/
  - Direct quote: “Antarctic Bottom Water forms on the continental shelf and sinks to spread through the bottom of the world's oceans.”
  - Relevance: A major cold, deep, named mass occupies geography invisible to a surface heat map.
- Verdict: CONFIRMED

### Claim 2 — Water masses cannot be classified by warm versus cold alone

- Query: `site:whoi.edu water masses temperature salinity North Atlantic Deep Water Antarctic Bottom Water`
  - Source: https://www.whoi.edu/science/PO/people/jprice/class/miscart/Stewart2006.pdf
  - Direct quote: “A core is a layer of water with extreme value ... of salinity or other property as a function of depth.”
  - Relevance: Water-mass identity is three-dimensional and may be traced by extrema other than temperature.
- Query: `site:noaa.gov World Ocean Atlas temperature salinity oxygen nutrients climatology`
  - Source: https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/
  - Direct quote: “objectively analyzed and statistical data at 102 standard depth levels of the World Ocean.”
  - Relevance: The authoritative atlas provides multiple variables across depth rather than a warm/cold partition.
- Verdict: CONFIRMED

### Claim 3 — Motions and boundaries are distinct from water masses

- Query: `site:noaa.gov ocean fronts gyres eddies upwelling water masses definition`
  - Source: https://oceanservice.noaa.gov/facts/gyre.html
  - Direct quote: “A gyre is a large system of rotating ocean currents.”
  - Relevance: A gyre is a circulation system, not a homogeneous parcel.
- Query: `site:noaa.gov ocean fronts eddies upwelling definition`
  - Source: https://www.weather.gov/media/zhu/ZHU_Training_Page/Met_Tutorials/Met_Tutorial.pdf
  - Direct quote: “An ocean front is the interface between two water masses of different physical characteristics.”
  - Relevance: A front is a boundary between volumes, not another volume.
- Supporting source: https://www.gfdl.noaa.gov/ocean-mesoscale-eddies/
  - Direct quote: “Ocean mesoscale eddies are the ‘weather’ of the ocean.”
  - Relevance: Eddies are mobile, transient three-dimensional structures.
- Verdict: CONFIRMED

### Claim 4 — Several field/depth lenses and seafloor geography are required

- Query: `site:goosocean.org essential ocean variables temperature salinity currents oxygen nutrients sea ice`
  - Source: https://goosocean.org/what-we-do/framework/essential-ocean-variables/
  - Direct quote: “the minimum set of ocean variables that are needed to assess ocean state and variability.”
  - Relevance: GOOS separately lists temperature, salinity, currents, sea ice, oxygen, and nutrients.
- Query: `site:noaa.gov ocean basin continental shelf abyssal plain ridge trench definitions`
  - Source: https://prod-01-alb-www-noaa.woc.noaa.gov/education/resource-collections/ocean-coasts/ocean-floor-features
  - Direct quote: “Beneath the smooth ocean surface extends an underwater landscape as complex as anything you might find on land.”
  - Relevance: Shelf, slope, plain, ridge, trench, canyon, and seamount geography structures the water above it.
- Supporting source: https://oceanexplorer.noaa.gov/ocean-fact/omz/
  - Direct quote: “Oxygen minimum zones are persistent layers in the water column that have low oxygen concentration.”
  - Relevance: Some large ocean provinces are chemical and vertical, neither temperature blobs nor circulation paths.
- Verdict: CONFIRMED

## PHASE 3 — FINDINGS TABLE

| # | Claim | Evidence summary | Verdict | Source |
|---|---|---|---|---|
| 1 | Heatmasses are a subset | Named cold and deep waters span basins beyond surface thermal features. | CONFIRMED | https://divediscover.whoi.edu/polar-regions/antarctic-ocean-circulation/ |
| 2 | Warm/cold is insufficient | Water masses use temperature, salinity, density, depth, origin, and tracers. | CONFIRMED | https://repository.library.noaa.gov/view/noaa/9306/noaa_9306_DS1.pdf |
| 3 | Volume, motion, and boundary differ | Gyres are current systems, fronts are interfaces, and eddies are mobile structures. | CONFIRMED | https://oceanservice.noaa.gov/facts/gyre.html |
| 4 | Multiple lenses are necessary | Operational ocean observing and mapping distinguish physical, chemical, biological, ice, and seabed variables. | CONFIRMED | https://goosocean.org/what-we-do/framework/essential-ocean-variables/ |

Summary: 4 of 4 claims confirmed. 0 contradicted. 0 unconfirmed.

## PHASE 4 — UNGROUNDED CLAIMS

No ungrounded claims.

## PHASE 5 — AMEND

1. Refine later searches around published global water-mass definitions and
   reproducible diagnostics rather than searching for informal “cold blobs.”
2. Add Southern Ocean, Arctic, tropical, and biogeochemical specialists or
   sources before claiming that an initial named-feature list is exhaustive.
3. Treat every proposed polygon as conceptual until a variable, depth, period,
   threshold or classification rule, dataset, and uncertainty are declared.

