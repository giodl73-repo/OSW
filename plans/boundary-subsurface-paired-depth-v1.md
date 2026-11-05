# Paired component depths for boundary and subsurface contexts

Use all60original compiled cases:20Mauritanian,20Baffin,10Pacific North Subsurface
Countercurrent and10Atlantic North Equatorial Undercurrent. Keep41supported cases
and19axis gaps. Mauritanian/Baffin have exact March/June/September/December15,2022
snapshots;the two northern contexts have exact January15/July15,2022 snapshots.
Preserve these original owner-specific periods without padding,temporal averaging,
seasonal means or annual extrema. No native/source-data acquisition,old producer
or validator replay,source-window switch or closed acquisition-case renewal.

Original rules:Mauritanian0degree northward,strict0.1m/s,50–300mselection/core
stratum;Baffin180degree southward,strict0.05m/s,100–300mstratum;PacificNSCC and
AtlanticNEUC90degree eastward,strict0.1m/s,100–400mstratum. All surface-component
and temperature gates remain null. Resolve explicit owner window overrides first,
otherwise the original explicit method default—never invent a fallback. Retain
window origin and original rule-operator file in the data and both CSV views.

Selection strata are not upper/lower current boundaries,thicknesses,bottoms or
proof of detachment. A layer from125to350mhas225mthickness,not350m. Preserve
both component boundaries separately. A core selected below100mcan belong to a
component reaching the surface;do not force its top to100m or require a detached
layer because the named target is an undercurrent. No surface gate is introduced.

Mauritanian/Baffin retain their original fixed-latitude geometry;northern contexts
retain fixed longitude. Validate exact source enum,operator ownership,original
section definitions,5km fixed-axis tolerance and consecutive increasing transverse
indices. Native longitude/latitude orientation is not inferred from temporal
support. Dates,axes,thresholds and owner bindings are independently explicit.

Keep every available ordered column/run and original selected core/primary
diagnosis. Pair finite upper/lower component contours only,with original native
sampling brackets. Unique overlapping depth runs on consecutive native transverse
columns within20km geodesic separation form partial linear strips. Reject splits,
merges,censors and gaps. No stronger candidate,neighbor,sample limit or bed fill.
Axis gaps retain null anchors and original candidate-or-null diagnoses.

For censored runs retain original first-to-last contiguous qualifying sample span
as conditional minimum support under the original piecewise-linear component
definition. It is not physical named-current thickness or surface-relative depth.
A one-level zero minimum is uninformative,not absent flow or zero actual thickness.
Censored boundaries/thickness stay null. Partial areas/area-span thickness omit
gaps and do not establish independently flow-normal current widths/areas,physical
uncertainty or a whole body. Native brackets are sampling scenarios,not confidence
or annual bounds. No between-section surface,independent terrain clearance,whole-
route physical profile or physical water volume is established.

Preserve original Mauritanian surface/undercurrent and opposing surface-flow
scope,Baffin water-mass/coastal-curve/ice qualifications,and northern same-sign
layer/NECC-EUC/multiple-jet exclusions. Do not infer thermal,salinity,density/PV,
named-current axis or coherent water-mass membership from selected velocity maxima.
Existing summer surface routes do not become winter/subsurface trajectories.

Output lossless shared-note JSON,section CSV and flat60row anchor CSV with owner,
date,axis,cutoff/direction,source window/origin/rule file,both depths,thickness,
minimum support,censor status and source pointer. Full dictionary and exact both-
CSV bytes must survive compact-note expansion. No records,precision or qualifiers
are dropped. Counts remain separate for Baffin5cm/s versus other10cm/s methods.

Offline cloud-only one idle CPU,fresh output,shared absolute60s including tests
and producer,outer timeout and producer SIGALRM/SIGTERM. Ordinary DescriptorQueryv3
starts0prior numeric/bytes,reserves before decoding/cache:250k tokens,32MBuniqueJSON,
2.5MBpacket,2.4MBwholeoutput. No UI/runtime/default-query/WASM/main/eddy/inventory
changes. Freeze previous data/methods;retain the single artifact after all branch
jobs terminate. Tests cover analytic geometry,censorship,60cases/41anchors/19gaps,
mixed dates/axes,explicit rule defaults/overrides,Baffin5cm/s,both-depth thickness,
selection-not-detachment,no invented defaults,immutability and full JSON/CSV parity.
