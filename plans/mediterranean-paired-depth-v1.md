# Mediterranean regional depths across four dated snapshots

Use the corrected v2compiled Mediterranean curtain cohort,not the superseded
v1Balearic10cm/s contours. Preserve all72cases:Balearic16,Ligurian16,Northern
Mediterranean20,Algerian20. Keep63supported cases and9axis gaps. Dates are exact
March15,June15,September15,December15,2022 snapshots,not seasonal means or annual
extrema. No native/source-data acquisition,old producer replay or case renewal.

Original cutoffs/directions:Balearic0.05m/s at60degrees,Ligurian0.1m/s at240,
Northern0.1m/s at270,Algerian0.1m/s at90. None applies a surface component gate.
Keep original0–200mcore-search/selection windows as selection metadata,never a
current bottom or thickness. Preserve original selected core/primary diagnosis,
case owner,branch scope and every available ordered column/run. Do not reselect
cores or impose a surface-connected layer. Keep owner cutoffs visible in both
CSV views and threshold-context counts separate.

All source sections have fixed longitude,with increasing native latitude and
consecutive latitude indices. Validate original5kmnearest-longitude tolerance
with the latitude scale and reject changed fixed axes/skipped indices. Reuse
paired-boundary/support/strip arithmetic; uniquely overlapping depth runs on
consecutive original latitude columns may form partial linear strips within
20km spherical geodesic separation. Reject split/merge,censored or missing pairs.
Do not close endpoints,bridge gaps or fill boundaries to a sample limit or bed.

Retain finite paired component boundaries and,where censored,the native first-
to-last qualifying depth span as conditional minimum support under the original
piecewise-linear component definition. It is not surface-relative depth,a finite
bottom or a physical named-current thickness bound. Single-level zero minimum
span is uninformative,not absent flow/zero actual thickness. Censored boundaries
and thickness remain null. Axis gaps retain null anchors and original candidate
diagnoses. No stronger replacement core,between-section interpolation,independent
terrain clearance,whole-route physical profile or physical volume is established.

Ligurian is the source-declared regional Northern Current segment. Preserve
parent identity/relationship and explicit no-inherited-parent-depth flag,without
assigning parent depth summaries or additive volumes. Other source identity
fields remain exact/unknown as originally declared. Areas are partial fixed-
longitude component geometry,not independently flow-normal current widths/areas.
Area/span and native-bracket scenarios are not whole-current thickness,physical
uncertainty,confidence intervals or annual ranges.

Output full lossless shared-note JSON,section CSV and flat72row anchor CSV with
owner/date/coordinates,cutoff/direction,no-surface-gate policy,selection window,
parent context,paired boundaries,minimal support,censor status and source pointer.
Compact metadata must expand to the full scientific dictionary and exact both-
CSV bytes. No case,run,value,precision,source pointer or qualification is dropped.

Cloud-only offline sequential one idle CPU,shared absolute60s including tests,
SIGTERM and fresh outputs. DescriptorQueryv3 explicit0prior numeric/bytes,token
reservation before decode/cache:250k/32MBuniqueJSON/2.5MBpacket/2.4MBwholeoutput.
No UI/runtime/default-query/WASM/main/eddy/inventory changes. Freeze prior data
and methods; retain the one artifact only after all branch jobs terminate.

Tests cover unchanged analytic geometry,censors/surface limits,splits/disjoint
support,all72cases/63anchors/9gaps,four dates,longitude geometry/indices/tolerance,
corrected Balearic5cm/s versus10cm/s substitution,no imposed surface gate or
selection-window widening,Ligurian parent context without depth inheritance,
source immutability and actual lossless JSON/CSV roundtrips.
