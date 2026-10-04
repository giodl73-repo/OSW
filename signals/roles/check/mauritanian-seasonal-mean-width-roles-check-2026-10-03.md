---
skill: roles-check
topic: mauritanian-seasonal-mean-width
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Mauritanian seasonal mean width review

Internal editorial review. CURRENT for physical support, SOUNDER for averaging
provenance, CHART for section/extent meaning, BEACON for range labels, HARBOR
for equivalent access, KEEL for schema/hash compatibility, LOGBOOK for status.
ORBIT not applicable. Reviewed primary text/captions, audit/width protocol,
input inventory, explorer/table rendering, generated dashboard and checks.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Mean width span could imply instantaneous width variability | P3 | Explicit mean-section definition; no annual/uncertainty inference. |
| CURRENT | Surface equatorward jet could imply reversal of whole MC | P3 | Source naming separates opposing shelf jet from poleward manifestations. |
| CURRENT | Core depths could become fixed-depth width bounds | P3 | Context only; fixed-depth bounds and paired edges null. |
| SOUNDER | Study-wide years differ from upwelling sample years | P3 | 2005–2016 study versus five 2005–2011 cruise support retained. |
| SOUNDER | Season label includes an unsampled month | P3 | December convention separated from January–April sampled months. |
| SOUNDER | August cruise could be included in seasonal mean | P3 | Excluded M129 retained in audit/quality note. |
| CHART | Latitude pooling could become current endpoints | P3 | 17–19 N pooling typed separately; no route constructed. |
| CHART | Transport or surface corridor could become width | P3 | 60 km and 200 km contexts explicitly excluded. |
| CHART | Reported interval could generate occupied area | P3 | No edges, geometry or buffer added. |
| BEACON | Generic range label would imply typical annual span | P2 (addressed) | Seasonal-mean title/value/table wording added. |
| BEACON | Midpoint could look like a measured scalar | P3 | Representative remains null; no midpoint chosen. |
| BEACON | Single recorded mean could imply seasonal animation | P3 | Play disabled and remaining-season widths unresolved. |
| HARBOR | Width meaning must survive absence of bar | P3 | Plain-text range, season/layer/sampling and exclusions. |
| HARBOR | Switching current could leave bar or route behind | P3 | Northern-to-Mauritanian switch checked. |
| HARBOR | Long source details must reflow | P3 | Focused mobile and all 32 scope previews pass. |
| KEEL | New calendar class was rejected by shared gate | P2 (addressed) | Gate extended specifically; full validation now passes. |
| KEEL | Mean definition and sampling could drift | P3 | Mutation tests reject relabel, invented scalar, playback and incompatible support. |
| KEEL | New inventory bytes invalidate seasonal provenance | P3 | Width/association hashes refreshed and both validators pass. |
| LOGBOOK | New evidence could silently alter canonical rank | P3 | Editorial width only; canonical SHA unchanged. |
| LOGBOOK | Full source claim could imply fields were acquired | P3 | HTML access limits and no digitization recorded. |
| LOGBOOK | Focused checks cannot prove full scientific release | P3 | Independent admission and clean-checkout release gate remain open. |

21 findings: no P1, two addressed P2, 19 P3 conditions. Approved for editorial
inspection. CURRENT/SOUNDER/BEACON agree that width of a mean section must not
be labelled mean instantaneous width or annual extremes. Amendments: introduced
explicit seasonal-mean range evidence with sampling support; separated opposing
flows and integration domains; repaired type-specific calendar gate and display.
Sixteen width, twelve dashboard and four seasonal-frame tests; full 18-width /
six-frame validators; 32 scope previews and focused browser pass. Canonical
ledger unchanged. Paired boundary extraction, other seasons, along-coast axes,
independent measurement admission and full clean-checkout release remain open.
