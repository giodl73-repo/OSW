# Coastal regional depths with distinct windows and mixed axes

Use all96original compiled coastal cases:16each for Norwegian Coastal,Tsushima,
Guiana,East Greenland Coastal,Gaspé and Jutland. Keep47original supported cases
and49axis gaps,including all16Jutland gaps. Exact March/June/September/December15,
2022snapshots are not seasonal means,residual currents,annual extrema,1991/1993
Gaspé observations,1966Jutland records or2024NorKyst measurements. No native
retrieval,old producer/validator replay or acquisition-case budget renewal.

Preserve primary0.1m/s component cutoff and owner-specific directions:0NCC,
60Tsushima,315Guiana,225EGCC,90Gaspé,0Jutland. No source method applies a surface
gate or temperature gate. Original core-search/selection windows are0–100mNCC,
0–200mTsushima,0–100mGuiana/EGCC and0–30mGaspé/Jutland. These are selection
windows,not current thicknesses,bottoms or caps on a connected layer. Retain
original selected cores,primary boundaries/status/thickness/censor and source
candidate diagnoses. Do not substitute better-resolved cores or fill axis gaps.

Original fixed latitude for NCC,Guiana,EGCC,Jutland;fixed longitude for Tsushima
and Gaspé. Validate each original enum against its method definition and5km
native-axis tolerance. Transverse native indices remain consecutive and strictly
increasing;the fixed coordinate/index remains constant. Do not transpose,skip
columns or convert an unsupported field kind to a regional route profile.

Reuse finite paired-boundary and minimum-support arithmetic. Unique overlapping
depth runs on consecutive transverse columns within20km spherical geodesic
separation form partial linear strips. Reject split/merge,censored/disjoint pairs
and gaps;do not close endpoints or fill to a sample limit,neighbor or bed. Keep
all available columns/runs and declared native counts distinct for axis gaps.

Native first-to-last qualifying sample span is conditional minimum support under
the original contiguous piecewise-linear component definition,not depth from the
surface,a finite bottom,physical named-current thickness bound or uncertainty.
Single-level zero minimum span is uninformative,not absent flow or zero actual
thickness. Censored boundaries/thickness stay null. Partial component area and
area/span thickness omit gaps and are not whole-current or independently flow-
normal quantities. Native brackets are sampling scenarios,not confidence or
annual bounds. No between-section surface,independent terrain clearance,whole-
route physical profile or physical volume is established.

Retain EGCC's source nonadditive coastal-branch relationship to East Greenland
without inherited offshore/parent depths. Guiana remains source-scoped episodic
shelf flow with unresolved permanent-current nomenclature. NCC is not assigned
to the broad unresolved Norwegian Current;Tsushima remains the selected regional
nearshore branch. No salinity/water-mass identity,alias resolution,related-current
depth inheritance or new physical current entity follows from velocity geometry.

Output lossless shared-note JSON,section CSV and flat96row anchor CSV with axis,
selection window,no-surface-gate policy,source identity/parent context,cutoff,
direction,dates,coordinates,paired depths/minimum support,censors and source
pointers. Null anchors/blank depths are preserved. Expansion must reproduce the
full scientific dictionary and exact both-CSV bytes. No records,precision,
qualifications or source pointers are dropped.

Offline cloud-only sequential one idle CPU,fresh output,one shared absolute60s
including tests and producer,outer timeout and producer SIGALRM/SIGTERM. Ordinary
DescriptorQueryv3 starts explicit0prior numeric/bytes,reserves before decoding
and caches packets:250k tokens,32MBuniqueJSON,2.5MBpacket,2.4MBwholeoutput. No
UI/runtime/default-query/WASM/main/eddy/inventory changes. Freeze prior code/data
and retain the single artifact only after all branch jobs terminate.

Tests cover analytic geometry/scenario units,censorship,all96cases/47anchors/49gaps,
all16Jutlandnullanchors,per-owner windows versus deeper connected layers,both
axes/indices/tolerances,owner/frame/cutoff/gate/window/date mutations,no inherited
EGCC depth or permanent Guiana promotion,minimal-span/zero semantics,source
immutability and actual full lossless JSON/both-CSV roundtrips.
