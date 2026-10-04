---
skill: roles-check
topic: indian-euc-dated-band
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Indian EUC dated subsurface band review

Internal review of source text, width record, v1.8 protocol, validator, source
audit, seasonal view and atlas disclosure. Seven installed lenses selected for
physics, provenance, map meaning, explanation, access, reproducibility and
status. ORBIT is not applicable. Not independent scientific admission.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | A descriptive saline/velocity band could become full current width | P2 | New metric retains band interpretation; no velocity threshold or paired edges claimed. |
| CURRENT | 80–150 m support could imply width at every depth | P2 | Depth range stored separately; fixed axis layer null and full-width inference false. |
| CURRENT | Historical longitudes could become one connected basin axis | P3 | No route constructed; matching profiles and overlying flow required. |
| SOUNDER | Survey support differs from reported strong-flow band | P3 | 2 S–2 N survey retained separately from 1.2 S–1.5 N band. |
| SOUNDER | Day precision needs explicit campaign support | P3 | Methods gives 1–3 March 2017; source locator and dates retained. |
| SOUNDER | Review's earlier original sources are not directly inspected | P3 | Taft source remains indirect; 2001 review access distinguished from original campaigns. |
| CHART | Span could become a mapped current polygon | P3 | Section geometry null; no width buffer or occupied footprint. |
| CHART | Meridional span could imply flow-normal width | P3 | Section orientation explicit; no exact flow-normal reinterpretation. |
| CHART | Display bar could imply full width | P3 | Full-width bar omitted for this metric. |
| BEACON | About 300 km needs a visible definition | P3 | Seasonal text and width table say described subsurface band span. |
| BEACON | Eastward velocity alone may not define an undercurrent | P3 | Audit retains dependence on overlying flow and historical definition. |
| BEACON | One March section could become annual seasonality | P3 | Playback disabled; annual length/width remain null. |
| HARBOR | Local metric must be readable without a map | P3 | Dates, depth, span and source presented as text. |
| HARBOR | Narrow layout must retain boundary meaning | P3 | 320 px seasonal and atlas reflow passed. |
| HARBOR | Global atlas must expose the new source review | P3 | Exact deep link and summary verified, no borrowed route. |
| KEEL | Conversion must be recomputable | P3 | WGS84 raw 298.5511199778176 km, rounded to 10 km; validator recomputes. |
| KEEL | Assumed thresholds and layered full-width claims need guards | P3 | Mutations reject threshold, paired edges, uniform layer and full-width relabeling. |
| KEEL | Width protocol change affects dependent frame receipts | P3 | Protocol hash and width SHA in frame document refreshed; five frames validate. |
| LOGBOOK | Counts must distinguish records, names and routes | P3 | 16/12 width records/names, 29 reviews; routes unchanged at 60/57. |
| LOGBOOK | Dated evidence must not imply current-year conditions | P3 | 2017 date displayed; historical section and broader geometry unresolved. |
| LOGBOOK | Internal review cannot admit a canonical width | P3 | Editorial status, remaining scientific gates and unchanged ledger/ranks retained. |

21 findings: 0 P1, 2 addressed P2, 19 P3 conditions. Approved for editorial
inspection. CURRENT, CHART and BEACON agree that a descriptive depth-range
band is a local metric rather than complete current width or an annual phase.

Amendments: created a distinct reusable band metric; enforced source limits,
dates, numerical conversion and inference exclusions; updated visible labels
and omitted the full-width bar.

Verification: 28 focused width/dashboard/seasonal-frame unit tests (14/10/4),
complete width inventory and route audits, five-frame receipt check, focused
dated-band browser checks and all 29 source cards. Browser test selector repaired
after targeting a nonexistent table ID; final check passed against actual rows.
Screenshot inspected: figures/indian-euc-dated-band-review.png. No complete
repository suite, independent approval, source figure digitization or publication.
