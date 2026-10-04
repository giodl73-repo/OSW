# Ocean motion almanac

This is a source-backed naming, measurement, and geography ledger, not a global
census. The browser page reads versioned research files. It also uses
the source-evidence and property ledgers embedded in the object/state crosswalk:

The proposed citable dataset and public presentation contract is in
`../plans/ocean-motion-atlas-publication.md`; the existing public-release
reconciliation gate still controls external publication.

The generated `release/v0.1.0/` candidate package normalizes 318 stable object
IDs, 5,761 typed relations, 30 source-scoped numeric measurements, 247
movie navigation records, 100 current length assessments, 877 state-to-NASA-crop
display overlaps, and 92,891 dated NOAA observations across 12 sample
days. Run `py analysis/build_ocean_motion_release.py` and
`py analysis/check_ocean_motion_release.py` from the repository root. The
package has copied source ledgers, checksums, CSV, JSON, role-labelled GeoJSON,
OSW taxonomy rules, and a coverage report. `object.html?id=current:acc` is a
package-backed object page, and `movies.html` lists every NASA crop with
source-labelled geographic navigation. The main almanac still presents richer
source-specific rows.

`reference-routes.html` is a separate working review surface for OSW approximate
route lengths. Its catalog covers all 89 currents without published ranked
estimates. Twenty-eight currents currently have thirty route candidates: the East
Australian coherent jet (about 2,100 km), the source-defined Agulhas Return
extent (about 4,600 km), the regional outer East Greenland corridor (about
2,700 km), the Brazil poleward branch (about 3,200 km), the Benguela shelf-edge
branch (about 2,500 km), the Agulhas regional extent to retroflection (about
2,000 km), and two separate studied reaches: Agulhas Return (about 3,300 km)
and the North Atlantic DWBC between 47 and 24.5 degrees N (about 4,100 km).
Three Australian components use explicit seasonal/naming conventions:
Leeuwin into the Bight (about 2,900 km), South Australian (about 800 km), and
Zeehan (about 800 km). These components must not be added or substituted for
the separate 5,500 km source-reported system estimate: transition gates differ.
NOAA glossary conventions add North Pacific (about 4,700 km, 3,900–5,000 km)
and Kuroshio Extension (about 1,400 km, 1,100–1,600 km). The North Pacific
candidate records the contrasting AMS western-origin convention and uses an
explicit date-line policy for geodesics, map display and periodic joins.
North Atlantic's British Isles approach convention measures about 3,300 km
(3,100–3,500 km); Alaska's northward regional branch measures about 1,400 km
(700–1,700 km), excluding the Alaskan Stream and nearshore Alaska Coastal
Current. Sources define regions and current identity, while OSW chooses the
drawn vertices and regional terminal gates.
Mediterranean regional conventions add the Northern Current (about 700 km,
600–800 km) and Algerian Current (about 900 km, 600–900 km). Their exact
gates are OSW choices; the source surveys do not observe these complete routes.
Detached eddies and downstream branches are excluded.
Somali seasonal components add winter southward flow (about 1,500 km,
1,100–1,800 km) and the June–July southern coastal limb (about 600 km,
500–700 km). These are distinct seasonal scopes, not one annual route;
Great Whirl and Southern Gyre circuits are excluded.
The Labrador main offshore regional branch measures about 2,100 km
(1,800–2,400 km), from southern Davis Strait to the Grand Banks tail.
The West Greenland northward shelf-break branch measures about 1,100 km
(900–1,300 km), excluding the separate coastal current and westward branch.
A proposed-additions section records the missing Mozambique Current name,
with evidence for episodic continuous flow and eddy-dominated regimes.
The separate West Greenland Coastal Current is also proposed for admission,
with shelf-branch scope and no borrowed offshore length. Both additions remain
outside the 100-name ledger and 89-record queue pending review.
The dated source thermal-plume extent is not a persistent current length.
Hiri adds a broad regional convention from the Australian boundary around
the Gulf of Papua entrance to a Louisiade approach (about 1,900 km,
1,900–2,500 km). Narrower naming conventions remain unresolved. Three more
proposed additions record Gulf of Papua Current, North Queensland Current
and Great Barrier Reef Undercurrent, with explicit system/member/layer review
gates. There are now eight proposed additions outside the canonical ledger.
Western Adriatic adds a near-surface Italian-coast corridor from a Po-region
approach to western Otranto (about 700 km, 700–800 km), with OSW-selected
gates. Deep dense-water branches, gyre loops and local Gulf of Manfredonia
recirculation are excluded. Source basin boundaries do not prove current
termination, and the route is not an observed drifter track.
Guinea adds a Cape Palmas approach to the Togo-Benin weakening region
(about 1,200 km, 1,000–1,200 km), using summer geography with editorial
vertices and gates. This is not its full extent. Guinea Counter Current and
Guinea Under Current are proposed distinct layer identities with null lengths.
Oyashio adds a south-of-Bussol first-intrusion branch (about 1,000 km,
700–1,200 km), with southern gates informed by seasonal temperature indices
at 100 m. These gates do not trace a velocity core. East Kamchatka and
offshore/eastward continuations are excluded; 40 N is an editorial intermediate
gate, not an annual mean.
North Brazil adds a surface branch to a regional retroflection approach
(about 2,200 km, 1,800–2,500 km), excluding its upstream undercurrent,
offshore return branch and ring tracks. The Guiana planning entry now
requires naming-scope resolution before a separate route; its audit is
`../research/guiana-north-brazil-naming-scope-audit.json`.
Caribbean adds a regional westward corridor (about 2,800 km, 2,500–2,800 km),
stopping before the northward Yucatan Current. Mindanao adds a near-surface
Philippine boundary branch (about 1,000 km, 800–1,200 km), with separate
model-derived mean/May/September northern gate conventions. These are
editorial paths, not recovered drifter or seasonal model axes.
Baffin adds a summer external coastal reach (about 1,200 km, 1,100–1,300 km),
excluding Lancaster intrusion and retaining the study bounds as partial.
Irminger adds the northward ridge-flank branch (about 1,200 km, 700–1,400 km),
excluding Greenland return and the separate North Icelandic continuation.
North Icelandic Irminger Current is a third proposed inventory addition; its
identity does not establish one fixed upstream water-parcel connection.
The four studied reaches are excluded from reference-route ordering. There
are 50 currents awaiting routes. The South Atlantic western intermediate reach
is approximately 2,100 km (editorial envelope 2,000–2,300 km), with no
whole-current endpoint or seasonal dimension claim. Overlapping rounded scenario envelopes have
explicit position sensitivity and links to the overlapping routes; those
position bounds are conservative, not statistical rank intervals.
These are editorial route measurements, not canonical length
admissions; the eleven-value published ranking is unchanged. The page displays
paths, scenario ranges, scope, source, and atlas/NASA navigation links. It is
part of the full local review tree and is not included in the isolated screened
export. Regenerate candidates with
`python analysis/build_current_reference_path_candidate.py --input <candidate-input>`
and index them with `python analysis/build_current_reference_path_catalog.py`.
The complete 89-record queue also has a primary construction strategy from
`../research/ocean-current-route-strategy-input.json`: basin-family splitting,
system graphs, continuity hypotheses, seasonal paths, dated geometry, naming
scope, layer-specific routes, section expansion, surveyed reaches or regional
gate construction. This is an OSW planning crosswalk linked to the existing
motion taxonomy, not an official physical classification. Every record retains
its ledger kind, source scope and next action. Strategy/search/coverage filters
and known component links support the full queue. Missing basin-member records
are explicitly distinguished from absence of the flow. The builder rejects
incomplete/duplicate assignments, undefined strategies, stale evidence/ledger
bases and a single reference length assigned to a cross-basin family.

- `../research/ocean-current-almanac.json` contains major named currents and
  source-published length claims. Null `length_km` means unranked, not zero;
  a separately reported `length_lower_bound_km` remains unranked. A reported
  system extent is admitted only with a link and a plain statement of what its
  source counts as the current. Two Azores records carry a separate 2009
  meridional-section observation at 24.5°W: latitude band, approximately
  110 km width across the section, and eastward or westward transport in Sv.
- `../research/ocean-current-length-evidence.json` materializes a rank decision
  and evidence class for every current. Regenerate it with
  `py analysis/build_ocean_current_length_evidence.py`. The browser filter
  exposes published estimates, bounds, hypotheses, sampled reaches, section
  observations, and records without numeric length. The Antarctic Circumpolar
  Current retains NASA/JPL's separate approximate 21,000 km account alongside
  the ranked paper's 25,000 km estimate; neither source defines a precise
  common reference path, so the variant is shown without replacing the rank.
  A 2005 oceanography thesis supplies an approximate 6,000 km extent for the
  broad Humboldt Current belt from southern Chile toward northern Peru and
  the Galápagos. It enters the system-extent ranking with that scope stated;
  it is not a measured Peru Coastal Current core length.
  Grenier et al. (2011) describe the Pacific Equatorial Undercurrent's
  approximately 14,000 km pathway from north of Papua New Guinea to South
  America. It is ranked as a Pacific basin-wide subsurface current, not as a
  cross-basin family length. A separate approximately 13,000 km published
  account remains a scope-specific variant.
- `../research/ocean-current-gate-distances.json` records the source gates,
  WGS84 direct-gate calculations, and rounded geographic floors for the five
  derived lower bounds. They are conditional on approximate source regions,
  not measured current paths. Regenerate with
  `py analysis/build_ocean_current_gate_distances.py`. The East Greenland
  Current uses the 78.5°N Fram Strait section and 59°N Cape Farewell boundary
  in Schiller-Weiss et al. (2023), correcting an earlier 81°N gate that was
  only the northern edge of the wider strait.
- `../research/ocean-current-illustrated-spans.json` gives all 98 currents a
  separate cartographic-span decision. A credited map service publishes 73
  historical current arrows at four display widths; 61 map to 27 ledger names.
  The companion polyline layer returned zero records on 2026-09-29. For each
  arrow, OSW takes half the WGS84 geodesic perimeter of its narrowest polygon
  as a reproducible illustrated-span proxy. The browser orders the longest
  single arrow for 24 mapped non-family names; three multi-basin family names
  and 71 names without source arrows remain unranked. This metric measures
  drawn symbols, not current lengths or physical lower bounds. The four-width
  range captures drawing-width sensitivity only; it is not a confidence
  interval. Regenerate with
  `py analysis/build_ocean_current_illustrated_spans.py` and keep the source
  GeoJSON digest consistent with the state-arrow join.
- `../research/ocean-current-nasa-crosswalk.json` classifies all 98 current
  records by NASA relation: seven directly named or described flows, three
  independently sourced related currents, and 88 regional movie gateways.
  Regenerate it with `py analysis/build_ocean_current_nasa_crosswalk.py`.
  A Portugal Current record carries a 2009 zonal-section longitude band at
  37°N and southward transport with source uncertainty. The same study locates
  the Canary Current crossing at 29°N and reports separate thermocline and
  intermediate-layer transports. Those section values are not whole-current
  lengths; observed band midpoints are atlas locators, not mapped paths.
  The Norwegian Coastal Current has a source-described Torungen station
  location, with an approximate offshore atlas point. Its name is kept
  separate from Norwegian Current while their identity relationship remains
  unresolved across naming conventions; neither has a ranked length.
  The Algerian, Balearic, and Western Adriatic currents have regional editorial
  points and MEDI state locator candidates based on primary literature. These
  points do not establish full paths, lengths, or NASA-specific identifications.
  Additional regional records distinguish the Baffin Current, the seasonal
  Mauritanian Current, the Gaspé coastal jet, and the Ligurian sector of the
  Northern Current. Gaspé/"Gaspe" is an explicit reviewed gazetteer alias.
  The Equatorial Undercurrent is a family with separate Pacific, Atlantic,
  and Indian records. Observed station or section locations support their
  locators; the Indian section reports approximately 13.5 Sv in March 2017.
  These are subsurface cores, so a NASA geographic crop link is marked
  "depth unverified" and is not evidence that the flow is visible in the clip.
  Marine Regions' "Lomonoscov Current" is linked to the Atlantic record as
  an explicitly sourced spelling variant of Lomonosov Current.
  North and South Equatorial Undercurrent now each have Atlantic and Pacific
  or Indian basin records, respectively. Published 130°E and 35°W section
  transports are displayed separately from unranked path lengths. Their
  subsurface setting also keeps the NASA crop links depth-qualified.
  Four western Pacific feeder names from Grenier et al. (2011) are separate
  records: Mindanao Current, New Guinea Coastal Undercurrent, New Ireland
  Coastal Undercurrent, and Solomon Island Coastal Undercurrent. The study
  describes the last as a potential feeder, so its continuity stays
  unresolved. Editorial points provide state and NASA crop navigation, not
  observed core positions or lengths. The study links the Mindanao Current
  to the Indonesian Throughflow, which NASA names; that relationship is
  independent source context and does not claim NASA identifies Mindanao.
  The surface New Guinea Coastal Current is a separate, seasonally reversing
  flow above the year-round New Guinea Coastal Undercurrent in a three-year
  mooring study. The north and south Pacific Subsurface Countercurrents are
  separate from the Equatorial Undercurrent; a 140°W section locates their
  subsurface jets but provides no whole-current lengths. The Hiri Current
  records a northward Coral Sea branch, with its naming extent around the Gulf
  of Papua explicitly unresolved across sources.
  A 1989 proposed 5,000 km Greenland-to-Middle Atlantic coastal connection is
  represented as a hypothesis, separate from the Labrador Current and excluded
  from the rank. Roughly 2,000 km sampled along the Gulf Stream is recorded as
  a study reach, not the whole current. NOAA's glossary splits the Gulf Stream
  System into Florida Current, Gulf Stream, and North Atlantic Current. The
  Gulf Stream's unranked ≥2,200 km floor uses the glossary's Cape Hatteras to
  southeast-of-Grand-Banks segment; NASA and NOAA Coast Pilot use the name more
  broadly from Florida Straits, and this difference is recorded in the ledger.
  The East Australian Current has a
  conservative ≥1,800 km inferred north–south lower bound for its coherent
  15°S–32°S shelf-break jet, separate from the southward extension and eddies.
  The East Greenland Current has a separate conservative ≥2,100 km meridional
  floor from a study-described 78.5°N Fram Strait section to 59°N Cape Farewell;
  this is not a measured coast-following length or the East Greenland Coastal
  Current's length.
- `../research/named-loop-current-eddies.json` snapshots factual names and
  separation dates from Horizon Marine's public Gulf of Mexico register.
  Regenerate it with `py analysis/build_named_loop_eddies.py` from the repo
  root. This is one regional naming convention; global eddy trajectory
  products generally use track identifiers.
- `../research/named-loop-current-eddy-identities.json` expands the 81 numbered
  Horizon rows into 96 searchable names, including 15 source-labelled secondary
  eddies. Regenerate it with `py analysis/build_named_loop_eddy_identities.py`.
  Secondary records link to a primary row but have no independently reported
  separation date, track, or state footprint. Franklin's 2010 primary record
  also links to a NOAA-hosted independent ring study; that confirms the study's
  name usage, not its NASA identity or OSW state footprint.
- `../research/named-loop-eddy-observations.json` keeps published individual
  positions separate from Horizon's name table. DiMarco et al. place Berek's
  approximate center near 26°N, 89°W in their 2024 MASTR discussion, without
  an exact center date in the cited passage. Its point joins CAMR and NASA
  crop B_3 as geographic context; it is not a ring outline or NASA identity.
  A WHOI/UGOS poster independently labels Berek on a 21 December 2023
  satellite sea-surface-height map. The atlas links that source map to an
  approximate NASA crop seek for the same model date; the date match is a
  cross-release inference, and the poster does not provide a numeric center
  for that date or identify a NASA ECCO eddy.
  Regenerate the joined context with
  `py analysis/build_named_loop_eddy_nasa_context.py`.
- `../research/named-eddy-geography.json` adds 20 recurring regional eddy names
  from Black Sea, Gulf of Alaska, eastern Mediterranean, and western tropical Pacific research, four named classes (Agulhas
  Rings, Peddies, Cuba anticyclones, and Meddies), and eleven studied
  individuals: Astrid, Laura, Ana, Eliza, Jeannette, Lilian, Ulla,
  the source-labelled eddy W, Haida-1998, and sampled Sitka and Kenai eddies from 2007. These are different
  identity levels: a regional name may recur across years, while an individual
  has a specific source year. The two 2007 records have published core-water
  CTD stations, which locate samples but not eddy centers. The Ana, Eliza, and
  Jeannette records preserve dated study points and reported track periods;
  Eliza's point is an approximate split-off site, and Jeannette's identity
  through a merger differs between studies. Lilian has a dated approximate
  altimetry center near Brazil, an undated first-detection point near the
  Agulhas retroflection, a published external track label, and a
  source-reported travel distance; the track itself has not been rejoined.
  Eddy W has a published 22 February 2000 center sample in BENG. Its single
  letter is a study label, and the source does not establish an identity match
  with Astrid or Laura.
  The Agulhas Rings family also retains a separate 1993–2016 study census of
  140 shed rings and 74 long-lived Walvis-crossing tracks. These are detection
  and tracking counts, not 140 or 74 personal names.
  Regenerate
  `../research/named-eddy-geography-join.json` with
  `py analysis/build_named_eddy_geography_join.py`. Its state candidates use
  editorial regional points and its NASA links are movie crops, not matched
  eddy detections. All eleven individuals precede NASA's 2021–2023 crop period,
  so their NASA links are explicitly labeled as views from a different era.
  The Cyprus, Shikmona, and Latakia eddy names are recurring Levantine regions
  in a drifter and altimetry study. Their MEDI points are editorial, with REDS
  excluded where the approximate state geometry would mislabel the sea.
  Latakia is mostly cyclonic in the study but sometimes reverses, so its single
  polarity facet remains unresolved. The Mindanao and Halmahera eddies are
  quasi-permanent western Pacific regions with source-reported typical centers
  and study-defined activity boxes. Their SUND point joins and F_4 NASA crop
  links are geographic gateways, not a vortex footprint, state containment,
  or NASA identification. New Guinea Eddy has a separate editorial WARM
  locator near a study-discussed 2°N, 138°E intermediate-depth site. A later
  paper uses “North Guinea Eddy” near 136°E; the source-specific naming and
  position difference is retained without an individual identity match.
  Every one of the 35 records has an OSW taxonomic link to NASA's broad
  ocean-eddy class. The Agulhas family and seven independently source-labelled rings also
  link to NASA's Agulhas Rings class; none is claimed as an individual NASA
  model eddy.
  The Black Sea entries have no suitable OSW state and are
  excluded from misleading MEDI and REDS polygon overlaps.
  The Meddies family and the April 1997 individual Ulla add subsurface
  Mediterranean Water eddies in the eastern North Atlantic. Ulla's published
  45°N, 11°30′W discovery position is a point, not a lens footprint. Both
  records link to the Mediterranean Undercurrent and NASA's broad eddy class
  only as source-current and taxonomic context; the crop does not verify a
  visible subsurface lens or identify Ulla in NASA's later model years.
- `../research/ocean-eddy-name-inventory.json` combines the 96 Horizon labels
  and 35 other named records into 131 source-scoped atlas addresses. It carries
  identity evidence, event timing where reported, NASA class context, state
  locator limits, and a link to each browser row. Regenerate it with
  `py analysis/build_ocean_eddy_name_inventory.py`. It is the current admitted
  source set, not a global census of every eddy or a NASA individual-identity
  match.
- `../research/ocean-motion-taxonomy.json` defines OSW's faceted crosswalk to
  the existing `flow_structure` object registry. It distinguishes object type,
  identity level, geographic setting, time behavior, polarity, core temperature,
  and evidence. Facets are independent; a warm core does not establish polarity.
- `../research/ocean-current-atlas-index.json` classifies each current record
  and supplies one or more approximate editorial locator points. All 81 named
  rings use one Gulf of Mexico gateway. None of these points is an observed
  core, boundary, event position, or length endpoint.
- `../research/marine-regions-current-crosswalk.json` inventories all 52
  records returned by Marine Regions' Current place type and reconciles them
  against the OSW ledger: 41 name or alias matches, seven unresolved candidates,
  and four records that represent another type of feature. Regenerate it with
  `py analysis/build_marine_regions_current_crosswalk.py`. Most source records
  have no coordinates; none of the seven unresolved candidates has a source point.
  Their names alone do not establish an OSW state join, NASA identification,
  or a current length. The West Spitsbergen and Jutland records do supply
  source points; those points support locator candidates in BPLR and NECS,
  respectively, but do not establish the currents' full paths.
- `../research/nasa-perpetual-ocean-objects.json` inventories objects NASA
  explicitly names or describes in the 2011 film, the Perpetual Ocean 2 pages,
  and the narrated 2025 transcript. It records the release, source, OSW object
  class, and whether the support is a proper name, described structure, or
  generic process. The 70 NASA crops are not counted as 70 objects. The companion
  `../research/nasa-perpetual-ocean-source-audit.json` records which parts of
  each NASA page were reviewed and why contextual geography or movie crops
  were excluded from the object count.
- `../research/nasa-perpetual-ocean-motion-forms.json` assigns a primary
  physical form to each of the 22 NASA records, separating boundary currents,
  overflows, eddy and ring classes, turns, deep flow, and vertical processes.
  The form is an OSW editorial facet; NASA naming support is a separate field.
  Five typed class links connect the broad 2011 ocean-eddy class to the
  regional eddy and ring classes described in later releases. These are
  taxonomic links, not identities of individual eddies across movies.
- `../research/nasa-perpetual-ocean-object-evidence.json` locates all 39
  object–release claims at NASA media-group anchors or exact narrated cue
  numbers. Regenerate it with `py analysis/build_nasa_object_evidence.py`.
  Regeneration checks 34 cited NASA media groups individually and 14 narrated
  passages for curated support phrases; an existing anchor alone is
  insufficient. Multiple film-description links are retained when NASA names
  the same current in separate versions of a release.
  The object/state crosswalk embeds those links so each NASA table source opens
  at its supporting page section; narrated cues refer to NASA's transcript.
- `../research/nasa-perpetual-ocean-object-properties.json` records fifteen
  NASA-reported values for the specific currents and eddy classes described in
  the 2011 story, 2025 Western Boundary Currents page, and narrated film. Values carry their source, unit,
  qualifier, and scope note; none is a current-length estimate. The crosswalk
  embeds them for display in the NASA object table.
- `../research/nasa-perpetual-ocean-tile-join.json` contains all 70 public NASA
  picker crop links and joins each OSW current locator and NASA object locator
  to its most detailed regional movie crop. Regenerate it with
  `py analysis/build_nasa_perpetual_ocean_tile_join.py`. The links are spatial
  context, not an identification of an object in every frame.
- `../research/nasa-current-cartographic-crop-join.json` checks independent
  published cartographic arrows for the seven NASA-identified flows against
  all 56 highest-zoom NASA crop boxes at four map display widths. It supplies
  eight Gulf Stream, four Agulhas, and six East Australian regional crop
  contacts; four NASA flows have no mapped source arrow. Regenerate it with
  `py analysis/build_nasa_current_cartographic_crop_join.py`. These are map
  contacts for navigation, not ECCO feature footprints or frame identities.
- `../research/nasa-object-movie-variant-join.json` audits all 55 movie files
  listed across the seven releases. Fourteen files have a checked media-group
  or narrated-cue join to one or more objects; ten are compositing layers,
  26 are release context only, and five belong to the polar release with no
  identified object. Regenerate it with
  `py analysis/build_nasa_object_movie_variant_join.py`. The browser exposes
  the direct file choices under each supported NASA object.
- `../research/nasa-perpetual-ocean-state-tile-join.json` intersects all 56
  coast-masked approximate OSW state polygons with those 70 NASA crop
  rectangles, allowing for the map's repeated longitude. Each state gets
  ranked regional movies and an overview. Regenerate it with
  `py analysis/build_nasa_state_tile_join.py` (requires Shapely). Its overlap
  fraction is equirectangular display area, not geodesic area or an identified
  NASA ocean object.
- `../research/nasa-ocean-object-state-crosswalk.json` joins every identified
  NASA object to all supporting releases, its regional movie, and each OSW
  state relation by evidence type. Regenerate it with
  `py analysis/build_nasa_object_state_crosswalk.py` after updating its source
  ledgers. Its mapped current crossings come from independent arrows or OSW
  sketches; object locator points do not prove footprints. A NASA-described
  class with no bounded locator, timed passage, or feature film receives a
  clearly labelled source-release overview movie, never a fabricated point.
  Child structures also join back to their NASA parent record and, when that
  parent is a named current, to its current-ledger row. The state view exposes
  all six stored NASA object/state evidence kinds, including schematic and
  editorial current crossings, width-sensitive cartographic contacts, and
  the OSW conceptual Indonesian Throughflow gate crossing in SUND.
- `../research/nasa-object-state-relation-matrix.json` materializes every
  identified NASA object × OSW state pair: 22 × 56 = 1,232 rows. It preserves
  every map evidence kind and marks pairs without evidence as unresolved,
  rather than absent. A separate contextual-member list now joins NASA's
  named western-boundary examples, NASA-narrated overturning members, and
  OSW taxonomic eddy children where those members have atlas evidence. It
  yields 26 class or system/state context pairs without transferring the
  member's footprint to the class. Each NASA current/state arrow relation
  carries the independent source arrow IDs from the named-current matrix,
  including width-sensitive contacts; the state view displays those IDs.
  All physical crossing and containment
  claims remain unknown without NASA feature footprints. Regenerate it with
  `py analysis/build_nasa_object_state_relation_matrix.py` after the crosswalk.
- `../research/nasa-perpetual-ocean-atlas-catalog.json` assembles one record
  for each of the 22 NASA-identified objects. Each record includes release
  passages and model periods, form taxonomy, reported properties, direct
  current and length evidence where available, all 56 state relation
  decisions, primary and source-linked movies, map-arrow crop navigation,
  and independently named eddies in class or flow context. A release-first
  index includes the audited object list, reviewed page parts,
  and the scope note for each of the seven NASA pages. The builder checks
  that this index agrees with the object-to-release edges in both source files.
  The catalog preserves unknown physical relations and rejects individual NASA eddy
  identity claims. The NASA object table uses this export for reverse links
  from the broad eddy class, Agulhas Rings, Gulf loop eddies, and the Persian
  Gulf overflow to their independently sourced named records. Regenerate it with
  `py analysis/build_nasa_perpetual_ocean_atlas_catalog.py` after its source
  ledgers.
- `../research/nasa-perpetual-ocean-object-media.json` records direct NASA
  feature films: the Agulhas Current and rings, the Gulf Stream deep return,
  and NASA's timed trapped-warm-water class example. Each link states whether
  the movie is feature-specific or only illustrates a class.
- `../research/nasa-perpetual-ocean-release-media.json` inventories every Movie
  item on the seven audited NASA release pages through NASA SVS's page API.
  The browser's release-first view joins this catalog to the audited object
  list and exact NASA passage link for each release, including the polar
  release that identifies no individual motion object in its page text.
  Regenerate it with `py analysis/build_nasa_perpetual_ocean_release_media.py`.
  Its 55 listings are media variants, not 55 identified ocean objects. Check
  the live series feed and each audited release's direct NASA related,
  source, alternate-version, and version-history links with
  `py analysis/check_nasa_perpetual_ocean_series.py`; a new linked release
  must be audited before it enters the object ledger.
- `../research/nasa-perpetual-ocean-crop-timeline.json` provides approximate
  date seeks for the regional beauty movies from NASA's separate 3,601-entry
  Science on a Sphere date list and four sampled 7,201-frame crop films.
  Regenerate it with `py analysis/build_nasa_perpetual_ocean_crop_timeline.py`.
  NASA does not publish an explicit date list for those crop files on the
  reviewed page, so the alignment is labelled as an inference. Matching the
  NOAA date does not identify a NOAA eddy in the NASA model.
- `../research/noaa-nasa-eddy-crop-join.json` links all 38,675 NOAA daily
  detections on the five sampled dates inside NASA's published date range to
  the most detailed NASA crop containing each detected center. The state atlas
  offers a direct crop link with the approximate same-model-date seek for each
  of those detections. Regenerate it with
  `py analysis/build_noaa_nasa_eddy_crop_join.py`. This is geographic and
  temporal navigation between different products, not an individual eddy
  identity match or a NASA-labelled detection.
- `../research/ocean-motion-state-join.json` is a state-first index for all 56
  approximate OSW ocean states. Regenerate it with
  `py analysis/build_motion_state_join.py` (requires Shapely). It distinguishes
  schematic centerline crossings, an East Australian Current editorial sketch,
  and point-in-state locator candidates. The sketch is declared separately in
  `../research/nasa-motion-editorial-paths.json`.
- `../research/cartographic-ocean-current-state-join.json` joins a published
  73-arrow cartographic layer to the same 56 state shapes. It maps 61 arrows to
  27 current names in the ledger, comparing all four published arrow
  widths; stable crossings and width-sensitive contacts are separate. Regenerate
  it with `py analysis/build_cartographic_current_state_join.py` (requires
  Shapely). The source layer credits NOAA NWS, the U.S. Army, and Maps.com and
  describes its polygons as arrows optimized for cartographic display. These
  joins are map relationships, not measured current paths or NASA ECCO data.
  Four arrows labelled East Wind Drift / Antarctic Subpolar map to the
  source-backed Antarctic Coastal Current (East Wind Drift); their broad
  cartographic polygons are not evidence of a continuous measured coastal path.
  The remaining 12 arrows carry explicit reasons for exclusion: blank labels,
  combined identities requiring reconciliation, or sea-ice drift rather than
  an ocean current.
- `../research/noaa-munster-eddy-seasonal-manifest-2021-2023.json` indexes
  twelve NOAA MUNSTER daily snapshots: 1 March, June, September, and December
  in each of 2021–2023. They hold 92,891 dated detections in total. Each
  snapshot has daily local IDs, center, polarity, source radius,
  and containment/intersection against the 56 OSW state shapes. Regenerate
  any date with `py analysis/build_noaa_eddy_state_snapshot.py --date YYYYMMDD`
  (requires netCDF4, NumPy, and Shapely). Source NetCDF files are downloaded
  to a temporary cache; each research JSON records its SHA-256 and source URL.
  These are twelve sample dates, not continuous 2021–2023 coverage. The browser
  loads each selected date on demand; only June dates have seven-day track files.
- `../research/noaa-munster-eddy-weekly-join-YYYY0601-YYYY0607.json` for
  2021, 2022, and 2023 matches all 7,851, 7,751, and 7,699 respective
  1 June detections to NOAA's overlapping seven-day trajectory files using
  polarity, exact day-one center, and radius. Regenerate a year with
  `py analysis/build_noaa_eddy_weekly_join.py --date YYYY0601`. The column reference is scoped
  to that weekly file; it is not a persistent cross-week identity or a match
  to a NASA ECCO eddy or historical ring name. The weekly product's separate
  trajectory-ID variable was not used because it does not identify columns in
  the inspected file.
- `../research/noaa-munster-eddy-weekly-state-join-YYYY0601-YYYY0607.json`
  indexes every center position in each sampled seven-day file against the 56 OSW
  ocean states. Regenerate a year with
  `py analysis/build_noaa_eddy_weekly_state_join.py --date YYYY0601`. A center visit is distinct
  from a daily contour crossing or containment. It does not connect the track
  to a NASA model eddy or a named historical ring.
- `../research/noaa-munster-eddy-weekly-contour-state-join-YYYY0601-YYYY0607.json`
  tests each available weekly NOAA contour on the 1 June matched trajectories in each year
  against the state shapes by date. Newly appearing trajectories later in the
  week are outside this join.
  Regenerate a year with `py analysis/build_noaa_eddy_weekly_contour_state_join.py --date YYYY0601`.
  Day-one relations are cross-checked against the separate daily product.

The named-eddy geography join also records separately dated positions when a
source supplies them. Ring Jeannette's reported 27 December 2015 track endpoint
at 21°S, 35°W falls inside the approximate BRAZ state polygon and links to the
NASA regional crop there. This is a point and a model-region navigation link,
not a ring footprint, state containment, or an individual identity in NASA's
2021–2023 animation. The source's track identity spans a merger and depends on
the tracking method.
Ring Lilian's source reports an undated first-detection point at 39.5°S,
14.6°E, which joins to SSTC; its 7 June 2006 approximate center joins to
BRAZ. Those two points do not define its intervening route, state crossings,
or a closed footprint.

## Coverage and navigation

The v1 atlas indexes all **98 located current ledger records**, with **six
published length estimates** eligible for this source-set ranking and other
records kept unranked when they have only bounds, sampled reaches, or proposed
system lengths. It keeps **seven
additional Marine Regions current-name candidates** visible for review. It also
indexes **22 NASA-named or
described motion records (including classes and processes)**, **70 NASA crop movies**, **56 OSW states**, **92,891 NOAA daily
eddy detections across twelve sample dates**, and **96 Loop Current eddy names from 81 numbered
events**, plus **35 other named eddy records** in this
source set. It is a complete join of these ledgers,
not a complete inventory of Earth's named currents or eddies. Some equatorial
names remain cross-basin families, and their mapped components still lack whole-current lengths. Other
regions and institutional naming systems need to be added with their own
sources; no global naming authority or complete named-eddy census is claimed.

Each current marker and each located NASA-described structure marker jumps to
its table record. The 14 narrated objects have bounded clip links in NASA's
published film; the bounds are editorial navigation intervals, not event
durations. Most Loop eddy records return to a shared Gulf region marker because
Horizon's register supplies names and dates, not coordinates for each eddy.
Berek also has a separate approximate published center marker from another
study. A future individual-eddy map layer needs
source-linked tracks with positions, time intervals, and identity reconciliation
across splits and mergers. NOAA/CMECS classifies hydroforms and META4.0
classifies tracked mesoscale eddies; OSW's contribution here is a joined
name–class–evidence–atlas index, not a replacement for those standards.

NASA's *Perpetual Ocean 2* is linked as motion context. The film's sequence
features Kuroshio, Agulhas, and Gulf Stream. NASA also publishes a public
picker with 70 direct regional movie links. The atlas joins every current
locator and every OSW state to crops; only the objects in NASA's explanatory text or transcript
are marked NASA-identified. Do not use the animation to infer current lengths,
ring identities, or specific eddy positions.

NASA object records with narrated timecodes link to a short, source-audited
passage in NASA's published WebM movie. The added Kuroshio eastward turn, Gulf Stream cold cores,
and North Atlantic sinking water are described structures, not newly named
individuals. The Gulf Stream cold-core polarity wording is retained as a
source-specific claim; the almanac does not generalize it to every cold core.

## State relation rule

`../research/ocean-current-state-relation-matrix.json` materializes all
98 × 56 = 5,488 named-current/state decisions, with 209 atlas-linked pairs
and current-first and state-first views. Arrow-based pairs retain the exact
source arrow IDs, including width-sensitive arrows overridden by a stable
arrow for the same current and state. Regenerate it with
`py analysis/build_ocean_current_state_relation_matrix.py` after the motion
and cartographic joins. Unlinked pairs remain unresolved, not absent.

The four existing OSW drawn current centerlines (Gulf Stream, Kuroshio,
Agulhas, and Antarctic Circumpolar Current) are intersected with the
coast-masked approximate state polygons. These relations say a **schematic
line crosses a schematic state**. An editorial East Australian Current line is
kept in a separate crossing category because it is not an existing Atlas 10
feature shape. The Indonesian Throughflow's drawn gate is also reported
separately. For other named currents and NASA objects, the state page
shows **cartographic arrow crossings** where the source has a mapped arrow,
and otherwise only **locator candidates**: a point in a state is not evidence
that the flow passes through the whole state. Arrow crossings are a stronger
atlas index than a point, but source arrow width and routing remain map design
choices. The Black Sea Rim Current has an atlas locator but no OSW state relation:
the approximate MEDI polygon covers its point while the state's label denotes
the Mediterranean Sea, so that semantic mismatch is explicitly excluded. The NOAA MUNSTER snapshot adds **dated
detected eddies**. Their closed contours are compared with state polygons:
fully covered contours count as contained, and contours that touch without full
coverage count as intersecting. The state selector can overlay their centers
on the atlas for that date; the colored dots are NOAA detections, not NASA
particle identities. The daily IDs are local to this file; they are
not stable track IDs or the 81 Horizon names. Named-ring containment and
intersection remain unknown until identities can be reconciled. MUNSTER's
daily detection field is approximately limited to 60°S–60°N and to the
detectable mesoscale range; a zero in a polar state is not proof of no eddies.
Each listed detection can show its available 1–7 June center path on the map.
The path is a NOAA trajectory of centers, not an eddy footprint for all seven
days and not a NASA model streamline. The state selector separately lists
every weekly track whose reported center visits that state, with visit dates
and a link to its path. It also lists dated contours that are fully contained
or intersect the state. A weekly center visit does not establish a contour
intersection or containment for that date; the contour lists use the separate
shape test. Choosing a track also offers a NASA regional movie near the
selected NOAA date, explicitly as geographic and model-time context rather
than a NOAA-to-NASA eddy identity match.

Validate data joins with `py analysis/check_motion_almanac.py`. Run
`py analysis/test_motion_almanac_browser.py` for the optional Chrome-based
page smoke test.

## Length rule

Marine Regions' "North Sea Bottom Current" remains a review candidate. Its
gazetteer record assigns it to the North Sea, while the cited Sivkov et al.
study describes intermittent Baltic Sea bottom currents supplied by North Sea
inflow. Neither source provides a verified route or length for that named
North Sea current, so the atlas does not place it in an OSW state.

Do not turn a picture, coast distance, endpoint separation, particle travel
distance, or current speed into a current's length. The current source set has
six published whole-current estimates, five derived geographic floors, and
24 ranked illustrated map spans; the union of the published and illustrated
sets covers 27 of 98 names. Those are different measures and must not be
merged into a single numerical ranking.

A reproducible estimated-length ranking should use this protocol:

1. Resolve each ledger name to a specific flow, branch, depth class, and
   upstream/downstream gates. Split cross-basin families into basin-specific
   records before ranking. Record source citations for both gates.
2. Fix one velocity product and time window for a ranking cohort. A global
   surface-current product can cover surface flows; subsurface undercurrents
   need a depth-resolving product and a separate cohort. Store product version,
   grid, temporal statistic, and depth or depth range with every result.
   Candidate inputs are [NASA's OSCAR surface velocity product](https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_INTERIM_V2.0)
   and [Copernicus global physics reanalysis](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/services)
   for depth-resolved comparisons. Test their coverage and access before
   selecting a baseline; neither dataset supplies named-current boundaries.
3. In each named flow's geographic corridor, find a connected core whose
   velocity points mainly along the source-described flow direction. Trace one
   geodesic centerline between the gates and sum its segment distances.
   Keep a branched current's main route separate from its branches; a closed
   circumpolar route has no ordinary start/end gates.
4. Repeat across representative months or years and plausible core thresholds.
   Report a median length and a sensitivity range, rounded to a precision the
   gates and grid support. Mark intermittent, reversed, or untraceable cases
   unresolved instead of forcing a length.
5. Sort only like-for-like computed lengths within each cohort. Keep published
   estimates, geographic floors, and illustrated spans in separate columns;
   compare their scope and flag large disagreements for review.

This would yield an explicitly model-defined ranking, not an intrinsic fixed
length for every current. Published estimates remain a separate source-reported
column when that analysis exists.
The current page ranks only the estimates admitted in its first source set.
For the Agulhas Current it also shows a source-reported roughly 1,000 km
coastal scope alongside an unranked ≥1,400 km floor inferred from a broader
27°S–40°S reach. Those definitions are incompatible as a single exact current
length, so neither enters the comparable ranking. A 2019 observational review
also found the Tasman Front and East Australian Current Extension rarely
distinct as instantaneous jets; the atlas retains the Tasman Front name as a
time-mean or regional index with its identity caveat.

## Eddy rule

Keep a named recurring eddy *region or type* distinct from a named individual
eddy and from a tracked trajectory ID. Never use a historical `Active` label
as a present-day status. Name sources and tracking products have different
coverage and identification rules; state both with each record.

Measurement conventions are consolidated in
`plans/ocean-current-measurement-protocol-v1.md` (v1.0); the route review page
shows its summary and links. Run `analysis/check_current_measurement_protocol.py`
after each batch. The audit checks calculation/provenance conformance and leaves
source support and scientific correspondence for review. The earliest EAC
source was rechecked on 2026-10-03; its unrecorded original retrieval date is
not reconstructed, and geometry/length remain unchanged.

The catalog builder now executes the protocol audit before replacing its output.
Catalog JSON pins the protocol version/hash and audit hash. Complete declared
scenario grids and input/report metadata agreement are checked automatically;
invalid dates, nonfinite lengths and omitted/duplicated scenarios are rejected.

## Widths and seasonal explorer

`reference-routes.html` now shows a separate width evidence section. The
100-name width inventory contains two Northern Current seasonal summaries
(about 25 km winter, 40 km summer) and two dated Azores meridional-section
spans (110 km each). Four width records cover three names; two existing width
mentions await original source/definition review and 95 names are not assessed. The 25-40 km span is
between reported typical values, not annual extrema or an uncertainty band.
Width measurement rules are in `plans/ocean-current-width-measurement-protocol-v1.md`;
check with `python analysis/check_current_width_inventory.py`.

`seasons.html` plays through these two sourced states with a changing width bar,
static labelled reference geography and seasonal length unknown. It indexes
all 100 names and retains unknown coverage. Physical annual route/footprint
animation needs new temporal geometry; see `plans/ocean-current-seasonal-atlas.md`.
Canonical release, published ranks and length candidate counts unchanged.

The seasonal explorer also plays two existing Somali editorial route components
with switching map, direction, scoped length and scenario envelope. Frames in
`research/ocean-current-seasonal-route-frames.json` pin source reports; validate
with `analysis/check_current_seasonal_route_frames.py`. The winter branch and
June-July southern limb differ in extent, so annual extrema remain unknown.
Open `seasons.html?current=somali` or follow a route card's seasonal link.

Azores Current and Countercurrent widths are fixed-orientation section spans
at 24.5 W, sampled 26 October-1 November 2009, not perpendicular-to-flow or
annual widths. The source Figure 1 caption says 2010 while explicit data text
says 2009; the discrepancy remains recorded for review. Single dated snapshots
disable seasonal playback. Explorer bars now show a labelled scale appropriate
to the selected records (0-150 km for 110 km values); no clipping at 50 km.


## Coverage dashboard

Open `dashboard.html` for all 240 current/eddy records, evidence lights,
search/filtering and changes since your browser's last marked snapshot.
Regenerate after ledger updates with `python analysis/build_motion_dashboard.py`.
See `plans/ocean-motion-coverage-dashboard.md` for evidence and update semantics.
This local research view does not perform provider acquisition.

### Global current route explorer and state crossings

`reference-routes.html#route-atlas` starts with the OSW global map: 100 selectable
current stations, reference paths where available, zoom buttons/wheel, drag pan,
keyboard arrows/+/−/Home, and selection into the visual route card. Direct card
fragments resolve after asynchronous rendering; map image dimensions are reserved
to prevent jumps. Each card provides its permalink and a global-map return link.

`analysis/build_reference_route_state_join.py` inverts nominal and every retained
scenario crossing for the 41 candidates / 39 currents. The result
`research/ocean-current-reference-route-state-join.json` covers all 56 states,
90 candidate/state pairs and 40 states with candidate crossings. This is a
display-geography join; counts are sensitivity cases, not observed passage,
probabilities, annual frequency, transport or containment. The almanac state
panels expose these separate candidates. Missing optional join data leaves the
existing state evidence available. Rebuilding the route catalog refreshes this
join and the dashboard. Focused checks:

```powershell
python -m unittest discover -s analysis -p test_reference_route_state_join.py
python analysis/test_reference_route_navigation_browser.py
python analysis/test_reference_route_atlas_browser.py
```
