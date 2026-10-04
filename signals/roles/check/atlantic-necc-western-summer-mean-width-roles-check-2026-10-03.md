---
skill: roles-check
topic: atlantic-necc-western-summer-mean-width
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Atlantic NECC studied reach and mean-field widths

Internal installed-role review, not independent scientific approval. Reviewed
source sections, input/candidate, width protocol and inventory, validator,
rendered card and browser evidence. Seven lenses cover physics, provenance,
map semantics, explanation, access, engineering and status; ORBIT not applicable.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Source fall merging cannot define summer branch topology | P2 | Removed transfer; summer branch correspondence explicitly unresolved. |
| CURRENT | Study gates are not whole-current endpoints | P3 | 42 W and 32 W bound a studied reach only. |
| CURRENT | Mean-flow band is not one branch width | P3 | Two mean section bands remain separate from selected summer route. |
| SOUNDER | Latitude choices must not look field-derived | P3 | All latitude gates and bends visibly editorial; no source digitization. |
| SOUNDER | Prose and HTML table numbers disagree | P3 | Locator identifies width paragraphs and records numbering discrepancy. |
| SOUNDER | Failed table download cannot count as inspected table | P3 | Width values checked in accessible prose; access receipt explicit. |
| CHART | Scenario envelope is not annual variation | P3 | 81 cases retained as selected assumptions only. |
| CHART | GUIA scenario-only contact could imply nominal passage | P3 | 18/81 GUIA versus 81/81 nominal WTRA separately displayed. |
| CHART | Map endpoint labels collided with short route | P3 | Shortened labels and increased figure text size; screenshot inspected. |
| BEACON | Mean width could become seasonal width interval | P2 | New mean_velocity_section type and v1.7 rule prohibit seasonal span/playback. |
| BEACON | Width after averaging differs from averaged widths | P3 | Definition stored, validated and displayed explicitly. |
| BEACON | Source season convention must remain exact | P3 | Summer JAS retained; no standard-calendar reassignment. |
| HARBOR | New route needs direct global-map card navigation | P3 | Exact atlas selection and inline map pass focused check. |
| HARBOR | Section controls need usable narrow layout | P3 | Both mean sections and route pass 320 px checks. |
| HARBOR | Different section locations must not autoplay as seasons | P3 | Playback disabled; selectable evidence remains accessible. |
| KEEL | Validator must reject temporal/boundary relabeling | P3 | New mutation tests reject invented annual ranges and changed averaging order. |
| KEEL | Regeneration must preserve scope and provenance | P3 | Full route audit and width validation pass; ledger hash unchanged. |
| KEEL | New data needs joins and preview regression coverage | P3 | All 112 route/state links and 23 source-preview cards pass. |
| LOGBOOK | Studied reach cannot enter comparable whole-length ranking | P3 | Excluded from reference-route ordering and published ranking. |
| LOGBOOK | Coverage counts must distinguish route and width progress | P3 | 54 of 89 / 35 pending; 15 scoped widths for 11 names. |
| LOGBOOK | Internal review is not science admission | P3 | Canonical and independent branch/axis review gates remain open. |

21 findings: 0 P1, 2 addressed P2, 19 P3 conditions. Approved for editorial
inspection; summer axis, branch and compatible monthly-width review still
required. CURRENT and BEACON agree that mean section bands do not supply a
summer-route width or annual extrema.

Evidence: 36 focused dashboard/width/catalog/route-generator unit tests;
complete route v1.2 audit, 56 candidates / 3951 scenarios; width v1.7 validation,
15 records / 11 names. Focused browser checks cover route, source calendar,
both mean sections, no seasonal playback, mobile and no date/rank transfer.
All 112 route/state links and all 23 source previews pass. Screenshot inspected:
figures/atlantic-necc-western-summer-review.png. Headless Chromium 1223 used.
No whole-repository-suite claim or scientific release mutation.
