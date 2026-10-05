---
skill: roles-check
topic: dashboard-evidence-navigation
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Dashboard evidence navigation review

Internal functional review of dashboard generator, coverage/update UI, query
record URLs and tests; not independent scientific peer review. Seven roles are
selected for physical interpretation, provenance, cartography, public editing,
accessibility, reproducibility and repository state. ORBIT is not applicable.

| # | Role | Finding | Severity / disposition | Evidence or action |
|---|---|---|---|---|
| 1 | CURRENT | Diagnostic presence is not a successful current axis. | P3, verified | All ten method documents counted, including three failed NOAA days. |
| 2 | CURRENT | Transport evidence must remain separate from width. | P3, verified | Three transport records get their own capability; width and ranked length counts remain zero. |
| 3 | CURRENT | Sparse dates cannot establish annual ranges. | P3, verified | Existing unranked/null annual fields enforced; no seasonal geometry added. |
| 4 | SOUNDER | Method data updates were absent from coverage fingerprints. | P2, resolved | Actual Loop documents and network input now enter their owners' content fingerprints. |
| 5 | SOUNDER | Source and protocol drift must fail before lighting coverage. | P3, verified | Diagnostic comparison, source manifest, source snapshot and protocol SHA checks. |
| 6 | SOUNDER | Year means cannot receive an invented exact endpoint. | P3, verified | Throughflow latest exact date remains null; Loop latest observation is 2026-09-25. |
| 7 | CHART | Diagram evidence cannot increase geographic footprint coverage. | P3, verified | New categories separate from geometry; no source locations or axes inferred. |
| 8 | CHART | A map selection should lead to the map-bearing card. | P2, resolved | Evidence links open Loop object maps or Throughflow network card directly; primary evidence-mode links follow them. |
| 9 | CHART | Existing global inventory must stay visible. | P3, verified | 100 current stations and 240 total objects preserved; existing atlas regression passes. |
| 10 | BEACON | Coverage counts need descriptive units. | P3, verified | Dated method diagnostics, passage networks and observed passage transport labels. |
| 11 | BEACON | Change reasons need the relevant evidence category. | P3, verified | Passage changes flag measurements; network topology flags routes/geometry; method changes flag time evidence. |
| 12 | BEACON | Bad record links must not imply store failure. | P2, resolved | Missing selection reports result-page mismatch while retaining valid query results. |
| 13 | HARBOR | Direct links must support keyboard selection. | P3, verified | Keyboard station selection exposes semantic links; matched cards open with focus and scroll. |
| 14 | HARBOR | Color cannot be the only evidence signal. | P3, verified | Count text, Updated label and change reason accompany lights. |
| 15 | HARBOR | Added links must retain compact reflow. | P3, verified | New coverage card inspected; 320 px reflow checked. |
| 16 | KEEL | Adding categories must not falsely mark every object updated. | P3, verified | Compared main snapshot with generated rows: only two owner content fingerprints change. |
| 17 | KEEL | Selected cards must survive share and reload. | P3, verified | Query/inspect URL round trip tested; new submission clears selection. |
| 18 | KEEL | Unmatched selected IDs must not open unrelated records. | P3, verified | Initial selection constrained to result-page IDs; invalid selection browser case. |
| 19 | LOGBOOK | Scientific/canonical inventory counts must remain stable. | P3, verified | Canonical release unchanged; no new ranked dimensions or named objects. |
| 20 | LOGBOOK | Local progress needs a reproducible contract. | P3, verified | Contract, source bindings, unit/browser checks and review versioned together. |
| 21 | LOGBOOK | Publication remains a separate action. | P3, open | This follow-up is local; prior PR19 publication is complete. Independent scientific review remains open. |

## Synthesis and amendments

Seven roles, 21 findings; three P2 issues resolved, 18 P3 notes, no open P1/P2.
APPROVED-WITH-CONDITIONS for local coverage/navigation behavior. CURRENT, SOUNDER
and CHART agree that evidence presence, physical geometry and measurement
admission need distinct categories.

1. Include method/network contents and bound receipts in coverage generation.
2. Link directly to the selected map/network card and preserve it on reload.
3. Keep valid results when a selected card is absent, with a precise message.

Verification: 25 focused Python tests and 13 subtests; 22 Rust tests; native/WASM
query regressions; complete dashboard coverage/update/outage regression; direct
Loop/network links, share/reload, selection clearing and 320 px browser checks;
two-owner fingerprint comparison; inspected compact network coverage card.
Full remote publication CI and independent scientific admission are not claimed.
