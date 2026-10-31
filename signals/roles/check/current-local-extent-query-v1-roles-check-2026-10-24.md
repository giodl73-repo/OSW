---
skill: roles-check
topic: current-local-extent-query-v1
date: 2026-10-24
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Scoped local extent Rust queries: internal source preparation review

Scope: new Rust store/CLI/WASM entry points, build-only cloud gate and parity
workflow. Internal installed lenses; no independent scientific reviewers or
subagents. This review permits preparation for one explicitly gated cloud
verification after the source freeze and held backup are complete. It does not
approve installation, public UI coverage or physical measurement admission.
ORBIT is excluded because no planetary analogy is present.

| Role | Finding | Severity | Resolution / condition |
|---|---|---|---|
| CURRENT | Model-local dimensions must not acquire whole-current meaning through a query API. | P2 | Separate collections and research metadata; physical width inventory increment remains0. |
| CURRENT | Seed points cannot define current containment or offshore boundaries. | P2 | Record inspection returns the original case context; physical state, geometry and seasonal joins rejected. |
| CURRENT | Seasonal query operators could imply a climatology. | P2 | Require explicit scalar year/month filters; reject seasonal selection and retain2013 monthly mean-field scope. |
| SOUNDER | Mutable input could silently change source meanings. | P2 | Exact835839-byte SHA256 gate before parsing; changed snapshots require reviewed versions. |
| SOUNDER | Null widths must remain distinct from zero. | P2 | Reuse established Rust numeric/null filter semantics; dedicated native and parity cases still require actual execution. |
| SOUNDER | Source cases and scalar outcomes need a resolvable relation. | P2 | Record API attaches original case via its case_id without manufacturing edge geometry. |
| CHART | A query result without actual map geometry should not imply a measured outline. | P2 | No new physical map scene; metadata links the reviewed bracket chart, and seed-position kind remains explicit. |
| CHART | Existing full-map projections must not be applied as current extent polygons. | P2 | Research API rejects geometry/state joins; future UI must retain the existing figure's quantity labels. |
| CHART | Partial profile/map review must remain visible. | P2 | Prepared dataset retains the separate12-map/four-profile review scope; no all-profile physical validation claim. |
| BEACON | Two small collections could be mistaken for the entire atlas. | P2 | Metadata exposes only72 cases/864 attempts, complete_atlas_loaded=false and a research dataset identifier. |
| BEACON | New entry points are not the same as delivered UI coverage. | P2 | Worker/UI wiring and compiled engine installation remain explicitly outstanding. |
| BEACON | Query filtering must not hide the original regional failures. | P2 | Original case statuses/gates and missing scalar rows remain queryable with explicit scope on every response. |
| HARBOR | A specialized view needs equivalent record access. | P2 | Generic paginated JSON and record-to-case inspection preserve textual evidence; UI tables still require delivery verification. |
| HARBOR | The new mode cannot leave unsupported physical controls active. | P2 | API rejects unsupported controls; future worker/UI integration must disable them before public coverage is claimed. |
| HARBOR | No browser interaction has been exercised. | P3 | Source-only preparation; browser automation deferred and no accessibility-completion claim. |
| KEEL | Rust syntax formatting cannot prove compilation or native/WASM equivalence. | P2 | Seven native tests and ten parity queries are written; actual execution remains required in the serial cloud case. |
| KEEL | Failed reloads could leave stale results in the research scope. | P2 | Clear local store before loading; cloud parity script checks failure invalidation and successful recovery. |
| KEEL | Resource controls must hold before toolchain installation and compilation. | P2 | Six tiny control tests passed; committed-source gate precedes compiler setup, with actual one-CPU affinity, one job/thread and shared concurrency. |
| LOGBOOK | Old executed source and installed corpus must remain unchanged. | P2 | Gate verifies83 input hashes plus committed bytes; only listed query/check source changes are allowed from the reviewed parent. |
| LOGBOOK | Build evidence must not imply installation or an enabled acquisition phase. | P2 | Separate build-only request, acquisition hold unchanged, installed-assets/admission flags false. |
| LOGBOOK | Repeated PRs would fragment the current-gap cohort. | P2 | Continue on the existing working branch; source-only backup preserves main and existing generated data. |

Roles reviewed:7. P1 blockers:0 for preparing one cloud verification.
P2 issues:20, addressed in source or retained as explicit verification/delivery
conditions. P3 notes:1. Verdict: APPROVED-WITH-CONDITIONS for source preparation.

Top finding: the small data path must preserve the same query semantics and
scientific scope while avoiding a full atlas load. SOUNDER, KEEL and LOGBOOK
agree that exact custody and actual native/WASM parity are required before
installation. No build/parity success is claimed by this source review.

## Three amendments

1. Reuse shared filtering/paging semantics through an isolated scoped store and
   expose only the two reviewed research collections.
2. Add stale-reload invalidation, null-versus-zero, missing-case and record/case
   tests with native/WASM parity on the small snapshot.
3. Freeze source and use a disabled build-only request with one sequential cloud
   job, preserving83 executed inputs and all installed data.
