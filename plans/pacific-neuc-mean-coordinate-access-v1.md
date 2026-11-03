# Pacific NEUC mean-object coordinate access v1

Predeclare before network outcomes. Use the exact single-record CDF2 object
whose source length,LastModified,header bytes,variable offsets/types were
verified in header inspection v1. This stage reads only known header fragments
and coordinate variables,not ocean velocities or a regional current diagnostic.

First request nonadjacent header ranges0-3,900-903,2000-2003. Require a strict
multipart206response,all/only requested intervals,unchanged total object size,
LastModified,identity encoding,boundedContentLength and exact binary payloads.
Compare each fragment to the frozen2064byte header. Reject full-body200,
merged/coalesced ranges,duplicate/missing/extra parts,truncation,encoding/source
changes or trailing data. Binary lengths determine payload ends,not a delimiter
search that could split numerical bytes. No automatic retry or successful replay.

Next read the known contiguous coordinate-only block2064-64399 (62336bytes).
Frozen header spans prove this covers depth/latitude/longitude/time only and
ends exactly before water_u at64400. Validate no gaps/overlap,one-dimensional
double encoding,declared counts,finite values and monotonic spatial axes.
Depth must retain40native levels0-5000m. Preserve all native coordinate values,
raw bytes/base64/hash,source identity and one shared transport receipt. Time
coordinate is not time bounds or proof of averaging duration/weighting.

Two HTTP requests,62348requested metadata/coordinate bytes,100000maximum body
per response,200000total response-body budget,including future-first-attempt
reservation. General adapter ceilings remain1000requests/1000000requested
bytes/1000000perbody/7000000totalbody;these do not authorize velocity reads in
this operator. Existing250000pairs/7MBdecoded ocean-field caps unchanged.
Every requested interval is preauthorized,nonoverlapping and attempted once.
Failure leaves a ledger;do not blindly replay successful requests.

Cloud-only sequential oneidleCPU for requests/binary parsing/axis decoding/tests.
Local code/metadata/source-text/hash/exact retention only. Run10frozen header
tests plus12new multipart/transport/coordinate contract tests before requests.
This proves access/layout,not a regional field,current identity,depth,seasonal
range,physical thickness,volume or runtime integration. Prior mean-layer versus
Eulerian-mean/producer weights/missing times/provider regional-bias gates remain.
Preserve registerv48,inventoryv42,eddy baseline/main/preview8788. Goal unfinished.
