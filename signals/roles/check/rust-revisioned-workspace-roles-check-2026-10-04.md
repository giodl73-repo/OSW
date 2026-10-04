---
skill: roles-check
topic: rust-revisioned-workspace
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 4
p2_remaining: 0
p3_count: 17
verdict: APPROVED-WITH-CONDITIONS
---

# Rust revisioned working-record review

Artifacts: Rust transaction/replay methods, snapshot binding, browser IndexedDB
persistence, working record editor, native journal IO and verification. CURRENT
covers scientific status; SOUNDER custody; CHART map separation; BEACON wording;
HARBOR access; KEEL concurrency/reproducibility; LOGBOOK operational status.
Role definitions were inspected in this conversation. ORBIT is inapplicable.
This is an internal role-lens review, not independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A saved proposal could be mistaken for scientific admission or enter source rankings. | P2 | Working store | Require proposed status and a separate collection; source rows and rankings remain unchanged in replay tests. Addressed. |
| 2 | Arbitrary edited record JSON has not passed domain measurement validation. | P3 | Authoring | Treat proposed_data as a pending copy, retain target identity and provide the source reference; source-admission workflow remains pending. |
| 3 | Transaction dates could be confused with observation dates. | P3 | Time | Keep created_at in journal event metadata; source dates remain inside the referenced/proposed record. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A journal loaded against changed source data could silently attach edits to the wrong snapshot. | P2 | Custody | Rust computes the source bundle SHA256 and requires exact journal binding; mismatched import test passes. Addressed. |
| 2 | Archive must preserve the prior record history. | P3 | History | Append delete operation, retain old events and replay the live collection; native/browser archive checks pass. |
| 3 | Local timestamps and replay validity are not authenticated authorship or tamper proof. | P3 | Audit scope | Document device-local metadata and unauthenticated journal; signatures and reviewed source migration remain future work. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Working source edits could implicitly alter published maps. | P3 | Geography | Keep proposed records outside imported geometry indexes; map/query regression proves the source inventory still renders. |
| 2 | Proposal scope needs to be visually obvious. | P3 | Record view | Show proposed working record in the table and full target/proposed JSON; inspector supplies source-reference button. |
| 3 | Stored geometry proposals do not have a validated draft-map preview. | P3 | Remaining work | Explicitly retain pending authoring status; map preview and admission require geometry/domain validation. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Calling a prepared transaction saved before durable storage succeeds would mislead users. | P2 | Save flow | Prepare in Rust without mutation, commit IndexedDB, then install and report saved revision. Storage-abort test passes. Addressed. |
| 2 | Source snapshot, working record and revision journal are different objects. | P3 | Copy | Define them near controls and in the contract, with separate query/export actions. |
| 3 | Native output overwriting a journal could erase revision recovery. | P3 | CLI | Create a new output file exclusively and sync writes; existing output is rejected unchanged. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | JSON authoring controls need visible labels, keyboard access and failure announcements. | P3 | Editor | Use semantic form/labels, required summary and status region; viewport/focus screenshot inspected. |
| 2 | Large record JSON must not force page-width overflow. | P3 | Reflow | Bound textarea width with internal scroll and test 320 px document width after editor mount. |
| 3 | Local storage can be unavailable. | P3 | Failure | Display workspace error and retain imported query use; editing controls are omitted or disabled rather than claiming persistence. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Two tabs could overwrite an intervening edit despite Rust validation. | P2 | Concurrency | Use expected revision in Rust and IndexedDB read/write transaction CAS; stale editor conflict and reload tests pass. Addressed. |
| 2 | Import could rewrite an existing historical event. | P3 | Import | Validate in Rust before storage and require the current journal prefix unchanged; rewritten history test rejects. |
| 3 | Native and WASM authoring paths could diverge. | P3 | Parity | Export browser journal, replay/query and prepare a new native revision, import it back; source/hash and atomic-invalid-batch unit tests pass. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earlier snapshot-only statements became stale after adding working authoring. | P3 | Status | Append README milestone and update contract; leave admission, rebase migrations and shared hosting pending. |
| 2 | New journal files must not overwrite source or previous history. | P3 | Filesystem | Native --output creates a new UTF-8 file and rejects existing paths; interrupted new files may be incomplete and are rejected on replay. |
| 3 | Local tests are not a full public release gate. | P3 | Release | Canonical checksum remains unchanged; independent science, human accessibility and clean-checkout/publication remain separate. |

## Synthesis

Seven roles, 21 findings: zero P1, four addressed P2 and seventeen P3. Approved
with conditions for local proposed-record authoring. Top finding: Rust validation
must precede durable commit, and live installation must follow successful commit.
SOUNDER/KEEL agree on snapshot binding and conflict detection. CURRENT/CHART agree
that saving a proposal is not scientific admission or a map/ranking update.

## Three amendments

1. Add snapshot-bound, replayable proposed-record journals and require source ID,
   pending status and valid UTC event timestamps.
2. Prepare without mutation, compare expected revision/history in IndexedDB, and
   install only after persistence; preserve archive history and conflicting edits.
3. Add browser export/import and native new-file journal IO; verify replay parity,
   failed storage, rejected existing paths and intact source records.

## Evidence and remaining conditions

Ten Rust tests cover typed queries, IDs, topology and workspace replay, invalid
atomic batches, UTC dates, source binding, status/identity and archive history.
Browser checks cover reload, two-tab conflict, native replay/prepare/output,
compatible import, mismatched hash/history rejection, old-snapshot journal export,
archive/source preservation,
320 px reflow and simulated storage abort without live mutation. Query/map parity,
100/240 inventory, spatial modes, share/export, errors and integrity-load checks
pass after authoring integration. Editor screenshot was viewed. Canonical checksum:
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

The journal supports proposed copies of imported records. New source admission,
reviewed promotion, rebase/schema migration, draft geometry preview and a multiuser
service remain implementation work. Browser storage is local and can be cleared;
export is the backup route. Native new-file writes sync on success; interrupted
new outputs may remain invalid while previous journals stay recoverable. There
is no authenticated audit log or atomic in-place native file replacement.
Independent science, human accessibility and full public release gates remain open.
