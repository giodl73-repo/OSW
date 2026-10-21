---
skill: roles-check
topic: kuroshio-query-atlas
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Regional model data/query/map integration review

Base:b2b6556d2f2994edd043b038e048d71e5983b0fe. Seven internal functional lenses
review the data contract, native/WASM projection, dashboard and current map UI.
CURRENT checks physical meaning; SOUNDER source custody; CHART geography;
BEACON claims; HARBOR access; KEEL deterministic gates; LOGBOOK publication.
ORBIT is not selected: no planetary analogy or atlas release. This review is
not external scientific approval. Final terminal publication evidence is
required below; no main merge follows this draft-branch verdict.

| Role | Finding and evidence | Severity | Recommendation / resolution |
|---|---|---|---|
| CURRENT | Partial18–30N axis lengths cannot enter whole-current ranking. | P2 resolved | Separate collection/quantity and nonranking flags;12 source-reported ranks unchanged. |
| CURRENT | Oblique fixed-latitude spans are not flow-normal current widths. | P2 resolved | Explicit section quantity, source scope and table labels;157 scoped-width records unchanged. |
| CURRENT | Search fallback and numerical uncertainty are unknown. | P2 resolved | Null occurrence/error fields, source caveat and sample-range denominators; no confidence/annual physical extrema. |
| SOUNDER | Source edition, licensed original and raw source query must agree. | P2 resolved | Version1 DOI/CC BY4.0, retained exact gzip/original hashes, source record and exact source-document binding. |
| SOUNDER | Missing/ambiguous cases cannot disappear in UI packaging. | P2 resolved | All6588 attempts, explicit reasons and null values; exact Python/Rust projection. |
| SOUNDER | A UI status embedded in scientific data becomes stale. | P3 | Remove old flag, renew producer hash only; preserve numerical cases/frames/statistics/source and use integration edition. |
| CHART | Rendered source geometry must preserve missing vertices. | P2 resolved | Rust paths break at nulls; no line buffer, polygon or observed-state inference. |
| CHART | Dated curves could persist after selecting another current. | P2 resolved | Dedicated model overlay cleared on selection; selected date/depth labels and regression gate. |
| CHART | Partial model card is not a newly admitted reference path. | P3 | Separate card class/count and fixed regional display extent;77 reference rows/order retained. |
| BEACON | Stored attempts can be mistaken for verified measurements. | P2 resolved | Regional model-attempts metric, resolved counts and source/unknowns visible; no canonical count inflation. |
| BEACON | First-of-month maps are not monthly means. | P3 | Dated snapshot labels, no interpolation/autoplay; daily attempts separately queryable. |
| BEACON | Sample spread differs from uncertainty. | P3 |2024 range/counts labeled; null uncertainty fields and explicit source sampling/smoothing limits. |
| HARBOR | Dark OSW context obscured initial dark strokes. | P2 resolved | High-contrast cream/pink/mint plus solid/dashed/dotted styles; final desktop/phone visual gate. |
| HARBOR | Motion and shared navigation need equivalent manual access. | P2 resolved | Keyboard controls, date/depth sharing,44px targets, reduced-motion disable/stop, map/card/return gate. |
| HARBOR | Narrow tables must not widen the page. | P3 | Stacked responsive grid and labeled scroll region;320px reflow gate with textual values/counts. |
| KEEL | Native/WASM cases and provenance can diverge. | P2 resolved | Exact6588-row/source/owner contracts, checksum pins, deliberate field/case/source/license/edition rejection. |
| KEEL | Complete new-head suite and independent reconstruction remain separate. | P2 open before merge | Focused22/97 and browser gates do not replace them; report22-target CI separately; retain last full baseline and403 fixture failure. |
| KEEL | Existing packets and other owners require preservation evidence. | P3 |45 collections,240 objects, phase plans/raw documents/release checked; older packet loads. |
| LOGBOOK | One continuing PR is the authorized publication workflow. | P2 resolved | Existing branch/PR83, no new PR or main merge; full objective stays active. |
| LOGBOOK | A near-limit packet cannot support unrestricted source growth. | P3 | Full-case size gate; partition storage before further large years/levels, never prune to fit. |
| LOGBOOK | Ordinal IDs would renumber records when adding source levels/years. | P2 resolved | Source edition/date/depth/section/method IDs, native-provided UI links and insertion/reorder regression. |
| LOGBOOK | Source/core coverage must remain explicit. | P3 |31 years/27 levels remain;89 unranked names/18 missing scoped-width owners,30 missing reference cards remain visible. |

Roles reviewed:7. P1 blockers:0. P2 findings:14 (13 resolved,1 open before
merge). P3 notes:8. Verdict: APPROVED-WITH-CONDITIONS for draft publication
after final focused/browser/visual/preservation/pin gates.

Top finding: regional model samples provide useful dated evidence without
establishing whole-current dimensions or physical annual bounds. CURRENT,
SOUNDER and BEACON agree. Three amendments: preserve unknown/censored scope in
typed records; expose source/missing-case counts and manual access in every
entry point; bind the complete projection and preserve old data before pushing.


## Final local publication evidence

- 22 focused Python tests pass, including the full scientific source rebuild,
  exact6588-case projection, preserved numerical data and explicit unknowns.
- 97 Rust tests pass; native/WASM builds and native atlas validation pass.
- New end-to-end browser passes exact native/WASM data,36 dated frames,
  date/depth controls/sharing, reduced-motion stop/disable, keyboard map-card
  return, overlay update/cleanup, seasonal page, exact source query,320px and
  dashboard one-owner coverage/native selection parity. No page errors.
- Existing general query regression passes. Snapshot regression passes106 exact
  atlas documents,eighteen loader rejections,native/WASM parity,101 current and
 140 eddy-record selectors,77 reference cards,mobile/optional/unavailable data.
- Final contrast/layout/link fixes rendered and visually inspected at1360x1100
  and320x1000.66 JavaScript files pass syntax;14 pages have validation
  assignments. This is not a complete14-page browser-suite claim.
- Preservation passes:45 collections,240 other objects,21 prior reports, all101
  phase plans and four raw seasonal documents exact. Kuroshio's complete
  numerical cases/frames/statistics/source/scope stay exact; only the old UI
  flag and producer checksum change. Prior bundle readable; historical release
  untouched.31 measurement rows,157 widths,463 samples,2853 old section cases.
- Final packet102819992 bytes;2037608 bytes remain below100MiB. All6588 attempts
  retained. Subsequent large datasets require partitioned storage.

The complete new-head default suite and independent22-report result remain
separate gates before merge. See recordedb2b6556 successes and403 fixture failure;
do not substitute old/focused results for those current-head gates.

Build recovery evidence: disk-full interruption retained as failure; two code
files recovered from staged copies and identity changes reapplied. Only the
verified inactive Rust incremental cache was removed; source originals retained.
Build defaults now avoid incremental cache growth and check free space before
formatting. Recovered97-test/native/WASM/atlas gate passes.

Stable-ID final checks:22 focused Python tests pass, including insertion/reorder
identity stability. The final native/WASM browser also opens the exact Rust-
provided sample ID from its table. Recovered build/source-preservation gates
pass; original130603298-byte provider file SHA256 remains unchanged.

Final navigation gate passes: model map/card controls stay synchronized and
return navigation preserves both selected date and source depth. Exact sample
inspection uses the persistent Rust-provided identity. Final22 Python/97 Rust,
source-preservation, general query,106-document/eighteen-rejection snapshot,
source/dashboard/season/phone/reduced-motion gates pass.

Publication pin gate:940 staged source/input/artifact paths match their declared
bytes, including the complete source graph, original archive and final UI.
Whitespace check passes. This evidence footer is separately rechecked against
its staged bytes; it changes no source, data, executable or dependency pin.
