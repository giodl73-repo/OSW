# NCC salinity at five frozen original velocity-core columns

Scope fixed before retrieval: all and only the five Norwegian Coastal context
records admitted as original interval-primary minimum reaches in referencev8.
No new column selection,threshold/window adjustment,nearest date,axis rotation,
comparison-based tuning or replacement target. Preserve all original velocity rows.

Use GOFS3.1expt93.0ts3z/2022 salinity,not the unarchived AMM15forecast analysed by
Enge2025. The latter informs a conditional practical-salinity classifier S<35PSU;
it does not validate HYCOMaxes or guarantee NCCidentity. Do not substitute absolute
salinity35.16g/kg,MLD,regional50–100msummary or deeper same-direction flow.

Before any field request,verify all five original native time indices and exact
timestamps,all40depth coordinates,selected latitude/longitude indices and original
three-longitude neighbor stencil. Require instantaneous source and practical
salinity metadata. No native-coordinate interpolation or tolerance relaxation.
Read one40level×3profilepatch per target;use only its original central column for
classification. Retain neighbors as source support,without reselecting among them.

At original core require original northward component>0.1m/s AND salinity<35PSU.
Missing input or a core outside the class remains unresolved/unclassified;do not
seek a shallower or weaker core. Trace the contiguous joint predicate upward and
downward over native samples. Both inputs must be finite at adjacent crossing
brackets. If both predicates fail in a bracket,use the first exit from the connected
interval(minimum lower crossing,maximum upper crossing). Equality belongs to the
excluded side. A missing input censors before that sample,without bridging or
substitution. Domain end censors at the last sample;surface support at0m remains
sample support,not proof of a physical current boundary. Retain both boundary
diagnostics,brackets,limiting criteria and native indices. No physical thickness,
whole-route profile,annual envelope or volume is established or calculated.

One scalar field,600planned values total;at most3attempts per identical patch,
1800requested values and14400conservative decoded bytes including all retries.
Retry only literal NetCDF I/O failure,after2then5seconds;never replay successes.
One dataset metadata-open attempt,no automatic retry. Original global caps remain
250000cellpairs,7MBdecoded,40levels,3–150profiles,20000pairs/patch and5kmnative-axis
tolerances. This study requires exact native correspondence. Field failures and
preflight failures remain in the five-target report. No change to endpoints/caps
or source substitutions after failure. Decoded hashes are not raw HTTP wire hashes.

All retrieval,numerics and tests run sequentially in cloud on one idleCPU. Local
work is code,metadata and exact-byte retention. New output must fit2.4MBsourcebatch,
2.5MBfile and3MBpublication caps. No inventory admission,main/runtime/UI changes or
claim that sparse2022instantaneous samples are seasonal means/annual extrema.
