---
skill: roles-check
topic: seasonal-atlas-navigation
date: 2026-10-04
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 1
verdict: APPROVED-WITH-CONDITIONS
---
# Atlas and seasonal evidence navigation

Internal editorial review through seven installed roles: CURRENT for physical
meaning, SOUNDER for record identity, CHART for mapped component, BEACON for
labels, HARBOR for controls/reflow, KEEL for browser compatibility, LOGBOOK for
status. ORBIT not applicable. Reviewed browser source, navigation tests,
record/frame mappings, mobile rendering and retained evidence restrictions.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Evidence link could imply complete seasonal geometry | P3 | Unknowns and playback eligibility unchanged. |
| CURRENT | Wrong seasonal route could imply wrong direction | P3 | Winter Monsoon opens matching winter frame. |
| CURRENT | Width and route might be conflated by return link | P3 | Return route parameter only for an associated route frame. |
| SOUNDER | Phase array index is unstable as records grow | P3 | URLs use stable width/frame/direction IDs. |
| SOUNDER | Cross-current phase could borrow evidence | P3 | Phase lookup scoped to current; invalid choice normalized. |
| SOUNDER | Navigation edit must not change numeric evidence | P3 | Only browser files/test/docs changed; canonical SHA unchanged. |
| CHART | Return to map could select another regional component | P3 | Six seasonal returns retain exact atlas route. |
| CHART | Pending axis could appear mapped after evidence navigation | P3 | Unknown current test retains no supported phase. |
| CHART | Optional evidence fetch could block route/state views | P3 | Optional frame fallback and existing state fallback checked. |
| BEACON | Seasonal links existed only for two named currents | P2 (addressed) | Generic evidence link now covers all previews/cards. |
| BEACON | Single width observation could look playable | P3 | Evidence wording avoids promising playback; eligibility retained. |
| BEACON | Readers need a usable recorded-view URL | P3 | Visible link tracks selected evidence ID. |
| HARBOR | Return/share controls must fit narrow view | P3 | 320 px reflow and screenshot checked. |
| HARBOR | State selection must remain keyboard-operable | P3 | Native selects/anchors retained. |
| HARBOR | Navigation should not erase scientific limits | P3 | Existing textual unknowns and mean/axis definitions remain. |
| KEEL | Multiple callbacks could break direct arrival | P3 | Existing mapped/proposal delayed-load checks pass. |
| KEEL | Only one example would under-cover link mapping | P3 | All 100/62 links and 26 record IDs checked. |
| KEEL | Playback URL changes could flood history | P3 | replaceState used; no added entries per frame. |
| LOGBOOK | New link count could be called new science coverage | P3 | Existing records only; no evidence-count increase. |
| LOGBOOK | Focused checks cannot prove full repository release | P3 | Full clean-checkout release gate remains open. |
| LOGBOOK | Roles review could imply independent approval | P3 | Internal editorial conditions stated. |

21 findings: no P1, one addressed P2, 20 P3 conditions. Approved for editorial
inspection. CURRENT/CHART agree that a recorded seasonal phase must return to
its own route component, not a different first-listed component. Amendments:
added evidence links throughout the atlas/cards; added stable phase share URLs;
added current/route-preserving return links and invalid-phase reset.
Verification: 100 atlas and 62 card addresses, 26 evidence IDs, six route-frame
round trips, two existing route deep links, all 23 proposal/history paths,
124 state links, optional-data fallback and mobile screenshot. Source data and
canonical ledger untouched. Independent scientific admission and full repository
release gates remain outstanding.
