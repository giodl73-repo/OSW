---
skill: roles-check
topic: eac-array-distance-readback
date: 2026-10-20
source_commit: 7a8d7dcedf3e0203c30110a011b8913c2d1bc879
roles_used: [CURRENT, SOUNDER, CHART, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# EAC fixed-array distance readback review

Internal functional review under `.roles/ROLE.md`; not external peer review.
Scope: the source-quality report's calculated WGS84 array distances and the
renewal of dependent checksums. Selected roles cover physical meaning, exact
provenance, map geometry, executable reconstruction and publication status.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | Array length could be mistaken for current length. | P2 resolved | Protocol explicitly limits these distances to fixed processing-grid geometry; admission remains false. |
| CURRENT | Readback must not alter span decisions. | P2 resolved | Core operator independently uses full precision; preservation comparison confirms all 3,770 profiles and 33,930 cases unchanged. |
| CURRENT | Precision is not physical uncertainty. | P2 resolved | Protocol defines millimetres as serialization only; annual physical range remains null. |
| SOUNDER | Linux mismatch needed an exact field diagnosis. | P2 resolved | Job119046629288 identifies 124 numeric leaves in three distance fields, no other differences; maximum 4.234607331454754e-9 m. |
| SOUNDER | Source coordinate bits must remain intact. | P2 resolved | Source profile and NPZ bytes exact against source commit; full source-quality comparison excludes only declared distances and renewed metadata. |
| SOUNDER | Protocol identity needs an executable pin. | P2 resolved | Source producer verifies protocol SHA before loading data; mutation test rejects changed protocol. |
| CHART | Map positions must not be rounded with calculated distances. | P2 resolved | All original longitude/latitude points are exact in the report and source profiles. |
| CHART | Figures must retain evidentiary class. | P3 confirmed | Source fields and core-span plots retain fixed-array and nonphysical-width labels. |
| CHART | Regeneration must not introduce unrelated visual changes. | P3 confirmed | All six existing EAC source/core/calendar SVG and PNG assets are byte-identical; figure manifests renew source bindings only. |
| KEEL | Float tolerance would conceal future scientific changes. | P2 resolved | Keep exact object and encoded-byte comparisons; narrow final-field round only. |
| KEEL | Local success cannot establish Linux reproducibility. | P2 condition | Push repaired report and inspect all seventeen independent Linux reconstruction targets before reporting that gate passed. |
| KEEL | Dependency hashes must follow the changed report. | P2 resolved | Renew source contract, core inputs, summaries, calendar source pin, figure manifests and generated query/engine bindings. Focused tests enforce them. |
| LOGBOOK | Full local gate belongs to its tested commit. | P2 resolved | Record 1,910 tests/1,222 subtests at774e466 separately; do not attribute it to this repair. |
| LOGBOOK | User requested one continuing PR. | P3 confirmed | Work remains on codex/current-measurement-gaps / draftPR83; no new PR or main merge. |
| LOGBOOK | CI acquisition failures differ from test failures. | P2 condition | Report paper-host403 separately from baseline and scientific reconstruction; do not waive either gate. |

Five roles; no remaining P1; two pending P2 gate conditions. Verdict:
APPROVED-WITH-CONDITIONS for continued draft work. Amendments implemented:
declare narrow distance precision, prove source/case/figure preservation,
and renew the full dependent checksum chain. Independent Linux reconstruction
and current-head integration results must remain explicitly scoped.
