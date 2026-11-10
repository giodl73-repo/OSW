# Makassar depth-surface terrain compatibility screen

The current programme now has59explicitly assumed depth-surface patches and12
partial component-volume scenarios in Makassar. Test those surfaces against
independent gridded terrain without converting seabed depth into current depth.
Preserve all original surfaces,volumes,source pointers and missing NorthCape slots.

This is a genuinely NEW environmental terrain-context case,not a retry of any
velocity/mooring/current-field source or a renewed native velocity budget. Ordinary
reads of retained typed depth descriptors use DescriptorQueryv3 with explicit
zero prior counters,250000numeric/32MBuniqueJSON/2.5MBpacket caps,reservations/cache.
The new terrain case additionally accounts the descriptor scalar reservation,
metadata(2000numeric tokens),terrain pixels and derived-analysis scalar allowance
together under250000scalars before any provider request. No old source-data,
native velocity arrays,prior producers or scientific validators are read/rerun.
The current-profile3–150profiles/40levels limits are not reinterpreted as a terrain
grid: no new current profile is collected. The terrain-specific two-dimensional
case is capped at6000pixels and6000comparison-point occurrences,below20000cells.

Primary source metadata identifies NOAA/NCEI's DEM Global Mosaic ImageServer:
https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_global_mosaic/ImageServer
and its query/exportImage operations. It is a heterogeneous service; do not accept
its default mosaic. One bounded metadata query intersects the predetermined
Makassar bbox and filtersName/ProductName/DemName forETOPO2022. Reject errors,
truncation,zero/more-than16rows,unknown products or unresolved15arcsecond identity.
Prefer explicitly named bed elevations; surface/bed are equivalent outside the
ice sheets here. Lock the selected exact raster IDs for the one numeric GeoTIFF
export; never substitute another DEM,host,format,epoch or default rendering.

ETOPO2022primary documentation states WGS84horizontal coordinates and elevations
in metres relative toEGM2008geoid(nominal mean sea level approximation):
https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/docs/1.2%20ETOPO%202022%20User%20Guide.pdf
Dataset citation:NOAA/NCEI ETOPO2022Global Relief Model,doi:10.25921/fd45-gt74.
Metadata is not evidence of surveyed bathymetry at every cell; no source-ID grid
or direct-sounding identification is claimed.

Plan exactly one bbox from all59source footprints,rounded outward on a0.04degree
grid with one-cell margin. Never retune resolution or choose only favorable
patches after a prospective cap failure. Export nearest-neighbor,F32,one-band,
EPSG4326,losslessTIFF,with raster functionNone. Verify CRS,dimensions,dtype,bounds
and affine pixel registration BEFORE array decode. Read all reserved pixels once.
This is sparse coarse terrain sampling,not inspection of all native15arcsecond
cells; thin land/isolated shoals and between-sample conflicts can be missed.

Use every exported pixel center inside each original rectangle. Evaluate the
same original central bilinear upper/lower surfaces at that point. Compare lower
depth with nominal water-column depth=surface_offset-ETOPOelevation for fixed
offset scenarios-20,0,+20m. These are sensitivity assumptions,not observed sea
levels,datum corrections or uncertainty/confidence bounds. Current depths and
ETOPOreference are not independently reconciled. Report sampled conflicts and
nonpositive water columns,offset sensitivity,NoData and no-sampled-conflict as
distinct outcomes. No-sampled-conflict is NEVER complete terrain clearance.
Do not clip/recompute a current boundary at the bed or alter the original volume;
the screen does not establish actual ocean current thickness,flow continuity,
physical current identity or physical volume eligibility.

One original case has exactly TWO provider operations(metadata plus field),no
retry/redirect/mirror/alternateformat. Reserve each target durably before request,
cap metadata100000bytes/field1000000bytes and cumulative raw7MB,retain raw bodies
before parse on success/error. No failed target replay.25srequest timeout plus
one absolute60second deadline shared with synthetic tests/SIGTERM handling.
Fresh output directory. Keep source/output total below2.4MB. Artifact upload only
after producer terminal; retain any failure ledger/raw bytes and do not rerun.
Cloud-only scientific parsing,terrain decode,geometry,numerical assembly and tests,
sequential on one idle CPU; local static/AST/manual primary metadata review and
exact byte custody only. Keep all canonical908references/old projection inventory,
main/runtime/defaultquery/UI/WASM/102eddy references unchanged.
