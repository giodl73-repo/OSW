# Ursa-event contour digitization — protocol v1

Status: editorial figure-derived candidate; independent scientific review pending.

1. Use only Figure 3's 2021-03-07 panel in the complete publisher original
   Johnson Exley et al. (2022), doi:10.3389/fmars.2022.1049645. The paper's
   Section 3.2 describes temporary detachment in early March. Attribute this
   candidate to the publication-scoped Ursa event; retain that interpretation
   as unverified and do not crosswalk a register or NOAA detection identity.
2. The bold black line is the mapped surface Loop Current SSH contour, while
   colors are deep reference pressure, SSH_ref. Trace the line, never a colored
   patch, instrument array, bathymetry, frame or circle fitted to an assumed ring.
3. Preserve the Methods' printed `0.65 cm` with unresolved physical unit. Image
   tracing records the depicted curve without reconstructing a numerical SSH
   field. Do not silently replace cm by m. No numerical altimetry is acquired.
4. Pin the complete original XML, source figure, preceding source-panel audit,
   method, state geometry and dependencies. Preserve CC BY 4.0 attribution,
   original source figure access and the OSW adaptation notice.
5. Search only the panel interior: [1122,678,1380,925] source pixels, xyxy.
   Require one dominant hollow closed dark loop, with both outer and inner
   traced edges strictly inside the search box. Never repair gaps, dilate a
   mask, smooth/reconnect lines or close along the frame.
6. Use max(R,G,B) below 40, 70 and 100 as three declared segmentation cases.
   Each must yield one dominant loop above 20,000 source pixel squared, with
   a direct hole child of comparable area. Use CHAIN_APPROX_SIMPLE to compress
   exactly collinear pixel vertices. Keep both stroke edges in the audit and
   explicitly reject any non-simple pixel ring instead of repairing it.
   Threshold 100 produces two rejected self-touching rings; retain those
   source pixel paths and reasons with null geographic polygons. Instrument
   dots and deep-color encroachment are artifacts, not physical boundary detail.
7. Georeference using manually reviewed common figure axes: -89 and -85 degrees
   longitude at source x=1121 and 1383; 28 and 25 degrees latitude at y=674
   and 894. These are transferred from the complete figure's repeated map grid
   and bottom-left geographic ticks, not inferred from the crop frame's lower
   edge. The figure does not specify a geodetic datum or map projection.
8. Store the threshold-70 outer edge as the nominal polygon, including original
   pixel vertices and seven-decimal display coordinates. Decimal precision is
   not survey accuracy. Test both stroke edges for all three thresholds, each
   under nominal and sixteen independent +/-3-pixel axis-anchor shifts: 102
   planned scenarios, 68 valid polygons from four accepted edge/threshold
   choices. Two threshold-100 choices cannot enter geographic scenarios.
   Keep the failures, case-level overlap fractions and envelope summaries.
9. Intersect only with existing coast-masked approximate OSW display polygons.
   Report display-area fractions and tested scenario ranges; they are not
   probability, physical uncertainty bounds or confidence intervals. Every
   whole-eddy physical `contained`/`intersects` decision stays unresolved.
10. Package the dated figure proxy as a candidate, separate from verified
    provider boundaries. Do not infer center, radius, perimeter-as-current-
    length, width, volume, annual margins, persistence, recurring seasonality or
    a NASA individual identity. NASA crop overlaps are geographic navigation
    only; retain the declared 2021-2023 model years. The event year is in range,
    but individual-event alignment remains unresolved.
11. Regenerate and compare the pixel/coordinate/state evidence in Python. Bind
    the exact audit and candidate/geometry projections in native Rust and WASM;
    re-signed promotions, date/owner changes and geometry mutations must fail.
12. Show the source curve and the digitized candidate together, with date,
    boundary interpretation, source, uncertain datum, calibration scenarios
    and state assessments accessible in text as well as on the map.
