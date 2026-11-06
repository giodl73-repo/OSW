---
skill: roles-check
topic: norkyst-complete-year
date: 2026-10-17
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Complete-year model temporal support review

Artifact: year source acquisition, chronological monthly assets, section statistics, native regional means, three figures and reproduction tests. Seven installed lenses applied directly, not independent reviewers. ORBIT is not relevant.

| Role | # | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | 1 | Full-year filtering requires both endpoint halos and leap day. | P2 resolved | All 370 daily requests and 8,856 source hours retained; February has 696 hours; complete 8,784-hour year. |
| CURRENT | 2 | Monthly model means do not identify physical current boundaries or annual width extrema. | P2 resolved | Unknown dimensions, false admission/extrema flags and offshore/model/layer scope remain explicit. |
| CURRENT | 3 | A shortcut for low-pass means could lose support or conflate variance. | P2 resolved | Exact linear mean identity verified against explicit filtering; every positive-weight hour required; variances/quantiles use full hourly sections. |
| SOUNDER | 1 | A source extension could drift from previously retained fields. | P2 resolved | Twelve complete noon-field comparisons and all70 two-month overlap dates, with actual values checked for differing cuts. |
| SOUNDER | 2 | Counted samples are not millions of distinct geographic locations. | P2 resolved | 21,254,400 space-time samples at2,400 fixed source locations stated separately. |
| SOUNDER | 3 | Provenance must distinguish original bytes, numerical reconstruction and uncertainty. | P2 resolved | Exact original/member pins, tight derived-value tolerances, explicit units and no confidence-interval claim. |
| CHART | 1 | Native grid vectors need geographic-to-plot rotation. | P2 resolved | Established geodesic-probe rotation; independent direction and speed checks against the existing map helper. |
| CHART | 2 | Sampling boundaries or section lines could look like current geometry. | P2 resolved | Fixed offshore patch, no coastline and non-axis orange line stated; physical geometry flag false. |
| CHART | 3 | Comparison scales and reading keys must remain legible. | P2 resolved | Common salinity/vector scales and zero-centered component scales; reference key moved inside panel to avoid title overlap. |
| BEACON | 1 | A completed calendar year could be described as a climatology. | P2 resolved | Model2024 label and explicit non-climatology language throughout. |
| BEACON | 2 | Temporal variability could be mistaken for measurement/width uncertainty. | P2 resolved | Separate variability figure with population/ddof convention and explicit limits. |
| BEACON | 3 | Acquisition completion is not shared UI completion. | P2 condition | Research artifacts are complete; registration, current/query controls and their combined gate remain outstanding. |
| HARBOR | 1 | Figures need an equivalent numerical source and description. | P2 resolved for research | Full summaries/support and hourly assets; SVG titles/descriptions and method/source captions. |
| HARBOR | 2 | Category/sign must be recoverable beyond color. | P2 resolved | Labeled signed axes/colorbars, directional arrows, dates, keys and source-cell values. |
| HARBOR | 3 | Interactive month controls require keyboard/reflow/motion verification. | P2 condition | Shared UI is a next integration deliverable; no claim those new controls already pass. |
| KEEL | 1 | Year output must not silently omit months or invent support. | P2 resolved | Exact global cadence, chronological12-month output, every month's asset and full-original reconstruction tested. |
| KEEL | 2 | Cached archives and differing hour cuts need strict identity handling. | P2 resolved | Frozen container/member checks; metadata per day and field pins per cut; overlapping values compared. |
| KEEL | 3 | The earlier 1,619-test pass cannot cover newly added year code. | P2 condition | 27-test/20-subtest research gate reported separately; eventual combined integration gate remains required. |
| LOGBOOK | 1 | Producer versions must survive the new orchestration. | P2 resolved | Two-month capsule and its generators unchanged; new year generator and input/source hashes retained. |
| LOGBOOK | 2 | License/citation and publication boundaries must stay accurate. | P2 resolved | Daily CC BY4.0 metadata, MET Norway/IMR credit and independent plots; no publisher assets added. |
| LOGBOOK | 3 | The user's rolling-PR workflow must remain intact. | P2 resolved | Same branch/draft PR83; source/index/measurement counts distinguished; no new PR or main merge. |

## Synthesis and amendments

Roles reviewed: 7; findings: 21; open P1: 0. **APPROVED-WITH-CONDITIONS** for complete-year research/source publication. Conditions: build/verify shared UI integration, retain physical-admission limits and pass the eventual combined gate. This is not approval of a current width or a completed full-project measurement inventory.

CURRENT/SOUNDER agree on complete temporal support with unchanged physical unknowns. CHART/HARBOR require clear non-boundary visual grammar and numerical access. KEEL/LOGBOOK require candidate-specific validation and preserved producer versions.

Three amendments are applied: exact overlap and original-source preservation; missing-aware linear regional means with independent numerical checks; common visual scales, corrected reference-key placement and a separate variability view. Shared interactive controls remain to be implemented and reviewed.
