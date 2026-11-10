# South Australian HYCOM 2D source selection v1

Declared 20 October 2026 before acquiring or decoding this new two-dimensional
velocity subset. The existing132E/100m/2012section and its12monthly outcomes
have been seen. Duran et al.(2020), original Figure2 on PDF page4, has now been
visually inspected; previous review covered AppendixB/C. No blinded claim.

## Gap and independent source context

The existing132Ediagnostic resolves12monthly component spans, but named-current
association remains unverified. A one-dimensional section cannot establish
along-current continuity or reliably distinguish a current from an eddy flank.
Acquire surrounding paired vectors before deciding that association. Do not
change the old diagnostic or promote it merely because it produces numbers.

Duran, Phillips, Furue, Spence and Bindoff(2020), doi:10.1016/j.pocean.2019.102254,
Figure2d/l shows132Eeast-GAB sections in CARS and MOM01. These are annual-mean
relative geostrophic and full-model fields, respectively, with non-monotonic
zonal-velocity shading in cm/s and separate meridional contours. Its drawn
transport-volume boundaries are not physical current edges. The source's
mean-field geography supplies context, not2012HYCOMaxis validation.

The exact retained original is
`research/source-data/duran-southern-australia-2020/journal-article.pdf`, SHA256
`e110e867b50df35706d4786ea493d25b82cd03733c683725324db856bfeb401e`.
It remains excluded from Git. No source figure or original image is redistributed.

## Frozen selection

- Same GOFS3.0 HYCOM+NCODA reanalysis dataset as the retained section:
  `https://tds.hycom.org/thredds/dodsC/GLBu0.08/reanalysis`.
- Both `water_u` and `water_v`; exact100m level; every daily00Zrecord of2012,
  including29February. Expected original indices6990–7355inclusive and depth19.
- Longitude130–134E and latitude38–32S. Expected original longitude indices
  3875–3925inclusive and latitude525–600inclusive. These are verified expectations
  from the old section, not permission to assume coordinates when decoding.
- Expected shape per component:366times ×1depth ×76latitudes ×51longitudes,
  or1,418,616paired vector positions. Keep all available and masked positions.
- Fetch the explicit DAP ASCII subset and DAS/DDS metadata, recording exact
  original response bytes/hashes, stable URLs, acquisition UTC time and headers.
  A40MBresponse cap covers the expected scalar text; oversized or truncated
  responses fail, not silently slice. No credentials or provider access bypass.
- Preserve native Int16 components, `-30000`missing flags, scale0.001m/s and
  offset0. Preserve coordinate association, source dtype, axis order, units and
  original clock. Reject different packing/units or an unavailable exact depth.
  Preserve provider datum metadata as supplied; WGS84 is an OSW distance/map
  convention where a calculation requires one, not invented provider metadata.

## Mandatory overlap oracle

At132E, compare **all55,632original component values** (366×76×2), including
missing flags, with the independently retained original section response:
`research/source-data/hycom-south-australian-2012/section.ascii`, SHA256
`524cc83b5c873848634e83dc9e03e35e885779757f0466bbcb978792b490ebc6`.
Require matching source coordinates, layer and every UTCtimestamp. No tolerance,
rescaling correction, sign flip, date shift or replacement by another model.
Abort on a changed overlap. Keep any provider metadata differences visible.

## Required source-quality outputs

Retain raw responses and a deterministic numerical subset with source masks.
Report paired availability by cell/date/month, finite ranges, clock coverage,
constant versus changing missing masks, axis/coordinate validation, overlap
results and original-file pins. A source map may show fixed grid locations and
recorded vectors, with missing values distinct from ocean absence. A constant
mask alone does not prove a coastline or bathymetric current edge.

No source averaging, filling, smoothing, rotation or new current mask is part
of intake. Any later monthly reduction must declare paired support and preserve
the original old-section rule of at leastceil(0.8×calendar days) for a cell.

## Subsequent inference stays separate

Declare an analysis protocol before calculating new continuity/axis decisions.
Evaluate the original selected132Ecores against along-flow direction, branching,
recirculation and source-region support. Crossing an investigation box or merely
having positive u cannot establish a named-current identity. Failure, alternative
interpretations and disconnected components remain visible. Do not force a
current path or fill a measurement counter.

No full width, flow-normal width, annual physical range, regional admission,
occupied polygon, physical OSW membership or NASA identification is authorized
by this source-selection protocol. The existing12outcomes remain unchanged
until an independently recorded scope/method review supports a specific claim.

## Native-coordinate precision amendment, 20 October 2026

The first request completed and parsed, but the original exact decimal-bound
comparison rejected its geographic selection before any scientific analysis.
Its response bytes were not retained because intake saved only after checks;
this custody defect is corrected before a second request. The preceding
protocol version had SHA256
`626e0c5b3a73ecf99bc5ddbea5421ba123a83fe0fab9225a4f4332e485e52c62`.

Before reacquisition, permit at most 0.00002 degree deviation of each native
endpoint from the declared decimal bounds, and 0.00005 degree deviation of
each native spacing from 0.08 degree. These accommodate single-precision
coordinate representation; they do not change source indices, domain,
resolution, exact depth, date selection or scientific criteria. Retain and
report the actual unrounded endpoints. Exact 132E overlap, all original
latitude/time/depth coordinates and all 55,632 packed scalar values still
must agree without tolerance. A larger discrepancy remains a hard failure.

Retain each complete provider response in an ignored acquisition staging
directory before decoding. Retain the validation error and staged originals
on failure; publish only after all source checks pass. Fixed source-map days
are indices 0, 182, 365, with all-date availability and a common all-date
speed scale. Direction glyphs are subsampled every fourth native cell, never
interpreted as trajectories, current axes or boundaries.

## Observed native-longitude spacing correction, 20 October 2026

The retained second response shows exact 130°/134° endpoints, but native
longitude increments of 0.0799560546875° and 0.080078125°. The largest
deviation from nominal 0.08° is 0.000078125°; the largest coordinate deviation
from the nominal linear sequence is 0.000068359375°. This falsifies the
assumed 0.00005° spacing allowance. Do not attribute it to an undocumented
provider implementation. The preceding amended protocol SHA256 was
`2be5a6d3f6d130119acb18a0ff42ca49f139cca60dc1c79f0f63325a325af408`.
All original time/depth/latitude coordinates and all 55,632 old packed
scalar values have independently compared exactly at 132°E. No new scientific
statistic or map has been calculated from the surrounding field.

Before further validation, request the coordinate-only DAP response for the
same time/depth/latitude/longitude indices. Preserve its original response and
require exact numeric equality of every coordinate against the cube maps.
This checks a separate provider response, not an independent model or source.
Reject differences. Preserve the original coordinate values throughout.

Keep the 0.00002° endpoint allowance. Latitude coordinates still must equal
the original section exactly. For longitude, require every coordinate to be
within 0.0001° of the declared nominal 130 + index×0.08° sequence, and every
positive native spacing within 0.0001° of 0.08°. Record the observed bounds,
minimum/maximum spacing and maximum nominal deviation in source quality.
These checks describe native coordinate representation; the exact separate
coordinate-response comparison and old scalar overlap are stronger identity
checks. No source index, period, depth, pairing, field or scientific selection
criterion changes. Reuse the retained originals; no third cube download.
