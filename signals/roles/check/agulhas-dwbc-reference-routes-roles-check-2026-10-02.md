---
skill: roles-check
topic: agulhas-dwbc-reference-routes
date: 2026-10-02
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Agulhas regional extent and DWBC studied reach

Internal review of two editorial inputs/outputs, figures, catalog, documentation
and browser expectations. Roles selected for physical scope (CURRENT), source
provenance (SOUNDER), mapping (CHART), explanation (BEACON), accessibility
(HARBOR), calculation (KEEL) and repository status (LOGBOOK). ORBIT excluded
because no planetary analogy is involved. This is a role-lens audit, not
independent scientific approval.

| Role | Finding | Severity | Amendment/condition |
| --- | --- | --- | --- |
| CURRENT | Agulhas 27–40 S scope is regional and includes the approach to retroflection. | P3 | State regional convention and exclude a claim of the narrower coastal jet's length. |
| CURRENT | DWBC deep interfaces vary across sections; linking them assumes continuity. | P3 | Preserve section-specific depths and explicit continuity assumption. |
| CURRENT | Neither route reconstructs a physical axis. | P2 | Independent oceanographic review required before admission. |
| SOUNDER | Sources constrain geography rather than editorial coordinates. | P3 | Source locators and coordinate-selection statements retained. |
| SOUNDER | Finite offset ranges are not measured errors. | P3 | Download all 81/27 scenarios and retain assumption language. |
| SOUNDER | Source geography may change when refreshed. | P3 | Retrieval dates recorded; source/input/map/tile roles distinguished. |
| CHART | Surface land clearance cannot validate deep bathymetric paths. | P2 | Require layer-specific bathymetric/velocity correspondence before admission. |
| CHART | DWBC map initially omitted the northern gate. | P3 | Corrected view box; inspected complete route and endpoints. |
| CHART | Long Agulhas source label could clip. | P3 | Shortened figure citation; full citation remains in adjacent page text. |
| BEACON | DWBC studied reach could be mistaken for a whole-current length. | P3 | Excluded from comparison ordering, with warning in its card. |
| BEACON | Agulhas and Agulhas Return have separate conventions. | P3 | Agulhas stops at turning gate; explicit return-current exclusion. |
| BEACON | Seven candidate-covered currents does not mean 89 lengths completed. | P3 | State eight candidates, seven currents and 82 awaiting routes. |
| HARBOR | Map colour alone cannot convey candidate scope. | P3 | Text, dashed route, alt descriptions, endpoints and JSON alternatives retained. |
| HARBOR | Mobile cards must retain source and method access. | P3 | Browser checks passed at 320 px without page overflow. |
| HARBOR | New maps need equivalent readable evidence. | P3 | Full-size SVG links and adjacent scope/scenario/layer/source text retained. |
| KEEL | Calculation needs verification for all retained scenarios. | P3 | Recomputed distances independently from stored vertices for all eight candidates. |
| KEEL | Input changes could leave stale catalog records. | P3 | Rebuilt both candidates and catalog; input hashes verified. |
| KEEL | Studied reaches must stay outside provisional comparison. | P3 | Browser asserts DWBC absent from reference ordering and warning present. |
| LOGBOOK | Existing published ranks and floors carry different evidence. | P3 | Canonical ranking unchanged; plan separates original geographic floors. |
| LOGBOOK | Current coverage needs consistent documentation. | P3 | README, plan, catalog and browser expectations reconciled. |
| LOGBOOK | Internal candidate approval is insufficient for canonical publication. | P2 | Scientific review, canonical integration and publication review remain open. |

Roles reviewed: 7. Findings: 21. P1: 0; P2: 3; P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for internal review. Top condition: scientific
axis review. CURRENT, CHART and BEACON agree that deep reach and regional
extent must remain visible beside every number. Three amendments applied:
correct DWBC viewport, shorten the Agulhas figure citation, and exclude DWBC
from reference ordering while reconciling coverage counts.

Verification: both candidate builds and catalog build; four numerical tests;
all-scenario recomputation and input-hash checks; full Chromium atlas test
including new values, studied-reach warning, filters, figure loading and
320 px reflow; both new figures visually inspected.
