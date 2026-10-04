# IngÃ¸y model section sampling protocol v1.1

Status: research diagnostic, not canonical current measurements. Date: 2026-10-03.

## Fixed acquisition rules

Use the Norkyst v3 z-depth hindcast archive for 2024. Select the fifteenth of
each month at 12:00 UTC and depth 10 m before examining values. These twelve
hourly snapshots are neither monthly means nor seasonal climatology. Native
model spacing is 800 m; request every fourth grid cell (3.2 km) within fixed
X indices 2420:4:2616 and Y indices 576:4:764. Preserve raw ASCII responses,
each day's DAS metadata, URLs, SHA-256 hashes, packing and source coordinates.
Existing pinned bytes may not silently change on rerun.

Source fields are eastward and northward total model velocities, salinity,
sea mask and longitude/latitude. Decode fill before scale/offset. Velocity
scale is 0.001 m/s; salinity scale is 0.001 with offset 30. Inspect each day's
metadata rather than assuming identical packing or license from the first file.
The individual hindcast metadata identifies Norkyst_v3 and CC BY 4.0.

## Fixed section and rendering

Longitude 24 E, latitude 71.10 to 73.00 N, at 10 m. Sample every 0.01 degree
latitude using bilinear interpolation in the source polar stereographic grid.
Require all four corners to be wet and non-fill. Otherwise record null. Check
projected source coordinates against lon/lat to within 1 m. Distance is WGS84
geodesic distance from the selected southern limit. Approximately 1.1 km display
spacing does not add resolution to the 3.2 km source subset.

Use fixed axes across frames. Plot salinity separately from eastward/northward
velocity components, preserving missing segments. Advance discrete snapshots;
do not interpolate unsampled dates. Playback is user initiated, can be paused,
stops on manual selection and stops when the page becomes hidden. There are no
motion tweens. Preserve dates, layer, model identity and credit with every frame.

## What cannot be inferred

This section is a coastal-to-offshore regional diagnostic, not a fitted
flow-normal transect or exclusively the Norwegian Coastal Current. Its limits
are OSW-selected, not physical boundaries. Total model velocity includes tides
and weather effects. Do not infer a current footprint, along-current length,
representative width, annual extrema, seasonal averages or state containment.
No salinity or velocity threshold has been admitted as a current boundary.

Monthly averages require full within-month sampling and tidal treatment.
Width inference requires an explicit water-mass/velocity definition, fixed
section support, boundary bracketing and independent physical review. Longer
annual animation needs a suitable spatial field subset, separately validated
frame geometries and OSW state joins.

## Credit and provenance

Modified Norkyst v3 hindcast data: MET Norway and Institute of Marine Research;
Albretsen, Sperrevik and Simonsen (2026), hindcast archive. Model description:
Christensen et al. (2026), doi:10.5194/gmd-19-2785-2026. OSW selects the subset
and interpolates profiles. CC BY 4.0 attribution and modification notice appear
on the page and in downloadable data. No scientific admission is implied.


## Synchronized regional field maps (v1.1)

Map the same pinned 48 by 50 cell subset at every selected date. Use the
original polar stereographic grid in relative projected kilometres, equal
axis scale, and source-coordinate latitude/longitude contours. The patch is
entirely offshore; it does not include a coastline. Label its role as a regional
model field rather than the Norwegian Coastal Current's occupied extent.

Salinity colors use fixed limits 33.0 to 35.2, with under/over colorbar ends;
record any clipped cells. Show velocity at every fifth subset cell. Rotate true
east/north components into the map plane by projecting a 1 km geodesic direction
probe at each position, then normalize direction while preserving speed. Arrow
reference is 0.5 m/s, scale 0.07, fixed across dates. Displaying east/north
components directly along tilted source X/Y axes is incorrect. Arrows show
instantaneous model velocity, not trajectories or measured current axes.

Draw the fixed 24 E profile section independently of velocity arrows. Both map
and profile use the same timestamp, depth and pinned receipt. Switch frames
discretely, with no advection animation between unsampled dates. Pin map files,
rendering rules, source hashes and generator. These field patches supply no
named-current boundary, width estimate, state-footprint join or annual extrema.
