# Ocean motion coverage dashboard

Working local dashboard, 2026-10-03. Entry: almanac/dashboard.html, linked
from the almanac. Covers the release's 100 currents, 136 named eddies and
four operational detections; 16 proposed names have a separate review link.

## Evidence lights

The selected evidence type controls the green indicator and card border:
published ranked length, editorial route, scoped width, geometry beyond a
locator, or time samples/phase records. Indicators mean presence, not quality,
scientific admission, present activity, complete width or annual extrema.
Canonical data and research candidates retain their scopes and object links.
The Gulf Stream derived width series remains a research candidate; Ingoy
samples remain regional model evidence rather than current footprints.

## Update semantics

Per-object SHA-256 fingerprints cover entity metadata, measurements, routes,
widths, direct claims, geometry, media, phase records and applicable dated/model
series. Built time alone never changes an object's fingerprint. First visit
establishes a baseline; subsequent loads/refreshes compare against the last
marked snapshot saved in this browser. Changed records receive an Updated
label and outline, with a brief animation disabled under reduced motion.
Mark changes seen acknowledges the available records. This is a browser-local
comparison, not a global editorial history or a claim about observation age.
Unavailable refreshes retain the loaded snapshot with an explicit error.

Check every minute is opt-in and skips hidden pages. Refresh loads a rebuilt
coverage snapshot, not new provider observations. After source-ledger updates,
regenerate the snapshot as part of the data workflow:

```powershell
python analysis/build_motion_dashboard.py
```

Pinned inputs and built_at_utc are downloadable. Reconstruct with build() and
compare to saved JSON after excluding built_at_utc; all 240 entries reconcile
with the versioned release ledger. Acquisition pipelines remain explicit.

## Verification

Browser test: analysis/test_motion_dashboard_browser.py. Checks all five
capability counts, current/eddy filters, search, object/route links, content
changes across refresh and reload, acknowledgement, no recurring false update,
failed-refresh retention, reduced motion and 320 px layout. Desktop/mobile
screenshots inspected; light-card inherited text contrast corrected.
Scientific/publication status is unchanged. No verification job remains live.


## Provenance and dated-evidence revision — 2026-10-03

Fingerprint version 2 includes linked release source records, including source
snapshot and method references. Each object also has separate identity, source,
claims/reviews, measurements, route/geometry, media and time-evidence hashes.
Update labels identify changed groups. The browser comparison key is versioned
to establish a fresh baseline when the fingerprint definition changes; an
algorithm upgrade must not make every object appear newly observed.

Latest dated evidence accepts valid explicit observation dates/range bounds,
geometry observation dates, width observation periods and dated/model frames.
Publication, retrieval and dashboard build dates never fill missing dates.
Dates apply to recorded evidence, which may be regional or partial; they do
not certify current-wide contemporary monitoring. Claim status counts come
directly from released individual claim reviews; source-rights review is not
scientific claim verification. Unrecorded observation dates stay unknown.

Two evidence tests verify date rejection and a synthetic source-rights review
change without writing canonical files. Only affected object fingerprints
change; capability counts and observation dates remain identical. Expanded
browser verification checks Gulf Stream 2026-09-28 and Ingoy 2024-12-15,
review details and source-change reason, plus original update/filter controls.
All checks pass. No verification process remains running.

## Visual atlas revision — 2026-10-03

The dashboard opens in Atlas view. All 240 filtered inventory objects have
stored geometry, a source-geography locator, or an explicitly editorial
regional gateway. The grouped Gulf gateway is a browsing location, not 96
separate observed centers. Source-geography points retain their ledger basis;
dated provider outlines retain observation dates; editorial routes remain
candidates. No new containment or current-width inference is made.

Green markers and routes reflect the selected evidence category. Amber outlines
mark content updates against the browser baseline. A grouped diamond reports
covered/total filtered names, so one member's evidence never lights every member
as individually covered. Click or use Enter/Space to open the member records.
Search and evidence filters apply to both atlas and cards. Regional presets
make nearby markers easier to select; they crop the map, not the record list.
Record cards remain the complete text alternative.

The ground SVG is regenerated from the existing OSW atlas coastline by the
same builder, with the source SVG hash pinned in the snapshot. The projection
is shared with existing locator joins; coarse coastlines are context only.
The builder also pins source geography, Loop context and full candidate route
files. Tests cover gateway grouping without individual position fabrication,
route/locator capability separation, keyboard selection, a pointer click on
the Gulf diamond, updates on map markers, refresh failure and narrow layout.
Three unit tests and the browser test pass; desktop atlas and mobile screenshots
were inspected. Provider acquisition remains separate from snapshot refresh.

## Compact cards and Beck-inspired schematic — 2026-10-03

The default view is now Beck schematic, alongside OSW map and Record cards.
The OSW map reuses the actual province-field, ocean mask and state labels.
The world schematic snaps candidate route vertices to an 8-unit diagram grid
and replaces each leg with horizontal/vertical/45-degree bends. Dateline jumps
start a new subpath. These coordinates never enter measurement calculations.
Every one of the 100 currents has one schematic station, using a midpoint
waypoint of its first available reference route or its first name locator.
Shared coordinates are displaced for readability. Labels use diagram-space
collision avoidance, with leaders where necessary; regional views rescale
marker and type sizes. The complete station index labels all 100 records.
Eddy diamonds group records by released basin and open all member identities;
placement is a schematic regional gateway, not an observed individual center.
Line crossings are not source-supported interchanges. Building scientifically
reviewed branching/connectivity remains separate work; the schematic is a
first atlas prototype, not an admitted global current network.

Record cards use five columns on desktop, less padding and expandable evidence,
sources and links. Observation dates and review counts remain available inside
the disclosure. All three unit tests pass. Browser verification passes with
100 world stations, 100 world labels, 100 index stations, regional eddy groups,
keyboard and pointer navigation, five evidence categories, persisted change
markers, acknowledgement, failure retention and mobile reflow. Desktop OSW,
Beck world and compact-card screenshots inspected; no test process remains.

## Source-described links and hover labels — 2026-10-03

Two local connectivity candidates record the NOAA glossary's Kuroshio →
Kuroshio Extension → North Pacific continuation. The catalog pins endpoint
identities, predicate, source URL/locator, access date, layer/time limitations,
and null junction/transport fields. It is not canonical admission. The builder
rejects unresolved identities, duplicate IDs, self-links and unexpected
predicates. Only source-described downstream links are drawn: source-distinguished
current and named-regional-segment predicates are explicitly excluded from
flow connectivity. Dashed schematic links connect identity stations, with
accessible source selection; dateline crossings split into border subpaths.
A new evidence category shows three participating current records; it does not
change any length, width, dated observation or geometry capability.

Map names now appear only on station hover or keyboard focus, in larger type
next to the station. Hidden leaders follow the same rule. Accessible names
and the full named index remain available. Collision placement is no longer
needed for simultaneous hidden labels; edge clamping keeps hover text within
the region view. Browser verification checks hidden, hover, pointer-out and
keyboard-focused label states, source selection and all six evidence filters.

## Visible station completeness — 2026-10-03

DOM counts alone did not prove visually distinct stations: nearby current
locators overlapped. The Beck world now numbers the released alphabetical
current index 1–100 and places stations at least 30 diagram units apart, inside
the map frame. The placement is an editorial diagram operation only; it changes
no source geometry, route length, state intersection or physical junction.
Names still appear on hover/focus. Index entries carry the matching numbers.
Routes, eddy gateways and all current stations have separate paint layers so
later paths cannot obscure earlier numbered stations. Browser checks assert
exactly the integers 1–100, all centers inside the guarded frame, and every
pair's separation, in addition to the hover and source-link checks. The world
screenshot was inspected with all stations exposed; no active test remains.

## Aleutian identity and branch evidence — 2026-10-03

The source-connectivity category now covers five links using three separate
predicates: downstream continuation, feeding and branching. Source selection
shows the predicate and its layer/time limits. Three AMS Aleutian links add
Oyashio feeding and Alaska/California branches to the two NOAA Kuroshio links.
The proposed Alaskan Stream stays outside the canonical map and the 1–100
station index. Its proposal raises the separate inventory-review count to 17.
An evidence test verifies link types, absent junction/transport values, no
Aleutian route or observation date borrowed from the glossary, and no accidental
Alaskan Stream canonical admission. Four dashboard unit tests pass.

Catalog rebuilds now regenerate the motion dashboard after protocol acceptance
and catalog writing, so route/proposal updates reach the coverage lights without
a separate manual command. This stage refreshes the available snapshot only;
it does not acquire provider observations. Other evidence pipelines can still
call the standalone dashboard builder after their input changes.

Verification completed: 4 dashboard evidence tests, 5 reference-catalog tests, expanded dashboard browser test and full almanac browser test pass. Catalog rebuild regenerates a matching dashboard snapshot with 17 proposals and five typed links. Canonical 100/136/4 counts remain unchanged. No verification job is running.

## Indexed source-scope notes — 2026-10-03

A curated source-note index currently covers Aleutian and Antilles. Each note
pins a source-scope audit and links the source with its passage. The evidence
category counts indexed notes, not independent scientific approvals. Audit
contents and note metadata participate in affected objects' source hashes;
empty note fields do not change other objects' baseline fingerprints. Only
explicit observation periods supply dates. Antilles now shows the regional
study's 2015-11-23 endpoint, with no source-derived width or reference route.
The map drawer and compact card disclosure expose its modern regional scope.
Five dashboard evidence tests and the seven-category browser check pass.

Verification completed: five dashboard evidence tests, eight width-inventory tests, the width validator, the expanded seven-category dashboard browser check and the full almanac browser check pass. Antilles has one source note, no route/width capability, and the explicit regional observation end date 2015-11-23. No verification process remains.


## 2026-10-03 · Atlas classifications and proposal scope

The global current atlas opens a selected route beside its visual map card.
All 100 current names and 140 eddy records remain selectable. Classification
is a compact keyboard-accessible disclosure using exact released inventory
level, description, setting and time behavior, including unresolved values.
These are editorial classifications, not scientific admission or evidence of
whole-current continuity.

The Solomon Island Coastal Undercurrent card now links a source-scope receipt:
the author-hosted abstract proposes Solomon Islands Coastal Undercurrent from
a 1/12-degree model; publisher full text was blocked. No axis, width, annual
range or observed continuity is inferred. Route coverage remains 52 candidates
for 50 of the remaining 89 names, with 39 pending; scope reviews now cover 17
currents. Canonical ledger and released facets are unchanged.

Verification: eight dashboard unit tests; global atlas navigation and all 140
eddy selections; all 17 source-scope previews; all 100 current classification
disclosures at 320 px and all 240 records against the released facets. System
Chrome automation stalled and was stopped; successful browser checks used the
already installed Chromium headless shell 1223. The focused test accepts an
absolute browser executable via OSW_TEST_BROWSER:
`python analysis/test_atlas_classification_browser.py` (local preview on 8788).
Screenshot inspected: figures/custom-current-atlas-navigation-review.png.
Review: signals/roles/check/atlas-classification-proposal-scope-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. Full scientific source and
extent review, missing routes and annual geometry remain open.


## 2026-10-03 · Pacific NECC east-central studied reach

Added a 140 W to 95 W editorial studied reach: approximately 5000 km with a
4900-5100 km scenario envelope (raw nominal 4994.045 km; 81 declared cases).
Johnson et al. (2002) section descriptions inform 140 W/125 W core locations;
110 W 6 N and 95 W 7 N are explicit editorial choices. The route excludes
western inflow and coastal redistribution, is not a whole-current length,
and stays outside comparable route and published-length rankings.

The source fitted surface expression near 110 W is absent in December-February
and peaks in August. This does not establish all-depth absence or a continuous
year-round path. Source ensemble June 1985-December 2000 is context, not a route
date. Source figures and CTD/ADCP arrays are not packaged; width and annual
ranges remain unresolved. Scope receipt:
research/pacific-necc-reach-seasonal-section-scope-audit.json.

Current coverage: 53 candidates / 51 of the remaining 89 names / 38 pending /
3708 scenarios, with 39 comparison routes and 14 studied reaches. State join:
106 candidate-state pairs across 43 states; 18 current source-scope reviews.
Canonical ledger, width records and 21 proposals unchanged.

Verification: 21 focused unit tests, candidate protocol audit, direct visual
card and three state links, 320 px reflow, no borrowed observation date/width
or comparable rank, and all 106 route/state navigation pairs. Installed
Chromium headless shell 1223 used. Screenshot inspected:
figures/pacific-necc-reach-reference-path-review.png. Seven-role receipt:
signals/roles/check/pacific-necc-studied-reach-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. Independent science and
monthly/depth axis review remain open.


## 2026-10-03 · Northern Tsuchiya reach and NEUC distinction

Added a Pacific North Subsurface Countercurrent studied reach from 155 W to
110 W: approximately 5000 km, scenario envelope 4900-5100 km, raw nominal
4998.364 km, 81 declared cases. Johnson and Moore (1997) Table 1 supplies the
mean core neighborhoods (3.5 N/220 m and 4.5 N/130 m); intermediate bends are
editorial. Source compilation years 1967-1996 do not date the route. Formation
and eastern continuation are excluded; estimate remains outside comparable
route ordering and published-length rankings.

The 130 E North Equatorial Undercurrent mooring identity remains separate and
route-pending. No northern Tsuchiya length or local depth is transferred. Its
transport integration band, and the Tsuchiya Table 1 integration bands, are
not admitted as widths. No annual ranges or monthly axes are inferred.
Receipts: research/pacific-nscc-reach-layer-section-scope-audit.json and
research/pacific-neuc-nscc-distinction-scope-audit.json.

Coverage now: 54 candidates / 52 of the remaining 89 names / 37 pending /
3789 scenarios, 39 comparison routes and 15 studied reaches. State join:
108 candidate-state pairs in 43 states. There are 20 current source-scope
reviews. Canonical ledger, widths and 21 proposed identities are unchanged.

Verification: 21 focused unit tests, v1.2 candidate audit, new northern
Tsuchiya/NEUC browser check, mobile reflow, no borrowed length/width/date/rank,
and all 108 route/state links. Screenshot inspected:
figures/pacific-nscc-reach-reference-path-review.png. Seven-role review:
signals/roles/check/pacific-nscc-neuc-scope-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. Axis, extent and independent
science review remain open. The browser test accepts OSW_TEST_BROWSER pointing
to an installed executable; successful checks used Chromium headless shell
1223 against the local 8788 preview.


## 2026-10-03 · Southern historical mean-core reach and branch scope

Added a Pacific South Subsurface Countercurrent historical mean-core studied
reach from 155 W 3.5 S to 110 W 5.5 S: approximately 5000 km, 4900-5100 km
scenario envelope, raw nominal 4998.626 km, 81 cases. Johnson and Moore (1997)
Table 1 supplies local 250 m/160 m peak depths. Intermediate bends are editorial;
western formation, secondary-jet geometry and eastern continuation excluded.
This is not a branch-averaged axis, combined length or whole-current estimate.

Rowe et al. (2000) primary/main and secondary SSCC terminology is retained in
a source receipt; correspondence to this historical route and independent
origin versus splitting remain unresolved. Its roughly 40 km PV-front span,
likely an upper bound affected by density resolution, is not current width.
Integration latitude bands also remain separate. No monthly geometry, route
date or annual dimension range is inferred. Receipt:
research/pacific-sscc-mean-reach-branch-width-scope-audit.json.

Coverage: 55 candidates / 53 of the remaining 89 names / 36 pending / 3870
scenarios, 39 comparison routes and 16 studied reaches. State join: 110 pairs
in 43 states. Current scope reviews: 21. Canonical ledger, widths and 21
proposed identities unchanged. This route stays outside comparable route
ordering and published-length ranking.

Verification: 21 focused unit tests, v1.2 complete candidate audit, direct
southern mean-core card/mobile/data checks, all 110 route/state links and all
21 source-scope previews. Screenshot inspected:
figures/pacific-sscc-mean-reach-reference-path-review.png. Seven-role review:
signals/roles/check/pacific-sscc-mean-branch-scope-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. Branch/axis science review
remains open. Browser checks used installed Chromium headless shell 1223;
analysis/test_pacific_sscc_mean_reach_browser.py accepts OSW_TEST_BROWSER.


## 2026-10-03 · Dated Gulf Stream System views in the custom atlas

The global current atlas now draws three already released Gulf Stream System
lines: September 25, 2026 partial geostrophic diagnostic and September 28,
2026 analyzed north- and south-wall fronts. Hover/focus exposes names and
dates; selecting a line opens its inline OSW map card and fits the view.
Compact dated controls switch the saved geometry; share URLs preserve the
exact geometry selection. Source links, snapshot receipts, method and scope
notes remain visible. The Gulf Stream segment receives no system geometry.

These saved lines are not a simultaneous width, whole-current centerline or
annual evolution. Coverage remains 55 reference candidates / 53 of the
remaining 89 names / 36 pending, with 100 current and 140 eddy records
selectable. Frozen release and canonical scientific admission unchanged.

Verification: nine dashboard unit tests; dated-view browser checks with
fresh shared-view restoration and 320 px layout; family component navigation
and global atlas regressions. Installed Chromium headless shell 1223 used.
Screenshot inspected: figures/atlas-dated-surface-card-review.png. Review:
signals/roles/check/atlas-dated-surface-navigation-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No complete-suite claim.


## 2026-10-03 - Saved sample playback inside the current atlas

Gulf Stream System now has inline date controls and sample playback on the
custom global atlas: twelve daily snapshots across 2025 or five selected
September 2026 days. Exact pinned diagnostic coordinates are shown, with a
fixed sample-set scale, source algorithm, date, stop reason and source links.
Older analyzed fronts are hidden while diagnostics play. Share URLs preserve
sample set/date; diagnostic detail links open the same date. Playback stops
on card changes, reset, disclosure close or hidden document.

Playback advances by sample, not elapsed time. Calendar gaps and processing
changes are explicit. No interpolation, seasonal climatology, physical current
endpoint or annual length/width extrema is inferred. These are existing
samples, not new acquisitions; coverage and canonical release unchanged.

Verification: all 17 exact geometries and sample metadata, shared-date
restoration, playback lifecycle, stable scale, 320 px layout and identity
boundary in analysis/test_atlas_timeline_browser.py; saved surface selection
and global atlas regressions pass. Mobile screenshot inspected:
figures/atlas-timeline-review.png. Seven-role review:
signals/roles/check/atlas-saved-sample-playback-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite claim.


## 2026-10-03 - Dated diagnostic state-to-atlas navigation

Each saved Gulf Stream System diagnostic card now lists its dated OSW
line intersections, with approximate clipped segment lengths and exact
predicate. State links preserve the selected sample date and series. State
inventories offer reverse atlas links for all 36 pinned dated intersections
across the 17 samples; the incoming date is visibly marked. All 56 states
are covered by the reverse view, including explicit unresolved absence for
states with no recorded diagnostic line intersection.

Relations remain partial diagnostic lines clipped by approximate state
shapes, not physical current passage, footprints, containment or annual
extrema. Processing labels remain date-specific. Optional sample-set failures
leave other state inventories available. Canonical science and route coverage
unchanged; no new provider acquisition.

Verification: analysis/test_atlas_sample_states_browser.py checks all 56
states / 36 relations, NAST W state-atlas-state round trip, requested date,
320 px layout and HTTP 503 fallback. Extended timeline browser check passes
all 17 per-frame state lists and prior geometry/playback checks. Screenshot
inspected: figures/atlas-sample-state-links-review.png. Seven-role review:
signals/roles/check/atlas-dated-state-round-trip-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite claim.


## 2026-10-03 - Antilles local-section provenance recheck

Rechecked Meinen et al. (2019) NOAA repository and AOML copies. The 49.4 km
coastline-to-site-B transport integration span is Table 3, not Table 5.
Corrected active source locators in the scope audit, public note, route
planning and width inventory; retained correction history. Table 1 nominal
A/A2/B/C instrument coordinates and the local mean peak around 400 dbar are
now structured in the receipt. Surface-to-1000-dbar/bottom integration bounds
are explicit. None is an along-stream endpoint or diagnosed current width.
Weak August-September transport seasonality does not supply animated axes.

Antilles whole length, width, annual ranges and route remain unresolved.
Coverage unchanged: 55 candidates / 53 of 89 / 36 pending / 3870 scenarios;
13 scoped width records, 21 current scope notes. No new scientific admission.
Verification: 27 focused dashboard/width/catalog unit tests, complete protocol
and width audits, all 21 source-scope browser cards including mobile. Review:
signals/roles/check/antilles-section-locator-correction-roles-check-2026-10-03.md,
21 findings, 0 P1, 1 addressed P2, 20 P3 conditions. No full-suite claim.


## 2026-10-03 - Guiana naming and continuity in the atlas

Guiana/Guyana source conventions now appear in a public source-scope card,
with related North Brazil navigation. The audit separates local shelf evidence,
offshore ring motion and a source-specific continuation label. Baklouti et al.
(2007) relevant sections were read; the evidence does not establish a universal
axis. Local non-detection is not global absence. No annual playback inferred.

Current source-scope reviews: 22. Length, width and route coverage unchanged:
55 candidates / 53 of 89 / 36 pending / 3870 scenarios. Guiana receives no
North Brazil dimensions or route; canonical ledger hash unchanged.
Verification: 16 focused dashboard/catalog unit tests, full protocol audit,
all 22 source-review cards with mobile and related navigation. Review:
signals/roles/check/guiana-source-convention-continuity-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite claim.


## 2026-10-03 - Atlantic NECC western summer reach and mean section widths

Added declared 42 W-32 W western summer study reach: approximately 1100 km,
1100-1200 km scenario envelope; raw nominal 1108.057 km, 81 cases. Longitude
gates follow study sections; latitude gates and bends are editorial. Branch
correspondence unresolved; source fall merging is not transferred to summer.
Source summer label remains JAS. This reach is outside comparable route
ordering and published-length ranking.

Added two scoped mean-field zero-contour section widths, about 860 and 920 km
at 42 W and 32 W. Width protocol v1.7 distinguishes boundaries found after
velocity averaging from the average of instantaneous widths; section values
are not a seasonal interval or width of the selected route. Playback disabled.
Canonical whole widths and annual length/width ranges remain unknown.

Coverage: 56 candidates / 54 of 89 / 35 pending / 3951 scenarios; 39 comparison
routes and 17 studied reaches. State join 112 pairs in 43 states. Widths:
15 scoped records / 11 names, 85 unassessed. Current source reviews: 23.
Canonical ledger unchanged. Verification: 36 focused unit tests, complete
route and width audits, direct card/mean-section/mobile browser checks, all
112 route/state links and 23 scope previews. Screenshot inspected:
figures/atlantic-necc-western-summer-review.png. Review:
signals/roles/check/atlantic-necc-western-summer-mean-width-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite claim.

## 2026-10-03 - New Guinea local seasonal direction

Added NGCC local direction view at 141.4 E, 1.7 S using Zhang et al. (2020).
November–April southeastward and May–October northwestward come from the
three-cycle monthly composite. El Niño exception is separately selectable
and excluded from seasonal playback. Map arrow is an illustrative local
symbol; no route, seasonal length/width or annual extrema inferred. Upper
30 m removal, instrument outage, limited record and coarse coastline noted.

Added New Guinea Coastal Intermediate Current as the 22nd proposed name,
with source and unresolved layer/extent gates. NGCC, NGCUC and intermediate
flow remain distinct; canonical 100 names and length ranking unchanged.
24 current source-scope reviews now appear on the atlas. Route coverage
remains 56 candidates / 54 of 89 / 35 pending; widths remain 15 records for
11 names. Refreshed seasonal-route width dependency SHA.

Verification: 13 focused dashboard/seasonal-frame unit tests; seasonal route
validator; NGCC month/exception/cleanup/proposal/mobile browser checks and
all 24 atlas source-review previews. Screenshot inspected:
figures/ngcc-seasonal-direction-review.png. Internal roles receipt:
signals/roles/check/ngcc-seasonal-direction-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite claim.

## 2026-10-03 - South Indian eastern-convention regional reach

Added declared 70–90 E studied reach: approximately 1700 km, 1600–1800 km
editorial sensitivity envelope; raw nominal 1707.653 km from WGS84 legs.
Three shapes and independent endpoint-latitude offsets give 27 cases with
longitude gates held fixed. Every latitude and connecting bend is editorial.
Older broad SIOC naming and later east-of-70-E convention remain visible.
Upper-1000 m historical transport is not a uniform-depth axis; source access
receipt separates inspected text/captions from indexed abstract and blocked
publisher retrieval. No source schematic or field digitized.

Excluded from comparable reference order and canonical ranked measurements.
Western ARC, recirculation and northeastern continuation lengths are not added.
ISSG and SANT 27/27 are coarse display crossings, not observed passage.
Annual length/width and whole-current dimensions remain unknown; static route
context in seasons does not enable playback.

Coverage: 57 candidates / 55 of 89 / 34 pending / 3978 scenarios; 39 comparison
routes, 18 studied reaches; 114 candidate/state pairs in 44 states, 25 source
reviews, 22 proposed additions. Width evidence unchanged: 15 records / 11 names.
Canonical current ledger unchanged. Verification: 23 focused unit tests,
complete route protocol audit, focused current browser/mobile checks, all
114 atlas route/state links and 25 scope previews. Screenshot inspected:
figures/south-indian-eastern-reach-review.png. Internal review:
signals/roles/check/south-indian-eastern-reach-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite claim.

## 2026-10-03 - South Pacific eastern frontal-proxy reach

Added declared 103–88 W studied reach between two reported STF crossings:
approximately 1400 km, 1300–1500 km editorial scenario envelope; nominal
1384.703 km, 27 cases. P18 crossing at 103 W 33.8 S was sampled February–April
1994; P19 at 88 W 34.5 S in February–April 1993. Source frontal locations are
not velocity-core endpoints or one dated axis. Intermediate vertices and
scenario offsets are editorial. Branch correspondence remains unresolved.

Protocol v1.2 M02/M03 clarification now records structured frontal anchors,
month-precision sampling windows and explicit proxy roles. Validator rejects
role relabeling, unsupported nominal vertices, duplicate anchors and invalid
or reversed dates. Full route card lists both sampling windows. Temperature
criterion at 150 m does not set axis depth; frontal band does not set width.
Ridgway/Dunn 2007 layered-flow limitation is included. No source field or
curve digitized; 1995 full-paper access limitation retained.

Coverage: 58 candidates / 56 of 89 / 33 pending / 4005 scenarios; 39 comparison
routes, 19 studied reaches; 115 route/state pairs in 45 states, 26 current
source reviews and 22 proposed additions. HUMB contact is display geometry
only. Widths remain 15 scoped records / 11 names; canonical current ledger
and published ranking unchanged. Annual length/width ranges remain unknown.

Verification: 24 focused protocol/catalog/dashboard unit tests, final protocol
mutation checks, complete route audit, focused atlas/card/source chronology/
mobile checks, all 115 route/state links and 26 source previews. Screenshot
inspected: figures/south-pacific-front-reach-review.png. Internal review:
signals/roles/check/south-pacific-front-reach-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite claim.


### Tasman Front composite and continuity scope — 2026-10-03

Added research/tasman-front-composite-continuity-scope-audit.json and visible
atlas evidence summary. Historical satellite/cruise source sets, unsynchronized
years, 164–166 E coverage gap and printed duration/date discrepancy are retained.
Oke et al. (2019) indexed abstract/Introduction question a persistent narrow
central front; direct full-paper access failed. Tilburg et al. (2001) original
PDF Introduction/figure caption read; no curve or field digitized. Alternative
EAC naming is a source proposal, not an admitted alias.

Protocol v1.2 now clarifies historical composites and contested continuity:
choose a historical composite, dated jet, mean connection or transport corridor
before measuring; meander bands are not widths and reference depth is not axis
layer. No route forced, no annual geometry enabled. Source reviews increase to
27; coverage remains 58 candidates / 56 of 89 / 33 pending / 4005 scenarios.
Canonical ledger, width inventory and published ranks unchanged.

Verified ten dashboard unit tests, direct Tasman deep link and separate EAC
navigation, all 27 source previews/mobile reflow, complete regenerated protocol
audit and inspected figures/tasman-front-scope-review.png. Internal .roles
review: signals/roles/check/tasman-front-continuity-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. Full repository suite and
independent scientific admission remain unclaimed.


### Monsoon Current Sri Lanka seasonal reaches — 2026-10-03

Added separate eastward June–September and westward November–February editorial
77–83 E regional routes. Summer drawing: about 800 [700,900] km; winter: about
700 [600,900] km; 27 scenarios each. Longitude gates and bends are editorial;
local historical sections do not establish regional dated axes. Both routes
are studied reaches outside published ranking. Five seasonal route frames now
cover three currents; Monsoon playback switches phases without interpolation.
Transition geometry, widths and annual dimensions remain unknown.

Schott/McCreary (2001) original PDF section 5.1.5 and Figure 48 caption read;
Schott et al. (1994) indexed abstract only, full-paper access limitation stated.
Summer near-coastal westward flow, subsurface counterflows, equatorial jets and
upstream/downstream branches excluded. Southwest/Northeast Monsoon Current
names are phases of the existing record; no canonical identities added.

Seasonal validator now supports east/west with endpoint orientation checks and
source-label/calendar agreement. Mutation tests reject reversed direction and
unsupported months. Phase labels and playback explanation updated. Source audit:
research/monsoon-sri-lanka-seasonal-layer-scope-audit.json.

Coverage: 60 candidates / 57 of 89 / 32 pending / 4059 scenarios; 39 comparison
routes, 21 studied reaches; 117 route/state pairs in 46 states; 28 current scope
reviews, 22 proposed additions. Width inventory and published lengths unchanged.
Canonical current ledger SHA checked unchanged.

Verified 28 focused protocol/catalog/dashboard/seasonal-frame unit tests,
complete route audit, five-frame validation, focused atlas/card/playback/mobile
check, all 28 source reviews and 117 route/state links. Screenshot inspected:
figures/monsoon-seasonal-reach-review.png. Internal .roles receipt:
signals/roles/check/monsoon-sri-lanka-seasonal-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. No full-suite or independent
scientific-admission claim.


### Indian EUC dated subsurface band — 2026-10-03

Added a local descriptive current/salinity-band span at 90 E for 1–3 March
2017: source latitude limits 1.2 S–1.5 N in the 80–150 m depth range, WGS84
298.5511199778176 km, reported approximately 300 km. This differs from the
2 S–2 N survey support, salinity transport domains and velocity-defined full
width. No uniform-depth width, mapped footprint, annual range or route admitted.
Siswanto/Kusmanto/McPhaden (2019) original PDF text Methods/Results/Conclusions
read; no figure digitized. Historical review stresses transient definitions and
warns against inferring connected extent from local observations.

Width protocol v1.8 adds dated_band_section with explicit latitude/depth/date
support, reproducible conversion and inference guards. Existing metrics and
values unchanged. Width table/seasonal view label the band metric and omit its
full-width bar; playback disabled. Source audit and atlas scope note added;
route planning now requires compatible longitudinal and overlying profiles.

Coverage: 16 scoped width records / 12 names, 84 names unassessed; one derived
series and three nonnumeric reviews retained. 29 current source-scope cards;
60 route candidates / 57 of 89 / 32 pending / 4059 scenarios unchanged. Canonical
ledger SHA verified unchanged; published ranking and release unchanged.

Verified 28 focused width/dashboard/seasonal-frame tests, complete width and
route audits, five-frame validation, focused dated-band/source/mobile browser
checks and all 29 source cards. Screenshot inspected:
figures/indian-euc-dated-band-review.png. Internal .roles review:
signals/roles/check/indian-euc-dated-band-roles-check-2026-10-03.md,
21 findings, 0 P1, 2 addressed P2, 19 P3 conditions. Full-suite and independent
scientific-admission claims remain open.


### Dated section locator on the custom atlas — 2026-10-03

Indian EUC selection now fits the 90 E dated latitude span and opens its
section-map card. A keyboard/clickable dashed blue locator and labeled card
bracket show geographic support, not current axis, velocity edges or footprint.
Dates/depth/definition remain beside the map. The same component appears in the
seasonal explorer; unrelated phases clear it. Existing atlas-feature deep links
restore this card, and Global view restores the world map.

Added deterministic coastline-only closeup background using the same OSW
projection/land geometry. Section closeups omit oversized province labels and
graticules; other atlas views retain their existing ground. SVG focus outline
was also oversized at this zoom; explicit contrasting stroke/shadow now retains
keyboard focus without obscuring the locator. Source role/date labels remain
in accessible names after dashboard update rendering. Width-load failure remains
optional to atlas navigation; invalid section roles suppress the locator.

Verified focused section/deep-link/keyboard/reset/stale-selection/mobile and
invalid-role checks, 100-current/140-eddy atlas regression, 29 source previews
and ten dashboard tests. Final screenshot inspected:
figures/indian-euc-atlas-section-review.png. No new scientific dimensions,
canonical data, ranks or release changes. Internal .roles review recorded in
signals/roles/check/dated-section-atlas-roles-check-2026-10-03.md.

## West Australian historical dimensions and source access — 2026-10-03

The West Australian atlas card now distinguishes the modern broad northward
offshore definition from Andrews (1977)'s cyclonic stream turning poleward.
The indexed abstract's 800 km trough extent, 100–200 km stream width and
370 m scale depth remain unadmitted historical source context. The full 1977
paper was unavailable; identity equivalence and its measurement methodology
remain unreviewed. None of these values enters current length ordering, width
measurements or annual ranges. The 2016 Leeuwin pathway paper's Introduction
and methods sections were inspected; modeled release/sector boundaries and
transport validation do not supply a West Australian axis or width.

Source-scope cards support additional citation links with passage locators and
explicit access limits. Dashboard generation rejects missing access/locator
metadata and non-HTTPS supporting URLs. West Australian links to the separate
Leeuwin record; related navigation does not copy its route or dimensions.
The shared measurement protocol clarifies historical name conflicts and why
transport agreement alone cannot validate width. This clarifies M01/M03/M09
under v1.2; no calculation, rounding or comparison rule changed.

Verification: 11 dashboard unit tests including malformed citation metadata;
all 29 source-scope previews at 320 px; direct West Australian source-link,
keyboard Leeuwin navigation and no-borrowed-route checks; full protocol audit
60 candidates / 4059 scenarios. Screenshot inspected:
`figures/west-australian-historical-dimensions-review.png`.
Counts remain 60 routes for 57 of 89 remaining-length names, 16 scoped width
records for 12 names, and 240 dashboard records. Canonical ledger SHA remains
6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e.
Internal role review is editorial; independent scientific admission remains open.

## Indian SEUC March–May reach and spatial core widths — 2026-10-03

Added a 60–105 E March–May subsurface studied reach for the Indian Ocean
South Equatorial Undercurrent. Source approximate longitude/latitude context
supports editorial connecting vertices, not an extracted velocity axis.
BRAN2020 density-layer context and 2001–2018 climatology remain explicit.
WGS84 nominal length is 4951.567 km, reported as approximately 5000 km;
27 editorial cases span 4946.549–4959.936 km, outward-rounded to 4900–5000 km.
The reach stays outside reference-route ordering and published length ranks.
Its four coarse map contacts (AUSW, EAFR, IND W, MONS) are display-region joins,
not physical current containment. Coarse land clearance does not verify
ridge-scale bathymetry or current continuity.

Added a separate width metric: maximum meridional extent of the 3D eastward
u>0.1 m/s climatological core at each longitude. Published median 169 km and
spatial range 26–294 km are retained. These are longitude variation, not annual
extrema, fixed-depth full width, flow-normal width or confidence intervals.
Protocol v1.9 adds this class and validates its threshold, temporal averaging,
spatial aggregation, median/range and exclusion flags. Existing 16 records
retain their values/types. Seasonal association width hashes refreshed.
The explorer hides the full-width bar and disables seasonal playback; no
monthly geometry, source contours or model arrays were acquired/digitized.

Primary corrected publisher HTML was inspected in sections 2–4, captions and
erratum. Conflicting 10 N/10 S and May/June mooring-end wording are recorded;
no exact observation day is manufactured. Supporting Information remains
uninspected. The representative isopycnal route and 3D core extent are separate
methods; the local 300–420 m density-layer conversion is not applied uniformly.

Verification: 15 width unit tests and full 17-record width validation; 11
dashboard tests; focused Indian SEUC browser checks and restored Indian EUC
section checks; all 30 scope cards; all 121 route-state links; full protocol
audit 61 candidates / 4086 scenarios; five seasonal-frame validation.
Standalone SVG capture timed out; a normal image document rendered the same
figure successfully. One Indian EUC screenshot capture failed transiently;
the unchanged check passed on rerun. Route/width/atlas screenshots inspected.
No full repository suite or independent scientific admission claimed.

Coverage: 61 candidates for 58 of the 89 remaining-length names; 31 await
routes. 39 comparison routes / 22 studied reaches. 47 states have candidate
contacts, 121 pairs across 56 states. Widths: 17 records / 13 names; 83
unassessed. Dashboard: 240 records / 22 proposed additions; 30 source reviews.
Canonical ledger SHA remains
6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e.


### Indian SECC winter surface reach — 2026-10-03

Added an editorial 50–90 E December–March surface studied reach, approximately
4,400 km with a 4,400–4,500 km drawing-sensitivity envelope (27 scenarios).
Wu et al. (2020) seasonal drifter context includes wind-slip-corrected undrogued
observations; the route is not a traced fixed-depth axis or whole-current length.
The 1993–2018 selection versus 1995–2018 figure-caption discrepancy is retained.
Huang et al. (2023) frequency/phase latitude classification at 80.5 E does not
supply paired current-width edges. Width and annual extrema stay unknown;
ORAS5 upper-30 m versus caption 0–40 m wording is retained in the audit.
One seasonal frame is inspectable; playback is disabled. Related SEUC navigation
opens its distinct subsurface card. No source arrays or contours were acquired.

Verification: 15 width, four seasonal-frame and 11 dashboard unit tests; full
17-record width/six-frame validators; 62-candidate/4,113-scenario protocol audit;
31 scope previews and all 124 route-state links; focused winter browser checks
and inspected atlas/season screenshots at desktop and 320 px mobile reflow.
The first focused assertion expected the seasonal comparison text, but the
width comparability note correctly takes precedence; the assertion now verifies
the displayed annual restriction and separate route sensitivity text.
Coverage: 59 of 89 remaining-length names have drawings, 30 await routes;
39 comparison routes / 23 studied reaches. Widths remain 17 records / 13 names,
82 unassessed and four reviewed without comparable numeric widths. Dashboard
240 records / 22 proposals / 31 source reviews. Canonical ledger SHA unchanged:
6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e.
Internal review is not scientific admission; no publication or remote action.


### Aleutian-region identity separation — 2026-10-03

Added proposed Aleutian North Slope Current as the 23rd source-backed inventory
addition. The Bering-side identity, Aleutian/Subarctic Current and Alaskan Stream
remain separate. Its author-described regional width is retained as source
context outside the canonical width inventory; no new route, ranking, observed
date or annual range. The Aleutian scope audit now records Western Subarctic
SST-front search bounds and warm Isoguchi-jet distinction, plus the source's
167 N versus nearby 167 W wording. Search bounds/gradient fronts are not velocity
axes, current endpoints or paired edges.

Proposal cards now display recorded source-access limits. NOAA relevant HTML
subsections/captions and the Mitsudera et al. (2018) repository PDF introduction,
first Results subsection, Figure 1 caption and Methods Data were read. Reed and
Stabeno (1997) repository abstract only; no full-article claim. PMEL Stream PDF
returned 502 and the 2025 AMS frontal-index page returned 403; neither promoted.
No source field, underlying survey or figure digitization acquired.

Verification: full 62-route / 4,113-scenario conformance audit (23 identities),
11 dashboard tests, all 31 scope previews, and focused Aleutian browser check:
proposal source limits, 100-name selector, unknown route/width/date, 240 dashboard
records, and 320 px reflow. Proposal screenshot inspected. Canonical SHA unchanged.
Coverage remains 59 of 89 with drawings, 30 awaiting routes; widths 17 records /
13 names. Seven-role internal review recorded separately; scientific admission,
field-derived geometry and full repository release gates remain open.


### Proposed-current navigation — 2026-10-03

All 23 proposal cards now support direct fragment arrival, keyboard focus,
shareable card links, same-link reselection and return to the global current
atlas. The Aleutian scope preview links separately to pending Alaskan Stream
and North Slope proposals. These links are validated against pending identities,
resolved to their own labels, and do not increase canonical atlas counts or
borrow geometries/widths. Only notes with pending relations receive the new
resolved metadata; unchanged notes keep their prior fingerprints.

Verification: 12 dashboard unit tests including malformed, missing, canonical
and duplicate proposal-ID rejection; all 31 scope previews; navigation browser
check of all 23 cold proposal links, Back/focus, two mapped route links, keyboard
scope relation, same-link reselection and 320 px reflow. Forced delayed loads
exercise either proposal/catalog completion order. Focus screenshot inspected.
An initial assertion wrongly required the final card to align at 16 px despite
maximum page scroll; the check now also accepts a visible heading at page end.
No runtime failure or additional padding was required. Canonical SHA unchanged;
100 selectable currents / 240 dashboard records / 23 pending additions remain.


### Mauritanian seasonal mean width — 2026-10-03

Added the author-reported 30–40 km upwelling-season mean undercurrent width at
reference 18 N from Klenz, Dengler and Brandt (2018). This is a local seasonal
mean width span, with no manufactured midpoint, confidence interval, annual
extrema, route buffer or fixed-depth edge geometry. Source convention is
December–April; five upwelling cruises sampled January–April during 2005–2011.
The whole study spans 2005–2016, and August 2016 is excluded from either seasonal
mean. Measurements pooled over 17–19 N are remapped by bathymetry to reference
18 N. Those pooling bounds are not an along-current route.

The audit distinguishes poleward surface/subsurface manifestations named MC by
the authors from the equatorward surface shelf jet and deeper return. The 60 km
transport integration window and 200 km surface-flow corridor are not widths.
Relevant primary publisher Introduction, section 2.1/Table 2, section 3.1 and
Figures 4–5 captions, Discussion and Conclusion read; source fields, figures,
paired edges and cruise reports were not acquired/digitized.

Width protocol v1.10 adds seasonal_mean_width_range, with explicit sampling and
mean-section semantics; previous 17 records retain values/types. Initial full
validation rejected the new calendar class until the common calendar gate was
extended to this documented type. Sixteen width tests now include midpoint,
annual relabel, playback, edges, sampling, years and section-support mutations.
Full 18-record width and six-frame validators pass; association hash refreshed.
Twelve dashboard tests, four seasonal-frame tests, all 32 scope previews, focused
Mauritanian browser check and inspected seasonal screenshot pass. Desktop and
320 px checks preserve unknown route/date, hidden bar and disabled playback.
Full route audit remains 62 candidates / 4,113 scenarios; 59 of 89 have drawings,
30 pending. Width coverage: 18 records / 14 names, 81 unassessed, four reviewed
without comparable numeric widths. Dashboard 240 / 23 proposals / 32 reviews.
Canonical SHA unchanged; internal review is not independent scientific admission.


### Atlas and seasonal evidence round trips — 2026-10-04

All 100 current atlas previews and all 62 route cards now link to widths and
seasonal evidence. A card with an associated seasonal route links to that exact
frame; seasonal explorer share URLs retain stable width/frame/direction record
IDs, and the return link selects the same current and seasonal route in the
atlas. Switching current clears an incompatible phase; phase selection and
playback replace the share URL without adding history entries. Unsupported
phase IDs normalize to the selected current's available state or disappear when
no state exists. Empty evidence remains unknown; links do not imply animation
availability, a full annual cycle or new measurements.

Verification: browser checks of all 100 atlas links, 62 route-card links, all
26 selectable recorded evidence IDs and six seasonal atlas round trips;
Monsoon winter-to-summer URL changes, current switch/reset, unknown-current
phase rejection and 320 px reflow. Mobile screenshot inspected. Existing two
mapped route and all 23 proposal deep-link/history checks pass, including delayed
loads; all 124 route/state links and optional-data fallback pass. No scientific
data values/types, canonical counts, rank or ledger SHA changed. This is local
navigation work, not scientific admission or a published release.


### Atlantic SECC reported March band — 2026-10-04

Added the Bourles et al. (1999) March 1994 section at 30 W, 6-8 S:
about 220 km WGS84 meridional band span (221.1817565 km before 10 km
rounding). This is an author-described band, not fixed-depth full width.
Two eastward cores near 40 and 240 m are separated by westward flow near
110 m. Exact local days, longitudinal continuity and annual ranges remain
unresolved. The nearby western non-detection does not establish basin-wide
reversal. The separately named Atlantic SEUC retains its own identity.

Protocol v1.11 records reported limits and distinguishes the computed midpoint
from an observed center. Atlas and seasonal explorer show scope/source links;
this view has no full-width bar, route or seasonal playback. Width coverage is
19 scoped records for 15 names; 80 unassessed and four reviewed without a
numeric metric, plus one derived series awaiting admission. Route coverage
remains 62 candidates for 59 of 89 pending-length names, with 30 pending routes.

Checks: width validator, 17 width/12 dashboard/four seasonal-frame unit tests,
focused Atlantic SECC browser, 33 scope reviews and navigation across 27 phases
pass. Internal seven-role review records 21 findings, three addressed P2 and
remaining source/admission conditions. No full-suite or independent scientific
approval claimed. Canonical almanac SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

Artifacts: `research/atlantic-secc-march-1994-section-scope-audit.json`,
`analysis/test_atlantic_secc_band_browser.py`, and
`signals/roles/check/atlantic-secc-march-band-roles-check-2026-10-04.md`.


### Reported month-section geography — 2026-10-04

The Atlantic SECC March 1994 band now has a map locator at 30 W, 8-6 S
in the global atlas and seasonal evidence card. Selecting its dashed locator
zooms to the reported section and opens its mapped card. Month precision and
unresolved exact days are explicit; this adds no current axis, footprint,
full-width claim or annual series. Center/span-only conversion records do not
supply map boundaries. The existing day-dated Indian EUC locator is preserved.

Atlantic and Indian focused browser checks cover keyboard activation, global
return, deep-link restore, view fitting, stale-section clearing and 320 px
reflow. Invalid-input checks reject forged date, center and edge roles. Both
Atlantic screenshots were visually inspected. Coverage stays at 19 scoped
width records for 15 names and 62 route candidates for 59 names. Internal
seven-role review: `signals/roles/check/reported-month-section-locator-roles-check-2026-10-04.md`.


### Antilles observed-section acquisition — 2026-10-04

Acquired and pinned NOAA/AOML final AB0505 LADCP text profiles: 57 casts,
22,619 depth samples, 40 provider-usable and 17 caution profiles. Source
assessment identifies casts 24-36 with no LADCP data. Dates/positions assign
23 casts to the first Abaco occupation (May 4-8, 2005), 27 to the repeat
(May 18-23), and seven to other sections excluded from this diagnostic.

The 400 m instrument-depth diagnostic leaves the first offshore boundary
unresolved under quality gates. The repeat produces 37.352311 km before
rounding: a sampled-peak-to-offshore-half-peak span, not full width. Its station
bracket distances are 34.55-50.27 km, describing sampling support rather than
confidence or annual variation. Tide removal is no, and error velocities and
quality comments are retained. Whole-current and annual dimensions remain null.

`almanac/antilles-sections.html` compares the two occupations and maps cast
positions, with hover/focus names, UTC timestamps and quality/velocity table.
The Antilles atlas card now contains a mapped observation card and a two-survey
selector. Its 23/27 instrument positions appear in both the atlas and card;
background reference routes fade while observations are selected. Saved links
and the detailed page's return link preserve the selected occupation. Global
view and selection changes remove the observation overlay, including delayed loads.
The dashboard fingerprints this two-occupation series. No canonical width or
route admitted: coverage remains 19 scoped width records for 15 names, 62 route
candidates for 59 of 89 names and 30 pending routes.

Regenerate offline with `python analysis/build_antilles_ladcp_section_diagnostic.py`.
The initial acquisition command is explicit and refuses to overwrite pinned
manifest data. Five data tests, 14 dashboard tests and the focused browser
check pass. Inventory/calculation/SVG regenerate byte-identically; page screenshot
inspected and canonical almanac unchanged. Internal seven-role review records
21 findings with three addressed P2 and scientific admission conditions.
Protocol: `plans/antilles-ladcp-section-diagnostic-protocol-v1.md`.
Review: `signals/roles/check/antilles-observed-section-acquisition-roles-check-2026-10-04.md`.

### Mapped eddy cards — 2026-10-04

All 140 eddy/detection selections now have an inline SVG map using their stored
point or outline. The card's extent stays fixed during main-map navigation.
Point names remain hover/focus only; geometry-role explanation and scoped state
links remain beside the map. Shared gateways never acquire fabricated centers.
Small outline views omit coarse state shading using the existing coastline
context layer; geographic precision is unchanged. Changed inventory records
receive an amber card border and textual update description.

Focused browser verification covers 140 maps / 131 scoped state links, bounds,
geometry class, saved-view restoration, zoom/reset, update isolation, focus and
narrow reflow. No canonical measurements, source observations or geometry added.
Review: `signals/roles/check/mapped-eddy-cards-roles-check-2026-10-04.md`.

### Persian Gulf outflow source dimensions — 2026-10-04

Scope review 34 adds hydrographic-core support in a separate source-audit
product and six-row atlas table. Its section-distance coordinate is not a new
route, and its water-mass width is not a velocity envelope or annual span.
Scope changes participate in existing source fingerprints and update lights;
width and route capabilities remain unchanged pending admission. Date/distance
source discrepancies stay visible in the audit. No canonical data modified.

### Hydrographic core width inventory integration — 2026-10-04

Six Persian Gulf core extractions now use `campaign_hydrographic_core` in the
shared width inventory. Updated coverage: 25 scoped records / 16 names / 79
unassessed / four reviewed nonnumeric / one derived series pending review.
Dashboard width presence includes the six source records; route and annual
capabilities remain unsupported. Spatial/occupation records cannot play as a
seasonal movie. Record URLs restore each selection; the upstream range keeps
its regional-span role. The protocol/audit hashes are checked offline.

Checks: 18 width tests, 15 dashboard tests and six-record browser pass; canonical
SHA256 unchanged. Internal review:
`signals/roles/check/hydrographic-core-width-integration-roles-check-2026-10-04.md`.

### Red Sea REDSOX reach scope — 2026-10-04

Scope review 35 records an author-reported approximately 130 km winter
descending-plume reach and three local branch/product components. The dashboard
fingerprint includes the audit; inventory edits can light its existing marker.
No current axis, whole-current length, numeric current width or seasonal route
capability is added. Channel dimensions remain separate geographic context.

Width status is now 25 records / 16 identities / 78 unassessed / five reviewed
nonnumeric / one derived series pending admission. Routes remain 62 candidates
/ 59 of 89 names / 30 pending / 4,113 scenarios. Three source-scope tests,
18 width tests, 16 dashboard tests and the 35-card scope browser check verify
the focused change. Canonical SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.
Internal review: `signals/roles/check/red-sea-redsox-branch-reach-roles-check-2026-10-04.md`.

### Tsuchiya angular width integration — 2026-10-04

Two current-linked records share Rowe et al. (2000)'s general 2-degree
meridional width statement; their claim ID prevents interpreting them as
independent measurements. Original angular units and approximately 220 km
conversion remain visible. No exact section location, annual extrema or
secondary-branch width added. Static studied-route context remains separate.

Coverage now 27 scoped records / 18 identities / 76 unassessed / five reviewed
nonnumeric / one derived series pending admission. All 35 scope-reviewed
identities remain represented. Scope audits and shared width records enter
existing dashboard fingerprints. Focused validation: 19 width tests, 17
dashboard tests and both-current browser navigation/reflow. Canonical ledger
unchanged. Review: `signals/roles/check/tsuchiya-angular-width-roles-check-2026-10-04.md`.

### Pacific NECC 2013 section series — 2026-10-04

New pending diagnostic: 72 pinned OSCAR timestamps, twelve local monthly mean
profiles at 140 W, paired first-zero-crossing boundaries and two alternative
thresholds. These add a scoped candidate series and twelve time samples to this
current's dashboard; actual source/diagnostic hashes enter measurement and time
fingerprints. The series does not establish a ranked length, canonical width,
climatology or annual whole-current extrema. Saved visual page:
`almanac/necc-section.html`, linked from the atlas and width-decision table.

Width inventory: 27 source records / 18 identities / 75 unassessed / five
reviewed nonnumeric / two derived series pending admission. Canonical ledger
and reference routes unchanged. Focused verification: five diagnostic tests,
19 width tests, 18 dashboard tests, deterministic JSON/SVG rebuild and both
atlas/width-inventory navigation paths on desktop and mobile. Review:
`signals/roles/check/pacific-necc-monthly-section-roles-check-2026-10-04.md`.

### Monthly section card navigation — 2026-10-04

The Pacific NECC series now has an inline selector, plot and section map inside
its atlas card. Saved months are shareable and survive standalone-page return.
Explicit playback stops at the last record and on hidden/switch/reset state.
The dashboard's existing source hashes and series capabilities remain unchanged;
no additional measurements or inferred current geometry added. Grid points and
boundary marks retain product/diagnostic meaning. Three focused browser checks
pass: monthly inline card, existing Antilles observed card and standalone NECC
page. Internal review:
`signals/roles/check/necc-inline-monthly-atlas-roles-check-2026-10-04.md`.


### Searchable atlas inventory index — 2026-10-04

The global atlas now provides a compact searchable index for every existing
100 current, 136 named eddy and four dated detection records. Search matches
names and map evidence; filters distinguish currents, eddies/detections and
records changed since the shared saved dashboard baseline. Index activation
uses the existing atlas selection handlers, opens the same card and brings the
map workspace into view. World reset clears the active index state; marking
updates seen and cross-tab baseline changes refresh update indicators.

Map evidence labels distinguish reference routes, dated geometry, reported
centers, locators and shared gateways. Index coverage is identity coverage;
it adds no observed geometry or measurements. Map labels remain hover/focus
only. The complete index remains available when markers overlap, including the
100 names using a shared regional eddy gateway. Tests cover all 240 unique
entries, name/evidence search, filtered counts, current and gateway card
activation, keyboard access, active state/reset, amber update filtering and
acknowledgment, empty results and 320 px reflow. Screenshot:
`figures/atlas-directory-review.png`. Canonical ledger unchanged.

### OSW state filter in the global atlas index — 2026-10-04

The index now filters existing identities by all 56 OSW states using the saved
reference-route scenario join and each eddy's saved state evidence. For currents,
labels distinguish nominal reference-route crossings from alternative-only
crossings. Multiple route components deduplicate to one current identity in the
index. Eddy labels retain their source relation and observation date, including
shared gateways, geography locators and dated outlines. Absence from the index
is absence of recorded evidence, not proof of physical absence or containment.
The selected state page is linked from the filter context.

`atlas-state` persists in current/eddy view links and reloads with the selected
card. World reset clears the feature while retaining the index's state filter.
Invalid states fall back to all entries; unavailable route joins display an
explicit incomplete-current-links message while keeping saved eddy links usable.
The state filter narrows the index; it does not remove other geography from the
world map. It adds no physical intersections, geometry, canonical measurements
or release records. All 56 resulting identity sets were compared against the
saved route and eddy evidence. Browser checks additionally cover nominal versus
alternative wording, dated detections, gateway cards, state/card restoration,
invalid/missing join handling, empty results and 320 px layout. Existing complete
240-entry search/update checks also pass. Screenshot:
`figures/atlas-state-directory-review.png`.

### Clickable OSW regions in the atlas — 2026-10-04

The existing 56 province shapes now form a keyboard/pointer navigation layer
beneath current routes and eddy markers. Activation clears the selected feature,
retains the world map, sets the state inventory filter and brings its evidence
list into view. Selection synchronizes in both directions with the dropdown and
restores from `atlas-state`. The geometry is copied exactly from the saved atlas
ground; no new boundaries or intersections are inferred. Shapes remain approximate
cartograms. An ocean mask and even-odd ocean clip exclude the saved land shapes
from visible state fills and pointer hit testing. Names use hover titles and
accessible keyboard labels; no persistent map text added.

Missing or invalid state geometry leaves the directory usable with an explicit
fallback message. Verification compares all 56 path strings against the saved
SVG, exercises keyboard selection for each state, physical pointer selection,
three interior-land exclusion points, current marker activation, dropdown/map
synchronization, reload and unavailable geometry. The 56-state evidence-set
browser test and monthly profile playback/navigation regression also pass.
Screenshot: `figures/atlas-clickable-states-review.png`. Canonical ledger and
source inventories unchanged; this is atlas navigation, not new ocean evidence.

### Atlas state navigation role review — 2026-10-04

Seven installed role lenses reviewed the index/state interface: 21 findings,
five P2 issues addressed. Optional geometry no longer blocks core control
initialization; malformed/empty shapes are rejected. Deliberate region activation
focuses the state selector, and initial delayed card reveals stop after user
interaction. Existing card share links track state dropdown changes. Three
focused browser checks and four JavaScript syntax checks pass. Full repository
publication and independent scientific/human accessibility reviews remain pending.
Receipt: `signals/roles/check/atlas-inventory-state-navigation-roles-check-2026-10-04.md`.

### Labrador regional source width — 2026-10-04

An approximately 50 km regional main slope-current description enters the
editorial width inventory and existing Labrador measurement fingerprint.
No canonical width, physical state intersection, new reference route or ranked
length is added. Nearby 300–1000 m contours remain bathymetric context, not
current measurement depths; regional 60 N–43 N limits are not paired width
edges. Exact dates, layer, boundary threshold and annual extrema remain null.

Source access is explicitly publisher-indexed section 4.2 paragraphs 29–33;
direct publisher access returned 403 and the repository PDF was not acquired.
Protocol v1.15 and pinned audit protect the extraction. The existing 17-frame
Gulf Stream series receives only a refreshed general-protocol hash, with its
numerical frames unchanged. Coverage: 28 source records / 19 identities /
74 unassessed / five reviewed nonnumeric / two derived pending review.
Verification: 20 width tests, 18 dashboard tests, inventory and section-series
validators, Labrador browser checks and existing Tsuchiya browser regression.
No full-suite or clean-release claim. Canonical ledger SHA256 unchanged.

### North Brazil–Guyana oblique mean section widths — 2026-10-04

Dimoune et al. (2023) supplies three source mean-width values: NBC1/HS1 about
520 km, NBC2/HS2 about 220 km and NBC3/HS3 about 440 km. They are cross-section
zero-contour spans of the January 1993–December 2017 mean rotated surface
geostrophic component, not instantaneous widths, seasonal extrema or current
lengths. HS1–HS3 use a 45-degree rotation. Source kilometre values are retained;
oblique latitude coverage is not converted as a meridional section.

NBC1/2 attach to North Brazil; NBC3 attaches to Guiana under the source's Guyana
continuation naming convention. The HS3 band straddles 10 N; no hard physical
boundary or canonical alias merge is admitted. Exact section longitude/endpoints
and boundary geometry remain unextracted. The mean-width table lists NBC2 about
220 km, while section 4.1 says 20 km in a different comparison. This unresolved
prose/table discrepancy is shown; it is not a 20–220 km uncertainty interval.

Protocol v1.16 and pinned audit:
`research/north-brazil-guiana-oblique-mean-width-scope-audit.json`.
The seasonal explorer displays mean oblique sections with no edge locator,
full-width bar or playback. Existing contextual routes retain their own scope;
Guiana still has no route estimate. Width coverage is 31 records / 21 names /
72 unassessed / five reviewed nonnumeric / two derived series pending review.
Canonical ledger, 11 published length ranks and 62 route candidates unchanged.
The Gulf Stream series receives only a new general protocol hash; its numerical
frames remain unchanged. Source review covers publisher HTML relevant sections
and indexed publisher PDF table text; no raw data or source figure digitization.

Verification: 21 width tests, 18 dashboard tests, both width provenance validators,
three-record browser checks (saved view, identity/scope/conflict, atlas/table
navigation and 320 px reflow). No complete release-gate claim; scientific
measurement/identity admission remains pending. Visual receipt:
`figures/guiana-oblique-mean-width-review.png`.

### Published widths inside current atlas cards — 2026-10-04

All 100 current cards now include a published-width evidence section. The 31
editorial source records across 21 names appear as compact expandable entries,
with source value/units, metric and phase visible in the summary. Expanded entries
retain geographic scope, layer, boundary rule, time convention, range meaning,
quality notes, full citation and paragraph locator. Each links to its exact
record in the seasonal inspector and its published source. General angular
summaries retain original degrees with a labelled kilometre conversion.

No new measurements, ranges, geometry or canonical admission added. Unknown
cards distinguish unresolved published widths, derived candidates and reviewed
nonnumeric source decisions; missing evidence is not zero width. A missing width
inventory retains the current map card and a detailed-page fallback. All 100
cards and every unique source-record link/definition were checked; keyboard
expansion, source discrepancy visibility, inspector return, world reset and
320 px reflow pass. Screenshot: `figures/atlas-inline-width-review.png`.
# Dashboard identity links open mapped cards — 2026-10-04

Dashboard card titles and selected map/schematic record titles now link to the
same `reference-routes.html?atlas-feature=…#route-atlas` selection used by
Explore atlas. Object record remains explicitly available in selected map
details and each card's evidence disclosure. This makes clicking the current
name follow the user's global-map-to-mapped-card navigation.

`analysis/test_dashboard_atlas_navigation_browser.py` verifies all 240 title
destinations and retained object-record URLs, plus actual Portugal and a dated
eddy navigation, map fit, reload restoration and World reset. Node syntax check
passes. No identity, geometry or measurement data changed.


## Touch zoom in the current atlas — 2026-10-04

The custom atlas now tracks two active pointers for pinch zoom and moving-center pan, keeps the selected card and URL, and clears gestures on pointer cancellation. One-finger/mouse drag captures the pointer after its movement threshold; taps still activate current markers. Visible instructions include pinch and keyboard controls. No data or geometry changed.

Verified with actual Chromium touch events in `analysis/test_atlas_touch_zoom_browser.py`: pinch scale and center, card retention, cancellation, subsequent marker tap, keyboard zoom and Global view. The existing full atlas browser regression passes using the bundled headless Chromium. Its pointer checks now scroll the map into view and its scroll assertions use reduced motion to avoid sampling an in-progress smooth scroll. Node syntax passes and the canonical almanac SHA256 remains unchanged.

## Shared atlas framing — 2026-10-04

Atlas URLs now retain bounded display framing in `atlas-view=x,y,width,height`, alongside the selected current/eddy, component, dated geometry or section. Zoom/pan updates the address and card share link; selecting another identity or Global view clears the previous frame. Valid frames survive reload and late monthly/observed-section initialization. Invalid, nonfinite, out-of-world, undersized and incorrect-aspect frames fall back to ordinary selection fitting. The display frame adds no measured geometry or precision. Width is serialized once and height derived from it to prevent rounding drift on reload.

Verified: `test_atlas_shared_view_browser.py`, the full atlas browser regression, touch zoom, monthly section and observed-section regressions; Node syntax passes. Canonical almanac SHA256 is unchanged. UTF-8 punctuation in the atlas and dashboard HTML was repaired after an encoding error during cache-version edits; subsequent reads explicitly use UTF-8.

## East Australian typical width summary — 2026-10-04

Added a 30 km institutional typical-current-width scalar from NSW-IMOS Node
Science and Implementation Plan 2015-25, dated 25 September 2014, section 3.3.1
(printed page 23). Source: https://imos.org.au/wp-content/uploads/2024/07/NSW-IMOS_Node_Plan_2015-25_Final.pdf .
CSIRO's separate 100 km strong-influence scale is retained in the scope audit,
not merged into a seasonal width range. Typical 200 m depth extent is contextual;
fixed layer, occupied dates and edges remain null. No full width bar, annual
playback or width ranking is inferred. Underlying Mata/Ridgway-Dunn support
remains pending review. PDF text was inspected; screenshot fetch failed.

Width coverage is now 32 records across 22 names; 71 unassessed, five reviewed
without compatible numeric width and two derived candidates. Protocol v1.17
adds institutional scalar rules and refreshed existing derived provenance without
changing numerical frames. Width validator, 22 width unit tests, 18 dashboard
unit tests, 17-frame series validator, EAC browser and all-current inline-width
browser checks pass. Internal roles receipt has three addressed P2 findings;
independent science, human accessibility and full release gates remain pending.

## Leeuwin monthly climatological fitted widths — 2026-10-04

Added a101 April ~132 km and September ~89 km from Deng et al. (2008),
TAO 19, 135-149, doi:10.3319/TAO.2008.19.1-2.135(SA). The published-layout PDF
was acquired, hashed and locally inspected at pages 138, 143 and 144. These are
monthly means of per-cycle fitted surface geostrophic widths at one crossing
near 26 S; the 1.89*L*cos(theta) convention and 43.45-degree angle are retained.
The coefficient is described as approximately half maximum, not exact FWHM.
July/August period-label discrepancies remain explicit. The transport layer,
filter window and RMS variability are separate from width depth, width and
confidence intervals. Other ten months remain unextracted; no annual playback,
full-current width, paired edge geometry or ranking is admitted.

Coverage: 34 width records across 23 currents; 70 unassessed, five reviewed
without compatible numeric width, two derived candidates. Protocol v1.18;
canonical data unchanged. Width validator, 23 width unit tests, 19 dashboard
unit tests, 17-frame validator, Leeuwin browser and all-current inline-width
checks pass. Internal roles review is conditional; independent scientific
admission, human accessibility and complete publication gates remain pending.
Next source step: calibrate and extract the other ten monthly graph values
with extraction margins and a recorded method, without interpolating them.

## Kuroshio regional threshold-width means — 2026-10-04

Three prose values admitted to editorial width inventory: ECS winter 218 km, summer 207 km, study-period mean 210 km. Normal-to-axis 0.1 m/s cutoff and weekly diagnosis-before-averaging are preserved, with unresolved averaging weights and month conventions. Regional tendencies reverse locally; 207–218 km is not a physical annual width interval. Surface field is not the 200 m bathymetric isobath layer. No map edges or full-season playback admitted. Protocol v1.19; source audit/PDF pinned; GS provenance hash refreshed without numerical frame changes. Dashboard validates width inputs and counts two seasonal samples rather than three states.

Coverage: 37 scoped records / 24 names, 69 unassessed, five reviewed nonnumeric, two derived candidates. Passed width validator, 24 width tests, 20 dashboard tests, 17-frame GS validator, Kuroshio source/atlas browser check and JavaScript syntax. Canonical unchanged. Source method/seasonal PDF pages and browser screenshot inspected. Internal role review approved with conditions; independent science/publication gates remain pending.

Final all-current browser run passed: 100 current cards, 37 distinct width records, keyboard source disclosures, inspector roundtrip, reset, mobile and unavailable-width fallback. The test now waits for the rendered inspector value on navigation.

## Kuroshio seasonal profile graph readings — 2026-10-04

Figure 5 inspection: page index 4 has no vector drawings; embedded raster image 104 is 684 by 661. Four geographic axes overlap at native resolution. Full seasonal edge/axis extraction is unresolved; source coordinates or a higher-quality independent source are needed. Figure 6a on page index 5 uses embedded RGB image 112 (960 by 574). Four seasonal width profiles yield 59/64 readable declared samples at 122.5–129.9 E; five color-occluded/ambiguous samples remain null. Pinned calibration, thresholds, raw pixels, image hash and decoder/runtime versions allow deterministic local regeneration.

Chart steps through winter/spring/summer/autumn without calendar interpolation or map morphing. +/-10 km bars are graph-reading allowances, not confidence, physical annual spread or seasonal-width admission. Missing crosses are below the numeric plot and table cells state missing. Dashboard counts four profile views without adding two prose seasonal values; scoped measurement inventory remains 37/24 names. Original prose audit stays immutable. Canonical unchanged. Passed two extraction/mutation tests, twenty dashboard tests, width validator, four-profile browser, prose inspector regression and syntax checks. Internal role receipt approved with conditions; independent science and full release gates remain pending.
