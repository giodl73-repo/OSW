---
skill: roles-check
topic: western-adriatic-radar-width
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Western Adriatic radar width review

Internal review through seven repository roles: physics, provenance,
cartography, public editing, accessibility, engineering and publication.
ORBIT is excluded because no cross-domain analogy is used. This review does
not replace independent scientific admission. Verification outcomes follow.

| Role | Finding | Severity | Resolution / reference |
| --- | --- | --- | --- |
| CURRENT | 40/50 km refer to different locations. | P2 addressed | Two local mean records; no combined range, annual extrema or playback. |
| CURRENT | Surface radar and unstratified tidal model are different products. | P2 addressed | Widths explicitly observed HFR profiles; no model-width promotion. |
| CURRENT | Seasonal velocity variation does not supply widths. | P2 addressed | Numeric width months/dates null; running medians identified as velocity filters. |
| SOUNDER | Deployment period is not common continuous valid support. | P2 addressed | Site gaps and early Ravenna absence preserved; exact averaging weights unresolved. |
| SOUNDER | Effective depth and grid spacing can be mistaken for layer/error. | P2 addressed | Approximate 1 m response and 1.5/5 km processing scales retained separately; fixed layer/error null. |
| SOUNDER | Original identity and selected review scope must be reproducible. | P2 addressed | Original size/pages/SHA, acquisition and protocol pins; selected pages explicitly listed. |
| CHART | Instrument coordinates are not section edges. | P2 addressed | Geographic endpoints and mapped boundaries unresolved; no route bands. |
| CHART | Source plots use opposite velocity signs. | P2 addressed | Figure-specific conventions preserved; no merged or repaired curve. |
| CHART | A width diagram can look like geographic boundary reconstruction. | P2 addressed | Explicit local mean and no mapped edges in caption/aria; no source digitization claimed. |
| BEACON | Location and mean operator must accompany each number. | P2 addressed | Ravenna/Pesaro and section labels visible beside source-specific charts. |
| BEACON | Tidal discrepancy strips resemble current widths. | P2 addressed | Context/protocol exclude 10-20 km discrepancy and velocity confidence from width evidence. |
| BEACON | Readers need direct access to the correct source element. | P2 addressed | Both array pointers bound and tested in inspector/source query. |
| HARBOR | Chart alone cannot communicate scope. | P2 addressed | Source-specific aria, caption, method text and ordinary links. |
| HARBOR | Narrow screens must retain both diagrams. | P2 addressed | Registered 320-pixel text-size/reflow test and screenshot inspection. |
| HARBOR | Direct phase navigation must preserve evidence class. | P2 addressed | Both phase URLs tested; scalar inference bar/edge locator hidden and play disabled. |
| KEEL | Multi-record source lookup must bind array position. | P2 addressed | Shared Rust lookup derives index by identity; Python full-row comparison rejects pointer swaps. |
| KEEL | Coherent receipt edits can evade superficial checksum checks. | P2 addressed | Native scope/fixed-layer/calendar rejection and direct WASM owner-transfer rejection tested. |
| KEEL | Parent source identities must stay protected. | P2 addressed | Eleven-owner deletion/alias regression; Baffin browser compatibility required. |
| LOGBOOK | Journal availability does not grant redistribution rights. | P2 addressed | PDF ignored; copyright/receipt and factual extraction only tracked. |
| LOGBOOK | Source-record count is not complete current dimensions. | P2 addressed | 57 scoped owners distinguished from 35 unassessed and wider seasonal/length gaps. |
| LOGBOOK | Draft stack and local checks cannot imply mainline completion. | P2 addressed | PR64 parent and current remote state recorded; independent admission remains pending. |

Roles: 7. P1: 0. P2: 21 addressed. **APPROVED-WITH-CONDITIONS** for editorial
local-mean evidence, subject to completed execution checks. Raw fields,
reproducible paired boundaries and independent science admission remain gates.

Top finding: a two-location mean comparison is not seasonal variation.
CURRENT, CHART and BEACON agree. Amendments: separate local means; preserve
sampling/operator distinctions; bind full rows and source pointers in the
Python/native/WASM path and maintain browser verification.

Additional KEEL P2 addressed: inspected PR64 offline log proves Python/native
tests ran before the native CLI existed. Existing pinned Rust test/build steps
now precede the Python gates in CI. All tests and checksum requirements remain.
Updated count: 22 P2 addressed; local suite execution and fresh remote outcome
remain separate evidence.

Execution complete: 1,004 Python tests /918 subtests and 41 Rust tests pass.
New Western Adriatic and parent Baffin browser checks pass. Both mobile diagrams
visually inspected; source/query/native/WASM parity and coherent loader/alias
rejection verified. Original transport, audit/provenance and engine pins pass.
Prior records, route catalog and canonical ledger are preserved. Editorial
publication conditions are met; independent scientific admission and fresh
remote validation remain unresolved.

CI fix verification: pinned 1.95.0 offline build in a fresh isolated target,
then 13 native guard tests against its executable, passed. No pre-existing
executable was needed for that check. Pending Linux CI is tracked separately.
