# P14N hydrography: metadata clarifications before property inspection

The original CCHDO files were acquired after the SADCP velocities were viewed. Only dimensions, variable definitions, quality-code metadata and source comments have been inspected at this point; temperature/salinity values have not. This adds implementation detail to the fixed join preflight without moving its windows or matching limits.

The current CF-NetCDF contains 198 profiles, including repeat casts and both legacy cruise legs. Do not equate this with 198 independent stations or automatically merge profiles. It was converted with hydro1.0.2.3 / params0.1.21; original comments identify exchange edition20020812WHPOSIODAM.

Pressure is sea pressure in dbar. Temperature is in-situ ITS-90 degrees Celsius. Salinity is practical salinity on PSS-78, dimensionless. Preserve these names and original quality flags. Do not label temperature potential temperature, salinity absolute salinity or pressure depth.

For depth context use `depth_m = -gsw.z_from_p(pressure_dbar, latitude_degrees_north, 0, 0)` with GSW3.6.23, already pinned in requirements-test.txt. Retain original pressure. Zero dynamic-height and sea-surface-geopotential arguments are the conversion convention, not measured local sea-surface corrections. Reference: <https://www.teos-10.org/pubs/gsw/html/gsw_z_from_p.html>. Do not manufacture a depth-error interval.

Retain selected profile cells with converted depth0–350m for visual water-mass context, including component-specific QC flags and raw finite values. Mark acceptable support only when the source pressure, temperature and salinity flags are all WOCECTD2 and the corresponding values are finite. Report the100–300m cell counts separately; do not add a new hydrographic layer-mean estimator or vertically interpolate across gaps in this initial join.

The CF source comments identify `EVENT_CODE: BO` and the original summary contains BE/BO/EN rows. The WHP format defines BO as bottom time; BE/BO/EN denote cast beginning/bottom/end. Sources: <https://archive.cchdo.io/whpo.ucsd.edu/misc/sampsum.htm> and <https://cchdo.github.io/hdo-assets/documentation/manuals/pdf/90_1/chap3.pdf>. Verify that each selected profile's timestamp agrees with its unique BO summary event. Preserve BE/EN context if available. The fixed3-hour test refers to this nominal bottom timestamp, not the actual time a sensor traversed100–300m; no exact same-depth simultaneity is claimed.

The2001 temperature-correction notice in the current cruise page remains a source-history caveat. The later exchange conversion date alone does not prove whether that correction was applied. Do not reapply it or claim it is resolved without a primary processing record.

All qualifying3-hour/15km CTD–ADCP pairs remain candidates; multiple matches are preserved. This is correspondence evidence from a shared cruise, not independent width validation, a named-flow classification or boundary detection. Existing physical-width and annual-range flags remain false.
