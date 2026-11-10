# REDSOX published layer-thickness references

Admit the twelve channel/layer/cruise mean-thickness records in Peters et al.
(2005), Table 2, printed page 577 / PDF page 9. Each record retains the
reported mean, sampled minimum, sampled maximum and CTD/LADCP cast count.
The original page was visually checked against the retained private PDF;
retain its SHA256, byte count, acquisition metadata, source locator and DOI.
Do not redistribute the copyrighted PDF or digitize figures.

The statistics describe active channel-axis casts. Bottom, interfacial and
whole-plume records reuse casts; neither layer counts nor independently
sampled extrema may be added. Inactive-flow casts were omitted, so the
sampled minimum is not a quiescent-flow thickness or annual minimum. Bottom
layers below approximately 15 m were undetectable in these LADCP observations.

Keep the source definitions: bottom-layer top at the velocity maximum;
interfacial layer between that top and the plume top. The plume top is
defined by any of speed below cutoff, direction departure greater than 45
degrees from mean bottom-layer flow, or salinity below cutoff. REDSOX-1
uses 0.075 m/s and 36.5 psu; REDSOX-2 uses 0.05 m/s and 35.7 psu. Their
winter/summer labels are campaign contexts, not matched seasonal means or
a common-operator annual range. Preserve these differences explicitly.

Use the existing reported_vertical_thickness metric with a source-reported
mean statistic and sampled min/max range. Thickness has no sea-surface
datum. Do not infer upper/lower depth boundaries, a vertical profile, paired
width, physical state occupancy or stored volume. Do not use bathymetric
channel width as plume width. No new observations or raw fields are collected.

The frozen register v48 remains byte-for-byte unchanged below its existing
file cap. Publish a small statistical-thickness addendum JSON/CSV and a new
pinned reference-inventory manifest. A loader reconstructs the complete
reference view in memory and combines CSV cells without publishing an
expanded register. Preserve every old reference, record, context, CSV cell
and ownership link, appending only the twelve Red Sea references. Do not
change the independent model-projection inventory v48 or its coverage counts.

Cloud checks verify the original table transcription, source provenance,
conditional cast/threshold definitions, reference ownership, old701references
and allCSVcells, all12newreferences, exact pieces/hashes/schema/counts,
duplicate/current/context/CSV mutations and false annual/global/volume claims.
All validation and tests run sequentially on one idle cloud CPU. Local work
is code, source-text/figure review, metadata, hashes and exact byte retention.
No tracked edits while jobs are live. No runtime, query UI, preview or main
changes. Goal remains unfinished beyond these scoped published statistics.
