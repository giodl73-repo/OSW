# Regional depth-surface and compatible volume scenarios

The user requested depth varying along currents and compatible length/width/depth
volume estimates. Advance that modelling with the reviewed paired NorthCape and
Makassar source descriptors. This is a NEW explicitly assumed regional interpolant,
not an alteration or rerun of the frozen source/partial-section products. Their
historical no-joining-cuts scope remains true; this product declares the additional
interpolation assumptions. Physical eligibility remains false throughout.

Read only research/barents-makassar-paired-section-geometry-v1.json and its review.
Keep all32original cases and14unresolved selections. Enumerate every adjacent pair
of the four declared cuts for each owner and each of the four2022dates:24segment
slots. Never skip an unresolved cut, combine dates, infer annual extrema or transfer
ownership between the NorthCape regional BSO context and the Makassar branch.

Require equal source branch, frame, unchanged0.1m/s component cutoff and homologous
native transverse coordinates. Fixed-cut coordinates retain their original5km
target-axis tolerance. Only consecutive source strip indices are eligible. Each
source strip already requires finite paired top/bottom contours and unique native
run connectivity. Join two such strips across neighboring sections only when all
four corner native depth-index intervals share at least one level and the pairing
is one-to-one in both directions. Reject splits/merges, missing or censored corners,
disconnected layers and unmatched strips; preserve each gap and endpoint censor.

Project upper and lower depth separately with bilinear longitude/latitude surfaces
over the resulting original rectangular corners. This is an explicit assumption
about the unsampled interior between cuts (up to2degrees longitude or1degree
latitude); it is NOT new model resolution, verified flow continuity, an independently
identified current axis, water-mass classification or knowledge of interior bathymetry.
Topography and flow may interrupt the assumed surfaces between source sections.

Integrate thickness against spherical surface area on6371008.8m radius. Use exact
cos(latitude)-weighted integrals of affine latitude values and the trapezoidal mean
in longitude. Use the stable small-angle expansion of1-h*cot(h) throughh6 for
h<.001radian; remainder is O(h8). Depth extrusion uses constant surface footprints,
not radially contracting spherical shells. Convert m3 to km3. Do NOT multiply a
full route length by unrelated width and depth or extrude unmatched partial areas.

Propagate the four source sampling-bracket thickness bounds with the same positive
integration weights. These conditional sampling scenarios are not model/identity/
shape/physical uncertainty,confidence intervals,true-volume guarantees or seasonal
ranges. Sum only disjoint matched patches within one declared segment/date/owner.
There is no current-total,annual-total or global-total sum, and no claimed full
segment volume. Keep physical volume/current depth/uncertainty/annual range null.

Publish depth-surface JSON,24-slot CSV and map-ready GeoJSON. GeoJSON coordinates
remain2Dlongitude/latitude; provider positive-down upper/lower depths are separate
properties and never relabeled WGS84altitude. No UI/runtime/defaultquery integration.

Use a bounded ordinary descriptor query with explicit zero prior counters under
DescriptorQueryv3(250000numeric/32MBuniqueJSON/2.5MBpacket),before-decode durable
reservations/cache,blocked networking and blocked source-data/native reads. No
provider/archive retrieval or closed native-case budget renewal. Cap derived
surface control-corner occurrences at6000 and all published outputs at2.4MB.
One shared60second test/producer deadline,SIGTERM handler,fresh outputs,sequential
one-idle-CPU cloud-only scientific parsing,geometry,numeric assembly and tests.
Local static edits/AST/manual primary metadata review and exact byte custody only.

Verify an analytic constant prism and units,independent Simpson quadrature for
varying depth at high latitude,sampling scenarios,unresolved and nonadjacent cuts,
owner/date/frame/coordinate/index mismatches,disconnected and split/merge layers,
all32source cases/all24slots,source immutability and complete JSON/CSV/GeoJSON
roundtrip. Keep canonical908references,old projection inventory/main/102eddy refs
unchanged. Overall current-depth programme remains incomplete.
