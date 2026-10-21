---
skill: roles-check
topic: kuroshio-axis-normal-source
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Axis-normal source extraction: functional review

Base9b335cb80429dff47d18984db62e3dda48934869. Internal application of the
seven relevant repository lenses to scientific code, report and figure;
no delegated reviewers or external scientific approval. ORBIT is not relevant
to this source increment. This is a draft source batch, not an atlas release.

| Role | Finding | Severity | Evidence / disposition |
|---|---|---|---|
| CURRENT | Axis normal is not independently observed velocity normal. | P2 | Resolved: metric, protocol, figure and velocity_normal_verified=false state the approximation, including initial-azimuth tangent convention. |
| CURRENT | Geometric separation cannot establish continuous occupied width. | P2 | Resolved: ocean connectivity unverified, physical inventory/state/annual-range admission false; no ribbon is generated. |
| CURRENT | Source boundary fallback is unknown, including widths beyond140km. | P2 | Resolved: null flags/uncertainty; all3 exceedances retained and flagged. No clipping or inferred threshold attainment. |
| SOUNDER | Original product/version/depth/time/license must be exact. | P2 | Resolved: complete provider2024 original passes SHA/MD5, compressed source pinned, CC BY4.0 attribution,3 nominal levels/all366days. |
| SOUNDER | Failures and ambiguity must remain reconstructible. | P2 | Resolved:16,470 stable source/date/depth/gate/window IDs;2,436 unresolved attempts; ambiguous candidate geometry and source indices retained. |
| SOUNDER | Numerical readback precision does not equal physical accuracy. | P3 | Confirmed: every resolved source interpolation/direct-normal/inverse check passes; physical uncertainty stays null. Display values use about10km precision. |
| CHART | Normals and latitude cuts must be distinguishable. | P2 | Resolved: actual geodesic normals, grey dashed latitude cuts and distinct source boundary styles in three dated maps. |
| CHART | A dated map must not masquerade as monthly mean geometry. | P2 | Resolved: maps explicitly2024-07-01; charts separately show monthly available-sample ranges/counts, without clipping finite values. |
| CHART | Projection/land context must remain separate from the metric. | P3 | Confirmed: WGS84 distances, equirectangular24N display, Natural Earth land context; no ocean-connectivity claim. |
| BEACON | Monthly min/max might be mistaken for error bars or climatology. | P2 | Resolved: heading, caption, description and report distinguish empirical model sample ranges from physical uncertainty and climatology. |
| BEACON | Tangent-window sensitivity must not become a confidence interval. | P2 | Resolved:7/14/28km conventions retained, paired-date sample counts explicit, no pooled physical range. |
| BEACON | More model calculations must not inflate admitted current coverage. | P3 | Confirmed:12 ranked lengths,157 scoped width records/83 owners unchanged. New metric is separately qualified. |
| HARBOR | Browser font fallback and crowded footer impaired readability. | P2 | Resolved after actual SVG rendering: sans-serif fallback list and footer spacing corrected; gate text/lines contrast >=4.5 against backgrounds. |
| HARBOR | Equivalent browsable data needs query integration. | P2 | Open required follow-up: report contains all records, but typed UI/table/card controls are not shipped yet. Do not claim atlas accessibility coverage. |
| HARBOR | Colour alone cannot identify gates or source curves. | P3 | Confirmed: distinct markers/line styles, labelled depths/gates, SVG title/description and ARIA references. |
| KEEL | New geometry needs analytic and complete retained-data checks. | P2 | Resolved:19 new tests plus22 previous checks; source custody, obliquity, independent boundary sampling, gaps, ambiguous crossings, endpoint and side/length guards, all summaries and direct normals. |
| KEEL | Cross-platform exact reconstruction is not yet proven for this head. | P2 | Open: c4978a2 Linux differed only in27 final bearing/coordinate digits, with all spans/statuses identical. Canonical print precision corrected; raw0.001m normal gate retained. Target23 still requires exact bytes; rerun new-head job. |
| KEEL | Full offline suite has an existing external acquisition failure. | P2 | Open: Rotschi1972 HTTP403 before tests at9b335cb. Last full local Python baseline774e466; no new complete-suite claim. |
| LOGBOOK | Keep the continuing review and avoid an unrequested release. | P2 | Resolved: same branch/draft PR83; no new PR or main merge; goal remains active. |
| LOGBOOK | Scientific source is not yet main query/atlas coverage. | P2 | Open required follow-up: typed contract, native/WASM record validation and shared map/card/seasons/dashboard delivery, with actual browser gates. |
| LOGBOOK | Previously admitted data must remain stable. | P3 | Confirmed: main packet, historical release, old reports/inventories unchanged. First-pass normal span values/statuses survive later provenance/readback clarification. |

Seven roles,21 findings:0P1,16P2 (12resolved,4open),5P3. Approved only as a
qualified draft source increment. Remaining native/UI, Linux and full-suite
gates prevent release/completion claims. The full core-data/info/visualization
goal remains active.

Amendments: keep the axis/velocity and geometry/occupancy distinctions;
retain every failed case and source pointer; complete typed mainline delivery
before presenting these results as integrated atlas coverage.
