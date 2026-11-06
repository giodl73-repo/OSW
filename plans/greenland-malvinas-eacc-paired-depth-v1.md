# Four-current regional paired depths and censored support

Advance depth representation for East Greenland, West Greenland, Falkland /
Malvinas and East African Coastal currents using all48cases in the frozen
compiled curtain cohort. Preserve all43supported regional cases and all5axis
gaps. The original January15/July15,2022 snapshots are separate dated fields,
not seasons, monthly means or an annual envelope. Original owner-specific
branches, fixed component directions, strict0.1m/s threshold, selections,
source geometry and diagnoses must remain exact. No native/source-data replay.

Retain every original ordered column/run and original primary core. Derive paired
upper/lower component contours and transverse partial strips with the unchanged
validated boundary/run/separation/strip functions. Pair only unique overlapping
depth runs on consecutive original native longitude columns, within20km geodesic
distance. Reject splits, merges, censors and gaps. Do not close endpoints or fill
from neighboring columns, sample limits, bathymetry or another current.

Add native_supported_depth_interval_m and its first-to-last span for each original
connected run. The span is a conservative inclusive minimum support for the
original contiguous piecewise-linear model component, even if an upper or lower
boundary is censored. It is not depth from the sea surface, a finite bottom,
an uncertainty interval, or a physical named-current thickness bound. A single
supported level has zero minimum span: uninformative, never absent flow or zero
actual thickness. Preserve null censored boundaries and finite-thickness nulls.
These bounds add useful depth evidence without disguising the unresolved edge.

The original selected core-containing run supplies a discrete axis-proxy anchor
only for an originally supported case. All5unresolved cases retain null anchors
and exact original candidate diagnoses; never use a weaker candidate instead.
Provide a flat48row depth-anchor CSV with coordinates, paired boundaries, minimum
native support, censor status, date, owner and source pointer. Blank values remain
unknown. Keep a full JSON shape report and section summary CSV as separate views.

Latitude-section areas are partial signed-component geometry, not independently
flow-normal current areas/widths. Area/span equivalent thickness excludes gaps
and is not a whole-current depth. Native brackets are sampling scenarios under
the interpolation definition, not confidence/physical/annual bounds. No between-
section depth surface, independent terrain clearance, physical-volume estimate,
whole-route profile, branch reassignment or global sum is established.

Offline cloud-only execution sequentially on one idle CPU; one shared absolute
60second clock including synthetic tests, SIGTERM handling and fresh outputs.
DescriptorQueryv3 explicit zero prior numeric/byte charges, before-decode numeric
reservation/cache,250000tokens/32MBuniqueJSON/2.5MBpacket/2.4MBwholeoutput. This
ordinary derived query does not reopen or renew native acquisition cases.
Sparse checkout excludes source-data and old native producers. No local science,
UI/runtime/default-query/WASM/main/eddy changes; all prior results stay frozen.

Tests must cover analytic strip units, paired/censored/surface boundaries, split-
merge/disjoint support, adjacency, all4owners/48cases/43anchors/5gaps, original
primary/frame/provenance/time mutations, single-level bounds, minimum-span versus
depth/thickness semantics, source immutability, and full JSON/both CSV roundtrips.
Retain the one cloud artifact only after all branch jobs terminate, install exact
bytes and publish through the existing guarded inlineUTF8GitTreeAPI procedure.
