---
skill: roles-check
topic: almanac-publication-reliability
date: 2026-10-07
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Publication reliability and consolidation review

Internal role review of the acquisition fix and accumulated main-targeted
snapshot. Selected lenses cover scientific scope, provenance, visual evidence,
public explanation, accessibility, validation and repository stewardship.
This is not independent scientific review of the measurements.

| Role | Finding | Severity | Section / recommendation |
|---|---|---|---|
| CURRENT | Publishing code does not admit whole-current dimensions. | P3 | Preserve all scoped width, seasonal and geometry flags. |
| CURRENT | Recurrence is distinct from tracked individual eddies. | P3 | Keep nine regional summaries and unresolved footprint status. |
| CURRENT | The full goal still has known gaps. | P3 | Report 89 missing published lengths and 57 unassessed widths. |
| SOUNDER | Download failures must not weaken the source pin. | P2 | Resolved: exact SHA remains required after every successful request. |
| SOUNDER | A changed or corrupt local original cannot be silently refreshed. | P3 | Existing-copy validation fails without a network retry or overwrite. |
| SOUNDER | Failed staging cannot leave a fixture for later runs. | P2 | Resolved: stage verified bytes, fsync, exclusive Windows rename/POSIX link, cleanup. |
| CHART | Main landing must include actual maps/cards, not just JSON. | P3 | Fast-forward the complete accumulated commit history including WASM/UI. |
| CHART | Nearby source context remains distinct from measured boundaries. | P3 | Retain prior route, section, station and recurrence scope labels. |
| CHART | All map modes still need CI coverage on the new head. | P2 | Open publication condition: await all registered browser gates. |
| BEACON | Local success is not protected-main success. | P3 | Publication receipt distinguishes local checks from exact-head CI. |
| BEACON | Download retry is not new scientific evidence. | P3 | Describe as source-fixture reliability only. |
| BEACON | A single publication PR should explain the complete scope. | P3 | Update PR 30 description with the accumulated data and query work. |
| HARBOR | Consolidation must retain mobile/chart and semantic card work. | P3 | Git ancestry proves existing commits are included. |
| HARBOR | Browser assignment is not proof of all checks passing. | P3 | Keep the distinction: 14 assignments, 52 registered checks. |
| HARBOR | Retry logs should remain readable. | P3 | Name the fixture, retry number and delay without dumping payloads. |
| KEEL | Transient failures need bounded retries. | P2 | Resolved: three attempts, 60 s/request, 1/3 s delays. |
| KEEL | Permanent HTTP and integrity failures must stop promptly. | P2 | Resolved: 403 and format/size/checksum errors never retry. |
| KEEL | CI is required against the consolidated commit. | P3 | Push the exact fast-forward head; leave existing live jobs alone. |
| LOGBOOK | Updating the publication branch could lose intervening work. | P2 | Resolve via refreshed remote ancestry immediately before non-force push. |
| LOGBOOK | Original paper fixtures must remain ignored. | P3 | Preserve source exclusion and all existing source-use decisions. |
| LOGBOOK | Draft branch PRs should remain until main lands. | P3 | Keep their review receipts; consolidate without premature closure. |

## Synthesis

Seven roles; P1: 0, P2: 6 (four implementation conditions resolved, ancestry
to verify immediately before push, exact-head CI open), P3: 15.
APPROVED-WITH-CONDITIONS. SOUNDER and KEEL agree
that retries must never accept altered or incomplete source bytes. CHART and
LOGBOOK require the full accumulated snapshot and its actual browser checks.

## Amendments

1. Add bounded transport retries while keeping source checksum/format/size pins.
2. Stage verified files and preserve exclusive, atomic destination creation.
3. Verify remote ancestry and fast-forward one existing PR to main; report CI
   and remaining scientific data gaps separately.
