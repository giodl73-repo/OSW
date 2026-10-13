# Pacific NEUC component breadths: version 1

1. Use the complete Li, Liu and Lin (2018) article JATS XML archived by Europe
   PMC, DOI 10.1038/s41598-018-35469-2. Pin its exact bytes and license metadata.
   Review Mean Structures of NEUCs, Methods, and original Figures 1 and 2.
   Publisher PDF access is unavailable; do not claim PDF-page review.
2. Preserve the author's approximate 3° southern (NEUCS) and 1° northern
   (NEUCN) meridional breadths. These are distinct jet components in the Argo
   climatological mean, not seasonal endpoints of one current. The middle
   jet exists, but its numeric breadth is unresolved; never interpolate 2°.
3. Assign these only to the basin-specific Pacific North Equatorial Undercurrent
   identity, with explicit southern/northern component labels. Do not transfer
   them to the cross-basin generic NEUC, surface NEC, or Tsuchiya countercurrents.
4. Retain the 27.0 σθ potential-density-anomaly surface (kg/m³). It is not a fixed
   depth or vertically integrated layer. Source depths and the separate 2000 m
   reference level of the relative-geostrophic comparison do not define width
   depth bounds. The admitted widths describe absolute geostrophic Argo flow.
5. Source Argo mean period is 2004–2014. Preserve year precision without exact
   dates or a monthly calendar. Do not mix with SODA or LICOM 1969–2007 widths.
   No raw hydrographic profiles, daily currents or monthly width series are
   acquired or recalculated in this extraction.
6. Convert latitude spans with WGS84 meridional distance at a common equatorial
   unit-conversion origin, symmetrically around zero. Round to 10 km because the
   source is approximate. The zero origin and normalization limits are not
   observed jet coordinates or edges; display source degrees before conversion.
7. Preserve a meridional breadth, not a measured flow-normal transect. The
   source describes tilting jets and supplies no fixed measurement longitude,
   paired width endpoints, width-threshold definition or width uncertainty here.
   Figure 1's zero-velocity contours are not independently extracted edges.
8. Western source core locations near 8°, 13°, 18° N and 130°–135° E are context,
   without constant-latitude jet axes across the basin. No buffers, physical
   footprints or OSW state containment/intersection follow from this source.
9. Compare both component breadths on one abstract kilometre axis with degree
   labels and complete tables. Reuse one checked Rust scene across query, atlas
   and seasons; highlight a selected component without fabricating animation.
10. Keep annual range, confidence interval, width error and seasonal playback
    eligibility false/null. Source interannual/decadal variability, velocity
    standard deviations and significance contours are not width uncertainty.
11. Any reproduced source figure retains Li/Liu/Lin attribution, DOI, figure
    number, CC BY 4.0 link and change statement. Distinguish its observational,
    assimilation and model panels; never imply OSW reran or digitized them.
