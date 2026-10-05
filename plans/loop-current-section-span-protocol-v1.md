# Loop Current inflow section-span diagnostic v1.0

Effective 2026-10-04. Editorial diagnostic, not a published current width.
This extends the existing fixed-section threshold rules to the existing Yucatan
gate: 21.875 N, 86.875-85.125 W. The corridor and five source dates come from
the pinned Loop length experiment; they are not optimized for width results.

1. Use separately pinned NOAA LSA and GCOOS-hosted DUACS absolute surface
   geostrophic ugos/vgos fields on 2025-01-15, 04-15, 07-15, 10-15 and
   2026-09-25. Retain each product/version, date, response and regional SHA.
2. Sample at each product's native longitude centres within the gate, using
   the existing bilinear sampler at fixed latitude 21.875. Require both velocity
   components in all four stencil cells, even zero-weight cells; never fill masks.
   NOAA spacing is 0.25 degree; DUACS spacing is 0.125 degree. Interpolation is
   not additional observational resolution or independence.
3. Select the largest northward component inside that corridor; ties go west.
   Require at least 0.15 m/s. This diagnostic floor is not a universal current
   boundary or scientific approval of identity.
4. Walk adjacent samples west/east from that peak to the nearest 50%-of-peak
   crossings. Stop at a missing sample or corridor edge. Preserve each boundary
   and its stop reason. Missing either boundary means a null paired span.
   Never bridge a below-threshold region to a different peak.
5. Interpolate longitude linearly within each bracket. Measure WGS84 geodesic
   endpoint separation at the declared latitude. Display nominal to nearest
   10 km, halves upward. Preserve raw values and exact brackets.
6. Retain 40% and 60% scenarios. A finite sensitivity interval requires all
   three scenarios to have paired boundaries; otherwise it is null. Round
   the finite interval outward to 10 km. This is neither a confidence interval
   nor a measurement-error bound.
7. Preserve inner/outer grid-bracket separation and width in native cell
   spacings. Overlapping inner brackets have lower separation zero. Under four
   spacings flags resolution review; four or more is not boundary validation.
8. Group sampled nominal-value spans only within one product and year, retaining
   count and algorithm. These are sparse sampled values, never annual extrema,
   seasonal ranges or proof that the difference is entirely physical change.
9. This is a zonal half-peak northward-component span. It is not a flow-normal
   width, total-speed envelope, bathymetric passage width, ADT-contour spacing,
   width of a traced streamline, whole-current width or observed footprint.
   Retain null annual width, measurement uncertainty and whole-current width;
   ranking and whole-current admission false. Never buffer a route with it.
10. Both products can share altimetry inputs. Product differences are method/
    processing differences, not independent confirmation or uncertainty bounds.
    Gateway/layer/component/resolution and scientific identity review remain open.

Impact: existing Gulf Stream, NECC, Leeuwin and Kuroshio numerical diagnostics
retain their rules and values. No canonical measurement or annual range changes.
