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

## Dashboard snapshot through Rust/WASM

The coverage dashboard now requests its checked source snapshot through the same
WASM worker as the query UI. `dashboard_receipt` retains the original dashboard
JSON bytes and SHA256 in the bundle manifest. Rust rejects a changed receipt,
incomplete or duplicate object identities, conflicting coverage totals, or a
source field/map feature that disagrees with the shared objects collection.
Query joins may extend objects without rewriting the dashboard's source fields.

`osw-query-cli BUNDLE.json --dashboard` and worker action `dashboard` return the
same source JSON string. Preserving that string avoids an extra floating-point
serialization pass over the source geometry. The browser decodes it for display.
No direct dashboard JSON fetch is used as a fallback. Refresh loads the current
checked bundle; failure retains the previously loaded snapshot with an explicit
status. First-load failure does not populate cards.

The initial increment migrated dashboard data loading and identity validation.
Coverage filtering subsequently moved to Rust as described below. Beck layout,
map drawing and the per-device seen baseline remain browser code.
The canonical release and scientific admission rules are unchanged.

The local required `offline` workflow change runs native Rust tests plus shipped
WASM query, all-collection, and dashboard browser checks. The new gate is not live
on main until this follow-up is published and merged.


## Dashboard selection in the shared engine

Worker action `dashboard_select` and native command `--dashboard-query` accept a
strict request containing `text`, optional `record_type`, `metric`,
`covered_only`, `changed_only`, and per-device `changed_ids`. Rust rejects
unknown request fields, types, metrics, unresolved IDs and duplicate changed IDs.
The bundle's checked `dashboard_search` projection preserves the dashboard's
label-plus-basin search scope. Selection uses the common object query engine,
then applies the explicitly supplied local changed-ID restriction. Coverage and
changed counts are returned with selected IDs. All query pages are collected;
the current table page limit cannot truncate dashboard inventory.

The browser retains the checked source record order for painting, delegates
selection to its persistent worker, and ignores results from older input
revisions or replaced workers. A failed selection reports an error and retains
the previous view; it does not fall back to a browser query implementation.
Refresh replaces the worker only after validating the next snapshot. The seen
baseline and content comparisons remain per-device browser preferences.
Geographic projection subsequently moved to the shared map renderer. Beck
rendering remains the next dashboard migration step.


## Dashboard geography through shared Rust map primitives

Dashboard selection now includes a `map_scene` generated by the same projector
used by native/WASM query maps. It renders the checked dashboard source features,
not the additional query-only diagnostic or seasonal overlays. Rust owns path
construction, seam breaks, polygon closure checks, invalid-geometry omissions,
point positions, grouped gateway identities, evidence counts and update flags.

The scene uses normalized equirectangular display coordinates plus an explicit
transform into the existing OSW atlas SVG frame. Marker positions are supplied
in that frame so existing hit targets, label sizes and glow styles keep their
scale. The browser paints paths and markers and wires keyboard/click behavior;
it no longer projects geographic coordinates or constructs route paths for
this map. The Beck schematic was subsequently migrated as described below.

A shared gateway with conflicting point positions is rejected rather than
silently choosing one. Gateways retain all selected source identities and their
scope note; they do not become individual eddy centers or footprints. Unsupported
or invalid geometry, including polygons requiring dateline clipping, is omitted
and reported in the scene and dashboard summary. Records remain available in
cards. Display projection is never used to estimate current dimensions or state
containment.


## Beck schematic through Rust/WASM

Dashboard selection now returns `beck_scene` alongside `map_scene`. The optional
four-number `view_box` defaults to the world frame and requires positive width
and height. Rust owns octilinear reference routes, seam breaks, stable inventory
station numbers, collision spacing, regional label positions and leaders,
source-described connection paths, displaced eddy gateways, basin classification,
and list-track positions. The browser paints SVG glyphs and binds interaction.
Native and WASM produce the same scene for the same selection and region.

All filtered current identities remain available in the basin lists, including
records without a map anchor. Stations retain the original inventory numbering.
Eddy groups retain records without coordinates. Only checked source connections
are drawn; schematic crossings, displaced symbols and nearby list tracks imply
no physical junction, observed footprint, measured length or state containment.
Map station names remain visible only on hover or focus; basin lists retain names.
The per-device seen baseline remains a browser preference.

This follow-up remains local until publication and merge. The canonical release
is unchanged. Verification includes Rust seam/collision tests, native/WASM scene
parity, all 100 distinct current stations, all 140 eddy identities in groups,
source connection identity preservation, invalid view-box rejection, keyboard
navigation, hover labels, coverage/update lights and the mobile dashboard.


## Required browser gate coverage

The local `offline` workflow follow-up runs twenty-two standalone browser scripts
through `analysis/run_rust_query_browser_checks.py`. It builds the native CLI
with pinned Rust 1.95.0 and exercises the shipped WASM binary in Chromium.
The checks cover:

- Query builder, maps, joins and native/WASM results.
- All 22 collections, canonical imports, pagination and record inspection.
- Dashboard maps, Beck stations, filters, updates and diagnostic navigation.
- Durable working-record saves, conflicts, import/export and failed storage.
- Source snapshot rebasing, conflict choices and native/WASM journal agreement.
- Taxonomy closure, source rejection and scoped measurement navigation.
- Florida width statistics and source-bound monthly chart playback.
- Agulhas mean-width evidence and its scope.
- All 240 dashboard identity links to selected atlas cards and reload/reset.
- Touch pinch/pan, keyboard reset and shared zoom/pan frame restoration.
- Global atlas routes, map cards, selection and navigation.
- All 56 saved OSW state shapes, masks, keyboard/pointer filtering and outages.
- Every state-filtered identity set, nominal/alternative route distinctions,
  and all stored route/state crossing links.
- All 140 eddy cards, scoped state receipts, polygon/locator distinctions,
  hover/focus names, shared views and mobile access.
- Seasonal atlas round trips for the full current/phase directory.

The scripts use the common cross-platform CLI path and Playwright's installed
Chromium by default; `OSW_TEST_BROWSER` selects an existing local browser.
Rebase source-update fixtures align the simulated identity ledger, taxonomy
labels, search projection and dashboard receipt before exercising migration.
They do not relax the production loader or change the canonical release.

This is broader than collection coverage, but does not yet run every dedicated
current-specific or atlas-interaction browser script. Those existing checks
remain the next expansion of the gate. No claim of complete scientific data
or all-page Rust migration follows from this browser gate.


Atlas URL checks retain the existing six-decimal display-frame encoding.
Reopening a shared eddy view permits less than 0.000002 display units per
coordinate, matching the shared atlas framing checks. Main-map zoom without
navigation must leave the eddy card extent exactly unchanged. This display
rounding is separate from source geometry and scientific measurement uncertainty.
The required browser runner executes scripts sequentially against its server.


## Seasonal page source loading through Rust/WASM

`seasons_receipts` retains the four original source JSON strings and hashes:
width inventory, reference-route catalog, seasonal-route frames, and the New
Guinea local direction audit. Rust validates each path, schema and checksum,
checks width/route/frame rows against their shared query collections, and checks
the complete current index without duplicates. Source fields explicitly set to
null must still exist in the projected record. Extra query join fields remain
allowed. Local direction phases retain the existing month windows, separate
El Nino exception, non-axis geometry role, and explicit null dimensions/ranges.

Native `--seasons` and WASM `osw_seasons` return identical `sources_json` strings.
The seasonal page uses worker action `seasons`, parses those checked originals,
and terminates the worker after loading. It makes no direct research JSON reads.
Failure reports the loader error and does not populate the current index.
Phase-plan construction and eligibility subsequently moved to Rust as described
below. The browser retains playback timing and presentation.
Source data and the canonical release are unchanged.

The gate adds seasonal snapshot integrity/parity checks and the local direction
browser check. Page readiness is the checked snapshot plus populated controls;
page network-idle alone does not prove worker completion. Altered direction
fixtures update dependent planning receipts before testing the semantic guard.


## Shared seasonal phase plans and playback policy

The seasonal snapshot now includes `phase_plans` for all 100 current identities.
Each plan returns source IDs rather than reserializing measurement values:
standalone widths in source order, recorded route frames with their linked width
context, and local direction records. Widths already used by a frame do not
appear twice. The browser resolves those IDs into the checked original source
records, retains synchronous selection, and displays the Rust comparison note.

Rust decides `can_play` from the existing comparability rules: at least two
records, no explicit comparison restriction, and either a supported width
summary covering every phase, only recorded route frames, or at least two
eligible local direction composites. The permitted index list excludes the
El Nino exception. Non-playable plans provide no automatic step indices; all
records remain manually inspectable. Comparison-note precedence is width
summary, route comparison, explicit width restriction, then local direction
interpretation. No interpolation, new annual extrema, dimension inheritance
or occupied footprints follow from playback.

The browser owns timer start/stop and SVG/HTML painting, and advances only the
returned indices. Independent source calculations check phase IDs/order,
linked contexts, eligibility and comparison notes for every current. The real
WASM UI checks every plan's options, playback control and displayed scope,
plus local direction exception handling and seasonal atlas round trips.


## Canonical object pages through Rust/WASM

The bundle now imports all twenty ledgers used by the object page, including
aliases, source-set length assessments, classifications, footprint candidates,
movie context, tiles, state assessments and source observations. Together with
editorial data this supplies 36 query collections. Canonical arrays are imported
without changing the release files. The query selector appends every collection
reported by Rust metadata, preserving the preferred order of existing views.

Native `--object-view ID` and WASM worker action `object_view` return the scoped
canonical evidence for an entity. Rust selects aliases, measurements, relations,
claims, observed current/detection/state records, footprint candidates and their
geometry/movie context. Detection packets retain state-linked tiles and their
claims. Tile relations use the source crop `tile_id`, distinct from the prefixed
canonical row ID. Entity/source indexes and source-set length assessments remain
complete for search, links, source attribution and ranking denominators.

The object page paints this view instead of fetching twenty release JSON files.
The worker terminates after returning the immutable view. Missing full object
collections and unknown IDs are explicit API errors; an unavailable bundle does
not populate records. Provider plot geometry subsequently moved to Rust as described below; named
footprint-candidate presentation remains browser code. The API introduces no new scientific record or relation.

The added gate checks all twenty canonical imports, nine representative current,
eddy, detection, state and classification views, native/WASM agreement, evidence
packet export, source links, mobile layout and first-load failure. Every shipped
collection is exercised by the existing all-collection browser check.


## Dated provider detection plot primitives

`object_view` now includes a `detection_plot` for operational detection entities.
It uses the shared Rust map projector to validate and construct provider polygon
paths and optional center points. Rust computes the equal-angular plot fit,
coordinate bounds, source date, labels and center-cross position. The browser
paints those primitives in the existing 600 by 350 SVG frame and retains the
scope note and evidence packet. Polygon rings use even-odd fill.

Invalid geometry, polygons requiring seam clipping and degenerate extents are
reported without drawing a false boundary. A missing center stays absent rather
than becoming an invalid synthetic point. The plot draws neither coastline nor
state boundaries, encodes no physical length/width/speed, and cannot establish
permanent extent or whole-eddy containment. Existing source observations and
state-relation receipts remain distinct from the display projection.

The object-page gate now covers all four provider detections: source-coordinate
bounds and dates, native/WASM scene agreement, painted paths/centers, fitted frame
and mobile overflow, alongside the other representative evidence views.

## Local integrated verification (2026-10-06)

All 22 browser gate scripts passed against the combined local checkout. The
initial sequence stopped at the dashboard diagnostic refresh assertion, which
used a five-second DOM assertion before the asynchronous checked snapshot had
finished loading. That check now waits for refresh completion, verifies the new
snapshot fingerprint and Rust changed-record count, and then checks the rendered
update light. The corrected script and all remaining scripts passed sequentially;
the three preceding checks had already passed against the same application files.
This was a resumed local verification, not one uninterrupted or remote CI run.

The full offline suite passed with 763 tests and 581 subtests. Whitespace checks
passed, and the canonical `almanac/release/v0.1.0` files have no diff. These results
verify the local migration; they do not establish publication on main or complete
scientific coverage. Named figure-derived footprint plotting still uses browser
geometry code, and unresolved source measurements remain unresolved.

## Named contour plots in canonical object views

Canonical `object_view` responses now include `footprint_plots`, keyed by the
selected footprint candidate IDs. Rust fits each candidate's existing canonical
polygon into the 500 by 350 card frame using the same validated projector as
provider detections. It returns the path, transform, source-coordinate bounds,
date, accessible description and coordinate caption. Missing or unsupported
geometry remains an explicit unavailable plot; seam-crossing geometry is not
closed into a false boundary. No measurement or state relation is added.

The canonical object page uses `footprint-card.js` to paint the Rust scene and
retain the existing attribution, review status, calibration sensitivity, state
assessments and NASA crop links. The dashed contour remains a figure-derived
instantaneous SSH proxy with unresolved whole-ring containment. The standalone
rights-screened preview retains its original asset and browser plot calculation;
its pinned manifest and the frozen release remain unchanged.

The object-page check independently compares source bounds and dates for the
named contour and all four provider polygons, native/WASM response equality,
painted paths, fitted extents and narrow layouts across all nine representative
objects. Expanded mobile checks found a long diagnostic identifier on the Gulf
Stream System card; object-page text now wraps that identifier.

## Global route atlas source loading through Rust/WASM

Native `--atlas` and WASM worker action `atlas` provide the exact source JSON
strings used by the route almanac and global map: the catalog, widths, seasonal
frames, dashboard, proposed additions, optional route/state join, and all 62
candidate reports (68 documents in this snapshot). The builder pins additional
receipts and state-join dependencies. Rust validates each report's schema, source
hash, current identity, displayed route length and geometry against the shared
catalog/map records; state identity sets and join dependency hashes are checked.

`reference-routes.js` loads one checked worker snapshot for its tables and cards.
The global atlas consumes the same snapshot, rather than reading a separate raw
dashboard or route/state join. Missing optional join data leaves the route map
and card available with an explicit unavailable-state-links note. Integrity
failure does not populate fallback cards from unchecked source files.

The dedicated browser check verifies exact source bytes, native/WASM parity,
five loader rejections, all inventory selectors and route cards, disabled direct
JSON reads, narrow layouts, missing optional join and unavailable first load.
The local gate now contains 23 scripts. The previous resumed 22-script result
predates this migration; it is not evidence of a full new 23-script run.

This source-loading migration adds about 5 MB of report receipts to the bundle
(41,020,316 bytes total). Projection, map fit and interactions in the custom
global atlas remain browser code. Lazy dated timeline and observed-section
sources also retain their existing loaders; these are further migration work.

Local verification for this migration passed 28 Rust tests, the dedicated atlas
snapshot check, global current/eddy map navigation, all 124 route/state links,
and all 56 directory identity sets. Directory tests now wait for populated
controls and restored selections instead of fixed short delays. Bundle-load
failure also updates the map status explicitly. These checks do not claim a
new full offline or 23-script CI run, and the changes remain local.

## Saved Gulf Stream timeline sources and paths

The atlas snapshot now also includes the two exact Gulf Stream timeline source
documents (70 source documents total) and Rust map scenes for their 17 saved
diagnostic lines. Timeline receipts are optional to allow an explicit unavailable
sample-set state. When present, Rust requires complete imported frame coverage,
ordered unique dates, matching source fields and timeline hashes, unchanged audit,
algorithm, source-subset and figure dependencies, and the existing annual-range
exclusions. The plots use the shared seam-aware projector; invalid geometry fails
validation instead of inventing a boundary.

`atlas-timeline.js` consumes the checked snapshot and paints the returned paths
with the Rust display transform. It retains sample-step timing, manual controls,
unsampled-day notes, source-processing changes, per-date line/state intersections,
share restoration and cleanup when another card is selected. The global atlas's
fit interaction remains browser code. No unsampled geometry or annual extrema
are introduced. Shared paths have five-decimal geographic display precision;
browser checks use that explicit rounding tolerance when comparing source vertices.

The browser gate now includes the saved-timeline check (24 scripts total). This
addition does not imply that a new full 24-script run has completed. The separate
dated-current detail page and observed-section loader remain further migration
work, alongside the global atlas's geometry and fitting calculations.

Local checks passed for all 17 saved geometries, per-date intersections, calendar
gaps, source links, stable scale, shared-view restoration, playback cleanup,
mobile layout and current identity boundaries. The 70-document atlas check
passed eight loader rejection cases, including altered annual scope, frame
projection and date order. Missing timeline receipts leave the current card
usable and its unavailable sample playback disabled. Native/WASM parity, 28 Rust
tests, syntax and whitespace checks passed; the frozen canonical release has no
diff. These results remain local and are not a new full CI result.

## Observed transverse sections in the checked atlas

The atlas snapshot now includes the exact Antilles May 2005 section diagnostic
source (71 documents total) and `observed_section_views`. Rust binds this document
to its query diagnostic, series evidence hash and pinned profile inventory. It
checks the 400 m instrument depth, transverse-section role, quality classes,
unique cast IDs, UTC timestamps, finite coordinates and nullable local velocities,
and the explicit full-width, annual-range and playback exclusions.

Rust provides source-bound station positions, quality colors, accessible labels,
cast detail text, one-sided diagnostic status and the two-occupation display fit.
The browser paints these positions and manages selection and card cleanup. Map
fitting uses the Rust bounds while retaining a saved global view when present.
The standalone section page remains a separate source loader. No current axis,
edges, full width or annual cycle follows from these transverse instrument points.

Missing optional observed evidence keeps the checked current card and standalone
link available without station overlays. Invalid evidence scope is an integrity
failure and blocks the newly loaded atlas snapshot. The local browser gate now
contains 25 scripts; this is not a claim of a new full 25-script run.

Local verification passed for 23 and 27 stations, native/WASM position agreement,
independent source-coordinate projection, quality colors, saved occupation and
view restoration, keyboard cast selection, standalone round trips, mobile
layout, global/card-switch cleanup and delayed source delivery after disposal.
Missing optional evidence and repinned invalid full-width scope are exercised.
The 71-document atlas parity check passed, as did 29 Rust tests including invalid
UTC times, quality, velocity, coordinate pairs and scientific exclusions. The
canonical release remains unchanged; these changes are local.

## Global atlas cartography in the shared Rust engine

The global atlas now delegates point projection, seam-aware path construction and
geographic fitting to Rust `cartography`. These are stateless display operations;
native `--cartography` reads a request from stdin, and WASM exposes the same
implementation as `osw_cartography`. Both use the shared map coordinate validator
and path construction rules. Invalid coordinates and polygons requiring seam
clipping return errors rather than drawing a false connection. Empty fits return
no new view; a single locator retains its contextual zoom extent.

The data worker supplies the already checksum-verified WASM binary with its atlas
response. `cartography.js` creates a small second instance without loading a
second record store, and calls its stateless export synchronously for interaction.
The browser caches these display results, paints paths/markers, and handles camera
movement, controls and saved addresses. It does not calculate source projection
or geographic fit in `reference-route-atlas.js`. The original scene and record
metadata remain unchanged; this introduces no measured physical extent.

The dedicated check covers 445 unique source-geometry operations from all atlas
features and all 62 route reports, with independent geographic projection and
fit calculations, native/WASM equality, seam breaks and invalid input rejection.
The local browser gate now has 26 scripts; this is not a new full 26-script result.

Local verification passed 30 Rust tests, the 445-operation native/WASM source
geometry check, global current/eddy navigation, shared zoom/pan and reload,
140 eddy cards with 131 scoped state links, touch pinch/cancellation/keyboard
controls, and the 71-document atlas integrity check. The eddy update assertion
now waits for card restoration after asynchronous loading. Source data and the
canonical release remain unchanged. Standalone detail-page loaders and other
presentation helpers still require migration, and publication remains pending.

## Coverage audit: local implementation versus main

Audit updated: 2026-10-07. The local branch `codex/wasm-mainline-dashboard`
starts at main commit `52646dc` (PR #22). The subsequent migrations described
above remain local and unpublished. Local browser success must not be
reported as a main-branch CI result.

| Surface | Local Rust/WASM coverage | Remaining work |
| --- | --- | --- |
| Query UI | All 38 bundled collections, pagination and inspection | Some research documents are not represented by these collections |
| Dashboard | Checked source receipt, selection, coverage/update lights, geographic and Beck scenes | Publish and run the new browser gate in CI |
| Global atlas and current/eddy cards | Checked 77-document snapshot, shared projection/path/fit, current and eddy navigation | Publish and verify the combined gate in CI |
| Object pages | Source-scoped evidence joins and operational/named footprint display scenes | Scientific evidence completeness is a separate task |
| Seasons | Checked four-source snapshot and scoped phase plans | More source-backed seasonal measurements |
| Atlas Gulf timeline / Antilles stations | Checked sources and Rust map scenes; standalone pages use shared checked loading | Publish and verify the combined gate in CI |
| Almanac index | Separate Rust-checked 63-document corpus, typed map scenes, current/eddy/NASA/release joins, all 56 states' membership and context views, NOAA daily/weekly file-scoped queries, source-name reconciliation, illustrated spans and diagnostic samples; actual-page checks cover all 12 NOAA sample dates | Complete the latest-runtime regression gate and publish; frozen historical exports remain separate |
| Movies | Rust filters and joins the exact rights-screened preview subset | Publish and verify the combined gate in CI |
| Standalone diagnostic pages | Antilles, NECC, Gulf Stream and NorKyst use the shared checked snapshot; Antilles paints Rust station positions; NorKyst has dedicated frame/sample queries | Publish and verify the combined gate in CI |
| Loop recorded dates | Rust validates comparison/selection receipts, joins method diagnostics and renders projected scenes; JavaScript manages playback | Publish and verify the combined gate in CI |
| Loop experiment | Static generated content and figures | Content/provenance checks; static prose does not require WASM |
| Screened atlas preview | Existing separately pinned dataset and renderer | Preserve frozen release; any replacement needs a separately versioned surface |

The three atlas helpers identified in this audit have since migrated to the
checked atlas source snapshot: `atlas-monthly-width.js` (Leeuwin),
`atlas-seasonal-width-profile.js` (Kuroshio), and `atlas-monthly-section.js`
(NECC). Their browser controls and presentation guards remain JavaScript;
the NECC helper delegates map projection and fitting to Rust.

Current local verification: 767 offline tests and 581 subtests, 513
standard-library tests, both required NetCDF fixtures, 36 Rust unit tests,
35 almanac JavaScript syntax checks and all 14 page coverage assignments passed.
All 47 amended-engine browser checks passed across sequential gate segments
and the focused check-25 rerun. The final continuation exited successfully.
The segments use the same engine receipt; intervening edits corrected test
expectations and added timeout diagnostics, without changing product bytes.
The observed-section return timeout did not reproduce on its focused rerun;
its cause remains unconfirmed. No uninterrupted full-gate or remote CI result
is claimed. Scientific evidence completeness remains separate.

CI syntax coverage now also discovers every `almanac/**/*.js` file through
`analysis/check_almanac_javascript.py`, rather than relying on a manually
maintained filename list. All 35 current almanac modules passed locally,
including nested preview code. This verifies syntax only; behavior and source
integrity still depend on their respective browser and offline checks. The CI
workflow change remains local and unpublished.

### Earlier gate history

The next gate invocation now includes the existing standalone NorKyst browser
check (27 scripts total), using the shared browser environment setting or
Playwright's installed Chromium. The already running 26-script process retains
its original list and does not cover this addition. NorKyst's garbled middle-dot
separators were corrected in the page title and chart labels; its raw data
loader is unchanged and remains on the migration list. Syntax checks passed;
the updated standalone browser check must run after the active gate finishes.

The combined run passed its first 14 scripts, then exposed an asynchronous
readiness assertion in the state-navigation test: network idle preceded saved
state restoration from the WASM snapshot. The test now waits for the restored
state value and for actual missing-geometry fallback messages/inventory counts,
instead of a fixed delay or immediate read. The corrected state test passed all
56 source shapes, keyboard/pointer navigation, reload and unavailable/malformed
geometry cases. The remaining checks are being run sequentially with the
runner's explicit `--from-check` option, starting at eddy state links. This is a
resumed run, not a new uninterrupted full-suite result.

The almanac syntax command also parses HTML and checks executable inline script
blocks, while excluding external script tags and JSON/data blocks. The current
tree has one executable inline script (the standalone NECC page), which passed
alongside all 30 JavaScript files. Syntax checks neither execute scripts nor
establish shared Rust loading for that page.

### Combined verification completed

All 27 current browser scripts passed locally across the initial run, the
corrected state-navigation rerun, and the sequential resumed run from eddy state
links through NorKyst. The initial process exited at its state restoration race;
the corrected state test and the resumed process both exited successfully.
This is complete coverage of the current gate's script list, with the interruption
and test-only readiness repair explicitly recorded, rather than an uninterrupted
27-script CI run.

Results include all 36 collections and 240 objects; workspace/rebase/taxonomy;
Florida and Agulhas source-scoped dimensions; 100 current phase plans; all 56
state identities/shapes; 140 mapped eddies and 131 recorded state links; 124
route/state links; 20 unchanged canonical collection imports; nine object view
cases; 71 exact atlas source documents; 17 saved Gulf geometries; 23/27 Antilles
station occupations; 445 independently checked cartography requests; and 12
NorKyst frames. Rejections, missing-data behavior, saved navigation, keyboard,
touch and mobile cases remain part of their respective checks.

The offline result remains 763 tests plus 581 subtests, and all 30 JavaScript
files plus the executable inline NECC script pass syntax checks. The frozen
canonical release has no changes. Publication and the remaining loaders in the
coverage matrix are still pending; this result does not establish all-content
WASM migration or new main-branch CI coverage.

## Checked source loading for all three atlas width helpers

Leeuwin's a101 monthly graph, Kuroshio's East China Sea seasonal profiles and
the Pacific NECC 140 W monthly section now load from `oswAtlasSourcesReady`.
The bundle pins their exact original JSON bytes and input hashes in atlas
receipts, bringing the atlas snapshot to 74 documents. Rust checks source
schema/identity, equality with the existing query diagnostic, and the explicit
whole-current/rank/confidence/seasonal exclusions. Historical charts also retain
their no-geographic-playback/no-annual-extrema scope; NECC retains its no-
climatology/no-mean-instantaneous-width and unknown whole-length/annual-range
scope. Existing scoped sample-to-diagnostic validation remains in force.

The browser retains controls, chart painting and its detailed sample/profile
presentation guards. No independent research fetch remains in these helpers.
An absent optional source disables its chart while retaining the atlas/current
card. A changed receipt, a source/query disagreement or invalid scientific
header fails the checked snapshot instead of falling back to an unchecked file.

Local verification passed 31 Rust tests, all three helper browser checks with
direct atlas research JSON reads blocked, and syntax checks. Leeuwin preserves
12 readings and reading allowances; Kuroshio preserves four profiles and missing
samples; NECC preserves 12 monthly sections and 37 source grid samples per
month. Playback end/pause/cleanup, saved selection, map independence, keyboard,
mobile and delayed/malformed presentation-document behavior are checked. The
presentation fault tests explicitly inject bad documents after verified source
delivery; they do not stand in for native receipt rejection tests.

The browser gate now contains 30 scripts. The earlier combined 27-script result
predates this migration; there is no claim of a full new 30-script run. The
updated 74-document source/integrity check passed eleven receipt/schema/scope/
projection rejections, exact native/WASM agreement, and missing optional width
source behavior while retaining the current card. WASM is 1,254,424 bytes
and the bundle is 41,690,420 bytes. The frozen canonical release remains unchanged.

## Standalone Antilles and NECC share the checked atlas

`checked-atlas.js` loads the checksum-verified worker/store and requests the same
Rust atlas snapshot used by the global map. It returns exact source documents
and Rust display scenes, terminates the worker after delivery, and rejects load
or integrity errors. Standalone Antilles and NECC consume this shared loader;
neither fetches research JSON independently. The NECC inline script is now a
separate deferred `necc-section.js` module.

Antilles station coordinates, quality colors and accessible labels come from
the existing Rust observed-section view. JavaScript paints those positions and
the source table, manages occupation selection, and maintains the return link.
NECC paints its original monthly inventory and source-defined brackets. Static
comparison figures and scientific scope notes remain available when dynamic
sources are absent; no unchecked data fallback is introduced.

Both standalone browser checks passed with direct research JSON requests
blocked, saved navigation/round trips, mobile layout and absent-source/load-
failure behavior. Antilles retains 23/27 casts and exact Rust scene positions;
NECC's delivered snapshot equals native `--atlas` output and its twelve rows
retain source-scoped values. All 32 JavaScript files pass syntax checks; no
executable inline scripts remain in the almanac. The browser gate now has 32
scripts, but only the targeted new checks have been run for this slice, not a
new complete 32-script gate. Rust, bundle, original scientific sources and the
frozen canonical release are unchanged by this standalone migration. Dated-
current, NorKyst, index and movies loading remain pending.

## Standalone Gulf Stream dates use checked timeline and width sources

`dated-current.js` now consumes the shared checked atlas loader for both Gulf
timelines and the section-width diagnostic. The latter's exact source receipt
brings the atlas snapshot to 75 documents. Rust binds the width source to its
query diagnostic, protocol/generator/sampler hashes, complete timeline frame
inventory, ordered dates, source subset hashes and processing algorithms.
The local 70 W meridional half-peak metric, scientific-review status, sampled-
value span role and no-annual-extrema/rank/confidence exclusions are explicit.
Selected-day widths remain local section candidates, distinct from streamline
lengths and full-current dimensions.

The page clears dynamic values while changing sequences and disables controls
when its checked evidence is unavailable. Images stay hidden until the selected
source figure decodes. A generation token prevents an older image completion
or failure from changing the newer selected frame's visibility/status. Browser
playback switches between original frames without interpolation.

Local verification passed 32 Rust tests and the new standalone browser check:
all 17 dates, exact native/WASM snapshot, original width/state/source values,
date gaps, manual/play/pause/hidden controls, delayed image replacement, mobile,
missing width receipt and bundle load failure. All 32 JavaScript files pass
syntax checks. The browser gate now has 33 scripts; no full new 33-script run
is claimed. The expanded 75-document source integrity check passed fourteen
rejection cases, exact native/WASM agreement and optional/unavailable data; the
atlas timeline round-trip check also passed. The standalone URL now follows the
selected series/date, so reload and copied links restore the visible observation.
The dedicated check passed again with all selected-address assertions and fresh
page restoration of the copied 2026 date.
WASM is 1,259,936 bytes; the bundle is 41,805,137 bytes. Scientific
sources and the canonical release remain unchanged. NorKyst, index and movies
loading remain pending.

## NorKyst standalone loading and hourly model scope in Rust

NorKyst's section timeline and map-frame catalog now have exact atlas source
receipts (77 source documents total). The bundle builder runs the existing
independent source-reconstruction checks and pins acquisition, generation,
protocol, projection helper, model receipts and map figure hashes. Rust checks
those dependencies, the fixed 24 E meridional section at 10 m, twelve preselected
2024 noon timestamps, 191 ordered samples per frame, finite-or-missing fields,
unknown current dimensions, and synchronized map/profile receipt identities.
Map display rules explicitly prohibit temporal interpolation, named-current
footprints and state-footprint joins. These hourly hindcast samples are regional
context, not monthly means or canonical current measurements.

The standalone page uses `checked-atlas.js`, keeps its original source profiles
and static projected figures, and saves the selected date in the address.
JavaScript still paints profile charts and runs the playback timer; model samples
are not yet separate query collections. Missing either optional document or a
bundle failure leaves its controls disabled and data displays empty.

Local verification passed 33 Rust tests, six independent Python reconstruction/
scope tests, and the expanded NorKyst browser check with direct JSON reads
blocked. All twelve frames, map/profile dates, native/WASM snapshot equality,
saved-date restoration, manual/play/pause/hidden controls, license, mobile table,
missing maps and load failure are covered. The 77-document integrity check
passed all eighteen receipt/schema/scope/support/synchronization rejections,
exact native/WASM agreement and optional/unavailable data. All 32
JavaScript files pass syntax checks. WASM is 1,276,899 bytes; the bundle is
42,513,207 bytes. No original scientific source or canonical release changed.
Index/movies migration and dedicated NorKyst query coverage remain pending.

## Rights-screened movie directory queries and joins in Rust

The movies page now calls Rust `movie_view` through the persistent data worker.
Native `--movies` reads the same selection from stdin; WASM exposes additive
`osw_movies`. Rust selects crop zoom/state/search matches, joins the original
display overlaps, deduplicates linked entities and orders links. JavaScript
paints the returned rows and manages controls, with generation checks that
discard stale responses. It does not fetch release ledgers or calculate joins.

Five exact receipts pin the rights-screened preview manifest and its four input
collections. Rust binds their hashes to the export manifest and its frozen
canonical parent, checks every preview row against the corresponding canonical
record, and requires the complete 70-crop/877-overlap inventory. The movie view
preserves the 218-entity/151-media screened subset, rather than importing excluded
links from the fuller research candidate. Display fractions remain display-area
overlaps with unresolved physical relation; movie geography is not identity or
current/eddy containment. Both frozen releases remain unchanged.

Local verification passed 33 Rust tests and the dedicated movie browser check:
nine independently calculated selections, exact native/WASM view equality,
five invalid selections, five receipt/export/projection rejections, all 70
crops, 56 state options, source-use scope notes, mobile and missing/failing data.
Direct release JSON reads are blocked in the browser check. UTF-8 is explicit
for native output, preserving source labels such as Sunda–Arafura.

The synthetic rebase fixture omits a stale optional movie export when changing
its canonical Kuroshio label. The old snapshot retains its original reviewed
subset; the synthetic new snapshot has no newly reviewed movie view and returns
an explicit unavailable result. The rebase interaction check passed retained
baselines, conflict choices, native/WASM parity, old-source preservation and
mobile behavior. The
browser gate now has 34 scripts; this is not a full new 34-script result. All
32 JavaScript modules pass syntax checks. WASM is 1,331,957 bytes; the bundle is
43,138,479 bytes. Index migration and dedicated NorKyst query coverage remain
pending, along with publication.

## Current combined gate and index loading inventory

A new complete 34-script browser run started on 2026-10-06 against the current
checkout, using the existing verified server on port 8788. Its result is pending;
the earlier resumed 27-script run and subsequent focused checks remain separate
evidence. Remote main was checked directly and remains `52646dc`.

The index has 52 unique literal source paths (including coverage and the optional
route/state join), totaling 48,139,958 raw bytes. Twelve NOAA snapshot/weekly
documents dominate this inventory. Appending all raw receipts to the shared
43,138,479-byte query bundle would duplicate much of the scientific corpus and
substantially increase every page's load. Index migration therefore needs a
separate checked surface payload or shared-source reuse, together with explicit
Rust-owned section queries; changing the JavaScript loader's name would not
complete migration of its filtering and joins. This inventory does not declare
all source files queryable or infer new current/eddy identities.

## NorKyst model query projection prepared separately

The candidate builder now adds `model_frames` (12 records) and `model_samples`
(2,292 records), with source-hour/date/depth support, exact field values and
nulls, source pointers, units checked against all 12 acquisition receipts, and
links from the Norwegian Coastal Current context. These remain model section
records, not observations, monthly means, named-current boundaries, ranked
widths or lengths, annual extrema, or state footprints. All current dimensions
remain null. No scientific source or canonical collection was changed.

Rust reconstructs both query projections from the checked atlas receipts and
requires exact equality, complete inventories and owner links/counts. Its query
map scenes show the fixed section support or sampling sites, including known
sites with missing fields; the map scope excludes physical boundary inference.
Earlier bundles without either model collection retain their original behavior.
A bundle declaring these collections must retain both source documents.

This candidate was built into `.pytest_cache/model-query-bundle.json`, not the
shipped bundle, while the complete 34-script browser gate continues against the
previous shipped runtime. The candidate contains 38 collections and is
45,271,553 bytes. A separate Cargo target preserves the gate's CLI binary.
Verification passed all 34 Rust library tests, four Python source/support tests,
native frame and sample queries (including January, final-page and unavailable
field selection), and five native loader rejections: changed field value,
invented current width, changed source time, truncated sample inventory and
missing map source. Matching map inventories are independent of pagination.

Browser presentation, shipped WASM rebuild, focused parity checks and admission
of this candidate to the combined gate are pending. The shipped browser still
has 36 collections; this work must not be reported as 38-collection WASM or main
coverage yet.

### Current 34-script run: interruption and continuation

The first 18 checks passed, including all collection pages, dashboard, workspace,
rebase, taxonomy, Florida/Agulhas evidence, touch/shared views, all 56 OSW state
shapes, 140 eddy cards and route/card navigation. Check 19 (route/state links)
timed out while dispatching a click to the Agulhas Return studied-reach route
button. A focused rerun of the unchanged test and unchanged shipped assets
passed all 124 route/state links, optional-join fallback and state navigation.
No product fix or causal explanation is claimed from that rerun.

The gate is continuing sequentially from check 20,
`test_seasons_rust_snapshot_browser.py`. This is a resumed run with a recorded
failed attempt and successful focused rerun, not an uninterrupted full gate or
a main-branch CI result. The source-only model query work and unreferenced model
card module have not changed the engine, bundle or query UI used by this run.

The separate model card module now presents source UTC time/depth, fixed section
limits, source units and all three scalar fields, null availability, sampling
and interpolation limitations, credit/license, the regional model field figure,
and links between source frames and individual samples. Its browser test is
prepared to verify original source values, seven loader rejections, all matching
map records independent of table pagination, keyboard frame/sample navigation,
saved filters, mobile and unavailable data. The module is not yet referenced by
the shipped query page. Syntax passes for all 33 current JavaScript modules;
compilation of the new browser test passes. Neither is a rendered UI result.

### All 34 shipped-runtime checks completed

The resumed process exited successfully after all remaining checks (20–34).
Together with the initial 18 passes and the focused unchanged rerun of check 19,
all 34 scripts passed for the 36-collection shipped runtime. The click timeout
and separate rerun remain recorded above; this is not an uninterrupted run or
a CI result on main.

Runtime files at completion:
- `almanac/query-data.json`: `6f82926dbee5ae20aa32d322f6d487ac189d42368b1835e4f8bef3e7024e548e`
- `almanac/query-engine.wasm`: `db8b577f243decef3f487448d1fbd62133049f0a354c2af81280119cdccaeb9e`
- `almanac/query-engine.manifest.json`: `1abfa1ad77e1ef0a800150a8542218101a290343d56661d4029600912b30271c`

The next rebuild adds the two candidate model query collections and their UI;
this later runtime requires its own focused verification.

## NorKyst query collections and UI integrated

The rebuilt shipped local bundle now contains 38 collections. `model_frames`
and `model_samples` are queryable through the same Rust store and worker as the
existing collections. Query presets expose all hourly frames and January sites.
Frame cards show source UTC time, depth, selected section limits, available
fields, source units, credit/license and the regional field map, with links to
individual samples and the recorded-date page. Sample cards link back to their
source frame. Typed model map scenes use fixed section support/sampling sites;
`model_date` and `sample_time_utc` are distinct from observational support. No
physical current geometry is added to the Norwegian Coastal Current object.

The focused model browser check passed all original frame/sample values and
source support, seven loader rejections, exact native/WASM queries and map
inventories independent of pagination, keyboard sample/frame navigation,
saved filter restoration, source scopes, 320 px layout and unavailable data.
The mobile card screenshot was inspected. All 34 Rust tests, four Python
projection tests and syntax for 33 JavaScript modules passed. The current engine
is 1,360,945 bytes and the bundle is 45,271,553 bytes.

The new browser test is now in the 35-script gate. This is not a complete
35-script result: the earlier 34 checks covered the prior 36-collection runtime
with its documented interruption, and the focused model check covered the new
runtime. The full collection UI check is running for the new bundle. Publication
and index/Loop/frozen-preview migration remain pending.

The updated collection browser check also passed all 38 shipped collections,
first/last pages, record inspection, exact canonical imports and all 240 object
map marks. It ran after the focused model check, sequentially. Opening the January
model frame with its saved query/inspection address was queued by the app;
visibility is not confirmed.
These are local verification results; main and CI remain unchanged.

## Checked Loop recorded-date playback

The standalone page now consumes `loop_recorded_view` from Rust through the
worker. Additive ABI `osw_loop_recorded`, native `--loop-recorded`, and worker
`loop_recorded` return the same minimal view. Two exact receipts bind the
comparison and predeclared source selection to input hashes, generator and all
eight method diagnostics. Rust rejects changed date order, source joins,
outcomes or admission flags. Source labels, failed scenario counts, method
differences and rounded display values are derived in Rust. Shared cartography
projects every source vertex and the editorial gates with a fixed map extent.

The generated HTML retains all four outcomes and query links for static access,
while embedded frame JSON and Python-projected animation paths were removed.
JavaScript paints checked scenes and manages date selection, playback, saved
dates and accessibility. Failed NOAA traces remain gray diagnostics here and
remain excluded from the query atlas's connected geometry frames. No current
length/width, annual extrema, seasonal phase, confidence interval or new identity
is admitted. A missing or invalid checked view leaves dynamic paths empty and
controls hidden, while preserving the retained table.

The browser check exposed `.controls { display:flex }` overriding the container's
`hidden` attribute on an unavailable load. The generated stylesheet now enforces
`[hidden]` and the rerun passed all three unavailable cases. Verification passed
35 Rust tests, three original scientific/generator tests, ten native loader
rejections, exact native/WASM view equality, independently projected vertices,
all four dates, direct source JSON reads blocked, query/date round trips, saved
date reload, keyboard playback, manual/hidden/reduced-motion stop behavior and
320 px layout. The rendered desktop screenshot was inspected.

The bundle still has 38 collections and is 45,280,796 bytes; WASM is 1,389,202
bytes. The Loop check is now included in the 36-script browser gate. A complete
new 36-script run has not been performed; older combined results and subsequent
focused model/collection/Loop checks remain distinct evidence. Frozen releases
and original Loop source documents remain unchanged. Index loading/joins,
frozen-preview versioning, broader scientific evidence and publication remain
pending.

## Index backend coverage audit (local, 2026-10-07)

The legacy index's literal loaders cover 52 documents, but seasonal selection
also requests nine additional snapshots. The checked index inventory therefore
contains 61 exact source documents and all 12 seasonal snapshot dates. Original
source bytes total 67,380,894; a separate lossless gzip packet is 4,755,202 bytes.
This corpus does not enlarge the 38-collection main query bundle.

`index_store.rs` validates the packet against a compiled catalog and every source
hash, byte count, root shape and schema. Additive load/query/document WASM exports
and an independent index worker provide source-scoped JSON-pointer queries,
filters, sorting and pagination. Source addresses are not persistent scientific
identities or new current/eddy membership claims. The old index page has not yet
been wired to this worker; its loaders and joins remain a migration gap.

The engine builds with 36 passing Rust tests and 34 JavaScript syntax checks.
WASM is now 1,448,576 bytes. The isolated backend check passed all 61 exact
source bytes/hashes, all 12 seasonal snapshots, an independent NOAA state/radius
query oracle, native/WASM metadata and query parity, source document retrieval,
invalid requests, changed packet rejection, and three browser input-tampering
failures with no raw research or main-bundle fetch. It is included in the now
37-script gate. These results are separate from index page coverage and from a
complete combined regression run; neither is claimed complete.
Remote main still resolves to `52646dc55f34f2c0df94d548aa2501964b4bad38`;
the broader migration changes are local and uncommitted.

## Checked index page loading and projection (local)

The index now uses `checked-index.js` and the independent Rust worker for its
document loads, including on-demand NOAA snapshots. Inspecting the supplemental
diagnostic-links helper found two additional timeline documents. The full page
corpus is therefore 63 documents, 67,771,372 original bytes, and 4,813,854 gzip
bytes. Both diagnostic timelines use the checked store too. Historical releases
are unchanged; their selected sources are read through the same catalog.

The worker supplies its verified WASM binary to shared stateless cartography;
index point projection now runs in Rust. The shared load/request client rejects
unknown paths, changed inputs, worker failures and timeouts without fetching raw
JSON. JavaScript retains presentation, joins and filtering; this is not a claim
that the entire index query/navigation logic has moved into Rust.

The actual-page browser check passed 100 current rows, current/eddy search,
saved state restoration, all 12 NOAA date options and exact state-specific map
inventories/independent point projections, diagnostic state links, 320 px layout
and unavailable-corpus behavior. All 36 Rust tests and syntax for 35 JavaScript
files passed. Rebuilt WASM is 1,449,304 bytes. The gate now includes both isolated
backend and actual-index checks (38 scripts); a complete latest-runtime gate
remains pending. This supersedes the preceding audit's index-loader gap and
61-document inventory, while its remaining joins/publication gaps still apply.

The rebuilt isolated backend check also passed with all 63 documents. The
actual-page rerun passed project-prefix hosting as well as the original root
URL; catalog addresses are relative to the project root. No research JSON,
historical release JSON, or main query bundle was fetched by the index page.

## Index current view queries (local)

Rust now builds the index's current rows from the original current, classification,
length-evidence, NASA-crosswalk, crop-link and taxonomy documents. It resolves
parent/component, name-overlap and source-associated current labels, NASA feeder
flags, scene/crop URLs and evidence records. Search and setting/length/NASA
facets execute in Rust. Competition ranks are calculated over the full inventory
before filtering, with unranked values kept null. Unknown facets and request
fields are rejected. These joins do not add geometry, identity equivalence,
physical dimensions or ranked claims to the source ledgers.

The additive `osw_index_currents` export, worker action and native
`--index FILE --currents -` return the same view. JavaScript paints existing
cards, formats source values and manages input/navigation. Sequence numbers
discard obsolete replies during rapid input. Related-current, map and state
links reset all four current filters and await fresh rows before jumping.

The focused check passed exact original-ledger joins for all 100 currents,
global ranks, five native/WASM views, 26 search/facet cases, invalid selections,
rapid input and related/map navigation. All 36 Rust tests, 35 JavaScript syntax
checks and whitespace checks passed. WASM is 1,482,899 bytes. The current-view
check is included in the now 39-script browser gate; no complete latest-runtime
gate is claimed. Other index sections still retain JavaScript joins/filtering,
and the local changes remain uncommitted/unpublished.

The actual-index page check also passed again after current-view/navigation
integration, including all 12 NOAA dates, source map inventory/projection,
diagnostic state links, mobile/outage behavior and project-prefix hosting.

## Index named-eddy views (local)

The Loop-name table, geography table and combined search inventory now use
`IndexStore::eddy_view`, additive `osw_index_eddies`, native
`--index FILE --eddies -`, and worker `eddies`. Rust searches the same original
source fields in their original order and resolves Loop contexts and linked
primary names, geography state/movie contexts, family parents and source-related
currents. Every row retains its exact source record and array pointer. The
inventory keeps all 136 source identities distinct, including duplicate labels;
empty searches leave the combined list empty while retaining declared counts.

JavaScript paints the existing tables and manages requests/navigation. Independent
sequence counters prevent outdated results from replacing a newer search. Family,
inventory, map, NASA-context and state links await the source table reset before
jumping. Published-study anchors retain their existing static navigation. No
regional locator, secondary name, class link or crop context is promoted to an
individual footprint, dated identity match, or persistent NOAA track.

The first check passed source comparisons but failed a pointer click on Batumi:
the nearby Sukhumi marker intercepts that location. Eddy map links now explicitly
support keyboard focus, with the existing focus styling; the revised check uses
Enter to reach Batumi without shifting either source location. The overlap itself
still exists at this map scale. The complete focused rerun passed 96 Loop and 35
geography records/joins, all 136 searchable inventory identities, six exact
native/WASM views, family/map/inventory navigation, invalid requests, rapid
search and 320 px layout. All 36 Rust tests, 35 JavaScript syntax checks and
whitespace checks passed. WASM is 1,502,890 bytes. The new check is in the now
40-script gate; a complete latest-runtime gate and publication remain pending.

The actual-index page check passed again after named-eddy integration: 100
current rows, all 12 NOAA date inventories/projections, diagnostic state links,
saved state, mobile, unavailable corpus and project-prefix hosting.

## Index NASA-object query view (local)

All 22 NASA-object rows now use `IndexStore::nasa_view`, additive
`osw_index_nasa`, native `--index FILE --nasa -`, and worker action `nasa`.
Rust resolves the original form/classification, parent/examples/system/class
links, external named-current context, catalog/named-eddy context, releases and
their evidence, feature media, cartographic crop contacts and directly linked
movie variants. Rows retain their exact original records and source pointers;
all crosswalk state evidence and property scopes remain unchanged. Release
evidence counts are computed over the full crosswalk before search filtering.

JavaScript paints the existing content, formats times and labels, and handles
input/navigation. A shared NASA-anchor handler resets search and awaits checked
rows before jumping, including links from other sections. NASA-row current
links also reset current filters before navigation. Obsolete search replies
are ignored. The index exposes `oswIndexPageReady` only after core sections
finish initial rendering; page checks use this signal instead of an early row
count. Diagnostic sample helpers retain their separate asynchronous readiness.

The focused check passed all 22 original records and every source/media/context
join, four exact native/WASM views, all original names, source media-group links,
filtered parent/current/map navigation, invalid requests, rapid search and
320 px layout. All 36 Rust tests, syntax for 35 JavaScript files and whitespace
checks passed. WASM is 1,525,838 bytes. The new check is included in the now
41-script gate. Release catalog and state views still use JavaScript joins;
complete latest-runtime regression and publication remain pending.

The actual-index page check passed again after NASA-object integration and the
readiness change: 100 currents, all 12 NOAA date inventories/projections, state
and diagnostic links, mobile, unavailable corpus and project-prefix hosting.

## Index release-media view (local)

The seven audited release panels now use `IndexStore::release_media_view`,
additive `osw_index_release_media`, native `--index FILE --release-media -`,
and worker `release_media`. Rust resolves each original release to its source
audit, frozen registry citation/credit and every identified object's
release-specific evidence. It checks the complete seven-release/55-movie
inventory and requires both citation and credit text. Registry resolution
preserves the existing last-record-per-URL rule. Every release and movie record
is returned unchanged; media variants remain media listings rather than newly
identified ocean objects.

JavaScript renders the checked release panels and uses the shared NASA
navigation handler to reveal objects hidden by search. The focused browser
check passed exact original-source joins, all 55 movie URLs/filenames/source
descriptions, all credits/citations and passage links, native/WASM equality,
filtered object navigation and expanded panels at 320 px. All 36 Rust tests,
35 JavaScript syntax checks and whitespace checks passed. WASM is 1,537,231
bytes. The new check is in the now 42-script gate; no complete latest-runtime
gate is claimed. State views, Marine Regions name reconciliation and illustrated
span joins still use JavaScript, and publication remains pending.

The actual-index page check passed again after release-media integration,
including all 12 NOAA sample dates, state inventories and source projections,
diagnostic links, saved state, mobile/outage behavior and project-prefix hosting.

## State observation and movie context queries (local)

`IndexStore::state_context_view`, additive `osw_index_state_context`, native
`--index FILE --state-context -`, and worker `state_context` now resolve state
reference-route scenarios, the fixed analyzed front and diagnostic streamline
relations, local published current observations, dated operational eddy records,
additional named-eddy point visits, shared Loop-region names and published Loop
center points. Original state selections and source records remain unchanged.
Related current/eddy identities are resolved from their source ledgers in Rust.

Rust also resolves recommended regional crops and the overview crop from exact
source IDs, retains polar perspective selection, and selects the approximate
movie seek only when the separate crop timeline contains that sampled date.
Requests are limited to the 12 declared NOAA sample dates, with atomic state
batches and invalid selection rejection. Fixed September 2026 observations keep
their own dates when a 2021–2023 NOAA day is selected. Point/gateway, editorial
scenario, operational polygon, diagnostic line and geographic movie contexts
remain separate evidence types; no individual NASA identity or whole-current
dimension is inferred.

JavaScript formats and paints the checked view, caches it by state/date within
one source corpus, and retains controls/navigation. The focused check passed all
56 state source joins across all 12 dates, fixed observation dates, missing movie
seeks and alignment scopes, native/WASM equality, route/local-observation and
movie DOM inventories, invalid selections and 320 px layout. All 36 Rust tests,
35 JavaScript syntax checks and whitespace checks passed. WASM is 1,595,619 bytes.
The check is included in the now 44-script gate; complete latest-runtime
regression and publication remain pending. NOAA daily detections, weekly tracks,
the diagnostic-sample helper, Marine Regions reconciliation and illustrated
spans still require migration.

The actual-index page check also passed after context integration, including
all 12 NOAA maps/inventories, source projection, state/diagnostic navigation,
saved state, mobile/outage behavior and project-prefix hosting.

## State evidence memberships (local)

`IndexStore::state_membership_view`, additive `osw_index_state_memberships`,
native `--index FILE --state-memberships -`, and worker `state_memberships`
now resolve all 56 states' current, NASA and named-eddy membership groups.
Single-state requests and atomic batches return the same source-preserving
views; metadata requests return the state picker. Unknown states, duplicate
batch members, conflicting selection forms and unknown request fields fail.

All 13 group types remain distinct: schematic/editorial lines, stable mapped
arrows, width-sensitive map contacts, OSW gate crossings and current/NASA/eddy
locator candidates. Rust resolves source names and complete source records,
stable/width-sensitive arrow IDs, NASA class/example context, unresolved pairs
and declared map-evidence counts. Context and unresolved ordering follows the
original NASA ledger. No class footprint, observed passage, containment or
identity equivalence is inferred. JavaScript formats and paints the typed
membership views, caches them within one checked corpus, and ignores stale
selection replies. Clearing the picker now clears the saved URL state and
selected-state count.

Verification passed every original membership/name/arrow/context/unresolved
pair across all 56 states, native/WASM batch equality, DOM membership and
context/unresolved links, invalid requests, rapid selection and cleared-state
navigation. The first browser assertion compared an uppercase CSS-rendered
heading with its original text; it now checks both text content and the existing
uppercase rendering. A later assertion attempted to join integer arrow IDs as
strings; it now preserves the original numeric IDs and checks their display
string separately. The complete focused rerun passed. All 36 Rust tests, 35
JavaScript syntax checks and whitespace checks passed. WASM is 1,571,875 bytes.

This is the membership portion of state migration. Dated observations, named
eddy point visits, NOAA detections/tracks and state movie selections retain their
existing JavaScript joins; their migration remains required. The new test is
included in the now 43-script gate; complete latest-runtime regression and
publication remain pending.

The actual-index page check passed after membership integration: all 12 NOAA
dates, source-specific state map inventories/projection, 100 current rows,
diagnostic links, saved state, mobile/outage behavior and project-prefix hosting.

## NOAA file-scoped state and track queries (local)

The new `index_noaa.rs` resolves all declared NOAA daily state inventories,
original records and source pointers, geographic display coordinates, weekly
track availability and dated NASA crop context. `noaa_state_view` preserves
contained and intersected groups separately, with weekly center visits and
weekly contour relations as distinct source records. `noaa_track_view` returns
the original file-scoped trajectory, projected points and seam-separated path,
center/contour visits and approximate regional movie-date context. Requests
reject unknown sample dates, states, cross-file detection addresses, unsupported
focus dates and extra fields. Single-position tracks remain renderable.

Additive WASM exports, native `--noaa-state`/`--noaa-track` commands, worker
operations and checked client APIs serve the state UI. JavaScript paints rows,
markers and paths; track buttons capture the displayed source date/state. Stale
track replies are discarded. A failed date change restores the previous source
selection. Existing initial source clones remain a loader cleanup task; their
presence is not evidence of new scientific identities or measurements.

The original page check passed all 12 NOAA map inventories after integration.
The first new source check completed its inventory/weekly/path comparisons but
failed the final pointer click because a parent details panel was closed; the
check now opens the actual panel hierarchy before clicking. A concurrent rebuild
also encountered the native executable's Windows file lock. That test terminated
before the rebuild was repeated successfully. All 36 Rust unit tests passed;
WASM is 1,637,495 bytes. The focused rerun passed all 12 dates × 56 state inventories, original source
records/pointers, projected coordinates, detection crop tiles/seeks, three
weekly center/contour joins, shortest/longest/seam-crossing track examples,
native/WASM equality, invalid source selections and actual track-button
navigation. The actual-page check passed again, including saved state, all
12 maps, mobile/outage and project-prefix hosting. All 35 JavaScript syntax
checks and whitespace checks passed. The required
browser gate now contains 45 scripts; its complete latest-runtime run and
publication remain pending. Diagnostic helpers, source-name reconciliation and
illustrated-span logic still need migration.

## Source-name, illustrated-span and diagnostic support queries (local)

`index_support.rs`, additive `osw_index_support`, native `--support`, the
checked worker and client now serve three strictly typed sections. Source-name
reconciliation preserves all 52 original Marine Regions decisions, search over
the original name/source/review fields, exact/alias/candidate/excluded facets,
source addresses and original OSW current records. Unknown facets and unrelated
request fields fail. Display-span rows preserve the original 24 ranked entries,
source order and current-record joins, including null published lengths and the
original metric/ranking/uncertainty statements. The UI's current links now reveal
filtered current rows before navigation.

Diagnostic queries resolve both saved Gulf Stream timelines for all 56 states,
returning original frame/relation records, file pointers and saved atlas links.
The browser helper paints those typed rows. Missing or rejected checked queries
show unavailable context rather than implying absence. The corpus builder now
explicitly retains both Rust diagnostic dependencies after removing browser
source reads; its 63-source inventory and original source bytes are unchanged.

Verification passed all source-name facets and every source name, exact original
span/current joins, both diagnostic sets for every state, native/WASM and DOM
agreement, invalid request rejection, filtered-current navigation and 320 px
layout. The actual-page check initially accepted a previous state's diagnostic
list before the newly selected state painted; it now waits for the selected
state and its completed diagnostic query. Its corrected rerun passed, including all 12 dated NOAA maps, 100 currents,
source projection, saved-state/diagnostic navigation, mobile, unavailable corpus
and project-prefix hosting. All 36 Rust unit tests and 35 JavaScript syntax checks passed. WASM
is 1,660,704 bytes. The complete 46-script latest-runtime gate and publication
remain pending, along with redundant source-loader cleanup and remaining
map-render join auditing.

## Checked index map scene and loader cleanup (local)

`index_map.rs`, additive `osw_index_map`, native `--map` and worker/client map
queries now resolve current/classification locators, the shared Loop-region
marker, published Loop center points, independent NASA-object locators, and
named-eddy geography markers. Rust also projects the dated NAVO front lines,
partial geostrophic diagnostic and four operational eddy outlines, preserving
source geometry and per-layer lengths/dates. JavaScript paints the checked
scene and maintains navigation/toggles; no additional footprint or passage
claim is inferred. Observed and editorial locators keep their original labels.

The index startup no longer clones its 51-document source list or any daily/
weekly NOAA snapshot. Typed queries supply all map, table and selected-state
views. Only the small date-picker manifest and frozen classification counts
are requested as full documents. The new explicit `index-sources.json` registry
preserves the complete 63-source corpus independently of browser loaders;
manifest discovery still verifies all 12 seasonal source documents. Exact
original source bytes and the compressed corpus are unchanged.

The focused map check passed every original locator/ordering/projected point,
front/diagnostic/polygon source geometry, native/WASM/DOM scene agreement,
map toggles, and exactly the two remaining document requests. Its first DOM
selector also included operational polygon anchors, which do not contain
circles; the corrected selector checks only the actual locator markers, while
polygons are checked independently. The actual-index page check passed all 12
NOAA map inventories, 100 currents, source projection, state/diagnostic links,
mobile/outage and project-prefix hosting. All 36 Rust tests, 35 JavaScript
syntax checks and whitespace checks passed. WASM is 1,688,773 bytes. The complete
47-script latest-runtime gate is being started; publication remains pending.

## Latest-runtime validation, first segment (local)

The full 47-script browser gate is running sequentially against the shipped
1,688,773-byte engine. Its first five checks passed: native/WASM query behavior,
all 38 collections (first/last pages and record inspection), all 240 object map
marks, dashboard receipts/updates/outage retention, scoped diagnostic navigation,
and durable workspace revisions/replay/conflicts/import/archive/storage abort.
The runner is currently checking workspace rebasing; no complete gate result
is claimed yet. Continue the same live runner rather than restarting it.

The complete offline pytest suite passed 767 tests and 581 subtests in 224.51 s.
The standard-library baseline passed 513 tests in 101.826 s. Both separately
required OISST/Argo NetCDF fixtures passed. Their first direct invocation used
an unwritable sandbox temporary directory; repeating with TEMP/TMP set to the
workspace's publication-temp directory passed both fixtures. Python compilation,
all 35 almanac JavaScript modules, and the nine other workflow JavaScript entry
points passed syntax checks. No research or frozen release files are changed.
These are local results; main-branch publication and remote CI remain pending.

## Refreshed index role review (local)

The installed CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL and LOGBOOK lenses
were applied to the migrated index/map/NOAA candidate and written to
`signals/roles/check/wasm-index-mainline-roles-check-2026-10-07.md`. ORBIT is
inapplicable to this code artifact because it introduces no planetary analogy.
The review records 21 findings: 18 P3 confirmations/improvements and three P2
conditions, with no P1 scientific invalidity identified by this internal review.
It is not external scientific peer review or permission to publish.

One concrete code fix remains: the weekly-track handler requests smooth scrolling
without checking reduced motion. Apply the preference check and exercise the
actual track button after the fixed-asset gate finishes; regenerate the checked
catalog/engine for that app change. The other two conditions are completion of
the latest browser gate and truthful publication status. The same live runner
has passed rebasing, complete taxonomy graph/filter/navigation checks and Florida
width statistics (eight checks completed), and is checking the Florida monthly
plot. Do not restart it merely because a polling interval returns no output.

## Explicit page coverage assignments (local)

`plans/almanac-page-coverage.json` enumerates every shipped almanac HTML page:
12 current WASM interfaces, one generated static diagnostic, and the separately
pinned historical screened preview. `analysis/check_almanac_page_coverage.py`
checks the complete filesystem inventory, duplicate addresses, local script
existence, each current page's declared entrypoint and membership of its browser
check in the required runner, plus the static builder/source test and frozen
preview checker. Static diagnostics cannot acquire scripts silently. The new
workflow step fails when a future page lacks a declared validation assignment.
Assignments are explicitly not passing results, mainline publication, or
scientific completeness. This distinguishes the historical preview rather than
claiming it migrated to WASM.

The page assignment check passed all 14 pages. The independent frozen preview
checker passed 218 entities and 8,709 claims. Both operate without changing the
frozen export. The running 47-script gate has passed checks 1–16, including
Florida monthly playback, Agulhas mean-section scope, seasonal/dashboard atlas
links, real touch zoom, shared views, all 56 saved state shapes, and 140 mapped
eddy cards/131 scoped state links. Reference-route atlas verification is active;
the original runner is still being continued. Reduced-motion track scrolling
and completed publication gates remain open review conditions.

## Route-state readiness and reduced-motion correction (local)

The original live gate terminated at check 19, after checks 1–18 passed. Its
route-to-state assertion read the result list as soon as the picker became EAFR,
before the typed state context finished painting. The check now waits for the
index readiness signal and the selected state's completed context. Its focused
rerun passed all 124 route/state links, sensitivity scopes, navigation and the
optional-data fallback. This is a concrete readiness correction, not a removed
source assertion or a timeout-based restart.

With that runner confirmed terminal, the track jump was corrected to honor
`prefers-reduced-motion`: instant scrolling for reduce, smooth otherwise. The
actual-button check records both requested scroll behaviors while checking the
same source path. Its full NOAA source rerun is currently active. The catalog
and native/WASM engine were rebuilt successfully; all 36 Rust tests passed and
the engine remains 1,688,773 bytes, with newly pinned app/catalog hashes. The
first segment's engine receipt precedes this app change; a complete new-engine
browser gate must run after the focused verification rather than claiming the
interrupted run proves the updated candidate.

README now describes the local candidate, its 38 collections, separate 63-source
index, all 14 page assignments and the frozen-preview exception. Mainline
publication and remote CI are still pending. The seven-role review's scrolling
finding will be closed after the actual-button check passes.

The corrected NOAA source/button rerun passed all 12 dates × 56 states and both
reduced-motion scroll modes. Page assignments, all 35 JavaScript syntax checks
and whitespace checks also passed. The HARBOR P2 is closed in the role review;
two publication conditions remain. A new full 47-script gate is starting against
engine SHA-256 `cbab9583c5e29f9bffb4641e629f06af998b4410dd463984da9d4ea04846f5f0`.

The new full gate's first query check passed against the amended engine; all-
collection verification is active in the same runner. A targeted publication
boundary scan of 103 changed text files found no private Windows user paths,
private-key blocks or GitHub-token patterns. It reported addresses only and
never printed matching credential content. This limited scan is not a complete
security audit and does not close the outstanding browser/publication gates.

Remote main was reverified at `52646dc55f34f2c0df94d548aa2501964b4bad38`.
Its enforced, strict required checks are `offline` and `netcdf-fixture`; linear
history is enabled and the required human approval count is zero. Local success
remains distinct from a completed protected-main publication.

## Object-check collection inventory correction (local)

The amended-engine gate passed checks 1–21, including the corrected 124-link
route/state readiness check, four-source seasonal receipt/phase checks and the
NGCC/El Niño direction scopes. It then terminated at the object-view check's
obsolete `len(collections) == 36` assertion. The shipped bundle has 38 collections
after adding the two NorKyst model collections; the complete collection check
already verified them.

The object check now requires exactly the union of declared canonical and
editorial collections, retaining the frozen 20-canonical-collection count and
all original-source equality assertions. Its output reports the actual declared
count. This avoids treating unrelated collection additions as an object-view
failure while still rejecting undeclared or missing collections. No product,
source bundle, engine or scientific assertion changed. The prior runner is
confirmed terminal; a sequential continuation is active from check 22 using
`--from-check test_rust_object_view_browser.py` against the identical amended
engine. The complete 22–47 segment remains pending.

The check-22 continuation passed the corrected object view, all 77 atlas source
receipts with 18 rejection cases, and all 17 saved timeline geometries. It then
terminated at check 25's 90-second wait for the observed-section selector after
the standalone return link. The orchestration wait also returned unusually late;
that observation is not proof of a cause. Process inspection confirmed the
runner terminal before any restart.

The same observed-section check, with unchanged production code and added
failure-context diagnostics, passed a focused rerun: all 23/27 source station
positions, occupation/share restoration, keyboard cast interaction, standalone
return, mobile, cleanup/disposal and invalid/missing-source cases. The earlier
timeout's cause remains unconfirmed. The extra diagnostics are retained rather
than claiming an undocumented fix. The same-engine sequential continuation is
now active from check 26 (`test_rust_cartography_browser.py`); checks 1–24 and
focused check 25 have passed. The complete remaining 26–47 segment is pending.

The check-26 continuation passed 445 source geometry requests across all 62
reports and atlas features, including independent projection/fit, native/WASM
identity, seams and invalid requests. It then terminated at NorKyst's missing-map
fixture: the test expected the page's optional-view message, but the new model
frame/sample collections require that receipt during Store loading. The actual
rejection was `Missing atlas source bytes`, before any page view could load.

The check now verifies that earlier rejection in both native and browser paths,
retaining disabled controls, hidden map and empty-row assertions. No product or
engine bytes changed. The original runner was terminal before continuation from
check 27. The corrected NorKyst check passed all 12 frames, playback/manual/hidden
controls, saved date, source/license, mobile and both unavailable-source cases;
check 28 also passed all 12 historical width readings/margins and missing/invalid
scope. Check 29's seasonal-profile verification is active in the same-engine
continuation. The full remaining browser segment and protected-main publication
are still pending.

## Same-engine continuation through check 39

Checks 29–39 passed: seasonal and monthly profiles, standalone Antilles and
NECC navigation, dated Gulf Stream evidence, rights-screened movies, 12 model
frames/2292 samples, four recorded Loop dates, the 63-source index store, the
index page's 100 currents/all 12 dated NOAA inventories, and current joins/ranks
with 26 filter cases and related-current navigation. The live runner continues
at the eddy check (40 of 47). Page assignments and whitespace checks passed
again. The engine remains SHA-256
`cbab9583c5e29f9bffb4641e629f06af998b4410dd463984da9d4ea04846f5f0`;
publication and the remaining browser checks are unverified.

Checks 40–42 also passed: 136 eddy identities and original Loop/geography
records, 22 NASA objects with original media/context joins, and seven releases
with 55 media listings and exact credits/citations. The same live continuation
is checking state memberships (43). A scan limited to the runner's 47 required
scripts found no hardcoded Windows paths or mandatory `OSW_TEST_BROWSER`
environment lookups. The shared native CLI helper selects the platform-specific
executable, and CI installs Playwright Chromium. This source inspection does not
establish a Linux runtime pass; remote CI remains pending.

Check 43 passed all 56 states and all 13 distinct evidence groups, preserving
source names/arrows, NASA context and unresolved pairs. Native/WASM and DOM
parity, invalid batch requests and rapid selection passed. Process inspection
confirmed the same runner and check 44's state-context child live.

Check 44 passed every state-context source join across all 12 sample dates,
including fixed observation dates and movie seek gaps/scopes, native/WASM/DOM
agreement, invalid requests and mobile layout. Check 45 is actively comparing
the NOAA samples. A direct SHA-256 comparison passed for all 39 files in the
engine manifest, including the shipped WASM, Rust sources, query bundle and
separate index artifacts. Research and frozen release files remain unchanged.

Check 45 passed all 12 NOAA dates × 56 state inventories against original
records, source addresses and projected centers, plus weekly center/contour
joins and native/WASM track paths. Invalid source identities were rejected,
and actual track navigation passed both reduced-motion preferences. The live
continuation has reached supporting-data check 46; map check 47 follows.

## Completed local browser coverage (2026-10-07)

Checks 46–47 passed, and runner session 74959 exited with code 0. Supporting
data preserved all 52 source decisions, 24 original display spans and both
diagnostic sets across 56 states, with native/WASM/DOM agreement, invalid
selection rejection, current navigation and mobile layout. The final map check
passed every original locator and its order, fronts, diagnostic paths and
operational polygons, native/WASM/DOM scene equality and layer toggles.

All 47 registered checks have now passed against engine SHA-256
`cbab9583c5e29f9bffb4641e629f06af998b4410dd463984da9d4ea04846f5f0`.
This is an aggregate local result: checks 1–24 passed in runner segments,
check 25 passed its focused rerun after an unreproduced return-navigation
timeout, and checks 26–47 passed in resumed segments after correcting the
NorKyst failure-case expectation. No product bytes changed during these
continuations. An uninterrupted full-run result and remote CI remain unverified.
The test corrections retain source comparisons and rejection assertions.

The KEEL local-validation condition is addressed with this explicit scope;
LOGBOOK's mainline publication condition remains open. This does not establish
scientific measurement completeness or a main-branch result.
