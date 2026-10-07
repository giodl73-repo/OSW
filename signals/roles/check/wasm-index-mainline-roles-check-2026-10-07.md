---
skill: roles-check
topic: wasm-index-mainline
date: 2026-10-07
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 3
p2_remaining: 0
p3_count: 18
verdict: APPROVED-WITH-CONDITIONS
---

# Rust/WASM index migration review

Base commit: `52646dc55f34f2c0df94d548aa2501964b4bad38`.
Reviewed artifact: uncommitted local candidate on `codex/wasm-mainline-dashboard`,
including `index_store.rs`, `index_noaa.rs`, `index_support.rs`, `index_map.rs`,
checked worker/client, explicit source registry, builders and migrated index UI.
The current engine is 1,688,773 bytes; its exact hashes are recorded in
`almanac/query-engine.manifest.json`. This review is of the working tree, not
the base commit alone, and must be updated when its identified fixes land.

Seven installed role definitions were read. CURRENT covers scientific claim
scope, SOUNDER provenance, CHART geometry, BEACON public reading, HARBOR access,
KEEL executable validation and LOGBOOK release status. ORBIT is excluded because
this candidate introduces no planetary comparison. These are internal role
lenses, not independent scientific peer review.

## CURRENT

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | NOAA IDs remain file-scoped; invalid cross-file IDs and unsupported focus dates are rejected. | P3 | `index_noaa.rs`; focused NOAA browser check | Retain those rejection cases and the identity limit beside tracks. |
| 2 | Daily contour contacts, weekly centers and weekly contours are distinct records. Missing contours are not evidence of absence. | P3 | NOAA state/track views and original source records | Preserve relation types rather than reducing them to one membership boolean. |
| 3 | Ranked illustrated spans remain display metrics, with separate published lengths. | P3 | support view; 24 source comparisons | Do not promote arrow geometry to whole-current length or seasonal ranges. |

## SOUNDER

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The 63-source registry no longer depends on browser loader text. Exact original source strings and hashes remain pinned. | P3 | registry, builder, compiled catalog and load validation | Add new dependencies explicitly and rebuild the catalog before the engine. |
| 2 | Fixed 2026 observations retain their dates when 2021–2023 NOAA samples are selected. | P3 | state-context source comparison across 12 dates | Continue distinguishing observation time from picker time. |
| 3 | Crop/model-date context retains source records and explicit identity limits. | P3 | NOAA crop and track APIs; focused source oracle | Keep approximate seek and individual identity claims separate. |

## CHART

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Shared Rust projection preserves the source coordinates and map offsets. | P3 | every locator/source geometry comparison in map check | Keep geographic calculations outside pixel coordinates. |
| 2 | Track seams break into separate subpaths; singleton tracks remain renderable. | P3 | shortest/longest/seam examples in NOAA check | Retain seam and sparse-track cases in the gate. |
| 3 | Overlapping named-eddy locators are not shifted to suggest different observed positions. Keyboard navigation remains available. | P3 | prior Batumi/Sukhumi finding; marker focus attributes | Improve selection at crowded locations through interaction, preserving coordinates. |

## BEACON

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Locator titles distinguish editorial, sample-site and observed-center evidence. | P3 | Rust map scene and DOM equality check | Retain these descriptions when redesigning the map. |
| 2 | Current links clear filters before revealing the destination row. | P3 | current navigation helper and support check | Reuse this behavior for new internal links. |
| 3 | Unavailable diagnostic queries explicitly avoid claiming current absence. | P3 | diagnostic helper error message | Preserve this wording in future error states. |

## HARBOR

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Weekly-track navigation requests smooth scrolling unconditionally. | P2 | `app.js` track handler, `scrollIntoView({behavior: "smooth"...})` | Check `prefers-reduced-motion` and use instant scrolling when requested; verify actual track navigation in both modes. |
| 2 | All locator markers are keyboard-focusable and have descriptive labels and visible focus styles. | P3 | Rust scene renderer; `styles.css` focus rules | Preserve the redundant textual tables and marker descriptions. |
| 3 | State and track results have polite live regions; focused 320 px checks pass. | P3 | index markup and focused checks | Extend assistive-technology testing without claiming a full accessibility audit. |

## KEEL

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The latest complete 47-script browser gate is still running. | P2 | live runner; first six checks passed, taxonomy active at review | Finish the gate, resolve failures and document the exact candidate tested before publication. |
| 2 | Offline tests passed: 767 tests/581 subtests, 513 standard-library tests and both NetCDF fixtures. | P3 | completed local command results | Retain the workflow's pinned dependency and Rust versions; remote CI remains separate evidence. |
| 3 | Typed source oracles cover source order, records, projection, joins, invalid requests and native/WASM/DOM agreement. | P3 | focused index checks | Keep those checks in the required runner when adding collections or views. |

## LOGBOOK

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | This large candidate is not on main and has no completed remote CI result. | P2 | local Git state; main at base commit | Prepare the concrete reviewed candidate and preserve the local/published distinction until it lands. |
| 2 | No research or frozen release files changed during migration. | P3 | `git diff --name-only -- research almanac/release` | Preserve immutable source and historical release boundaries. |
| 3 | UI migration does not supply the still-missing scientific lengths, widths or seasonal coverage. | P3 | source inventory and coverage plan | Track scientific admission separately from implementation coverage. |

## Synthesis and amendments

Roles reviewed: 7. P1 blockers: 0. P2 issues: 3. P3 findings: 18.

Verdict: **APPROVED-WITH-CONDITIONS** for continued local integration;
publication readiness is not established.

Top actionable code finding: honor reduced motion for weekly-track navigation.
KEEL and LOGBOOK agree that focused local success cannot establish main-branch
coverage or completed publication.

1. Fix reduced-motion scrolling and verify the actual track button flow.
2. Finish the live browser gate, fix failures and record the candidate's evidence.
3. Prepare the reviewed changes for publication with truthful release status and
   the remaining scientific measurement work visible.

## Amendment verification

The HARBOR P2 scrolling finding is addressed. The track handler now checks
`prefers-reduced-motion`, and the actual button-flow test passed both instant
(reduce) and smooth (no-preference) modes while verifying the returned source
path. The complete 12-date/56-state NOAA source comparison also passed again.
The route-state gate failure was an assertion before asynchronous readiness;
its corrected focused check passed all 124 original route/state links and
fallbacks. No source assertion was removed.

Two P2 conditions remain: the complete updated-engine browser gate and
truthful publication status. The interrupted gate passed its first 18 checks
on the previous receipt; it is not a complete result for this amended candidate.
A new complete gate is required and is being started.

## Completed local validation amendment

All 47 registered browser checks passed against the same amended engine
SHA-256 `cbab9583c5e29f9bffb4641e629f06af998b4410dd463984da9d4ea04846f5f0`.
The final continuation exited with code 0. The result spans sequential resumed
segments plus the focused observed-section check: its earlier return-navigation
timeout did not reproduce, and its cause remains unconfirmed. Test corrections
addressed asynchronous state readiness, declared collection counts and earlier
required-source rejection; original source equality assertions remain.
This is not an uninterrupted full-run result or remote CI evidence.

The KEEL local-validation P2 is addressed. All 39 files in the engine manifest
match their SHA-256 receipts; research and frozen release files are unchanged.
The LOGBOOK publication P2 remains open: these changes are still local, and
protected-main coverage requires the candidate to land with remote CI passing.
The verdict remains APPROVED-WITH-CONDITIONS, with one P2 remaining.

## Mainline publication verification

PR #23 merged at `4bcd621be2ae51598c196660ffcb31062cf1b732` after the strict
required `offline` and `netcdf-fixture` checks passed. The PR CI run
https://github.com/giodl73-repo/OSW/actions/runs/37633512614 completed all 47
registered browser checks in their exact order without interruption, plus
767 offline tests, 513 standard-library tests, 36 Rust unit tests, syntax and
page-assignment checks. The independent push CI run also passed.

The merged main tree exactly equals tested candidate `e86649b`, verified by
`git diff --exit-code e86649ba494e6ea93dd3ed056a43eb7f762668f6 4bcd621be2ae51598c196660ffcb31062cf1b732`.
The earlier observed-section timeout did not recur in the full remote gate;
its original cause remains unconfirmed. The LOGBOOK publication P2 is closed.
All three original P2 findings are addressed; the historical review findings
and verdict above are retained with these amendments. This closes the migration
review conditions, not the remaining scientific measurement or source-use work.
The separate post-merge main CI run remains distinct from the completed
candidate CI evidence.
