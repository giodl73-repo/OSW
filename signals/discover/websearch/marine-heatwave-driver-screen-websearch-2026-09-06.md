# Web grounding — North Atlantic marine-heatwave driver screen

**Date:** 2026-09-06  
**Question:** Which authoritative exact-date products can distinguish local
surface forcing from horizontal ocean advection around the August 7–12, 2026
North Atlantic threshold transition?

## Direct evidence

| Source | Direct support | OSW use |
|---|---|---|
| [NOAA Global RTOFS open-data registry](https://registry.opendata.aws/noaa-rtofs/) | Describes the 1/12-degree, 41-layer HYCOM/CICE operational system, assimilated observations, daily update, variables, public S3 bucket, and citation. | Exact August 7–12 surface temperature, current, and mixed-layer-thickness fields; remote ETags and compact extracted-value checksum. |
| [NOAA RTOFS documentation](https://github.com/NOAA-EMC/RTOFS_GLO/wiki) | Maintainer documentation for the operational global ocean system. | Product and field-semantics context; no claim that the offline diagnostic is a native tracer budget. |
| [NOAA/NCEI CFSv2](https://www.ncei.noaa.gov/products/weather-climate-models/climate-forecast-system) | Operational coupled analysis includes flux and ocean products from 2011 to present, but the inspected NCEI time-series catalog exposed 2026 only through March at retrieval time. | Rejected as an exact August forcing source for this stage; no substituted date. |
| [ERA5 single levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview) | Hourly 0.25-degree fields updated daily with about five-day latency, including surface energy-flux variables. | Preferred exact-date atmospheric forcing source once authenticated acquisition is available. |
| [Copernicus Global Ocean Physics](https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description) | Daily 1/12-degree temperature, velocity, and mixed-layer depth over a rolling operational archive. | Valid alternative ocean source, but download requires account authentication; NOAA RTOFS avoids that blocker for D11. |

## Finding

The public NOAA RTOFS S3 bucket retained every required August cycle even
though the HYCOM.org GOFS 3.1 historical aggregate ends in 2024 and its latest
endpoint no longer covers the event. HTTP range reads recovered only the local
chunks from two daily files: a surface standard-level T/U/V field and a
diagnostic mixed-layer-thickness field. The compact artifact contains 4,221
collocated grid centers for each of six 00 UTC snapshots.

An offline local tangent-plane gradient gives the Eulerian surface horizontal
advection `-u dT/dx - v dT/dy`. Across August 11–12, the RTOFS box-mean surface
temperature rises 0.5396°C/day, and the endpoint-mean horizontal-advection term is
0.0708°C/day, and 0.4688°C/day remains unresolved. At the anchor, advection is
−0.109°C/day while modeled SST warms 0.601°C/day. Four- and eight-neighbor
gradient estimates differ by less than 0.002°C/day in the box mean.

The box-mean diagnostic mixed layer shoals from 19.497 to 7.801 m, which makes
surface forcing and vertical structure especially relevant next. It is not a
budget term by itself. The unresolved tendency also contains vertical
advection, entrainment, mixing, diffusion, assimilation increments, numerical
effects, time sampling, and gradient error. D11 therefore excludes horizontal
advection as the dominant modeled box-mean bridge-day term without attributing
the remainder to the atmosphere.

## Next evidence

Acquire exact hourly radiative and turbulent surface fluxes, average them over
the same interval and support, and convert them to a mixed-layer temperature
tendency under explicitly tested layer-depth conventions. Retain all excluded
model terms in the remainder rather than treating apparent closure as causation.
