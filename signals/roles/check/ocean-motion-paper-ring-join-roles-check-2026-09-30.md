---
skill: roles-check
topic: ocean-motion-paper-ring-join
date: 2026-09-30
depth: quick
roles_used: 6
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: paper-sourced Loop Current rings

Artifact: `research/named-loop-eddy-published-observations.json`, the unified eddy inventory, the full and screened data packages, and the screened review atlas. Selected CURRENT for eddy identity, SOUNDER for provenance, CHART for state geometry, HARBOR for access, KEEL for package checks, and LOGBOOK for release status.

| Role | Finding | Severity | Evidence / recommendation |
| --- | --- | --- | --- |
| CURRENT | Paper observation windows are not separation dates or full lifetimes. | P2 | Retained only as `observation_start`/`observation_end`; keep the distinction beside each record. |
| CURRENT | The paper and Horizon rows may refer to the same physical rings, but the source graph has no verified event identity join. | P2 | Keep distinct source IDs and label the Horizon crosswalk as possible only. |
| SOUNDER | Each paper record needs its own citation and locator, independent of the Horizon source row. | P2 | Verify three entity `source_id` values and three observation claim sources resolve to the articles. |
| SOUNDER | Figure contours are described but no coordinate boundaries or method have been extracted. | P2 | Keep state relations unresolved until a dated, reviewable geometry is available. |
| CHART | An instrument-array box or Gulf regional phrase would look like an eddy footprint if drawn as such. | P2 | Keep paper records without map points or polygons; the atlas labels no physical containment. |
| CHART | NASA class context can be mistaken for a NASA identification of a named ring. | P3 | Preserve the generic class relation and no individual movie identity claim. |
| HARBOR | The screened directory and record detail need a keyboard and text route to the paper evidence. | P2 | Screened browser checks cover directory, deep links, source links, and record text. |
| HARBOR | Source-scoped duplicate names can confuse search results. | P3 | Keep the source-record count and paper/Horizon distinction in the full atlas introduction; human review remains pending. |
| KEEL | Rebuilt package manifests must pin the changed inventory, code, and documentation. | P2 | Run release, preview, site validators after the final rebuild. |
| KEEL | A future accidental Horizon dependency could silently remove the three records. | P2 | The preview validator now requires all three paper entities and observation claims and rejects Horizon URLs. |
| LOGBOOK | The full candidate still uses 17 rights-pending external sources. | P1 | Keep the public release gate closed; this narrow paper-source correction does not clear the full candidate. |
| LOGBOOK | Counts now refer to 134 source records, not 134 unique eddies. | P2 | Keep this distinction in release and preview documentation and avoid unique-ring claims. |

Roles reviewed: 6. P1: 1; P2: 9; P3: 2. Verdict: **NEEDS-WORK for public release; acceptable for the internal screened review atlas after validators pass.** The strongest shared finding from CURRENT, SOUNDER, and CHART is that dated paper observations do not establish a closed state footprint.

Amendments made: paper-only IDs and observation claims; no state points for these records; independent paper citations in screened record details; source-record wording and validator assertions. Remaining: acquire and review dated contours, resolve the broader source-use gate, and conduct human accessibility and scientific review before publication.
