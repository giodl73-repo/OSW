# Tsushima campaign paired-current depth scenarios

Use original Matsuyama1990 Table1 paired signed mean alongshore current values,
manually transcribed and visually checked against the retained original PDF.
Verify acquisition metadata PDFhash/bytes match the source facts. Do not download
or redistribute that copyrighted PDF. The source's common Table1 averaging
period is July26-August14,1980,not the longer A/B deployment toAugust25.

Keep all five original station pairs and frames. Positive alongshore is east90deg
at A/C/B/D and75degTRUE atE. Do not replace E's frame with east or the modern
HYCOM60deg frame. Depths are10m paired with30/70/110/70/70m forA/C/B/D/E.
No raw current-meter series is available; no temporal exceedance test is possible.

Before computing, declare eligibility: a finite positive shallow common-period
mean U and finite negative deep common-period mean U at the same station/frame
and averaging interval,with0<z_shallow<z_deep. Retain the open depth bracket
(z_shallow,z_deep). If the time-mean vertical profile is continuous there is at
least one direction change inside; uniqueness,monotonicity and identification as
the physical lower boundary of the current are not established. At stationA both
mean values are positive; retain its observations but NO bracket or extrapolation.
No weaker cutoff,alternative frame,other station or longer averaging period may
replace a rejected pair.

Define ONLY an explicit linear two-level scenario:

    z_zero = z_shallow + U_shallow / (U_shallow - U_deep)
                           * (z_deep - z_shallow)

Both velocities use the same cm/s source unit,so the ratio is dimensionless and
the output unit is metres. Require strictly interior output. Keep full calculation
precision in the derived artifact and round only display values. This is a
conditional interpolation of two observed campaign MEANS,not an observed exact
zero contour,current bottom,first crossing,time-mean of instantaneous depths,
surface-to-bottom thickness,profile fit or threshold penetration. Nonlinear
vertical structure can place a crossing elsewhere in the bracket or create
multiple crossings. Bracket width is neither statistical uncertainty nor an
annual/seasonal depth range. Do not assign a confidence interval or interpolate
among stations. Do not bridge unsampled surface0-10m or below the deep instrument.

Add a new source-specific evidence class/inventoryv5; preserve all731previous
references and immutable pieces/CSVcells. Each new row carries the two source
means/depths,positive frame,common dates,station,source row pointer/hash,open
bracket,linear assumption and derived report pointer/hash. Use the distinct metric
derived_two_level_mean_direction_change_depth_scenario. Exact physical boundary,
thickness,uncertainty,annual range,width pairing,volume and route/state/seasonal
integration remain ineligible. Retain all five audit records,including A's rejection.
No exact map coordinates have been extracted; do not invent geometry or route joins.

Do not use source modal width or Eq8 in this calculation. Those existing source
discrepancies remain unresolved; the paired Table1 means stand separately.
The source thermocline interval and H station profile are not zero contours at
the moorings. Instrument depths and local bathymetry do not establish current
bottoms. This single finite summer campaign does not establish a recurring cycle.

All calculations/tests run cloud only,sequentially on one idleCPU. No new ocean
field requests. Tests must preserve prior evidence,verify raw source pairs/frame/
period,unit-consistent formula,open bracket,all-and-only eligible records and no
physical/annual/volume promotion. Fixed publication caps2.5MB/file,3MBtotal; frozen
registerv48 unchanged. No runtime/UI/main modification.
