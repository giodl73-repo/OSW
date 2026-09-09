---
skill: discover-websearch
topic: ocean heat quantity receipts
date: 2026-09-05
claims_checked: 3
confirmed: 3
---

# Web grounding — Ocean heat quantity receipts

## Claims to ground

| # | Claim | Source of claim | Why it needs grounding |
|---|---|---|---|
| 1 | Ocean volume transport and heat transport are governed, section-based scientific quantities. | OSW registry gap | Otherwise OSW could mistake local analysis labels for standard quantities. |
| 2 | Ocean surface heat flux is a boundary exchange per unit area and a core observing variable. | Nordic surface receipt | Otherwise a surface term could be confused with heat content or a closed budget. |
| 3 | Ocean heat content requires declared vertical, spatial, temporal, and anomaly/integration conventions. | Argo receipt audit | Otherwise one temperature level could be promoted into an inventory. |

## Web evidence

### Claim 1 — Volume and heat transport are section-based quantities

- Query 1: `site:cfconventions.org "ocean_volume_transport_across_line"`
  - Source: [CF Standard Names table v68](https://cfconventions.org/Data/cf-standard-names/68/build/cf-standard-name-table.html)
  - Direct quote: “ocean_volume_transport_across_line” with units `m3 s-1`.
  - Relevance: directly names a cross-line ocean volume-transport variable.
- Query 2: `site:cfconventions.org "northward_ocean_heat_transport"`
  - Source: [CF Standard Names table v92](https://cfconventions.org/Data/cf-standard-names/92/build/cf-standard-name-table.html)
  - Direct quote: “northward_ocean_heat_transport” with units `W`.
  - Relevance: directly names ocean heat transport and its power unit.
- Verdict: **CONFIRMED**.

### Claim 2 — Surface heat flux is boundary exchange and an observing variable

- Query 1: `site:goosocean.org "Ocean surface heat flux" EOV`
  - Source: [GOOS Essential Ocean Variables](https://goosocean.org/what-we-do/framework/essential-ocean-variables/)
  - Direct quote: “Ocean surface heat flux” appears in the physical EOV list.
  - Relevance: establishes its place in the sustained ocean-observing framework.
- Query 2: `site:gcos.wmo.int ocean surface heat flux essential climate variable`
  - Source: [GCOS Ocean Surface Heat Flux](https://gcos.wmo.int/site/global-climate-observing-system-gcos/essential-climate-variables/ocean-surface-heat-flux)
  - Direct quote: “exchange of heat, per unit area, crossing the surface”.
  - Relevance: distinguishes a boundary flux density from an ocean heat inventory.
- Verdict: **CONFIRMED**.

### Claim 3 — Heat content requires explicit integration support

- Query 1: `site:ncei.noaa.gov ocean heat content depth ranges reference anomaly`
  - Source: [NOAA/NCEI Global Ocean Heat Content CDR](https://www.ncei.noaa.gov/products/climate-data-records/global-ocean-heat-content)
  - Direct quote: “time-series for multiple depth ranges in the global ocean”.
  - Relevance: shows that time and depth range are integral product dimensions.
- Query 2: `site:ncei.noaa.gov ocean heat content how calculated density heat capacity area volume`
  - Source: [NOAA/NCEI World Ocean Database FAQ](https://www.ncei.noaa.gov/products/world-ocean-database)
  - Direct quote: “multiplied by the climatological mean density ... heat capacity ... area and volume”.
  - Relevance: directly describes the integration ingredients absent from a single-level anomaly map.
- Verdict: **CONFIRMED**.

## Findings

| # | Claim | Evidence summary | Verdict | Source |
|---|---|---|---|---|
| 1 | Volume and heat transport are section quantities. | CF governs cross-line volume transport and northward heat transport with dimensional units. | CONFIRMED | [CF v68](https://cfconventions.org/Data/cf-standard-names/68/build/cf-standard-name-table.html), [CF v92](https://cfconventions.org/Data/cf-standard-names/92/build/cf-standard-name-table.html) |
| 2 | Surface heat flux is boundary exchange and an EOV. | GOOS lists it as an EOV; GCOS defines it per unit area across the interface. | CONFIRMED | [GOOS](https://goosocean.org/what-we-do/framework/essential-ocean-variables/), [GCOS](https://gcos.wmo.int/site/global-climate-observing-system-gcos/essential-climate-variables/ocean-surface-heat-flux) |
| 3 | Heat content needs explicit integration support. | NOAA products declare depth/time ranges and describe density, heat capacity, area, and volume. | CONFIRMED | [NCEI CDR](https://www.ncei.noaa.gov/products/climate-data-records/global-ocean-heat-content), [WOD FAQ](https://www.ncei.noaa.gov/products/world-ocean-database) |

Summary: **3 of 3 claims confirmed; 0 contradicted; 0 unconfirmed.**

## Ungrounded claims

No ungrounded claims.

## Amendments

1. Use the exact CF/GOOS names as external anchors while keeping OSW's type
   assignment explicitly editorial.
2. Require geometry, direction/sign, units, and time support in every transport
   or surface-flux receipt.
3. Require vertical bounds, spatial footprint, time support, baseline, density,
   heat-capacity convention, and integration method before granting a
   heat-content identity test.

## Boundary

These sources establish governed quantities and reporting practices. They do
not validate OSW's particular ORAS5 values, define one universal reference
temperature, or make the OSW receipt vocabulary a community standard.
