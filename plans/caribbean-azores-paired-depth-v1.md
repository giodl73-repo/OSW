# Caribbean and Azores regional paired depths

Use all20original compiled cases:five Caribbean sections and five Azores sections
at each exact January15/July15,2022 snapshot. Keep19supported regional cases and
one unresolved gate-edge case with its original candidate diagnosis. These are
model snapshots,not seasons,monthly means,annual extrema or new observations.
No native/source-data retrieval,old producer/validator replay or case renewal.

Preserve the source270degree westward Caribbean and90degree eastward Azores
components,strict0.1m/s primary contour,0.05m/s surface selection gate,and complete
native0–200mselection window. The surface selection gate is below the primary
cutoff:it neither forces a primary top at0m nor establishes a physical surface
layer. Preserve nonzero upper boundaries. Original native surface connectivity
is graph topology only,not selected-layer or physical-body thickness. Retain
the raw source flag plus an explicit not-computed interpretation for the axis
gap,so its defaultfalse flag is not mistaken for observed current absence.

Use original legacy longitude provenance dictionaries,not Mediterranean enum
tags or fixed-latitude adapters. Check exact section definitions,the original
finite nearest-longitude receipt within5km,and sampled wrapped longitude against
the original native coordinate (which may use0–360degrees). Preserve increasing
native latitude indices at fixed longitude. Do not reselect any core or replace
the unresolved edge with another candidate. Gates remain original source choices.

Reuse paired-boundary/minimum-support/strip arithmetic. Only uniquely overlapping
depth runs on consecutive original latitude columns within20km spherical geodesic
separation form partial linear transverse strips. Reject splits,merges,censored
pairs and gaps;do not close endpoints or fill from neighbors,sample limits or bed.
Retain every available column/run and every original selected primary boundary,
status,depth,thickness/censor and source pointer exactly.

Native first-to-last qualifying sample span is conditional minimum support under
the original contiguous piecewise-linear component definition,not depth from the
surface,a finite bottom,physical named-current thickness bound or uncertainty.
Single-level zero minimum support is uninformative,not absent flow/zero actual
thickness. Censored boundaries/thickness remain null. Partial component area and
area/span thickness omit gaps and do not establish a whole current or independent
flow-normal width. Native brackets are sampling scenarios,not confidence/annual
bounds. No between-section surface,independent terrain clearance or volume.

Keep Caribbean southern-jet context separate from northern jets,Yucatan,Loop,
Antilles and upstream island flows. Keep Azores eastward-jet context separate
from its westward countercurrent,northern recirculation,Portugal/Canary and eddies.
Do not join RU29_2024inversion layers or24.5W_2009density-layer extents as if they
were these2022component boundaries. Geographic maxima are not independent named-
current axes or water-mass identification.

Output lossless shared-note JSON,section CSV and flat20row depth-anchor CSV with
owner/date,cutoff/direction,surface gate,selection window,topology interpretation,
paired depths,minimal support,censor status and source pointers. Shared-note
expansion must restore the full scientific dictionary and exact both-CSV bytes.
No records,values,precision,censors or qualifications are dropped.

Offline cloud-only sequential one idle CPU,fresh output,shared60sabsolute deadline
including tests and producer. An outer timeout wraps both processes;producer
also handles SIGALRM/SIGTERM. DescriptorQueryv3 starts explicit0prior numeric/bytes,
reserves before decode/cache:250k tokens,32MBuniqueJSON,2.5MBpacket,2.4MBwholeoutput.
No UI/runtime/default-query/WASM/main/eddy/inventory changes. Freeze old data and
methods;retain the single artifact only after all branch jobs terminate.

Tests cover analytic geometry/scenario units,censorship,nonzero primary tops
despite the surface gate,native wrapping/receipt/indices,all20cases/19anchors/one
gap,owner/direction/gate/window/date/primary mutations,minimal span versus depth,
zero-bound semantics,source immutability and actual full lossless JSON/CSV checks.
