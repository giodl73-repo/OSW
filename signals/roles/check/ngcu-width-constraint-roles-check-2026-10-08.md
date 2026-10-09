---
skill: roles-check
topic: ngcu-width-constraint
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal functional review

Seven installed roles review physical interpretation, data identity, visual
grammar, public wording, accessibility, reproducibility and publication.
ORBIT is excluded because no analogy is used. This internal review is not
independent scientific admission.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | O(<20 km) is a qualified size constraint. | P2 | Newsletter p13 | Exact notation retained; representative point and range null. Addressed. |
| CURRENT | Downstream core doubling is spatial, not seasonal. | P2 | p13 | No 40 km value, 20–40 km range or seasonal cycle computed. Addressed. |
| CURRENT | Core depth and instrument reach differ from a width layer. | P2 | p13 / report p16 | Separate context; fixed layer and boundaries unresolved. Addressed. |
| SOUNDER | Source qualifier can be lost in numeric sorting. | P2 | Inventory | Structured qualified constraint separate from null point width. Addressed. |
| SOUNDER | Cruise 113 conflicts with Figure 3 caption 133. | P2 | p13 | Both raw labels and conflict retained; no exact width occupation inferred. Addressed. |
| SOUNDER | Underlying Doppler crossing method remains unresolved. | P3 | Report / protocol | Supporting ADCP coverage reviewed; paired widths not extracted. |
| CHART | A point or 0–20 km bar would manufacture data. | P2 | Constraint visual | Source notation and text only; no point, interval or zero endpoint. Addressed. |
| CHART | Nominal 150°E salinity section is not a width boundary. | P2 | Figure 2 / geography | No section, route buffer or occupied footprint supplied. Addressed. |
| CHART | Narrow layout can clip source notation. | P2 | Registered browser | 320 px SVG label bounds, font size and page reflow tested. Addressed by check. |
| BEACON | Less-than wording can imply a rigorous hard bound. | P2 | Caption / aria | Order-of-magnitude qualification and unknown representative width explicit. Addressed. |
| BEACON | The speed exceedance can be mistaken for a cutoff. | P2 | Method note | Above 80 cm/s remains speed context; boundary cutoff not adopted. Addressed. |
| BEACON | Work-in-progress source needs its evidence class. | P2 | Citation / quality | Newsletter unpublished-manuscript class explicit. Addressed. |
| HARBOR | The visual needs equivalent textual meaning. | P2 | SVG / figcaption | Source notation, unit and limitations appear in text and aria. Addressed. |
| HARBOR | Data access should survive limited perception. | P2 | Current card | Direct source query plus details and source link. Addressed. |
| HARBOR | Season controls can falsely offer playback. | P2 | Inspector | Playback, interval bar and boundary locator remain ineligible. Addressed. |
| KEEL | Null point and range break former display assumptions. | P2 | Atlas / table / inspector | All three entry paths explicitly handle qualified constraints. Addressed. |
| KEEL | Coherent receipt edits could promote a width. | P2 | Rust / Python | Complete compiled record binding and numeric/date/context mutation guards. Addressed. |
| KEEL | Parent remote acquisition jobs failed. | P3 | PR56 | Both offline failures inspected as terminal; failure cause recorded from job log separately. Protected gates retained. |
| LOGBOOK | Newsletter requires author permission for reuse. | P2 | Copyright page 44 | Originals stay ignored; metadata and editorial extraction tracked. Addressed. |
| LOGBOOK | A constraint must not become another independent point sample. | P2 | Inventory | One scoped constraint; 95 records / 51 owners / 41 unassessed. Addressed. |
| LOGBOOK | Official scientific admission remains outstanding. | P3 | Status | Editorial extraction pending independent admission; draft publication. |

Roles reviewed: 7. P1 blockers: 0. P2: 18 addressed through extraction,
interfaces and executable checks. P3: 3 followups. Verdict:
APPROVED-WITH-CONDITIONS, contingent on passing batch validation.

Top finding: the reported less-than scale is not an exact width or a numeric
range. CURRENT, SOUNDER, CHART and BEACON agree. Amendments: preserve the
constraint as its own structured quantity; fix all null-value display paths;
bind the original and reject downstream arithmetic or seasonal promotion.
