# Pacific NEUC precomputed mean header inspection v1

Active depth gap: weak southern NEUC near8N,not the13/18Njets or3NNSCC.
Li2018 doi:10.1038/s41598-018-35469-2 requires a temporal-mean approach;
quarterly snapshots/one-year means can be eddy dominated. Keep source Argo
P-vector,LICOMmean/geostrophic products and HYCOM total velocity distinct.

Fresh provider directory/HEAD inspection found monthly/yearly and nominal
1994_01_2015_12 mean velocity objects on the uniform grid. Metadata access
is now verified;no averaging weights,field types,dimensions,axes or physical
current identity inferred solely from filenames. Provider documents deep
Ryukyu/PhilippineSea instabilities;mean products do not automatically cure
these defects. Regional impact still needs assessment.

This job inspects only the exact NetCDF CDF1/CDF2 header grammar,per Unidata
AppendixB. Sequential exact byte-range requests read only each declared
metadata element;no bulk prefix,no prefetch,coordinate/velocity variable
data,global field download or depth diagnostic. Require206/exactContentRange/
ContentLength/LastModified/identity encoding and fixed same provider object;
refuse200full-body replies before reading. Maximum200000header bytes and
1024requests,25seconds each,no automatic replay. Single fixed object identity
checked against recorded HEAD length/LastModified. Unknown/HDF5/streaming
formats fail closed;no new format adapter without a separate declaration.

Preserve literal header bytes/base64/hash,typed attributes,dimensions,variable
offsets/record flags and range receipts. Parsing stops at end of variable
declarations before all data offsets. Output supports later source/method
decisions;does not validate temporal weights,missing-day support,seasonal
coverage,model bias,NEUC identity/depth,physical volume or runtime integration.

Cloud-only one idleCPU for binary parsing/tests/network requests;local only
primary text/directory/HEAD metadata review,code,hash/exact retention. Existing
ocean-field caps250000pairs/7MBdecoded are unchanged and no ocean velocity
values are permitted in this inspection. Preserve registerv48,inventoryv42,
eddy baseline and main. No need to move preview server or compile WASM.
