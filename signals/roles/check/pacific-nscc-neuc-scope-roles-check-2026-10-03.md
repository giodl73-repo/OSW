---
skill: roles-check
topic: pacific-nscc-neuc-scope
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Northern Tsuchiya reach and NEUC identity scope

Internal installed role review, not independent scientific approval. Seven
lenses cover physics, source support, mapping, explanation, access, engineering
and repository status. ORBIT does not apply.

| Role | Finding | Severity | Section | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | Similar subsurface names could acquire the same length | P2 | Identity | 130 E NEUC stays route-pending; northern Tsuchiya section support separate. |
| CURRENT | Local core depths are not uniform axis depth | P3 | Layer | 220 m/130 m qualified as local mean supports. |
| CURRENT | Two section cores do not establish a dated material trajectory | P3 | Scope | Editorial interpolation and truncation explicitly stated. |
| SOUNDER | Transport latitude bounds could be presented as width | P2 | Audit | Integration bands retained separately; width remains unresolved. |
| SOUNDER | Source compilation years cannot date the route | P3 | Time | 1967-1996 context only; observation period and dashboard latest date null. |
| SOUNDER | A geostrophic reference depth is not the core layer | P3 | Audit | 700-dbar reference separately identified; no axis-depth transfer. |
| CHART | Whole-Pacific extent is longer than the selected reach | P3 | Gates | 155 W/110 W are truncations; formation and eastern continuation excluded. |
| CHART | Scenario spread can resemble occupied footprint | P3 | Figure | Editorial scenario linework and no-width interpretation retained. |
| CHART | Surface NASA imagery cannot identify this subsurface jet | P3 | Context | Reference route/crop display overlap remains separate from flow identification. |
| BEACON | The 5000 km estimate might be repeated without its scope | P3 | Preview | Studied reach label and exclusions beside figure. |
| BEACON | A weak mean is not necessarily weak synoptic flow | P3 | Source | Later Johnson et al. source retained as context; no time-resolved field claim. |
| BEACON | Shared terminology could overstate proven distinct trajectories | P3 | Naming receipt | Different source support recorded; no connecting trajectory or canonical alias decision. |
| HARBOR | Selected subsurface identity must be readable without palette | P3 | Card | Name, depth, scope and remaining gates given in text. |
| HARBOR | Narrow viewport must preserve pending/mapped difference | P3 | Browser | Both cards checked at 320 px without horizontal overflow. |
| HARBOR | Return from a selected feature must remain available | P3 | Navigation | Global reset tested; existing keyboard/selectors retained. |
| KEEL | New route needs complete assumption-grid audit | P3 | Protocol | All 54 candidates/3789 scenarios validate under v1.2; generator unchanged. |
| KEEL | Neighboring identity must not gain route or width capabilities | P3 | Focused test | NEUC route/width zero, NSCC width zero and date null verified. |
| KEEL | Additional joins could break existing navigation | P3 | State browser | All 108 route/state links and fallback checked. |
| LOGBOOK | Candidate and current counts differ | P3 | Status | 54 candidates/52 of 89 names/37 pending; 15 studied reaches. |
| LOGBOOK | Source rights should follow the actual notice | P3 | Rights | NOAA page U.S. copyright notice recorded; no source assets copied. |
| LOGBOOK | Editorial review is not release admission | P3 | Ledger | Canonical hash unchanged; source/axis science review remains open. |

21 findings: 0 P1, 2 P2 addressed for editorial inspection, 19 P3 conditions.
Approved with conditions: review interpolation and complete extent, obtain
month/depth axes, and resolve branch-specific NEUC geometry. CURRENT and
SOUNDER agree that shared eastward subsurface descriptions cannot transfer
dimensions across identities.

Amendments: preserve distinct source supports, retain local depths without a
uniform-axis inference, and separate transport integration bounds from width.
Evidence: relevant Johnson and Moore (1997) sections 1-3/Table 1, Johnson et
al. (2002) naming context and the NEUC mooring study mean-structure paragraphs;
21 focused unit tests; analysis/test_pacific_nscc_reach_browser.py; all 108
route/state links. Screenshot inspected:
figures/pacific-nscc-reach-reference-path-review.png. No full repo suite claim.
