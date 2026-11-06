---
skill: roles-check
topic: asca-alignment-readback
date: 2026-10-20
roles_used: [CURRENT, SOUNDER, CHART, BEACON, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# ASCA numerical readback review

Source base `20b1017`; reviewed the working repair described in
`plans/asca-readback-repair-batch-2026-10-20.md`. These are internal functional
checks, not external scientific review or release approval. CURRENT/SOUNDER
cover scientific/provenance impact, CHART/BEACON cover interpretation, and
KEEL/LOGBOOK cover strict reconstruction and failed-gate recovery. Visual
assets and controls are unchanged; existing browser accessibility checks are
retained. There is no planetary comparison.

| Role | Finding | Severity | Action/evidence |
|---|---|---|---|
| CURRENT | Rounding a decision variable could change measured boundaries. | P2 | Addressed: only the non-decision indicator is rounded after all measurement/summary decisions; `measure` stays full precision. |
| CURRENT | The indicator is not a diagnosed physical current direction. | P3 | Original fixed-array component/no-rotation interpretation and physical-admission flags remain unchanged. |
| CURRENT | Source sampling and correction limitations persist. | P3 | No new full-file checksum, corrigenda review, current width or annual range claim. |
| SOUNDER | A blanket numerical tolerance would conceal other data differences. | P2 | Addressed: strict equality retained; only an explicitly pinned derived-field readback is changed. |
| SOUNDER | Original observations must not be rounded with the indicator. | P3 | Raw/monthly/query packets, source vectors, clocks, masks and original protocol remain exact. |
| SOUNDER | Provenance must identify the new representation. | P3 | Report binds six-decimal declaration and generator; downstream hashes are renewed. |
| CHART | Readback precision could be shown as physical angular certainty. | P2 | Addressed: declaration explicitly separates numerical readback from observational accuracy or error bars. |
| CHART | A new output angle could accidentally rotate map geometry. | P3 | No rotation/geometry code change; source spans/brackets and both figure assets remain byte-exact. |
| CHART | Unresolved outcomes must remain visible. | P3 | All 931 outcomes and 2,793 cases persist; primary 330 resolved/601 unresolved unchanged. |
| BEACON | Only editing the three Linux discrepancies would be inconsistent. | P2 | Addressed: one rule applies to all non-null computed indicators; 925 stored representations change by less than half a microdegree. |
| BEACON | A successful repair could be retold as a new scientific measurement. | P3 | Batch names a representation repair; all physical width/range limitations retained. |
| BEACON | Local disk failures and a Linux numerical mismatch have different causes. | P3 | Both failures, counts and receipts are documented separately. |
| KEEL | ASCA was missing from the independent reconstruction audit. | P2 | Addressed: target16 verifies original byte subsets and strict encoded report equality. |
| KEEL | New declaration pin must be enforced in the browser engine. | P2 | Addressed: ninth corruption case mutates readback pin; native/WASM must both reject. |
| KEEL | The old complete run failed and cannot establish a green baseline. | P3 | Keep terminal 1,881-pass/nine-ENOSPC-failure receipt; run a new clean full with storage guard and new receipt. |
| LOGBOOK | A failed automatic repack must not be mistaken for a lost commit. | P3 | Commit/push and committed pins verified; only the abandoned temporary pack removed after Git termination. |
| LOGBOOK | Source originals and failed evidence need preservation during cleanup. | P3 | Original datasets retained; failed logs/receipts retained, fixtures compressed losslessly, caches only removed. |
| LOGBOOK | Continuing work must remain in the existing PR. | P3 | Same draft PR83, no new PR or main merge; broad data goal remains active. |

Six roles, zero P1 findings in the proposed representation change, six P2
findings addressed, twelve P3 notes. APPROVED-WITH-CONDITIONS: obtain fresh
current-head Linux byte equality and a passing complete gate before release.
The code review does not override either outstanding gate.

Amendments: declare exclusive field precision; verify all non-angle data and
source custody; keep the failed full run and start a distinct storage-guarded
complete run instead of relabeling or overwriting its result.

Terminal local follow-up: 19 ASCA tests, 81 Rust tests, locked builds/native
atlas and all existing ASCA browser views/source queries pass. Native/actual
WASM match all 931 outcomes; all nine corruptions, including the new protocol
pin, reject. 770 staged pins verify, including the retained source-byte graph.
All source vectors, spans, decisions and summaries are unchanged; both figure
assets and all 60 Red Sea typed cases remain exact. A fresh independent Linux
and complete-suite result remain required; local checks do not replace them.
