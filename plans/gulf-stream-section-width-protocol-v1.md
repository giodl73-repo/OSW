# Gulf Stream daily section-span candidate v1.0

Effective 2026-10-03. Research-only derived candidate, not a published width
or official current boundary. Applies to fixed 70 W meridional section only.

1. Use pinned NOAA LSA absolute surface geostrophic ugos/vgos subsets and
   native latitude centres in 35-41 N. Sample at 70 W with the existing bilinear
   wet-cell interpolation; require both components. Do not fill missing cells.
2. Select the largest positive eastward component in that window, ties to
   lowest latitude. Require at least 0.15 m/s; this is an editorial diagnostic
   floor, not a universal current boundary or scientifically approved identity.
3. On each side, walk adjacent profile samples from the peak to the nearest
   crossing of 50% of its eastward component. Stop at missing data or window
   edge; either missing boundary means unknown width. Do not bridge separate
   peaks across an intervening below-threshold region.
4. Linearly interpolate boundary latitude within each native-grid bracket.
   Measure WGS84 meridional boundary separation. Round nominal to nearest
   10 km for display. Preserve unrounded diagnostic, source profile and brackets.
5. Also evaluate 40% and 60% thresholds as finite boundary-choice sensitivity.
   Keep all outcomes; only complete paired boundaries supply sensitivity spans,
   rounded outward to 10 km. This is not statistical or annual uncertainty.
6. Record grid-bracket separation bounds as geometric sampling brackets only,
   not confidence/error bounds. Record nominal width in native 0.25-degree
   cell spacings. Under four spacings is flagged for resolution review; even
   four or more does not independently validate the boundary.
7. This metric is a meridional half-peak eastward-velocity section span. It is
   not a flow-normal jet-coordinate width, total-speed width, full envelope,
   water-mass width, current footprint or width of the plotted streamline.
8. No local width buffering, width-based state join, length-times-width area,
   canonical rank or annual extrema. One day per month is not a monthly mean.
   Source processing changes are retained. Scientific identity, component,
   orientation and boundary/resolution validation remain open.
9. A yearly group may record the min/max of its sampled rounded candidate
   values, with sample count and processing versions. Label this a sampled
   value span, never annual extrema, error bounds or isolated physical change.

## Method context and impact

Archer et al. (2017), doi:10.1002/2017JC013286, section 3.4 uses 50% of core
speed in a rotated jet frame for HF-radar Florida Current observations; its
Appendix A rotates velocity and section geometry. It motivates a relative
threshold, but this OSW fixed-meridian/eastward-component calculation does not
replicate that method, location, sensor or reported numerical widths.
https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017JC013286
Read 2026-10-03. This is a current-specific addition under the general width
protocol v1.1; published Northern/Azores/Mediterranean values remain unchanged.
