# South Java model context query preparation

This extends the existing current-gap working branch/PR83. It prepares five
source-qualified records and two provenance entries, without rebuilding or
loading the large atlas packet.

| Collection | Rows | Meaning |
|---|---:|---|
| `current_model_analysis_layers` |2 | Author-defined study bands, not measured thickness. |
| `current_model_depth_context` |3 | Approximate model core depths and a threshold-depth cap. |
| `sources` |2 | One publication and one internal protocol, not two independent datasets. |

All rows carry the related surface-current ID and exact source/figure references.
Only the surface-layer definition and two surface-depth records carry the
surface `entity_id`. The two SJCU rows have null entity ownership; they do not
admit a canonical undercurrent or assign its deeper core to the surface current.
Year support is the study analysis interval, not14 independent annual samples.
No observed velocity, width, physical thickness, uncertainty interval, seasonal
range, state footprint or ranked length is added.

`analysis/south_java_layer_query_v1.py` pins the reviewed facts and diagram and
prepares a deterministic contract. Its append function requires the existing
accepted South Java object/entity; it cannot add a missing identity. It checks
collections, prior owner/source references and counts, collisions, duplicate
application and publication DOI aliases before preparing small replacements.
The final mapping update occurs after validation. It does not clone the full
packet or rewrite other objects/physical records. Separate owner reference and
capability fields avoid changing width coverage. Existing paper DOI aliases
require explicit reconciliation rather than a second publication registration.

The contract uses JSON-typed comparison: numeric zero cannot replace a false
flag. A new source cannot silently repair a broken prior reference. The
15 focused offline tests passed in0.346s on one BelowNormal CPU. They cover
quantity/ownership promotion, source mutation, atomic refusal, prior-context
preservation, provenance and physical coverage preservation. The two new query
collection labels passed a Node syntax check. No local browser, native/WASM
build, provider request or velocity processing ran.

## Preparation versus delivery

The contract and examples are prepared; Rust execution of these queries,
actual packet append/export and browser delivery remain unverified. The
historical diagram manifest's query-preparation flags describe its earlier
generation stage. The new preparation review is the current status for query
records; the diagram/facts bytes remain unchanged.

Next include this adapter in one compatible current-data batch. Verify against
the delivered106-current packet in the cloud, including source-registry
reconciliation if needed, unchanged prior rows/counts and actual Rust queries
for both collections. Verify record/figure navigation and scope before marking
the new data installed. Preserve all83 scientific,23 runtime and20 verified
local-extent UI inputs. Full-atlas publication and main merge are not authorized
by this prepared contract alone. Continue other measurement gaps in the same
batch, without creating a PR per record.
