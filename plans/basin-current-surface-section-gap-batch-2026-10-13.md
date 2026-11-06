# Basin current local surface-section diagnostics

2026-10-13. Continuing branch `codex/current-measurement-gaps`, draft PR #83.
Previous goal turn was progress: commit 6a37ded added six regional reference
reaches. This batch adds measured local model-component spans and their source
profiles, queries and visuals for three previously unassessed width owners.
Current association, flow-normal width and whole-current dimensions remain unresolved.

## Data and calculation

Exact archived NOAA PIFSC / Earth & Space Research OSCAR 2017.0 responses:
three vector sections, 13,608 native positions, both u and v retained. Portugal
has 288 missing vector pairs; no missing interval is bridged. Metadata allows
free use and redistribution; original provider CSV/metadata bytes are retained
with acquisition URLs, UTC time, byte counts and SHA256, protected from text
normalization in Git. These are satellite-derived near-surface vectors with a
nominal 15 m coordinate, not direct instruments or depth-resolved flow.

The queries requested January 1–December 28, 2013. The original archive returns
72 records January 1–December 26, including four six-day gaps. Initial parser
assumptions of 73 uniform five-day records were rejected and corrected against
the actual archive before source admission. No source times, query bounds,
peak search windows or threshold choices were changed to improve the outcome.

| Current context / fixed section | Local monthly nominal span values | Resolution review flags |
| --- | --- | --- |
| Portugal / 40 N, southward component | about 70–190 km | 10 of 12 months |
| South Atlantic / 30 W, eastward component | about 110–330 km | 8 of 12 months |
| South Pacific / 100 W, eastward component | about 90–200 km | 10 of 12 months |

These spans of twelve local monthly-mean values are neither whole-current
widths, annual physical extrema, climatology nor uncertainty intervals. Peak
locations can jump between bands. The December South Pacific peak is at the
search-window edge. All 36 samples retain `current_association_verified: false`.
Spans narrower than four native grid spacings are flagged; wider spans still
require boundary, effective-resolution and model-error review.

The pinned protocol/input defines paired-vector monthly averaging, minimum
five samples per cell, 0.02 m/s diagnostic peak eligibility, connected half-peak
boundaries and 0.4/0.5/0.6 sensitivity scenarios. All 108 threshold scenarios,
profiles, contributing actual timestamps, boundary brackets and missing-data
outcomes are retained. Distances are shortest WGS84 boundary separation,
reported to 10 km. Fixed-orientation component spans are not flow-normal widths.

## Store and presentation

Three diagnostic documents and 36 source-bound samples join the existing
`diagnostics` and `width_samples` collections. The 42-collection native/WASM
store supplies monthly charts and local section marks before table pagination.
Monthly controls highlight readings; no interpolation, tracked current axis,
annual footprint, route buffer or NASA current identification is implied.
Inspectors show source/protocol links, current-association and resolution flags,
threshold sensitivity and exact parent diagnostics. Three SVG profile sheets
have live text, title/description and twelve panels each. Current dashboard
entries link to the queries and profile sheets.

Frozen Rust source receipts reject altered reports even if source JSON, sample
projections and supplied checksums are rebound consistently. Existing sample
binding rejects value, owner, month, metric, uncertainty and resolution changes.
The scientific claim remains a local component diagnostic pending review.

## Counts and invariants

Width assessments: 18 not assessed (previously 21); four owners have section
spans while width remains unresolved (previously Loop alone). The 131 published
scoped records / 70 owners, two earlier derived-width candidates, six reviewed
nonnumeric decisions and all prior measurement records remain unchanged.

Exactly Portugal, South Atlantic and South Pacific dashboard fingerprints
change. Portugal's existing 2009-11-11 observation date is preserved; the other
two remain null. Archival product timestamps do not become observation dates.
Canonical current inventory, published length evidence, all 73 reference routes
and their ordering are byte-identical. Seasonal route data changes only its
reviewed width-inventory dependency receipt, with every frame unchanged.

Lossless JSON source corpus: 198 documents. Canonical scientific-release rows
remain unchanged. Licensed raw CSVs are separately retained; corpus documents
include their complete parsed vectors and source receipts.

## Verification

- 46 Rust tests and serialized locked native/WASM builds passed.
- Focused numerical/source/inventory checks: 40 tests and 544 subtests passed.
- New browser: all three monthly charts and twelve mapped spans before
  pagination; keyboard selection, manual monthly controls, inspector/source
  links, 320 px reflow and native/WASM parity passed. Five native and three
  WASM rejection cases include consistently rebound source forgery.
- Source-index page checks passed; full exact-corpus, legacy sample and complete
  offline gates are recorded on completion.

Both prior-head GitHub runs failed at institutional paper acquisition before
validation tests. Exact local original fixtures remain available. No paper
edition/pin was substituted to make those remote downloads pass. New-head CI
is reported separately from local gates.

Reproduce: verify/acquire source sections explicitly; build section inventory,
three diagnostic reports and profile sheets; refresh their worklist receipts
and the seasonal dependency hash; regenerate dashboard, source index and query
bundle; serialize the Rust build; then run the default offline suite and
registered browser checks. No executable rebuild while tests use the engine.

## Final publication gate receipt

**1,326 tests and 931 subtests passed in 1146.29 seconds (19m06s).** Final browser passed three current contexts, 36 monthly samples, source/parent inspection, keyboard/monthly controls, pagination-independent chart/map scenes, 320px reflow, five native and three WASM rejection cases. Legacy sample browser passed all 127 earlier samples and five missing readings. Index store browser passed 198 exact documents, 12 seasonal snapshots, independent NOAA oracle, native/WASM parity and checked-input failures; index page checks also passed. All 61 engine pins and 198 source-file pins verified; three profile sheets and representative UI captures visually reviewed. Editorial publication conditions are satisfied; named-current association and physical width/annual-range admission remain unresolved.
