---
skill: roles-check
topic: kuroshio-extension-width
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal functional review

Seven installed roles review physical scope, provenance, visual meaning,
accessibility, reproducibility and publication. ORBIT is excluded because no
analogy is used. Internal review is not independent scientific admission.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | Meridional width is not automatically flow-normal breadth. | P2 | p445 / protocol | Orientation explicit; no normal-width conversion. Addressed. |
| CURRENT | Monthly mean and climatological scales differ in support. | P2 | p445 / audit | 100 km width point; 200 km separate scale context. Addressed. |
| CURRENT | Jet displacement and steric seasonality are different variables. | P2 | pp444–445 | No width variation inferred from either. Addressed. |
| SOUNDER | January 2005 is an illustrative field date. | P2 | Figure 1b | Figure date context preserved; width occupation/month membership null. Addressed. |
| SOUNDER | Analysis interval, grid and smoothing need separate provenance. | P2 | Data section | AVISO 1993–2010, 1/3° Mercator and low-pass context stored separately. Addressed. |
| SOUNDER | Paired width boundary rule is unresolved. | P3 | Source method | Scientific gate retained; axis method does not resolve it. |
| CHART | A 100–200 km bar would imply unsupported variation. | P2 | Chart | One approximate point; contextual scale in adjacent explanation. Addressed. |
| CHART | SSH contour search is not occupied width geometry. | P2 | p444 methods | No route buffer, edges or state footprint. Addressed. |
| CHART | Mobile labels can clip. | P2 | Browser check | Check 320 px readability, label bounds and page overflow. Addressed by registered check. |
| BEACON | Monthly mean can sound like monthly observations. | P2 | Caption / aria | Explicitly state no dated width series extracted. Addressed. |
| BEACON | Different geographic supports must remain visible. | P2 | Method note | Date-line monthly jet versus Japan–165°E climatological scale. Addressed. |
| BEACON | Unknown uncertainty must accompany the point. | P2 | Caption | Null numerical uncertainty stated beside value. Addressed. |
| HARBOR | Chart needs a text equivalent. | P2 | SVG / caption | Metric, time operator and unknowns in aria and visible text. Addressed. |
| HARBOR | Meaning must not depend on color. | P2 | Point display | Numeric km labels and scope text supplied. Addressed. |
| HARBOR | Source access needs a direct path. | P2 | Current card | Source query link preserves complete measurement context. Addressed. |
| KEEL | Changed coherent receipts could bypass source rules. | P2 | Rust guard / tests | Compiled whole-record binding; coherent mutation tests retain rejection. Addressed. |
| KEEL | Original must be verified without weakening defaults. | P2 | Acquisition / Python | Complete source SHA and bytes pinned; ignored hydration explicit. Addressed. |
| KEEL | Existing CI source timeouts persist. | P3 | PR55 | Original download timed out at Qiu/Chen before tests; protected gates retained. |
| LOGBOOK | AMS copyright does not authorize electronic republication. | P2 | Institutional cover | Original ignored; metadata/extraction only tracked. Addressed. |
| LOGBOOK | Contextual scale must not inflate width counts. | P2 | Inventory | One new width record: 94 records / 50 owners / 42 unassessed. Addressed. |
| LOGBOOK | Editorial review is not official admission. | P3 | Status | Scientific admission pending; draft publication. |

Roles reviewed: 7. P1 blockers: 0. P2 issues: 18 addressed through data,
display and executable checks. P3 notes: 3 remain. Verdict:
APPROVED-WITH-CONDITIONS, contingent on passing the batch's local checks.

Top finding: different averaging operators and spatial support cannot be
pooled into a seasonal width interval. CURRENT, SOUNDER and CHART agree.
Amendments: preserve 200 km as contextual scale; separate figure dates from
width occupations; bind the complete measurement in Python and Rust and
display those distinctions beside the approximate point.
