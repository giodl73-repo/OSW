---
skill: discover-websearch
topic: osw-atlas-v0
date: 2026-08-21
claims_checked: 4
confirmed: 4
---

# OCEANLINES Atlas v0: web evidence

## Claims to ground

| # | Claim | Why it matters |
|---|---|---|
| 1 | A surface-temperature atlas needs a global, regular, versioned SST product. | defines the first observational raster |
| 2 | Surface temperature cannot represent subsurface storage. | prevents a category error |
| 3 | Surface velocity is not full-depth heat transport. | prevents flow arrows being read as energy budgets |
| 4 | Gates require topography, while current transport and cross-front heat exchange remain distinct. | prevents the “cold wall” simplification |

## Web evidence

### Claim 1 — global surface temperature

- Query: `site:noaa.gov OISST daily sea surface temperature official dataset 0.25 degree`
  - Source: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
  - Direct quote: “observations from different platforms ... into a regular global grid”
- Query: `NOAA OISST v2.1 temporal spatial resolution netCDF official metadata`
  - Source: https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC01606
  - Direct quote: “spatial grid resolution of 0.25 degree and temporal resolution of 1 day”
- Verdict: **CONFIRMED**.

### Claim 2 — depth requires a different evidence class

- Query: `site:argo.ucsd.edu gridded temperature salinity full depth data products`
  - Source: https://argo.ucsd.edu/data/argo-data-products/
  - Direct quote: “Global gridded 1/4 degree full depth NetCDF temperature and salinity climatology”
- Query: `site:ecco-group.org ECCO Version 4 Release 4 ocean state estimate observations model`
  - Source: https://www.ecco-group.org/docs/v4r4_synopsis.pdf
  - Direct quote: “synthesizes nearly all modern observations with an ocean circulation model”
- Verdict: **CONFIRMED**.

### Claim 3 — velocity is not heat transport

- Query: `site:podaac.jpl.nasa.gov OSCAR currents top 30 m 0.25 degree`
  - Source: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0
  - Direct quote: “average over an assumed well-mixed top 30 m of the ocean”
- Query: `Drake Passage transport temperature heat useful concept net volume balance Cunningham 2003`
  - Source: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2001JC001147
  - Direct quote: “Transport or divergence of heat is a useful concept only where there is a net balance of volume.”
- Verdict: **CONFIRMED**.

### Claim 4 — gates and fronts need multiple layers

- Query: `site:gebco.net current gridded bathymetry global terrain model 15 arc-second`
  - Source: https://www.gebco.net/data_and_products/gridded_bathymetry_data/
  - Direct quote: “a global terrain model for ocean and land”
- Query: `eddy heat flux crossing Antarctic Circumpolar Current observations Drake Passage`
  - Source: https://journals.ametsoc.org/view/journals/phoc/46/7/jpo-d-16-0029.1.xml
  - Direct quote: “the divergent eddy heat fluxes are poleward almost everywhere”
- Verdict: **CONFIRMED**.

## Findings

| # | Evidence summary | Verdict | Primary source |
|---|---|---|---|
| 1 | NOAA OISST v2.1 is a daily 0.25-degree spatially complete surface product. | CONFIRMED | https://www.ncei.noaa.gov/products/optimum-interpolation-sst |
| 2 | Argo resolves depth observationally; ECCO supplies a modeled/assimilated state. | CONFIRMED | https://argo.ucsd.edu/data/argo-data-products/ |
| 3 | OSCAR is an upper-30-m velocity estimate, not a full-depth heat budget. | CONFIRMED | https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0 |
| 4 | GEBCO supplies geometry while observations show poleward eddy heat flux across ACC fronts. | CONFIRMED | https://www.gebco.net/data_and_products/gridded_bathymetry_data/ |

Summary: 4 of 4 claims confirmed. No claims contradicted or unconfirmed.

## Ungrounded claims

No ungrounded claims.

## Amend

1. Test current authentication and subsetting interfaces before selecting an ingestion route.
2. Add independent product comparisons when the first observational raster is generated.
3. Treat disagreement between surface, in-situ, and assimilated layers as a result.
