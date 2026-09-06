# Evidence Receipts

*A map can be beautiful before its noun is justified. The receipt records what
the evidence actually earned.*

**Evidence class:** this guide defines an OSW audit format and applies it to
eighteen worked evidence cases. It does not create new observations or promote a model result
into an observation.

[Inspect the eighteen machine-readable receipts](../research/ocean-object-evidence-receipts.json) ·
[view the first detected-object receipt](../figures/osw-d1-noaa-crw-mhw-point-2026.svg) ·
[view its connected daily footprint](../figures/osw-d2-noaa-crw-mhw-footprint-20260801.svg) ·
[follow the footprint lineage](../figures/osw-d3-noaa-crw-mhw-lineage-2026.svg) ·
[inspect the gap-identity bakeoff](../figures/osw-d4-noaa-crw-mhw-gap-identity-2026.svg) ·
[inspect the tracking-robustness matrix](../figures/osw-d5-noaa-crw-mhw-tracking-sensitivity-2026.svg) ·
[inspect the branch-policy bakeoff](../figures/osw-d6-noaa-crw-mhw-branch-sensitivity-2026.svg) ·
[inspect the multi-branch family](../figures/osw-d7-noaa-crw-mhw-lineage-family-2026.svg) ·
[inspect the family-pruning ladder](../figures/osw-d8-noaa-crw-mhw-family-pruning-2026.svg) ·
[inspect the typed temporal bridge](../figures/osw-d9-noaa-crw-mhw-typed-gap-graph-2026.svg) ·
[use the naming guide](13-HOW-TO-NAME-AN-OCEAN-PATCH.md) ·
[inspect the object registry](../research/ocean-object-classification.csv)

## The three-axis receipt

```text
WHERE DID IT COME FROM?       HOW FAR DID THE CLAIM GET?       DID THE NOUN PASS?
observation analysis          field                            pass
derived observation product  candidate                    ×   fail
assimilative reanalysis   ×   detected object                  not tested
simulation                    tracked object
conceptual synthesis          identity sensitivity
                              integrated quantity
                              mechanism hypothesis
```

These axes must remain separate. “Observation” identifies origin, not whether
a current or heatwave was detected. “Integrated quantity” identifies the claim
stage, not whether it came from instruments or reanalysis. “Pass” applies to one
declared identity test, not to every interpretation of the same pixels.

## What every receipt records

```text
source bytes + checksum
        ↓
variable · units · depth · time · footprint · baseline
        ↓
primary claim + representation
        ↓
candidate object ── required identity test ── pass / fail / not tested
        ↓
supports · does not support · next evidence · boundary statement
```

The `does_not_support` list is part of the result. It prevents a surface
temperature map from silently becoming heat content, a one-day anomaly from
becoming a marine heatwave, or a gateway transport from becoming convergence.

## Fifteen worked receipts

| Receipt | Earned claim | Identity tests not earned |
|---|---|---|
| OER001 | OISST surface-temperature anomaly field on 2026-08-01 | marine heatwave duration/rule; heat content; transport |
| OER002 | Argo-derived temperature anomaly at 300 dbar in July 2026 | water-mass property signature; vertically integrated heat content |
| OER003 | February 2018 ORAS5 volume and reference-relative heat transport across declared Arctic gates | convergence; storage; causal Arctic delivery |
| OER004 | 2018 ORAS5 surface heat exchange integrated over the Nordic room | heat inventory; advective convergence; complete budget |
| OER005 | 2026 NOAA CRW marine heatwave at one North Atlantic pixel | spatial footprint; subsurface heatwave; heat content; cause or impact |
| OER006 | Connected 41,025 km² footprint containing that pixel on 2026-08-01 | full-event tracking; subsurface volume; material identity; cause or impact |
| OER007 | 21-day exact-overlap lineage of daily footprints | universal identity across tracking rules; gap reconnection; parcel motion; mechanism |
| OER008 | One-day temporal-gap identity bakeoff | continuous August 11 threshold evidence; uniquely correct policy; material continuity |
| OER009 | Connectivity and minimum-overlap robustness bakeoff | universal adjacency equivalence; uniquely correct IoU threshold; mechanism |
| OER010 | Split/merge branch-selection bakeoff | uniquely correct branch score; material continuity; mechanism |
| OER011 | Complete exact-overlap lineage family around the anchor | one privileged heir; gap continuity; material genealogy; mechanism |
| OER012 | Minimum-area pruning ladder for the lineage family | unique scale cutoff; falsehood of removed branches; resolution independence |
| OER013 | Strict-daily graph versus explicitly typed one-day bridge | gap-day threshold evidence; interpolation; material continuity; complete post-gap family |
| OER014 | Separate-product OISST cross-check of the category bridge | product equivalence; local reheating cause; heat content; forcing or advection |
| OER015 | RTOFS surface horizontal-advection screen | native tracer budget; surface/vertical attribution; validation; causation |
| OER016 | GFS surface-energy / RTOFS mixed-layer screen | native model closure; reanalysis; vertical attribution; validation; causation |
| OER017 | RTOFS fixed 0–50 m storage screen | native-layer heat content; observed storage; budget closure; vertical attribution; causation |
| OER018 | RTOFS depth-integrated horizontal-advection screen | native tracer flux; conservative convergence; cross-model closure; vertical attribution; causation |

### OER001 — one warm surface map

The OISST anomaly carries a baseline, date, units, grid, source-response hash,
and observational-analysis provenance. It tells us where the analyzed surface
was warm or cold relative to the 1971–2000 climatology on one day.

That is still not a marine heatwave. The receipt marks the heatwave identity
test `not_tested` because one snapshot does not establish the specified
percentile, duration, gap, and spatial rules.

### OER002 — one subsurface level

The Argo analysis reaches below the surface, but it remains one mapped pressure
surface. At 300 dbar it supports a monthly potential-temperature anomaly under
the RG baseline and mapping method.

It does not establish a water mass because no volumetric temperature–salinity
or source signature was tested. It does not establish ocean heat content
because no depth integral, density/heat-capacity convention, geometry, or
reference state was evaluated.

### OER003 — crossing a gate

The Arctic receipt passes three related identity tests. Native wet faces and
their orientation establish each gate. Normal velocity integrated over face
area establishes volume transport. Adding temperature and an explicit
reference establishes reference-relative advective heat transport.

This is stronger than a current arrow, but narrower than a heat budget. A gate
reports crossing; convergence requires differences among every boundary, and
storage requires the changing inventory inside the room.

### OER004 — breathing through the surface

The Nordic receipt integrates monthly surface heat-flux density over 12,550 wet
cells with native areas and a declared sign. It therefore earns a surface heat
exchange claim for the defined room and year.

It does not directly measure ocean heat content. Surface exchange is only one
term in the heat-content tendency; lateral advection, storage, mixing,
unresolved boundaries, and sampling compatibility remain separate tests.

### OER005 — the first noun earned from a time series

OSW selected 42.125°N, 49.875°W because its separate OISST snapshot showed a
large positive anomaly there. NOAA Coral Reef Watch's independent 5-km derived
product then supplied 32 checksum-pinned daily category files. The pixel
contains a 27-day linked event from July 23 through August 18: 19 qualifying
days, a one-day gap, then seven qualifying days. The declared two-day gap rule
joins those already-qualified runs. Its maximum NOAA category is 2 (strong).

This passes the registry's marine-heatwave identity test at a point. It does
not yet create a heatmass polygon. That next noun requires spatially connected
neighboring detections and an explicit footprint-tracking rule.

### OER006 — the point becomes a place

On August 1, four-neighbor connectivity on NOAA's native 0.05° grid finds a
bounded patch containing the OSW-D1 anchor: 1,769 pixels and approximately
41,025 km² by spherical cell-area integration. Its irregular, hooked outline
is stored as exact latitude-row runs rather than an artist's blob. The patch is
almost entirely category 1, with three category-2 pixels.

This earns a daily spatial footprint. It does not establish that every daily
shape during the 27-day point event is the same evolving object. That requires
an explicit overlap, split, merge, persistence, and minimum-area policy—the
next rung from a map shape to a tracked ocean event.

### OER007 — the shape has a life of its own

The native-grid footprint can be followed through exact inherited pixels. The
governed primary branch begins on July 21—two days before the anchor itself
crosses the threshold—grows from roughly 2,622 km² to a maximum of 49,439 km²,
and collapses to 3,323 km² before ending on August 10. Across those 21 days its
area-weighted centroid travels about 450 km. The weakest transition retains
only 19.8% intersection-over-union, and five transitions expose more than one
overlapping branch candidate.

This produces the most important distinction yet. The pointwise Hobday-style
event joins qualifying runs across the one-day August 11 gap, giving 27 days.
Exact spatial inheritance does not: no August 11 active component shares even
one native pixel with the August 10 remnant. Calling the August 12 patch “the
same heatmass” therefore requires a new, explicit gap-bridging rule. Temporal
identity at one point and spatial identity of a changing patch are not the
same operation.

### OER008 — one gap, two legitimate answers

Seeding the post-gap patch independently reveals that August 10 and August 12
share 122 exact native grid locations. That is 84.1% of the small August 10
footprint and 26.7% of the larger post-gap patch, with intersection-over-union 0.254. No
spatial dilation or allowed displacement is needed.

Only the time policy changes the answer. Uninterrupted daily inheritance says
**split**, because none of the prior footprint pixels is threshold-active on
August 11. Permitting one missing threshold day says **join**, because the
same locations become active again and both pointwise runs satisfy the
five-day minimum. `policy_dependent` is therefore an evidence result, not an
embarrassment: it identifies the exact convention on which the public noun
depends.

### OER009 — the ambiguity has an address

Changing spatial adjacency from edge-only to edge-or-corner adds one
corner-connected cell on three of 21 tracked days. Despite those small geometry
changes, all five lineage lifetimes and both exact gap footprints remain
identical. The live identity choice is overlap strictness. Any exact overlap or IoU at
least 0.10 preserves the 21-day July 21–August 10 lineage. IoU at least 0.20 or
0.25 produces the same 18-day July 21–August 7 plateau. Requiring IoU 0.50 is so
strict that neither transition touching the July 23 seed passes.

The disputed transition is now explicit rather than vaguely “sensitive.” From
August 7 to 8, 216 exact native cells persist, yet intersection-over-union falls
to 0.198 because the footprint reshapes substantially. An absolute-touch rule
keeps the lineage; a moderate proportional-overlap rule ends it. That is a
definition choice about threshold-state identity—not evidence that water
parcels separated, returned, or changed mechanism.

The five overlap cutoffs are an illustrative diagnostic sweep, not a
literature-calibrated claim that 0.20 or 0.25 is the uniquely correct threshold.

### OER010 — the denominator chooses the heir

Five D3 transitions contain more than one overlapping component. Largest exact
intersection, greatest IoU, and largest overlapping component nevertheless
select the same native cells for all 21 days. Their agreement is stronger than
matching dates alone: the stored component hashes agree cell for cell.

Maximizing only the fraction of a candidate inherited from the seed-side shape
behaves differently. On July 30 it prefers a fully inherited 12-cell splinter
over the 1,233-cell main component, whose inherited fraction is 82%. After
temporarily merging back, it selects a fully inherited one-cell splinter on
August 3 instead of the 1,977-cell main component, then has no successor on
August 4. Its lineage lasts 14 days.

The arithmetic is valid; the identity meaning is poor without a scale or
two-sided-overlap condition. A very small candidate can score 100% simply by
being contained inside the prior footprint. OSW therefore treats branch choice
as a governed part of the object definition and does not equate a one-sided
fraction with physical continuity.

### OER011 — stop crowning one heir

Keeping every adjacent-day exact-overlap connection converts the same evidence
into a directed lineage family: 28 daily components and 29 edges from July 21
through August 10. D3's 21-node primary lineage remains intact as the trunk,
but seven off-primary components are no longer discarded. Five split nodes and
one merge node make the topology explicit.

Five side components terminate without a successor. Two July 30 splinters—12
pixels and one pixel—merge back into the primary July 31 component. The largest
side component contains 54 pixels on August 8 and terminates the next day.
These fates explain why a single-branch rule can be useful while remaining
incomplete.

The graph does not claim that water parcels split and recombined. Its nodes are
threshold-state footprints and its edges are exact shared grid locations. It
also stops before the inactive August 11 field; adding the D4 gap bridge would
require a visibly different temporal-edge type.

### OER012 — scale changes the family, not the trunk

Applying minimum daily component areas of 0, 25, 250, 500, 1,000, and 1,500
km² leaves all 21 primary-trunk nodes intact without an override. The side
family contracts from seven components to four, four, two, one, and finally
zero. At 1,500 km² the graph is exactly the D3 trunk.

The steps have concrete meanings. A 25 km² cutoff removes three one-cell
components of roughly 23 km² each. Nothing else changes at 250 km². At 500
km², the 279 and 465 km² components disappear and the only merge-back topology
vanishes with them. At 1,000 km² only the 1,254 km² August 8 side branch
remains; at 1,500 km² it too is removed.

This does not prove that small components are false. It proves that “five
splits and one merge” is a scale-conditioned description, whereas the primary
trunk is stable across this particular diagnostic ladder. A published family
map therefore needs an area convention tied to product resolution and purpose.

### OER013 — preserve the threshold-inactive day in the edge

The strict D7 graph has 28 nodes and 29 adjacent-day exact-overlap edges and
ends on August 10. D4 supplies a separately governed seven-day primary lineage
from August 12–18. Joining them adds seven nodes, six ordinary daily edges, and
exactly one new edge type: a conditional bridge from August 10 to 12.

That dashed bridge stores the reason it differs. It spans two elapsed days and
one threshold-inactive day; zero August 10 footprint cells remain active on
August 11. Its endpoints nevertheless share 122 exact grid locations, or 84.1%
of the prior footprint and 26.7% of the post-gap footprint, with IoU 0.254 and
zero spatial dilation. The conditional graph therefore has 35 nodes and 36
edges and reaches August 18.

Nothing is interpolated onto August 11. Solid edges mean consecutive active
days; the dashed edge means a declared event-identity allowance. The post-gap
addition is one primary lineage rather than a complete branch-family expansion,
so the graph exposes both its temporal policy and its asymmetric completeness.

### OER014 — a category return is not necessarily a local rebound

Six NOAA OISST fields from a separate analysis cover August 7–12 over a fixed 12-by-17-cell
box around the CRW anchor. From August 11 to 12, the CoralTemp-derived category
at the anchor returns from zero to one. The nearest 0.25-degree OISST cell does
not warm with it: SST falls 0.13°C. At the same time, the area-weighted fixed-box
mean rises 0.160°C and the box maximum rises 0.18°C.

This is not a contradiction that one product can settle. OISST and CoralTemp
have different grids, inputs, processing, and thermal definitions, while the
category also depends on a daily climatological threshold. It does establish a
useful guardrail: do not narrate the August 12 category return as observed local
reheating. The paired pattern instead motivates explicit tests of spatial
rearrangement, product sensitivity, surface forcing, currents, and mixing.

### OER015 — motion matters, but it does not supply most bridge-day warming

Six NOAA RTOFS nowcast snapshots put surface temperature, surface velocity, and
diagnostic mixed-layer thickness on one 1/12-degree curvilinear grid. Local
tangent-plane temperature gradients convert the velocity into an Eulerian
horizontal-advection tendency. The calculation uses the mean of each daily
interval's endpoint tendencies and retains a four- versus eight-neighbor
gradient-stencil check.

From August 11 to 12, the fixed RTOFS box warms 0.5396°C/day. Horizontal
the signed advection term is +0.0708°C/day—13.1% of that same-sign mean—leaving
+0.4688°C/day unresolved. At the anchor, horizontal advection is −0.109°C/day
while modeled temperature rises +0.601°C/day, so motion opposes rather than
explains local warming there. The box-mean diagnostic mixed layer also shoals
from 19.497 to 7.801 m, an important context for the next surface-forcing test.

The remainder is not “the atmosphere.” It combines surface fluxes, vertical
advection and mixing, entrainment, diffusion, assimilation increments,
time-sampling, gradient, and numerical errors. D11 is therefore a mechanism
screen and exclusion result, not a closed heat budget or causal attribution.

### OER016 — surface gain is material, but depth controls its warming scale

Twenty archived NOAA GFS forecast files supply four non-overlapping six-hour
means for each of five daily intervals. Six surface fields reconstruct net
downward heat flux: downward shortwave and longwave minus upward shortwave,
longwave, latent, and sensible components. Every retained GRIB message carries
its original index line, byte range, metadata, and SHA-256 receipt.

The fixed box loses surface heat on August 7–9 and gains it on August 10–11.
For the August 11–12 bridge interval, the GFS mean is +112.61 W/m² into the
surface. Bilinear sampling on the RTOFS grid and mixed-layer scaling gives
+0.1219°C/day for box-mean flux over box-mean starting depth, +0.1800°C/day
when starting depths are floored at 5 m, and +0.3381°C/day with native
cellwise endpoint-mean depth. Those scales span about 26–72% of D11's
+0.4688°C/day pre-flux remainder.

That span is the result, not nuisance uncertainty: very shallow diagnostic
layers make `Q/(ρCp h)` nonlinear. GFS and RTOFS also have different grids,
physics, initialization, and analysis cycles. OER016 therefore supports a
contemporaneous and material surface-energy contribution, while withholding
native budget closure, reanalysis status, vertical-process attribution,
independent validation, and causation.

### OER017 — the surface intensifies, and the fixed upper column gains heat

Six RTOFS nowcast profiles sample potential temperature at fifteen standard
depths from the surface through 50 m. Trapezoidal integration over fixed 10,
20, 30, and 50 m columns avoids dividing by the rapidly changing diagnostic
mixed-layer thickness used in OER016.

From August 11 to 12 the fixed-box surface warms +0.5396°C while the 0–50 m
column mean warms +0.0997°C. The surface signal is therefore 5.4 times larger,
but the column does not merely rearrange unchanged heat: its fixed-depth
storage tendency is positive. The cumulative scale rises from +92.13 W/m² in
0–10 m to +236.03 W/m² in 0–50 m. GFS surface gain is 47.7% of that 0–50 m
box magnitude. At the anchor, however, the modeled column-storage scale is
+1739 W/m², far beyond its +87 W/m² local GFS surface gain.

OER017 therefore rejects both simple extremes: this is neither surface-only
warming of an unchanged upper column nor a surface-flux-closed event. It remains
a standard-depth, constant-`ρCp` storage proxy. Horizontal and vertical
transport, mixing, shortwave penetration, analysis increments, native-layer
geometry, and cross-model mismatch remain open.

### OER018 — motion was hiding below the surface

The upper-ocean cube also carries horizontal velocity at every one of its
fifteen depths. Applying the D11 local-gradient method level by level and then
integrating changes the apparent mechanism ranking. Horizontal advection grows
from +21.01 W/m² through 10 m to +171.21 W/m² through 50 m. The latter is 72.5%
of the +236.03 W/m² fixed-column storage scale, even though D11's surface-only
term was just 13.1% of surface warming. Those percentages use different
vertical supports and denominators; they are a comparison of two diagnostics,
not one fraction increasing with depth.

Adding +112.61 W/m² GFS surface gain makes the two resolved scales 120.2% of
storage and leaves −47.79 W/m². That is encouraging magnitude agreement, not
a native budget closure: surface forcing comes from another operational model,
and `−u·∇T` on interpolated standard levels is not conservative native tracer
convergence. At the anchor, integrated horizontal advection is +715.66 W/m²,
but +936.28 W/m²—53.8% of storage—remains unresolved.

OER018 establishes the vertical lesson without overclaiming the budget:
surface diagnostics can miss a major subsurface motion term. Vertical exchange,
mixing, shortwave penetration, assimilation increments, interpolation, and
time-sampling remain in the partial residual.

## Why four more registry objects were necessary

The receipt audit found that OSW already named gates, branches, and control
volumes but lacked exact entries for the quantities computed through them. The
registry therefore now includes:

- **volume transport** — a signed velocity–area section integral;
- **heat transport** — a convention-declared heat/enthalpy section integral;
- **ocean heat content** — an inventory over depth, area, and reference state;
- **ocean surface heat flux** — energy crossing the air–ocean boundary per area
  and time, optionally integrated over a declared surface.

CF provides governed ocean-transport terminology, while GOOS identifies ocean
surface heat flux and subsurface temperature among the sustained variables
needed to assess ocean state. These are established scientific quantities; OSW
is only placing them into its object-and-evidence grammar.

## Planetary boundary

The same receipt axes apply to remote planetary data, but the origin must name
the actual observation: for example, cloud-top radiance or retrieved
temperature rather than “deep atmospheric heat.” A visible band can remain a
field or candidate without passing the identity test for a jet, material body,
heat inventory, or transport.

## Common mistakes

- Treating observational origin as proof that a named object was detected.
- Calling assimilative reanalysis either pure observation or pure simulation.
- Recording what a source contains but not the exact transformed artifact.
- Omitting depth, time support, baseline, sign, geometry, or units.
- Using `fail` when the required test was never performed; use `not_tested`.
- Letting a passed gate-transport test imply convergence or storage.
- Hiding unsupported interpretations outside the machine-readable result.
- Treating a checksum as scientific validation rather than byte identity.

## Use the receipts

The [machine-readable collection](../research/ocean-object-evidence-receipts.json)
is generated from checksum-pinned OSW artifacts by
[`build_ocean_object_evidence_receipts.py`](../analysis/build_ocean_object_evidence_receipts.py).
It is a worked contract for future atlas layers, not yet a universal schema.

[Field Guide index](README.md) · [Naming guide](13-HOW-TO-NAME-AN-OCEAN-PATCH.md) ·
[Gates and transports](04-GATES-TRANSPORTS-AND-RELAYS.md) ·
[Transformation and overturning](05-TRANSFORMATION-AND-OVERTURNING.md)
