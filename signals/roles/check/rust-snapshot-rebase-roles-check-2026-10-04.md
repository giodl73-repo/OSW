---
skill: roles-check
topic: rust-snapshot-rebase
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 5
p2_remaining: 0
p3_count: 16
verdict: APPROVED-WITH-CONDITIONS
---

# Source snapshot rebase review

Artifacts: Rust three-way comparison, v2 journals, worker snapshot persistence,
conflict controls, native CLI and browser/native verification. CURRENT covers
scientific scope; SOUNDER provenance; CHART geometry; BEACON status; HARBOR access;
KEEL correctness/concurrency; LOGBOOK operational documentation. Installed role
definitions were inspected during this work. ORBIT is inapplicable. This internal
review uses role lenses; it is not independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Merging values could appear to admit changed scientific claims. | P2 | Status | Keep all copies proposed, source records unchanged and admission separate. Addressed by validation and browser source-preservation checks. |
| 2 | Automatic object merge does not establish scientific coherence between fields. | P3 | Preview | Show complete resulting records and require domain review before admission. |
| 3 | Null and missing have different measurement meanings. | P3 | Comparison | Preserve presence flags and test both cases; do not substitute zero. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A journal alone lacks the old source needed for a valid comparison. | P2 | Baseline | Retain exact bundle bytes with first journal in the same storage transaction; verify hash or require matching attached baseline. Addressed. |
| 2 | Input provenance must survive migration. | P3 | Journal | v2 events retain parent bundle/journal hashes, revision and decisions; old journals remain exportable. |
| 3 | A canonical JSON hash is not a signature or an original-byte journal receipt. | P3 | Contract | Document typed serialization and unauthenticated local metadata explicitly. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Index merging arrays could splice unrelated coordinates or seasonal samples. | P2 | Merge | Treat arrays atomically and require a choice on conflicts. Addressed with Rust tests. |
| 2 | Source rebasing could silently modify imported map geometry. | P3 | Geography | Install only working copies; source query/map indexes remain imported. |
| 3 | A merged proposed geometry still needs geometry and measurement validation. | P3 | Admission | Keep draft geometry outside official source maps and rankings until validation. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Prepared output could be reported saved before persistence succeeds. | P2 | Save | Prepare without mutation, commit, then install; simulated storage-abort check passes. Addressed. |
| 2 | Missing targets must not disappear silently. | P3 | Conflict | Require explicit omission and explain old-journal recovery. |
| 3 | A successful migration is not a source release. | P3 | Wording | State proposed-record migration and pending admission in controls and contract. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Conflict choices need labels and keyboard access. | P3 | Controls | Use labeled native selects, semantic buttons and status feedback. |
| 2 | Expanded JSON comparisons can force narrow viewport overflow. | P3 | Reflow | Bound internal JSON scrolling; verify expanded conflict plan at 320 px. |
| 3 | Raw JSON comparison requires substantial reading effort. | P3 | Usability | Field path and old/proposed/new values are available; consider a structured value comparison after this local version. Human usability review remains open. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Sequential conflict IDs can attach choices to another field after plan changes. | P2 | Identity | Bind IDs to record/path/kind and reject unused choices. Addressed with stable hashes and tests. |
| 2 | Another tab can change destination history during preview. | P3 | Concurrency | Check expected revision in Rust and IndexedDB history CAS; stale tabs must reload. |
| 3 | An inventory-sized migration can exceed one transaction's operation limit. | P3 | Batching | Prepare multiple events atomically; 51-record test confirms complete replay without live mutation. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earlier documentation marked rebasing unimplemented. | P3 | Status | Update README and query contract with implemented rules and commands. |
| 2 | Export/import must preserve the existing recovery route. | P3 | Recovery | Keep old source/journal exports and native exclusive new-file outputs. |
| 3 | Local verification does not prove a full release. | P3 | Release | Keep clean-checkout, independent science and human accessibility gates open. |

## Synthesis

Seven roles, 21 findings: zero P1, five addressed P2 and sixteen P3. Approved with
conditions for local proposed-record migration. Top finding: retain and verify the
baseline before comparing changes. SOUNDER/KEEL agree on identity and input binding;
CURRENT/CHART agree that merging records does not admit measurements or geometry.

## Three amendments

1. Retain source bytes atomically with journals and verify the old snapshot hash.
2. Use stable field conflict IDs, atomic arrays and explicit removed-target and
   destination-copy choices; record parent provenance in v2 events.
3. Prepare the whole candidate without mutation, commit with revision/history CAS,
   then install; retain old exports and document native/browser recovery limits.

## Evidence and conditions

Fourteen Rust tests pass, including three-way conflicts, missing/null distinctions,
atomic arrays, missing targets, destination collisions and a 51-record migration.
Browser checks pass for retained source bytes, conflict preview/choices, native/WASM
payload and provenance parity, v2 replay, old/source preservation, durable revisions,
cross-tab conflicts and storage abort. Conflict screenshot was viewed. Expanded-plan
320 px reflow and final map/query regression also pass. Canonical ledger SHA256:
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

Domain admission, semantic ID/schema migration, signatures, draft-map validation,
multiuser hosting, human accessibility review and public release remain open.
The canonical ledger is preserved; this slice changes proposed-record tooling.
