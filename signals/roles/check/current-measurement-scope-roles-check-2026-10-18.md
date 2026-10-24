---
skill: roles-check
topic: current-measurement-scope
date: 2026-10-18
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Thirteen measurement scope assessments

Direct review of the changes from baseline `82aa5e520bdf2d602beaf7eda1cf8fa811f8589f`.
These are repository functional lenses, not independent oceanographic peer
review. Seven roles apply to data, source binding, diagrams and atlas/query UI.
ORBIT is excluded because there is no planetary comparison.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | Family and component widths cannot be pooled. | P3 | All thirteen parent widths stay null and decisions stay unassessed; preserve the no-inheritance rule. |
| CURRENT | Ambiguous names cannot be silently equated. | P3 | Norwegian and Spitsbergen links retain related-name status; native guard rejects confirmed aliases. |
| CURRENT | Existing components do not establish exhaustive membership. | P2, open | Batch explicitly limits membership to existing links and proposals. Resolve basin conventions before claiming a complete physical taxonomy. |
| SOUNDER | Scope evidence must be reproducible. | P3 | Deterministic generator binds nine frozen inputs, per-owner basis objects, documents and figures; keep exact-byte verification. |
| SOUNDER | A global registry edit should not change every owner's evidence. | P2, resolved | Per-owner basis hashes isolate an added Leeuwin record to the Australian system; synthetic test retains the other twelve reports. |
| SOUNDER | Related owners' dates are not parent observations. | P3 | Preservation checks all dates unchanged; do not use acquisition dates or member dates to light up parent observation coverage. |
| CHART | Relationship diagrams could resemble flow geometry. | P3 | SVG and card state that links are relationships, not current paths or physical boundaries. Retain this qualification. |
| CHART | Pending members need distinct visual treatment. | P3 | Dashed proposed boxes, labels and admission status supplement color. Keep released and proposed links separate. |
| CHART | Narrow cards make diagram lettering small. | P3 | Full-size SVG and equivalent HTML member/status/count text are present. Preserve both alternatives. |
| BEACON | Assessments could be mistaken for completed measurements. | P3 | Batch and reports explicitly say zero new numeric measurements and retain all thirteen missing-width decisions. |
| BEACON | Record counts are not widths. | P3 | Diagram labels say scoped width records; parent scalar and seasonal range remain null. Keep units out of record counts. |
| BEACON | Source links should show useful content immediately. | P2, resolved | Card links query the document root with limit 100, rather than displaying only its schema field. |
| HARBOR | Meaning cannot depend on diagram color. | P3 | HTML members, relationship/status labels and counts accompany accessible SVG title and description. Retain redundant text. |
| HARBOR | Proposal navigation needs keyboard focus. | P3 | Browser gate checks Enter activation and focused pending-member destination; preserve existing focus behavior. |
| HARBOR | Small screens and motion preferences require checks. | P3 | Browser gate uses 320 px viewport and reduced motion; no automatic original-document download is needed. |
| KEEL | Compiling successfully did not prove the actual packet loaded. | P2, resolved | Missing notes receipt, Australian source receipt and scope-audit projection were fixed; engine builder now requires native atlas packet loading. |
| KEEL | Full-packet fixtures retained multiple large mutations. | P2, resolved | Five helpers defer construction and discard each packet; all 28 mutation cases and rejection assertions are retained. Verify the focused gate. |
| KEEL | The latest complete predecessor suite failed. | P2, open | Preserve terminal two-failure result and repairs. Require a fresh complete clean successor gate before main release. |
| LOGBOOK | User rejects a PR for every gap. | P3 | Continue branch and draft PR83; no new PR and no merge. |
| LOGBOOK | New assessments must not inflate coverage. | P3 | Preserve 155 widths, eleven ranked lengths, 76 routes and all dimension capabilities; only thirteen scope-note counts change. |
| LOGBOOK | Test attempts must remain distinguishable. | P3 | Keep earlier rejected packet and invalid scalar-query attempts with corrected successor results; do not report them as scientific measurement failures. |

Roles reviewed: 7. P1: 0. P2: 6 (4 resolved, 2 open). P3: 15.
**APPROVED-WITH-CONDITIONS** for the draft batch, conditional on the focused
browser/fixture gates and a later complete clean gate before main release.
The open membership condition also prevents claims of exhaustive taxonomy.

CURRENT and BEACON agree that these are prerequisites, not numeric gap closures.
SOUNDER and KEEL agree on exact source/owner binding. Three applied amendments:
owner-local basis hashes, readable root-document query links, and native atlas
loading of the generated packet. Original scientific measurements are unchanged.

Focused terminal results: eight scope/endpoint tests and five subtests pass;
two dashboard tests pass; 62 Rust tests pass. Five fixture lifetime tests pass
with all 28 corruption cases retained. Broad browser gate passes all thirteen
cards, fourteen exact source documents, 100 current-object native/WASM queries
and six native/actual-WASM rejection cases, with keyboard, 320 px reflow and
reduced motion. Final preservation passes 93 engine, 166 research and 346
indexed-document hashes, all original measurements/dates and 227 other owners.

A final review amendment also checks the route-planning document, note and
source hash against the exact expected scope assessment. Changing only a
planning projection must be rejected even when its owner is unchanged. The
final engine browser receipt and complete successor suite remain separate
gates; the preceding broad browser success does not substitute for them.
The final engine browser gate subsequently passes all 100 current-object
queries, map/card reflow and all seven native/actual-WASM corruption cases,
including the planning-only document mutation. No page errors or automatic
original downloads occur. The complete clean successor suite is still pending.
