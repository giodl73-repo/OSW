---
skill: discover-websearch
topic: osw-atlas-01
date: 2026-08-21
claims_checked: 3
confirmed: 3
---

# OCEANLINES Atlas 01: OISST access evidence

## Claims to ground

| # | Claim | Source of claim | Why it matters |
|---|---|---|---|
| 1 | NOAA exposes a final, global, daily OISST collection suitable for a fixed atlas snapshot. | implementation assumption | determines whether the layer is reproducible |
| 2 | SST, anomaly, error, and ice are separate variables on the product grid. | measurement firewall | prevents one field being mislabeled as another |
| 3 | OISST is an interpolated analysis and its error field matters. | atlas boundary | prevents “observed” from implying direct measurement at every cell |

## Web evidence

### Claim 1 — a fixed global product is accessible

- Query: `site:coastwatch.pfeg.noaa.gov erddap ncdcOisst21Agg_LonPM180 sst dataset`
  - Source: https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.html
  - Direct quote: “Final, Global, 0.25°, 1981-present”
- Query: `site:ncei.noaa.gov OISST v2.1 daily global grid final product`
  - Source: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
  - Direct quote: “Data are currently available from September 1, 1981—present, and updated every day.”
- Verdict: **CONFIRMED**.

### Claim 2 — variables remain distinct

- Query: `site:ncei.noaa.gov OISST v2.1 variables anomaly error ice netcdf`
  - Source: https://www.ncei.noaa.gov/thredds/dodsC/OisstBase/NetCDF/V2.1/AVHRR/202006/oisst-avhrr-v02r01.20200601.nc.html
  - Direct quote: “Daily sea surface temperature anomalies”
- Query: `site:ncei.noaa.gov OISST estimated error sea ice variables ERDDAP`
  - Source: https://www.ncei.noaa.gov/erddap/info/ncdc_oisst_v2_avhrr_by_time_zlev_lat_lon/index.html
  - Direct quote: “Estimated error standard deviation of analysed_sst”
- Verdict: **CONFIRMED**.

### Claim 3 — the field is an analysis, not direct coverage everywhere

- Query: `site:ncei.noaa.gov OISST interpolated fill gaps error field confidence`
  - Source: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
  - Direct quote: “The dataset is interpolated to fill gaps on the grid”
- Query: `site:ncei.noaa.gov OISST error field measure confidence quality`
  - Source: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
  - Direct quote: “The error field provides a measure of confidence or quality”
- Verdict: **CONFIRMED**.

## Findings

| # | Evidence summary | Verdict | Source |
|---|---|---|---|
| 1 | NOAA maintains a final daily global OISST collection. | CONFIRMED | https://www.ncei.noaa.gov/products/optimum-interpolation-sst |
| 2 | SST, anomaly, estimated error, and ice are independently addressable fields. | CONFIRMED | https://www.ncei.noaa.gov/erddap/info/ncdc_oisst_v2_avhrr_by_time_zlev_lat_lon/index.html |
| 3 | OISST fills gaps by interpolation and supplies an error field. | CONFIRMED | https://www.ncei.noaa.gov/products/optimum-interpolation-sst |

Summary: 3 of 3 claims confirmed. None contradicted or unconfirmed.

## Ungrounded claims

No ungrounded claims.

## Amend

1. Add the anomaly and error fields only as separate selectable layers.
2. Compare the display-strided field with the native grid before publication.
3. Keep the fixed final snapshot separate from preliminary near-real-time products.
