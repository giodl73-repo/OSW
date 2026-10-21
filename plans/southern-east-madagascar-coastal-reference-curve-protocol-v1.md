# Southern East Madagascar coastal reference curve, version1

Predeclare a new geographic construction after the paired coastline experiment
confirmed all27 earlier coastal scenarios intersect both land products. Retain
those failures and the farther-offshore alternatives unchanged. Do not fit the
new curve to the independently reported approximate650km current extent.

## Geography and geometry role

Nauw et al.2008, Introduction2, identifies the eastern Madagascar southern
branch from approximately20S toward Cape Sainte Marie near25deg30minS;
Introduction6 leaves downstream paths unresolved. Use that coastal branch
only. Natural Earth1:10 million land5.1.1 supplies geographic coast context,
not bathymetry, source current positions or a velocity axis. Every new line
is an **OSW offshore coastal reference curve**, not a measured current route.

## Fixed construction

1. Use the retained original Natural Earth archive and the regional land
   extraction already specified by the coastline comparison. Select the
   polygon containing the interior reference point47E,23S. Reject ambiguous
   or absent ownership. Its northern clipping edge at18S must not enter a
   selected route.
2. Transform that land to local azimuthal equidistant coordinates centered
   at47.5E,23S, WGS84, metres, with explicit longitude/latitude order.
   Construct exterior buffers at10000,25000 and50000 projected metres, with
   round joins and8 segments per quadrant. These are arbitrary cartographic
   offset parameters, not observed offshore core distances or current widths.
   Projection buffers are not exact geodesic coast-distance contours.
3. Transform exterior contours to WGS84 longitude/latitude. Intersect each
   with start latitude19.9,20.0 or20.1S; select the easternmost intersection.
   Intersect with end longitude45.2,45.3 or45.4E between24 and28S; select the
   southernmost intersection. These exact gates are OSW conventions near the
   source's approximate coastal regions, not source station coordinates or
   exact named-current endpoints.
4. Retain all27 offset/start/end combinations. Extract both contour arcs
   between the gates; use the shorter WGS84 geodesic polyline sum. Reject if
   the selected arc leaves45–51E or27.5–19.5S. This prevents a northern or
   western-island/clipping-edge shortcut from representing the eastern branch.
5. Simplify the selected contour by250 projected metres, preserving its
   endpoints. This controls cartographic detail only. Compare full versus
   simplified WGS84 lengths and retain both; never erase a failed case.
   Test both against the original finer land, with geodesic densification
   at no more than1km. Require strict empty intersection; no coastal buffers
   or numerical thresholds can turn contact into clearance. Also record
   coarse OSW land contacts separately rather than moving a route to fit it.
6. Nominal convention:25000m offset,20.0S start,45.3E end. Report exact
   calculated lengths to0.001km as computational readback, not accuracy.
   Preserve all27 geometries; export coordinates to8 decimal degrees only
   after analysis, then recheck exported geometry for land contact and length.
   Public nominal length is rounded to100km; round the scenario envelope
   outward to100km. The range is convention sensitivity, not physical width,
   seasonal motion, statistical uncertainty or annual extrema.
   Normalize signed zero in derived length-difference readback only; never
   round input geometry or land-contact decisions before analysis.

## Admission boundary

Where all declared gates pass, the curve can be an explicitly editorial atlas
reference with its sourced finer coastline, inputs, method and alternatives.
Keep source650km rank12, April2001 width120km and all prior quantities unchanged.
Explain any length difference without calibration or source-error inference.
No geometry date, fixed depth, speed threshold, physical state passage, occupied
area or seasonal playback follows. State intersections and NASA crops remain
navigation joins. Do not draw the undated curve as an April2001 observed axis.

Test the geometry operations with simple synthetic coasts, holes, gate choices,
wrapping arcs and rejection cases; reproduce every retained case. Bind exact
source/dependency/figure hashes and current ownership through Rust/WASM, with
negative promotion and omission tests. Supply atlas/card/query and textual
equivalents, keyboard access and320px review. External scientific axis review,
bathymetric correspondence and annual geometry remain open.

Coast-offset curves form a separate comparison class from waypoint reference
paths until their conventions are made comparable. Include the curve in atlas
navigation and the route inventory; exclude it from published length rankings
and the existing waypoint-reference ordering. Preserve all prior candidate
rows and their ordering metadata in the working catalogue extension.
