---
skill: roles-check
topic: agulhas-asca-100m-sections
date: 2026-10-17
source_commit: 2efe752
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Agulhas ASCA100 m source sections: preparation review

Internal functional review of the registered source packets, Rust module
and chart renderer. This is not external scientific peer review or approval of
current boundaries. Loop checkpoint8225959 and acquisition fix2efe752 are published on PR83.
The Agulhas integration is live in the local mainline UI; publication checks
remain pending. ORBIT is inapplicable: no planetary comparison is introduced.

| Role | Finding | Severity | Evidence / action |
| --- | --- | --- | --- |
| CURRENT | Source100 m depth and the paper's20 dbar grid description are distinct. | P2 resolved | Retain NetCDF metre coordinate; original methods discrepancy is documented. No100 dbar relabeling or uniform depth slab. |
| CURRENT | Independent component means cannot form a geographic velocity vector. | P2 resolved | Per-field masks retained; separate paired means/counts require both source components at the same time/cell. Renderer shows components independently. |
| CURRENT | Output500 m spacing overstates independent observing resolution. | P2 resolved | Source uses interpolation, filtering and regression; array instrument spacing is much larger. No diagnosed edge, width, rank, density or transport admitted. |
| SOUNDER | Retained byte subsets do not verify the complete2 GB file checksum. | P2 resolved |59 exact multipart responses, every content range and original float byte hash checked; complete-file checksum explicitly unverified. No authenticity claim based on the provider MD5. |
| SOUNDER | Product2.0 and source-header first-version history disagree. | P2 resolved | Preserve both source metadata and provider identity; no undocumented correction/version substitution. Corrected C/D rotation context retained. |
| SOUNDER | Restoring a nominal clock could change source timing. | P2 resolved | Original float32 epoch seconds remain exact.64-second quantization allowance applies only to calendar-coverage labeling; source bins and timestamps remain unchanged. |
| CHART | Array distance is not a mapped current boundary. | P2 resolved | All charts label along-array distance; geographic edges remain null. Existing Agulhas map supplies context only; no source-line or width polygon invented. |
| CHART | Missing offshore U could look like no flow. | P2 resolved | Finite runs break at missing means; exact cell selector shows unavailable and n=0. Actual Rust-scene renderer test verifies the line stops offshore. |
| CHART | Sample SD shading could be mistaken for uncertainty. | P2 resolved | Descriptive spread labeled beside charts; zero/singleton support yields null SD. Units and fixed full-series axes retained. No confidence or annual-extrema interval. |
| BEACON |931 processed profiles are not931 independent full-current surveys. | P2 resolved | Source period/depth and processed observational status remain explicit; original filtering, regression and offshore geostrophy recorded. |
| BEACON |27 year-month bins could be described as a typical seasonal cycle. | P2 resolved | Keep years;25 complete nominal schedules, two partial months. Chronological controls stop at the end and generate no intermediate frames. |
| BEACON | An old published219 km limit could silently bypass corrections. | P2 resolved | Original transport-integration limit is not adopted as a100 m width. Identified2022 corrections and unreviewed full corrected figures/tables remain documented. |
| HARBOR | Charts require an equivalent data route. | P2 resolved | Labeled native cell selectors expose exact means, spread and support; SVG descriptions state missing-cell behavior. Controls and source/inspection links use semantic HTML. |
| HARBOR | Month selector overflowed320 px. | P2 resolved | Intrinsic select width corrected; browser reflow check passes and mobile screenshot reviewed. Charts scroll within bounded containers with an explicit hint. |
| HARBOR | Autoplay and lifecycle handling need reduced-motion support. | P2 resolved | Isolated host exercises motion-change stop, manual controls and final-frame stop. Query host owns shared listeners; renderer adds no retained per-render global listener. Actual query host also passes reduced-motion and manual-control checks. |
| KEEL | Stored JSON must agree with original float bytes and independent statistics. | P2 resolved |10 source tests pass; all finite float32 bits/null masks/timestamps preserved. Every monthly scalar and paired statistic agrees with independent Python statistics. Four source corruptions reject. |
| KEEL | Mutable projections alone cannot establish source integrity. | P2 resolved | Small compiled contract binds exact monthly source/dependencies/owner joins; eleven coherent mutations reject in the isolated Rust harness. All eleven coherent alterations also reject in actual native/WASM stores. |
| KEEL | Prepared code is not passing mainline publication coverage. | P2 pending publication gate | Integration, rebuilt native/WASM and dedicated UI/source/atlas/inspector/mobile check pass. All45 collections pass first/last pages, inspector, canonical imports and240 map marks. Current cards and full default offline gate remain pending. Never rebuild executable during validation. |
| LOGBOOK | Source-only and prepared integration states need accurate reporting. | P2 resolved | Plan records live integration and pending publication gates. Contract freezes source sections; no new scoped width is counted. Mainline counts146 widths /76 owners /45 collections /269 indexed JSON sources. |
| LOGBOOK | Source material must be redistributable and reproducible. | P2 resolved | Retained ASCA source subsets are CC BY4.0 with attribution and receipts. Copyrighted paper copies stay in ignored cache; independent source-field graphic is original. |
| LOGBOOK | This work must not create another PR per gap. | P2 resolved | Same branch and draft PR83. No additional PR or merge. Loop checkpoint and acquisition fix are pushed; Agulhas continues on that branch. |

## Evidence and remaining conditions

- Source/aggregation protocol and source pass:
  `plans/agulhas-asca-100m-section-aggregation-protocol-v1.md` and
  `plans/agulhas-asca-100m-source-pass-2026-10-17.md`.
- Latest source tests:10 passed in11.23 seconds. Actual registered source-query,
  atlas, inspector, native/WASM parity, mobile and reduced-motion checks pass;
  eleven coherent changes reject in both engines.47 Rust tests pass.
- New Rust module compiles in a separate offline harness;11 coherent source,
  projection, ownership and admission changes reject. Desktop/mobile renderer
  browser checks pass from its27-frame scene; screenshots reviewed.
- Integration patch is applied. All42 other legacy collections,24 prior series,
  widths/samples/routes and canonical arrays compare unchanged to8225959. Only
  Agulhas dashboard content changes. All45 collections pass; current-card sweep and full offline
  publication gate remain pending; dedicated test is registered in the normal runner.
- Full corrected2022 tables/figures, source-array geographic coordinates,
  current-boundary rules and physical/annual widths remain open. These are not
  conditions for describing the pinned source fields, but they are conditions
  for making new dimensional claims from them.

CURRENT, SOUNDER and CHART agree on retaining processed-field scope and explicit
missing support. HARBOR's mobile failure has been corrected. KEEL and LOGBOOK
require completed broad publication gates before the final review verdict.
