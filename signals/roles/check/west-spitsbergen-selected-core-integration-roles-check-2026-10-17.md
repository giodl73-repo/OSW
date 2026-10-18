---
skill: roles-check
topic: west-spitsbergen-selected-core-integration
date: 2026-10-17
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---
# Shared WSC selected-core record integration

Direct review through seven installed role lenses, not independent external review. ORBIT omitted: no astronomical mechanism. Artifact: 150th scoped width record, Python/Rust guards, generated bundles and shared browser renderer.

| Role | Finding | Severity | Resolution |
|---|---|---|---|
| CURRENT | Core width cannot be promoted to whole-current width. | P2 | 28 km retains local zonal selected-core meaning; whole-current and physical-edge geometry remain unknown. |
| CURRENT | Variability and uncertainty have different meanings. | P2 | 7 km is stored as reported standard deviation, separate from null width range and false confidence/annual flags. |
| CURRENT | 2015 tubes and 2020-2023 selected core are different estimators. | P2 | Seven source rows retain separate definitions; the six-row tube comparison remains intact. |
| SOUNDER | Record, original and figure must agree across runtimes. | P2 | Compiled audit/figure bindings require exact row and dependency hashes. |
| SOUNDER | A removed record could bypass per-row validation. | P2 | Owner/width presence triggers the completeness guard; missing record and removed source pin reject together. |
| SOUNDER | Dataset metadata must not imply downloaded profiles. | P2 | Native fields remain explicitly unacquired; metadata snapshots and HEAD probes are labelled. |
| CHART | The statistic must not become a buffered route. | P2 | Native query returns no map geometry; no geographic edge pair extracted. |
| CHART | New measurement should not change other route definitions. | P2 | All six seasonal frame objects remain equal; only their shared inventory source fingerprint is refreshed. |
| CHART | A whisker can imply extrema. | P2 | Graphic, adjacent text and numeric facts identify reported SD; annual range remains unknown. |
| BEACON | Caption must explain selection and missing seasons. | P2 | Exact three mission windows and unextracted selected membership are stated. |
| BEACON | Long evidence text can bury the card. | P3 | Card details collapse by default; query and selected-record pages open details. |
| BEACON | Data refresh should not imply independent scientific approval. | P2 | Editorial extraction status remains; source association and scientific admission caveats retained. |
| HARBOR | Every route needs numeric facts and a source path. | P2 | Shared renderer includes point, SD, unknowns, mission table, record inspector and source query. |
| HARBOR | Hidden details must remain keyboard reachable. | P2 | Native summary with 44 px target; keyboard opening and link navigation verified. |
| HARBOR | Narrow tables and graphics need usable alternatives. | P2 | Wrapped 320 px table, short headers with accessible names, full-size figure link and reduced-motion check. |
| KEEL | Binding changes must reject identically in native and WASM. | P2 | Four engine corruption cases reject; Rust tests cover method, source pin, record deletion and duplication. |
| KEEL | New indexed metadata can remain unreachable despite a successful build. | P2 | All five new JSON sources are verified in the shipped WASM source UI. |
| KEEL | An earlier full suite does not prove this candidate. | P2 | be51979 suite is tracked separately; new clean combined gate remains required. |
| LOGBOOK | Stored and proposed width counts must remain distinct. | P2 | 150 editorial scoped widths across 79 owners; proposed branch records unchanged; unresolved aliases still have zero widths. |
| LOGBOOK | Source refresh can cause misleading dashboard changes. | P2 | Only WSC update fingerprint changes; other owners preserve content except required seasonal provenance hash refresh. |
| LOGBOOK | Workflow must remain one continuing PR. | P2 | All commits belong to codex/current-measurement-gaps / draft PR 83; no main merge. |

21 findings: 0 P1, 20 P2, 1 P3. Amendments are implemented and focused checks support them. Verdict remains conditional on the clean combined offline gate and remote-head verification. No full-suite or remote-CI passing claim is made here.

## Amendments
1. Preserve the source statistic and its SD as separate quantities, with explicit geographic, layer and temporal support.
2. Enforce original/owner/completeness bindings and preserve all earlier measurements and physical route definitions.
3. Use one renderer across cards, seasons and query with numeric/source alternatives and keyboard-accessible compact details.

## Post-review gate evidence

- The final all-card check passed all 100 current cards and 150 unique width records. The new widget uses selectedCoreId; measurementId remains unique to the generic record disclosure.
- The broad focused Python gate passed 48 tests and 658 subtests in 454.99 s.
- be51979 full suite is TERMINAL_FAIL from a fixture MemoryError, with 1,645 passed tests and 1,081 subtests. The twelve-copy allocation was replaced with the same twelve sequential checks; all 31 affected tests pass in 84.90 s.
- Combined clean full gate and remote-head verification remain conditions. Inspected be51979 CI runs 39102535428 and 39102528802 failed during unchanged Van Aken/Reading original acquisition (connection refused), before the offline suite; this does not establish the status of a future candidate.
