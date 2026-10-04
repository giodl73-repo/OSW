---
skill: roles-check
topic: australian-component-reference-routes
date: 2026-10-02
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Australian components and ordering sensitivity

Artifact: three editorial route inputs/outputs, candidate catalog computation,
comparison UI and documentation. Seven roles selected for physical scope,
provenance, cartography, explanation, access, reproducibility and repository
status. ORBIT omitted because no planetary analogy is present. Internal
role-lens review, not independent scientific approval.

| Role | Finding | Severity | Amendment/condition |
| --- | --- | --- | --- |
| CURRENT | Leeuwin southern-extension naming differs from the western-coast-only convention. | P3 | Scope explicitly includes the Bight and retains a shorter editorial interpretation. |
| CURRENT | South Australian and Zeehan describe seasonal components. | P3 | Winter naming convention declared in scope, time and figure labels. |
| CURRENT | Editorial waypoints remain unsupported as measured current axes. | P2 | Independent scientific route and gate review before canonical admission. |
| SOUNDER | The 2004 source describes component regions, not these coordinates. | P3 | Paragraph locators, source citation, retrieval date and coordinate role preserved. |
| SOUNDER | Alternate regional gates are OSW assumptions. | P3 | Alternative interpretations explicitly state they are not published termination coordinates. |
| SOUNDER | Rounded envelopes cannot imply probabilities. | P3 | Catalog and UI state finite independent envelope interpretation. |
| CHART | Initial Leeuwin Bight chords crossed coarse land. | P3 | Moved offshore before retention; every retained scenario passes the mask. |
| CHART | Coarse clearance does not establish shelf-edge alignment. | P2 | Bathymetric/velocity correspondence required before scientific admission. |
| CHART | Initial Leeuwin start label overlapped the header. | P3 | Expanded northern viewport; inspect regenerated figure. |
| BEACON | The system's 5,500 km does not belong to Leeuwin alone. | P3 | Separate system measurement and component scopes in page and documentation. |
| BEACON | Component routes cannot be added without handling gaps/overlaps. | P3 | Explicitly state routes are not a system partition; no total computed. |
| BEACON | Adjacent nominal ordering hides overlapping envelopes. | P3 | Add conservative position bounds and links to overlapping routes. |
| HARBOR | Ordering sensitivity needs a textual representation. | P3 | Dedicated table column and native details/links provide equivalent access. |
| HARBOR | Enlarged maps need full-size access and endpoint text. | P3 | Existing full-size links and adjacent source/scope/JSON retained. |
| HARBOR | New wide table could overflow mobile page. | P3 | Retain table scroll wrapper; check 320 px page reflow. |
| KEEL | Endpoint ties and nested ranges need deterministic semantics. | P3 | Three focused tests cover disjoint, touching/nested/equal envelopes and excluded reaches. |
| KEEL | New overlap links break name-based row matching. | P3 | Give comparison rows stable IDs and use them in browser checks. |
| KEEL | Candidate numerical outputs need coverage beyond nominal values. | P3 | Recompute all 675 retained scenarios and verify input hashes. |
| LOGBOOK | Current inventory claims must match catalog. | P3 | Reconcile eleven candidates, ten currents and 79 unbuilt records. |
| LOGBOOK | Historical progress paragraphs can appear current. | P3 | Mark plan progress entries chronological and add current header count. |
| LOGBOOK | Role review alone cannot authorize public data admission. | P2 | Scientific review, canonical integration and publication review remain open. |

Roles reviewed: 7. Findings: 21. P1: 0; P2: 3; P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for local review. Top condition: independent
scientific route review. CURRENT, SOUNDER and BEACON agree that component
naming and endpoint assumptions must accompany every length. Amendments:
reject land-crossing sketches, reconcile seasonal component scopes, and expose
overlap sensitivity without suggesting an empirical rank distribution.

Verification record: candidate/catalog builds; four geodesic tests; three
ordering tests; independent recomputation/hash checks for all 675 scenarios.
All three maps inspected; adjusted Leeuwin viewport inspected again. A byte-identical
rebuild of the three candidates and full catalog passed. Full browser test
passed with new card values, ordering details, stable IDs, filters, map loading
and 320 px reflow. The almanac checker passed. These checks do not establish
a physical current axis.
