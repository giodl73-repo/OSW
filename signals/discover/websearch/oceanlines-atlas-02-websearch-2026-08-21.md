---
skill: discover-websearch
topic: osw-atlas-02
date: 2026-08-21
claims_checked: 3
confirmed: 3
---

# OCEANLINES Atlas 02: anomaly evidence

## Claims to ground

| # | Claim | Source | Why it matters |
|---|---|---|---|
| 1 | OISST's supplied anomaly uses a 1971–2000 reference period. | implementation assumption | defines zero and every mapped value |
| 2 | The anomaly is daily OISST minus a climatological mean. | measurement firewall | distinguishes anomaly from absolute SST |
| 3 | The climatology is interpolated in space and time. | visualization boundary | prevents false native-resolution claims |

## Web evidence

### Claim 1 — reference period

- Query: `site:ncei.noaa.gov OISST v2.1 anomaly climatology 1971-2000`
  - Source: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
  - Direct quote: “represents the 1971–2000 base period”
- Query: `site:ncei.noaa.gov OISST ERDDAP climatology based 1971-2000`
  - Source: https://www.ncei.noaa.gov/erddap/info/ncdc_oisst_v2_avhrr_by_time_zlev_lat_lon/index.html
  - Direct quote: “Climatology is based on 1971-2000 OI.v2 SST.”
- Verdict: **CONFIRMED**.

### Claim 2 — anomaly definition

- Query: `daily OISST anomaly minus 1971-2000 climatological mean`
  - Source: https://essd.copernicus.org/articles/8/165/2016/essd-8-165-2016.pdf
  - Direct quote: “the daily OISST minus the 1971–2000 climatological mean”
- Query: `site:ncei.noaa.gov OISST daily sea surface temperature anomalies variable`
  - Source: https://www.ncei.noaa.gov/thredds/dodsC/OisstBase/NetCDF/V2.1/AVHRR/202006/oisst-avhrr-v02r01.20200601.nc.html
  - Direct quote: “Daily sea surface temperature anomalies”
- Verdict: **CONFIRMED**.

### Claim 3 — interpolated climatology

- Query: `site:ncei.noaa.gov OISST climatology interpolated 1/4 daily grid monthly file`
  - Source: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
  - Direct quote: “interpolated to 1/4° daily grid file from the 1° monthly file”
- Query: `OISST anomaly climatology Xue 2003 interpolation daily grid`
  - Source: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
  - Direct quote: “The climatology is described in Xue et al. (2003).”
- Verdict: **CONFIRMED**.

## Findings

| # | Evidence summary | Verdict | Source |
|---|---|---|---|
| 1 | NOAA defines anomaly zero using 1971–2000. | CONFIRMED | https://www.ncei.noaa.gov/products/optimum-interpolation-sst |
| 2 | The supplied field is daily SST minus that climatology. | CONFIRMED | https://essd.copernicus.org/articles/8/165/2016/essd-8-165-2016.pdf |
| 3 | The reference is interpolated from monthly 1° to daily 0.25°. | CONFIRMED | https://www.ncei.noaa.gov/products/optimum-interpolation-sst |

Summary: 3 of 3 claims confirmed. None contradicted or unconfirmed.

## Ungrounded claims

No ungrounded claims.

## Amend

1. Keep absolute SST and anomaly in separate interface modes and palettes.
2. Label the reference period in the map, details, and documentation.
3. Add the supplied estimated-error field next rather than implying uniform confidence.
