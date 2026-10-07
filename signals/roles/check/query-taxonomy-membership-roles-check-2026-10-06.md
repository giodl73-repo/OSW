# Queryable editorial identity taxonomy: roles review

Base commit: `629ed31`; working branch `codex/agulhas-mean-section-width`.
Artifact: source-bound membership projections, Rust graph selection, query UI.
Internal functional review; no new independent scientific classification.

## Selection

CURRENT: interpretation and measurement independence. SOUNDER: source identity
and projection receipts. CHART: geographic meaning. BEACON: membership wording.
HARBOR: navigation, sharing and reflow. KEEL: validation and graph selection.
LOGBOOK: local/canonical distinction. ORBIT excluded: no analogy introduced.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | Family membership must not inherit member dimensions. | P3 verified | Existing object records selected unchanged; parent width IDs empty; member widths remain separate. |
| 2 | CURRENT | Identity membership is not physical connectivity. | P3 verified | Explicit scope and false connectivity flag; flow-network query remains distinct. |
| 3 | CURRENT | Existing classification and physical completeness differ. | P3 open | All 240 stored facets preserved; missing members/eddy links require separate evidence work. |
| 4 | SOUNDER | Naming citations could be mistaken for parent evidence. | P3 verified | Context-only URLs; editorial ledger source pointer is the assignment provenance. |
| 5 | SOUNDER | Stale or edited source bytes must fail loading. | P3 verified | Two raw JSON/SHA receipts bound to input manifest; altered raw source rejected. |
| 6 | SOUNDER | Identity facets must match their source entities. | P3 verified | Complete inventory and exact type/level/basin/setting/time/label projections checked. |
| 7 | CHART | A family map could imply a whole-family footprint. | P3 verified | Existing individual features selected; no geometry aggregation or new physical state joins. |
| 8 | CHART | Parent and child lists initially lacked visual grouping. | P2 resolved | Separate parent-family/system and member/component headings in inspected cards. |
| 9 | CHART | No declared edge is not proof of an isolated flow. | P3 verified | Empty membership context explicitly retains unknown physical taxonomy. |
| 10 | BEACON | Direct children and all descendants need distinct meanings. | P3 verified | Separate controls; umbrella returns two direct subfamilies versus seven descendants. |
| 11 | BEACON | Result wording lacked the relation interpretation. | P2 resolved | Editorial identity scope is shown beside query results and on cards. |
| 12 | BEACON | Source collection rows need readable labels. | P3 verified | Child-to-parent labels and context-only naming reference; both cards accessible. |
| 13 | HARBOR | Opening a parent outside results left sharing on the child. | P2 resolved | Exact-parent object query before inspection; parent share/reload verified. |
| 14 | HARBOR | Meaning must survive narrow screens and non-color reading. | P3 verified | Keyboard button navigation, semantic selects, textual definitions and 320 px reflow checked; manual assistive-technology review remains open. |
| 15 | HARBOR | Root inclusion must be an explicit choice. | P3 verified | Checkbox and shared include_root parameter; default excludes root. |
| 16 | KEEL | Ancestor/descendant direction needs an independent oracle. | P3 verified | All connected roots plus an unlinked named eddy tested in four directions against ledger-derived closure. |
| 17 | KEEL | Invalid links must not silently change the graph. | P3 verified | Eight loader rejections; projection, label, pointer, source, facets and vocabulary checks; cycles rejected. |
| 18 | KEEL | Builder edits could discard scientific filters. | P3 verified | Existing advanced object filters retained; two-filter native/WASM and builder/share checks. |
| 19 | LOGBOOK | New editorial links must not mutate canonical relations. | P3 verified | Canonical release diff empty; new taxonomy_links collection explicitly editorial. |
| 20 | LOGBOOK | Local verification and publication are separate states. | P3 open | New changes remain uncommitted and unpushed; PR20 already merged separately. |
| 21 | LOGBOOK | Data and implementation provenance must stay reproducible. | P3 verified | Python taxonomy generator pinned; native/WASM source/bundle receipts checked. |

## Synthesis

Seven roles, 21 findings: three P2 issues resolved; 18 P3 notes; no open P1/P2.
APPROVED-WITH-CONDITIONS for local taxonomy navigation. CURRENT, SOUNDER and
BEACON agree that these are recorded identity assignments, not source-proven
physical connections or inherited measurements. Complete scientific taxonomy,
manual assistive-technology review and publication gates remain open.

Verification: 23 Rust tests; three Python projection tests and two subtests;
independent closure checks for every connected root in all four directions;
eight malformed-loader cases; native/WASM parity; builder filters, direct
parent/child cards, parent share/reload, grouping, keyboard access, explicit
root inclusion and 320 px reflow. Existing
query and dashboard evidence navigation browser regressions passed.
