# NwASC source-anchor regional reference connection

Declared2026-10-22 before calculating this connection, its bend scenarios or
map joins. The source prose and coordinates were already inspected; this is
not a blinded study. Continue draft PR83, with no additional PR or main merge.

## Fixed evidence

Hansen etal(2011),doi:10.1029/2011JC007375,paragraph10/original PDF page3,
gives P1 at62N,0deg30minW; P2 at62deg40minN,3E; S1 at62deg48minN,4deg15minE.
The author-provided reference points occur along the NwASC discussion for the
August2007-July2010 mean surface field. Use all three in that source order.
Retain the already acquired PDF checksum and source report. Do not infer that
these nominal reference coordinates are exact centerline observations.

The paper describes steering along the500m contour. No bathymetric array or
contour has been acquired for this calculation: the connection must not be
called a500m isobath, diagnosed jet axis, trajectory or physical current edge.
The possibly mixed P2 width does not remove the author's geographic reference
point. No P2 width or coastal-current width is inferred from this connection.

## Geometry and measurement rules

1. Longitude precedes latitude in OGC:CRS84/WGS84. Convert degrees/minutes
   arithmetically, preserving the sign of west longitude. Keep all three
   source anchors unchanged. The nominal reference is the two shortest WGS84
   geodesic legs P1-P2 and P2-S1. Sum their lengths; no coastline length,
   transport, speed, residence time or whole-current length is calculated.
2. Record unrounded calculations for decisions, then serialize distances to
   six decimals in km. Round public reference length to10km. Geographic
   reference length remains separate from the published historical3500km
   extent and from every qualified whole-current length rank.
3. Retain nine finite bend probes. On each leg, find its geodesic midpoint
   and displace it by-10,0,+10km along the right normal to the local forward
   geodesic bearing. Insert that point, preserving P1,P2,S1, and sum the four
   legs. Use the Cartesian product of the two offsets. The10km scale is an
   editorial geometry probe, not source resolution, positional uncertainty,
   width, confidence, annual variability or an inferred range of real axes.
   Round the displayed scenario span outward to10km. Do not suppress cases.
4. Densify geodesic legs to at most1km for land checks and10km for standard
   OSW display joins. Check all nine probes against both the coarse OSW land
   mask and the retained Natural Earth1:10M land5.1.1 archive. Clip the latter
   to the declared northern-European region using a separate reader; never
   mutate the frozen Madagascar reader's regional configuration. Reject
   admission on any land contact. These checks are cartographic, not surveyed
   coast, bathymetry, reef, navigational or subgrid clearance certification.
5. Display-state crossings and NASA crop overlap are editorial line/display
   relations only. Retain every scenario and exact source addresses. NASA
   crop recommendations do not identify this mean current in a simulation or
   dated movie frame. No physical containment or current-state passage.

## Presentation and integration

Add one regional reference route for the already admitted NwASC identity.
Preserve all77previous candidate rows, their source bytes and existing routes.
The old catalogue stays at its own source address; expose an explicitly
derived78-route projection rather than replacing the old source bytes.
Update the current's route plan and map capability from the new report.
Global current names retain hover/focus behavior. Provide a regional map,
source-anchor coordinates, reference length, bend-probe meaning, current-card
navigation and queryable record. No whole-current width or seasonal route
playback follows. All102identities,13published ranks and167widths stay fixed.

## Verification

Rebuild the candidate/map deterministically, verify source/archive/producer
pins, preserve all previous numerical reports and candidate records, and
reject changed anchors, invented dated geometry, physical-join promotion or
rank changes in native/WASM ingestion. Check the actual map, route card,
navigation, keyboard/mobile and unavailable seasonal playback. Run the
project roles review and fresh Linux report reconstruction in the same PR.

Computational geodesic display samples serialize to eight decimal degrees;
source anchors remain unchanged. This readback convention is not positional
accuracy or source-coordinate uncertainty. Geometry checks precede rounding;
rounded exported display samples must also remain clear of both land masks.
