# OSW project history

This record preserves changes in the project's way of seeing the ocean, not
only software releases. Atlas version status remains in `README.md` and
`PREVIEW-STATUS.md`.

## 2026-09-08 — The ocean gains a vertical address

The 56-province reference answered “where on the ocean surface?” but left the
water beneath it without a complete address. OSW now pairs any declared
horizontal reference with one of five conventional pelagic depth bands. The
result assigns every valid wet voxel exactly one horizontal × vertical address,
truncated honestly by bathymetry.

The distinction that makes the system useful is also its limit: depth bands are
reference geography, while mixed layers, thermoclines, haloclines, pycnoclines,
water masses, and bottom boundary layers are diagnosed physical overlays. They
may cross, overlap, disappear, or depend on a stated criterion. The new address
therefore covers the ocean without claiming to have partitioned all of its
physics. Guide 15 records edition-1 intervals, endpoint rules, masks, vertical
coordinate requirements, and the boundary against false full-depth ecological
or transport claims. Six new reference terms bring the editorial registry to
116 objects and 112 relations.

The first browser workbench turns that definition into an inspectable grammar:
all 56 reference identities can pair with any edition-1 band, shelf/basin/trench
teaching columns demonstrate bathymetric truncation, and independent regime
overlays can be switched on without changing the address. The workbench also
makes an important absence visible: selecting a cross-product class does not
prove it is occupied. Exact province geometry and versioned bathymetry must be
intersected before OSW can claim local wet volume.

The next evidence step samples GEBCO_2026 at the nearest 15-arc-second pixel
center to each approximate OSW seed. Fifty-three seeds return bathymetric depth;
NEWZ, NWCS, and REDS return positive elevation and remain visibly non-wet rather
than being nudged offshore. The result upgrades one column in the workbench
from illustration to a measured grid cell while preserving the harder limit:
one seed is not a province mean, extent, profile, or occupancy fraction.
The matching Type Identifier cells prevent “GEBCO value” from becoming a false
synonym for direct sounding: 28 seeds use direct-measurement codes, 24 use
indirect or interpolated codes, one uses a mixed/unknown pre-generated grid,
and three are land.

The point screen then widens into 56 local bathymetry neighborhoods. Each uses
1,089 paired elevation/TID samples across an 8° × 8° window, enough to reveal
nearby shelves, slopes, basins, trenches, and land contact without inventing a
province outline. Twenty-nine windows are fully wet at this sampling and 27
mix land and water. Their 60,984 grid points are longitude/latitude samples—not
equal-area fractions or province statistics—and the workbench says so beside
both the depth-class and source-type views.

The square-window limitation then yields to the first source-aligned true
footprint. Marine Regions Version 4 polygons are intersected against a global
0.25° GEBCO elevation/TID substrate: 681,631 wet centers across 54 territories,
weighted by spherical cell area and rendered on Oceanic Mollweide. The result
does more than make a prettier map. It reveals that OSW had been holding two
Longhurst editions in one mental picture. The older directory has 56 identities;
the downloadable revised 2007 geometry has 54, with five code aliases and no
separate `NPSE` or `OCAL` polygon. OSW keeps both names visible and fabricates
neither missing border.

Three source rings require recorded validity repair, while 5,519 polygon centers
disagree with GEBCO's wet mask and 2,772 wet GEBCO centers fall outside the
source cover. These mismatches are retained as evidence. “True footprint” now
means source-aligned static ecological geometry at a declared raster sampling;
it still does not mean a moving habitat, current, water mass, heat field, or
transport boundary.

## 2026-09-05 — Ocean objects become a field guide

The maps produced a larger question: are OSW's jets, bands, water masses, and
relays new objects, or new names for existing science? A literature grounding
found mature but partly separate traditions for water masses, fronts, jets,
eddies, Lagrangian coherent structures, transformation, ecological provinces,
dynamic seascapes, and marine heatwaves. Contemporary Nordic research also
independently describes the branching, cooling, recirculation, and Arctic relay
that the 2018 OSW control volume exposes.

OSW therefore makes no priority claim for the component science. Its proposed
contribution is integration: one public object-card grammar declaring definition,
boundary, dimension, lifetime, measurement, transport, scale, counterexample,
and status. Thirteen linked guides now teach the overlapping object families and
the legitimate—but bounded—rotating-fluid comparison with gas giants. The same
parcel can belong to several objects because each answers a different question.

The guide synthesis then became a faceted classification rather than a false
single hierarchy. Version 0.1 now records 106 teaching terms across 13 ontological
types and 101 qualified relations. Each term declares the test that identifies
it, its geometry, time behavior, coverage promise, mobility, evidence status,
and external vocabulary family. The key advance is structural: a water mass,
current, front, heatwave, ridge, wave, and analyst-drawn gate no longer compete
as if they were the same kind of object. A separate relationship graph records
how they carry, bound, transform, steer, overlap, and measure one another. The
73rd term, **sill**, was added when the seafloor guide demonstrated that the
controlling crest of a passage is neither the whole ridge nor an analyst-drawn
gate—a useful proof that the registry must grow with sharper distinctions.
Guide 09 then added seven wave and water-level objects after separating pattern
propagation from parcel motion: surface gravity wave, tidal current, Kelvin
wave, inertial oscillation, tsunami, storm surge, and seiche. The round total of
80 was again a versioned editorial count, not a natural constant. Guide 10 then
made the vertical dimension legible without collapsing unlike evidence: a
source-tagged plume, an upward velocity field, reversible isopycnal heave, and
irreversible cross-density transformation are now separate objects. Eight
refinements bring the registry to 88, including coastal and equatorial
upwelling, Ekman pumping, meltwater plumes, intrusions, and turbidity currents.
The count remains versioned and editorial rather than a natural constant.
Guide 11 then removed the cartographic fiction that polar ice is one white
thing. Sea-ice cover, floes, pack ice, fast ice, leads, polynyas, glacier-fed
ice shelves, grounding lines, and liquid ocean cavities now have distinct
identity tests. The grounding line also required a thirteenth ontological type,
**contact boundary**, because a grounded-to-floating transition is not a
property-gradient front. Brine rejection and basal melting remain transformations rather
than shapes. Most importantly for the Antarctic heat question, the cavity is an
ocean room: heat must cross shelf and cavity gates, circulate beneath a moving
roof, and reach the ice–ocean boundary layer before it can support basal melt.
Guide 12 extended the same discipline to life and chemistry. It separates
persistent oxygen-minimum structure from thresholded hypoxia, chlorophyll proxy
from biomass and production, ordinary bloom from harmful impact, and chemical
concentration from integrated pool and boundary flux. Biological and chemical
objects now connect directly to currents, upwelling, transformation, provinces,
gates, and control volumes without being mistaken for those physical objects.
Guide 13 then closed the navigation gap across the growing system. A generated
visual matrix begins with a five-step evidence ladder—measure, organize,
classify, integrate, cross—then shows 13 equal type cards and the sparse pattern
of 24 identity tests across them. Its central rule is procedural: begin with the
measurand and earn the noun. Registry counts remain visibly editorial, while a
reflowable guide provides the complete textual equivalent of the SVG.

The first evidence-receipt audit then found four conspicuous absences in the
registry itself: volume transport, heat transport, ocean heat content, and ocean
surface heat flux. Adding these established quantities brings the live registry
to 110 terms and 107 relations. Guide 14 separates evidence origin, claim stage,
and identity-test outcome, then applies that grammar to four existing OSW
artifacts. A one-day anomaly can now remain a valid field while explicitly not
earning the marine-heatwave noun; a section integral can earn heat transport
without silently becoming convergence, storage, or causal delivery.

The fifth receipt crosses the next evidence-ladder rung. An independently
selected North Atlantic anomaly point was tested against 32 daily NOAA Coral
Reef Watch files. A 27-day linked event (July 23–August 18, maximum category 2)
passes OBJ046's duration rule, making it OSW's first observation-derived
detected object. It remains a point event, not yet a spatial heatmass.

The next receipt then gives that point a measured daily shape. Four-neighbor
connectivity on the native NOAA grid finds a bounded, irregular 1,769-pixel
footprint covering about 41,025 km² on August 1. This is OSW's first
data-derived heatwave boundary rather than a schematic orange blob. It remains
a daily footprint until overlap, split, merge, and persistence rules track it
through time.

OSW-D3 then applies that tracking rule instead of assuming continuity by eye.
Greatest exact-pixel inheritance follows the footprint for 21 days, July 21 to
August 10, across about 450 km of centroid motion. The footprint grows to
49,439 km², fragments through five branch-ambiguous transitions, and contracts
to a 3,323 km² remnant. On August 11 its exact-overlap lineage ends—even though
the pointwise duration rule later reconnects the anchor across that one-day
gap. This exposes a foundational distinction for the atlas: a point event and
a moving spatial object can have different legitimate lifetimes.

OSW-D4 isolates the disagreement instead of smoothing it away. The August 10
footprint and independently seeded August 12 footprint share 122 exact grid
locations: 84.1% become active again, and no spatial dilation is needed. Daily
inheritance still splits them because August 11 has no active inherited pixel;
a one-day gap policy joins them because both surrounding runs pass duration.
OSW therefore adds `identity_sensitivity` and `policy_dependent` to its evidence
grammar. The atlas can now say not only what object was detected, but which
declared convention makes two appearances “the same” object.

OSW-D5 then locates the ambiguity precisely. Edge-plus-corner connectivity adds
one cell to three of 21 daily components, yet both adjacency rules produce the
same five lifetimes and exact 122-cell gap bridge. The lifetime instead forms three overlap regimes:
21 days for any touch or IoU at least 0.10, an 18-day plateau for IoU at least
0.20 or 0.25, and only the seed day at IoU at least 0.50. The decisive moderate
edge is August 7 to 8: 216 exact cells persist, but extensive reshaping reduces
IoU to 0.198. “Sensitive to method” has become a dated, measured statement.

OSW-D6 then challenges the rule used at the five visible splits. Largest shared
footprint, greatest IoU, and largest overlapping component reproduce the same
21 daily components cell for cell. A one-sided inherited-fraction rule instead
chooses a 12-cell splinter on July 30 and a one-cell splinter on August 3 because
both are 100% inherited; it ends on August 3 after only 14 days. This exposes a
denominator trap: perfect inheritance of a tiny fragment is not necessarily the
best continuation of the named object.

OSW-D7 removes the forced-heir assumption altogether. Retaining every
adjacent-day component reachable by exact overlap yields a 28-node, 29-edge
family around the anchor. The D3 path remains a 21-node trunk, while seven side
components expose five splits and one merge. Five side branches terminate; two
July 30 splinters merge back on July 31. The result changes the representation,
not the physics: it is a threshold-state genealogy, not a claim that material
water divided and recombined.

OSW-D8 then asks how much of that family survives a declared minimum daily
area. Across thresholds from zero to 1,500 km², every one of the 21 primary
nodes remains without special protection. The seven side components contract
through a four–four–two–one–zero ladder; the merge disappears at 500 km² and
all side topology disappears at 1,500 km². The durable claim is therefore the
trunk. Branch, split, and merge counts are explicitly scale-conditioned.

OSW-D9 then reconnects the August episode without falsifying the threshold-inactive day.
The strict exact-daily graph remains 28 nodes and 29 edges through August 10.
A visibly and structurally different dashed edge spans the threshold-inactive
August 11 field and joins 122 shared endpoint cells to D4's seven-day post-gap
primary lineage. Under that declared policy the graph becomes 35 nodes and 36
edges through August 18. The gap is preserved as metadata, not painted over as
an ordinary day.

OSW-D10 then asks whether that category return is also a local temperature
rebound in an independent product. It is not. From August 11 to 12 the nearest
OISST cell cools 0.13°C even as the CRW category returns from zero to one. The
fixed OISST neighborhood mean warms 0.160°C and its maximum warms 0.18°C. This
separates a threshold-state transition from a simple local-heating story and
makes spatial rearrangement, product sensitivity, and a real tendency budget
the next evidence targets.

OSW-D11 fills the threshold-inactive day with physical model state rather than
another category edge. Six public NOAA RTOFS snapshots place surface
temperature, currents, and diagnostic mixed-layer thickness on one grid. Across
August 11–12 the fixed box warms 0.5396°C/day, while endpoint-mean horizontal
the signed advection term is only 0.0708°C/day and opposes warming at the anchor. The
0.4688°C/day remainder is deliberately unnamed: the mixed layer shoals sharply,
but surface forcing, vertical processes, mixing, assimilation, and numerical
terms must be measured before mechanism attribution.

OSW-D12 adds the missing surface-energy scale without relabeling the D11
remainder as “the atmosphere.” Twenty archived GFS forecast files contribute
four non-overlapping six-hour means per day for downward and upward shortwave,
longwave, latent, and sensible heat flux. The fixed box changes from net surface
heat loss on August 7–9 to gain on August 10–11; the bridge interval receives
+112.61 W/m². Scaling that gain with RTOFS diagnostic mixed-layer thickness
supports roughly +0.12 to +0.34°C/day across declared depth treatments, versus
the +0.4688°C/day pre-flux remainder. The result is the first explicit
air–sea/ocean-layer intersection in the tracked-object chain—and remains a
cross-system plausibility screen, not a native model closure or causal result.

OSW-D13 then removes the unstable diagnostic mixed-layer denominator entirely.
Fifteen RTOFS standard-depth temperatures define fixed 0–10, 0–20, 0–30,
and 0–50 m columns on the same 4,221 cells. During August 11–12 the box surface
warms +0.5396°C while the 0–50 m mean warms +0.0997°C: the surface intensifies
5.4 times faster, yet the upper ocean genuinely gains heat. The fixed-column
storage scale grows from +92 W/m² in the upper 10 m to +236 W/m² through 50 m.
GFS surface gain is about 48% of that 0–50 m magnitude, and the anchor's much
larger column change cannot come from local surface flux alone. The next target
is therefore depth-integrated horizontal advection, followed by vertical and
assimilation terms—not another surface-only explanation.

OSW-D14 overturns the surface-only mechanism ranking. The D11 surface
horizontal-advection diagnostic was only 13.1% of modeled surface warming, but
the same offline `−u·∇T` calculation integrated through 50 m is +171.21 W/m²,
72.5% of the +236.03 W/m² fixed-column storage scale. Together with +112.61
W/m² GFS surface gain, the box terms total 120.2% and leave a modest −47.79
W/m² partial residual. This numerical near-closure is deliberately not called
a budget closure because the surface term crosses model systems and the
advection is neither native tracer flux nor conservative convergence. At the
anchor, advection changes from −30 W/m² through 10 m to +716 W/m² through
50 m while 53.8% of storage remains unresolved. The conceptual advance is
clear: motion that looks secondary at the skin can dominate the upper-column
story. The 13.1% and 72.5% ratios have different denominators and are not a
single fraction increasing with depth.

## 2026-09-05 — The Arctic gates become a room

Open gateway arrows answered which way water and reference-relative heat cross
individual sections, but they could not answer where that heat changes or
goes. OSW therefore promoted the Nordic Seas from background water into a
proposed control volume: Atlantic water enters across three Greenland–Scotland
Ridge section intents, while the accepted Fram and Norway–Svalbard sections
form distinct exits toward the Arctic.

The first plate began as a contract rather than a result, then earned a surface
boundary through failure. The original mesh did not reach Scotland. The first
Denmark intent missed Greenland by roughly 220 km. Fixed Faroe endpoints could
not support two independent land-attached cuts on the ORCA025 mask. Finally,
the first successful ridge cut leaked through the North Sea because Britain is
not joined to continental Europe. Each failure removed a cartographic
assumption.

The corrected room contains 12,550 wet surface T cells behind 284 unique native
faces: Denmark Strait, a continuous Iceland–Scotland Ridge cut, an explicit
northern North Sea closure, Fram Strait, and Norway–Svalbard. Every face
separates inside from outside and the interior reaches no mesh edge. Readiness
then passed a full-depth internal audit across all 284 faces. Readiness is now
five pass / three open; monthly state and budget terms remain unfinished. The
gate anatomy is radically asymmetric: Fram alone supplies 814 of 1,816 km² and
is the only section with most of its area below 700 m. The breakthrough is the
change in question—from “how much heat
crosses this line?” to “what happens to heat inside this ocean room?”

The room then acquired its first actual budget term. Native T-cell metrics and
twelve 2018 monthly surface-flux fields cover the exact interior. The
time-weighted forcing is −39.4 W/m², −106.8 TW, or −3.37 ZJ net downward:
the ocean loses heat overall, with four warming months against eight cooling
months. Readiness reaches six pass / two open, but this surface exchange is not
yet advective convergence, storage, or a complete transformation budget.

Twelve compact native T/S/U/V states then aligned the interior and all five
gates without downloading unused rectangles. Whole-room mass imbalance stays
within −0.064 to +0.074 Sv. At 0°C reference the time-weighted boundary term is
+96.8 TW convergent, dominated by +189 TW through Iceland–Scotland, aided by
+26 TW through Denmark Strait, and offset by −34 TW through Fram and −85 TW
through Norway–Svalbard. Finite-difference
storage and surface exchange leave a +37.7 TW diagnostic mean remainder. OSW
keeps that remainder named, visible, and unresolved rather than turning an
offline closure error into a mechanism. Readiness is seven pass / one open.

An independent archived quantity then rules out the most obvious numerical
suspect. ORAS5 `sohtcbtm` total-column heat content reproduces the reconstructed
monthly storage tendency at *r* = 0.99998 with 1.45 TW RMSE. Replacing storage
moves the mean remainder only from +37.7 to +37.9 TW. A live inventory of all
23 public native-grid variable families confirms that the monthly ICDC archive
does not expose the tendency, native tracer-advection, mixing, diffusion,
ice–ocean heat-exchange, or assimilation-increment fields needed to decompose
what remains. The negative result narrows the problem without naming a cause.

OSW next challenged the easiest narrative for that remainder with co-located
monthly ice concentration, ice thickness, and mixed-layer depth. The remainder
does not follow their smooth seasonal clock: its correlation is +0.05 with
area-mean ice concentration, −0.01 with an ice-volume proxy, and +0.33 with
mixed-layer depth. Twelve same-year months cannot identify a mechanism, but
they can reject the visual shortcut that the alternating remainder is simply
an ice-season curve under another name.

The next numerical challenge finally spans the annual gap. Changing only the
temperature assigned to each moving boundary face leaves inside- and
outside-cell estimates within ±2.25 TW of adjacent averaging. A monthly-mean
upwind donor rule adds 43.0 TW of convergence and moves the annual remainder
from +37.7 to −5.3 TW. Nearly all of that shift enters through the two southern
gates, especially Iceland–Scotland. OSW does not call this closure: the actual
model uses a nonlinear time-stepped tracer scheme, monthly residuals remain
large, and the archive does not contain its native fluxes. The result identifies
boundary tracer transport—not storage or a simple ice season—as the dominant
recoverable method sensitivity.

Separating the upwind estimate into paired branches turns the numerical result
back into oceanography. Denmark exports net water but imports heat because its
3.46 Sv inward branch is 4.67°C while its 5.07 Sv outward branch is only
1.41°C. Iceland–Scotland exchanges 22.62 Sv inward at 6.22°C against 19.23 Sv
outward at 4.48°C. Fram imports net water yet exports heat because its larger
inward branch is nearly freezing while its smaller outward branch is 1.94°C.
The conceptual unit changes again: a gate is not one arrow but two rivers whose
volume, direction, and temperature must remain paired.

Adding depth reveals that the paired rivers occupy a shallow heat system inside
much deeper geometry. The upwind sensitivity converges +148.8 TW above 700 m
and diverges 9.0 TW below. Iceland–Scotland supplies roughly 72–80 TW in each
of the first three layers; Norway–Svalbard removes nearly all of its heat above
300 m; Fram removes about 10–12 TW in every layer through 700 m and little
below. A deep gate is not necessarily a deep heat pathway.

Projecting the same arithmetic onto all 284 native faces replaces five smooth
gate arrows with interleaved heat jets. Only 115 faces add heat while 169 remove
it, yet a compact set of Atlantic inflow faces wins: the 20 strongest faces
carry 52% of 1,067 TW gross absolute exchange. Positive and negative faces
cancel 87%, leaving +140 TW net. The largest import (+66.4 TW) and export
(−30.3 TW) faces both occur along Iceland–Scotland. A gate total is the small
difference between much larger neighboring transports.

An area-normalization challenge then asks whether those hotspots merely trace
large faces. Twelve of the 20 strongest total-TW faces remain in the top 20 by
cross-sectional MW/m². Some secondary ranks change, proving geometry matters,
but the leading Iceland-side import survives as both +66.4 TW total and maximum
+7.66 MW/m² intensity. The dominant Atlantic jet is not manufactured by face
area alone.

The next view opens the word *intensity*. Net heat is factored exactly into wet
area, gross exchange speed, and a signed thermal transport factor. Their
P90/P10 spreads are 12.8×, 8.1×, and 22.7× respectively. The strongest
Atlantic import is simultaneously broad, fast, and thermally favorable rather
than winning through one geometric accident. The signed factor is deliberately
not called temperature because it also carries directional cancellation.

OSW then refuses to let an annual mean manufacture permanence. Every face is
reranked in each monthly mean. The leading Iceland-side import remains positive
and absolute rank #1 in all twelve; all 20 annual leaders retain their sign.
Each monthly top 20 contains 14–19 of the annual leaders, averaging 16.7. Only
88 of 284 faces keep one sign all year, so this persistence belongs to the
dominant exchange structure rather than to every boundary cell.

Adjacent faces then become candidate jet runs instead of isolated pixels. The
largest is a compact four-face Iceland-side import carrying +106.5 TW across a
33 km centerline span. Its opposite geometric archetype is a 33-face,
326 km Norway–Svalbard export band carrying −72.0 TW. Both retain their sign in
all twelve monthly means; the strongest ten runs together carry half the gross
exchange. Because annual-sign segmentation yields 95 runs—including 51
single-face fragments—OSW records components, not automatically named currents.

A four-scale bakeoff prevents those 95 components from hardening into false
ontology. Centered 3-face sign sums reduce the inventory to 53 runs and 13
singletons without displacing the compact +106.4 TW leader. At 5 faces the
dominant object changes: a broader 32-face Scotland-side band consolidates at
+144.3 TW while the original core persists inside it. Jet identity is
hierarchical and scale-dependent, not a single natural count produced by this
segmentation rule.

The face-count result then survives conversion to physical distance. Matched
20/3 and 30/5 km/face classifications agree on 277 and 278 of 284 faces; the
50/7 comparison still agrees on 266. The compact-to-broad hierarchy is not a
grid-index artifact, while the weaker coarse-scale match exposes where curved
paths and nonuniform spacing begin to matter.

The analysis finally reconnects spatial jets to the room's seasonal heat
account. Southern input and northern export co-vary at *r* = 0.81 in the same
month, the strongest of twelve circular alignments, while surface forcing and
storage track at *r* = 0.98. The internally consistent annual upwind account is
+260.4 TW south, −120.4 TW north, −107.6 TW surface, +26.5 TW storage, and
−5.8 TW unresolved. This is a timing screen across twelve confounded months,
not a parcel clock or causal attribution.

## 2026-09-05 — Velocity crosses the Arctic gates

The geometry surfaces became measurements for one deliberately limited month.
OSW retrieved checksum-pinned February 2018 native ORAS5 potential temperature,
salinity, U velocity, and V velocity and passed the same 75-level state through
Fram Strait and both noninterchangeable Barents definitions.

Fram is not a weak gate: it is a strong two-way gate whose +6.21 Sv northward
and −6.66 Sv southward branches nearly cancel to −0.45 Sv. The Barents proxy
and closure carry +3.23 and +3.64 Sv net eastward. Their +0.41 Sv difference
turns the earlier geometry warning into a measured consequence: changing what
the line encloses changes what it counts.

At a 0°C reference the three advective heat signals are +52, +73, and +81 TW.
Four T-to-face collocation rules leave volume invariant and move heat by at
most 1.71%. Literature-based joint T/S Atlantic Water classes expose warm,
salty inflow without erasing the complete signed section. One month and three
open gates still do not establish convergence, seasonality, climatology, or
heat delivered within the Arctic.

The remaining May, August, and November states then completed the four-snapshot
comparison. Every sampled month preserves the same directional grammar: net
water leaves through Fram, while water enters through either Barents section.
More surprisingly, Fram's 0°C-reference advective heat remains positive even
as its net volume remains negative. Warm inflow and colder export can therefore
carry opposite answers to “which way does the water go?” and “which way does
the temperature-weighted energy go?” The new plate makes that distinction the
center of the composition rather than a footnote.

## 2026-09-04 — The Arctic gate meets the grid

Before returning to transport, OSW tested whether the two Arctic entrance
lines even mean the same thing on the native curvilinear grid. They do not.
The downloaded ORCA025 mesh contains a clean, surface-land-bounded 60-face V
row across Fram Strait. At the Barents opening, however, the native U column
whose mean lies closest to 20°E curves from 15.40°E to 25.88°E over the target
latitude span and remains wet at both clipped ends.

The T mask sharpened the refusal: the approximate Bear Island target is wet in
ORCA025, and the nearest dry T cell lies more than 200 km away. The resulting
plate, **One gate fits the grid. One does not.**, now preserves a necessary
fork. Fram advances to full-depth mask and partial-cell tests. Barents must be
either a virtual-endpoint mixed U/V Fugløya–Bear observational proxy or a
separate land-bounded Norway–Svalbard model closure. This is geometry readiness
only—no state field or heat claim has crossed the gate.

OSW then refused to leave the fork abstract. A native-face bakeoff constructs
both paths under one topology contract. The 43-face observational proxy keeps
its wet virtual endpoints; the 73-face model closure reaches coast at Norway
and represented Svalbard land. Both mix U and V faces, remain connected through
F-grid corners, repeat no face, and duplicate no corner flux. Their successful
construction proves a sharper principle: numerical validity cannot erase
semantic difference.

The following sensitivity matrix asks which construction choice actually moves
those valid paths. Corridor penalties of 10, 20, and 40 km leave every fixed-
endpoint path unchanged. Nine plausible endpoint intents instead create nine
proxy paths and six closure paths; the most displaced face sets replace 100%
and 81% of their respective baselines. Endpoint placement is now a mandatory
future sensitivity, while the 20 km path cost survives only as a transparent
default—not as a physical scale or uncertainty estimate.

Only then did the paths become full-depth measurement surfaces. The same
partial-step operator used in the Drake audit produces zero native-mask
mismatches across all three Arctic sections. Fram opens 814 km² and descends
to 2,577 m; its deep area is intrinsic to the gateway. The two Barents meanings
open only 161 and 224 km² and remain shallower than 700 m. The visual lesson is
simple but consequential: a longer line need not be a deeper gate, and section
area constrains transport before velocity supplies it.

## 2026-09-04 — The current becomes a junction

OSW moved to the Agulhas corridor and rejected one more seductive arrow. The
source archive crosses its longitude storage seam at southern Africa, so two
matching native OSCAR windows were fetched, checksum-pinned, and stitched
without interpolation. The resulting 71-field regional substrate preserves the
coast, the retroflection, the eastward return corridor, and the Cape Basin.

The first audit asks a new question: can fast water have almost no mean
direction? In the retroflection sector it can. Mean sample speed is 0.50 m/s,
but vector coherence is only 8% because the flow turns and changes direction.
The Cape Basin is likewise energetic but weakly coherent, while the coastal
current and return-current sectors retain their expected southwestward and
eastward preferences.

The companion plate, **The current turns. Some water escapes.**, overlays 28
strict 45-day seasonal trajectories on the native annual vectors. It establishes
a new OSW visual verb—**current → turn → return**, with leakage rendered as an
intermittent branch field rather than a second river. It remains M2: the map
contains surface pathways, not transported volume or heat.

The next challenge source-tagged the question. One hundred eight nearby
upstream releases produced a large unresolved class, and nine plausible Cape
Basin/return gate pairs produced nine different fate censuses. Cape crossings
ranged from 2 to 20 and return crossings from 23 to 54. OSW therefore refused
to turn equal particle counts into a leakage percentage. The durable object is
now a three-part contract—source, destination, and time horizon—plus an explicit
sensitivity test for each.

The literature then supplied the promotion target. The first Agulhas M3
contract replaces the surface pilot with full-width/full-depth transport-
weighted releases at 32°S every five days for a year and four-year 3-D
advection. It also separates any GoodHope crossing from odd crossing parity:
the former measures exchange and transformation, while the latter asks whether
Indian-origin water remains in the South Atlantic. The six promotion checks
are now visible by design: one reference geometry is acquired and five remain
open. No new OSW M3 result will be drawn until a suitable eddy-rich dataset and
target-grid mapping are pinned.

The authors' own GEOMAR archive then changed the status of that block. OSW
ingested only three compact CC BY 4.0 derived files: the exact experiment
sections, four example trajectories, and annual transport by exit. The map
reveals that the leakage gate is literally bent—a long diagonal western leg
joined to a zonal northwest leg. Recomputing `West + Northwest` reproduces the
published 9.894 Sv mean and +0.464 Sv/decade archived-period trend, while the
east return exit averages 40.015 Sv. This is OSW's first attributed replication
of a transport-weighted Agulhas result. Geometry is acquired; raw 3-D velocity
for a new run is not.

## 2026-09-03 — The Arctic entrance becomes a pair

OSW moved from Drake Passage to the land-constrained Atlantic routes into the
Arctic. Two checksum-pinned native OSCAR substrates now cover Fram Strait and
the Barents Sea Opening over the same 71 historical fields. The first screen
immediately rejected a seductive simplification: averaging all of Fram Strait
produces southward surface motion, because western export and recirculation
hide the narrower northward Atlantic-side lane.

The paired plate therefore treats Fram as opposing traffic—western export,
central transition, and eastern inflow—while keeping the Barents entrance
separate. It is the first OSW gateway view whose main result is that a net arrow
can conceal the mechanism it was meant to explain. The plate remains M2:
nominal-15-m velocity, not full-depth volume or heat transport.

The first map was then challenged with 59 nearby screens. Western Fram export
and Barents inflow retain their signs in every tested case, but eastern Fram
motion reverses when the screen moves north of 79°N. That failure is productive:
the M2 line is now explicitly a branch hypothesis, while the M3 section must
earn its latitude through native full-depth geometry and transport sensitivity.

OSW then let the three declared lanes move. Across 112 deterministic seasonal
surface releases, completed western Fram tracks are unanimously southward,
eastern Fram paths split almost evenly between northward and other outcomes,
and completed Barents tracks are predominantly eastward. The resulting plate,
**Export is cleaner than inflow**, is the first Arctic corridor view. It also
makes every terminated track visible and keeps equal particle counts outside
the language of probability, volume, and heat.

The move to the Indonesian Throughflow changed the question from *where does
the line go?* to *can this grid hold the gate at all?* A 1:10m-coastline plate
now places every finite and masked OSCAR sample across five named candidate
screens. Lombok and Ombai visibly fail the M2 support threshold; Makassar and
Lifamatola retain grid support but return a contrary surface sign; only Timor
clears both tests. OSW records this as progress: the resolution refusal arrives
before a persuasive but unsupported pathway picture.

The refusal immediately selected a better tool. A compact public HYCOM
1/12° pull restores candidate wet sections at all five passages and adds 33
standard depth levels with temperature, salinity, and velocity. The companion
plate, **The finer grid opens all five**, makes the advancement and its limit
equally visible: resolution passes, but a single collocated daily field is not
native-face transport. The vertical curves also reveal why this matters—the
five named gates are not interchangeable tubes.

## 2026-08-30 — The ocean becomes time-resolved

M3 then opened with a refusal as important as its equation. OSW now has a
tested native-face section kernel for signed volume and reference-relative
advective heat transport, plus an exact dry-run ORAS5 seasonal request. The
kernel verifies its reference-temperature identity and explicitly leaves mass
closure unevaluated for one open section. Its committed numerical receipt is a
balanced synthetic case—not an observational or reanalysis result.

The intake audit also prevents a subtle category error: ORAS5 temperature and
velocity fields alone do not establish conservative face area. A real Drake
calculation remains blocked until native U/V face widths, layer thicknesses,
wet masks, coordinates, and staggering are present and validated. Nominal
quarter-degree area and rotated display velocity are not silently promoted to
transport geometry.

The first companion-source audit narrowed the blocker. Public ICDC metadata for
the 650,753,384-byte ORCA025 `mesh_mask.nc` exposes U/V coordinates, masks, and
horizontal metrics, but no explicit `e3u` or `e3v` arrays. OSW records the
38-variable inventory and stops at the unresolved native-face partial-cell
thickness instead of inventing one from T-point depths.

The reconstruction candidate then became executable without becoming
authoritative. A tested synthetic partial-step operator rebuilds T-cell bottom
thicknesses and takes adjacent minima for interior U/V faces. Unlike the older
utility, it emits no fabricated terminal row or column. The receipt proves the
array arithmetic and depth bounds only; the public server timed out during the
first live-subset attempt, so no Drake mesh values or transport were claimed.

The next service window transformed that limitation. OSW retrieved a compact,
checksummed native Drake mesh and found zero mask disagreements across more
than 3.47 million reconstructed wet U/V faces. Face-column depth closes to
floating-point roundoff and every wet area is positive. Geometry moved from a
synthetic candidate to a native consistency pass without being overstated as
an independent configuration proof.

Public ICDC monthly native T/U/V files then removed the historical pilot's CDS
credential dependency. A deterministic land-bounded gate at 67.125°W spans 87
U faces between the Antarctic Peninsula and South America. February 2018 gives
124.29 Sv net eastward: 221.43 Sv eastward balanced by 97.14 Sv westward. The
value is near the older canonical 134 Sv estimate, while newer cDrake work has
reported substantially larger transport—exactly why OSW labels this one month,
one member, and one gate rather than “the” Drake transport.

The first real heat calculation also makes the reference-temperature problem
visible instead of footnoted. The same section is 2.32 PW relative to −1.9°C,
1.35 PW relative to 0°C, and −1.20 PW relative to 5°C. With 124.29 Sv net
volume, those values must differ. One open section remains unable to claim
mass closure, convergence, or heat delivered to Antarctica.

The same gate then survived its first seasonal sampling without becoming a
climatology. February, May, August, and November net transports occupy a narrow
122.12–127.77 Sv band and average 124.18 Sv. The underlying eastward and
westward branches each range roughly 12–13 Sv, exposing cancellation that the
net alone conceals. The new passport places those branches beside all three
heat-reference answers rather than selecting the most convenient number.

Then the gate itself was challenged. Five nearby land-bounded native sections
spanning 69.125°W to 65.125°W produce four-sample volume means separated by
only 0.111 Sv. The corridor-scale volume answer is therefore much harder to
move than the line on the map. Heat exposes the remaining numerical choice:
four defensible offline T-to-U collocations shift the 0°C-reference mean by as
much as 0.050 PW. OSW now shows those two sensitivities side by side instead of
folding them into one false uncertainty score.

Finally the gate acquired depth. Preserving positive and negative contributions
within all 75 levels reveals that nearly half of net volume passes below 700 m,
while roughly two thirds of the 0°C-reference net heat signal lies above 700 m.
The result replaces the misleading choice between “surface current” and “deep
ocean”: Drake transport is full-depth, but temperature weighting makes its heat
portrait top-heavy.

The same gate was then reorganized by temperature rather than depth. Six
declared classes reveal a colder counterflow: 86.9% of westward transport is at
or below 2°C, while the eastward branch spans every class. The 1–3°C population
carries most of the net water. This is the first OSW “thermal population” view,
and it explicitly refuses the stronger water-mass label until salinity and
density join temperature.

Those populations then returned to geography. A native latitude–depth portrait
draws every wet gate cell and uses the section convention correctly: dots mark
eastward motion out of the page and crosses mark westward motion into it. The
cold Antarctic shelf, deep basin, warmer northern wedge, and embedded return
lanes become visible together. OSW now has both the accountable totals and the
physical slice that explains where they arise.

Finally the slice became an accounting map. Matched panels color each native
face by signed volume and signed 0°C-reference heat contribution, exposing the
alternating lanes that build the net result. Temperature weighting quiets the
cold southern and deep lanes and amplifies the warm northern wedge. The cells
close exactly to the gate totals, while a prominent resolution warning prevents
bright grid cells from becoming invented permanent “heat provinces.”

The motion ladder then crossed from gates to a control volume. A four-sided
native box balances roughly 125 Sv entering from the west against about 58 Sv
leaving east, 66 Sv leaving north, and less than 1 Sv leaving south. Its mean
volume imbalance is only 0.007 Sv. For the first time in OSW, the reference
temperature lesson resolves constructively: the closed-box heat answer changes
by only 0.000203 PW across three references, compared with multi-petawatt
differences at one open gate. The remaining 0.055 PW outward advective heat
flux is deliberately not called accumulation until storage and non-advective
terms join the budget.

The first control volume was immediately challenged rather than canonized.
Eight nested boxes remain volume-balanced to better than 0.010 Sv, yet their
mean heat residuals shift by 0.0336 PW with eastward extent and 0.0535 PW with
northward extent. This separates a robust numerical property—mass closure—from
a conditional diagnostic—the heat residual of a chosen region.

Storage then entered without pretending to finish the budget. A separate
checksummed T-cell metric companion supplies native area while preserving every
earlier mesh receipt. Heat content across 75,782 wet cells shows cooling through
August and slight warming by November. Sparse storage tendencies reduce but do
not close the advective residual; the remaining 0.013–0.084 PW is labeled
unresolved sampling and omitted physics, never a newly discovered heat source.

The storage probe then became monthly without becoming bloated. A compact native
contract retrieves only the box T cells and four boundary windows, reducing a
twelve-month state series to about 9.7 MB. It reproduces every prior anchor
exactly and resolves eleven tendencies. The mean gap persists at 0.0622 PW,
demonstrating that better sampling alone cannot substitute for missing budget
terms.

Surface forcing then entered on the same native grid. Twelve compact
`sohefldo` fields add only about 66 kB and preserve the exact control-box
footprint. The modeled net downward surface input averages 0.0195 PW across the
334-day comparison: enough to explain 31% of the previous 0.0622 PW remainder,
but not enough to close it. The remaining 0.0427 PW stays positive in every
interval. This is the first measured reduction of the M4 gap, and an equally
important refusal to rename the rest: ORAS5 restoring, ice, mixing, diffusion,
freshwater effects, assimilation increments, native tracer advection, and
time-integration still prevent causal attribution.

After the one-year surface field failed to justify a region count, merge, or
split, OSW stopped asking static summaries for a stronger answer. The first M2
artifact now preserves all 71 historical five-day OSCAR snapshots on the same
fixed 25-by-54 sampled grid. Timestamps, joint velocity masks, quantized
components, valid-cell counts, query provenance, and two checksums travel with
the data. Its downloaded-byte checksum exactly matches the seasonal M1 source.

This is a substrate milestone, not a pathway result. No parcel has been
released, no coastline rule or interpolation has been selected, and no track
has been mistaken for transported heat. The next experiment must declare those
solver choices before it draws a line.

The global substrate also exposed its own limit: its inherited 20-cell display
stride places samples about 6.7 degrees apart. OSW therefore packaged a second
71-frame field over Drake Passage, the Scotia Sea, and adjacent ACC waters at
roughly two-thirds of a degree, then at the archive's native roughly one-third
degree. The native regional artifact is the solver domain; the coarsened one is
retained as a falsification case, not permission to interpolate through
Patagonia, the Antarctic Peninsula, or any unresolved island.

Only then did OSW release parcels. Four historical dates each seed ten
equal-count wet-interior points across a schematic Drake section. A tested forward RK4
solver with a six-hour step, linear time interpolation, strict four-wet-corner
spatial interpolation, no diffusion, and immediate invalid-stencil termination
produces 35 complete 30-day tracks and preserves five losses. The plate makes
the solver receipt as prominent as the paths and explicitly refuses volume,
residence, coherence, temperature-advection, full-depth, or heat claims.

The declared six-hour step then survived a 3/6/12-hour bakeoff: all cases kept
the same 35 completions and five losses, and completed endpoints stayed within
1.40 km of the three-hour reference. Near-mask loss times stayed within six
hours, while still remaining disqualified as coastal-residence evidence.

The spatial bakeoff was far less forgiving. Native and coarsened regional
fields each produced 35 completions, but two identities switched status and
the 34 common completed endpoints separated by a median 79.01 km and as much as
310.68 km. OSW promoted the native field and recorded the matching total count
as a cautionary example of aggregate agreement hiding geographic failure.

Finally, OSW challenged the seed coordinates themselves. Each of the 40
central releases became a deterministic 3×3 neighborhood spanning ±15 km
along and across the section. Three hundred twenty-one of 360 tracks complete;
33 neighborhoods complete all nine, five are mixed, and two lose all nine.
Completed endpoints can nevertheless separate from their central result by as
much as 507.63 km. The new endpoint-cloud plate therefore promotes the corridor
while demoting every individual line from certainty to one sample of a locally
divergent flow.

The clock received the same treatment. Every central seed was started at five
times spanning −5 to +5 days. One hundred seventy-six of 200 tracks complete;
34 ten-day windows complete all five, two are mixed, and four lose all five.
The typical window median endpoint shift is 41.60 km and the maximum is 548.23
km. The matched “where” and “when” plates establish the corridor—not a single
coordinate or timestamp—as the durable M2 object.

The two experiments were finally paired without a composite score. Each seed
now carries adjacent position and clock marks. All four seasonal rows contain
eight of ten full/full seeds; globally the matrix contains 32 full/full, two
lost/lost, and six mixed or one-sided cases. This is the first M2 artifact that
shows a robust corridor interior and fragile margins while keeping the
evidence dimensions visibly separate.

## 2026-08-29 — Motion before zoning

OSW paused revision of the provisional 11/22/56 geography to study what the
water actually does. The new motion contract separates six increasingly strong
objects: surface speed, direction, simulated parcel pathways, temperature
advection, section heat transport, and transport convergence. This prevents a
beautiful current drawing or `temperature × velocity` proxy from silently
becoming a claimed full-depth heat budget.

The implementation sequence is now evidence-led: OSCAR for an explicitly
upper-30-m surface-motion atlas; conditional OceanParcels pathway ensembles;
then mass-checked three-dimensional ORAS5 gate pilots. Only after surface
motion and at least one gate budget are reproducible will the atlas ask whether
its frozen boundaries organize pathways, barriers, or convergence strongly
enough to justify changing the zones.

The first motion plate turns every OSW zone off. A single public historical
OSCAR field from 2018 proves the water-first grammar with 1,203 projected
direction-and-speed glyphs. It is a visual prototype using the older 2017.0
third-degree archive, not the production OSCAR v2.0 layer and not a heat-flow
map. The production ingestion path is nevertheless complete: exact-day NASA
CMR discovery, authenticated or local NetCDF input, joint vector masks,
quantization, provenance, checksums, and tests.

The motion study then expanded from one day to eleven sampled annual fields,
four meteorological-season means from 71 five-day fields, and a continuous
holds/turns skeleton. The first return to zoning was intentionally an audit,
not a redraw: the frozen 22-region overlay was compared with 759 supported
surface-motion cells across 44 sampled region adjacencies. The resulting plate
shows border cut-through warnings and internal directional disagreement side
by side, keeps sparse samples visually quiet, and preserves the gate-budget
requirement before any region is merged, split, or moved.

The audit then gained two falsification views. An along/across plate showed
that most well-supported borders are oblique or mixed rather than strongly
flow-following. A zoning-free partition-sensitivity bakeoff asked whether the
seasonal direction field chooses a natural count on its own. It did not: the
number of components and their retained coverage changed sharply with the
similarity threshold. An apparent 20-component result retained only 60% of
supported cells, so OSW recorded it as a mirage rather than a replacement map.

The next robustness pass exposed the mechanism behind that mirage. With the
same data and threshold, changing only four-neighbor to eight-neighbor graph
connectivity changed the sizable-component count from 20 to 9. By contrast,
omitting any single season left the four-neighbor count at 20–21. OSW therefore
recorded the component number as a method output—not an ocean fact.

OSW then replaced the temptation to rank the 22 regions with a passport
matrix. Every region receives the same five motion questions, but the columns
remain independent and missing screened-border evidence remains visibly
missing. This made internally contradictory regions, well-sampled regions, and
evidence-poor regions distinguishable without issuing premature merge or split
instructions.

The next scale-down exposed what those region averages concealed. All 56
province identities received seasonal direction signatures, and their
membership agreement was compared inside each of the 22 containers. Several
regions mixed strongly opposing province signatures, while singleton regions
had no membership test at all. OSW preserved the audit as diagnosis—not an
automatic split plan—because the all-pairs means are coarse and not adjacency
or exchange calculations.

An adjacency correction then replaced the broadest all-pairs claims with local
sampled province contacts. Several dramatic distant oppositions disappeared;
the surviving weak seams could be attached to specific owned edges and mapped
without crossing land. This became the first diagnosis that locates an
internal research target while explicitly refusing to call it a split line.

The internal seams were then challenged through time. Four matched seasonal
maps showed that none of the 32 sampled seams stayed opposed throughout DJF,
MAM, JJA, and SON; the 10 seams that remained in one class were all aligned.
This removed the last justification for turning a weak annual-mean seam into a
permanent boundary from the surface-motion pilot alone.

A second matched plate asks which of those arrows hold. Eleven sampled 2018
fields produce a mean vector and a declared directional-persistence ratio in
each sufficiently supported cell. Stable direction remains bright; energetic
but reversing motion fades. The result begins to distinguish durable surface
corridors from transient texture without converting persistence into a border.

The third matched motion view restores the seasonal dimension. Seventy-one
five-day fields form DJF, MAM, JJA, and SON panels with identical projection,
speed scale, persistence scale, and no zoning. Reversals and migrations can now
be distinguished from pathways that hold across the year. The plate remains a
one-year historical case, not a climatology.

A fourth view extracts the first motion skeleton without drawing borders.
“What holds” fades mean-direction glyphs according to agreement among four
seasonal directions. “What turns” colors each supported cell by its maximum
pairwise seasonal angle. Declared bins identify 402 aligned candidates, 288
turning candidates, and 69 diffuse or other cells, while the continuous values
remain primary. These are diagnostics to test future geography—not geography
itself.

## 2026-08-29 — Data enters the Ocean States map

The Oceanic Mollweide state view now carries seven matched observational
fields: absolute SST, SST anomaly, estimated SST analysis error, and Argo
potential-temperature anomalies at 10, 300, 700, and 1000 dbar. This is the
first test of the state geography as an evidence-bearing reference layer rather
than a colored classification poster.

The result establishes a strict visual contract: source grid cells remain the
primary marks; realm, region, and state borders provide orientation; no value
is averaged or assigned to an ocean state. Paired equal-area polar mirrors use
the same active field. Missing Argo polar coverage remains visibly empty rather
than being extrapolated. The seven plates therefore expose both ocean structure
and the limits of observation through one stable cartographic grammar.

## 2026-08-29 — Oceanic Mollweide wins the state map

### The third seminal moment

The project now recognizes three linked cartographic breakthroughs:

1. **Complete surface identity** — the classic 56 provinces let the whole
   surface ocean be named like states.
2. **Coast-owned form** — the approximate states inherit recognizable real
   coastlines while continents recede into background context.
3. **An ocean-state world map** — Oceanic Mollweide gives those states a
   convincing global composition with the Pacific as the central field.

The first matched projection bakeoff transformed the same 56 approximate
Ocean States into Oceanic Interrupted Mollweide and an Oblique Cylindrical
Equal Area strip. With identical white-land context, ocean-region tones, labels, and
boundary hierarchy, Oceanic Mollweide was the clear visual winner.

Its six equal-area ocean-emphasis lobes give the Pacific a broad central field,
make individual states feel like a coherent world geography, and turn the
projection interruptions into an intelligible part of the composition. It is
now the leading projection for the **Ocean States view**. PELAGOS retains its separate role
as the leading experimental view for heatmasses and continuous
ocean pathways; the two decisions answer different cartographic questions.

The Oblique Ocean Strip remains valuable as a relationship view centered on
the Drake Passage–Indonesian Throughflow great-circle axis, not as the primary
state atlas.

## 2026-08-29 — Regions, families, states

The 56-state discovery first exposed two overlapping classifications: five
oceans and four biome families. Their useful intersection produces eleven
ecological realms. A continuity audit then revealed that several realms were
multipart—including Polar and Pacific Coastal—so the atlas stopped calling
them regions. The working hierarchy is now **11 organizational realms → 22
contiguous schematic regions → 56 classic province identities**.

The hierarchy also preserves its two source axes. Pacific, Atlantic, Indian,
Southern, and Arctic are conventional ocean identities; Polar, Westerlies,
Trades, and Coastal are recurring ecological families. Their eleven realms
organize 22 named territories, which contain the 56 surface-ocean identities.
The 11- and 22-part layers are provisional OSW constructs. Region membership
is connected in the unmasked, pre-projection nearest-seed topology; land and
projection seams may divide the visible mark. The boundaries remain original
nearest-seed geometry with real coast-owned edges, not published Longhurst
geometry.

## 2026-08-29 — Ocean States of the World

After the 56-state surface geography and 36 overlapping feature systems became
the center of the work, **OCEANLINES** no longer described the project: lines
were only one kind of ocean object. The project was renamed **OSW — Ocean
States of the World**. In ordinary conversation it may be called **The Ocean
States**.

The new name preserves the project's central map idea: ocean states can be
learned like the states on a familiar political map, while waters, currents,
fronts, seafloor structures, living systems, and events cross and overlap
them. “States” remains a visual and organizational analogy, not a claim that
the approximate provinces are sovereign, fixed, exhaustive through depth, or
published Longhurst boundary geometry.

Active code, artifacts, metadata, and interface branding use `OSW` and the
`osw-` filename prefix. Dated reviews below retain the former project name when
describing work performed before the rename.

The reviewed `atlas-08-private-preview` branch was subsequently pushed at the
owner's request. It is publicly visible for review but has not replaced Atlas
07 on `main` or GitHub Pages and is not a promoted release.

## 2026-08-29 — The ocean becomes a place

### The breakthrough

OCEANLINES found a complete surface geography: the classic Longhurst system of
four biomes and 56 named biogeochemical provinces. This changed the project from
an atlas of selected heat reservoirs, currents, fronts, and events into a map on
which **every surface-ocean location can first have a province identity**.

The owner recognized this as a hallmark moment. The central analogy became:

> The 56 provinces can be learned like states, while heatmasses, currents,
> fronts, blooms, and events cross them like larger moving systems.

### What was built

- `38c9352` identified Longhurst-style provinces as the strongest available
  complete surface cover.
- `9df16e7` created the first Province Atlas: an original state-like cartogram,
  a 56-row reference directory, and an explicit 54/56 edition boundary.
- `9ea0281` approved the first cartogram as an additive private experiment.
- `495ec4b` replaced decorative land seams with horizontally compressed,
  checksum-pinned Natural Earth coastlines—real continental fingerprints that
  orient the viewer without returning visual control to land.
- `2327cec` made the inversion literal in a monochrome state-map study:
  continents became negative-space holes cut directly from the unified province
  field, while the earlier four-biome plate remained preserved.

### What the first map means

The province identities, codes, basin memberships, and biomes are scientific
reference facts. The equal-ish beveled province shapes are not geographic
Longhurst boundaries and do not encode real area, distance, direction, exact
adjacency, or exact coast contact. That separation is now a permanent project
contract: **identity can be simplified; geometry must declare its truth.**

### The visual promise

The mature Province Atlas should hold two complementary truths:

1. **Equal voice** — a varied, contiguous puzzle cartogram in which every
   province has room to be recognized and remembered.
2. **True footprint** — a licensed or independently reproducible geographic
   reference in which province size, shape, contact, and uncertainty can be
   inspected honestly.

The intended hook is a stable code and color system that can move between those
views. The static Longhurst reference is only the beginning: natural ecological
boundaries move seasonally and interannually.

## 2026-08-29 — The provinces become the atlas

### The second breakthrough

The first state-map experiments still treated coastlines as decoration or as a
single hole punched through unrelated tiles. The owner supplied the decisive
correction: **the coastline must belong to the province itself**. ALSK should
inherit a recognizable Alaska edge; HUMB should inherit Peru and Chile; BENG
should inherit southwest Africa.

`ef5f37a` rebuilt the 56 pieces from approximate geographic seeds over a
complete ocean field and subtracted checksum-pinned Natural Earth land from
them. The internal borders remain original schematic geometry, but every
coast-facing piece now owns the real coastline it reaches. Continents became
the lakes inside the ocean-state map.

`a72074d` then made that geometry the common Atlas 10 ground. All six conceptual
lenses and the SST, SST-anomaly, Argo-depth-anomaly, and estimated-error modes
can be read without leaving the 56-state system. Every province is selectable,
keyboard operable, URL-addressable, and zoomable; changing views preserves the
selected geographic frame.

`96c2b91` replaced the 36 numbered point markers with selectable geographic
shapes. Established OCEANLINES artwork supplies the first heatmasses, currents,
gates, and buried waters; mechanism-specific regions, loops, seams, and seafloor
paths complete the catalog. The shapes remain declared schematic indexes—not
observed boundaries—but the map can now show what kind of ocean object crosses
each province instead of reducing every object to the same dot.

The durable interaction principle is:

> Select a province as the place. Then change the view to ask what waters,
> flows, edges, life, events, or observations cross that place.

This is still a reference cartogram—not validated Longhurst boundary geometry
and not a mechanism, budget, or material wall.

## 2026-09-08 — The ocean states gain volume

The source-aligned 54-province footprint became a three-dimensional address
ledger. Each wet 0.25° GEBCO center now contributes spherical area multiplied
by the thickness of every OSW depth band present above its seabed. The result
estimates approximately 1.338 billion km³ of water: 5.14% epipelagic, 19.50%
mesopelagic, 62.84% bathypelagic, 12.41% abyssopelagic, and 0.11%
hadalpelagic. That total lies 0.0258% below the independent USGS
1.338-billion-km³ context estimate—an unusually clean scale check, not a
calibration or validation of individual province borders.

The workbench now lets a visitor flip one province profile between the share
of seafloor reaching each band and the share of actual sampled water volume in
each band. This is the fourth seminal step: the “states” are no longer only
surface pieces or bottom-depth summaries; they now have a declared, auditable
vertical extent without being misrepresented as water masses or ecological
columns.

The next cartographic pass makes that ledger comparative. The same Mollweide
frame can show ecological families, sampled wet-area rank, sampled water-volume
rank, or area-weighted mean-depth rank. Five deliberately coarse classes carry
the global pattern; a three-number passport gives the selected state's exact
rank and share. This separates a state's geometric capacity from its dynamical
importance and makes differences such as “large,” “voluminous,” and “deep”
visible rather than interchangeable.

The vertical-shape pass then gives every sourced state a literal hypsometric
fingerprint. Dominant seafloor area divides the 54 into 11 shelf-led, 19
deep-floor-led, and 24 abyssal-floor-led states. A separate ≥5% breadth count,
hadal-presence flag, and area-to-volume rank shift preserve the character that
one dominant label would otherwise erase. KURO is the sole current state with
at least 5% of sampled seafloor area in all five bands; 29 states contain at
least one sampled hadal center. The fingerprint completes a bathymetric
covering while explicitly declining to call it geomorphology or dynamics.

The depth selector then reaches the map. “Selected band” ranks state water
volume inside the active vertical address and leaves states with no sampled
reach in a separate gray class. The upper three bands span all 54 sourced
states, the abyssal band spans 50, and the hadal band spans 29; SPSG leads the
upper three by volume while NPSW leads the lower two. The passport distinguishes
the state's share of the global band from the band's share of the state. This
is the first visible realization of the full horizontal × vertical address,
rather than a vertical diagram sitting beside an unrelated world map.

The five-band water atlas then removes the need to remember those toggles.
Five Mollweide small multiples use one fixed scale for each state's share of
global sampled band volume, with absolute totals kept in panel subtitles. The
top-five share rises gradually from 36.02% epipelagic through 40.33% abyssal,
then jumps to 68.09% hadal. The plate makes a new relationship visible—the
deepest volume is far more geographically concentrated under this partition—
without relabeling volume concentration as heat, habitat, or circulation.

## 2026-09-08 — The ocean states become neighbors

This is the next seminal step: the source-backed provinces now form an
auditable relationship graph instead of merely tessellating a map. Exact
shared Version 4 polygon edges produce 54 nodes and 128 borders; ten point-only
contacts remain visible in a rejected log. The graph is deliberately not built
from neighboring colored pixels. A fresh provider acquisition reproduces every
one of the 1,036,800 committed 0.25° assignments, while the short `CNRY--MEDI`
edge proves why source topology and raster support must remain distinct.

The conceptual advance is larger than adjacency. A permeable province can be
a stable accounting unit without being a sealed physical container. Future
state accounts can distinguish inventory, cross-border flow, change, balance,
relationship, event shock, and revision—much as economic geography follows
regions through time—while preserving the different physical meanings and
their uncertainty.

The first six continuous depth silhouettes make the states more individual.
`NECS` is overwhelmingly shelf-like at this sampling, with a 66 m median
seabed, while even the shallowest tenth of `NPPF` lies below 4,261 m. A paired
0.5° center screen exposes where that character is stable and where coastal
sampling matters. These are bathymetric fingerprints, not water masses or
deep ecological borders.

The first transport pilot remains unselected. Its frozen rule chooses among
source edges by custody, native-grid geometry, compatible fields, controls,
testable numerics, and bounded scope—not by the most dramatic preliminary
result.

## 2026-09-08 — The states gain contents

The Ocean-State Exchange Observatory opens with a deliberately narrow first
inventory: potential-temperature distributions for six source-backed
Drake-sector provinces, four depth supports, and four monthly means in 2018.
Its 96 property passports preserve address, time, evidence class, source and
method lineage, distribution shape, support, and an explicit absence of an
uncertainty estimate. Another 128 records compare neighboring distributions
without promoting a descriptive contrast into a front or barrier.

The cartographic correction matters as much as the data. Only native cells in
the downloaded model window receive temperature or support color; the rest of
each global province stays quiet and out of domain. The map therefore shows
where the result exists rather than allowing a small regional sample to paint
an entire ocean state. Salinity, density, oxygen, and heat content remain
visibly unsupported. This is the first time OSW can ask what a state contains
while keeping stock, uncertainty, boundary identity, and flow rigorously
separate.

## 2026-09-08 — One border becomes a measured question

The frozen pilot rule considered every one of the 128 exact source edges and
selected `SANT--SSTC` without reading transport outcomes. Six candidate edges
had complete support in the regional ORAS5 substrate; `SANT--SSTC` won because
16 of its 18 native faces admitted exact one-cell displaced controls with the
same wet vertical masks, the strongest control fraction in the eligible set.
The famous Drake gateway did not replace a province edge, and the much larger
`ANTA--SANT` candidate did not win by visual or narrative importance.

The result demonstrates why the distinction matters. Gross opposing exchange
is far larger than the net in every sampled month. Net volume points from
`SSTC` to `SANT` in February, May, and August, then reverses in November;
different depth bands simultaneously run in opposing directions. The displaced
control has the same broad sign pattern. OSW has therefore earned a bounded
native-face transport method, not proof that the static source edge is a wall
or uniquely controls the flow. That honest negative evidence is exactly what
the exchange program was built to preserve.

## 2026-09-08 — The line fails its first persistence test

Stage 5 froze its temperature-front detector before looking for a favorable
alignment. The detector searched four native faces to either side of the
`SANT--SSTC` segment, required both absolute gradient strength and local
prominence, and allowed only a one-face match. It repeated the test at four
depths in four months and required seasonal, vertical, and control advantage
rather than accepting one striking surface panel.

None of the 16 cases matches the static line. The surface field does contain
detectable nearby gradients, but their peaks sit three or four faces away; most
deeper peaks miss the absolute floor. Surface-to-depth contrast direction
agreement reaches only 66.7%, below the frozen 75% requirement, and the static
line gains no advantage over its displaced control. The first physical
disposition is therefore deliberately narrow: this segment is not supported as
a persistent temperature front in the sampled 2018 model screen. The reference
edge remains useful, and interannual and other-property identities remain
unknown.

## 2026-09-08 — An event enters the state ledger

The existing 2026 North Atlantic marine-heatwave lineage now has explicit
province × surface addresses. Its primary exact-overlap footprint moves about
450 km across 21 days while remaining dominantly inside `GFST`. The daily
ledger preserves two tiny cross-state overlaps rather than rounding them away:
0.79% of the July 28 footprint falls in `NWCS`, and 0.05% of the August 3
footprint falls in `NAST W`.

The complete lineage family adds one graph transition. A July 29 side branch
moves from a `GFST` centroid into adjacent `NWCS`, but inherits only 13 pixels,
or 0.62% of its source component. That is enough for a geometric lineage and
state-address transition, not for a claim that water volume or heat crossed the
border. The primary trunk survives every tested area-pruning threshold; a
seven-day continuation remains in `GFST` through August 18 only under the
declared one-day-gap policy. For the first time, OSW can show motion, splitting,
and identity sensitivity through a state graph while leaving every unavailable
inventory and transport cell visibly empty.

## 2026-09-08 — The matrix chooses restraint

The full exchange program ends with 128 border records rather than a new
number of regions. Each row keeps geometry, depth character, hydrographic
content, exchange, stability, controls, event evidence, gate dependence,
uncertainty, decision rule, and falsification or upgrade criteria separate. No
weighted score can hide the missing columns.

The result is 127 `unknown` physical interpretations and one bounded `demote`.
That demotion applies only to the 16 tested native faces of `SANT--SSTC` as a
persistent physical-boundary candidate: its exchange resembles a displaced
control and its tested temperature gradients never stay on the source line.
The complete Longhurst edge remains in the reference map. No source geometry
is merged, split, moved, deleted, or silently replaced.

This is the program's deeper success. OSW now has an auditable grammar for
asking what a state contains, what crosses a border, whether a boundary
persists, and how an event moves through the graph. The grammar can absorb new
years, properties, products, observations, and revisions without pretending
that today's missing evidence is a discovery. Adoption, external scientific
review, and publication remain separate decisions.
