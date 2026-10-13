---
skill: roles-check
topic: baffin-regional-width
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Baffin regional width review

Internal review of source extraction, protocol, data, Rust guards and UI.
These seven repository lenses cover oceanography, provenance, cartography,
editing, accessibility, engineering and publication. ORBIT is excluded because
this batch makes no cross-domain analogy. This is not independent scientific
admission. Verification outcomes are appended after execution.

| Role | Finding | Severity | Resolution / reference |
| --- | --- | --- | --- |
| CURRENT | East Devon and Lancaster widths have different spatial supports. | P2 addressed | Two records and diagrams; no combined range or selected midpoint. |
| CURRENT | Excursion widening and winter meters do not establish seasonal widths. | P2 addressed | Protocol rules 2-3; annual/playback flags false and months/dates null. |
| CURRENT | Unusually severe sea ice limits typical-year applicability. | P2 addressed | Preserved in both captions and context; applicability unresolved. |
| SOUNDER | Institutional hosting does not establish redistribution rights. | P2 addressed | Ignored original, acquisition rights statement and factual extraction only. |
| SOUNDER | Drifter envelopes are not measured simultaneous full widths. | P2 addressed | Separate A/B/C sampling metadata; full-width inference ineligible. |
| SOUNDER | Exact source bytes and inspected scope must be recoverable. | P2 addressed | SHA256, size, pages, receipt/protocol pins and selected-page review declared. |
| CHART | Lancaster width must not be applied to the external route. | P2 addressed | Route omits intrusion; no geographic band or geometry edits. |
| CHART | A scale diagram may imply reconstructed edges. | P2 addressed | Captions and aria state no mapped width edges; paired boundaries unresolved. |
| CHART | Offshore position and nearby eddy diameter can resemble widths. | P2 addressed | Context fields remain distinct; protocol rules 1,5,6 exclude conversion. |
| BEACON | Public values need a readable scope beside the number. | P2 addressed | East Devon and Lancaster labels, locations and limitations next to each diagram. |
| BEACON | A 10-30 km interval can be repeated as seasonal variability. | P2 addressed | Reported average regional span and no annual range stated together. |
| BEACON | Source links must select the appropriate array element. | P2 addressed | Identity-derived /measurements/0 and /measurements/1 pointers. |
| HARBOR | Source meaning must survive without visual geometry. | P2 addressed | Source-specific aria label, caption, method text and query link. |
| HARBOR | Small screens need readable values and no document overflow. | P2 addressed | Registered 320-pixel atlas regression and screenshot inspection. |
| HARBOR | Each width must remain directly navigable. | P2 addressed | Both phase URLs, source pointers and query/native parity exercised. |
| KEEL | Multi-record audits must not depend on a Humboldt-specific branch. | P2 addressed | Shared Rust array lookup derives pointer for any registered source. |
| KEEL | Context deletion and owner edits can evade editable dispatch. | P2 addressed | Ten-source identity registry plus coherent native/WASM alias rejection. |
| KEEL | New coverage must enter the maintained browser gate. | P2 addressed | Baffin test registered; rebuilt engines and deterministic local suite required. |
| LOGBOOK | Scoped evidence is not physical whole-current completion. | P2 addressed | Counts separate evidence coverage; canonical lengths, widths and seasonal admission unchanged. |
| LOGBOOK | Selected pages must not be described as full article review. | P2 addressed | Audit lists inspected pages and explicitly denies full review. |
| LOGBOOK | Remote source timeout is separate from local validation. | P2 addressed | PR63 run/job inspected; failure before tests recorded accurately. |

Roles: 7. P1: 0. P2: 21 addressed. Verdict: **APPROVED-WITH-CONDITIONS**
for editorial regional evidence, conditional on completed execution checks.
Independent scientific review, paired edge methods and compatible repeat widths
remain admission gates, not completed claims.

Top finding: regional average widths cannot become an annual range. CURRENT,
CHART and BEACON agree that spatial excursion changes must retain their support.
Amendments: separate the two regional records; preserve sampling/ice/depth
context; bind record identity and array pointers across Python/native/WASM.

Execution complete: 966 Python tests /918 subtests and 41 Rust tests pass.
Baffin and existing Humboldt browser checks pass; source-pointer/query parity,
coherent native/WASM rejection and 320-pixel Baffin screenshot verified.
The 100-current seasonal snapshot compatibility check passes. Source and
engine pins verified; prior records, canonical ledger and route catalog
preserved. Conditions for editorial publication are met. Stronger scientific
admission and remote source availability remain unresolved.
