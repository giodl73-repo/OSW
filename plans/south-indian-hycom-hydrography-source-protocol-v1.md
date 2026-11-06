# South Indian 80E paired velocity/hydrography source v1

Declared before acquiring HYCOM values for this section. The older OSCAR
2013 component-span diagnostics and their resolution/association failures
are known. This is source preparation, not a blind test or a width admission.

Use GOFS3.1 GLBv0.08 expt53.X data/2013, with the already retained complete
provider DDS/DAS and coordinate response from the same dataset. Preserve
their bytes and original acquisition provenance. Exact native80E is central;
include its immediately adjacent native longitude nodes as sensitivities.
Keep every native latitude node between48S and30S inclusive (1e-5degree
representation allowance). Require exact provider15m and1000m z-levels.
No vertical interpolation, layer mean or assumption of uniform grid spacing.

Request water_u, water_v, water_temp and salinity together. Check Int16
packing, standard names, units, missing values, Float32 scale/offset, Earth
east/north velocity frame and in-situ temperature metadata. No conversion to
potential temperature, density or geostrophic reference velocity is admitted.
Select exact daily00Z Gregorian2013 timestamps by actual coordinate values;
missing dates remain explicit. Split checked source-index runs into at most
six dates, use at most two simultaneous requests and cap each response20MB.
Keep every successful original, URL, checksum, byte count, acquisition time
and failure. Components/depths/coordinates must exactly match the frozen plan.

Monthly means use identical valid times for all four fields at each native
cell and depth. Require ceil(80%*calendar days) common samples. Decode the
provider's Float32 packing constants as their exact binary32 values promoted
to Float64; sum valid packed integers in Int64 before scale/division/offset.
Keep counts, absent means and every month/depth/neighbor outcome. No filling,
filtering, outlier deletion, generated boundary nodes or post-result selection.
Use the existing fixed ZIP_STORED/NPY1.0 writer without changing it; retain
full-precision nullable JSON and Float64 arrays. Original responses stay inputs.

Stramma1992 was visually reviewed across all ten original pages. Front
station brackets are not current edges; table transports are not widths.
Large station spacings smooth the published speeds, and the paper explicitly
leaves width detail unresolved. Its eastern front may carry westward flow;
ACC and SIOC are distinct current bands with possible exchange. The80E choice
avoids transferring a western Agulhas Return section into the eastern naming
convention. Source velocity reference surfaces, historical dates and section
orientation differ from this dated model section. No paper reproduction or
isolated resolution-effect claim is made.

The two depths supply context, not the whole upper1000m field. Three nearby
meridians are correlated model samples, not independent observations or a
longitudinal axis survey. Native model salinity/temperature and total velocity
will support a separate, explicit feature-association assessment. This source
stage admits no named-current width, axis, length, annual extrema, NASA match,
state passage or seasonal footprint. Existing sources, all33 scientific
reports/operators and all170width/78reference rows remain unchanged.

Continue existing branch/draft PR83. No per-gap PR or main merge.
