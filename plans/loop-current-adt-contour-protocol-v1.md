# Loop Current ADT contour comparison v1

Status: local methodological comparison; source-use, endpoint, effective-resolution
and scientific admission remain open. Extends the dated surface experiment.

## Compatible quantities

Use the exact 25 September 2026 GCOOS response containing Copernicus/DUACS
absolute dynamic topography (ADT above geoid, m) and surface absolute geostrophic
ugos/vgos (m/s), NRT 0.125-degree product version P1D_202411. Preserve null masks.
This is a different product/method check against NOAA RADS, with shared altimetry
inputs possible. It is not independent observational confirmation. The provider
labels daily averages at midnight but supplies no time bounds in this response;
do not fabricate an exact averaging window.

## Finite contour search

Contour ADT levels 0.05 through 1.50 m inclusive at 0.01 m spacing with contourpy
serial algorithm, separate lines and corner_mask=False. Full masked quadrilaterals
are excluded; never bridge a missing corner. These are absolute ADT contours,
not the demeaned 0.17 m method. No guessed Gulf mean or borrowed MDT is added.

Clip each contour to the editorial rectangle 98–81.5 W, 21.875–31 N. Retain only
open segments with one endpoint on the Yucatan gate (21.875 N, 86.875–85.125 W)
and the other on the Florida gate (81.5 W, 23–25 N). Orient Yucatan to Florida.
Reject missing endpoint velocities, southward inflow and westward outflow.
Closed rings or disconnected contours cannot be appended to complete the path.
These gate conventions match the prior experiment and still require bathymetric
and geographic review. Count rejected clipped segments, including those without
both gateways; preserve every gateway-connected candidate and its rejection.

Measure WGS84 geodesic length over retained six-decimal coordinate vertices.
Divide each leg into equal geodesic pieces of at most 10 km, sample speed at
each midpoint with strict four-wet-cell bilinear interpolation, and compute
length-weighted mean speed. Reject any missing sample; do not average only wet
parts of a candidate. Require mean speed at least 0.10 m/s. Choose the greatest
mean speed among eligible segments, never shortest or nearest the desired length.
If none are eligible, keep the result unresolved. A best level at either search
edge signals an incomplete scan and blocks a resolved selected estimate.

## Comparison and reporting

This implements a declared finite approximation inspired by the maximum-velocity
contour method discussed by Laxenaire et al. (2023), sections 2.3.1 and 3.1.1,
doi:10.3389/fmars.2023.1080779. It is not a full reproduction: original supplemental
implementation, gate positions and all algorithm details have not been recovered.

Report selected diagnostic length rounded to 100 km, retaining 0.1 km calculation
readback. Report NOAA integration and DUACS contour lengths separately for the
same source date. Their difference is product/method disagreement, not confidence
or an annual range. The set of all scanned contours is not a physical width or
length uncertainty interval. Neighboring ADT levels remain selectable evidence;
no ranking, width, annual extrema or named-eddy identity is admitted.

Before admission, recover original methodological details, test scan spacing and
gateway conventions, repeat dates across observed regimes, review effective
resolution/near-coast masks, and complete scientific and source-use review.
