# HE667 Skagerrak ADCP source custody screen

New independent2025September dataset Albinusetal2025PANGAEA.988085,
150kHzHEINCKEOceanSurveyor. Original metadata explicitly describes earthframe
minutelyvelocities at4mbinspacing; parameter methodlabels say1200kHz, an
unresolvedmetadata discrepancy, not an automatic correction. Coverage crosses
Jutland/Skagerrakfront regions, not proof everyprofile is namedJutlandflow.
No borrowing surface drifter depth or local seabed as physical current bottom.
ThorreportunderlyinghindcastdatarequiresNDA, not requested. HE649rawCTDmetadata
restricted, no originalrawrequested. HE667otherinstrument992950/988075web
cachemiss discovery targets remainclosed(no mirror/alternatehost/retry).

Prospective one cloud case3HTTPoperations: original988085landing GET<=250KB,
then HEAD of the unique exact linkedHE667_OceanSurveyor_150kHz_ADCP.nc at
httpsdownload.pangaea.de, then ONLYif declaredpositivefilelength<=1900000bytes
one fullfileGET<=1900000bytes. HEADmetadata is not a repeated body download;
predeclared GET may follow only first successful sizecheck. Missing/oversize/
HTTPerror metadata blocks ALLfielddownload. No redirects/retries/fallback/subset
requests, no opportunisticotherdatasets. Eachoperation durablyreservedbefore
attempt, rawresponses streamedtodiskbeforeHTML/NetCDFparsing, shared7MBrawcase
cap and2.4MBwholeoutput(1.9MBfilegatealsoallows eventualexactpublication).
Ifsizegatefails, retainmetadataevidence,no assertion native fields processed
or hidden unprocessed backlog. Producerterminalbeforeartifactupload.

OneidleCPUalltests/sourceparsing/headerinspection cloud only.90secabsolute
alarm/SIGTERM,25sectransportperoperation,outer100seckillafter5. Freshdir,
retainfailureledger/rawerrorbody. Archive/field budgetsnotrenewed by stages:
250000numericvalues/10000metadata,3-150selectedprofiles/40nativelevelsperprofile,
20000cells/6000measurementnodes/5kmtolerance,7MBraw. THISstage0selectedprofiles/
0nativearrayvalues, no velocity/salinity/time/coordinatearray reads; headers
only dimlength/dtype/units/names. No instrumentsourceQC/velocityunits/current
membership inferred from a landinglabel or variable name. Anylaterfieldstage
muststaywithin THIScaseoperation/scalar/time/rawcaps, newfrozenversion, no
repeatedsourceURL/artifacttargetbodydownload. Boundandpreflightselectedslices
before native reads. No wholefileloads merelytoinspectgeometry.

No measurements/references/depthbounds derived/admitted. Keepcanonical891/
111identities/102eddy/21UTF8/unrelatedleaves/main/runtime/UI/defaultquery unchanged.
A header-only retainedfile is sourcecustody, not physicalcurrent-depthcoverage.
