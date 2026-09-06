---
skill: discover-websearch
topic: ocean-motion-heat-transport
date: 2026-08-29
claims_checked: 4
confirmed: 4
---

# Web evidence — ocean motion and heat transport

## PHASE 1 — CLAIMS TO GROUND

| # | Claim | Source | Why it matters |
|---|---|---|---|
| 1 | OSCAR can support a global surface-motion layer, but not a full-depth heat-transport map. | proposed OSW implementation | Determines the honest first motion product. |
| 2 | Ocean heat transport requires temperature and velocity integrated through a section, with mass balance and eddy terms treated explicitly. | physical definition | Prevents `SST × arrow` from being mislabeled as heat flow. |
| 3 | ORAS5 can support a three-dimensional transport pilot, but its assimilative-model character and regional biases must remain visible. | proposed OSW implementation | Determines the evidence status of the quantitative layer. |
| 4 | Lagrangian particles can expose pathways and sample temperature, but depend on the flow field and numerical choices and are not a heat budget. | proposed OSW implementation | Defines what a trajectory view may claim. |

## PHASE 2 — WEB EVIDENCE

### Claim 1 — OSCAR supports surface motion, not full-depth heat transport

- Query 1: `site:podaac.jpl.nasa.gov OSCAR V2.0 surface currents 30 m 0.25 degree official`
  - Source: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0
  - Direct quote: “OSCAR ocean mixed layer velocities are calculated from satellite-sensed sea surface height gradients, ocean vector winds, and sea surface temperature gradients.”
  - Relevance: The velocity is a diagnostic product derived with a simplified physical model.
- Query 2: `OSCAR daily global quarter degree current animation PO.DAAC`
  - Source: https://podaac.jpl.nasa.gov/animations/Ocean-Surface-Current-Speed-from-OSCAR-V2.0
  - Direct quote: “Level 4, quarter degree grid with a 1 day resolution dataset.”
  - Relevance: It has suitable global daily support for an atlas layer.
- Query 3: `OSCAR variables u v units PO.DAAC`
  - Source: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0
  - Direct quote: “u | zonal total surface current | m s-1”
  - Relevance: The product exposes vector components with physical speed units.
- Query 4: `OSCAR assumed well mixed top 30 m`
  - Source: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0
  - Direct quote: “an average over an assumed well-mixed top 30 m of the ocean.”
  - Relevance: This is the decisive vertical-support limitation.
- Verdict: CONFIRMED

### Claim 2 — Heat transport is a depth/section budget, not a warm-current overlay

- Query 1: `ocean heat transport vertical integral temperature flux section`
  - Source: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005GL022474
  - Direct quote: “compute the vertical integral of the temperature flux vT across an east-west section bounded by continents.”
  - Relevance: Establishes the section and vertical integral.
- Query 2: `ocean heat transport depth zonal integration velocity temperature density heat capacity`
  - Source: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008GL035490
  - Direct quote: “the integration is carried out over depth and zonally.”
  - Relevance: Confirms that surface velocity alone is insufficient.
- Query 3: `ocean heat transport mass flux balance section reference temperature`
  - Source: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005GL022474
  - Direct quote: “as long as the total mass flux across the section is zero.”
  - Relevance: Identifies the mass-balance condition behind section transport.
- Query 4: `eddy ocean heat transport considerable portion total`
  - Source: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008GL035490
  - Direct quote: “the time-mean eddy heat transport constitutes a considerable portion of the total time-mean heat transport.”
  - Relevance: Mean arrows alone can omit an important transport component.
- Verdict: CONFIRMED

### Claim 3 — ORAS5 is useful three-dimensional evidence with material limitations

- Query 1: `site:ecmwf.int ORAS5 0.25 75 levels reanalysis`
  - Source: https://www.ecmwf.int/en/forecasts/dataset/ocean-reanalysis-system-5
  - Direct quote: “a new global eddy-permitting ocean-sea ice ensemble reanalysis analysis system.”
  - Relevance: Establishes that ORAS5 is not direct observation alone.
- Query 2: `site:cds.climate.copernicus.eu ORAS5 vertical levels 5500 m`
  - Source: https://cds.climate.copernicus.eu/datasets/reanalysis-oras5?tab=quality_assurance_tab
  - Direct quote: “75 levels in the vertical ... ranging from 0 m to ~5500 m depth.”
  - Relevance: Provides the depth support required for a transport pilot.
- Query 3: `ORAS5 assimilates temperature salinity sea level sea ice official`
  - Source: https://cds.climate.copernicus.eu/datasets/reanalysis-oras5?tab=quality_assurance_tab
  - Direct quote: “Assimilation of in-situ temperature and salinity data.”
  - Relevance: Explains why the state estimate is observation-constrained.
- Query 4: `ORAS5 Gulf Stream bias transport official`
  - Source: https://www.ecmwf.int/en/forecasts/dataset/ocean-reanalysis-system-5
  - Direct quote: “misrepresentation of front positions and overshoot of the northward transport of the Gulf Stream.”
  - Relevance: A documented bias is directly relevant to motion mapping.
- Verdict: CONFIRMED

### Claim 4 — Particle trajectories are conditional pathway experiments

- Query 1: `site:docs.oceanparcels.org particle movement existing flow field U V`
  - Source: https://docs.oceanparcels.org/en/latest/examples/tutorial_parcels_structure.html
  - Direct quote: “simulate the movement of particles within an existing flow field environment.”
  - Relevance: Tracks inherit the supplied velocity product.
- Query 2: `site:docs.oceanparcels.org sample temperature particle trajectory`
  - Source: https://docs.oceanparcels.org/en/latest/examples/tutorial_parcels_structure.html
  - Direct quote: “temperature, to keep track of the temperature that particles experience.”
  - Relevance: Sampling temperature along a path does not compute transported watts.
- Query 3: `site:docs.oceanparcels.org grid velocity interpolation trajectories`
  - Source: https://docs.oceanparcels.org/en/latest/examples/tutorial_peninsula_AvsCgrid.html
  - Direct quote: “The impact of grid and velocity interpolation scheme on trajectories.”
  - Relevance: Numerical/grid choices can materially alter paths.
- Query 4: `site:docs.oceanparcels.org sub-grid diffusion particle trajectories`
  - Source: https://docs.oceanparcels.org/en/latest/examples/tutorial_diffusion.html
  - Direct quote: “sub-grid scale effects can be parameterized as a stochastic process.”
  - Relevance: Unresolved dispersion requires an explicit model choice.
- Verdict: CONFIRMED

## PHASE 3 — FINDINGS

| # | Finding | Verdict | Source |
|---|---|---|---|
| 1 | OSCAR is global and satellite-informed. | CONFIRMED | https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0 |
| 2 | OSCAR is daily at 0.25 degree. | CONFIRMED | https://podaac.jpl.nasa.gov/animations/Ocean-Surface-Current-Speed-from-OSCAR-V2.0 |
| 3 | OSCAR exposes zonal and meridional components in m/s. | CONFIRMED | https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0 |
| 4 | OSCAR represents an assumed well-mixed upper 30 m. | CONFIRMED | https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0 |
| 5 | Conventional meridional heat transport is vertically and section integrated. | CONFIRMED | https://doi.org/10.1029/2005GL022474 |
| 6 | The calculation combines velocity and temperature. | CONFIRMED | https://doi.org/10.1029/2008GL035490 |
| 7 | Balanced mass/volume transport matters to interpretation. | CONFIRMED | https://doi.org/10.1029/2005GL022474 |
| 8 | Eddy transport can be a material part of total transport. | CONFIRMED | https://doi.org/10.1029/2008GL035490 |
| 9 | ORAS5 is an ensemble ocean/sea-ice reanalysis. | CONFIRMED | https://www.ecmwf.int/en/forecasts/dataset/ocean-reanalysis-system-5 |
| 10 | ORAS5 supplies 75-level support to about 5500 m. | CONFIRMED | https://cds.climate.copernicus.eu/datasets/reanalysis-oras5?tab=quality_assurance_tab |
| 11 | ORAS5 assimilates observations. | CONFIRMED | https://cds.climate.copernicus.eu/datasets/reanalysis-oras5?tab=quality_assurance_tab |
| 12 | ORAS5 has documented regional current/front biases. | CONFIRMED | https://www.ecmwf.int/en/forecasts/dataset/ocean-reanalysis-system-5 |
| 13 | OceanParcels advects particles in supplied velocity fields. | CONFIRMED | https://docs.oceanparcels.org/en/latest/examples/tutorial_parcels_structure.html |
| 14 | A trajectory can sample temperature as an attached field. | CONFIRMED | https://docs.oceanparcels.org/en/latest/examples/tutorial_parcels_structure.html |
| 15 | Grid and interpolation choices affect trajectories. | CONFIRMED | https://docs.oceanparcels.org/en/latest/examples/tutorial_peninsula_AvsCgrid.html |
| 16 | Sub-grid dispersion may be represented stochastically. | CONFIRMED | https://docs.oceanparcels.org/en/latest/examples/tutorial_diffusion.html |

Summary: 4 of 4 claims confirmed. 0 contradicted. 0 unconfirmed. Sixteen
specific findings support a staged motion program.

## PHASE 4 — UNGROUNDED CLAIMS

No ungrounded claims.

## PHASE 5 — AMEND

1. Treat “heat moving around the ocean” as a hierarchy of speed, direction,
   pathways, section transport, and convergence rather than one map layer.
2. Add a second three-dimensional estimate or direct observing section when
   interpreting any ORAS5 gate result, especially in documented bias regions.
3. Test the frozen zoning only after movement products exist; do not tune the
   movement evidence to make the current boundaries appear successful.

