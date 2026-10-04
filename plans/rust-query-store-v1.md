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
