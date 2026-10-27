# Azores dated section provenance and visualization

Status: source implementation prepared; native/WASM/browser delivery unverified.

The original Comas-Rodriguez et al. (2011) PDF has now been inspected. Retain
the two existing 110 km section measurements and their dates, geometry, methods,
and identity. Expose verified station boundaries and the independent section
diagram in the atlas current card, selected width page, and structured width
query. No route, physical footprint, representative width, annual range, or
new measurement is admitted.

The source caption prints 2010 while the methods specify 2009. Show that conflict;
do not resolve it through an editorial correction. Separate ADCP averages and
transport-layer support do not define a fixed layer for these widths. Preserve
the Azores Current's existing seasonal model-core records as a separate metric.

## Prepared source implementation

- `analysis/azores_2009_section_projection_v1.py` verifies the two exact rows,
  adds only source-pinned manifest metadata, and extends the existing source index
  without replacing historical source strings.
- `rust/osw-query/src/azores_section_review.rs` requires an exact activation and
  source binding. It rejects changed or duplicate section rows and emits a shared
  scene for width queries and the atlas/seasons snapshots.
- `almanac/azores-2009-section.js` renders that scene and links to the selected
  width record and exact indexed source row. It is wired to the three UI surfaces.
- The runtime diagram derives from the visually reviewed source diagram, with
  the preparation-status footer replaced by a scientific scope note.
- `analysis/azores_2009_section_engine_v1.py` prepares the matching compiler
  inventory and engine overlay. Nine exact installed source versions are
  archived under `research/azores-2009-section-runtime-history-v1/`; inherited
  historical bindings remain separately verified. These source-fixture checks
  are not a full live 1194-file custody audit.
- `analysis/azores_2009_section_cases_v1.py` retains twenty previous query cases
  and adds six section cases, including both owners, record IDs, sorting and
  pagination. Twelve complete source-document queries are declared. Execution
  against native/WASM engines is still pending.
- Source-index compression and receipt updates are implemented and tested with
  a tiny fixture. No installed packet or index was loaded locally.

## Verification completed locally

Small Python source fixtures check lossless preparation, unchanged measurements,
source-index preservation, and refusal of altered identities, values, layer,
dates, geometry, ranking, source pins and duplicates. DOM checks exercise owner
selection, record links, original-source pointers and inspect callbacks. These
checks do not establish native/WASM execution or real browser behavior.

## Required delivery work

1. Use installed logical parent
   `233c156bf1e044e7378d5bb739633da59eadb28125d40fc3254dd503e2bc1a32`.
   Retain exact prior compiled sources and manifest provenance for the delivery
   compatibility audit. Local generated preview remains unsynchronized.
2. Assemble the full cloud delivery orchestrator, source-index receipt update,
   source binding inventory and disabled execution request. Do not treat the
   prepared source projection as a completed runtime artifact.
3. Verify all original measurement collections, object identities, owner links,
   routes, width counts and historical source-index strings are unchanged.
4. Execute native tests, whole-response native/WASM width-query parity and full
   atlas/seasons snapshot parity in one cloud job after a scoped delivery phase
   is established. The current source-review-only phase permits no heavy work.
5. Inspect actual desktop and narrow-screen browser results for both currents,
   individual and mixed width queries, exact source-row navigation, dated width
   selection and current-card navigation. Check visible date conflict and absent
   annual playback; compare the separate existing model-core evidence.
6. Install the exact verified artifact on the existing working branch and update
   its coverage checkpoint. No main merge, local binary build, or local bulk sync.

Whole-current length, width uncertainty, repeated seasonal observations, and
the wider catalogue's remaining measurement gaps stay open after this delivery.
