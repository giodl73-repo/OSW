---
skill: roles-check
topic: nordic-section-widths
date: 2026-10-14
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Nordic branch data and existing WSC comparisons: internal review

Base: 9edfb0574c9207e80ee48b6ef9cf0d6664e488aa. Seven repository lenses;
ORBIT is inapplicable. Internal review does not admit identities or measurements.

The initial implementation incorrectly attached source widths to ambiguous
canonical labels. Three existing tests rejected this. The implementation was
corrected: all 140 canonical-owner width records are retained byte for byte,
the existing six WSC rows are reused under `west-spitsbergen`, and the new
Gimsøy record belongs only to proposed identity `norwegian-atlantic-slope`.
The four older proposed branch records remain unchanged; a new query collection
exposes those four plus the new section result. No existing no-transfer test
was weakened or removed.

| Role | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| CURRENT | Norwegian Current is not an admitted alias for its Atlantic slope branch. | P1 resolved | New datum has only proposed_current_id; canonical inventory unchanged. |
| CURRENT | WSC widths already exist and cannot transfer to historical Spitsbergen Atlantic Current. | P1 resolved | Reuse exact six existing rows and their original audit; duplicate records/files removed. |
| CURRENT | WSC section C includes flow before inferred branch partitioning. | P2 | Existing source interpretation retained; alternate transport tube not pooled with threshold tube. |
| SOUNDER | Gimsøy range is characteristic, not four dated widths. | P2 | Four support dates retained, midpoint/annual extrema/per-date values unknown. |
| SOUNDER | Source brackets are operator choices, not width error. | P2 | Existing threshold cases drive dashed display envelopes; source width_range_km remains null. |
| SOUNDER | Nearby transport layers and assumed errors are separate quantities. | P2 | Gimsøy fixed layer and uncertainty null; 20.1 km transport width / 4 km error excluded. |
| CHART | The same source cannot be counted twice for a new graphic. | P1 resolved | New WSC scene reads the established records; no new canonical widths counted. |
| CHART | Filtering must preserve alternate operator context. | P2 | WSC scene retains six rows and marks matches; source-method definitions remain separate. |
| CHART | Independent figures need legible text and provenance. | P3 | Matplotlib SVGs visually checked; explicit units, source, date, definitions and unknowns. |
| BEACON | Proposed and canonical records must be visibly distinct. | P2 | Proposed branch collection, title/scope, candidate-card text and status make this explicit. |
| BEACON | Six WSC entries are three sections under two methods. | P2 | Caption and scope retain this; no new time samples added. |
| BEACON | Flux tolerance is not width error. | P2 | Existing 10% tolerance stays on approximately 1.3 Sv transport. |
| HARBOR | Meaning must survive color loss. | P2 | Primary circles, alternate squares, dashed sensitivity and numerical text supplied. |
| HARBOR | Inspectors require collection and ID. | P2 | Nordic/Antilles callback arguments fixed; tests require actual record headings and IDs. |
| HARBOR | Source and data access must work on mobile. | P3 | Owner-correct source/inspector/mobile and proposal-card navigation checks passed at 320 px. |
| KEEL | Existing no-transfer tests define a scientific invariant. | P1 resolved | Original Norwegian/WSC/dashboard checks retained and pass targeted verification. |
| KEEL | Proposed records need frozen bindings and independent source pins. | P2 | Python/Rust require five exact records, new candidate binding, original/protocol hashes, and no canonical transfer. |
| KEEL | Complete offline and UI publication gates are required. | P2 | Final run: 1,384 tests / 1,054 subtests passed in 1,279.26 s; all 44 collection and 100 current-card UI checks passed. |
| LOGBOOK | Data counts must reflect genuine additions. | P1 resolved | 140 canonical-owner records / 74 owners unchanged; five proposed query rows include one new datum and four existing rows. |
| LOGBOOK | Source copies require rights and attribution. | P2 | New Fer2020 original is CC BY4.0 with receipt; existing WSC original/audit reused. |
| LOGBOOK | One PR and accurate remote status are required. | P2 | Same draft PR83; prior remote fixture acquisition hit Hughes HTTP403, no pins relaxed. |

Amendments: restore correct identity ownership; remove duplicate source data;
separate proposed branch records; reuse existing WSC measurements for graphics;
fix inspector arguments and require successful record rendering.

Initial failed runs remain in ignored validation logs. A stale combined-chart
assertion was separately corrected to include the new WSC comparison scene;
it still requires the three older comparison kinds and all six WSC method rows.
Local publication gates passed: full suite above; 47 Rust tests; targeted
ownership checks 12 tests / 210 subtests; endpoint/monthly checks 5 tests /
13 subtests; eight native/WASM rejection cases; real Nordic/Antilles record
inspectors; proposed-card query navigation; all 44 collections; all 100 current
cards / 140 width records; staged-byte and whitespace checks.
Scientific admission and missing whole-current/annual widths,
exact section dates, geographic edges and numerical errors remain unresolved.

Provenance follow-up: adding the section datum and updating the proposal
curation date changed the proposal-document checksum. The endpoint-context
receipt and its two monthly dependencies were refreshed only after proving
equatorial proposal entries, numerical values, dates and all other bytes
unchanged. The five endpoint/monthly tests and 13 subtests pass; the final full
suite above passed against the refreshed artifacts.
