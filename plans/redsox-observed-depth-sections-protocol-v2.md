# REDSOX native-source union grid, with frozen cores and honest sampling limits

Keep ALL17 original winter cases and v1 outcomes. V1 sampled salinity only at
velocity depths and can miss finer CTD dips or missing samples between those
nodes. V2 checks that limitation explicitly, without modifying frozen v1 files,
changing the17-case scope, thresholds, geometry, core, or source quality policy.
Archive/source/previous output exposure is explicit; this is not blinded.

Reproduce every frozen profile-depth result before refinement, using SAME
original parsers, velocity_layer/core selection, native source members and GSW
hydrographic depth conversion. Require exact core depth, native velocity, and
same-core interpolated salinity, not a tolerant comparison. No weaker/saltier
core replacement; unsupported and excluded cases remain exactly as v1.

Build a sorted union of every original LADCP depth and every native hydrographic
depth within the LADCP domain. Keep all original missing samples as nodes. No
rounded depth deduplication or fixed resampling. Interpolate velocity only from
adjacent finite native velocity samples <=20m apart and salinity only from
adjacent finite native hydrographic samples <=5m apart. No extrapolation. Retain
each point's original bracket indices/status and each edge's source bracket and
complete/missing/gap/outside status. An edge spanning an unsupported native
interval is a barrier even when BOTH endpoint values happen to be known.

Trace q>.2m/s AND S>=38 on this piecewise linear source representation, from
the unchanged velocity core. Evaluate each complete edge with separate q/S
crossings, retain first crossing from inside and both candidates. Missing points,
native gaps, hydrographic-domain limits and velocity sampling ends remain unknown.
Do not close with bed/header depth. Retain source-core index separately from
union seed index. No whole-plume/whole-current identity or full physical thickness.

The fine union bracket is NOT native velocity resolution, an error bar or new
independent observation. Keep ORIGINAL velocity/hydrographic brackets with each
boundary. Linear reconstruction is an explicit model between source samples,
not measured sub-bin velocity. Original coarse diagnoses remain separately
available; do not call any depth change an annual range or a correction to the
historical source observations. No physical cast/synchronization/reference-quality
upgrade, tidal correction, width/area/volume or new scalar reference admission.

Two declared output batches: lowerNorthernChannel5cases and winterSection3
12cases, each <2.4MB. Shared full17-case original native reservation44726scalars
remains; before decode also reserve maximum2*6000*17derived grid values jointly
under7MB. Native values <=250000, <=300LADCP/2000CTD rows, <=6000unionnodes PER
CASE. No extra fields/network requests. No success replay or per-batch source
budget reset. Bound each artifact/publication by unchanged caps.

All science, archive decode, interpolation, tests and builds CLOUDONLY on one
idleCPU sequentially. Local static editing/AST, document/metadata review, hashes
and exact retention only. Preserve810references, old1038-case scoped audit,
routeinventory48, all102eddyrefs and main/runtime/UI. Full depth goal remains open.
