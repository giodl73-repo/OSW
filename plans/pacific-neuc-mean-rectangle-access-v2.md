# Pacific NEUC native rectangle row access v2

New access plan after v1 first128range response timed out at25seconds with
zero successful ranges and zero field response bytes. Failure review/ledger
retained;do not rerun v1. Keep all four diagnostic longitudes,latitude gate,
signed-integral/core window,weak-flow primary/sensitivity cutoffs,source-mean
qualifications and no-promotion rules of section protocolv1 unchanged.
No successful source data from v1 exist to replay. Existing source/kernel/
operator versions remain frozen;this is a new acquisition layout.

Acquire complete native longitude rows from the minimum through maximum of
the four previously declared nearest native longitude indices. Every longitude
inside this rectangle is now explicitly authorized,not hidden overfetch.
Read all native6-10N latitudes and40depths. The full western135-140E band is
useful for independent later zonal-mean review corresponding geographically
to Li2018Figure2,but this stage retains four discrete section diagnostics;
it does not claim reproduction of the source geostrophic or averaged operator.
The added longitude samples do not create additional named-current cases.

Exact big-endian packedshort component rows replace single-cell ranges.
Partition each component into nonoverlapping five-native-depth patches;
each patch must fit20000cellpairs. Preflight the full rectangle under the
unchanged250000pair/7MBdecoded shared ocean limits,150latitudes per section,
40levels and5km nearest-longitude tolerance. Count every authorized rectangle
cell,including interior longitudes not used by the four section diagnostics.
No additional coordinate retrieval or global field download.

First request only the first contiguous native row to distinguish field-byte
access from multipart overhead. Exclude this row from subsequent requests.
Then use at most32nonadjacent row ranges per multipart request. One source-
pinned reader,160requests and7000000total body bytes unchanged;1000000total
requested bytes remains within the frozen general transport ceiling rather
than the earlier single-cell plan's smaller100000byte allocation. Per-body
ceiling lowered from50000 to12000bytes;whole planned request count and body
reservation checked before IO. Every byte range must be exactly returned;
no full-body200,coalescing,identity drift,encoding,retry or successful replay.
The existing25second request timeout stays fixed. Checkpoint exact successful
rows and shared ledger immediately. Any later failure requires a new resume
plan using preserved bytes,no blind full reacquisition or perpatch reset.

Run36cloud checks before IO:12transport/coordinate,12connected-layer,
8original section/storage/packing/budget/diagnostic,4new rectangle budget/
index/extraction/frozen-science tests. Cloud-only sequential oneidleCPU for
field retrieval,decoding,geometry,diagnostics and tests. Retain full packed
rectangle with source indexing plus exact extracted four columns/profiles,
diagnostics and shared transport ledger. Local exact retention/hash only.
Mean semantics/regional provider defects/current identity remain unresolved;
physical depth,volume,annual ranges and new inventory cases not authorized.
Registerv48,inventoryv42,eddybaseline,main and preview8788 preserved.
