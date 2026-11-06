# Prospective ECCO subset guard v1

The full goal needs consistent current-depth estimates and along-route/time
variation. Catalog941references is not that deliverable. This component checks
one COMPLETE contiguous rectangular request from supplied metadata before any
values;it is not an executable depth operator or a verified ECCO endpoint.
No provider field request,account authentication or new depth is part of thisrun.

Generic DAP2 syntax follows official OPeNDAP constraint-expression documentation.
ECCO-GROUP/ECCO-ACCESS README advertises spatial subsets,primarily native LLC.
Its ecco_access directory click was restricted;that target is closed,no raw/API/
mirror/alternateformat bypass. Regular0.5degree compatibility remains unproven.
Previous readthedocs subsetcall outcome remains unretained;do not repeat it.
The guard supports explicit flat floating-point Arrays only and rejects Grid,
structures,packing,unknown units/masks,implicit coordinates and unsupportedaxes.
Real metadata must identify actual dimension order and all vertical interfaces.
A metadata hash field is not a proof of actual acquisition or providerbehavior.

One full time/lat/lon window counts all profiles together:3-150profiles,<=40
contiguous levels,<=20000cells,<=250000requestednumericvalues,<=7MBnativearray
bytes. No partition/jobs/stride/capreset. Numeric native-array byte calculation
excludes transport overhead,so a verified transport bound remains prerequisite.
No network code,URLs,credentials,decoding,cropafterdownload orobservations.
The plan requests coordinates/interfaces. Actual missing-value attributes still
need verified custody;the fill-metadata flag is only a declaration. This does
not validate currentaxis/identity,depthcutoff,seasonality,profile orvolume.

12meaningfulsyntheticcloudchecks cover inclusiveindexing/allarrays constrained,
alltimes aggregateprofilecap/verticalstride rejection/rangeandtypeerrors/missing
axes/dimensionorder/Gridpackingunitsfillrejection/interfaces/identifierandproduct/
immutabilitybyteaccounting/no endpointorsciencepromotion/credentialdeclarations.
Cloudonlyoffline sequentialoneidleCPU,60sharedseconds includingtests/report,
signals/outertimeout/freshoutput,wholeartifact<=2.4MB. No compiled scientific
input/nativeinput;no DescriptorQuery question is replayed orledgerreset. Existing
canonicalv57/941refs andalloldquestionchargesremain unchanged. No UI/runtime/
query/default/WASM/browser/server/mainchanges. SamePR83,no extraPR.

Before actual acquisition:secureEarthdataavailability,actual metadata custody,
verifiedserver subset/transportbounds,and a separatelyfrozen scientificoperator
withcurrentidentity,geographicgates,dates,indices,velocityframe/cutoffs/support/
censor rules remain required. Booleandeclarations alone neververifyacquisition.
