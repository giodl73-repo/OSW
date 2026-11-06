# ECCO current-depth feasibility gate v1

Purpose: establish whether a fresh ECCO velocity archive can support regional
model depth diagnostics for broad accepted currents. This is an access and
method specification, not an executable field operator or a new depth result.
No change to the preferred v53 reference inventory or 102 eddy size references.

## Evidence already reviewed

PO.DAAC product ECCO_L4_OCEAN_VEL_05DEG_DAILY_V4R4,
DOI 10.5067/ECG5D-OVE44, collection C1990404811-POCLOUD, describes daily
geographic EVEL/NVEL velocities, Z cell centers and Z_bnds interfaces.
Its regular 0.5-degree grid interpolates an underlying roughly 1-degree
MITgcm state estimate; interpolation does not add dynamical resolution.
The official ECCO v4r4 guide reports LLC90 and horizontal resolution 22-110 km.
This is not suitable evidence for an 8-km North Cape jet or narrow Tsushima
branch. Broad Alaska Current is a possible target, distinct from Alaska
Coastal Current and Alaskan Stream. No target identity has yet been validated
against fields. No route, point, date, index or bottom has been selected.

Reviewed official documentation:
https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_VEL_05DEG_DAILY_V4R4
https://ecco-group.org/user-guide-v4r4.htm
The first product read succeeded; a later repeat returned a timeout. That
source is now closed to further requests, mirrors and format substitutions.
Existing reviewed statements are retained; do not claim a fresh verification.
The prior subset-documentation call outcome was not retained across context;
therefore this protocol does not rely on it or repeat it. Access support is
not proven by the mere existence of an OPeNDAP link.

## Access gate

Administrative checks found no local .netrc/_netrc, no named Earthdata
username/password/token environment variables, and no GitHub Actions secret
names containing EARTHDATA, NASA or ECCO. This is limited to those checked
locations, not proof that the user has no account or every possible secret
is absent. No values were printed. Protected native data needs Earthdata
access; the public bucket metadata/checksums/images are not public native
velocity arrays. Direct protected S3 access is restricted to us-west-2, and
a default GitHub-hosted runner is not evidence of that location. Do not
assume temporary S3 credentials make that route viable.

Use a user-authorized secure cloud credential configuration; never request
credentials in chat, commit them, or print them. Do not reuse the older
ECCODrive WebDAV password convention for PO.DAAC access. No authenticated
request, credential transfer or cloud data retrieval is authorized by this
record alone. The user has been asked whether an account is available.

## Required before the first field request

1. Verify a fresh documented HTTPS server-side subset path, with provider
   closure preflight. Resolve actual granule identity, coordinates, units,
   dimensional shape, fill values, wet support and response byte bound from
   metadata. Metadata must not conceal a whole global array download.
2. Confirm cloud authentication and a bounded response without local native
   decoding. An inaccessible provider gate closes that target; do not switch
   mirrors, dates, versions, instruments or environments to evade failure.
3. Freeze a separate versioned executable operator BEFORE velocity values:
   accepted current ID; independently justified regional geographic gates;
   exact dates and indices; geographic component/bearing; core search window;
   primary velocity threshold and sensitivity choices; contiguous vertical
   tracing; mask and support/censor treatment; tie policy; error handling;
   expected profile/level/cell/byte counts and independent-question ledger.
   No outcome-dependent choice of axis, date, direction, cutoff or window.
4. Validate the new operator with synthetic missing-level, reversed-flow,
   threshold-crossing, dry-cell, disjoint-layer, edge-winner and coordinate/
   unit cases in the same cloud time budget before any field acquisition.

## Meaning of a future result

Retain selected location, time, model/version, selection basis, core depth,
upper/lower crossing brackets, resolved/censored status and threshold
sensitivities separately. Missing is not zero, seabed or no current. Trace
only finite adjacent supported levels; never bridge gaps or disconnected
same-direction flow. A support endpoint or last wet cell is not a detected
current boundary. Geographic EVEL/NVEL must not be confused with native-grid
UVEL/VVEL. Do not equate an averaged velocity contour with an average of
instantaneous boundaries. A few dated snapshots are not seasonal ranges.

A regional model threshold diagnostic is not an observed whole-current
physical depth. No parent/member scalar inheritance, annual range, common
length-width-depth footprint or volume follows from such a result. Publish
these distinctions with every admitted row, not only in a general caveat.

## Fixed execution limits

Scientific decoding, numerical assembly, geometry and tests cloud only,
offline sequential one idle CPU. No local field processing. All tests and
computation share 60 active seconds, signal handling and an outer timeout.
Fresh output directory. DescriptorQuery v3 for compiled reads; a truly
independent ECCO question starts prior 0/0, while any continuation carries
all charges. Caps remain 250000 numeric tokens, 32 MB unique JSON, 2.5 MB
packet, 2.4 MB whole artifact, 7 MB native data, 3-150 profiles, 40 levels,
20000 cells and existing geometry/node tolerances. Check exact geometry
semantics against the frozen native protocol before implementing.

If the product has more than 40 levels, stop before field acquisition unless
a prospectively justified <=40-level diagnostic window is fixed; report
truncated deep support as censored. Do not partition profiles/levels/jobs,
reset ledgers or obtain a whole field to crop after decoding. Provider and
failed/validated scientific versions stay frozen. No field request or
scientific test was made for this feasibility record. No UI/runtime/query/
WASM/server/main change is part of this task. Existing PR83 remains the
publication destination; no per-current PRs.
