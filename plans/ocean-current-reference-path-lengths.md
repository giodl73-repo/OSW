# Reference-path estimates for the other 89 currents

Date: 2026-10-04. Status: working editorial candidates; no new canonical
numeric estimates admitted. Current coverage: 62 candidates for 59
of the 89 currents; 30 awaiting routes. Progress entries below are chronological.

The current inventory contains 100 names and 11 source-reported ranked length
estimates. The remaining 89 consist of seven OSW geographic lower bounds, one
published lower bound, one proposed system-length hypothesis, one sampled
reach, eight section-only records, and 71 records without a numeric length.
Those groups partition the 89; existing cartographic arrow spans are a separate,
overlapping display measure.

## Intended result

Every remaining current gets a reference-path decision. Where evidence permits,
provide an approximate length, a visible path, endpoint and branch assumptions,
and a range from alternative plausible routes. Otherwise retain the explicit
reason that a whole-current path cannot yet be defined. A lower bound, section
width, coastal distance, or sampled reach must not become a whole-current
estimate simply because it is the only available number.

Use separate tables for source-reported extents and OSW reference-path estimates.
An optional combined comparison must retain method, scope and comparability
warnings on each row. Approximate ordering is useful even when adjacent ranges
overlap; describe such positions as unstable rather than implying exact ranks.

## Route construction

1. **Define the object.** Resolve system versus branch, flow direction, layer,
   named-flow start and end, and seasonal reversal. For a current family that
   spans multiple basins, record basin members separately. A branched system
   needs a declared main route and separate branches; do not silently add all
   branches into its main-route length.
2. **Use sourced geography.** Read the existing naming sources for endpoints,
   turns, confluences and separation regions. Record the passage for every
   waypoint or region. A schematic can support an explicitly editorial route,
   with that geometry role visible. Do not imply that its drawn arrow is a
   measured current axis.
3. **Build plausible paths.** Trace a nominal route and shorter/longer supported
   alternatives through the declared regions. Preserve a source's coordinate
   reference system; record the chosen CRS for OSW editorial coordinates.
   Check land crossings, longitude seams, loops and branch connectivity.
   Reconstruct a closed circuit only where evidence supports continuity.
4. **Calculate geodesic length.** Sum WGS84 geodesic distances along the declared
   reference polyline. The result measures that polyline, not every meander or
   the distance traveled by a water parcel. Do not multiply a straight endpoint
   distance by a universal curvature factor.
5. **Describe sensitivity.** Vary supported endpoints, branch conventions and
   route alternatives. Report their length range as an assumption sensitivity
   range, not a statistical confidence interval. A local segment remains a
   reach unless its endpoints define the whole named flow. Round to precision
   justified by source geography, normally tens or hundreds of kilometres.
6. **Validate and join.** Compare estimates against any independent reported
   extent. Inspect discrepancies before admission. Use the same route for
   state intersections and NASA crop navigation, retaining its editorial or
   model-derived role and avoiding a physical-passage claim without evidence.

## Model refinement

For flows with suitable resolution and layer support, diagnose a current axis
from velocity data within a source-defined corridor. Specify the product,
version, dates, depth averaging, speed/direction rule, extraction method and
start/end gates. Check repeated months or seasons and report route variability.
Require geographic and flow continuity; a streamline alone does not establish
the named current's endpoints. Coarse products may miss narrow shelf currents.

[NASA SVS 5505](https://svs.gsfc.nasa.gov/5505) describes ECCO2 output for
2021–2023 and combines depths in its visualization. Movie pixels therefore do
not provide a uniquely defined current centerline or layer. The
[ECCO V4r4 velocity product](https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4)
is a separate potential analysis product; it must not be described as the
exact field used for those movies. Product selection and resolution suitability
must be established per current before extraction.

## First batch and required records

Start with the seven source-gated geographic floors: their existing endpoints
provide a useful starting point, but every intermediate route still needs
evidence. Then work through the 82 other records, prioritizing currents with
source-defined endpoints and continuous named-flow descriptions. Resolve the
Norwegian labels and broad South Indian/South Pacific flow scopes before
forcing a single route; see `ocean-current-length-definition-audit.md`.

Each candidate must record stable current ID, route ID, geometry role, scope,
layer/time convention, source-linked gates and waypoints, CRS, nominal/alternative
lengths, algorithm and input hashes, sensitivity assumptions, rank eligibility,
review status and state/crop joins. Keep candidate lengths separate from the
existing published-estimate field. First deliverable: seven inspected route
candidates, followed by the full 89-record decision inventory.

## Current verification boundary

The first computed candidate is the East Australian Current coherent jet:
approximately 2,100 km, with a rounded 2,000–2,300 km editorial scenario envelope.
The generator retains 27 scenarios and checks their densified geodesic routes
against the coarse OSW land mask. All scenarios cross ARCH and AUSE in the
display atlas. Twelve NASA crops have some scenario overlap; `level2_F_5` is
the deterministic recommended complete-route crop. These are navigation joins.
The seven original geographic-floor records and eleven published estimates
are unchanged. This is one candidate from the proposed first batch, not a
completed seven-route or 89-current inventory.

The Agulhas Return source was inspected in full on the next pass. Printed
pages 125 and 136 support a source-specific western/eastern convention beyond
the original 21–60 degrees E sketch. A separate candidate from first clear
evidence near 16 degrees E to the midpoint of the 66–70 degrees E terminal
region measures approximately 4,600 km, with 243 editorial endpoint/meander
scenarios spanning a rounded 3,900–4,900 km envelope. The original studied
reach remains approximately 3,300 km and is excluded from reference-route
ordering. The source's temporal and branch limitations remain attached.

`almanac/reference-routes.html` now displays the candidate maps, scope, source,
state/crop links and a searchable 89-current decision inventory. The generated
`research/ocean-current-reference-path-candidates.json` indexes three routes
for two currents and 87 currents without routes. This page is a full-tree
review surface, not part of the isolated screened export or a public release.

Additional inputs: `research/agulhas-return-reach-reference-path-input.json`
and `research/agulhas-return-extent-reference-path-input.json`. Pass each with
`--input` to the candidate generator, then run
`python analysis/build_current_reference_path_catalog.py`.

The East Greenland pass adds an approximately 2,700 km regional outer/slope
corridor, with 27 finite editorial scenarios spanning a rounded 2,500–2,800 km
envelope. The source's 78.5 degrees N section and 59 degrees N regional boundary
define this particular comparison; 59 degrees N is not asserted to be the exact
Cape Farewell coordinate. Keep the separate coastal-current axis, Arctic
upstream extensions, interior branches and downstream West Greenland flow out
of this route. All scenarios cross ARCT and SARC in the display atlas; complete
route crop `level2_C_1` supplies geographic context only. The catalog now has
four candidates for three currents, with 86 currents awaiting routes. Input:
`research/east-greenland-reference-path-input.json`; use the same generator and
catalog commands above. The canonical floor and published ranking are unchanged.

The Brazil/Benguela pass adds two scoped branch candidates. The Brazil
poleward branch measures about 3,200 km, with 27 source/assumption scenarios
spanning a rounded 2,600–4,200 km envelope. Chidichimo et al. (2021) supplies
the 10–15 degrees S origin region; Schmid and Majumder (2018) supplies the
34.5–40.5 degrees S southern front/confluence proxy convention. Neither source
supplies the chosen full-route vertices. The Benguela shelf-edge branch
measures about 2,500 km, with 54 scenarios spanning a rounded 2,200–2,600 km
envelope. Cape Agulhas regional geography from Caínzos et al. (2023) and the
Angola–Benguela frontal convention from Lass et al. (2000) support scope; the
observed 1997 front latitude is an alternate endpoint convention, not an
observed full-current route. Offshore extensions and ecosystem perimeters are
excluded. Both candidates carry supporting source links in the catalog and UI.

Inputs: `research/brazil-reference-path-input.json` and
`research/benguela-reference-path-input.json`. Catalog coverage is now six
routes for five of the 89 currents, with 84 currents awaiting routes. The two
existing 1,200 km regional geographic floors remain separate and unchanged.

Inputs: `research/east-australian-reference-path-input.json`.
Outputs: `research/east-australian-reference-path-candidate.json` and
`figures/east-australian-reference-path-candidate.svg`.
Run `python analysis/build_current_reference_path_candidate.py` and
`python analysis/test_current_reference_path_candidate.py`.

The first seven-current batch now has eight candidates for seven currents;
82 of the 89 currents still await routes. The added Agulhas regional route
from 27 degrees S to a 40 degrees S turning gate measures about 2,000 km,
with 81 scenarios spanning 1,800–2,200 km. Russo et al. (2022) supports this
regional extent convention, rather than a narrower coastal-jet definition;
the eastward return current and ring trajectories are excluded.

The DWBC candidate measures about 4,100 km along a coarse western-boundary
sketch linking 47 and 24.5 degrees N study sections. Its 27 scenarios span
3,900–4,200 km. Caínzos et al. (2023), section 3.2.3, provides section-specific
deep-flow identity and latitude gates, not a continuous axis. Intermediate
vertices and continuity are OSW assumptions. It joins the Agulhas Return
studied reach outside reference-route ordering. Neither candidate replaces
the existing 1,400 km Agulhas or 2,400 km DWBC regional geographic floor.

Inputs: `research/agulhas-reference-path-input.json` and
`research/deep-western-boundary-reach-reference-path-input.json`.
Their output maps, coordinates, scenarios and atlas/NASA context joins are
accessible from `almanac/reference-routes.html`. All eight candidates remain
editorial, with scientific axis and canonical-admission gates unresolved.

The Australian-component pass adds Leeuwin (about 2,900 km, 2,400–3,000 km),
South Australian (about 800 km, 700–1,100 km) and Zeehan (about 800 km,
500–900 km), each with 54 scenarios. Ridgway and Condie (2004), sections 2,
7 and 9, supplies the regional and winter naming conventions. All intermediate
vertices are OSW choices. Leeuwin includes a southern extension into the
Bight; the shorter central-Bight alternative is an editorial interpretation.
South Australian and Zeehan retain austral-winter scope and different regional
handoffs. The routes do not form a partition of the published 5,500 km system:
they cannot be summed into that measurement. Existing Leeuwin >2,000 km
published bound and the full system estimate are unchanged.

The comparison catalog now provides overlapping candidate IDs and conservative
position bounds from retained rounded scenario envelopes. Touching intervals
count as overlaps. Bounds treat route choices independently and say nothing
about probability, untested routes, physical axes or uniform scope. Studied
reaches are excluded. South Australian and Zeehan have positions 8–9 among
the current nine comparable routes, rather than a precise tied rank.

Inputs are the three `research/{leeuwin,south-australian,zeehan}-reference-path-input.json`
files. Rebuild with the candidate/catalog commands above. Verify with
`python analysis/test_current_reference_path_candidate.py`,
`python analysis/test_current_reference_path_catalog.py` and
`python analysis/test_motion_almanac_browser.py`.

The North Pacific pass adds two source-convention candidates. NOAA's glossary
defines a North Pacific extent beginning near 160 degrees E and ending beyond
about 150 degrees W. OSW uses a nominal 145 degrees W terminal gate and a
150 degrees W alternative, with three latitude corridors chosen by OSW.
The route measures about 4,700 km, with 162 scenarios spanning 3,900–5,000 km.
The AMS glossary instead places the western origin near 170 degrees W; that
contrasting convention is linked explicitly, not merged into this extent.
Downstream Alaska/California branches are excluded. Kuroshio Extension uses
NOAA's approximate 145–160 degrees E convention: about 1,400 km with 27
scenarios spanning 1,100–1,600 km. Other literature can use different limits;
no universal termination is claimed.

Inputs: `research/north-pacific-reference-path-input.json` and
`research/kuroshio-extension-reference-path-input.json`. The North Pacific
input declares `longitude_seam_policy=shortest_geodesic_periodic_display`.
Without that explicit policy, date-line-jumping vertices remain rejected.
With it, scenario vertices normalize longitude, WGS84 geodesics take the short
arc, display points unwrap continuously and land/state joins use adjacent
world copies. Crop checks retain periodic translations. Endpoint labels use
the unwrapped positions, and the map marks the 180-degree seam. Exactly
180-degree legs still require intermediate waypoints; a full-revolution route
requires separate circuit handling. Numerical tests cover eastward/reverse
seam crossings, short-arc distance, local Pacific joins and absence of an
unrelated Atlantic intersection.

Every candidate now pins the generator file and its SHA-256 in addition to
the input/map/tile hashes. Catalog generation rejects a missing or stale
generator fingerprint. The initial all-candidate rebuild exposed differences
in older output files; a second full rebuild was byte-identical before adding
the fingerprint fields. All outputs are regenerated with those fields.
The catalog test suite includes rejection of stale/missing generator records.

Coverage is thirteen candidates for twelve currents and 77 unbuilt records.
All routes remain editorial and the published ranking is unchanged.

The North Atlantic/Alaska pass adds two regional candidates. North Atlantic
uses NOAA's 40 degrees N, 50 degrees W start region and British Isles
destination, with three OSW western-approach terminal routes: about 3,300 km
and a 3,100–3,500 km envelope over 81 scenarios. Onward Norwegian/Canary,
Iceland-directed branches, upstream Gulf Stream and the full Gulf Stream
System are excluded. Alternate terminal routes are editorial geographic
conventions rather than observed branches.

Schumacher et al. (1979), NOAA PMEL-13, section 1.1, distinguishes northward
Alaska Current off British Columbia/southeast Alaska from Alaskan Stream
on the northern/northwestern gyre arm. OSW chooses regional gates for the
northward branch: about 1,400 km, 700–1,700 km over 81 scenarios. The source's
1977 Kodiak measurements do not observe this full route; they concern the
distinct stream/shelf circulation. The nearshore Alaska Coastal Current is
also excluded. The regional start/end choices remain open scientific gates.

Inputs: `research/north-atlantic-reference-path-input.json` and
`research/alaska-reference-path-input.json`. Generated routes cross NADR,
NECS, NWCS and SARC for North Atlantic and ALSK, OCAL and PSAE for Alaska
in the OSW display atlas; these are editorial line/region relationships.
Complete-route NASA crop contexts are `level2_C_2` and `level2_A_1`.
Coverage now has fifteen candidates for fourteen currents, with 75 awaiting
routes. All 1,026 retained scenarios have independently recomputed lengths.

## Full planning taxonomy and decision inventory

All 89 records now have one explicit primary construction strategy in
`research/ocean-current-route-strategy-input.json`. The classification is an
OSW planning crosswalk into the existing `ocean-motion-taxonomy.json`, not a
scientific assignment to a single exclusive physical type. Constraints can
overlap: a seasonal flow may also be subsurface or branched. The primary
strategy describes the next scope/evidence problem to resolve.

| Primary strategy | All records | Awaiting routes |
| --- | ---: | ---: |
| Split basin families | 8 | 8 |
| Define system and branch graph | 3 | 2 |
| Keep continuity hypothesis separate | 1 | 1 |
| Construct seasonal routes | 13 | 10 |
| Construct dated/regime geometry | 3 | 3 |
| Resolve naming/extent convention | 13 | 11 |
| Construct layer-specific paths | 13 | 13 |
| Extend evidence beyond sections | 5 | 5 |
| Preserve surveyed-reach scope | 1 | 1 |
| Establish sourced regional route | 29 | 21 |
| Total | 89 | 75 |

Each catalog decision retains the existing ledger kind, source/evidence scope,
primary strategy, next action and known component-current links. A candidate
does not resolve every broader scope problem: the DWBC study reach still
needs a system/branch graph for a broader estimate. Known family members are
explicitly incomplete coverage; North and South Equatorial family basin-member
records have not yet been added, which does not imply flow absence.

The generator validates exact 89-record coverage, unique assignments, defined
strategies, family-kind agreement, valid component navigation and pinned
evidence/ledger bases. Family objects cannot receive one route measurement in
the candidate comparison; their children need separate routes. The browser
supports strategy and coverage filters together, full-text evidence search,
component links, next steps and taxonomy descriptions. This crosswalk remains
in the full working review tree, outside the canonical export.

This plan supplies a reproducible estimation method, not 89 completed lengths.
Scientific route review, source-use screening and publication review remain
required. Existing published estimates also differ in scope and do not by
themselves define a uniform global reference-path ranking.

## Mediterranean regional candidates (2026-10-02)

Northern Current: approximately 700 km, with a rounded 600–800 km envelope
across 54 scenarios. Berta et al. (2018), section 1 supplies the Ligurian-to-Catalan
regional convention; Aguiar et al. (2022), section 2.1 supplies the bifurcation
near 40.6 N. OSW chooses exact gates and offshore vertices. The shorter
alternative ends earlier in the Catalan region. Corsica feeders, downstream
Ibiza/Balearic branches and offshore eddies are excluded. This is not the
December 2011 Toulon survey's measured full route.

Algerian Current: approximately 900 km, with a rounded 600–900 km envelope
across 108 scenarios. Cotroneo et al. (2019), section 1 describes eastward
along-slope coastal flow after the Alboran Sea. OSW chooses western gates
at -1.5/0 E and eastern gates at 7/8 E; the source does not assert those exact
endpoints. Alboran gyres, shed eddies and downstream Mediterranean routes
are excluded. The 2014–2016 glider surveys are not a complete current axis.

Both candidates use the highest-resolution all-scenario complete-route NASA
crop level2_C_2. Display crossings are Northern: MEDI/NECS; Algerian: MEDI.
These are editorial atlas intersections, not scientifically established
physical current passage. All retained scenarios avoid the coarse OSW land
mask; shelf-break correspondence remains unresolved.

Current totals: 17 candidates for 16 of 89 currents, 73 awaiting routes,
15 comparable route rows and two separately labeled surveyed reaches.
The source-gated regional strategy retains 29 records, now 19 unbuilt;
all other strategy counts remain as in the preceding planning crosswalk.
Optional regional figure typography/symbol scales keep Mediterranean figures
readable. All 17 candidates were regenerated to pin the changed generator.
The canonical eleven-value published ranking is unchanged.

## Somali seasonal routes and inventory expansion (2026-10-02)

Schott and McCreary (2001), section 4.2.1 supports a winter southward coastal
branch from divergence near 6–8 N to EACC confluence near 2–4 S. The OSW nominal
7 N to 3 S route measures approximately 1,500 km, with a 1,100–1,800 km envelope
across 81 editorial scenarios. Exact longitudes and intermediate vertices are
OSW choices. The northern counterflow, offshore feeder, eastward continuation,
undercurrents and gyre circuits are excluded.

Section 4.1.1 supports a different June–July southern coastal limb: cross-equatorial
flow turns offshore south of 4 N, with little exchange with the Great Whirl.
An OSW equatorial bookkeeping gate to 3.5 N separation gate measures about
600 km, with a 500–700 km envelope across 81 scenarios. This is a seasonal
component, not the full summer Somali system. It does not assume rare gyre
coalescence and does not add Southern Gyre or Great Whirl perimeters.

Both maps were inspected and all scenarios pass the coarse land-mask check;
shelf/slope correspondence remains unresolved. NASA complete-route crop is
level2_D_4. State/crop links remain editorial display geography.
Totals: 19 candidates for 17 of 89 currents, 72 awaiting routes, 17 comparison
rows and two separately labeled studied reaches. Seasonal strategy remains
13 records, now 9 unbuilt. Canonical published ranks remain unchanged.

The current ledger omits Mozambique Current. A separate proposed-additions
record and review-page section preserve this inventory gap without silently
claiming a complete global census. Lutjeharms et al. (2012) describes intermittent
continuous flow and an approximately 1,500 km plume in a dated thermal image;
Harlander et al. (2009) describes an eddy-dominated mooring record without a
continuous upper-layer boundary current. Neither establishes a persistent
whole-current axis/length. Identity, dated geometry, taxonomy and canonical
integration remain open. The proposed addition is not counted in the 89 queue.

## Labrador and West Greenland regional branches (2026-10-02)

Labrador main offshore regional route: approximately 2,100 km with a
1,800–2,400 km rounded envelope across 81 scenarios. Hildebrand (1984),
Oceanographic Setting, printed p. 11/PDF index 12 supports the southern Davis
Strait origin and the Labrador/Newfoundland-to-western-Flemish-Pass/Grand-Banks
tail sequence. Exact 60 N/43 N gates and vertices are OSW choices. The source's
figure arrows encode velocity classes, not distances, and were not digitized.
Feeder currents, Hudson Strait intrusion, inshore Avalon route and downstream
branches/eddies are excluded. This historical geographic convention is not a
current or simultaneous velocity field.

West Greenland northward shelf-break branch: approximately 1,100 km with a
900–1,300 km envelope across 81 scenarios. Gou et al. (2022), abstract and
section 3.1 supports Cape Farewell-to-Davis continuation, distinguishing the
coastal shelf current and westward major branch. OSW chooses exact gates
and the 66/67/68 N Davis terminal alternatives. Flow beyond Davis Strait
remains possible; the terminal convention does not establish cessation.
No top-50 m model axis or 500 m contour is extracted. The source model
period 2008–2018 is context rather than the date of our editorial geometry.

All scenarios pass the coarse land mask. Both figures visually inspected.
Recommended full-route NASA crops: Labrador level2_B_2; West Greenland
level2_B_1. Display crossings: Labrador NWCS; West Greenland NWCS/SARC.
These remain editorial cartographic relations; physical current passage and
shelf/slope correspondence still require review.

Totals: 21 candidates for 19 of 89 currents, 70 awaiting routes, 19 comparable
rows and two separate study reaches. Source-gated regional strategy has 29
records and 17 unbuilt. No canonical published lengths changed.

West Greenland Coastal Current is a second proposed inventory addition,
with separate shelf-current identity, no copied shelf-break route/length,
and canonical admission pending. Gou 2022 full text is the primary identity
support. The 2023 moored-observation paper is additional title/indexed-excerpt
context; its publisher full page returned 403 and no whole-current extent
is inferred from that access. Two proposals are outside the current ledger.

## Baffin reach and Irminger ridge branch (2026-10-02)

Fissel et al. (1982), abstract/results pp. 180/183, describe summer near-surface
Baffin flow observed at least from Lady Ann Strait (76 N) to Cape Dyer (67 N).
The OSW external coastal reference reach is about 1,200 km, with a
1,100–1,300 km envelope across 54 scenarios. It omits the Lancaster Sound
intrusion/return and transient eddies; latitude bounds are not full-current
endpoints. The editorial path is not a digitized 1978/1979 drifter track.
It joins the separately labeled studied-reach group and is excluded from
main reference-route ordering.

Vage et al. (2011), section 1 pp. 590–592, and Fried et al. (2026), section 1,
support the northward western-Reykjanes-flank Irminger Current and its distinct
northern and Greenland-return paths. OSW 56/65 N regional gates give about
1,200 km, with a 700–1,400 km envelope across 81 scenarios. Narrower 58/64 N
and broader 55.5/65.5 N conventions are editorial choices, not published
nomenclature endpoints. Return flow, NIIC, interior gyre circuits and deep
overflow currents are excluded. No two-core axis or model particle track traced.

Both figures inspected; all scenarios pass the coarse land-mask check.
Both full-route NASA crops are level2_B_1. Display crossings: Baffin NWCS,
Irminger SARC. Physical passage and coastal/ridge correspondence remain open.
Totals: 23 candidates for 21 of 89 names; 68 awaiting routes; 20 comparable
rows and three separate studied reaches. Source-gated regional strategy
retains 29 records, now 15 unbuilt. Baffin's whole extent remains unresolved
despite candidate coverage. Canonical eleven-value published ranking unchanged.

A third proposed inventory object is North Icelandic Irminger Current.
Fried 2026 names this flow and notes that its source waters may differ from
those at the chosen upstream OSNAP particle release region. The proposal
therefore does not assert a fixed parcel-continuity edge, borrow ridge-flank
length or define full north-Iceland endpoints. Identity and canonical admission
remain pending; proposal lies outside the 100-name ledger and 89-record queue.

## 2026-10-03: Caribbean and Mindanao regional routes

Added Caribbean (approximately 2,800 km; 2,500–2,800 km across 54 scenarios)
and Mindanao (approximately 1,000 km; 800–1,200 km across 81 scenarios).
Caribbean selects one westward regional corridor, ending at the transition
before the northward Yucatan Current; the alternative northern corridor is
not an additional branch to sum. Centurioni and Niiler (2003) supply regional
circulation context, not this exact path. Lagrangian decorrelation length
scales do not measure the named current.

Mindanao uses Kim et al. (2004) near-surface model northern gates: 14.3 N
mean, 13.2 N May, 15.1 N September. Deeper bifurcation gates and the opposing
undercurrent are excluded. The 5.5 N southern approach and all longitudes
are OSW choices; seasonal alternatives change only the northern gate.
Grenier et al. (2011) provide regional downstream topology, not the full axis.
Their 8.098 N interception section is not an origin or length endpoint.
One southern scenario initially intersected the coarse land mask; moving
the editorial southern approach offshore resolved it. Shelf/core position
still requires independent bathymetric and velocity verification.

Coverage: 25 candidates for 23 of 89 names; 66 awaiting routes. Twenty-two
comparison rows and three studied reaches; 1,782 editorial scenarios total.
NASA crops are geographic navigation context, not current identity matches.
Canonical measurements and the eleven published length ranks remain unchanged.

Validation: 12 focused tests, full almanac checker and full Chromium browser
suite pass. Both SVGs inspected; 25 provenance pins and all 1,782 geodesic
sums verified; catalog rebuild byte-identical. Internal seven-role review
recorded in `signals/roles/check/caribbean-mindanao-reference-routes-roles-check-2026-10-03.md`.

## 2026-10-03: North Brazil surface branch and Guiana scope decision

North Brazil adds approximately 2,200 km (1,800–2,500 km), from a 5 S
surface-origin convention to a 7 N nominal retroflection approach. Earlier
5 N and later 9 N terminal-region conventions yield 81 editorial scenarios.
Sources: Dimoune et al. (2023), section 1, and NOAA/AOML NBC overview.
NOAA's broader 4–10 N range lies outside this finite scenario set.
No extracted mean axis, upstream NBUC, offshore return branch, downstream
continuations or ring perimeter/travel distance is included.

Guiana/Guyana needs explicit nomenclature resolution; the planning strategy
now reflects that source ambiguity. The audit retains null length, no alias
merge and no fixed physical boundary. The catalog supports an explicit
per-current next action for this source-specific work.

Coverage: 26 candidates for 24 of 89 names; 65 awaiting routes. There are
23 comparison rows, three studied reaches and 1,863 scenarios. Scientific,
canonical and publication gates remain open; eleven published ranks unchanged.

Validation: 12 focused tests, full almanac checker and full Chromium browser
suite pass. The map was visually inspected; all 1,863 scenario sums and 26
provenance pins verified; catalog rebuild byte-identical. Seven-role internal
review: `signals/roles/check/north-brazil-guiana-scope-roles-check-2026-10-03.md`.

## 2026-10-03: Oyashio first-intrusion branch

Qiu (2019), The Oyashio Current, pp. 391-393, supplies a naming convention
south of Bussol Strait and distinguishes the first southward intrusion from
offshore return flow and downstream fronts. The regional route starts at an
OSW Pacific-side gate south of the strait and ends nominally at 40 N.
Alternatives use April 38.5 N and December 41.5 N temperature-index limits
at 100 m. These are not recovered velocity axes or seasonal current lengths.
All longitudes and connecting vertices are editorial; 40 N is not an annual
mean. Upstream Kamchatka, Okhotsk circuits, offshore return, eastward extension
and eddies are excluded. Oyashio planning now reflects seasonal-route work.

Approximately 1,000 km, 700–1,200 km across 81 scenarios. Coverage is now
27 candidates for 25 of 89 current names; 64 await routes. There are 24
comparison rows, three studied reaches and 1,944 scenarios. Canonical lengths
and the eleven published ranks remain unchanged.

Validation: 12 focused tests, full almanac checker and full Chromium browser
suite pass. All 1,944 geodesic sums and 27 provenance pins verified; catalog
rebuild byte-identical. Map visually inspected. Seven-role review in
`signals/roles/check/oyashio-first-intrusion-route-roles-check-2026-10-03.md`.

## 2026-10-03: Broad Hiri convention and Gulf of Papua names

Added a broad Hiri regional route: approximately 1,900 km (1,900–2,500 km),
54 scenarios. Wijeratne et al. (2018), sections 1/3.1.5, support a near-15 S
northward origin convention and Gulf of Papua circulation; Oliver and Holbrook
(2014), section 3, support a broader 18 S regional origin alternative. These
are not equivalent-depth observations. Burrage (1993), pp. 136-137, describes
clockwise flow around the Gulf entrance and an exit around the Louisiades.
All connecting vertices and the final eastern approach are OSW choices.
Closed gyre return, eddies and downstream New Guinea routes are excluded.

Ganachaud et al. (2014), section 4.1, distinguish NQC, GBRUC beneath it and
Hiri south of PNG, and propose a connected Gulf of Papua Current system.
Hiri planning now requires naming-scope work even with this broad candidate.
Added three proposed inventory records for those missing names, with null
whole-current lengths and no canonical alias merge. System/member/layer
relations must be reviewed before admission. Six proposals total remain
outside the 100-name ledger and 89-current length queue.

Coverage: 28 routes for 26 of 89 names; 63 awaiting routes. Twenty-five
comparison rows, three studied reaches, 1,998 editorial scenarios. Published
eleven-length ranking and canonical measurements remain unchanged.

Validation: 12 focused tests, full almanac checker and full Chromium browser
suite pass. Hiri SVG inspected; all 1,998 sums and 28 provenance pins verified;
catalog rebuild byte-identical; six proposals unique and absent from pinned
ledger. Internal seven-role review in
`signals/roles/check/hiri-gulf-papua-names-roles-check-2026-10-03.md`.

## 2026-10-03: Guinea regional route and vertical names

Guinea adds a Cape Palmas offshore approach to the weakening region near
2 E: about 1,200 km, with a 1,000-1,200 km editorial scenario envelope.
Alory et al. (2021), Surface Circulation and Subsurface Conditions, supports
the regional summer context; exact vertices and alternative 1.5 E gate are
OSW choices. Source simulation summer mean is 2010-2017, drifter climatology
1979-2019. The upwelling extent and Gulf boundary are not current endpoints.
All 54 scenarios clear the coarse map; physical axis correspondence remains
unreviewed. NASA C3 covers the display route; ETRA/GUIN are display crossings.
Guinea Counter Current and Guinea Under Current are two proposed names,
with separate layer/extent gates and null lengths. No undercurrent direction
or full extent is inferred from this cross-shore section.

Coverage: 29 candidates for 27 of 89 names, 62 awaiting routes, 26 comparison
rows and three studied reaches; 2,052 scenarios. Eight inventory proposals
remain outside canonical counts. Scientific/canonical/publication gates open.

Measurement conventions are consolidated in
`plans/ocean-current-measurement-protocol-v1.md` (v1.0); the route review page
shows its summary and links. Run `analysis/check_current_measurement_protocol.py`
after each batch. The audit checks calculation/provenance conformance and leaves
source support and scientific correspondence for review. The earliest EAC
source was rechecked on 2026-10-03; its unrecorded original retrieval date is
not reconstructed, and geometry/length remain unchanged.

Verification for Guinea and protocol: 14 focused tests, full checker and browser
suite pass; 29 provenance sets and all 2,052 geodesic scenarios audit successfully.
Revised Guinea SVG inspected. Seven-role internal audit:
`signals/roles/check/guinea-measurement-protocol-roles-check-2026-10-03.md`.

## Protocol enforcement follow-up (2026-10-03)

Catalog builds now run the v1.0 conformance audit before writing output and pin
its result and protocol hashes. Audit reconstructs the full declared scenario
grid, rejects omissions/duplicates/nonfinite distances/invalid dates, and checks
source metadata equals the pinned input. A rejection test proves the catalog
output write is not reached. These strengthen enforcement of existing rules;
no route, algorithm, canonical count or ranking definition changes.

Enforcement verification: 17 focused tests and full almanac checker pass;
consecutive audit/catalog builds are byte-identical and both protocol/audit
hash links verified. Existing seven-role audit updated with enforcement evidence.

## 2026-10-03: Western Adriatic surface corridor

Regional Po approach to western Otranto measures about 700 km, with a
700-800 km envelope across 54 retained editorial scenarios. Poulain and Hariri
(2013), sections 2.1-2.2/3 and figure 1, supplies surface-flow and western-exit
context; Sciascia et al. (2018), section 2.1, supplies buoyant Po-forced identity
and wind modulation. Exact vertices and gates at 40.4/40.0 N are OSW choices.
The source's rotated local-frame outflow coordinates are not treated as lon/lat;
40 N basin residence-time boundary does not establish current termination.
Deep branches, basin gyre circuits and local recirculation are excluded. This
is neither a drifter trajectory nor a velocity-derived annual mean axis.

All scenarios clear the coarse atlas land mask; shelf/velocity correspondence
remains open. MEDI is the display crossing and NASA C2 the recommended context.
Coverage: 30 candidates for 28 of 89 names, 61 awaiting routes; 27 comparison
rows, three studied reaches, 2,106 scenarios and eight inventory proposals.
Protocol v1.0 runs automatically before catalog output; independent scientific
and canonical/publication gates remain open.

Verification: 17 focused tests, full almanac checker and full Chromium browser
suite pass. All 30 reports and 2,106 scenarios pass the automatic protocol audit;
byte-identical audit/catalog rebuild and matching protocol/audit pins verified.
SVG visually inspected. Seven-role audit:
`signals/roles/check/western-adriatic-surface-route-roles-check-2026-10-03.md`.

## Jutland regional reference corridor (2026-10-03)

Added German Bight approach to northern-Jutland offshore/Skagerrak approach
under the canonical Jutland Current name. Lenz et al. (2024), Section 1.3,
supports northward Danish-coast circulation; Passaro et al. (2015), Section 2,
supports surface-flow context and transition to Norwegian Coastal Current.
The source papers describe regional circulation and sea-level/sediment studies,
not these route vertices or a measured full-current length. OSW selects both
gates, every offshore point and the alternative southern/eastern gates.

Approximately 400 km; 400-500 km across 54 editorial scenarios. This excludes
upstream English Channel/southern North Sea circuits, Baltic Current inflow,
Norwegian Coastal Current continuation and separate North/South Jutland branch
lengths. No seasonal length or width inferred from sea-level seasonality.
All scenarios pass coarse OSW land clearance; shelf/current-core correspondence
and exact naming gates still need scientific review. NECS display crossing and
NASA level2_C_1 crop provide geographic context only.

Lenz Figure 1 caption explicitly lists North and South Jutland labels. Their
relation to the single canonical name remains unresolved in
`research/jutland-current-naming-scope-audit.json`; no aliases, branch identities
or lengths admitted. The underlying circulation-chart convention needs review.

Coverage: 31 route candidates for 29 of 89 names; 60 awaiting routes,
28 comparison rows, three studied reaches and 2,160 editorial scenarios.
Jutland envelope positions 26-28 overlap other short routes, including touching
rounded envelopes. Published 11-estimate ranks and canonical measurements
remain unchanged. Revised Jutland SVG inspected: legend moved above route to
avoid covering it. Protocol audit and 35 focused tests pass.

Full Chromium browser suite passes Jutland scope/source/crop navigation, 31/29/60 coverage, 28 comparison rows, revised shortest-route ordering and touching-envelope bounds alongside all existing atlas checks.

## Davidson historical winter regional route — 2026-10-03

The 1978 Fisheries and Environment Canada report, *Potential Pacific Coast
Oil Ports*, Volume II, Appendix II section II.1 / printed II-1 to II-2
(PDF pages 12-13), supplies California-Oregon northward surface-current scope
and October-March season. OSW selects every offshore vertex and bookkeeping
gates at 35 N and 46 N; alternative 34 N/45.5 N gates test endpoint convention.
No exact named origin, endpoint or measured axis is published in this passage.
Conditional Vancouver Island penetration and the deeper California Undercurrent
are excluded. Historical applicability and coastal bathymetry need review.

The WGS84 route is approximately 1,300 km, with a rounded 1,200-1,400 km
editorial envelope across 54 gate/longitude/endpoint-latitude scenarios. All
scenarios avoid the coarse atlas land mask; this does not validate coastal
core location. NASA crop level2_A_2 covers all retained routes geographically,
without asserting Davidson identification or synchronized seasons in the movie.
The separate approximate 64 km historical width is not used as a route buffer.

Coverage: 32 candidates for 30 of 89 names; 59 await routes. Twenty-nine
comparison rows and three studied reaches retain 2,214 editorial scenarios.
Davidson envelope positions 14-22 overlap other regional lengths; these are
sensitivity positions, not published or empirical whole-current ranks. No
canonical lengths or published rankings change. SVG and seasonal page inspected.

## Tsushima Japanese coastal corridor — 2026-10-03

Yoon et al. (2016), doi:10.1002/2016JC011891, introduction, supports the
Nearshore Branch from the eastern Tsushima channel along Japan toward Tsugaru.
Downstream merges mean the full corridor is not an exclusive component or parcel
route. Yokomatsu and Kida (2025; online 2024) uses broader coastal/offshore
grouping; JMA warns that continuous paths are rare. Source-specific grouping
levels are retained rather than declaring a universal two/three-branch taxonomy.

Every vertex and inlet/outlet approach gate is OSW-selected. The regional route
is approximately 1,300 km, with 54 gate/coordinate scenarios yielding a rounded
1,100-1,300 km envelope. It excludes the Korean/offshore pathway, Soya
continuation and separately named Tsugaru outflow. Coarse atlas land clearance
passes all scenarios but cannot validate shelf location or small-island clearance.
NASA level2_F_2 covers all retained routes geographically. No source figure,
velocity field, thermal front or dated geometry is digitized. JMA seasonal
thermal-area strength is not a width, route length or occupied velocity footprint.

The naming audit is research/tsushima-current-naming-scope-audit.json. Four
source-backed missing-name proposals are added: Tsugaru Warm and Soya Warm
(Ohshima and Kuga 2023, introduction), East Korea Warm and North Korea Cold
(Yoon et al. 2016, introduction/Figure 1 caption). All retain unknown lengths,
nonranked status and independent name/layer/extent admission gates. Twelve
inventory proposals now sit outside the unchanged 100-name canonical ledger.

Coverage: 33 route candidates for 31 of 89 names, 58 awaiting routes; 30
comparison rows, three studied reaches and 2,268 editorial scenarios. Tsushima
envelope positions 14-24 are scope-sensitive comparison positions, not empirical
whole-current ranks. No canonical numeric length or published ranking changes.
Twenty-six focused tests pass; route screenshot visually inspected.

Full Chromium suite passes updated coverage, Tsushima source/scope/NASA crop,
four new inventory cards and existing seasonal/dated atlas behaviour.

## Balearic island-margin route — 2026-10-03

Garcia-Ladona et al. (1996), *The Balearic current and volume transports in the
Balearic basin*, Oceanologica Acta 19(5), 489-497, Conclusions (printed 496,
PDF page 8) supports Ibiza-to-north-Menorca shelf geography. June 1989 FE-89
survey context is retained, supplemented by Ramirez-Romero et al. (2020)
model-comparison discussion of differing regional extents. The upstream
Northern Current, its cyclonic return loop, southward channels and Algerian
eddy paths are excluded. No broader North Balearic identity merger is admitted.

OSW selects all offshore vertices and Ibiza/Menorca approach gates. The route
is approximately 400 km, with a rounded 300-400 km envelope across 54 gate and
coordinate scenarios. All clear the coarse atlas land mask, which omits small
islands here. Optional labelled island-centre points now supply orientation;
points do not enter any length, mask or state operation and are not island
outlines or clearance validation. Every candidate was regenerated after this
shared presentation change, and seasonal report digests refreshed. NASA crop
level2_C_2 covers all retained routes geographically; no physical identification.

Coverage: 34 candidates for 32 of 89 names; 57 awaiting routes. Thirty-one
comparison rows and three studied reaches retain 2,322 geodesic scenarios.
Balearic sensitivity positions 30-31 are scope-dependent, not empirical ranks.
No canonical length or published ranking changes. Twenty-seven focused tests
pass; revised map visually inspected.

Full Chromium suite passes route values, source/crop links, reviewed-width
source passages, unknown seasonal width/static map context and updated
34/32/57 coverage. No verification process remains running.


## Gaspé regional corridor — 2026-10-03

Leclercq's February 2022 UQAR-ISMER thesis, printed page 14 / PDF page 30,
places the Gaspé Current from the lower estuary near Pointe-des-Monts toward
the Magdalen Islands. Printed page 5 / PDF page 21 supplies coastal-flow,
episodic-feeder and Anticosti context. Paquin et al. (2024), section 2,
provides detachment and recirculation cautions; no model axis is digitized.
The thesis is independently accessible; access to the original blocked AMS
paper has not been recovered.

Every vertex and gate is selected by OSW. The regional corridor is approximately
500 km, with a rounded 400-500 km gate/coordinate sensitivity envelope across
54 scenarios. It excludes upstream estuary length, the north-shore feeder,
Anticosti and Chaleur recirculation, and Cabot/Scotian continuation. All scenarios
clear the coarse mask, which cannot validate fine coastal or island clearance.
A labelled Magdalen centre point supplies orientation only. Legend placement
was corrected and inspected. NASA level2_B_1 is geographic context.

The separately reported typical width range of 10-20 km does not buffer this
route or establish summer/winter length changes. No midpoint, confidence
interval or annual extrema are inferred. Coverage is 35 candidates for 33 of
89 names, with 56 awaiting routes; 32 comparison rows and three studied
reaches contain 2,376 scenarios. Gaspé sensitivity positions are 28-32;
these are conditional editorial ordering, not published empirical ranks.
Canonical 100 names and 11 published-ranked lengths remain unchanged.

Verification: all 39 current tests, width/section-width/seasonal validators,
length protocol audit and full Chromium suite pass. Both route and width-page
screenshots were visually inspected. Internal seven-role review records
physical boundaries, naming extent and temporal support as remaining conditions.


## Norwegian Coastal Current to Ingøy — 2026-10-03

Christensen et al. (2026), Norkyst version 3, section 1, distinguishes coastal
and Atlantic flows and supports Skagerrak-to-Barents regional geography.
Skagseth et al. (2011), Introduction paragraphs 3-7 and Figure 2, provides the
Ingøy approach context and a warning about complex bank-region pathways.
The southern route gate is Norwegian coastal geography, not the Baltic
freshwater origin used by the 2011 source. All vertices are OSW-selected.

The approximately 2,100 km route has a rounded 2,000-2,200 km sensitivity
envelope across 54 gate/coordinate alternatives. One initial coarse-land
intersection was corrected by an offshore central-coast waypoint; every retained
scenario now clears that mask. Fine coast, islands, shelf and water-mass
correspondence still require review. Fjords, offshore Atlantic branches,
West Spitsbergen and Murman continuations are excluded. The Ingøy gate truncates
a regional corridor, rather than defining the entire connected system.

The naming audit retains broad Norwegian Current as unresolved. NOAA's glossary
has no physical details sufficient to equate it with either modern named flow.
Qualitative seasonal structure is documented separately; the paper's bathymetric
slope dimension and transport-support section approximation are not admitted as
uniform current width. Hydrographic DJF differs from the velocity-table JFM;
calendar definitions must stay source-specific. Norkyst hindcast availability is
a future animation research lead, with access/license/metric review pending.

NASA level2_D_1 covers the route geographically. Conditional comparison
positions are 8-14. Coverage: 36 candidates for 34 of 89 names, 55 remaining,
33 comparison rows and three studied reaches, with 2,430 scenarios. Canonical
length ranks remain unchanged. All 39 current tests, protocol audit and full
Chromium suite pass; the enlarged-label map was visually inspected.


## Canary offshore return-flow corridor — 2026-10-03

Kounta et al. (2018), section 1, distinguishes the named northern offshore
return flow from the wider Canary Current System and places its departure
near Cape Blanc. Ibrahim and Sun (2026), section 4, supports a northern feed
region near 35 N. The selected corridor is approximately 1,700 km, with a
1,500-1,800 km rounded envelope across 54 OSW gate/coordinate alternatives.
Every vertex is selected by OSW; no source axis or model field is digitized.
The western archipelago detour is not identified as an observed fall path.

Upstream Portugal/Azores, downstream North Equatorial, Lanzarote Passage
recirculation and intermediate poleward flow are excluded. Small-island
outlines are unresolved; Madeira/Tenerife centre points provide orientation
only. All scenarios pass the coarse land-mask check; finer bathymetric and
physical-path checks remain open. NASA level2_C_3 is geographic context.

The 2023 seasonal paper names the Canary intermediate Poleward Undercurrent
(CiPU/iPUC) separately. Its proposed identity has no borrowed length or width;
alias, layer and continuation review remains open. Thirteen additions now sit
outside the unchanged canonical 100-name ledger. The scope audit also records
2015 seasonal geography and the fall-cruise October/November discrepancy.
No dated frame or annual extrema are constructed from those passages.

Coverage: 37 candidates for 35 of 89 names; 54 remaining, 34 comparison rows
and three studied reaches, containing 2,484 geodesic scenarios. Canary
conditional comparison positions are 12-18, not published uniform ranks.
Thirty-nine current tests and protocol audit pass; map screenshot inspected.

Full Chromium suite passes Canary value/envelope/source/crop, separate CiPU
proposal, updated counts/queue and existing atlas joins. No verification process
remains running.


## Portugal offshore reference corridor — 2026-10-03

Added approximately 1,400 km, with outward-rounded 1,100–1,800 km across
81 editorial scenarios. Three northern interface gates (45, 47.5 and 50 N)
use the regional chapter's geographic convention; the 35 N southern gate
uses combined-system convergence context, not a uniquely measured offshore
endpoint. All longitudes and bends are OSW choices. The nominal 47.5 N
gate is not an observed midpoint axis. No seasonal length range admitted.

Martins et al. (2002) distinguishes offshore and coastal flows. Its 36–44 N,
24–12 W statistics box is neither whole-current extent nor width; its 670 km
coastal drifter displacement cannot become the offshore length. Separate
coastal names and undercurrent aliases remain in the scope audit for review.
No canonical identities or numeric measurements added. Source edition year
requires confirmation: repository copyright 2004 is not publication dating.

Candidate input/report/map, naming-seasonal audit and NASA level2_C_2 context
are available locally. Coverage is now 38 routes for 36 of the remaining 89
names, with 53 awaiting routes and 2,565 audited editorial scenarios.

Verification: protocol audit and 37 focused current tests pass; full Chromium
atlas suite passes revised route values, source/NASA crop, counts and ordering.
A focused seasonal-page check verifies static source wording, disabled Portugal
playback, unknown seasonal length and narrow layout. Map screenshot inspected.
Internal seven-role review records 21 findings with zero P1; scientific and
publication gates remain open. No verification process remains running.


## West Spitsbergen approach and northern branch inventory — 2026-10-03

Added an 800 km editorial corridor with 600–900 km outward-rounded envelope
across 81 gate/offset scenarios. The southern departure approaches at
72.5/73/73.5 N are selected within regional Barents bifurcation geography,
not source-defined exact origins. Northern gates near 79.5–79.8 N stop in
the branch region. Excludes the Front Current feeder, Barents eastward
inflow, recirculation, shelf/fjord intrusions and downstream named branches.
All vertices are OSW choices; no shelf isobath or observed axis digitized.

Goszczko et al. (2018) supplies regional continuation context; Menze et al.
(2019) supplies northern branching context from summer surveys. Dundas and
Fer (2026) distinguishes source-specific core/front branches and limited
glider season coverage. Sampling regions, transect divisions and transports
are not lengths/widths. Spitsbergen Atlantic alias/extent relationship remains
unresolved; no second route copied onto that ledger name.

Svalbard, Yermak and Yermak Pass branches are now separately proposed names,
with layer, separation/rejoin, alias and time gates. The summer composite
does not establish all three at every time. No parent length borrowed.
Canonical names and numeric measurements unchanged; 16 proposals remain
outside the 100-name ledger. NASA level2_C_1 is geographic context only.
Coverage: 39 candidates/37 names/52 awaiting, 2,646 editorial scenarios.

## Azores route and Aleutian naming review — 2026-10-03

Azores candidate retained: about 3,600 km, with a 3,300–3,700 km editorial
scenario envelope from 81 scenarios. This is the source-scoped eastward
reference corridor, not an observed velocity axis. The countercurrent and
southward branches remain separate. Width and annual changes retain the
previous scoped evidence rules. Coverage is 40 candidates / 38 names / 51
awaiting, with 2,727 scenarios; no new published ranked length admitted.

The next naming review distinguished eastward Aleutian/Subarctic Current from
westward Alaskan Stream using the AMS definition and NOAA/source literature.
The Stream is a proposed 17th addition, outside the 100-name release. Aleutian
whole-current length, width and seasonal ranges remain null: source definitions
provide relationships but no defensible endpoint coordinates. Its planning
queue now points to the scope audit and a specific velocity/front gate review.
Three source-described Aleutian feeder/branch links extend the Beck research
connectivity catalog to five typed relationships. Feeding, branching and
continuation remain separate predicates; naming distinction and regional
membership never become implied physical flow links. No lengths or widths
are transferred across them.

## Antilles modern regional scope — 2026-10-03

Meinen et al. (2019), read through the NOAA repository PDF after the publisher
returned 403, supports mean northward flow at 26.5 N during 8 May 2005–
23 November 2015. This does not invalidate the older, geographically distinct
surface-flow assessment or define whole-current endpoint coordinates. The
route remains unknown, with a specific naming/layer/endpoint next action.
The fixed 49.4 km coast-to-site-B transport integration span is not admitted as
current width. Annual dimensions and seasonal route playback remain unknown.

A source-scope note exposes this modern-versus-historical distinction in the
dashboard without modifying the frozen release's claims. Its observation end
date is explicitly regional study coverage, not a whole-current monitoring date.
Source notes have their own evidence light; they do not activate route, width
or time-frame capability. Width source review now covers two names without a
comparable numeric width, with 91 names still unassessed; eight scoped records
for six names and the one derived-width candidate remain unchanged.

## Angola inventory gap — 2026-10-03

Angola Current is absent from the frozen 100-name ledger and is now the 18th
source-backed proposed addition. Kopte et al. (2017) regional observations and
Korner et al. (2023) circulation context support the identity. Whole-current
endpoints, physical width and annual dimension ranges remain unresolved.
The 75 km span of the fixed transport integration box is not admitted as width;
ecosystem bounds and collection metadata bounds do not become a route or footprint.
PANGAEA.868684 supplies eight child-data leads under CC-BY-3.0; metadata was
read, sample data was not acquired. The audit records month precision and
remaining layer/time/gate requirements. Canonical counts and route coverage
remain 100 and 38 of 89 respectively.

## South Atlantic western intermediate reach — 2026-10-03

Boebel, Schmid and Zenk (1999), section 3.5, supports an intermediate-depth
regional context near 40 W, 39 S and a farthest RAFOS reach at 16 W, 43 S.
OSW connects those anchors with a declared western reach: approximately
2,100 km, with 81 editorial scenarios spanning 2,000–2,300 km. The shapes
do not reconstruct float trajectories or the documented large meanders.
The float-reach gate is not an endpoint of the whole South Atlantic Current.
Eastern continuation, recirculation and SAC/ACC exchange remain unresolved.

This fourth studied reach stays outside the 37-row reference-route order.
Coverage is 41 candidates for 39 of 89 names, with 50 awaiting routes and
2,808 scenarios. Width and annual ranges remain unknown. The NASA level2_C_5
crop covers every retained display scenario; that overlap is navigational
context, not identification of a subsurface current in surface animation.

## West Australian naming and measurement support — 2026-10-03

The AMS definition supports broad offshore northward flow distinct from coastal
southward Leeuwin. Ridgway and Condie (2004) coastal-system dimensions are not
transferred. D’Adamo and Onton (2003) seasonal context inherits Buchan and
Stroud (1993) / US Navy (1976) atlas patterns, with probable-flow legend entries;
the original atlas was not read and no seasonal geometry is admitted. Search
metadata dated the government report differently; its front matter establishes
15 July 2003. A 1977 title/abstract is a historical naming lead only because
full publisher access failed. The route strategy now requires scope resolution
and a layer/time-defined offshore corridor before selecting endpoints or one
axis. A dashboard source note exposes the distinction; it lights no route,
physical width or seasonal-frame category. Route coverage remains 39/89.


## North Cape Northern-branch Western Hopen reach — 2026-10-03

Full primary Morozov et al. (2017) text and inspected Fig. 1/Fig. 9 identify the
Northern branch near western Hopen Deep and the LS05 frontal/core neighborhood.
IMR/PINRO (2009), hydrographical conditions pp. 20–21, independently distinguishes
Northern versus Central branch geography. OSW selects a southern Hopen approach
near 30 E, 75 N and a rounded LS05 neighborhood near 28.5 E, 77 N, with intermediate
western-margin waypoints. These are declared study-area gates, not whole-current
endpoints or a digitized source axis. The transverse LS05 ship track is excluded
as a longitudinal route. Partial cyclonic recirculation is not added as a loop.

Candidate length: approximately 200 km; rounded 200–300 km envelope across 81
editorial cases. Classified as studied reach and excluded from comparison order.
All 81 coarse-ground checks pass; finer island/bathymetric correspondence remains
unverified. Nominal and all cases cross BPLR diagram state only. NASA level2_D_1
and level2_E_1 cover the displayed reach in all cases; geographic context does not
identify the actual current, dated observation or vertical layer.

Coverage: 42 candidates/40 of 89 names; 49 awaiting routes, 2,889 sensitivity
cases. Thirty-seven comparison rows plus five studied reaches. State inventory
now has 91 candidate/state pairs. Width record remains a separate approximately
8 km Gaussian scale, not a route buffer. Canonical ledger and ranks unchanged.
Eighteen focused route/protocol/state/dashboard tests pass; focused browser
inspects card, map return, width definition and static seasonal-context display.
Route screenshot inspected for map/labels; source PDF receipt is hashed in audit
without redistributing its figures or document.


## Atlantic Equatorial Undercurrent subsurface reach — 2026-10-03

Full primary Napolitano et al. (2022), doi:10.1029/2021JC017999, institutional
IRD PDF, supports the equatorial jet's eastern Sao Tome interaction and branching
near 6 E; introduction distinguishes termination-site geography between 5 E and
the continental margin. Full publisher Hormann and Brandt (2007),
doi:10.1029/2006JC003931, section 2.3.1.1 paragraph 14 supports the 35 W observed
equatorial current section and approximately 100 m mean core context.

OSW selects a truncated 35 W to 5 E pre-island reach: approximately 4,500 km,
rounded 4,300–4,600 km envelope over 81 editor-selected shapes/offset cases.
No upstream North Brazil retroflection path, island branching, westward return
or modeled eddy trajectory is included. No depth-uniform or single dated axis
is claimed. Published transport changes and vertical thickness are not horizontal
width evidence; annual dimensions remain unknown. Classified studied reach and
excluded from reference-route length ordering, including whole Pacific EUC.

All cases pass coarse land checks and cross ETRA, GUIN and WTRA diagram states.
NASA level2_C_4 covers the whole displayed reach in all cases; surface movie
context does not identify a thermocline current or match observation dates.
Coverage: 43 candidates/41 of 89 names, 48 awaiting, 2,970 scenarios; 37
comparison rows and six studied reaches. State inventory has 94 candidate/state
pairs. Source scope note refreshes dashboard evidence. Canonical ledger and
published ranks unchanged. Eighteen route/protocol/state/dashboard checks and
focused browser map/card/return/scope checks pass; figure visually inspected.


## Mediterranean Undercurrent lower-core reach — 2026-10-03

Full primary Bower, Serra and Ambar (2002), doi:10.1029/2001JC001007,
Introduction/Data/Results [2]–[7] and [19]–[25], supports the AMUSE launch
neighborhood at 36.5 N, 8.5 W, Cape St. Vincent turn and western-slope region
between 37 N and 38.2 N. The lower-core nonmeddy selection is 950–1250 dbar;
pressure is not equated with one fixed depth. May 1993–March 1994 describes
float deployment, with tracks up to 11 months; no precise composite last date
is inferred. WHOI Bower Lab data/report links are available for future trajectory
acquisition, not yet a parsed dataset in this candidate.

OSW selects a coarse offshore reach from the launch neighborhood around the
cape to an editorial 38.2 N western-slope longitude. Approximate length 300 km,
rounded 200–300 km envelope from 81 shapes/offsets. Excludes Gibraltar density
flow, interior water spreading, meddy loops, Estremadura branches and uncertain
farther-north continuity. Studied-reach class excluded from length ordering.
A Mediterranean salt tongue or isolated RAFOS track is not a whole-current axis.

Existing 30 km one-sided ensemble span and 10 km geostrophic survey band remain
separate; no annual 10–30 km range or uniform route buffer. Source [22] also
reports an at-least-50 km mean northward-flow band on the western slope; recorded
as additional evidence pending metric/boundary review, not silently admitted as
full width. No numerical width inventory change.

All cases pass coarse-ground checks and cross CNRY diagram state. NASA
level2_C_2 (among other crops) covers the full displayed reach in every case;
this does not identify subsurface flow in the surface movie. Coverage now
44 candidates/42 of 89 names, 47 awaiting routes, 3,051 scenarios, 37 comparison
rows and seven studied reaches. State inventory now has 95 candidate/state
pairs. Canonical ledger and ranked estimates unchanged. Nineteen focused
route/protocol/state/dashboard tests and browser checks pass; all 56 state
inventories/95 pairs checked. Route screenshot visually inspected.


### 2026-10-03: Atlas selection opens an inline visual card

Current selection now fits the selected editorial route and opens its visual map card beside the global OSW map, without changing the fragment or scrolling away. Multiple components have individual selectors; the full route card retains its permalink, measurements, source citations and return navigation. Pending routes show an unresolved locator notice. Eddy selections show their existing source scope and record link in the same panel. Global view clears the panel. Desktop cards scroll internally; mobile cards stack below the map. No geometry, measurement, season or scientific-status data changed.

Verification: reference-route atlas browser checks passed all 100 current options, component switching, in-place selection, map-card links and return, all 140 eddy record links, zoom/pan/keyboard and 320px reflow. Shared update-light and direct route-navigation checks also passed. Visual review: figures/reference-route-inline-card-review.png.


### 2026-10-03: Atlantic South Equatorial Undercurrent studied reach

Full primary Fischer et al. (2008), doi:10.1029/2008GL035753, supports float-study longitude context 35 W to approximately 10 W, with floats parked at 200 m and mean section cores around 3 S westward / slightly south of 4 S eastward. The declared smooth editorial route measures approximately 2,800 km with 2,700–2,900 km scenario envelope across 81 cases. Actual western meanders, recirculation loops, NBUC feeding legs, surface drift and uncertain eastern fate are excluded. The paper's greater-than-2,500 km sampling span is retained separately in the scope audit; it is not admitted as whole-current length.

Coverage: 45 candidates / 43 of 89 names / 46 pending / 3,132 scenarios; 37 comparison rows and eight studied reaches. State join: 56 states / 97 candidate-state pairs / 40 states with declared crossings. Width review retains 3–6 S as a sampling band, not numeric width: nine scoped records across seven names, one derived candidate, three sources-reviewed nonnumeric decisions and 89 unassessed. Whole-current dimensions and annual ranges remain unknown.

Verification: 28 focused route/protocol/state/dashboard/width unit checks; Atlantic SEUC inline card / full card / mobile browser check; all-state browser check with optional-data 503 fallback. Source-scope review and visually inspected figure recorded separately. No new canonical length, width, observation date or seasonal axis admitted.


### 2026-10-03: Atlantic North Equatorial Undercurrent section-context reach

Relevant primary sections of Bourles et al. (1999), doi:10.1029/1999JC900058, and Burmeister et al. (2020), doi:10.1029/2020GL088350, support separate western 35 W and central 23 W observational neighborhoods near 5 N. The connecting smooth route is editorial, not a continuous observed axis. Approximately 1,300 km; 1,200–1,400 km selected-scenario envelope; 81 cases. Source recirculations, surface NECC, unresolved eastern filaments and termination are excluded. Western density-core and central 65–270 m definitions remain separate; no uniform layer or simultaneous trajectory asserted.

Historical source reports two-degree latitude width at 35 W in February 1993 and April 1996. Angular value, center and month precision retained in source audit for boundary/extraction review; numeric km inventory admission pending. Model half-width, moving integration limits and fixed 4.25–5.25 N transport box are not substituted for physical boundaries. No seasonal dimension animation derived from weak seasonal transport or sporadic events.

Coverage now 46 candidates / 44 names / 45 pending / 3,213 scenarios; 37 comparison rows and nine studied reaches. 56 states / 98 route-state pairs / 40 states with routes. Width coverage: nine numeric records across seven names, one derived candidate, three nonnumeric reviews, one historical mention pending definition review and 88 unassessed. Verification: 28 focused units, NEUC browser card/preview/width/provenance checks and all-state browser checks including 503 fallback and mobile. Figure inspected; canonical ledger unchanged.


### 2026-10-03: Month-dated historical angular section widths

Width protocol v1.4 adds source-reported angular section spans with month
precision. Bourles et al. (1999), section 4.8, reports two-degree latitude width
at 35 W centered at 5 N in February 1993 and April 1996. Both convert to about
221.1656 km using WGS84, rounded to approximately 220 km. Computational
normalization around the center does not establish observed edge coordinates.
Exact days, lateral threshold and uniform depth bounds remain unknown.

Two separate historical records replace the pending width mention. They are
not seasonal states, annual extrema or whole-current widths. The explorer
labels them Historical section observation, retains their months, disables
seasonal playback and displays static route context. General protocol hashes
and the Gulf Stream derived-series metadata are refreshed; its 17 numeric
frames are unchanged by this metadata update.

Current width coverage: 11 scoped numeric records / eight current names,
one derived series candidate, three reviewed nonnumeric decisions, zero
pending historical mentions and 88 unassessed. Route coverage remains
46 candidates / 44 of 89 names / 45 pending routes. Canonical ledger unchanged.
Focused verification: 29 unit checks; historical width/route browser check;
17-frame section-width provenance checker. Browser integration results and
role review are recorded in the corresponding verification notes.


### 2026-10-03: Ligurian coastal studied segment and parent navigation

Poulain et al. (2012), doi:10.4430/bgta0052, supports surface-flow context from
Genoa through Imperia to Menton–Nice. The Ligurian name remains the ledger's
editorial Northern Current segment convention; Marine Regions MRGID 3357 is a
Proposed standard naming entry and does not define endpoints. Declared offshore
Genoa–Menton/Nice truncations yield approximately 100 km with 100–200 km
scenario envelope across 81 cases. This is a studied segment, not complete
named-current length, a drifter track or shelf-break axis. Source data combine
first-metre CODE and wind-sensitive first-10–20-cm ARGOSPHERE sampling with
intermittent summer/fall observations. No continuous annual coverage inferred.

Both the inline atlas preview and full visual card link to the broader Northern
Current card. Parent metadata is checked against the unchanged canonical ledger;
overlapping parent/segment lengths must not be summed. Whole-parent seasonal
widths are not copied. Imperia 20–30 km coast-distance limits and Menton–Nice
15–35 km profile-band distances remain pending boundary-definition review.

Coverage: 47 route candidates / 45 of 89 names / 44 awaiting routes /
3,294 scenarios; 37 comparison rows plus ten studied reaches. All 56 states and
99 route-state pairs validated, including optional-data 503 fallback and mobile
navigation. Width inventory: 11 scoped numeric records / eight names, one derived
candidate, three nonnumeric reviews, one profile mention pending review and
87 unassessed. Thirty focused unit checks and Ligurian browser checks pass.
The generated figure was inspected and label size adjusted for readability.


## 2026-10-03: East Adriatic source-convention corridor

A new Otranto-to-Istria editorial offshore corridor measures approximately
800 km, with a 700–800 km envelope across 81 declared path/endpoint cases.
Its unrounded WGS84 path is 755.894 km; the source's 800 km basin dimension
was not used as current length. All cases avoid the coarse atlas land mask;
islands, channels and bathymetric fidelity require finer review.

The East/Eastern Adriatic alignment is editorial under the northwestward
eastern-coast surface-circulation convention. Dalmatian-name synonymy remains
unresolved; western return flow and recirculation loops are excluded. There
is no diagnosed continuous core, admitted whole-current length, numeric width
or seasonal path. Publisher backgrounds were read; original 2002–2003
measurement full text was unavailable during this source audit.

Coverage: 48 candidates / 46 of 89 names / 43 pending / 3375 scenarios;
38 comparison routes and ten studied reaches; 100 candidate/state pairs
across 40 of 56 states. Canonical current ledger unchanged.


## 2026-10-03: Black Sea Rim closed reference circuit

Declared counterclockwise circuit: approximately 2100 km, 1900–2200 km
across nine closed shape/longitude cases. Every case preserves an arbitrary
repeated anchor and orientation; no current origin, termination or parcel
travel time inferred. General surface geostrophic context is 1999–2009;
vertices are editorial, not extracted from the mean field. Seasonal continuity
and fine bathymetry remain review gates. Interior gyres and coastal eddy loops
are excluded.

Raw MEDI (nine cases) and REDS (four cases) display-mask contacts are retained
in the candidate and state-join excluded-contact audit, with declared geographic
reasons. The Black Sea has no dedicated state in this display inventory;
these contacts do not become state navigation links. The measured route is
not altered to erase the raw associations. Protocol v1.1 records this policy.

Coverage: 49 candidates / 47 of 89 names / 42 pending / 3384 scenarios;
39 comparison routes plus ten studied reaches; 100 admitted display-route/state
pairs and two excluded raw contacts. No canonical current dimensions changed.


## 2026-10-03 · East Greenland coastal studied reach

Added an editorial 66 N–Cape Farewell route: approximately 800 km,
800–900 km over 81 declared scenarios (raw nominal 838.753 km). This reach
is separate from the source approximately 1000 km shelf survey description
and is excluded from the main reference-route comparison ranking. The weak
68 N identification, 63 N merger, offshore diversions and West Greenland
continuation remain explicit scope limits. Canonical ledger unchanged.

The local Cape Farewell 30 km width at 15% maximum inner-jet velocity remains
a single campaign section, without route buffering, annual extrema, exact
section dates or fixed depth bounds. Atlas selection opens its route image;
the seasonal explorer shows static route context and disables playback.

Coverage: 50 candidates / 48 of 89 names / 41 pending / 3465 scenarios;
39 comparison routes and 11 studied reaches. State join: 101 candidate-state
pairs across 40 states. Width inventory: 13 scoped numeric records / 10 names.

Verification: protocol conformance, 34 focused unit tests, EGCC desktop/mobile
width and route browser checks; visual crop inspected. Seven-role review has
21 findings, 0 P1, 3 addressed P2 and 18 P3; independent scientific admission,
finer bathymetry and continuity review remain pending. See
`signals/roles/check/egcc-reach-width-roles-check-2026-10-03.md`.


## 2026-10-03 · Atlas family and system navigation

The custom atlas now exposes seven catalog family/system records with 17
immediate component links, including nested equatorial families and the Gulf
Stream System. Selection fits and highlights component routes or name
locators, with no connecting line, aggregate length or family footprint.
Each component returns to its family/system record through explicit links.
Incomplete coverage and nonadditive scopes are stated in the preview.

Source-reported lengths remain available even when an editorial route card
is pending; these cases are no longer labelled unknown length. Route coverage
remains 50 candidates for 48 of 89 names, 41 pending. Browser verification
covers all seven records and 17 links, keyboard descent, return, 320 px
reflow and existing 100-current/140-eddy atlas behavior. Roles review:
`signals/roles/check/atlas-component-navigation-roles-check-2026-10-03.md`.


## 2026-10-03 · Norwegian naming and branch inventory

Reviewed NOAA Norwegian Current / Spitsbergen Atlantic Current definitions
against Baumann et al. (2026), Ocean Science 22, 17–29, introduction and methods.
The ambiguous Norwegian name is not automatically Norwegian Coastal Current
or Norwegian Atlantic Current. Spitsbergen Atlantic Current is not declared
an alias of West Spitsbergen Current. Two source-scope audits retain these
uncertainties and no neighboring length, width or route is transferred.

Proposed Norwegian Atlantic Current and its Slope and Front branches as three
separate identities beyond the canonical 100 names. Proposal inventory now
contains 21 additions. The source's heat-budget box and static mean core are
not annual or whole-current dimensions for the unresolved Norwegian name.
No new canonical measurement or current identity admitted.

All 14 current source-scope summaries now appear in the selected atlas preview,
with audit receipts, source links and related-record links where declared.
Related IDs are validated against released identities. Verification: 20 focused
unit checks, all 14 scope previews at 320 px, both Norwegian/Spitsbergen
navigation cases, three proposed cards, and family navigation regression.
Route coverage remains 50 candidates / 48 of 89 names / 41 pending.
Role receipt: signals/roles/check/norwegian-naming-scope-roles-check-2026-10-03.md.


## 2026-10-03 · New Ireland subsurface regional reach

Added New Ireland Coastal Undercurrent east-coast editorial reach:
approximately 400 km, 300–500 km across 81 scenarios, raw nominal 401.074 km.
The route excludes Solomon Strait inflow across the basin, New Britain/St
Georges branches, Bismarck continuation, retroflection and downstream EUC
length. It is a studied reach, excluded from the main comparison ordering.

Grenier et al. (2011), doi:10.1029/2011JC007477, relevant introduction,
ORCA025-G70 description/validation and pathway text read. The source model
closes St Georges Channel at its resolution; this is not a physical channel
absence. Model fields and trajectories not digitized. NASA links provide
geographic surface context, not undercurrent identification. An initial
closer-island scenario contacted coarse land; central vertices were moved
0.2 degree east, then all declared cases regenerated and checked.

Coverage: 51 candidates / 49 of 89 names / 40 pending / 3546 scenarios;
39 comparison routes, 12 studied reaches, 102 candidate-state pairs across
41 states. Source scope notes now cover 15 names. Canonical ledger unchanged;
width and annual margins remain unknown for this NICU reach.

Verification: 15 focused unit checks, protocol audit, NICU visual/card/mobile
and static-season check, all 102 route/state navigation pairs. Regional image
inspected. Seven-role review: 21 findings, 0 P1, 2 addressed P2, 19 P3;
independent scientific admission remains open. Receipt:
`signals/roles/check/new-ireland-undercurrent-reach-roles-check-2026-10-03.md`.


## 2026-10-03 · New Guinea undercurrent reach and source seasons

Added a northern PNG subsurface regional reach from an offshore
Vitiaz-downstream approach to the 142 E, 2.5 S mooring neighborhood:
approximately 600 km, 500–700 km over 81 scenarios (raw nominal 600.298 km).
Vitiaz passage itself, upstream Solomon Sea branches, New Britain/St Georges
branches and downstream cross-equatorial EUC connection are excluded. This
studied reach is not a whole-current length and remains outside the main
comparison ordering. Local 150–250 m core support is not a fixed-depth axis
along the entire route; surface monsoon reversal belongs to another current.

Ueki et al. (2003), doi:10.1029/2002JC001611, relevant introduction, Data,
Table 1 and Results inspected. Source seasons are explicitly boreal:
winter January–March, summer July–September, fall October–December. Protocol
v1.2 preserves these source month windows independently of latitude and rejects
invalid month receipts or promotion to annual geometry. Static source seasons
and local velocity changes cannot supply seasonal length/width maps.

Impact: geodesic algorithm, rounding and comparison groups unchanged; all 52
candidates re-audited. Existing numeric candidate files and seasonal frames
not revised. Canonical ledger SHA unchanged. Coverage: 52 candidates / 50 of
89 names / 39 pending / 3627 scenarios, with 39 comparison routes and 13 studied
reaches. State join: 103 candidate-state pairs across 41 states; 16 scoped
current source reviews. Width coverage and proposal counts unchanged.

Verification: 36 focused tests; NGCU direct visual-card/season-label/mobile
browser checks; all 103 route/state navigation pairs. Regional crop inspected.
Seven-role review: 21 findings, 0 P1, 2 addressed P2, 19 P3, independent science
gates open. Receipt: signals/roles/check/new-guinea-undercurrent-seasons-roles-check-2026-10-03.md.

## Red Sea REDSOX reported reach — 2026-10-04

Peters et al. (2005), section 5a, supplies an approximately 130 km winter
velocity-supported descending-plume reach from Bab el Mandeb. It is retained
as a source-reported local reach, not a reconstructed geodesic axis or ranked
whole-current estimate. The velocity quantity is plume speed magnitude above
0.2 m/s; 100–250 m describes layer thickness, not fixed depth bounds.

Separate channel descriptions of 130 km (Peters abstract), 120 km (Peters
section 3a) and 115 km (Bower section 3a) have unresolved geographic conventions.
Their spread is not an uncertainty interval. The approximately 5 km channel
width is not a current velocity-boundary width. Northern, southern main and
southern gully components retain local source identities pending admission.

Audit: `research/red-sea-redsox-branch-reach-scope-audit.json`. Compatible axes,
paired current edges, exact occupation support and independent identity review
remain required. No route candidate added: current totals are 62 candidates /
59 of 89 names / 30 pending / 4,113 scenarios. The canonical ledger is unchanged.

