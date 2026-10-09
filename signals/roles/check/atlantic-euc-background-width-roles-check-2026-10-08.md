---
skill: roles-check
topic: atlantic-euc-background-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal functional review

Seven installed roles review source evidence, dimensions, data binding, display,
acquisition and publication. ORBIT is excluded because no analogy is used.
Internal review is not independent scientific admission.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | 200 km is a background approximation, not a computed campaign width. | P2 | Original p16 | Regional summary point; no new contour calculation. Addressed. |
| CURRENT | Thickness/core depths do not define the width layer. | P2 | Source paragraph | Fixed layer null; context exclusions explicit. Addressed. |
| CURRENT | Core displacement is not width change. | P2 | Original p16 | Oscillation cannot become width interval/error. Addressed. |
| SOUNDER | The English OCR lead alone lacked original verification. | P2 | Source access | Complete French original pinned and passage visually inspected. Addressed. |
| SOUNDER | French/English versions are not independent samples. | P2 | Source context | One 1988 source point; translation flag false. Addressed. |
| SOUNDER | Historical paired-boundary support remains unknown. | P3 | Protocol | Retained scientific gate; no boundary method invented. |
| CHART | A point must not be drawn as a confidence range. | P2 | Chart | Single approximate point, null uncertainty/interval. Addressed. |
| CHART | No paired edges can support route buffering. | P2 | Geometry | Geometry null, no occupied state footprint. Addressed. |
| CHART | Mobile point labels must stay readable and in bounds. | P2 | Browser check | Existing end-aligned label; 320 px bounds/readability check. Addressed. |
| BEACON | Background and campaign width require different wording. | P2 | Current card | Campaign-width unknown separate from background summary. Addressed. |
| BEACON | Pacific and generic family must not inherit the Atlantic value. | P2 | Owner / guards | Basin owner binding and coherent native mutation checks. Addressed. |
| BEACON | Dated figures could be misread as seasonal 200 km samples. | P2 | Caption / protocol | Background dates null, playback disabled. Addressed. |
| HARBOR | Chart requires semantic description and source access. | P2 | Inspector / atlas | Existing accessible chart, source query and method text reused. Addressed. |
| HARBOR | Point value alone hides unknown uncertainty. | P2 | Caption | Unknowns included beside value. Addressed. |
| HARBOR | A reader needs campaign context separately. | P2 | Current card | Eight-record table and conflict charts retained. Addressed. |
| KEEL | Book acquisition filename could permit path escape. | P2 | Acquisition helper | Only two fixed basenames allowed; pre-fetch path mutation test. Addressed. |
| KEEL | Ignored original must remain strictly verified. | P2 | Python / hydration | Hash and source bytes required; explicit existing helper adds one pin. Addressed. |
| KEEL | Remote acquisition is currently failing for an existing source. | P3 | Publication | Protected checks remain required; do not claim CI green. |
| LOGBOOK | Copyright forbids assuming redistribution permission. | P2 | Acquisition | Whole book ignored; metadata/extraction only shipped. Addressed. |
| LOGBOOK | Counts must reflect evidence scope. | P2 | Inventory | 93 records / 49 owners; no full-current dimension admission. Addressed. |
| LOGBOOK | Independent scientific admission is outstanding. | P3 | Status | Explicit gate; draft is not official admission. |

Roles reviewed: 7. P1 blockers: 0. P2 issues: 18 addressed. P3 notes: 3 remain.
Verdict: APPROVED-WITH-CONDITIONS.

Top finding: neither the dated sections nor the later translation supplies
dated 200 km measurements. CURRENT, SOUNDER and BEACON agree. Amendments:
inspect/pin the original; preserve all support exclusions; keep source point
display and basin ownership separate from campaign charts and generic families.
