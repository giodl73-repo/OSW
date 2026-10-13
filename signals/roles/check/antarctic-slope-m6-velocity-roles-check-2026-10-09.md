---
skill: roles-check
topic: antarctic-slope-m6-velocity
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# M6 local velocity review

Artifact: primary-data ingestion, aggregation protocol, shared Rust/WASM
collection and interactive signed velocity charts. Internal functional lenses;
no independent scientific review. ORBIT does not apply to these Earth observations.

| Role | Finding | Severity | Resolution |
|---|---|---|---|
| CURRENT | A station velocity is not a physical current dimension. | P2 | Separate velocity collection; dimensions and occupied footprints are not inferred. |
| CURRENT | Geographic components differ from the article's rotated along-slope analysis. | P2 | Preserve released U/V, signed cm/s; explicitly exclude rotation/filter reproduction. |
| CURRENT | Seasonal means can conceal uneven hourly coverage and partial years. | P2 | Counts, expected slots and fractions retained; partial February endpoints excluded from composites. |
| SOUNDER | Exact source bytes and license must survive ingestion. | P2 | Full CC BY 4.0 TSV retained in deterministic gzip; raw SHA and acquisition receipt shipped. |
| SOUNDER | Unequal hourly counts must not silently change equal-year weighting. | P2 | Composite averages complete year-month means; synthetic unequal-count test distinguishes pooling. |
| SOUNDER | Nominal depth tables disagree and timestamp timezone is unspecified. | P2 | Preserve released 228 m identity; disclose table disagreement and retain source time convention. |
| CHART | Negative velocity must remain visible. | P2 | Signed source-wide axes and meaningful zero line for both components. |
| CHART | Filtering or pagination must not rescale the apparent change. | P2 | Rust computes fixed component/series axes from the complete approved collection. |
| CHART | Repeated readings must not imply many separate current locations. | P2 | Deduplicate map to one fixed M6 station; map scope describes its evidentiary role. |
| BEACON | Interannual spread can be mistaken for measurement uncertainty. | P2 | Whiskers explicitly describe spans of year-month means; uncertainty remains unresolved. |
| BEACON | Source depth and dates should be near the chart. | P2 | Titles state M6/228 m; global scope states 2017–2021; inspector exposes counts and years. |
| BEACON | A short route to evidence is required. | P2 | Dataset citation beside each panel, protocol in inspector, atlas link directly to charts. |
| HARBOR | Color alone cannot identify partial months. | P2 | Diamond outline and accessible partial-month label supplement color. |
| HARBOR | Dense monthly marks need a keyboard alternative. | P2 | Focusable marks, visible focus and a reading selector/open button. |
| HARBOR | Playback must respect user motion settings and hidden pages. | P2 | Shared stop registry, reduced-motion listener and manual selection retained. |
| KEEL | Default reproducibility should not require a fresh provider download. | P2 | Complete licensed source committed; builder reconstructs offline and checks raw SHA. |
| KEEL | Mutable bundles can coherently promote observational support. | P2 | Rust binds exact approved rows, source hash and owner joins; native and six WASM rejection cases. |
| KEEL | Legacy minimal fixtures must remain supported without bypassing current source pins. | P2 | Legacy exemption requires collection, source pin, declaration and all owner joins to be absent. |
| LOGBOOK | New source collection needs declared coverage. | P2 | Registered browser check and generic first/last-page collection checks; source documents indexed. |
| LOGBOOK | Local results cannot establish remote publication. | P2 | Branch work recorded separately from main; remote CI remains a publication condition. |
| LOGBOOK | This batch must not imply all core gaps are filled. | P2 | Width/length and unresolved named-eddy footprints remain explicitly outstanding. |

## Verification and conditions

Source reconstruction and sparse/equal-year tests pass. Native Rust's 41 tests
and native/WASM builds pass. Browser parity, source-wide signed axes, partial
February support, 320 px layout, playback/reduced-motion and six altered-source
rejections pass. Native coherent source-value/hash mutation is rejected.
All 49 shipped JavaScript files pass syntax checks; all 14 pages retain declared
validation assignments. Full Python suite and generic collection browser run
were still running when this review was written; their final results belong
in the batch receipt. Remote CI is pending and mainline publication is not claimed.

Three amendments applied: preserve missing-hour and equal-year semantics;
use signed velocity grammar with explicit descriptive spans; add equivalent
manual controls and immutable native/WASM source bindings.

Cross-role consensus: nominal depth, local spatial support and descriptive
variation must remain visible in every use of these records.

### Final local receipt

Full Python suite passed: 1,177 tests / 918 subtests, 502.77 seconds. All 40
collections passed their native/WASM first/last-page and inspector checks.
The subsequently added native mutation test passed separately with both existing
aggregation tests. The final M6 browser check also passed direct atlas-to-chart
navigation. The remaining review condition is remote CI/publication; no mainline
status or completion of the larger scientific inventory is claimed.
