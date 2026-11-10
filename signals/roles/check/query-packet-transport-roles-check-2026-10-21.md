---
skill: roles-check
topic: query-packet-transport
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Query packet transport: internal functional review

Base: ede0418a637b5bd7ddc3a6ab91c7ae1bec70a574. Artifact: transport protocol,
Python reader/writer, native reader, worker assembly, complete-source workspace
compatibility and their checks. Seven relevant repository lenses are applied
as an internal review, without delegated reviewers or external scientific
approval. ORBIT is excluded because this is not a planetary comparison or
atlas release.

## Findings

| Role | Finding | Severity | Evidence and disposition |
|---|---|---|---|
| CURRENT | Repacking must not change physical claims or values. | P3 | Confirmed: complete logical bytes, all49 collections/43353 rows unchanged from the base. Keep the preservation check. |
| CURRENT | Retained model spans must not become perpendicular widths or whole-current lengths. | P3 | Confirmed: unchanged Kuroshio scope, failed cases, unknown uncertainty and unflagged boundary fallback. No new measurement admission. |
| CURRENT | Eighteen missing width owners include heterogeneous identities. | P3 | Open scientific work:6 entries classified as current,8 families,4 systems. Do not inherit component widths onto parents or equate unresolved names. |
| SOUNDER | Physical entrypoint identity differs from logical snapshot identity. | P2 | Resolved: engine pins entrypoint and members; workspace SHA remains40a91e86c8eebfb9b0da86d58e2a4d80951325a95d5c90617af97f44955320ba. |
| SOUNDER | Parts can split UTF-8 and must not be decoded separately. | P2 | Resolved: raw byte assembly, exact individual and aggregate hashes; boundary-split regression. Preserve binary Git attributes. |
| SOUNDER | Source export/rebase must retain complete original bytes. | P2 | Resolved: native/WASM saved-source and explicitly reattached102819992-byte source rebasing pass. Export remains complete logical JSON; both UI/WASM guards raised from100MB to512MiB. |
| CHART | Transport changes must preserve every atlas source and route card. | P2 | Resolved:106 exact source documents,18 loader rejections,77 reference cards; optional/missing data remain explicit. |
| CHART | Dated regional map/card links must keep date/depth. | P2 | Resolved: Kuroshio map overlay, keyboard return,36 dated source frames, selection sharing and clearing pass. |
| CHART | Object marks must not be described as physical footprints. | P3 | Confirmed:241 marks include current locators and contextual gateways;136 named eddy plus4 operational records. Keep distinctions in coverage messages. |
| BEACON | Removing a Git blob cap does not provide unlimited in-memory queries. | P2 | Resolved: protocol states full-bundle memory remains and lazy collection loading is future work. |
| BEACON | Instructions to attach query-data.json become misleading after partitioning. | P2 | Resolved: missing-source message requests the exported complete source snapshot. Export filenames remain osw-source-*.json. |
| BEACON | Storage work must not inflate scientific completion counts. | P3 | Confirmed:12 qualified lengths,83 scoped width owners and remaining evidence gaps unchanged. |
| HARBOR | Missing/corrupt members must produce readable failure states. | P2 | Resolved: shipped worker reports HTTP/hash/path failures through query status; no partial query result is installed. |
| HARBOR | Existing narrow and keyboard flows must remain usable. | P2 | Resolved: general query/workspace and dated map/card checks retain320px reflow and keyboard interactions. |
| HARBOR | Large-source rejection must be actionable and consistent. | P2 | Resolved: UI/WASM share512MiB guard and text; complete-source attachment and early oversized rejection pass in the shipped browser engine. |
| KEEL | Ordered parts need schema, length, path and hash validation in each reader. | P2 | Resolved: Python/native/worker validators; missing/changed/path/order/size/aggregate/legacy checks. Native rejects resolved paths outside its bundle directory. |
| KEEL | Coverage checks incorrectly assumed240 objects and no working admissions. | P2 | Resolved: verify every frozen release row exactly/in order, unique IDs, working inventory, all collection first/last pages and record inspection. Rebase fixture preserves pinned identity while testing a three-way editorial conflict. |
| KEEL | A fresh complete offline gate is still unavailable. | P2 | Open: existing CI paper acquisition fails HTTP403 before tests; local disk below4GiB full-suite guard. Last complete Python baseline774e466:1910 tests/1222 subtests. Do not claim fresh full-suite or release approval. |
| LOGBOOK | Work must stay on the continuing authorized branch/PR. | P2 | Resolved: codex/current-measurement-gaps, existing draft PR83, no main merge. Verify remote SHA after push and update only the current snapshot section. |
| LOGBOOK | A fresh checkout must reconstruct without an ignored monolithic copy. | P2 | Resolved: tracked hash-bound parts, byte-preserving attributes, revision-aware Git reader and unchanged public entrypoint. |
| LOGBOOK | Stale generated parts can accumulate after later rebuilds. | P3 | Open documented maintenance work: writer never deletes prior parts or originals. Later cleanup must prove that an asset is generated and unreferenced. |

## Synthesis

Seven roles,21 findings:0P1,15P2 (14resolved,1open),6P3. Focused final gates
pass; this review permits a draft increment. It does not authorize a main merge or
claim scientific release readiness. A fresh complete offline suite remains
open. The full core-data/info/visualization goal remains active.

The shared concern across SOUNDER, KEEL and HARBOR is that partitioning must
preserve existing source snapshots and fail visibly on incomplete input.
The complete-source rebase and corruption gates decide that concern.

## Amendments

1. Preserve logical bytes and workspace identity; pin physical transport
   separately and verify all parts before installing any store.
2. Preserve complete source exports, align UI/WASM limits, exercise saved and
   explicitly attached source rebasing, and retain canonical identity in fixtures.
3. Correct obsolete inventory assertions while preserving every frozen row;
   publish evidence and incomplete full-suite status in the same continuing PR.
