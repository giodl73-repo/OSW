# Ocean Motion: From Current to Heat Delivery

## Status

This is the OSW motion-study contract. It does not redraw or validate the
11-region, 22-region, or 56-province geography. Those covers remain frozen
while motion is studied independently.

## The key distinction

Ocean temperature is an inventory property. Velocity is motion. A particle
track is a possible pathway through a chosen velocity field. Heat transport is
temperature carried across a declared section through depth. Heat convergence
is the net transport into a declared volume and is the quantity most directly
related to local heat-content change after surface fluxes and mixing are
accounted for.

These are related, but they are not interchangeable.

| Level | Question answered | Minimum fields | Honest map label |
|---|---|---|---|
| 1. Speed | Where is surface water moving quickly? | surface `u`, `v` | surface current speed |
| 2. Direction | Which way is it moving now or on average? | surface `u`, `v` | surface velocity |
| 3. Pathway | Where would released parcels travel in this flow field? | time-varying `u`, `v`, solver choices | simulated parcel pathways |
| 4. Temperature advection | Is moving water locally warmer or colder than a declared reference? | collocated `u`, `v`, temperature, reference and depth support | temperature-advection proxy |
| 5. Section transport | How much heat crosses this gate? | 3-D velocity and temperature, section geometry, mass balance, thermodynamics | section heat transport |
| 6. Convergence | Where does transport add or remove heat? | closed-volume transports plus surface and mixing terms | heat-transport convergence |

## First three motion products

### M1 — Surface motion atlas

Use NASA PO.DAAC OSCAR v2.0 total surface-current components on the Oceanic
Mollweide view. Show direction and speed with a restrained vector/streamline
grammar over a neutral ocean field. The product represents a modeled,
satellite-informed average over an assumed well-mixed upper 30 m. It is not a
full-depth current measurement and must not be titled "heat flow."

Required controls:

- snapshot versus monthly or climatological mean;
- arrow/streamline density;
- speed legend in metres per second;
- land and missing-data masks;
- source date, collection, DOI, retrieval date, and checksum; and
- zoning hidden by default, available only as a comparison overlay.

The historical grammar pilot now has two matched views. The first shows one
5-day field. The second samples eleven 2018 fields and computes an OSW
directional-persistence ratio:

`magnitude(time-mean velocity) / time-mean(magnitude(velocity))`.

A value near one means the sampled vectors align; a value near zero means they
cancel directionally. This exposes where a single day resembles a persistent
surface corridor and where energetic motion reverses. The ratio is not
Lagrangian coherence, a natural border, or heat transport. Production still
requires OSCAR v2.0 and a stronger temporal sampling contract.

A third plate resolves the same historical meteorological year into DJF, MAM,
JJA, and SON using all 71 available five-day fields in the interval. It reveals
seasonal reversals and migrations that the sampled annual mean suppresses.
Because it covers only December 2017 through November 2018, it is a seasonal
case study—not a multiyear seasonal climatology.

The fourth plate derives two continuous cross-season diagnostics from those
four means. Cross-season alignment is the magnitude of the mean of four unit
direction vectors (`0` cancels; `1` aligns). Maximum seasonal turn is the
largest pairwise angle between seasonal mean directions (`0°` to `180°`). The
map labels thresholded candidate counts for orientation but keeps the
continuous fields visible. Neither diagnostic creates a region.

The fifth plate performs a deliberately preliminary audit of the frozen
22-region overlay. For every supported pair of neighboring coarse cells, it
compares the seasonal directions on both sides and estimates the fraction of
their mean vector normal to the flat nearest-seed border between the two
province seeds. Their product is a
`cut-through score`; region interiors are separately summarized by mean
neighbor-direction similarity. Only boundary pairs with at least three coarse
neighbor pairs enter the ranking. This can identify where better evidence is
most valuable, but that normal belongs to OSW's schematic geometry—not a
validated oceanographic boundary—and neighboring samples are not statistically
independent. One historical year cannot authorize a redraw. The M3 gate-budget
requirement below remains unchanged.

Each ranked border also reports the same score separately for DJF, MAM, JJA,
and SON. The seasonal floor, ceiling, and range are descriptive checks: a
stable high score is a stronger investigation target than a mean produced by
one exceptional season, but neither is a confidence interval or evidence of
interannual persistence.

A matched orientation plate prevents the cut-through score from becoming a
one-sided verdict. It computes an `along-border score` from the tangential
component and maps `cut-through − along-border` continuously. Negative values
lean along the schematic border; positive values lean across it. The declared
±0.10 screening bins are orientation aids, not natural classes. In this pilot,
most well-supported borders remain oblique or mixed rather than strongly
followed or crossed.

The next zoning-free experiment tests partition-count sensitivity rather than
starting from the 22 regions. Supported neighboring cells join when their mean
directional cosine similarity across DJF, MAM, JJA, and SON exceeds a swept
threshold. The count of connected components with at least five cells and the
fraction of cells retained in them are reported together. The historical pilot
shows no stable plateau: a momentary count near 20 coincides with extensive
small-fragment loss. Connected components therefore remain diagnostic objects,
not candidate ocean states.

A robustness pass then holds the data and threshold fixed while changing the
neighbor graph and omitting each season in turn. At threshold `0.30`, switching
from four-neighbor to eight-neighbor connectivity changes the sizable-component
count from 20 to 9, while leave-one-season-out four-neighbor counts remain
20–21. Graph topology dominates that apparent count. This falsifies any claim
that the pilot has discovered approximately twenty natural motion regions.

Finally, the 22-region passport matrix compares the frozen geography without
deriving a composite score. Each row reports seasonal alignment, internal
neighbor-direction similarity, maximum seasonal turning, screened weighted
border orientation, maximum screened cut-through, and support counts. This
separates contradictory evidence from missing evidence and creates a research
queue without issuing retain, merge, split, or move decisions.

The membership audit moves one level down. It computes an unweighted seasonal
mean-direction signature for every one of the 56 province identities, then
reports mean and worst all-pairs directional similarity among the members of
each frozen region. All 56 have at least one supported coarse cell in this
pilot. Broad all-pairs disagreement can identify a mixed container, but it does
not locate a new boundary or prove that nonadjacent members should be separated.

An adjacency correction therefore compares only province pairs that touch
across supported four-neighbor display cells. It aggregates seasonal direction
similarity at those sampled contacts and transfers the result to the owned
schematic province seam. This removes distant all-pairs exaggeration, but the
contact is still grid- and resolution-dependent rather than validated boundary
exchange.

The seasonal seam plate repeats the local adjacency test separately for DJF,
MAM, JJA, and SON. Of 32 sampled internal seams, 10 stay in one declared class
through all four seasons; all 10 stay aligned and none stays opposed. This is a
within-year time test, not interannual persistence, but it prevents a
seasonally reversing interface from becoming a permanent-looking split line.

### M2 — Parcel pathway laboratory

Release ensembles from named gates and thermal features into a declared,
time-varying velocity product. Use OceanParcels or an equivalent receipted
solver. Tracks may sample temperature, but a track remains a trajectory—not a
measure of transported heat.

The first M2 substrate is now packaged without trajectories:
`atlas/data/oscar-timeseries-2018.js` preserves the 71 five-day historical
OSCAR fields behind the M1 seasonal study on a fixed 25-by-54 grid. Its source
checksum exactly matches the seasonal artifact; a second checksum covers the
ordered, quantized frames. This proves temporal input continuity only. The
coarse display sampling, older product, surface depth, and land mask make it a
pathway-method pilot rather than production pathway evidence.

A regional pair covers Drake Passage, the Scotia Sea, and adjacent ACC waters
from 45–70°S and 80–40°W. The 38-by-61 coarsened field samples every second
native cell; the primary 76-by-121 field retains the archive's roughly
one-third-degree grid. Both carry the identical 71 timestamps. Neither
authorizes tracks until temporal/spatial interpolation, coastal termination,
time step, releases, and losses are declared and tested.

The first declared run releases 10 equal-count surface parcels across the wet
interior of a schematic Drake section on four dates. It integrates forward for 30 days with
fourth-order Runge–Kutta, a six-hour step, linear temporal interpolation,
strict four-wet-corner bilinear spatial interpolation, no diffusion, and
termination at the first invalid stencil or domain stage. Thirty-five of 40
tracks complete; the five losses are retained. The ensemble is deliberately
not area- or transport-weighted, so neither track density nor completion may
be read as exchange or heat delivery.

A time-step sensitivity pass repeats all releases at 3, 6, and 12 hours. All
three retain the same 35 completions and five losses; the largest completed
endpoint separation from the 3-hour reference is 1.40 km. Loss timing near the
strict mask varies by at most six hours. OSW therefore treats the
completed open-water paths as numerically stable at this scale while refusing
to interpret a termination timestamp as precise beaching or residence.

Spatial sensitivity is much larger. The native one-third-degree and coarsened
two-thirds-degree runs each total 35 completions, yet two release identities
switch status. The 34 commonly completed endpoints separate by a median 79.01
km and maximum 310.68 km. The aggregate count is therefore a false comfort:
path geometry from the coarsened field is not promoted.

Release-location sensitivity next shifts every central seed by −15, 0, and
+15 km in both along-section and across-section coordinates, producing 360
deterministic native-grid trials. Of those, 321 complete. Thirty-three of 40
neighborhoods complete all nine trials, five mix completed and terminated
tracks, and two lose all nine. Among central-complete neighborhoods, the
typical median endpoint displacement is 58.46 km; the largest individual
completed displacement is 507.63 km. This supports a broad pathway corridor,
not one privileged line, and the equal-count design is not a probability model.

Release-time sensitivity holds position fixed and starts each central seed at
−5, −2.5, 0, +2.5, and +5 days. Of 200 deterministic trials, 176 complete.
Thirty-four of 40 ten-day windows complete all five, two are mixed, and four
lose all five. Among central-complete windows, the typical median endpoint
displacement is 41.60 km and the largest completed displacement is 548.23 km.
Position and clock sensitivity therefore converge on a corridor-level claim
while rejecting an exact path as the stable scientific object.

The paired passport preserves both tests rather than averaging them. Every
seasonal release row contains eight of ten seeds classified full/full. Across
the 40 central releases, 32 are full/full, two are lost/lost, and six are mixed
or one-sided. This locates a stable corridor interior and fragile passage
margins under the declared method, but “full” remains completion support—not a
probability, impermeable boundary, exchange rate, or heat-delivery estimate.

Every result must declare release time and depth, integration direction and
duration, velocity product, interpolation, time step, coastal behavior,
diffusion model, random seed, and losses. Sensitivity ensembles are preferable
to a single authoritative-looking line.

### M2 — Paired Atlantic–Arctic entrances

The Arctic question begins with two routes, not one. OSW packages matching
native-resolution historical OSCAR fields around Fram Strait and the Barents
Sea Opening: 71 five-day fields from December 2017 through November 2018 at
nominal 15 m. OSCAR stops at 80°N, so the Fram domain ends there without
extrapolation.

A whole-strait Fram surface average is southward (−0.023 m/s), which would be
misleading if labeled “Atlantic inflow.” Splitting the same zonal screen into
traffic lanes resolves the apparent contradiction: the western lane averages
−0.067 m/s southward, the central lane −0.005 m/s, and the eastern lane
+0.022 m/s northward. The eastern inflow is strongest in DJF and SON and almost
vanishes in this JJA sample. At the Barents Sea Opening, the declared
meridional screen averages +0.022 m/s eastward, positive in every season.

These are unweighted surface-velocity screens, not transports. They do not
identify Atlantic Water, include depth, multiply by section area, carry
temperature, or establish heat delivered to the Arctic. Their purpose is to
fix the next M3 geometry: preserve the opposing Fram branches and treat the
Barents route separately before calculating full-depth volume and heat.

The receipted M3 intake contract requests February, May, August, and November
2018 from native ORAS5 member `opa0`: T-cell potential temperature and salinity,
U-face native i velocity, and V-face native j velocity. The broad domains are
Fram 20°W–20°E, 72–82°N and Barents 15–45°E, 68–80°N; exact native indices must
still be discovered from the curvilinear coordinates. Salinity is mandatory so
warm cells are not automatically renamed Atlantic Water. Both complete signed
sections must be reported before any temperature–salinity subset.

The public native mesh changes the two gateways differently. A single
surface-land-bounded ORCA025 V row spans Fram Strait in 60 faces, so that gate
can advance to full-depth mask and partial-cell checks. A single Barents U
column cannot represent the declared 20°E line: the best-mean candidate drifts
from 15.40°E to 25.88°E between 70.5°N and 75°N, and wet cells continue beyond
both clipped endpoints. Worse, the approximate Bear Island target falls on a
wet T cell at this resolution; the nearest dry T cell is over 200 km away. The
candidate is rejected. OSW must now choose between a virtual-endpoint mixed U/V
Fugløya–Bear proxy for observational comparison and a separate land-bounded
Norway–Svalbard gate for model closure. Those are different measurements.

The next bakeoff constructs both on the same C-grid graph. The Fugløya–Bear
proxy is a 43-face chain (23 U + 20 V) between virtual wet anchors. The broader
Norway–Svalbard closure is a 73-face chain (36 U + 37 V) between modeled coasts;
its northern endpoint lies about 243 km from the approximate Bear target. Both
have connected F-corner chains, unique faces, degree-two internal nodes, and no
corner duplication. Those tests establish usable geometry, not equivalence.

A 54-case construction challenge then varies nine endpoint intents and three
line-departure penalties for each meaning. The 10, 20, and 40 km penalties
select the same path within every endpoint case. Endpoint intent does not: the
proxy produces nine paths of 39–49 faces, including a plausible placement with
no faces shared with baseline; the closure produces six paths of 73–74 faces
and replaces up to 81% of baseline membership. OSW therefore promotes endpoint
placement—not path-cost scale—to a required sensitivity. This is method
sensitivity, not ocean or transport uncertainty.

The full-depth audit next reconstructs interior face thickness from native
`e3t_0`, `mbathy`, and `e3t_ps`, taking the minimum of adjacent T-cell
thicknesses at each U/V face. All three sections return zero mask mismatches,
finite positive wet areas, and exact depth-bin area closure. Fram spans
814 km² and reaches 2,577 m, with 60% of area below 700 m. The 161 km²
Fugløya–Bear proxy and 224 km² Norway–Svalbard closure reach only 444 m and
432 m respectively. They are shelf gates; Fram is a deep gateway. Area limits
what velocity can carry but is not itself transport.

The February 2018 native-state pilot now supplies that velocity together with
potential temperature and salinity. Fram resolves +6.21 Sv northward against
−6.66 Sv southward, leaving a −0.45 Sv whole-section net; its small residual
must not hide the two large branches. The Fugløya–Bear proxy carries +3.23 Sv
net into the Barents Sea, while the broader Norway–Svalbard closure carries
+3.64 Sv. Their 0.41 Sv difference is a section-domain effect, not an error
bar. At a 0°C reference the corresponding advective heat signals are +52,
+73, and +81 TW, but these are gateway transports—not heat convergence or
Arctic delivery. Four adjacent-cell tracer-collocation rules shift heat by at
most 1.71% and leave volume invariant. Literature comparison classes use both
temperature and salinity and remain subordinate to the full signed sections.

The complete four-snapshot comparison preserves the signs in February, May,
August, and November. Fram exports −0.45 to −2.05 Sv net, yet its 0°C-reference
advective heat remains +24 to +64 TW because the northward branch is warmer
than the larger southward branch. The Barents proxy imports +2.77 to +3.80 Sv
and +61 to +102 TW; the model closure imports +3.10 to +4.03 Sv and +71 to
+110 TW. The broader closure exceeds the proxy in every month, although the
gap changes from 0.23 to 0.49 Sv. These are four seasonal snapshots—not a
time-weighted annual mean.

### M4 — Nordic Seas heat-transformation room

The Arctic gateway results motivate a closed accounting domain rather than
another open-section comparison. OSW now defines the Nordic Seas as a proposed
control volume bounded to the north by the accepted Fram section and to the
east by the accepted land-bounded Norway–Svalbard model closure. The southern
boundary began as three Greenland–Scotland Ridge intents, but native topology
rejected that representation. The accepted surface cut instead uses Denmark
Strait, one continuous Iceland–Scotland Ridge section, and an explicit northern
North Sea closure. The latter is required because Britain does not join
continental Europe. The Fugløya–Bear observational proxy stays outside this
closure because virtual endpoints do not form a coast-to-coast boundary.

The frozen accounting convention is
`storage tendency + outward advective heat − downward surface heat =
unresolved remainder`. Ice exchange, mixing, diffusion, assimilation, and
numerical or geometric error remain named parts of that remainder until native
terms can be obtained. Volume closure must pass before reference-relative heat
convergence is interpreted, and heat must be reported at −1.9, 0, 2, and 5°C
reference temperatures.

The [contract plate](figures/osw-m4-nordic-seas-budget-contract.svg) now records
five passes and three open requirements. An expanded native mesh and five
sections enclose 12,550 wet surface T cells behind 284 unique faces; every face
separates inside from outside and the component touches no mesh edge. All five
sections also pass the internal full-depth mask, width, partial-step, wet-area,
and depth-bin checks. Fram supplies 814 of 1,816 km² of total boundary area and
is the only gate whose majority area lies below 700 m. All twelve monthly
T/S/U/V states, `e1t`/`e2t` plus surface heat flux, and native
ice/mixing/diffusive/assimilation terms remain open. Native T-cell metrics and
twelve monthly surface-flux fields now cover the exact interior, advancing the
ledger to six pass / two open. Their 2018 time-weighted result is −39.4 W/m²,
−106.8 TW, and −3.37 ZJ net downward, with four warming and eight cooling
months. This is one surface term—not advective convergence, storage,
transformation, or Arctic delivery.

Twelve compact native monthly states now cover every interior T cell, both
tracer neighbors of every boundary face, and every required U/V velocity. At
0°C reference their time-weighted advective convergence is +96.8 TW while the
surface term is −106.8 TW. Monthly storage tendencies follow the seasonal
cycle. Whole-room imbalance remains −0.064 to +0.074 Sv, and all four reference
temperatures remain reported. The +37.7 TW diagnostic mean remainder retains
ice, mixing, diffusion, assimilation, numerical terms, and offline-method
error; it is not interpreted as a process. The ledger is seven pass / one open.

Archived ORAS5 `sohtcbtm` provides an independent storage test on the same
12,550-cell room. Its monthly tendency follows the reconstructed 75-level
temperature storage at *r* = 0.99998 with 1.45 TW RMSE; substituting it changes
the time-weighted remainder from +37.7 to +37.9 TW. Storage reconstruction is
therefore not a plausible explanation for the missing magnitude. The live ICDC
ORCA025 catalog exposes 23 variable families, but none is a native temperature
tendency, tracer-advection tendency, mixing/diffusion tendency, ice–ocean heat
exchange, or assimilation increment. Closure remains open at the archive
boundary rather than being filled with inferred physics.

The same-room seasonal context then tests—not assumes—an ice or mixed-layer
explanation. Across the twelve 2018 monthly means, the remainder correlates
+0.05 with area-mean ice concentration, −0.01 with an ice-volume proxy, and
+0.33 with area-mean mixed-layer depth. Its alternating signs and spikes do not
track either smooth seasonal state curve. These contemporaneous one-year
correlations are seasonally confounded and cannot show that ice or mixing are
unimportant; they only fail to support those state variables as simple proxies
for the unresolved budget term.

Four tracer-to-face rules then isolate the boundary-flux numerical choice.
Inside- and outside-cell rules shift annual advective convergence only +2.25
and −2.25 TW from the adjacent-mean baseline. A monthly-mean upwind donor rule
shifts it +43.0 TW, yielding 139.8 TW convergence and a −5.3 TW mean remainder.
The shift is concentrated at Iceland–Scotland (+33.9 TW) and Denmark Strait
(+10.6 TW), not at the northern exits. This does not select upwind as truth:
monthly remainders still span −85 to +110 TW, and separate monthly means cannot
reproduce the model's time-stepped nonlinear flux-corrected tracer transport or
submonthly velocity–temperature covariance.

Directional branch anatomy shows what the upwind endpoint is detecting.
Denmark's 3.46 Sv inward branch carries 4.67°C water while its 5.07 Sv outward
branch carries 1.41°C water, yielding heat convergence despite net volume
export. Iceland–Scotland pairs 22.62 Sv inward at 6.22°C with 19.23 Sv outward
at 4.48°C. Fram pairs 5.94 Sv inward near 0°C with 4.43 Sv outward at 1.94°C,
therefore importing net water while exporting heat. Net flow direction alone
cannot determine heat direction; opposing volume and temperature populations
must be retained separately.

Reference-depth binning places that exchange vertically. Summed across all
five gates, the upwind endpoint converges +148.8 TW above 700 m and diverges
9.0 TW below it. Iceland–Scotland adds +80, +78, and +72 TW in the 0–100,
100–300, and 300–700 m bins. Norway–Svalbard removes 46 and 37 TW above 300 m;
Fram removes approximately 10–12 TW in each upper-700-m bin but little through
its much larger deep area. Gate depth controls capacity, not the depth at which
heat transport must actually occur.

Native-face projection then reveals the horizontal concentration hidden inside
each gate total. Across 284 faces, 115 converge heat and 169 diverge it. Gross
absolute face contributions total 1,067 TW, but 87% cancels between opposing
jets, leaving +140 TW. Twenty faces carry 52% of the gross exchange; the
strongest +66.4 TW import and −30.3 TW export faces both lie on the
Iceland–Scotland path. Face totals combine width, depth, velocity, and donor
temperature and therefore must not be read as local heat-flux density.

Dividing each face by reconstructed wet cross-sectional area separates total
transport from intensity. The top-20 lists overlap on 12 faces, so width and
depth materially affect some hotspot ranks. Yet the strongest import near
13.0°W, 64.0°N remains first in both views at +66.4 TW and +7.66 MW/m². This
supports a resolved intense Atlantic-side jet rather than an artifact of one
large face, while cross-sectional MW/m² remains distinct from air–sea W/m².

The same receipt now factors every face's net heat exactly into wet area, gross
exchange speed, signed thermal transport factor, and ρCp. P90/P10 spreads are
12.8× for area, 8.1× for speed, and 22.7× for the absolute signed factor. The
leading Atlantic import combines 8.66 km², 0.249 m/s, and +7.49°C rather than
depending on one oversized face. The last quantity is an accounting factor—net
heat divided by gross exchange—not a measured water-mass temperature.

Monthly reranking tests whether that structure is an annual-mean artifact. The
same Iceland-side face remains positive and absolute rank #1 in all twelve 2018
monthly means. All annual top-20 faces retain their sign, while 14–19 appear in
each monthly top 20 (mean 16.7). In contrast, only 88 of all 284 faces preserve
one nonzero sign all year. The dominant jets are seasonally persistent within
this member/year, but that does not establish interannual persistence.

Maximal adjacent same-sign sequences translate the face field into 95 candidate
jet runs. A compact four-face Iceland-side core carries +106.5 TW across about
33 km, while a broad 33-face Norway–Svalbard band carries −72.0 TW across about
326 km. Both, and all ten strongest runs, preserve their sign in every monthly
mean; those ten account for 50% of gross exchange. Fifty-one single-face runs
warn that sign segmentation also preserves noise and local interleaving, so the
runs are descriptive connected components rather than objective current names.

Centered 1-, 3-, 5-, and 7-face sign sums challenge that fragmentation. Three
faces reduce 95 runs to 53 and 51 singletons to 13 while preserving the compact
+106.4 TW Atlantic leader. At five faces, a broader 32-face Scotland-side band
becomes the strongest import at +144.3 TW; the original core remains a nested
feature rather than disappearing. These are scales in a jet hierarchy, not
competing estimates from which one uniquely correct current count can be chosen.

Distance-radius calibration removes the strongest grid-index objection.
Cumulative face-center radii of 20, 30, and 50 km agree with paired 3-, 5-, and
7-face signs on 277, 278, and 266 of 284 faces. Thus the nested jet result is
robust at approximately 20–30 km, while the decline to 93.7% agreement at
50 km records increasing sensitivity to nonuniform spacing and section curves.

A monthly relay screen reconnects the resolved gate structure to surface forcing
and storage. Southern-gate input and northern-gate export have same-month
*r* = 0.81, stronger than any of eleven circular shifts. Surface forcing and
storage have *r* = 0.98. The annual upwind-consistent terms are +260.4 TW south,
−120.4 TW north, −107.6 TW surface, +26.5 TW storage, and −5.8 TW unresolved.
Seasonal covariance is not parcel transit: these twelve months cannot determine
travel time, residence time, or causality.

A nearby-screen bakeoff prevents that intake from inheriting one arbitrary M2
line. Thirty eastern-Fram cases vary screen latitude and the longitude where
the inflow lane begins: 20 are northward, while all cases at 79.0–79.33°N are
southward. In contrast, all 18 western-Fram cases remain southward and all 11
Barents screens from 20–30°E remain eastward. Direction support is descriptive,
not probability or uncertainty. The result makes Fram section placement a
blocking M3 sensitivity rather than silently selecting 78.67°N.

A deterministic pathway experiment asks whether those screen signs extend
into recognizable surface corridors. At four seasonal release times it follows
32 equal-count seeds in western Fram for 20 days, 40 in eastern Fram for 20
days, and 40 at the Barents entrance for 30 days. All 26 completed western
Fram tracks move southward. Eastern Fram remains mixed: 14 of 27 completed
tracks move northward and 13 do not. Barents is predominantly eastward in 27
of 30 completed tracks. The remaining 6, 13, and 10 tracks terminate when the
strict four-wet-corner stencil or regional domain fails.

The result strengthens a corridor-level export claim in western Fram, but it
does not turn particle counts into transported volume or probability. The
eastern inflow remains seasonally and spatially conditional, and every path is
a nominal-15-m kinematic experiment with no diffusion, depth, salinity,
temperature, or heat.

### M2 — Indonesian Throughflow gate readiness

The Indonesian Throughflow is a branching inter-ocean system, not one line.
The INSTANT observational design separates the principal Makassar and
Lifamatola inflows from the Lombok, Ombai, and Timor outflows. OSW therefore
tests those five named passages independently before attempting paths or a
summed transport.

The first audit packages the same 71 historical OSCAR fields on a native
one-third-degree regional grid and asks a deliberately prior question: does a
candidate grid-aligned surface screen have enough finite samples to represent
the strait? The declared rule requires at least three finite points in every
frame for an M2 screen. Lombok has one of four and Ombai two of four, making
both explicitly underresolved. Makassar has five of eight and Lifamatola five
of five, but their annual nominal-15-m signs oppose the declared southward
route. Timor has nine of nine and the declared westward sign.

These results audit the substrate, not the geography. The provisional
axis-aligned lines are not the INSTANT mooring sections, and a contrary surface
sign does not falsify a full-depth throughflow. Instead, it warns that a
nominal-15-m velocity field cannot stand in for sill-controlled, vertically
structured, tidally mixed transport. No Indonesian pathway or heat claim
advances from this screen; the next data choice must resolve all required
passages and temperature–salinity structure.

The first M3 data bakeoff therefore moves from 1/3° OSCAR to the public 1/12°
HYCOM GLBa0.08 experiment 91.2 archive. A compact 16 November 2018 sample keeps
all five candidate sections, 33 standard z levels, temperature, salinity, and
both horizontal velocity components. Surface wet support rises to 20/32 at
Makassar, 14/16 at Lifamatola, 7/17 at Lombok, 10/15 at Ombai, and 38/38 at
Timor. Every candidate now clears the declared three-point geometry threshold.

The vertical profiles are already more informative than the surface map:
Lombok's resolved standard levels end near 900 m, while Ombai reaches 2,500 m;
Lifamatola's snapshot surface sign opposes its declared deep-inflow role before
turning at depth. But this is still a single daily field on a collocated
standard grid. Section angle, connected wet columns, thickness, face geometry,
and temporal sensitivity must pass before an area-weighted volume calculation,
and temperature–salinity branch accounting must precede heat.

### M2 — Agulhas junction anatomy

The Agulhas system is not one continuous arrow from the Indian Ocean into the
Atlantic. The western-boundary current runs south along Africa, an energetic
retroflection turns much of that motion east into the Agulhas Return Current,
and intermittent rings, cyclones, and direct-flow fragments leak west into the
Cape Basin. OSW therefore treats **current → turn → return** as the primary
geometry and leakage as a variable branch field.

The first audit stitches two matching native OSCAR longitude windows across the
archive's 20°E storage seam without interpolation. Four declared diagnostic
windows then retain every jointly finite u/v sample from 71 historical fields.
The coastal sector has 0.40 m/s mean sample speed and 61% southward samples;
the return-current sector has 0.31 m/s mean speed and 74% eastward samples.
The retroflection is faster at 0.50 m/s yet has only 8% net vector coherence,
which is evidence of changing directions inside an energetic turning field—not
weak motion. Cape Basin coherence is 11%.

Seven declared seeds released at four seasonal dates produce 28 complete
45-day deterministic tracks. Their divergence is a feature of the result: a
mean arrow would erase the mechanism. The windows are diagnostic sectors, not
new borders, and the equal-count nominal-15-m paths are not probabilities,
water-mass identities, volume transports, heat transports, or climatology.
Full-depth leakage and heat require native section geometry, temperature,
salinity, eddy treatment, and an explicit Atlantic-bound transport definition.

The source-tagged challenge expands four upstream centers into deterministic
3×3 release neighborhoods at three dates. Of 108 paths followed for 150 days,
the baseline 15°E Cape Basin and 35°E return thresholds classify 14 as Cape,
24 as return, 62 as unresolved, and eight as terminated. Moving the west gate
among 12/15/18°E and the east gate among 33/35/37°E produces Cape counts from
2–20 and return counts from 23–54; four paths meet both thresholds under some
definitions and remain explicitly double-marked.

That spread is the result, not noise to suppress. Equal particle counts cannot
be reported as leakage percentages, and threshold sensitivity cannot be fixed
by selecting the most visually satisfying gate. M3 must replace these surface
fates with native full-depth source transport and a literature-compatible
Atlantic leakage definition.

The M3 experiment contract now follows that literature-compatible design. It
requires transport-weighted releases over the current's full width and depth at
32°S every five days for one release year, followed in three dimensions for
four years. Every crossing of the exact published GoodHope polyline must retain
time and direction. At-least-one crossing measures exchange and thermohaline
transformation; an odd number of crossings identifies water that remains in the
South Atlantic for an overturning-retention question.

This distinction is not cosmetic. Published experiments find transit times
from less than a month to several years, with a modal interval near 160–170
days and more than half of transport arriving only within roughly 280–300 days.
They also show that moving the release section from 32°S to ACT near 34°S and
changing the crossing-parity rule alter the mean estimate. OSW therefore pins
both as required sensitivities. The archived reference geometry is now pinned;
the contract remains blocked on an eddy-rich, continuous five-year 3-D
T/S/velocity substrate and target-grid mapping.

The authors' GEOMAR archive resolves the reference-geometry half of that block.
Its CC BY 4.0 section file contains the exact 63-coordinate experiment boundary:
the 32°S release, east/south domain exits, and a composite leakage exit with a
53-coordinate diagonal `West` leg joined to a two-coordinate `Northwest` leg.
The raw INALT20 velocity is not archived, but compact derived section transport
and example-trajectory files are.

OSW's attributed recalculation sums `West + Northwest` for each of 57 release
years. It reproduces a 1958–2014 mean of 9.894 Sv, a population standard
deviation of 2.082 Sv, and a +0.464 Sv/decade ordinary linear fit. The archived
`East` return-current exit averages 40.015 Sv. These are published model-output
results, not a new OSW run or observation-only estimate. Their successful
replication validates the bent-gate grammar while leaving a new experiment
blocked on raw eddy-rich 3-D velocity and target-grid mapping.

### M3 — Heat-delivery pilot

Use a three-dimensional state estimate such as ORAS5 for a small set of
physically meaningful gates before attempting a global field. Candidate pilots
are Drake Passage/ACC cross-front exchange, Atlantic inflow to the Arctic, the
Indonesian Throughflow, and the Agulhas leakage corridor.

For each gate, calculate volume transport and heat transport together. Declare
the section normal, wet cells, vertical limits, temperature convention,
reference treatment, density and heat capacity treatment, eddy/diffusive terms,
and closure residual. ORAS5 is an assimilative reanalysis with known regional
biases; it is not observation-only truth.

The first M3 implementation separates three contracts. The dry-run ORAS5
manifest requests operational all-level potential temperature and native zonal
and meridional velocity for February, May, August, and November 2018. A strict
NetCDF readiness audit then requires native U/V coordinates, horizontal face
widths, vertical thicknesses, and wet masks before any section is extracted.
It never substitutes nominal 0.25-degree area or rotated cell-centred velocity
for explicit face geometry. Finally, the section kernel calculates signed
volume and reference-relative advective heat transport from an already
extracted face array.

The kernel passes a balanced synthetic verification: +0.02 and -0.02 Sv give
zero net volume and 0.00016399136 PW net heat transport independent of the
chosen reference temperature. That is a calculation test, not an ORAS5 or
Drake estimate. A single open section also cannot report mass closure; closure
requires all control-volume boundaries and storage tendency.

A metadata-only audit of the public University of Hamburg ICDC ORCA025
`mesh_mask.nc` finds the expected U/V masks, coordinates, and horizontal
metrics (`e2u` and `e1v`). It does not find explicit native-face `e3u` or `e3v`
layer thicknesses. T-point reference and partial-bottom fields are not silently
converted into U/V thicknesses; that reconstruction must be sourced and tested
against the precise NEMO/ORAS5 configuration first.

CDFTOOLS 3.0 supplies one candidate reconstruction: assemble T-cell thickness
from the reference profile and partial bottom cell, then take the minimum of
adjacent T thicknesses at each U or V face. OSW records that algorithm for a
future falsification test but does not accept it yet: it is third-party source,
not an explicit ORAS5 face field, and the implementation itself cautions about
its terminal-edge handling.

The first OSW reconstruction experiment improves that candidate by emitting
only genuine interior faces: an `L×J×I` T-cell subset yields
`L×J×(I−1)` U faces and `L×(J−1)×I` V faces. No last row or column is copied.
A synthetic partial-bottom fixture verifies dry columns, reference-thickness
fallback, adjacent minima, and face-column depth bounds. This removes the known
terminal-edge shortcut but does not validate ORAS5 equivalence.

The live native-mesh test now advances that status. OSW downloaded only a
checksummed 75×200×176 Drake subset from the public ICDC OPeNDAP service. Across
1,734,557 wet interior U faces and 1,739,887 wet interior V faces, the
reconstruction has zero mask disagreements. Maximum face-column depth residual
is 7.11×10⁻¹⁵ m, and every wet face area is finite and positive. This is a
native geometry-consistency pass, though not an independent face-field
comparison.

The same archive supplies native February 2018 `votemper`, `vozocrtx`, and
`vomecrty`. A deterministic land-mask rule selects 87 U faces at 67.125°W from
66.21°S to 55.92°S, with positive normal eastward. Temperature is collocated by
a declared arithmetic mean of adjacent T points. The first full-depth result is
221.43 Sv eastward minus 97.14 Sv westward = **124.29 Sv net eastward**. That
falls near older canonical Drake estimates but is one monthly reanalysis member
and not a mean observational transport.

Reference-relative heat transport is 2.32 PW at −1.9°C, 1.35 PW at 0°C, and
−1.20 PW at 5°C. The exact reference-change identity closes within sub-watt
floating-point roundoff across the four samples. These are
all descriptions of the same open-section calculation, not competing physical
answers; none provides mass closure or heat convergence.

Running the identical contract in May, August, and November produces net
eastward transports of 122.56, 122.12, and 127.77 Sv beside February's 124.29
Sv. The four-sample mean is 124.18 Sv and range is 5.64 Sv. Yet the eastward
branch spans 12.92 Sv and the westward branch 12.48 Sv: cancellation makes the
net look more stable than its components. At 0°C reference, sampled net heat
ranges from 1.25 to 1.35 PW. Four months are a seasonal probe, not an annual
mean or climatology.

The next falsification test moves the land-bounded native U-face section across
five nearby columns from 69.125°W to 65.125°W. Their four-sample volume means
range from 124.167 to 124.279 Sv: only 0.111 Sv across the tested gates. The
sample-to-sample range at each gate remains about 5.64–5.71 Sv. This supports a
stable net-volume corridor within the tested band; it does not prove a unique
section or observational accuracy.

Temperature staggering is a different sensitivity dimension. At the fixed
67.125°W gate, arithmetic-mean, west-point, east-point, and upwind T-to-U
collocations leave volume exactly unchanged but give four-sample mean heat
transports of 1.300, 1.344, 1.256, and 1.350 PW at a 0°C reference. The
approximately ±0.05 PW method spread is kept visible. None of these offline
choices reproduces the model's native tracer-advection operator.

Layer-resolved branches show why a full-depth gate matters. Four-sample net
volume contributions are 24.05, 40.28, 31.16, 26.32, and 2.38 Sv in the
declared 0–200, 200–700, 700–1500, 1500–3000, and >3000 m strata. At a 0°C
reference their net heat contributions are 0.364, 0.494, 0.287, 0.149, and
0.005 PW. Roughly 48.2% of net volume lies below 700 m while 65.9% of the heat
signal lies above it. Midpoint depth bins are descriptive—not water-mass,
neutral-density, or overturning classes.

A temperature-class partition asks a different question of the same cells.
The <0, 0–1, 1–2, 2–3, 3–5, and >5°C classes conserve both volume and
0°C-reference heat to roundoff. Fully 86.9% of the westward branch is at or
below 2°C; the 1–3°C classes carry 86.50 Sv, or 69.7% of net volume. This
supports a colder return-flow description, but temperature alone cannot name
a water mass without salinity, density structure, source history, and mixing.

The latitude–depth portrait restores the location hidden by those summaries.
Across 4,662 wet native cells, four-sample mean potential temperature spans
−1.16 to 7.46°C and normal velocity spans −0.277 to +0.982 m/s. The slice shows
a cold Antarctic-side shelf, deep cold basin, warmer northern wedge, broad
eastward motion, and embedded westward lanes. Because east–west motion is
normal to this north–south section, dots mean eastward out of the page and
crosses mean westward into it; left/right arrows would be geographically false.

The matched contribution map changes the color question from “what temperature
is here?” to “what does this native face cell add to the signed total?” Its
volume cells sum to 124.185 Sv and its 0°C-reference heat cells to 1.300 PW.
Alternating eastward and westward lanes appear in both panels, while cold
southern and deep contributions weaken in the temperature-weighted heat view.
The brightest 10% of native cells carry 54.9% of absolute volume and 59.5% of
absolute heat contribution, but that concentration is grid-resolution dependent.

### M4 — First control volume

A single section cannot evaluate mass closure or heat convergence. The first M4
pilot therefore surrounds a small grid-aligned Drake box with four native
boundaries: U faces at 69.125°W and 65.125°W, and V faces near 66.16°S and
55.85°S. Every term uses reconstructed partial-cell thickness, native face
width, native normal velocity, and arithmetic adjacent-T collocation. Positive
sign means outward from the box.

Across February, May, August, and November, the mean volume terms are −124.87
Sv west, +58.00 Sv east, +66.11 Sv north, and +0.77 Sv south. Their mean net is
only +0.007 Sv outward, with a 0.005–0.009 Sv monthly range. Within this box,
most western inflow therefore leaves east or north; the southern advective
volume boundary is small. This is a box result, not a general claim that heat
cannot reach Antarctica by other longitudes, depths, eddies, mixing, or time
periods.

Net outward advective heat at a 0°C reference is 0.020, 0.037, 0.104, and 0.058
PW in the four sampled months, averaging 0.055 PW. Once volume nearly closes,
changing reference temperature from −1.9 to 5°C changes the four-sample mean by
only 0.000203 PW. This demonstrates why a closed mass budget makes heat
convergence far less reference-dependent than one open gate.

The remaining heat flux is not yet heat accumulation. A complete tendency
budget must add matched heat-content storage, surface and freshwater forcing,
diffusion/mixing, sea-ice terms where applicable, and the model's native tracer
advection. The first M4 stages diagnose advective boundary divergence and
storage before testing one surface term below.

Nested-box sensitivity then changes one geometric dimension at a time. Four
eastward extents produce four-sample mean heat divergences from 0.021 to 0.055
PW, a 0.0336 PW range. Four northward extents produce 0.003, 0.001, 0.032, and
0.055 PW, a 0.0535 PW range. Every tested box retains a worst monthly volume
imbalance below 0.010 Sv. Thus volume closure is robust in this family while
advective heat divergence is strongly geometry-dependent.

The first storage probe adds native T-cell area (`e1t × e2t`) to reconstructed
partial thickness for 75,782 wet cells in the primary box. Volume-weighted mean
temperature moves from 1.362°C in February to 1.319°C in May, 1.240°C in
August, and 1.248°C in November. The corresponding sparse heat-content
tendencies are −0.0157, −0.0279, and +0.0031 PW. Storage tendency is
reference-invariant because the box volume is fixed.

Endpoint-average outward advective divergences over those intervals are 0.0286,
0.0705, and 0.0808 PW. Adding storage and outward advection leaves 0.0129,
0.0425, and 0.0839 PW unclosed. These are not inferred heat sources: monthly
endpoint differencing is not a time-integrated tendency, and surface forcing,
mixing, diffusion, ice terms, and native tracer advection are absent.

The compact budget-state contract then narrows every monthly retrieval to the
T cells surrounding the box and the exact U/V boundary windows. Twelve files
total roughly 9.7 MB and reproduce February, May, August, and November volume,
heat, and box temperature exactly. Eleven adjacent-month intervals replace the
three seasonal jumps.

Across 15 January–15 December, time-weighted mean storage tendency is −0.0061
PW and endpoint-trapezoidal outward advection is +0.0683 PW, leaving +0.0622 PW
unclosed. Individual remainders range from 0.0306 to 0.0933 PW and remain
positive in all eleven intervals. Denser temporal sampling therefore does not
identify the missing processes; it strengthens the requirement for matched
surface, ice, mixing, diffusion, and native tracer-budget terms.

The native ORCA025 archive then supplies `sohefldo`, net downward surface heat
flux, over the exact same 86×16 T-cell footprint. Endpoint-trapezoidal surface
input averages +0.0195 PW across the 334-day span. Under the declared sign
convention,

`storage + outward advection − downward surface input = remaining`.

The surface term explains 31% of the prior +0.0622 PW mean remainder and leaves
+0.0427 PW. Every interval remains positive after it is included. This is a
useful partial attribution—not closure. `sohefldo` is an ORAS5 model/reanalysis
field with surface-restoring context, not a direct flux observation; monthly
means and endpoint trapezoids are not the model's integrated tracer budget.
Ice-ocean exchange, mixing, diffusion, freshwater/reference effects,
assimilation increments, and native tracer advection remain unresolved.

## Why convergence comes before new zones

A velocity arrow can cross a proposed boundary without carrying unusual heat.
A warm current can cross a boundary yet be balanced by a colder return flow at
depth. Conversely, eddies and mixing can move heat across a strong mean-current
front. Therefore the future zoning test should ask whether candidate boundaries
organize repeatable transport convergence, exchange barriers, or coherent
pathways—not merely whether arrows visually follow them.

The zoning work resumes only after at least one reproducible M1 surface-motion
view and one mass-checked M3 gate calculation exist. M2 is illuminating but is
not a substitute for the M3 budget.

## Tests for the future zoning pass

The motion evidence will not automatically generate one uniquely correct
partition. It will let OSW compare candidate boundaries with declared tests:

| Test | Diagnostic | What would count against a boundary |
|---|---|---|
| Persistence | seasonal and interannual stability of the diagnosed feature | the boundary reverses or wanders across most of its proposed territory |
| Cross-boundary exchange | normal volume and heat transport through the proposed edge | exchange is as strong as, or stronger than, transport along the edge |
| Pathway retention | fraction of a released ensemble retained within or routed consistently through a candidate region | trajectories mix rapidly across several neighboring regions |
| Convergence coherence | sign and magnitude of heat-transport convergence inside the candidate region | convergence and divergence form unrelated patches with no stable regional identity |
| Vertical agreement | comparison of surface, thermocline, intermediate, and deep motion | the surface partition conceals a dominant return path or depth reversal |
| Gate dependence | sensitivity of regional exchange to narrow passages and topographic controls | the proposed edge ignores the gate that actually controls exchange |

These diagnostics should be shown as scores with uncertainty and scale, not as
proof that a fluid boundary is a permanent wall. A future rationalization may
merge, split, move, or demote regions; it should not preserve 22 merely because
22 is already drawn.

## Promotion rules

- Never label `uT` or `vT` alone as total heat transport.
- Never infer full-depth delivery from OSCAR's assumed upper-30-m average.
- Never infer transported heat from a streamline or parcel count alone.
- Never hide the temperature reference or an unbalanced volume flux.
- Keep mean-flow, eddy, and parameterized diffusive contributions distinct.
- Show missing support and model limitations instead of filling them decoratively.
- Preserve the current zoning unchanged until the motion evidence can test it.

## Evidence base

- [NASA PO.DAAC OSCAR v2.0](https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0)
- [ECMWF ORAS5 description](https://www.ecmwf.int/en/forecasts/dataset/ocean-reanalysis-system-5)
- [Copernicus ORAS5 quality assessment](https://cds.climate.copernicus.eu/datasets/reanalysis-oras5?tab=quality_assurance_tab)
- [Zuo et al. (2019), OCEAN5/ORAS5](https://doi.org/10.5194/os-15-779-2019)
- [Boccaletti et al. (2005), vertical structure of ocean heat transport](https://doi.org/10.1029/2005GL022474)
- [Volkov et al. (2008), eddy-induced meridional heat transport](https://doi.org/10.1029/2008GL035490)
- [OceanParcels structure and field requirements](https://docs.oceanparcels.org/en/latest/examples/tutorial_parcels_structure.html)
- [OceanParcels diffusion treatment](https://docs.oceanparcels.org/en/latest/examples/tutorial_diffusion.html)
