# Native-client and full-coordinate diagnosis

After collection timeout41665233958and successful12endpoint urllibmetadata probe
41669996596, diagnose the actual netCDF4/netCDF-C client without reading ocean
velocity or salinity. Use the same fixed uv3z2022/ts3z2022URLs and native DDSshapes:
depth40,lat4251,lon4500,time2920. All values are native coordinate metadata,not
current-depth measurements. No alternate dates,gates,currentcore or classifier.

One worker,one attempt,one idleCPU. Persist an explicit receipt before importing
netCDF4,each dataset open,global metadata,coordinate descriptor,array read,close
and paired comparison. Coordinate-read helper accepts onlydepth/lat/lon/time;
model-field read names rejected. Reserve both datasets' entire coordinate arrays
jointly before reads under unchanged250000nativevalues/7MBconservativebytes.
Retain exact finite increasing arrays,units/indices/sourcemetadata and byte hashes.
Full paired arrays/timeunits/calendar must match; preserve pending stage if a call
blocks. No wrapper that weakens or bypasses original future scientific preflight.

The parent uses a120second subprocess wall deadline and retains the last worker
stage,complete arrays already saved,bounded process-log prefixes and outcome even
on worker timeout/failure. A4min step inside7minjob leaves artifact upload time.
This diagnostic does not retry whole collection or successful field requests.
No velocity/salinity fields or depth references are requested/admitted. Responsive
metadata alone does not prove client health;even paired coordinate success does
not prove current identity or physicalbottom/thickness/width/area/volume.

Run all tests and actual diagnosis CLOUDONLY. Local code/metadata/hash retention
only;no local analysis imports,numerics,tests or UI/server work. Fixed2.4MBsource,
2.5MBfile/3MBpublication caps. Retain exact completed diagnostic artifacts and
explicit limitations; prior791refs,eddybaseline,main/runtime/UI stay unchanged.
