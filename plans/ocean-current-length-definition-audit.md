# Current length definitions: next admission pass

Audit date: 2026-10-02. This supplements the seven source-gated geographic
span scenarios and the eleven admitted published length estimates. It records
why the next broad basin currents need a defined layer and endpoint convention
before OSW computes a whole-current reference route.

| Current | Direct evidence | Admission decision and next action |
|---|---|---|
| South Indian Current | [Stramma (1992), abstract](https://doi.org/10.1175/1520-0485%281992%29022%3C0421%3ATSioc%3E2.0.CO%3B2) names an upper-1000-m flow associated with the subtropical front and describes northeastward departure east of 100 degrees E. [Grand et al. (2015), section 3.2](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2014gb004898) identifies an eastward current near 40 degrees S. [Ridgway and Dunn (2007), section 3.4](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2007GL030392) distinguishes the intermediate gyre return flow from the subtropical front and warns against treating that front as the gyre boundary. | A single line along 40 degrees S cannot stand for every depth and naming convention. Obtain the original hydrographic sections and define an upper-ocean frontal-jet route with explicit surveyed gates; preserve intermediate gyre return flow as a different scope. No numeric whole-current estimate admitted from these descriptions. |
| South Pacific Current | The [Stramma et al. (1995) source](https://journals.ametsoc.org/view/journals/phoc/25/1/1520-0485_1995_025_0077_tspc_2_0_co_2.xml) is the existing naming citation; its full publisher text was unavailable in this pass. [ODP Leg 181 synthesis](https://www-odp.tamu.edu/publications/181_SR/synth/s_2.htm) describes currents meeting east of Chatham Rise to form the named flow. [Ridgway and Dunn (2007), section 3.4](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2007GL030392) finds no clear relationship between the front and deeper gyre flow east of New Zealand. | Do not choose Tasmania as the start solely from a global schematic or infer a deeper route from the surface front. Inspect the 1995 hydrographic study, identify a named-flow start near Chatham Rise and its eastern conversion, then declare the layer and reference path. No numerical whole-current estimate admitted yet. |
| Norwegian Current labels | [Gascard et al. (2004), sections 2.1-2.3](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2003GL018303) separates Norwegian Coastal Current, Norwegian Atlantic Current, and the Atlantic branches into the Barents Sea and Fram Strait. | A transit distance for Norwegian Atlantic water cannot be assigned to the inventory's ambiguous Norwegian Current or the fresh coastal current without an identity decision. Resolve the current taxonomy and branch endpoints before admitting an extent. |

The gate scenarios already added to the atlas are a geographic comparison,
not a route reconstruction. Their ±0.5-degree shifts are an editorial
sensitivity choice, not observed position errors. The next route admissions
must record a source-defined object, layer, start/end gates, branch rule,
reference time or averaging period, method, and evidence for any intermediate
waypoints. If the evidence supports only a reach, preserve that reach label.

No copied figures, source geometry, or downloaded provider data are added by
this audit. The seven existing span scenarios are regenerated with
`python analysis/build_ocean_current_gate_distances.py` and checked by
`python analysis/check_motion_almanac.py`.
