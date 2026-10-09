---
skill: roles-check
topic: pacific-neuc-isopycnal-breadths
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Pacific NEUC component breadth review

Artifact: source extraction, scientific guards, native query comparison,
dashboard coverage and atlas/seasons/browser rendering. Source parent commit
`27e4579ff117f820837f56f886ed5fd04be87492` (draft PR78). This is an internal
functional review; independent scientific admission remains outstanding.
ORBIT is excluded because no planetary analogy is made.

## CURRENT — physical support

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 1 | The 3°/1° values describe two jets, not one jet's seasonal extremes. | P2 resolved | JATS Results / Mean Structures; two immutable measurement records. | Keep southern and northern components separate; width range and annual eligibility remain null/false. |
| 2 | A 27.0 σθ density surface is not a metre depth interval. | P2 resolved | Original Figures 1/2 and Methods; frozen scope flags. | Preserve variable-depth isopycnal support; reject fixed layers and 2000 m reference-level transfer. |
| 3 | Meridional breadth need not equal flow-normal width for tilting jets. | P2 resolved | Results describe southwest–northeast tilt; protocol rule 7. | Name meridional breadth explicitly and leave physical width edges and footprints unresolved. |

## SOUNDER — provenance and statistic roles

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 4 | Archive XML is the reviewed original text; a PDF review cannot be claimed. | P2 resolved | Complete JATS acquisition, reproduced SHA/89,353 bytes; access record. | Pin complete archived text and identify reviewed sections/figures without invented PDF pages. |
| 5 | Argo mean 2004–2014 differs from model/reanalysis 1969–2007 panels. | P2 resolved | Figure 1 caption and Methods; source_mean_years and diagnostic. | Preserve Argo absolute-geostrophic attribution; reject model-period and raw-observation promotion. |
| 6 | Article variability and significance contours do not provide width errors. | P2 resolved | Protocol rule 10; null uncertainty and false CI flags. | Omit width whiskers and seasonal playback; do not repurpose velocity SD/significance. |

## CHART — visual grammar

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 7 | Unit-normalization latitude bounds are not geographic width endpoints. | P2 resolved | Equatorial WGS84 conversion origin; source context flags. | Use an abstract common-axis comparison; no GIS buffers or width-derived state joins. |
| 8 | Published zero contours have not been digitized or adopted as width edges. | P2 resolved | Figure 1 caption versus source author's prose breadth; scope notes. | Label original contours as source velocity context; keep boundary rule unresolved. |
| 9 | A complete source figure contains six distinct diagnostic panels. | P2 resolved | Visually inspected unchanged Figure 1 and display caption. | Identify the top-left Argo panel and separate all model/reanalysis comparisons beside the image. |

## BEACON — clear source meaning

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 10 | Rounded kilometres can look more exact than approximate source degrees. | P2 resolved | Source degrees shown before ~330/~110 km; protocol round-to-10-km rule. | Retain degree labels and conversion explanation; never imply a measured 330 km endpoint pair. |
| 11 | A middle jet exists without a reported numeric breadth here. | P2 resolved | Middle_component null width with source core near 13° N. | Display unresolved middle breadth; no 2° interpolation. |
| 12 | Generic NEUC and Pacific NEUC identities are not interchangeable. | P2 resolved | Canonical ledger scope; source-specific frozen owner. | Attach only to the basin-specific owner and test transfer rejection. |

## HARBOR — equivalent access

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 13 | Narrow-screen scaling can make comparison labels unreadable. | P2 resolved | Fixed 1000 px chart in a local focusable scroll region; 320 px browser check. | Retain 16 px text, visible scroll cues and page reflow. |
| 14 | Source-image color cannot provide the only data meaning. | P3 | Source tables, degree/km text, explicit layer/period, image alt/caption. | Retain textual source breadths and caption without requiring palette interpretation. |
| 15 | Component selection is different from seasonal animation. | P2 resolved | Phase labels are jet components; null calendar, disabled playback and hidden generic bar. | Use selected component labels and static comparison; keep source links keyboard operable. |

## KEEL — reproducible validation

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 16 | Coherent receipt edits must not authorize rewritten scientific support. | P3 | Frozen audit/projection, early Rust guard and eleven planned shared native/WASM mutations. | Reject altered ranges, uncertainty, depths, calendar, owner, erased context, density, missing record and stripped proof. |
| 17 | Query sort must not alter the shared source-comparison scene. | P2 resolved | Browser scene equality exposed unsorted matching IDs; Rust now canonicalizes those IDs. | Exact query/atlas/seasons equality and reversed-order Rust regression pass after the final rebuild. |
| 18 | Source XML must retain its original bytes across Git platforms. | P2 resolved | Scoped `.gitattributes -text`; pinned article, acquisition, protocol and figure assets. | Preserve source response bytes and reject any changed dependency. |

## LOGBOOK — source rights and publication

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 19 | Source figures require explicit license and credit. | P3 | Article CC BY 4.0 permissions, source-figures receipt and visible caption/link. | Keep figure number, DOI, author attribution and unchanged-byte statement. |
| 20 | A scoped width gain cannot establish a complete atlas. | P2 retained limitation | 24 unassessed width owners, 89 length gaps, unresolved annual ranges/eddy footprints. | Keep the full goal active and report source/geometry/temporal gaps. |
| 21 | Hosted source failures coexist with a validating companion run. | P2 retained limitation | PR78 run 37945954828 terminal timeout; companion 37945964061 source/native/full-offline steps succeeded, WASM checks still live. | Separate local data validation from remote source transport and mainline admission; never call CI green without evidence. |

## Synthesis and amendments

Seven roles, 21 findings, no P1. Sixteen P2 findings are resolved, two P2
limitations remain and three P3 findings record confirmed strengths. The full
offline suite passes 1,264 tests / 923 subtests. Final 45 Rust tests and the new
eleven-guard browser check pass after scene-order normalization. Verdict remains
conditional on independent scientific admission and mainline publication.

Top finding: component differences on a density surface are not annual
dimensional margins. CURRENT, SOUNDER and CHART agree that depth, time,
orientation and boundary support must survive both source and map rendering.

Three amendments:

1. Preserve separate southern/northern components and null middle breadth;
   keep approximate source degrees before rounded kilometre conversions.
2. Close deterministic scene ordering and carry the same scientifically
   rejected mutation bytes through the real WASM loader.
3. Finish exact regression/publication receipts, source-image attribution and
   remote-state accounting while retaining overall atlas gaps.
