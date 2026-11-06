---
skill: roles-check
topic: caribbean-ru29-source-fields
date: 2026-10-23
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Caribbean RU29 source layer review

Artifact: licensed source custody, frozen complete readback, four-panel
visualization, lazy source inventory and numerical cell reader. Seven installed
lenses applied sequentially by the implementing agent; this is internal review,
not independent oceanographic validation. ORBIT is not relevant to this batch.

## Selected roles and findings

| Role / reason | Finding | Severity | Location and disposition |
|---|---|---|---|
| CURRENT / physical support | A section cannot establish complete current width when navigation missed its margins. | P3 | Protocols, page and report retain explicit incomplete width/depth coverage; no dimensional admission. |
| CURRENT | Multiweek occupations do not establish a seasonal envelope or instantaneous map. | P3 | Exact declared windows shown; no annual extrema or seasonal interpolation. |
| CURRENT | Source uncertainty cannot become an independent per-cell confidence interval or a whole-transport error. | P3 | Source facts/protocol/page retain contextual RMS only; no transport reproduction claim. |
| SOUNDER / custody | Initial metadata review missed nested virtual-state groups; v1 could not retain all selected files. | P2 | Resolved for this readback by frozen v2 recursion, retained v1 failure and independent complete original comparison. Future NetCDF feasibility must inspect groups. |
| SOUNDER | Selected-member checks do not verify the provider's whole ZIP checksum. | P3 | Custody/report/page/README distinguish CRC32/SHA256 checks from unverified archive MD5. |
| SOUNDER | Missing current units and incorrect contour-latitude units must not be silently repaired. | P3 | Exact original attributes retained; displayed current units attributed to paper/code separately. |
| CHART / visual grammar | Four component panels need identical signed scales and disclosed clipping. | P3 | Frozen shared ±0.5 m/s scale, zero-centred legend, missing grey, per-panel clipping counts and full source values retained. |
| CHART | Midpoint display edges must not look like measured current boundaries. | P3 | Declared display-edge rule; no current outline or width inference. |
| CHART | Narrow layouts must preserve readable chart access. | P3 | 320px internal scroll, visible full-size link, numerical cell alternative; actual screenshots reviewed. |
| BEACON / reader claims | A source inventory count could be mistaken for independent ocean observations. | P3 | Batch plan identifies original values/profile slots/interpolation; source page calls these retained fields. |
| BEACON | Paper and commented notebook have conflicting eddy filtering descriptions. | P2 | Resolved as an admission condition: disclose discrepancy and withhold pipeline-reproduction claim; scientific discrepancy itself remains open. |
| BEACON | Readers need a short visual-to-method/source path. | P3 | Page links paper, dataset, exact author commit, complete mirror, custody and frozen protocol. Canonical current-card integration is tracked as remaining delivery work. |
| HARBOR / equivalent access | Palette alone did not expose each displayed numerical velocity to keyboard/nonvisual readers. | P2 | Fixed with lazy complete occupation payload and labelled occupation/latitude/depth controls; numerical results include direction words and missing state. |
| HARBOR | Source search/loading and selected-cell changes require announcements. | P3 | Both status regions use role=status; source controls have associated labels; filtering and keyboard opening checked. |
| HARBOR | Wide chart/table must not widen the mobile page. | P3 | Actual 320px document-width assertion and internal scroll regions pass. |
| KEEL / platform and performance | Loading a 44 MB mirror by default would waste memory and bandwidth. | P3 | Page initially fetches only inventory and figure; 1.07 MB occupation payload loads on demand. No raw source or complete mirror fetched in browser check. |
| KEEL | Local native/build/browser overlap would violate the user's resource limit. | P3 | Each stage run sequentially, BelowNormal, one CPU, owned browser descendants monitored; no runtime rebuild started. |
| KEEL | Original reconstruction and UI delivery need separate, deterministic gates. | P3 | Independent actual-source tests, exact v2 replay, exact page payload check and focused browser check assigned separately in CI. |
| LOGBOOK / publication | A local source page is not a mainline or canonical Rust measurement admission. | P3 | Coverage row marked candidate source_inventory; batch plan keeps Rust/query/card integration open. |
| LOGBOOK | Frozen failures must survive later corrections. | P3 | v1 commit, protocol, tests, preflight and diagnostic retained; v2 imports unchanged shared functions. |
| LOGBOOK | Passing focused checks must not be presented as full goal completion or fresh remote CI. | P3 | Broad data gaps, fresh-head CI and full regression remain open in the batch plan. |

Roles reviewed: 7. P1 blockers: 0; P2 issues: 3; P3 notes: 18.
All three P2 admission conditions are addressed locally as above; the source
filter discrepancy remains a declared scientific limitation.

Verdict: **APPROVED-WITH-CONDITIONS** for the standalone source layer.
Top finding: preserve source support and nested state without promoting an
incomplete multiweek section into whole-current dimensions.
CURRENT, SOUNDER and CHART agree on this scope requirement.

Three amendments made: (1) preserve nested groups in a new frozen version;
(2) disclose unit/filter discrepancies and incomplete physical support;
(3) add a lazy, keyboard-accessible numerical cell reader. Canonical query/card
integration and fresh remote verification remain explicit next delivery steps.
