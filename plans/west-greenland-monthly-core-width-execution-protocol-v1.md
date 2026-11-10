# West Greenland regional core diagnostic: execution custody v1

Prepared for one prospective, cloud-only case. The numerical choices are in
`plans/west-greenland-monthly-core-width-protocol-v1.md`. Neither file alone
authorizes reading originals: a committed transitive preflight and reviewed
workflow are required first. Preserve this version after original execution.

## Inputs and prerequisites

Require successful source-header run 40092026859, sample-support run 40093031002
and observation-view run 40094342378 with their retained execution reviews.
Restore original artifact 12558929959 from the first source run, without a fresh
provider download. Verify the full archive SHA, exact first custody, directory,
all declared member metadata and the exact source header report. Select one
ADCP at each LS1–LS8 by header schema, not a filename suffix. Check each selected
member SHA, size, CRC and reconstructed header before reading arrays.

Read only TIME, UCUR, VCUR, supplied time-varying DEPTH and surveyed coordinate
variables. Require the declared east/north identities, units, calendar, TIME/bin
axes, finite singleton positions and WGS84 source reference. Retain coordinate
attributes and uncertainty. Do not convert nominal depth or pressure to a layer.

Project WGS84 inverse distances/azimuths from LS4 onto the declared along and
offshore references. Require increasing transverse position LS1 to LS8. Keep
along-reference offsets so section obliquity remains inspectable. No endpoint
or station is admitted as a current boundary or state intersection.

## Retained traces and interpretation

Retain every original aligned hour index and signed alignment offset, moving
layer rejection code, cross component, dense unfiltered/filtered along-series,
joint eligibility mask, filter segments, station losses, monthly conditional
means, support denominators and all three threshold results. Both edge bracket
indices and station IDs accompany a resolved span. No aggregation hides a
censored, missing, merged, weak, off-anchor or insufficient-support result.

Hourly traces remain in the cloud artifact as a bounded NPZ, never an automatic
local sync. The JSON report and static SVG are small review artifacts. A
successful calculation may produce zero resolved spans; that result does not
close the physical measurement gap. The figure must show support/censoring and
the regional metric beside any number. Inspect it before admission.

## Resources and immutability

One shared serialized cloud job, one CPU, low priority, numeric workers one,
2 GiB available disk/memory, at most 64 MiB per raw member/decoded array,
20,000 hourly grid slots, 64 MiB compressed traces and 8 MiB JSON. Use one
private exact-byte temporary NetCDF file at a time and remove it. Reject
oversized outputs instead of truncating. Write outputs only if absent or
byte-identical. No source URL is fetched by the producer.

Pin NumPy 2.4.1, SciPy 1.17.1, netCDF4 1.7.4, pyproj 3.7.2 and pytest 8.4.2 in
the workflow. Bind operator, numerical kernel, both test files, both protocols,
source visual reviews, prerequisite execution reviews/reports, workflow and
role review, plus all imported frozen helper dependencies, in the prospective
preflight. Run synthetic fixtures before restoring originals. No local builds,
original arrays or browser tests; no working-data publisher or scientific release.
