---
skill: roles-check
topic: azores-section-widths
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Azores dated-section width evidence

Seven relevant installed .roles lenses; ORBIT excluded without planetary
analogy. Internal audit is not independent scientific approval. Scope:
width inventory, temporal/section validation, adapted UI, tests and docs.

| Role | Finding | Severity | Amendment or remaining condition |
| --- | --- | --- | --- |
| CURRENT | Meridional spans are not automatically perpendicular-flow widths. | P2 | Preserve metric/orientation; scientific section definition review remains. |
| CURRENT | One survey cannot define an annual seasonal cycle. | P3 | Dated section type; no annual extrema or uncertainty range. |
| CURRENT | Depth extent does not imply constant width at all depths. | P3 | Layer text preserves vertical support and nonuniformity. |
| SOUNDER | Caption date differs from explicit data text. | P2 | 2009 chosen from station dates; 2010 caption discrepancy retained for review. |
| SOUNDER | Rounded 110 km should not become a recomputed exact span. | P3 | Source value retained; coordinates not substituted as new width estimate. |
| SOUNDER | AzCC surface altimetry can miss subsurface flow. | P3 | Subsurface evidence and sensor limitation explicit. |
| CHART | Section endpoints are not an occupied-current polygon. | P3 | Section geometry role explicit; no width-derived state/footprint join. |
| CHART | A fixed 50 km bar would clip 110 km. | P3 | Labelled dynamic scale grows to 150 km. |
| CHART | Coastwise route context is not available for these names yet. | P3 | Unknown route remains hidden; no guessed axis drawn. |
| BEACON | Hardcoded regional-summary label misdescribes dated observations. | P3 | Evidence type and section orientation displayed per record. |
| BEACON | Short phase labels could hide actual dates. | P3 | Explicit date label and full observation period in explorer. |
| BEACON | Extra records could exaggerate inventory completion. | P3 | Four records/three names/two pending/95 unassessed visible. |
| HARBOR | Single snapshot should not imply animation. | P3 | Playback disabled; one dated phase labelled. |
| HARBOR | Magnitude should remain available without colour. | P3 | Numeric value and bar scale text retained. |
| HARBOR | New definitions must remain readable on mobile. | P3 | Full browser suite covers 320 px explorer/review reflow. |
| KEEL | Dated section should not be relabelled core or seasonal summary. | P3 | Validator checks type, metric and temporal evidence. |
| KEEL | Section geometry and dates need valid ordering. | P3 | Negative tests reject changed orientation and reversed dates. |
| KEEL | Expanded records must preserve identity coverage. | P3 | 100 decisions and four unique records validated. |
| LOGBOOK | New evidence needs retrieval date and specific locator. | P3 | Full publisher text read; 2026-10-03 and data/domain passages recorded. |
| LOGBOOK | Width extension must remain distinct from canonical release. | P2 | Nonrepresentative/nonranked editorial records; admission review remains. |
| LOGBOOK | Current counts need consistent documentation. | P3 | README/method plan updated; initial versioned protocol describes initial pilot. |

Seven roles, 21 findings, zero P1, three P2, eighteen P3.
APPROVED-WITH-CONDITIONS for local editorial evidence collection. Key
amendments: preserve meridional section metric; record caption date conflict;
adapt numeric scale and single-snapshot presentation. Independent scientific
section/provenance and canonical-release gates remain open.

Verification: 23 focused tests and width inventory checker pass. Full Chromium
browser suite passes new record counts, dates/metric, 110 km display, 150 km
scale, date-conflict text, disabled single-state playback and unknown annual
range alongside prior seasonal-map and mobile checks. Azores explorer screenshot visually inspected; numeric scale, dated label and
unknown route context are legible. Full almanac, route-protocol and seasonal-frame
audits also pass. Caption date issue remains an open review condition.
