# Rust record store and query interface v1

## Direction

OSW becomes a queryable atlas: choose a question, inspect the matching records,
and open their map or evidence. One Rust engine runs natively and in WebAssembly.
Versioned JSON remains the audited import/export format. Rust owns the loaded
record store, ID indexes, filtering, joins, ordering and pagination.

## First implementation

- Import the complete frozen ledger: entities, sources, claims, relations,
  measurements and geometries; retain original fields and IDs.
- Import the working motion inventory, scoped widths, editorial reference
  routes and recorded state links without promoting editorial evidence.
- Keep collection names and a manifest of source-file SHA256s in each bundle.
  Rebuild explicitly when source artifacts change; no network acquisition.
- Objects join their width IDs, measurement IDs, route IDs, source IDs and state
  codes; state relation kinds remain visible and are not physical containment.
- A structured query supports text, record type, state, evidence presence,
  explicit field filters, sorting, limit and offset. Unknown fields/operators
  or invalid inputs return errors. Queries never execute code or SQL.
- The browser exposes presets, a query builder, result table, selected record
  evidence, an editable JSON query, download and shareable query URLs.
- WASM executes actual queries; a failed WASM load is reported visibly.
  There is no silently divergent JavaScript query engine.
- Native CLI and browser run the same Rust functions and bundle fixture.

## Scientific contract

Missing remains null or absent, never zero. Regional widths retain phase,
boundary, layer, time and source scope. Sorting a scoped scalar does not make
it a whole-current ranking. The object query offers published ranked lengths
and editorial reference-route coverage separately. Grouped gateways, locators,
dated polygons and line/state crossings retain their recorded relation kinds.
Keep canonical release and editorial imports separately identified.

## Storage and migration

The initial engine holds an indexed imported snapshot; the source bundle is
persisted on disk and can be queried offline through the CLI. Revisioned proposed working copies now use the journal described below.
Scientific admission and multiuser service remain subsequent
layers before replacing source-authoring workflows. Larger field grids belong
in external binary assets referenced by stable IDs, rather than duplicated in
every object record. Larger-scale snapshot caching and a richer query language are subsequent
layers, not substitutes for Rust query execution.

## Required proof

Cargo tests for invalid IDs/query inputs, typed filters, state/evidence joins,
missing values, numeric sorting and stable pagination; native queries against
the actual bundle; browser WASM queries matching CLI results, shared queries,
record evidence, source links, narrow layout and explicit failure state.
Preserve the canonical ledger checksum. Independent scientific admission and
full release gates remain separate from software correctness.

## Query-driven maps

The shared Rust engine projects each matching object's stored point, line and
polygon into an SVG scene. The scene contains **all matching objects**, independent
of table limit/offset. Browser code paints Rust primitives, adds pan/zoom, hover
names and record selection. The existing OSW coastline remains the base layer.
Equirectangular coordinates are display coordinates, never length/width inputs.
Longitude seams split line paths; polygons requiring seam clipping are explicitly
omitted from rendering and reported in result JSON until that clipping is built.
No named eddy is assigned an invented footprint: shared gateways stay gateways.

Inspected `bisect-map` in the local apportionment repository: projection.rs,
renderer.rs and Cargo.toml. It supplies a useful display/measurement separation
and SVG/PNG architecture. This version implements OSW's global projection locally,
without importing the US inset renderer, bundled fonts or raster dependencies.
A shared projection/path crate and native PNG export are follow-on candidates
once global seams, regional views and source geometry contracts are aligned.

## Implemented commands

```powershell
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
rust/osw-query/target/debug/osw-query-cli.exe almanac/query-data.json
rust/osw-query/target/debug/osw-query-cli.exe almanac/query-data.json query.json
python analysis/test_rust_query_browser.py
python analysis/test_rust_spatial_queries.py
```

The browser test uses `OSW_TEST_BROWSER` for a Playwright Chromium executable and
the existing local server on port 8788. The engine build uses pinned Cargo.lock,
`--offline --locked`, and the installed wasm32-unknown-unknown target. Rebuilding
a bundle requires rebuilding the engine manifest before browser use. SHA256 checks
detect stale/mismatched artifacts; they are not signatures or proof of authenticity.
The first full snapshot is about 21 MB; splitting immutable collections and caching
will matter as the inventory grows. Scalar filtering/text search scans the imported
rows; ID joins are indexed. Arbitrary relation graph traversal, source admission and native
raster exports are not implemented yet. Spatial queries are implemented as described below.


## Computed spatial predicates

`spatial: {state_code: "NADR", predicate: "intersects"}` computes geography in the
same native/WASM engine. It is distinct from `state_code`, which filters recorded
state evidence. Both can be combined intentionally in a structured query.

- `intersects`: stored line/polygon has any contact with a display-state polygon,
  including boundary-only contact (reported separately).
- `within`: the entire stored polygon is covered by the display-state polygon,
  including its boundary; this describes that geometry, not the full named object.
- `locator`: a non-gateway stored point is covered by the state polygon.
- `gateway`: a shared regional gateway point is covered by the state polygon.

The bundle imports all 56 original OSW display-state shapes after subtracting the
same coarse land mask used by existing Python state joins. Imported coordinates
are geographic representations of display polygons, not physical boundaries.
Holes and polygon components are retained. Rust uses pinned `geo` 0.28.0 planar
DE-9IM predicates, longitude unwrapping and adjacent +/-360 degree copies; it never
uses pixel distance for a scientific measurement. Reference route spatial lines
use the existing WGS84 geodesic densification at <=10 km; display lines still show
stored route vertices. Dated lines/polygons retain source coordinates, dates,
geometry ID, datum status and positional uncertainty where available. Source-defined
route/state semantic exclusions are honored by default. `include_excluded: true`
can inspect raw geometric contacts with explicit exclusion reasons.

Result rows include `spatial_matches`. The map outlines the selected masked state,
brightens matching geometry, and dims the other geometry of matching objects as
context. Inspecting a record shows the computed relations separately from the stored
record and its recorded evidence. Point locators and gateways never enter polygon
containment queries. Missing geography is not a negative physical-passage claim.

Oracle checks compare actual Rust queries with Shapely predicates on the original
SVG/land-mask shapes in native display coordinates, independently of the bundle's
state coordinate conversion. Browser/native parity, state-mode controls, highlighted
geometry, shared queries and full result-map inventory remain required checks.


## Revisioned working records

Inspect any imported record and open **Create proposed working copy**. Store the
complete proposed JSON, label and explanation. Rust validates its source identity,
proposed status, operations, UTC timestamp, revision and resource limits. Working
copies appear in the `working_records` collection. They retain their source record
ID inside proposed data and are not inputs to source-backed rankings or geography.
The source reference remains available from the inspector. Promotion/admission is
an explicit future workflow, not a side effect of saving a proposal.

`osw.workspace-journal.v1` stores the source bundle SHA256 and an append-only list
of transactions. Each carries a unique transaction ID, expected base revision,
UTC timestamp and upsert/delete operations. All operations validate before any
record is installed. Archive removes a live working copy while retaining prior
events. Reopening replays the journal and builds the query collection in Rust.
A different bundle hash requires an explicit rebase; old journals stay stored
under their old snapshot key, with a saved-snapshot list and export control. These local journals are not authenticated audit
logs: timestamps and authorship are user/device metadata, not scientific evidence.

The browser persists journals in IndexedDB, keyed by snapshot hash. Rust prepares
and validates the candidate without mutating the live store. An IndexedDB read/write
transaction checks the expected revision and history prefix before saving. Only
successful storage installs the candidate in Rust. A second tab must reload after
a conflict. Import cannot replace existing history with modified or shorter events.
Browser storage is local and can be cleared by the browser; export journals for
backup and native use. Failed workspace loading is visible while imported queries
remain available. Limits: 50 operations/transaction, 2 MB transaction, 8 MB journal,
1000 revisions. Schema mismatches fail visibly; no implicit migration is performed.

Native commands use the same validation/replay logic:

```powershell
rust/osw-query/target/debug/osw-query-cli.exe almanac/query-data.json --workspace journal.json query.json
rust/osw-query/target/debug/osw-query-cli.exe almanac/query-data.json --workspace journal.json --transaction transaction.json --output next-revision.json
rust/osw-query/target/debug/osw-query-cli.exe almanac/query-data.json --export-workspace --output new-empty-journal.json
python analysis/test_rust_workspace_browser.py
```

Native outputs create a new UTF-8 JSON file and sync its writes. Existing files
are rejected. The prior journal is never overwritten. Interrupted writes can leave
an invalid new file; replay rejects it and the previous journal remains recoverable.
There is no multi-process database or atomic in-place filesystem replacement.
Without --output, export/prepare returns a JSON envelope containing the journal.
Browser import expects the journal itself, as produced by --output or browser export.

Verification covers reload persistence, stale-tab conflicts, native/browser replay,
native new-file output, unchanged existing output, compatible append-only import,
rejected source/hash/history changes, archive history, malformed UTC timestamps,
source preservation, narrow layout and storage abort without memory mutation.

## Explicit source-snapshot rebasing

The browser retains the exact source bundle bytes alongside the first saved journal
for that hash, in the same IndexedDB transaction. Export both for backups. Older
journals without a retained baseline require attaching the matching old bundle;
Rust verifies its hash before comparison. Source snapshots are limited to 100 MB.

Choose a saved journal, preview its rebase onto the currently loaded source, inspect
the complete resulting proposed records, resolve conflicts, then save. Rust compares
old source, proposed data and new source recursively by object field:

- An unchanged proposal takes the new source value.
- An unchanged source takes the proposed value; matching changes agree.
- Absent fields remain distinct from explicit nulls.
- Conflicting values require a source/proposed choice. Arrays are atomic values,
  including geometry coordinates and time series; elements are never merged by index.
- A missing source target requires explicit omission; no ID rename is inferred.
  Omitted proposals remain recoverable in the old journal.
- A different existing destination working copy requires an explicit choice.

Conflict IDs bind record ID, JSON pointer and conflict kind. Unknown/stale choices
are rejected. Preview and preparation do not mutate the store. Save rechecks the
destination revision and history inside IndexedDB, commits the complete journal,
then installs it in Rust. Migrations larger than 50 records use multiple validated
events in one candidate journal and one browser commit. Empty migrations do not
create a revision. Existing source records and old journals remain unchanged.

Rebased journals use `osw.workspace-journal.v2`; both v1 and v2 replay are supported.
Rebase events retain the old bundle hash, typed canonical journal SHA256, old revision
and explicit decisions. These hashes bind inputs, not authenticated authorship.
The parent journal hash uses Rust's typed JSON serialization, not original file
whitespace. Event timestamps are migration metadata, not observation dates. Proposed
status persists; scientific validation and admission remain separate.

Native preview/prepare use the same Rust implementation:

```powershell
rust/osw-query/target/debug/osw-query-cli.exe new-bundle.json --rebase old-bundle.json rebase-request.json
rust/osw-query/target/debug/osw-query-cli.exe new-bundle.json --workspace destination-journal.json --rebase old-bundle.json rebase-request.json --prepare --output new-journal.json
python analysis/test_rust_rebase_browser.py
```

The request contains `journal`, expected destination `base_revision`, unique
`transaction_id`, UTC `created_at` and `resolutions` (conflict ID to `source`,
`proposed`, or `omit` for a removed target). Preview supplies conflict IDs and values.
Native outputs retain the exclusive new-file behavior described above. No schema
conversion or semantic source-ID mapping is inferred by this workflow.

## Standalone Rust SVG maps

**Download map SVG** in the query page calls the same Rust renderer as the native
CLI. It exports the complete global query scene, independent of table pagination
and the browser's current zoom. The original OSW coastline is embedded; the file
contains no external images, scripts or links. Hover/focus titles identify marks.
It retains geometry styles, selected-state highlights and dimmed context features.
The caption reports mapped/unmapped objects and omitted features. Point locators
and shared gateways retain their distinct symbols and scope.

SVG metadata embeds the exact query, bundle SHA256, scene features, source roles,
dates/notes, spatial relations and omissions. It is a portable display receipt,
not an authenticated release. Equirectangular coordinates never become scientific
lengths or widths. The source ledger and pending proposals are unchanged.

```powershell
rust/osw-query/target/debug/osw-query-cli.exe almanac/query-data.json --svg plans/examples/all-currents-query.json --output currents.svg
python analysis/test_rust_svg_export.py
```

Native export exclusively creates a new file and syncs writes; existing paths are
rejected. Invalid/non-object queries fail before creating a file. An interrupted
write can leave an incomplete new output. Browser export and CLI produce identical
SVG bytes for the same bundle/query. Verification checks 100-current and 240-object
scenes with one table row, NADR state highlights, valid XML, escaping source markup,
no external resources, browser rendering and unchanged existing output. Raster
export, regional framing and animated seasonal exports remain follow-on work.

## Geometry observation windows

Object queries accept `geometry_time: {from: "2026-09-25", to: "2026-09-28",
include_undated: false}`. Bounds are required, valid Gregorian `YYYY-MM-DD` days,
ordered and inclusive. This selects features by their recorded `observation_date`,
not acquisition time, journal time or a current's entire lifespan. Missing/null
dates are excluded by default. Explicit `include_undated: true` includes those
features as dimmed **undated context**, never evidence of occupancy on that day.
Malformed/non-day source dates do not become undated context. No interpolation,
nearest-date substitution, seasonal inference or persistence between observations
is performed. A window with no qualifying feature returns no objects.

Objects qualify if at least one stored feature passes the window; source rows retain
their full original feature list for inspection. The map alone renders selected
features, preserving original `feature_index` values. Counts and omissions concern
the selected scene. Combining `spatial` and `geometry_time` requires a feature
to satisfy both conditions; an off-window crossing cannot qualify an object.
The returned spatial relations are similarly limited to selected-time features.
Recorded state links remain a separate stored-evidence filter.

The query controls expose bounds and undated context. The map's recorded-day selector
uses valid dates reported by Rust metadata and runs an exact-day query. Shared URLs,
native queries, result downloads and SVG receipts retain the same window. SVGs
display their selected days and carry the temporal scope in metadata. Inspector
records retain all source fields, including other dates, without implying that all
those features are in the selected map. The initial eight dated features on three
days are now supplemented by the diagnostic frame import below. The combined
bundle contains 25 dated features on 19 days. This remains sparse dated evidence;
whole-current seasonal geometry needs further source work.

```powershell
python analysis/test_rust_temporal_queries.py
```

Verification derives qualifying records/features directly from source dates and
original spatial feature indices, checks native/WASM equality, preserved loaded
records, exact-day controls, share replay, temporal SVG captions and 320 px reflow.
Python and serde_json can parse some decimal coordinates one ULP apart; loaded-row
preservation is compared against the unfiltered Rust store. Source files remain
byte-identical. Source dates/scopes are never reconstructed from floating values.

## Verified diagnostic frame import and playback

`geometry_frames` imports 17 existing Gulf Stream frozen-field diagnostic frames:
twelve fifteenth-of-month daily snapshots in 2025 and five selected September 2026
days. The bundle builder calls the existing timeline validator, which checks pinned
source/figure/algorithm bytes, recomputes traces and finite seed/step scenarios,
retains stopped traces and verifies recorded state intersections. Both timelines
remain research-only and noncanonical. They establish neither monthly means nor
climatology, annual extrema, whole-current axes, widths or parcel trajectories.

Each frame preserves its original coordinates, date/time support, source URL and
hashes, processing algorithm/version, stop reason, diagnostic trace distance,
null width/positional uncertainty, nine sensitivity scenarios and limitations.
Five of the 17 nominal traces stop without reaching the downstream gate; they are
not dropped. Diagnostic distances remain outside the published ranked lengths.
Objects and series carry resolvable frame IDs. Map and spatial features retain
frame/series identity and receipts. Rust rejects unresolved or cross-object frame
references and a feature whose date, geometry or role differs from its frame.

The query inspector links complete frame records and their observation-day map.
**Gulf Stream recorded diagnostics** selects the first 2025 day and fits its map
marks. **Fit matches** is available for other selections. Recorded-day playback
advances by observation at one frame per second, preserving query filters and zoom;
date gaps are unequal and are not elapsed-time animation. Playback stops on pause,
another query, failure, hidden page or the final observation. The date catalogue is
global: a chosen day may have no evidence for the current query, which produces an
empty scene rather than substituting another observation. Source-defined seasonal
routes and model-field subsets are not converted into dated occupied footprints.

This bundle update changes its hash; stored proposals require the explicit snapshot
rebase workflow. Canonical release collections and the source ledger are untouched.

```powershell
python analysis/test_rust_geometry_frames.py
```

Verification compares all 17 frame payloads/coordinates to original timeline files,
confirms all stops and null dimensions remain, checks native/WASM queries, mapped
frame IDs, inspector links, playback/pause, regional fit and narrow layout. Original
SVG/Shapely state oracle queries also pass with the imported geometries.

## Source-defined seasonal routes — 2026-10-04

The Rust bundle imports six checked editorial phases in `seasonal_routes`:
Somali winter and June–July southern limb; historical Davidson October–March;
Sri Lanka Monsoon Current June–September and November–February; and an Indian
SECC December–March studied reach. These belong to four existing current objects.
Their vertices, source URLs/locators, layers, time conventions, candidate hashes,
width context and phase-comparability decisions remain attached to the records.
The seasonal inventory's stale width receipt was refreshed after validating the
same Davidson association against the current 37-record width inventory.

Objects carry `seasonal_route_ids`. Seasonal map features carry a `phase_id` and
the original source geometry role. Rust rejects mismatched ownership, coordinates,
role, calendar, source metadata, or a phase feature carrying an observation date.
No canonical record or published length is admitted by this import.

Object queries accept exactly one selector:

```json
{"collection":"objects","seasonal":{"month":1},"limit":50}
```

```json
{"collection":"objects","seasonal":{"phase_id":"somali-winter"}}
```

Months must be integers 1–12. A month selects only seasonal features whose source
calendar explicitly contains that month; null calendars are excluded. The Somali
winter phase is selectable by name, with its month range still unresolved.
April and May currently produce empty month scenes. This means no supported phase
in this imported inventory, not absence of ocean flow or zero current dimensions.
Exact-day `geometry_time` and `seasonal` are separate, incompatible selectors.

Spatial and seasonal conditions must match the same stored feature. Unselected
routes and locators cannot supply the state intersection of a selected phase.
Map scenes use every matching object before table pagination, retain phase receipts
and computed relations, and export the same metadata through native/WASM SVG.
Source rows continue to retain their full geometry lists.

The query UI provides named months, source phases, a January preset and direct
phase-map links inside current cards. **Play source months** steps the selected
query through month numbers at one-second intervals, preserves filters/zoom, and
shows empty months explicitly. This is discrete source-convention playback, not
interpolation, a current-year animation, observed monthly velocity fields, annual
extrema or a width footprint. Playback is opt-in, pauses on user request, and stops
on other queries, failure, a hidden page or December. Recorded-day playback
switches back to exact observation dates.

```powershell
python analysis/check_current_seasonal_route_frames.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_rust_seasonal_routes.py
```

The browser test compares all 12 months and six phases between native Rust and
WASM, checks three OSW states with same-feature selection, invalid/combined
selectors, source record fidelity, null dimensions, month gaps, keyboard/card
navigation, monthly playback/pause, mobile reflow and byte-identical SVG export.
Changing this bundle hash requires the existing explicit journal rebase workflow.

## Scoped width samples — 2026-10-04

`width_samples` projects 88 original samples from three existing diagnostic
documents: 12 Leeuwin a101 monthly fitted-width plot readings; 64 Kuroshio East
China Sea seasonal profile plot readings at 16 longitudes in four seasons; and
12 Pacific NECC 140 W monthly-mean connected-component diagnostics for 2013.
All five unresolved Kuroshio readings remain null and queryable. This imports
additional query granularity, not new canonical measurements or admitted ranks.

Every sample retains its full original `source_sample`, source metadata in
`source_context`, optional seasonal `source_phase`, parent `diagnostic_id` and
exact JSON pointer `sample_path`. Projection code is pinned in the bundle input
receipts. Bundle generation reconstructs all three diagnostics from their pinned
source archives/PDF extraction configurations before projecting them. It checks
and records original source, protocol, configuration and audit hashes. Original
journal PDFs stay local and excluded from Git; use the existing checksum-pinned
fixture acquisition command when regenerating from a fresh checkout. NECC's
existing narrowly bounded arithmetic-roundoff comparison remains in effect.
Rust resolves each pointer and binds the original payload, phase path,
current owner, metric, value, plot-reading interval, month/year, longitude, phase
label and status to its parent diagnostic. Cross-object references, changed
values/support, invented uncertainty and whole-current/ranking promotion fail
store loading. Parent diagnostics remain inspectable in the query UI.

`value_km` is a scoped plot reading or a locally derived diagnostic, depending on
`sample_family`. It is not a common global width metric. Sorting values does not
establish a ranking of named currents. `plot_reading_interval_km` retains the
source extraction allowance; `measurement_uncertainty_interval_km` remains null
and `is_confidence_interval` false. NECC threshold-sensitivity results remain in
the original sample and are not collapsed into an uncertainty interval. Original
profile pixels, brackets, sample times and stop/missing statuses are preserved.

Leeuwin records preserve conflicting historical period labels rather than
inventing a combined averaging window or dated year. Kuroshio retains its
1993–2008 study-period years, with unresolved month membership for named seasons;
no month numbers are supplied for its 64 readings. NECC retains source year 2013
and explicit source month/sample times. No width sample creates a geographic
route, occupied footprint, annual range or confidence interval.

Objects gain `width_sample_ids` and `capabilities.width_samples`. **Has evidence:
Scoped width samples** finds the three covered objects. Their cards link directly
to filtered sample queries. **Leeuwin monthly widths** and **Kuroshio width
profiles** provide example queries, with full context and parent diagnostics in
the inspector. Generic field filters can select a family, month, source year,
longitude, named phase or unresolved `value_km` independently of source-map phases.
Visible sample controls select current, method family, source month and numeric
value availability. Sorting preserves these selections. Extra structured filters,
including duplicate/unsupported control values, remain active and are disclosed
instead of being silently discarded by form use. Current-card links initialize
the visible current selector. **NECC monthly diagnostics** selects its 12 months.
These sample records have no `map_scene`; source geometry cannot be inferred from
scalar widths. Source-month map playback continues to use `seasonal_routes`.

```json
{"collection":"width_samples","filters":[{"field":"current_id","op":"eq","value":"leeuwin"}],"sort":{"field":"month"}}
```

```json
{"collection":"width_samples","filters":[{"field":"value_km","op":"exists","value":false}]}
```

Verification:

```powershell
python -m pytest analysis/test_query_width_samples.py -q
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_rust_width_samples.py
```

Checks cover all source rows, five missing readings, separate uncertainty roles,
three current joins, native/WASM parity, null-last numeric order, malformed source
bindings, direct card navigation, parent diagnostic access and 320 px reflow.
Canonical release files and published length ranks remain unchanged. This source
snapshot update uses the same explicit proposal-journal rebase contract.

### Source width charts

Width sample queries return a Rust-generated `chart_scene` alongside the table.
Six panels separate the three source diagnostics and four Kuroshio seasons.
Charts include all matching samples before table pagination. Axes use the full
original diagnostic domain, so filtering does not change the scale. The four
Kuroshio panels share their diagnostic's width scale.

Points remain disconnected. Whiskers show plot-reading allowances, not confidence
intervals or measurement uncertainty. Five unresolved samples appear as crosses
in a separate missing strip, never as zero-width values. Source period and method
notes remain visible. These scalar charts introduce no geographic footprints,
annual extrema, interpolation or cross-method width ranking.

Each point or missing mark opens its original sample card by click, Enter or
Space. Charts are labelled SVG groups with individually labelled buttons; the
table provides the original values and text alternative. Narrow screens scroll
the chart within its frame while the surrounding page reflows.

Verification: `python analysis/test_rust_width_charts.py` with `OSW_TEST_BROWSER`
set to Chrome. Checks cover all 105 marks, seven panels, five missing readings,
stable filtered axes, source-value fidelity, native/WASM equality, keyboard
selection, mobile scrolling, empty results and stale-chart clearing on errors.

### Remaining current-length decisions

The `route_decisions` collection imports all 89 remaining-current decisions
from the audited route catalog. Thirty have no candidate route; 59 have at
least one, accounting for 62 candidates. Eight unresolved basin-family names
remain families. Each record keeps its original decision, source-catalog hash,
construction strategy, candidate IDs, next action and source scope audits.
Object cards join their own decision; published ranked lengths stay separate.

Rust validates projection fields, owner joins, complete remaining-current
coverage, candidate counts and IDs, catalog receipts and audit ownership.
Planning records cannot declare ranking eligibility. Existing routes retain
their original admission gates. These are research priorities rather than
approved physical classifications or dimensions.

**Remaining length decisions** queries the full worklist. **Unbuilt remaining
routes** selects the 30 zero-candidate decisions. Strategy filters distinguish
seasonal routes, naming/extent conflicts, subsurface paths, families and systems.
Visible current, strategy and construction-status controls preserve selections
when sorting or resubmitting. Additional and duplicate structured constraints
remain active and are disclosed beside the form.
Selection opens the next evidence needed and inspected-access notes; candidate
links and atlas cards retain direct navigation.

Verification: `python analysis/test_rust_route_decisions.py` with
`OSW_TEST_BROWSER` set to Chrome. Checks cover complete source membership,
89/30/8 query counts, 62 route references, original audit payloads, seven invalid
bundle cases, native/WASM equality and keyboard/current-card/mobile navigation.

### Recorded-day width samples and sensitivity

The sample import now includes 17 existing Gulf Stream **system** section-span
diagnostics, bringing the collection to 105 samples across four method families.
The system identity is retained; these values are not inherited by the separate
Gulf Stream Current or by its mapped diagnostic streamline. The imported
diagnostic is reconstructed against every pinned NOAA subset, source-processing
version, velocity sampler and section-width protocol before projection.

The metric remains a fixed-70-W meridional half-peak eastward-component span.
Each record retains its exact observation day, date-derived year/month, source
algorithm, full profile, nominal boundary brackets and all 40/50/60% scenarios.
Rounded section-span values supply `value_km`. A separate
`diagnostic_sensitivity_interval_km` retains finite threshold-choice sensitivity;
`sampling_bracket_interval_km` retains geometric grid-bracket spans. Neither is
measurement uncertainty, a confidence interval, a flow-normal width or an annual
range. Resolution flags remain visible. The inspector rounds grid brackets
outward to 10 km for display while preserving original values in the JSON record.

The dated chart uses elapsed Gregorian days, including gaps between December
2025 and September 2026. Axis ticks describe calendar coordinates, not additional
observations. Closely dated points may overlap; each retains its own keyboard
target and table row. No connection or interpolation is drawn. Original source
axes remain fixed under filters. Dashed whiskers show threshold sensitivity;
solid whiskers on other methods continue to show plot-reading allowances.
Source processing changes remain explicit and are not attributed solely to
physical changes. Source year/day controls retain selections when sorting.

Verification: `python analysis/test_rust_dated_width_samples.py`, projection
tests, width-chart and width-query browser regressions. Tests cover all 17
original samples, Gregorian elapsed spacing and tick conversion, stable filtered
axes, three processing versions, eight source mutation rejections, year/day form
retention, keyboard selection and 320 px reflow. Bundle projection payloads match
the originals exactly. Native JSON readback allows only last-bit f64 differences
in derived velocities (absolute 1e-15 m/s) and boundary latitudes (1e-14 degree);
dates, rounded widths, thresholds, brackets and flags remain exact. Original
diagnostic files and source hashes are retained. Canonical release files and
scientific admission remain unchanged.
# Local recorded-day section maps

The `width_samples` query can supply a map scene when its matches include the
Gulf Stream system dated half-peak section family. Rust derives each nominal
LineString from the source-bound longitude and paired interpolated south/north
boundary latitudes. It does not add geometry to the canonical inventory or to
the object's occupied footprint. Invalid, reversed, unresolved or unsupported
sample coordinates remain unmapped; their records remain queryable.

The map includes every matching sample before table pagination. Its inspection
target is `width_samples`, with a separate owner entity ID, source day, processing
version, subset checksum, metric, rounded value, sensitivity and bracket ranges.
The meridional surface diagnostic is not a flow-normal width, current axis,
streamline buffer or state-containment assertion. No geographic positions are
invented for the other sample methods. Coincident dates retain separate keyboard
targets and table records without artificial spatial offsets.

Day/year sample filters control these maps. Object geometry-day/month playback
controls are hidden and disabled here. The UI fits local spans with a minimum
4-degree display window, shows geographic display bounds, and links sample cards
directly to their section queries. Portable SVG exports retain the global OSW
display, all source receipts and explicit local-section labels; they do not
calculate scientific dimensions from display coordinates.

Verification: `analysis/test_rust_dated_width_samples.py` checks all 17 exact
source endpoints, source receipts, pre-pagination coverage, native/WASM identity,
local fit, card links, filter retention, keyboard selection and 320 px reflow.
`analysis/test_rust_svg_export.py` checks native/WASM export byte identity and all
17 marks with a one-row page. Rust tests cover missing/reversed/out-of-range
endpoints and unsupported sample methods. Existing object map and width query
checks remain required regressions. These maps are an editorial diagnostic
presentation; scientific boundary/resolution admission remains open.

## Recorded section playback

Section maps now offer explicit play/pause through their recorded days. Rust
returns sorted `recorded_days` and `display_bounds` from all matching records,
before pagination. The browser requests this inventory with only the day
predicate represented by the visible day control removed. Every duplicate,
unsupported, year, month, method, metric and source constraint remains in the
query. Playback appends an exact observation-day predicate for each source day,
retaining sort and page size and resetting the page offset.

Playback starts at the selected source day, or the first eligible day, and stops
at the final eligible observation. One observation per second is ordinal playback,
not elapsed-time animation; no missing months or unrecorded days are synthesized.
The map fits the eligible source bounds once, then keeps its viewport through the
frames. Chart source axes remain fixed. Date and processing version are visible
beside each frame. A new query, pause or hidden page cancels subsequent frames;
an already running query may finish. Object geometry-day/month controls remain
separate. SVG receipts retain the exact frame query, source days and display bounds.

`analysis/test_rust_section_playback.py` verifies a filtered five-day inventory,
the four eligible frames beginning September 24, exact native source results,
fixed map viewport, duplicate year/day and metric predicate retention, keyboard
play/pause, query cancellation and 320 px reflow. No annual seasonal cycle is
inferred from the sparse 17-day source series.

## Local Loop Current product and method comparison

Two unranked diagnostics for 25 September 2026 are imported separately: NOAA
RADS surface velocity integration and a finite Copernicus/DUACS ADT contour
scan from a public GCOOS response. The Loop owner links both diagnostics and
their two dated geometry frames. They have no reference-route IDs or published
measurement admission. The existing 17 Gulf Stream frames remain unchanged.

The builder reconstructs both diagnostics from pinned snapshots before import.
Original diagnostic JSON bytes are preserved in each record; Rust checks their
SHA and parsed document equality, source/protocol receipts, owner links,
classification/date, nonadmission fields, comparison source and exact frame
geometry. Query map selection opens the owner and method cards; cards and the
source audit link to the mapped comparison page. Both methods and all retained
candidate/failed traces remain available as source documents in the store.

Contour levels and sensitivity scenarios are numerical search choices, not
widths, confidence intervals or annual ranges. Product agreement may reflect
shared altimetry inputs. Original supplemental algorithm details, gateway and
effective-resolution review, repeated regimes and source-use review remain
open. These local additions do not change the canonical release or ranked
length inventory. Validation: `python analysis/test_rust_loop_diagnostics.py`
with `OSW_TEST_BROWSER` set, plus the two Loop scientific test modules.

## Loop Current recorded-date extension

Local follow-up to main commit 05fdf5c. Four predeclared 2025 dates (15 January,
April, July and October) repeat the identical NOAA seed/step/threshold and DUACS
finite-contour rules. Source manifests retain both response and regional snapshot
checksums. The comparison file retains all failed nominal and sensitivity outcomes.

The Loop owner now joins ten method diagnostics across five recorded dates and
seven connected geometry frames. Three new NOAA nominal failures have no connected
length and no accepted map frame; their stopped traces remain visible on the
recorded-date experiment page. Existing Gulf Stream frames remain seventeen.

The Rust loader requires paired NOAA/ADT records on every represented date,
source-bound document equality, exact date/owner joins, geometry equality and the
same-date NOAA comparison receipt. A failed trace cannot receive a map frame.
The atlas uses exact recorded dates, without persistence or interpolation.
The new page steps between four snapshots at equal viewing intervals, preserves
selected-date links and disables playback for reduced-motion preferences.

Verification: python -m pytest analysis/test_loop_current_recorded_dates.py -q;
python analysis/test_rust_loop_recorded_dates.py with the configured browser.
Original-source field/mask readback covered all eight new regional receipts.
No annual extrema, seasonal phase, width, named-eddy identity or ranked length is
admitted. Source-use, gateway/effective-resolution and original method review remain
open; repository publication was authorized on 2026-10-04. Scientific admission
remains separate from the repository publication checks.

## Source-described flow networks

The Indonesian Throughflow pilot adds flow_networks, flow_network_nodes,
flow_network_edges and passage_samples. Its twelve nodes and fourteen directed
connections describe selected source pathways across different layers. Schematic
positions have no geographic scale. Eight published first-deployment mooring
positions are geographic point locators, never whole-current footprints.

network_path is available only with collection flow_networks, and specifies
network_id, from_id, to_id and max_hops (1-16). Rust searches simple paths with
a 4096-expansion/64-result cap, returning explicit truncation and hop-limit flags.
The Pacific-to-Indian pilot has five connections at max_hops 8. No metric length
or travel time is inferred. Ordinary query resubmission preserves path constraints.

Rust binds original source JSON bytes, SHA, document/projection equality, node
references, owner joins and mooring map coordinates. Three 2004-2006 exit means
retain Sv units, depths and processing-choice intervals. Integration windows
35/35/160 km are not current widths; seasonal/annual dimensions remain null and
rank eligibility false. Source: Sprintall et al. 2009, Tables 1-2 and Introduction.

Verification: python analysis/test_rust_flow_network.py with OSW_TEST_BROWSER;
python -m pytest analysis/test_flow_network.py -q. The source scope audit and
roles review accompany this editorial addition; canonical admission remains open.

## Dashboard evidence and record links

The coverage dashboard counts ten dated Loop method diagnostics, one Indonesian
Throughflow passage network and three observed passage transport records as
separate evidence classes. These counts do not supply whole-current length,
width, annual extrema, geographic footprint or scientific admission. Unresolved
nominal diagnostics remain counted as records; a record count is not a count of
successful paths. The five recorded observation dates are retained, while the
2004-2006 transport means do not acquire an invented exact observation endpoint.

Dashboard content fingerprints include the actual method documents and network
input. Time evidence, source metadata, network geometry and passage observations
are assigned to their relevant change groups. Source/diagnostic/protocol receipts
are checked before generating coverage. Adding these categories changes the
content fingerprints of the Loop and Throughflow owners only.

Dashboard evidence links constrain the query by record ID and use an optional
inspect URL parameter to open the matched record card directly. The selection
must belong to the returned result page. A missing selection leaves the valid
query results available with an explanatory message. Inspection updates the
share link and browser URL; submitting a new query clears that selection.
Direct object inspection fits mapped features before opening the card.

Verification: analysis/test_dashboard_diagnostic_navigation_browser.py,
analysis/test_motion_dashboard_browser.py and analysis/test_motion_dashboard.py.

## Loop inflow recorded section spans

Two new source-bound diagnostics, diagnostic:yucatan-noaa-sections and
diagnostic:yucatan-adt-sections, each retain five recorded dates and produce
five loop_dated_half_peak_section samples. The existing Yucatan gate at
21.875 N supplies the fixed section. These are zonal half-peak northward-
component spans, not widths of the traced Loop axis or representative current
widths. The dedicated section protocol declares thresholds, wet-cell rules,
native adjacency, brackets, WGS84 distance, rounding and unresolved boundaries.

NOAA rounded samples are 120, 110, 110, 110 and 100 km; DUACS samples are
90, 80, 80, 80 and 70 km, respectively on January/April/July/October 15 2025
and September 25 2026. Product-specific sparse sampled spans retain their
counts and processing versions. No product pooling, annual extrema or confidence
interval is admitted. The September 2026 NOAA nominal span is under four native
cell spacings and retains its resolution-review flag. Other spans also require
scientific boundary/component and identity review.

The query store now has 115 width samples across five current owners and nine
source panels; the original 105 values, metrics and source records remain
unchanged. Canonical widths remain 37 source records. Local Loop coverage has
two additional diagnostic width documents and ten dated section samples.
Rust validates parent source JSON/SHA, source projections, owner links and
latitude support. Maps derive only paired west/east endpoints at the declared
latitude; no route buffer or occupied polygon is generated. Charts separate
products and preserve elapsed-day gaps. Playback steps recorded dates with no
interpolation and retains product/year/method filters. Reduced-motion preference
stops playback and disables animation controls while manual filters remain.

Verification: test_loop_current_section_spans.py, test_rust_loop_section_spans.py,
test_rust_width_samples.py and test_rust_dated_width_samples.py. Scientific
admission, source-use review and true annual width evolution remain open.

## Published observation locations and OSW state queries

Spatial queries now accept passage_samples with predicate locator only. The
existing point topology code indexes each source-bound mooring mark, retains
source name, URL/hash and published deployment dates, and returns feature-index
relations separately from recorded state links. Intersects, within and gateway
predicates are rejected for these records: mooring points cannot establish
current or passage containment. Recorded state_code joins remain object-only.

Eight first-deployment INSTANT mooring locations map into the approximate SUND
display polygon. This returns three passage transport records with eight point
relations, not eight independent transport values. Coordinates and deployment
periods remain separate from the 2004-2006 exit means. Deployment dates do not
prove coordinate persistence or exact redeployment locations; no historical
state boundary, velocity footprint or time-varying mooring track is supplied.

The independent Shapely audit tests every published point against all 56 state
display polygons, including holes, boundary contact and longitude shifts. Its
state-geometry SHA is independent of the complete bundle SHA, avoiding circular
provenance. No-match is not proof that the named current is absent.

Query controls expose Locator in state for passage observations, preserving
explicit source filters. Map labels use the individual mooring names and open
their parent transport record. Observation-site maps retain zoom/export and
source inspection while date/month animation controls are hidden. The Throughflow
mooring sites in SUND preset and shared query URLs retain that same predicate.

Verification: build_passage_observation_state_audit.py and
test_rust_passage_state_queries.py: independent 56-state oracle, four malformed
metadata rejections, eight SUND markers, native/WASM parity, keyboard inspection,
state selection, share/reload and 320 px layout. Canonical state/current relations
and measured inventory remain unchanged; these are local computed point joins.

## Agulhas ACT mean-section source record

The width collection adds `agulhas-act-eulerian-mean-section-width`: 219 km at
the ACT section near 34 S, April 2010-February 2013 (month precision). Its
coast-to-author-reported-mean-zero-isotach metric retains the publisher and
institutional source access limitations in a checksum-bound audit. General
protocol v1.20 formalizes this evidence class. No exact occupations, recovered
edge geometry, fixed measurement layer, seasonal width range or whole-current
width is inferred. The source-reported 3000 m mean depth extent is contextual.

Coverage: 38 source records for 25 named currents, 68 unassessed, two derived
candidates and five reviewed without numeric width; 115 diagnostic samples
remain separate. Atlas and seasonal evidence cards show the scalar with its
period and boundary. The evidence page omits an unsupported bar and geographic
locator, and disables annual playback. Existing 37 width records and all Gulf
and Loop section values are unchanged; protocol receipts are refreshed.

## Existing identity taxonomy and membership queries

The complete object inventory retains canonical identity facets (type, identity
level, geographic setting, basin and time behavior). The query bundle carries
`taxonomy_links`: twenty existing `part_of_system` assignments from the current
ledger, projected as basin/subfamily memberships or named system components.
The source ledger and taxonomy vocabulary are stored with exact JSON/SHA
receipts; the naming URLs are context, not independent evidence for the parent
assignment. This adds no new canonical relation or scientific classification.

Rust checks complete object identity coverage, exact facet projections, link
identity/labels/pointers, declared source bytes and an acyclic graph. A malformed
or incomplete projection fails loading. Canonical current and eddy collections
remain unchanged. Missing members and missing parents are unassessed, not absent
flows or isolated eddies.

Query `objects` with `taxonomy: {root_id, relation, include_root}`. Relations are
`children`, `parents`, `descendants` and `ancestors`; include_root defaults false.
This selects existing object records before regular evidence, state, time,
filter, sorting and pagination operations. It never aggregates or inherits
lengths, widths, source dates, state memberships or map geometry. Other
collections reject taxonomy selection. Unknown roots and directions fail.

The countercurrent umbrella has two direct subfamilies and seven descendants:
the subfamilies plus five basin members. A Pacific NECC ancestor query returns
the NECC subfamily and countercurrent umbrella. The Gulf Stream system has three
declared components (Florida, Gulf Stream and North Atlantic), without implying
that these are an exhaustive physical network or a partition of system length.

The query UI exposes identity level, membership root/direction and explicit
root inclusion. Existing advanced object filters survive builder changes.
Inspectors provide the identity definition, declared parent/child buttons and
queries for ancestors/descendants. Share URLs retain these selections. The
membership collection also provides direct links back to both object cards and
labels its naming references as context only.

## Local filtered-width statistics follow-up (2026-10-06)

The `widths` collection now includes the Florida HF radar jet at 25.42 N for
2005-2006. The mean (59 km), observed filtered-series span (41-76 km), standard
deviation (6 km) and reported confidence allowance on the mean (+/-2 km) retain
different statistical roles. Confidence percentage remains null. A nominal
0.75 m sensing depth does not become a fixed layer. The half-core-speed jet
coordinate definition and 40 h metric filter remain attached to the source audit.

The audit and protocol v1.21 are pinned in bundle inputs. Atlas cards expose
mean and observed range together; the evidence inspector explains the seasonal
phase without fabricated numeric frames or boundaries. Exact occupations,
monthly widths, map footprints, annual extrema and global ranking remain
ineligible. Reproduce with the width validator, dashboard/bundle builders and
`analysis/test_florida_width_statistics_browser.py` using a local atlas server
and `OSW_TEST_BROWSER` pointing at Chrome.

## Florida monthly graph readings and chart playback (2026-10-06)

The separate Figure 9b diagnostic now projects twelve historical monthly
readings into width_samples, with +/-1 km graph-reading allowances. Its raw
source JSON and SHA bind each sample; source PDF, config, protocol and generator
are pinned. The gray overall-average curve is distinct from the two individual
years and the unextracted within-month standard-deviation envelope. No geographic
width edges, fixed vertical layer, annual physical range or whole-current
ranking are supplied. Chart playback and manual stepping highlight existing
records only, with reduced-motion and hidden-page guards. Shared card selection
also synchronizes the highlighted reading. Corpus: 127 samples, ten chart
panels, five unresolved readings. Rebuild with build_florida_monthly_plot.py
and the existing dashboard, bundle and engine builders. Verify with
test_florida_monthly_plot.py and test_florida_monthly_plot_browser.py.
