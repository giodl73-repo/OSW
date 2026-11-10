# Project only structural coordinate metadata

HTTPcoordinate diagnostic41675462729passed32tests but its first unconstrained
uv3zDDSrequest timed out after15s, before any coordinate response. Retain that
failure separately. This NEWwrapper requests DDSstructural metadata projected to
depth,lat,lon,time while keeping both fixed2022products,entire native arrays,
Float64parsing,units,calendar,exact pairing and two retained controls unchanged.

OPeNDAP documents that DDSconstraint expressions select returned structural
metadata: https://docs.opendap.org/index.php/DAP2%3A_Constraint_Expressions .
DASignores constraint expressions,so leave DASrequests unchanged rather than
claiming to constrain them: https://docs.opendap.org/index.php/DAP2%3A_DAS_Service .
The four complete coordinate arrays remain required; this is not fewer samples
or weaker current measurement rules. Projection is metadata-only,not model data.

Scopedwrapper overrides only operator,HTTPclass and the two DDSURLs. Every
original parser,HTTPtimeout/byte limit,no redirect/retry/duplicate rule,native
worker,120sparentwalllimit and exact oldcontrol check remains frozen. Parent
must launch this NEWworker. Restore all original globals after success/error.
No fresh data,velocity/salinity fields,currentdepthrefs,physicalbottom/thickness,
width/area/volume or annual/whole-route claim. All source outcomes/pending/error
receipts retained. Cloud-only oneidleCPU;prior scientific/publication caps and
791refs/main/runtime/UI/eddybaseline unchanged.
