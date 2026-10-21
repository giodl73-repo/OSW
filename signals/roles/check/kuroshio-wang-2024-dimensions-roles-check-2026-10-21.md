---
skill: roles-check
topic: kuroshio-wang-2024-dimensions
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Source extraction and scientific map review

Base commit:abd5eb61378bed8e1e49ba49c6460012f2256bbc. Artifact: protocol,
compressed original/custody, numerical producer/report, tests and standalone
scientific figure. Internal functional review, not external scientific approval.
CURRENT reviews metric support; SOUNDER custody; CHART geography; BEACON claims;
HARBOR equivalent access; KEEL reconstruction; LOGBOOK scope/publication.
ORBIT is not selected: no planetary analogy or atlas release is proposed.

| Role | Finding / evidence | Severity | Recommendation / outcome |
|---|---|---|---|
| CURRENT | Fixed-latitude separation is oblique;140km normal-search length is not its upper bound. | P2 resolved | Label fixed-section span, preserve all values; no perpendicular width or full-current admission. |
| CURRENT |30% boundary fallback is not flagged in the original. | P2 resolved | State potential censoring in protocol/report/figure; no inferred threshold attainment or confidence interval. |
| CURRENT | One modeled year at three levels is not a32-year climatology. | P2 resolved | Explicit2024 sample extrema, levels and expected/valid counts; no physical annual extrema. |
| SOUNDER | Original exceeds the ordinary Git file limit. | P2 resolved | Retain local original and byte-exact84.8MB gzip; verify compressed/original SHA256 and provider MD5 offline. |
| SOUNDER | Depth mapping is nominal, supplied by article/provider example. | P2 resolved | Preserve source example without execution; source levels01/23/30, no layer-average inference. |
| SOUNDER | Version/licence/custody need attribution beside derivatives. | P3 | Version1 DOI, CC BY4.0, provider metadata/acquisition receipt and figure attribution retained. |
| CHART | Source curves have gaps; interpolation could conceal unsupported geometry. | P2 resolved | Keep null vertices, reject ambiguous/long numerical legs and break SVG paths at missing points. |
| CHART | Static panels could be mistaken for monthly means or seasonal tracks. | P2 resolved | First-day dates predeclared and labeled, three levels separate, no interpolated playback. |
| CHART | Projection/coastline need explicit meaning. | P3 | Equirectangular, Natural Earth1:10 million map scale; no land-clearance or accuracy inference. |
| BEACON |908 lengths and4976 spans could inflate canonical measurement coverage. | P2 resolved | Standalone source report, nonpromotion flags;12 ranked lengths/157 scoped widths unchanged. |
| BEACON | Missing dates affect empirical annual ranges. | P2 resolved |314/366 regional surface lengths and304/366 example section spans; all rejected cases retained. |
| BEACON | Numerical readback precision can imply unsupported accuracy. | P3 | Six-decimal computational readbacks; maps round about10km and disclose grid/smoothing limits. |
| HARBOR | Color alone cannot identify three curves. | P2 resolved | Solid axis, dashed left, dotted right; legend and data alternative. |
| HARBOR | Scientific SVG needs an equivalent textual account. | P3 | Title/description, all numeric JSON, batch tables and scope explanations. |
| HARBOR | Standalone figure does not prove mobile interactive access. | P2 open before UI integration | Add keyboard/reflow/reduced-motion/browser checks with the native/WASM interface; do not claim them now. |
| KEEL | New computations need a real original, not synthetic-only parser tests. | P2 resolved |16 tests include complete byte-exact source/report rebuild and all1098/5490 cases. |
| KEEL | Source refresh must not be an implicit test network dependency. | P3 | All original bytes and companion data local; reconstruction reads gzip in memory. |
| KEEL | Full suite and independent new-head reconstruction are separate gates. | P2 open before merge | Add22nd reconstruction target; report CI separately; do not substitute focused tests for complete suite. |
| LOGBOOK | Source artifact is not shipped query/card/playback coverage. | P2 open before UI integration | Keep native_wasm_ui_integrated false and explicit next integration work; no inventory counts changed. |
| LOGBOOK | Previous PR workflow must persist. | P3 | Same branch/PR83; no new PR, no main merge, full objective remains active. |
| LOGBOOK | Other years/levels must remain visible work. | P3 |31 years and27 levels explicit; latest-complete-year choice made before extraction. |

Roles reviewed:7. P1 blockers:0. P2 findings:14 (11 resolved,3 scoped open
conditions). P3 notes:7. Verdict: APPROVED-WITH-CONDITIONS for source/report
draft publication; UI integration and full new-head verification remain work.

Top finding: these are reproducible regional model dimensions with potentially
censored boundaries. CURRENT/SOUNDER/BEACON agree. Amendments: independent gate
intersections with rejected cases; fixed modeled-year support and denominators;
explicit original custody plus redundant visual line patterns. Desktop figure
rendering/inspection and staged source-pin results are recorded in the batch
publication evidence; no external scientific approval is claimed.


Publication evidence:16 focused tests pass on the final producer/report,
including byte-exact numerical reconstruction. The final twelve-panel SVG was
rendered at1200x1390 and visually inspected; date/depth/gates, redundant line
patterns, unresolved values, source/limits and coordinate labels are legible.
All17 staged input/output/source/review blobs match workspace bytes, including
the compressed original. Staged whitespace passes. Shipped almanac/query/Rust
files and all existing inventories remain byte-unchanged fromabd5eb6. At that
head, scientific21-report job119271231298 and NetCDF119271231685 passed;
offline119271230625 failed before tests on the existing Rotschi1972 HTTP403.
