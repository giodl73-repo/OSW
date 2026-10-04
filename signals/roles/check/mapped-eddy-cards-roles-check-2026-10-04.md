---
skill: roles-check
topic: mapped-eddy-cards
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Mapped eddy cards: internal editorial review

Artifact: reference-route-atlas.js eddy selection and styles, browser verifier,
repository status. CURRENT/SOUNDER cover physical scope and provenance;
CHART/BEACON/HARBOR cover rendering, explanation and access; KEEL/LOGBOOK
cover verification and inventory fidelity. ORBIT excluded: no planetary analogy.
Internal role perspectives do not constitute independent scientific admission.

| Role | Finding | Severity | Section / resolution |
|---|---|---|---|
| CURRENT | Point cannot establish material extent. | P3 verified | chooseEddy retains locator/center/gateway explanation. |
| CURRENT | A stored outline cannot imply live extent. | P3 condition | Historical status and observation date remain beside map. |
| CURRENT | A contour proxy differs from provider polygon. | P3 verified | Existing role-specific description retained. |
| SOUNDER | Map must use stored geometry without new inference. | P3 verified | Original coordinates projected directly; no buffer/radius/trajectory. |
| SOUNDER | Shared gateway must remain shared. | P3 verified | Point reused; explicit no-individual-center explanation. |
| SOUNDER | State relations must retain their receipt and date. | P3 verified | All 131 scoped links reconcile with pinned release records. |
| CHART | Coarse state shading overwhelms a small outline. | P2 resolved | Small views use existing coastline layer without state shading. |
| CHART | Local card geometry might clip. | P3 verified | All outline bounds and point coordinates inside selected extent. |
| CHART | Card must not shift with main-map pan/zoom. | P3 verified | Captured extent independent; zoom browser check. |
| BEACON | Name locator and dated shape need different wording. | P3 verified | Selected explanation appears beside map and in accessible label. |
| BEACON | Source record should be reachable from visual. | P3 verified | Existing record link and state receipts retained. |
| BEACON | Inventory updates could be mistaken for live movement. | P3 condition | Existing baseline explanation retained; no playback added. |
| HARBOR | Hidden names must be recoverable without pointer. | P3 verified | Focus exposes name and gives accessible description. |
| HARBOR | Color alone cannot convey changed record. | P2 resolved | Amber border accompanied by textual update description. |
| HARBOR | Card should reflow on narrow viewport. | P3 verified | Responsive SVG and 320 px document check. |
| KEEL | An updated record must not light unrelated card. | P3 verified | Synthetic Kraken baseline change isolates updated map border. |
| KEEL | Saved links and reset must preserve/clear card correctly. | P3 verified | Reload restoration and Global-view disposal checked. |
| KEEL | Narrow verification cannot prove release readiness. | P3 condition | Focused 140-card browser only; full repository suite not rerun. |
| LOGBOOK | Display change must not inflate scientific inventory. | P3 verified | Canonical SHA256 unchanged; no geometry/measurement admission. |
| LOGBOOK | Status must include reproducible verification command. | P3 verified | README and coverage plan name focused browser verifier. |
| LOGBOOK | Screenshot alone cannot prove all inventory cards. | P3 verified | One visual inspection plus exhaustive 140 selections and 131 links. |

## Synthesis and amendments

Seven roles, 21 findings: zero P1, two addressed P2, 19 P3 verified notes or
conditions. APPROVED-WITH-CONDITIONS for local atlas presentation. CURRENT,
SOUNDER and CHART agree that a locator or contour retains its evidence scope.

Three amendments: reuse stored geometry with distinct role descriptions;
remove coarse state shading in small outline views; provide keyboard names
and text alongside amber update borders. Focused browser passes all 140 maps,
131 state links, restoration, zoom/reset, update isolation and mobile reflow.
Updated outline screenshot inspected. Independent scientific review and release
gates remain open; no claim of full-repository verification or publication.
