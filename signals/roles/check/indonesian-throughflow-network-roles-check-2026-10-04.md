---
skill: roles-check
topic: indonesian-throughflow-network
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Indonesian Throughflow network review

Internal functional review of source input, bundle builder, Rust loader/path
query, query card and tests. This is not independent scientific peer review.
CURRENT covers physical scope; SOUNDER provenance; CHART map grammar; BEACON
interpretation; HARBOR equivalent access; KEEL validation; LOGBOOK publication.
ORBIT is excluded because this artifact contains no planetary comparison.

| # | Role | Finding | Severity / disposition | Evidence or action |
|---|---|---|---|---|
| 1 | CURRENT | Connections combine contributions at different depths. | P3, verified | Network scope and card disclose mixed layers and possible reversals. |
| 2 | CURRENT | Exit transports must not be added to upstream transport. | P3, verified | Only three exits enter the reported -15 Sv budget. |
| 3 | CURRENT | Integration window is not physical current width. | P3, verified | 35/35/160 km are explicitly integration widths; current dimensions remain null. |
| 4 | SOUNDER | Source needs exact table and period identification. | P3, verified | Sprintall 2009 Tables 1-2, 2004-2006 means and individual deployment dates retained. |
| 5 | SOUNDER | Processing-choice interval can be mistaken for seasonal variation. | P3, verified | Interval kind explicitly excludes seasonal extrema and confidence bounds. |
| 6 | SOUNDER | Projections and locator coordinates require source binding. | P3, verified | Raw JSON SHA, document equality and all source projections checked by Rust. |
| 7 | CHART | Schematic distances cannot establish lengths. | P3, verified | Diagram coordinates are editorial; geographic node coordinates and edge metrics are null. |
| 8 | CHART | Published point marks cannot establish passage containment. | P3, verified | Eight map marks use the mooring-locator role, with first-deployment scope. |
| 9 | CHART | Node classes and pathways need a legible key. | P3, verified | Circle/square key, pathway colors and prose scope adjacent to schematic; rendered view inspected. |
| 10 | BEACON | Path results may imply particle trajectories. | P3, verified | Query results say conceptual connections, with no metric length or travel time. |
| 11 | BEACON | Public values need sign and depth context. | P3, verified | Passage card explains Indian-directed negative transport, depth and mean period. |
| 12 | BEACON | Names should remain available without persistent diagram labels. | P3, verified | Hover/focus names plus all twelve named node buttons and readable path labels. |
| 13 | HARBOR | Pointer-only node navigation excludes keyboard users. | P3, verified | Focusable SVG buttons support Enter/Space; equivalent semantic node list. |
| 14 | HARBOR | Small-screen layout must retain evidence scope. | P3, verified | 320 px reflow checked; source scope and integration-width caveat remain in card. |
| 15 | HARBOR | Selection needs text feedback. | P3, verified | Focus/hover changes node description; selection opens source card with network return link. |
| 16 | KEEL | Network projections could be orphaned or owner joins removed. | P2, resolved | Loader rejects unknown network projections and missing owner network/passage joins. |
| 17 | KEEL | Bounded search needs failure behavior. | P3, verified | Unknown IDs and hop limits rejected; hop-limit flag checked; simple paths exclude repeated nodes. |
| 18 | KEEL | Ordinary query submission lost path constraints. | P2, resolved | Builder preserves active network path and filters; browser regression covers resubmission. |
| 19 | LOGBOOK | Research graph must not imply canonical admission. | P3, verified | Rank eligibility false; canonical release and ranked lengths unchanged. |
| 20 | LOGBOOK | Source interpretation should be reviewable in repository. | P3, verified | Source input, scope audit, contract and tests versioned together. |
| 21 | LOGBOOK | Publication and scientific admission are distinct milestones. | P3, open | User authorized repository publication; complete network coverage and scientific admission remain open. |

## Synthesis and amendments

Seven roles, 21 findings: two P2 issues resolved and 19 P3 notes. No open P1/P2.
APPROVED-WITH-CONDITIONS for the editorial network/query slice. CURRENT, SOUNDER
and CHART agree that neither diagram distances nor integration windows can enter
the current length/width ranking.

1. Require source-bound projections and owner joins; reject orphan rows.
2. Preserve network constraints when submitting the ordinary query controls.
3. Keep source period, mixed-depth scope, locator role and null dimensions visible.

## Verification

Two flow-network Python tests; 22 Rust tests; five native/WASM conceptual paths;
eight mapped moorings; six malformed-bundle rejection cases; invalid network/node
and hop queries; query resubmission; keyboard node inspection; 320 px reflow;
rendered schematic inspection. Full Python suite: 749 passed plus 539 subtests.
Required remote publication checks must pass before merge. Independent scientific
review, complete exchange-network coverage and measurable branch axes remain open.
