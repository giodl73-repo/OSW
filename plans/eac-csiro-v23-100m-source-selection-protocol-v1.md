# East Australian Current: CSIRO 100 m source selection, v1

Declared 18 October 2026 after reading provider metadata, the 2024 data
descriptor, the November 2023 gridding procedure and NetCDF attributes/shapes,
before decoding the selected field values or calculating any new dimensions.
The source's published figures have been seen. This is an exploratory source
selection, not a blinded study or a current-width admission protocol.

## Exact product and selection

- DOI: `10.25919/sfw7-hc46`; CSIRO collection common ID 52949, collection
  record ID 69711, metadata version 23, data version 19. Preserve both version
  numbers. The retained NetCDF citation says v19 and its creation date is
  November 2023; the metadata record was published in November 2025.
- Provider file ID 67390004, named
  `EAC_filled-daily-distance-depth-gridded-product_20120401-20220727.nc.zip`.
  Complete ZIP length 381,438,579 bytes, SHA256
  `0d3a84a6042b3c4bcec123e24610da0dc7d4c8787db106465ee5297fa38d6ff4`.
- Complete uncompressed NetCDF length 8,108,045,936 bytes, SHA256
  `d27c6d424cd3ab9f2afdb9d353af45ba7a29bd162f3d8a8db693186ece6bef2f`.
  The original ZIP member CRC32 `4f6113b3` was verified through its entire
  contents. Local filesystem compression changes storage, not source bytes.
- Select the exact **100 m** source depth, all **3,770 times**, all **124
  geographic array positions**, and these eight original fields: `UCUR`,
  `VCUR`, `TEMP`, `PSAL`, `UCUR_uncertainty`, `VCUR_uncertainty`,
  `TEMP_uncertainty`, `PSAL_uncertainty`. No nearest-depth substitution.
- Retain complete `TIME`, `DEPTH`, `LONGITUDE`, `LATITUDE`, and `BOTTOM_DEPTH`
  coordinate arrays and all source attributes. Verify source dimension order
  `(TIME, DEPTH, LONGITUDE)` before slicing. Preserve float64 values, NaN
  payloads/masks, chronological order and coordinate association exactly.
- No date, season, velocity, uncertainty or completeness filter determines
  membership. No rotation, spatial smoothing, filling, masking, clock rounding
  or replacement by an observed-only product is performed by OSW.

## Interpretation and outstanding source questions

The source is a processed observational product made from SOM-filled mooring
records and spatial mapping. It is not an archive of 3,770 independent daily
crossings. The descriptor reports a five-day filter, daily output, a deployment
gap between 2013 and 2015, and approximately 1–2 km output spacing against
roughly 10–65 km mooring separation. Preserve the actual supplied time axis
and missing masks; determine availability from the arrays, not a guessed
calendar interval. No long gap is filled by OSW.

`UCUR` and `VCUR` are eastward and northward components referenced to true
north. The paper's separate minus-20-degree analysis rotation is not applied
during acquisition. Geographic coordinates describe the fixed source array,
not moving current edges or a current centerline.

The uncertainty fields are retained with their exact provider names, units,
attributes and missing values. The NetCDF names them `*_standard_error`; the
descriptor describes propagated instrument, reconstruction and mapping
contributions. Do not assign a universal confidence level, Gaussian sigma,
independence assumption or lateral-boundary error from those labels alone.

Preserve two documentary disagreements without silently correcting source
metadata: the NetCDF lineage says it removes flags 1/2/5 called “good”, whereas
the descriptor says those flags are retained; the file lineage says nearest
neighbor mapping, whereas the descriptor and version-23 collection metadata
say natural neighbor. Inspect available processing code and retain unresolved
scope where the precise final spatial mapping cannot be independently bound.

Bathymetry, bottom boundary conditions, missing instruments, a deployment gap
and an unavailable velocity sample are different concepts. Preserve source
values even if a later quality assessment identifies a questionable cell.
Any proposed exclusion or physical width operator requires its own declared
protocol and sensitivity review. No annual width extrema, scalar whole-current
width, geographical boundary, ranking or seasonal current polygon is admitted.

## Reproducible outputs and checks

Store a deterministic compressed NumPy subset with eight `(3770,124)` fields,
the five complete coordinates, header and acquisition receipts. Record each
array's dtype, shape, byte count and SHA256 in source order. Check every subset
array against a second read of the original NetCDF and preserve all missing
positions. Retain the source archive and full NetCDF locally; do not add the
8 GB original or temporary signed download URLs to the repository.

Quality reporting must include per-field finite/NaN counts, nonfinite values,
time support and gaps, year/month membership, geographic association, source
depth, field/uncertainty masks and negative uncertainty checks. A standalone
source figure must show dated fields, uncertainty availability, fixed-array
geometry and missing periods before dimensional analysis begins. Default
offline verification uses the pinned retained subset; explicit original-source
verification is a separate reproducible operation.

Credit: Sloyan, Cowley and Chapman; CSIRO, IMOS, NESP and the Marine National
Facility. Dataset CC BY 4.0. Data descriptor: Sloyan et al. (2024), Scientific
Data 11, 10, doi:10.1038/s41597-023-02857-x. Gridding procedure: Cowley and
Sloyan, November 2023, provider supporting file ID 8826.
