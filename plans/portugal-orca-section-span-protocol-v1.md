# Portugal ORCA section span protocol v1

## Evidence and calculation

Use the Portugal event `orca-2009-portugal-north-section` in
`research/named-current-published-observations.json`. Preserve its two reported
longitude/latitude limits, [-14.8,37] and [-13.5,37]. Compute their shortest
ellipsoidal separation with `pyproj.Geod(ellps='WGS84').inv`, divide metres by
1000, and round to the nearest kilometre for display. Retain the unrounded
calculation separately. This is an OSW calculation from published coordinates;
the paper does not report a kilometre width.

WGS84 is our calculation convention. The paper's coordinate datum and endpoint
rounding errors are unresolved. The shortest geodesic is slightly different
from distance along the 37 N parallel; neither is a reconstructed ship track.
Do not combine these distances into a physical uncertainty interval.

## Physical and temporal scope

The source identifies Portugal flow in the northern section, stations 19-23,
using adjusted inverse geostrophic transport and water properties. Keep the
surface/thermocline context (neutral-density layers 1-4) distinct from a fixed
metre slab. The intermediate flow does not establish the same current extent.
The source's transport uncertainty has units Sv and cannot become width error.

15 October-11 November 2009 bounds the cruise, not the exact occupation of this
band. Store it as cruise context; exact observation days remain unknown. The
box's eastern closure used 1992 observations, so the full model is not a
synoptic 2009 survey. Do not assign monthly samples or seasonal playback.

## Admission limits

This is a nominal local section span. It is neither a measured current axis nor
a diagnosed flow-normal width. Whole-current length, width, annual extrema,
uncertainty and geographic footprint remain unknown. Do not buffer a route by
this distance, rank whole-current widths, or fill missing seasonal frames.

Primary review: Perez-Hernandez et al. (2013), DOI 10.1002/jgrc.20227,
abstract, sections 2 and 6, Table 1 and discussion paragraph 40. Publisher HTML
and institutional PDF parsed text were available; original PDF bytes and page
images were not acquired. The frozen local event supports reproducible input
coordinates, not a checksum claim about the publisher's original document.

## Presentation

Show the two source limits on a section-distance graphic, identify the WGS84
calculation, and keep the cruise date limitation adjacent. Label any mapped
segment as a source section, never as an along-current route or physical edge.
Retain the existing independent 40 N surface component diagnostic separately.
