# Native-pressure depth companions

Extend the validated Canary PIES pressure-conversion policy to eligible
native-pressure references in immutable inventoryv26. Use GSW3.6.23,
depth=-gsw.z_from_p(sea_pressure_dbar,latitude,0,0), same assumed zero
dynamic-height/surface-geopotential terms,6decimal serialization and10m
display rounding. GSW height is positive-up, depth positive-down. Published
oceanographic pressure is assumed sea pressure; do not subtract atmosphere
again. This standard-ocean reference conversion omits ocean-state corrections;
rounding and numerical reproducibility are not physical accuracy.

Enumerate ALL pressure-native references from validatedv26 cloud loader:
Benguela1270dbar mean lower-pressure extent at published34.5S and Rim350dbar
sampling-censored reach with no retained latitude/verifiedpressure datum.
Benguela's explicit section latitude permits an approximate metre companion.
Rim remains unconverted; invent no basin/route-centroid latitude or missing
pressure datum. Preserve its censor context and unknown deeper flow extent.
Keep both outcomes in JSON/CSV, absent converted values remain null/empty.

Retain full native reference and sourcepointer beside conversion fields.
Benguela remains September2013-July2015 regional CPIES-GEM geostrophic mean,
OFESmeanreference/bottom-pressurevariability, pair-averaged,excludingEkman.
Not direct full-column observations or a flat boundary across11-17.5E.
No new reference IDs added to inventory,no independent measurement count,
no native unit relabeling or mutation of validatedv26addenda. Metre companion
is linked to the same reference and is not an extra measurement. Physical
bottom/thickness/uncertainty/annualrange/volume and route/state/width/seasonal
join eligibility remain unknown/ineligible. Native857m2dbar count unchanged.

Pin existingCanaryoperator/method, inventory/inputgraph,newcode/tests/protocol
andworkflow. All calculations/tests/loaderassembly/cloud only sequential
oneidleCPU; no local science. Networktripwire during actualproducer. No new
native arrays/remote source requests;2metadata outcomes,1convertedscalar,
no synthetic additional profiles to meet unrelated nativeprofile minimum.
Check official75term examples, sign/inverse at1e-7dbar,unknown/missing/invalid
coordinates,sea-vs-absolutepressure,duplicate/omission/physicalpromotion,
sourceimmutability,CSVnulls/full nativeinventory. Newoutput<2.4MB,file<2.5MB.
Freshoutputdirectory,producerfinishesbeforeartifactupload. Preserve102eddyrefs,
21UTF8/runtime/main/oldvalidatedoperators, exactparentGitTreepublicationonly.

Data lead attempted this turn: the primary study's observed original link
http://aoml.noaa.gov/phod/SAMOC_international/samoc_data.php normalized bywebtool
toHTTPS andreturnednotaccessible. TargetCLOSED;no retries/alternatehostbypass,
no ocean fields obtained and no claim data absent globally. Conversion uses
retainedreferences only, not a renewed metadata acquisition allowance.
Official method:https://teos-10.github.io/GSW-Python/conversions.html#gsw.conversions.z_from_p
andhttps://www.teos-10.org/pubs/gsw/pdf/z_from_p.pdf . Reference assumptions are
explicit; exact source pressure/physical boundary errors remain unknown.
