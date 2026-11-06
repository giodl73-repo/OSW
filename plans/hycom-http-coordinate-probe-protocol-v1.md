# Bounded HTTP full-coordinate reader

The native-client diagnosis stalled on uv3zdepth40arrayread after successful
dataset open. Test the SAME2022uv3z/ts3z native metadata and full coordinate arrays
via their HTTPASCIIendpoint. This changes transport,not source,declared grid,
timestamps,measurement rules or future current-selection method.

Reuse the frozen native coordinate worker and120sparent deadline via a new scoped
wrapper/factory. Parent must launch the NEWHTTPworker script. Only full depth,
lat,lon,timevariables and DDS/DAS may be requested. Fixed12URLs,one attempt each,
15snetwork-operation timeout,no redirects,retries,caching or duplicate requests.
Persist pending/completed HTTPledger and exact response-body bytes/base64hashes.
Response caps20kBfor DDS/DAS and32bytes per declared coordinate plus4096header
bytes bound the complete raw metadata footprint. No model-field data request.

Parse only exact Float64DDScoordinate declarations and DASStringattributes.
Full ASCIIresponse header/count/axis label and every numeric token must match.
No regridding,rounding,interpolation,gap fill or time substitution. Frozen finite,
increasing full-native-array checks and exact paired axes/units/calendar still
apply. Depth40,lat4251,lon4500,time2920 and250000values/7MBcaps unchanged.

Additionally match both products against retained March61.5N andDecember62.25N
joint-section coordinate controls: all40depths,native latitude/index,every sampled
longitude/index and original date/time index under originalGregorianhourunits.
No old velocity/salinity fields are fetched again. These are precision/provenance
controls,not additional current-depth measurements or whole-grid observations.

Tests and actual transport run CLOUDONLY,sequentially on one idleCPU. Local code,
metadata,pins and exact retention only. All normalized arrays and raw response
receipts together must fit2.4MBsource/perfile2.5MB/publication3MBcaps. Preserve
failure/pending receipts without interpreting them as missing currents. No current
depth,physicalbottom/thickness/width/area/volume or annual coverage established;
prior791refs,main/runtime/UI/eddybaseline unchanged. Any future model-field
transport needs separate packed-value/mask/scale verification before collection.
