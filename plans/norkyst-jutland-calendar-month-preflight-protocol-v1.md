# Complete monthly Jutland component-depth support

Native daily and aggregate metadata both returned HTTP500. Preserve those six
metadata attempts, do not retry them, and retain the existing fixed-z bounds.
Prepare complete-time support from the working fixed-z source before new reads.

Use full calendar March/June/September/December2024, three FIXED original editorial
center grid nodes (column19 of each old39profile cut), all hourly values, paired
u_eastward/v_northward and first11provider z-levels0,1,2,3,5,7,10,15,25,50,65m.
These are fixed search locations, not new velocity maxima, current axes or current
edges. Do not move points for stronger flow, relax cutoffs or infer water-mass
membership. New measurements will be monthly mean-field component descriptors,
not means of instantaneous current thicknesses or a seasonal climatology.

Reuse exact hour12profiles for the four prior15ths at each center. New daily
queries split0-11/13-23 on those dates; every other day uses0-23. Every month/hour/
point must be covered exactly once by new requests plus prior profiles, with no
overlap/gap/padding. Actual dataset URLs come from the retained Ingoy acquisition
index. Reuse its daily DAS bytes from the already retained monthly ZIPs; open only
bounded .das members, verify acquisition member hashes and frozen metadata rules.
No old Ingoy field values/arrays are decoded; no metadata or field HTTP replay.

Preflight the entire four-month programme jointly, including the39348prior reserved
scalars. Count both new velocity arrays and one shared decoded coordinate map:
v-coordinate text must exactly match u-map text without duplicate numeric decoding.
Keep unchanged250000scalar/7MBdecoded limits,11levels,11/12/24hourly profiles per
point patch (3-150),<=20000velocitypairs/patch. A fixed-point temporal patch is
not a new spatial transect or a spatial-axis selection. Split source-output chunks
by month, each<=2.4MB; do not reset the native budget by month/point. Reserve all
future requests and allow one attempt per distinct target with persistent receipt.

Consumer must require every paired finite hour at each depth for complete-month
mean, population standard deviation or quantile. Missing/land stay null; no partial
mean or temporal interpolation. Temporal quantiles are model variability, not
measurement uncertainty. Primary0.1m/s northeast45degree component and0-25mcore/
selection remain, sensitivities0.05/0.2stay distinct.65m domain end, missing next
level or model bathymetry is not a current bottom. No width, physical layer/volume,
full-year range, annual extrema, season means, original-method or runtime promotion.

This stage only validates custody/time coverage/budget and creates a request plan.
No new ocean HTTP requests or values are acquired. All archive parsing, geometry,
counts and tests run only in cloud sequentiallyoneidleCPU; local staticediting/
AST,source/metadatareview,hashes/exactretentiononly. Execute new fields only after
the exact preflight artifact is reviewed and a bounded consumer is declared.
