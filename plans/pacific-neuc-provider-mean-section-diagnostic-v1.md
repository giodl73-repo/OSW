# Southern Pacific NEUC provider-mean section diagnostic v1

Predeclared before velocity outcomes. Li2018 identifies a weak southern jet
near8N,about3degrees meridional width in the western basin,and compares
sections averaged135-140E. Source cores2-5cm/s,weak total model versus
geostrophic velocities,and long temporal averaging motivate this diagnostic.
https://www.nature.com/articles/s41598-018-35469-2
Original JATS/prerequisites/scope audits remain pinned. Four discrete sections
135,136.5,138,140E are OSW sampling choices,not the paper's zonal average or a
digitized source route. Sample all native latitudes within6-10N,not selected
editorial offsets. Independent source latitude context6.5-9.5N is an OSW
approximation around8N/3degree width,not a measured current boundary. Exclude
middle/northern jets and3NNSCC;no branch or parent inheritance.

Use exact single-record CDF2 GOFS3.1 provider nominal1994-2015 mean object and
retained cloud axes. Classify as native-mean-derived fixed-depth velocity,
with exact historical producer weights/time completeness and fixed-z Eulerian
mean equivalence unverified. A filename period/time coordinate is not complete
sampling evidence. Known provider PhilippineSea/Ryukyu defects remain open.
This stage tests regional structure;it cannot promote current identity or a
new inventory case before independent scientific review of the actual outcome.

Predeclare eastward component,300-1500m signed-integral/core selection window,
primary0.02m/s and separate0.01/0.05m/s sensitivity descriptors. The window is
an OSW search choice spanning western undercurrent depths,not source top/bottom
interfaces. Trace each selected column across all40native0-5000m levels using
unchanged interval diagnostic/connected-layer kernels. No surface gate. Require
complete finite support in selection window,positive signed integral and a
core strictly above primary cutoff. Greatest integral wins;first ascending
native latitude breaks ties. Retain gate/support-edge winners unresolved;
never replace with a weaker interior candidate. No qualifying column is not
absence of the named current. Sensitivity thresholds do not fill primary gaps.
Record whether selected latitude is within independent context and whether the
primary layer has a resolved upper isotach below the surface. These flags do
not independently establish current identity. Missing remains null;crossings
require adjacent finite samples;5000m/sample edge is not a physical bottom.

Cloud-only,sequential oneidleCPU. CDF2 big-endian packed signedshort u/v,
fill-30000 removed before scale0.0010000000474974513;CF east/north frames,
storage dimensions/offsets/recordcount and source identity must match header.
Longitude nearest native index within5km;no coordinate/field interpolation.
Read only each selected longitude/native latitude/full depth cell pair.
Fixed ceilings250000pairs/7MBfloat32 decoded,20000pairs per section,
150profiles per section,40depthlevels. One reader/shared authorized plan,
160HTTP requests maximum,100000requested packed bytes,128ranges per request,
50000response bytes per request,7000000total response body bytes. Separate
section/component batches keep requested ranges far apart;no coalesced or
unrequested payload accepted. All dimensions/budgets checked before network.
No full field/global velocity download,no new coordinate retrieval,automatic
retry,successful replay or budget reset. Each successful request immediately
writes exact completed-range checkpoint and shared ledger,including on later
failure. Resume only with a new plan consuming preserved successful bytes;
do not blindly rerun acquisition after partial success. Run32cloud tests
(12transport/coordinate,12connected-layer,8new storage/scope/packing/budget/
diagnostic contracts) before field requests. Retain raw packed bytes and hashes
alongside profiles/diagnostics/source offsets and ledger. Exact source bytes
retained locally only;no local field processing/tests/runtime/preview.

No complete physical depths,annual range,whole-current thickness/volume,
transport-to-volume conversion,independent model axis or inventory promotion
claimed. Registerv48,inventoryv42,eddybaseline/main unchanged. Goal unfinished.
