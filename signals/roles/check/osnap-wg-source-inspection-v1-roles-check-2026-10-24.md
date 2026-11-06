---
skill: roles-check
topic: osnap-wg-source-inspection-v1
date: 2026-10-24
source_commit: 0e4da2d5873967e7384b99ed7719d5f288d82d88
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 2
p2_count: 7
p3_count: 12
verdict: NEEDS-WORK
---

# OSNAP original custody and header inspection: functional review

This is one assistant's review through the repository's seven relevant
functional lenses, not independent reviewers or external scientific peer
review. ORBIT is excluded because no planetary comparison is proposed.

Artifacts: `analysis/inspect_osnap_wg_2016_2018_source_v1.py`, its synthetic
tests, the prospective inspection protocol, and the reviewed deployment
metadata/archive inventory. This review covers source custody and headers;
it does not approve current dimensions, observed samples, geometry or release.

The original archive has not been downloaded or inspected by this producer.
The source workflow and committed prospective preflight do not exist yet.
The command refuses original access until that preflight and its bound workflow
are committed and byte-verified. The active Davidson delivery remains separate.

## Role selection

CURRENT checks physical scope; SOUNDER checks exact field identity and custody;
CHART checks geographic claims; BEACON checks public interpretation; HARBOR
checks equivalent access; KEEL checks executable safeguards; LOGBOOK checks
truthful stage and release status. Each lens has three findings below.

## CURRENT

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Source headers are explicitly separated from physical measurements. | P3 | Producer result has zero derived dimensions/ranges and no materialized variable arrays. | Preserve these limits through any source-index projection. |
| 2 | Actual sample times, layer coverage, motion, missingness and velocity processing remain unassessed. | P2 | Only metadata/README and the ZIP directory have been reviewed; no original instrument header or samples inspected yet. | Complete a separate source-support review before choosing a width method. |
| 3 | The eight LS moorings are not presented as the full ten-mooring study array. | P3 | Source review and protocol distinguish the extra DSOW moorings. | Keep coastal, slope and deep-current identities and coverage separate. |

## SOUNDER

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 4 | Original archive/member hashes, reviewed directory fingerprint and ZIP CRC checks are explicit. | P3 | `digest`, `archive_directory_hash`, `checked_members`, and immutable custody/report writes. | Retain complete custody before interpreting headers or samples. |
| 5 | Review amendment now records acquisition times, request/response metadata, first execution commit, license link and deployment period. | P3 | `download_original`, `custody_record`; replay-provenance synthetic checks pass. | Preserve the first acquisition record during exact replay. |
| 6 | Actual variable IDs, units, accuracies, fill values and flags are still unknown. | P2 | README points to file attributes; original header inspection is pending. | Verify all selected original headers before claiming dataset interpretability or sample validity. |

## CHART

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 7 | No map geometry or state join is produced by this stage. | P3 | Result declares zero geometry/state joins; code only copies headers. | Do not turn array coverage or archive names into current edges. |
| 8 | The method does not substitute chart pixels, nominal depth names or a salinity front for velocity width. | P3 | No numerical field or coordinate reconstruction exists in the producer. | Keep future geometry conditional on reviewed coordinates and sample support. |
| 9 | A mapped observation layer still needs coordinate/datum, depth/time support and footprint checks. | P2 | Header collection alone does not interpret coordinate variable values. | Add those checks before rendering sample positions or current bands. |

## BEACON

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 10 | Status names and progress logs say HEADER, not measured current. | P3 | `PASS_SOURCE_HEADERS_ONLY` and `PASS instrument HEADER` labels. | Preserve the distinction in any public delivery summary. |
| 11 | Instrument files without `.nc` suffixes remain in the declared inventory. | P3 | Exact reviewed names; extensionless-member fixture passes. | Explain inventory selection by provider membership, not filename extension. |
| 12 | A future public page must distinguish custody, schema, sample support and measurement readiness. | P2 | This prepared stage has no public data-view integration. | Give each stage a separate label; do not light a measurement-complete indicator for header availability. |

## HARBOR

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 13 | Core evidence is available as structured text rather than color, pointer or animation. | P3 | JSON custody/header output and prose protocol. | Preserve a textual equivalent when a visual is added. |
| 14 | Keyboard, reflow, focus and accessible data-table behavior for a future header viewer remain unverified. | P2 | No viewer is proposed or exercised by this source-only producer. | Require an actual browser gate before public UI admission. |
| 15 | Reviewed README information has an explicit text/custody path. | P3 | Metadata review records both-page visual inspection and the exact README hash. | Link source and machine-readable metadata alongside later visuals. |

## KEEL

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 16 | The serialized cloud execution workflow is missing. Original execution is not ready. | P1 | No workflow is yet supplied for this prepared producer; preflight validation requires one. | Add and review a workflow that shares the one-heavy-job delivery concurrency group, with bounded resources and explicit source execution. |
| 17 | Twenty-one focused synthetic checks pass, including actual classic/HDF5 NetCDF headers with zero observation rows. | P3 | Test run at the reviewed source commit: 21 passed; no original archive access. | Run the same checks under the pinned cloud environment before originals. |
| 18 | Unsupported groups/types and metadata-budget failures deliberately stop inspection; actual format coverage is unproved. | P2 | Explicit rejection guards; original files remain uninspected. The zero-row fixture already caught and resolved a classic in-memory-reader portability defect using an exact-byte temporary copy. | Preserve original bytes; if originals require unsupported handling after this version executes, create a reviewed new version instead of silently dropping fields or editing executed science. |

## LOGBOOK

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 19 | The committed prospective preflight is missing. Original execution remains blocked by its guard. | P1 | Required preflight path is absent; `verify_preflight` checks committed input bytes before networking. | Bind producer, tests, protocol, this review, source records, requirements and execution workflow; commit the freeze before any original case. |
| 20 | Deployment license and DOI are kept distinct from the earlier deployment's CC0 metadata. No original archive is committed to Git. | P3 | Pinned metadata review and custody fields; original archive remains undownloaded. | Carry attribution with any later cloud source artifact and keep source licensing separate from repository licensing. |
| 21 | The complete archive hash and original-header receipt are still absent. | P2 | Only a bounded directory suffix and README are currently retained; whole-archive SHA-256 is null. | Produce and inspect the guarded cloud custody/header artifacts before closing this source stage. |

## Synthesis

Roles reviewed: 7. P1 blockers: 2. P2 issues: 7. P3 notes: 12.

**Verdict: NEEDS-WORK for original-data execution.** Preparation and synthetic
tests are complete enough to review; actual original access is not approved by
this record. The top finding is the missing committed execution workflow and
prospective freeze. KEEL and LOGBOOK agree on that gate; CURRENT and SOUNDER
agree that header availability cannot establish physical sample support.

The `roles-check` skill and repository review protocol require a NEEDS-WORK
verdict when P1 gates remain. No user approval is requested: the missing work
is concrete repository preparation, followed by the already required sequential
cloud validation. The active goal and existing cloud run continue.

## Three amendments / next gates

1. Add the source-inspection cloud workflow after the active delivery queue,
   with one CPU, bounded memory/disk/downloads, exact artifact custody and no
   automatic working-data publication.
2. Commit the prospective preflight binding the complete source/review/workflow
   bytes before original access. Retain this review; close its findings with a
   new receipt rather than retroactively substituting a passing verdict.
3. Inspect actual source headers/custody and then plan a separately reviewed
   sample-support, measurement and accessible-view stage. Do not admit a width,
   annual range, current edge or state intersection from this metadata producer.

Original archive execution: **not performed**. Measurements admitted: **0**.
Working dataset changed by this stage: **no**. Scientific release: **no**.
