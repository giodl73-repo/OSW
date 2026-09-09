---
skill: discover-websearch
topic: longhurst-56-province-cover
date: 2026-08-29
claims_checked: 4
confirmed: 4
---

# Web evidence — Longhurst's 56-province surface-ocean cover

## Claims and verdicts

| # | Claim | Evidence | Verdict | Source |
|---|---|---|---|---|
| 1 | The classic system divides the global ocean into four primary biomes and 56 provinces. | Published descriptions specify polar, westerly-wind, trade-wind, and coastal biomes subdivided into 56 BGCPs. | CONFIRMED | https://doi.org/10.1002/gbc.20089 |
| 2 | It covers shelves and open ocean rather than selecting only famous features. | The partition is described as encompassing both continental shelves and open oceans. | CONFIRMED | https://doi.org/10.1002/gbc.20089 |
| 3 | Province identity is grounded in physical forcing and characteristic production cycles. | The provinces use circulation, fronts, topography, temperature, salinity, chlorophyll, bathymetry, and recurrent seasonal behavior. | CONFIRMED | https://doi.org/10.1029/2008GL034238 |
| 4 | Static polygon boundaries are a computational reference, not permanent natural walls. | Longhurst emphasized that boundaries represent mean locations and dynamic methods show seasonal extents and overlaps. | CONFIRMED | https://doi.org/10.1002/gbc.20089 |

## Key evidence

- Reygondeau et al. describe two levels: four primary biomes and 56 smaller
  biogeochemical provinces, with rectilinear boundaries originally chosen for
  computational convenience: https://doi.org/10.1002/gbc.20089
- Oliver and Irwin recover recognizable systems including major gyres,
  equatorial upwelling, Gulf Stream/Kuroshio regions, and large river plumes,
  while repeating that boundaries are not fixed:
  https://doi.org/10.1029/2008GL034238
- Marine Regions provides a browsable/downloadable Longhurst polygon layer and
  individual gazetteer identities such as the Pacific Warm Pool Province:
  https://www.marineregions.org/gazetteer.php?id=21490&p=details
- Later dynamic classification uses temperature, salinity, chlorophyll, and
  bathymetry to estimate seasonal province locations, extents, and overlaps:
  https://doi.org/10.1002/gbc.20089

## Interpretation for OCEANLINES

Longhurst is a strong candidate for a complete **surface ecological cover**.
It does not classify every molecule through depth, diagnose transport barriers,
or replace water-mass analysis. The static polygons should be presented as mean
reference provinces. A future observed mode could render a probability core and
transition band rather than pretending that each boundary is a wall.

No ungrounded claims.

## Amend

1. Verify the exact downloaded layer's edition, feature count, license, geometry,
   and checksum before repository use; Longhurst-derived products vary by version.
2. Use `COVER` for the wall-to-wall surface provinces and retain WATERS/FLOWS/
   EDGES/FLOOR/LIFE/EVENTS as overlapping object lenses.
3. Build a later `COLUMN` cover separately for depth-dependent water-mass mixtures.

