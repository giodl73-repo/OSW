---
skill: roles-check
topic: passage-observation-state
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Published mooring point and state-query review

Internal functional review of network projections, spatial index/query gate,
map metadata, controls and independent audit. Not independent scientific review.
CURRENT examines physical meaning; SOUNDER provenance; CHART topology/maps;
BEACON public language; HARBOR access; KEEL verification; LOGBOOK repository scope.
ORBIT is not applicable to this terrestrial observation-location join.

| # | Role | Finding | Severity / disposition | Evidence or action |
|---|---|---|---|---|
| 1 | CURRENT | Point coverage cannot establish whole-current containment. | P3, verified | Passage queries require locator; intersects/within/gateway rejected. |
| 2 | CURRENT | Transport means and mooring locations have distinct support. | P3, verified | Three 2004-2006 means remain parent records; eight sites do not create eight transport values. |
| 3 | CURRENT | Display-state membership is not a historical physical boundary. | P3, open | Static approximate geometry; no inferred 2004-2006 state boundary or current footprint. |
| 4 | SOUNDER | Observation marks lacked individual source-support metadata. | P2, resolved | Site names, source URL/SHA, locator and published deployment dates retained and validated. |
| 5 | SOUNDER | Deployment interval could imply exact position persistence. | P3, verified | First-deployment support explicitly distinguished from exact redeployment and persistent tracks. |
| 6 | SOUNDER | The derived audit needs noncircular provenance. | P3, verified | Canonical serialization hash of state geometry, network source SHA and generator SHA retained. |
| 7 | CHART | Point topology must retain holes and boundary contact. | P3, verified | Existing covers/touches logic and longitude shifts reused; independent full-state oracle. |
| 8 | CHART | Multiple moorings inherited one passage label. | P2, resolved | Individual mooring labels on map, hover and keyboard targets; parent record remains linked. |
| 9 | CHART | A source point must not become a passage polygon. | P3, verified | Eight Point marks only; unchanged axes and state/current relation inventories. |
| 10 | BEACON | Observation-location results need precise names. | P3, verified | Throughflow mooring sites in SUND preset; locator relation separated from recorded evidence links. |
| 11 | BEACON | No matches must not imply current absence. | P3, verified | Audit/contract explicitly restrict no-match interpretation; NADR has no matching sites. |
| 12 | BEACON | Sources should be recoverable from computed relations. | P3, verified | Relation metadata retains source URL/hash, site name and deployment support. |
| 13 | HARBOR | Computed site selection needs keyboard access. | P3, verified | Focusable marks open parent record with computed relations and textual sites. |
| 14 | HARBOR | Station-location maps exposed unrelated date playback. | P2, resolved | Object date/month controls hidden for passage maps; manual state controls remain. |
| 15 | HARBOR | Narrow screens must retain query and source access. | P3, verified | 320 px reflow and semantic state/predicate controls checked. |
| 16 | KEEL | Source support mutations must fail before display. | P3, verified | Name, deployment start, source URL and source SHA corruption rejected by loader. |
| 17 | KEEL | Testing SUND alone would not cover the state inventory. | P3, verified | All 56 Rust state queries compared with independently derived point/feature matches. |
| 18 | KEEL | State changes and shares must preserve locator-only meaning. | P3, verified | Browser SUND/NADR controls, preset and share/reload; native/WASM parity. |
| 19 | LOGBOOK | New computed joins must stay outside canonical relations. | P3, verified | No canonical ledger change or recorded state-link promotion. |
| 20 | LOGBOOK | Duplicate IDs must not overwrite spatial records. | P3, verified | Cross-collection spatial duplicate IDs fail loading. |
| 21 | LOGBOOK | Scientific and publication milestones remain distinct. | P3, open | This follow-up is local; source identity and independent physical state interpretation remain review work. |

## Synthesis and amendments

Seven roles, 21 findings: three P2 issues resolved, 18 P3 notes, no open P1/P2.
APPROVED-WITH-CONDITIONS for local observation-point topology. CURRENT, SOUNDER
and CHART agree to preserve the distinction between a mooring location, a
transport section, deployment support and whole-current geographic membership.

1. Bind individual site names and source/deployment metadata to the original rows.
2. Expose locator-only state controls and source-specific labels/inspection.
3. Remove unrelated time animation from static first-deployment site maps.

Verification: 22 Rust tests; independent 56-state oracle; eight SUND locations;
four metadata rejection cases; native/WASM parity; keyword/focus inspection,
state control, sharing and 320 px browser checks. Existing object spatial and
network queries are regression gates. Scientific interpretation and new remote
publication are not claimed complete.
