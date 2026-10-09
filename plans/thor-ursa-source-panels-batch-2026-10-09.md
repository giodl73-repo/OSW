# Thor and Ursa dated source panels — 2026-10-09

Status: local editorial implementation verified; independent scientific
admission and hosted checks pending. No mainline or scientific-release claim.

Parent: `44f96072cbefcea7743364e48c2862abec21a971`,
`codex/pacific-neuc-isopycnal-widths`, draft PR 79.
Branch: `codex/thor-ursa-dated-source-panels`.
Implementation commit: `27bcf4349252a747ee088869b9fe3161392d586d`, pushed.
Draft PR: https://github.com/giodl73-repo/OSW/pull/80, stacked on draft PR 79.
Committed original XML and both figure blobs rechecked against their pinned
SHA-256 and byte sizes after commit; all match.

## Delivered data and presentation

- Complete publisher JATS XML and unchanged Figures 2/3 from Johnson Exley et
  al. (2022), doi:10.3389/fmars.2022.1049645; CC BY 4.0 with author, source,
  copyright, license and cropping notice retained.
- Fifty source-panel records for two publication-scoped eddy identities:
  Thor, 2020-01-01 through 2020-06-29; Ursa, 2021-01-01 through 2021-05-01.
  Each has a printed date, row/column, source pixel crop, and explicit unknown
  geometry/center/radius/area/state relationships.
- Native Rust scene outputs shared by atlas and object pages, manual date
  selection and previous/next controls, exact source-index panel inspection,
  and complete unchanged original figures with axes and color legends.
- Two new indexed JSON documents: source-panel audit and acquisition receipt.
  156 source documents, 5,491,074 compressed bytes. 54 JavaScript modules and
  fourteen existing HTML surfaces. 42 query collections remain unchanged.

The Methods print `0.65 cm`; normalized contour value remains null. Source
colors show deep SSH_ref, while the bold contour depicts the surface Loop
Current. Numerical altimeter fields were not acquired. Fifty panels are regional
field displays during named shedding events, not fifty confirmed ring positions.
No panel boundary, annual margins, physical state join or seasonal climatology
is admitted. The visually closed-looking Ursa-event contour on 2021-03-07 is a
lead for subsequent interpretation and digitization, not an admitted footprint.

## Frozen provenance

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| Complete publisher JATS XML | `028757a8727a183ce8a4e2f4d06de969d9a74dcd1d7d21fda968529c5c904c2c` | 90,312 |
| Original Figure 2 WebP | `ab125ebdf2f642f3a21dd59516c90775f3a87d2ea3ba4a55a964591d1cf30fa8` | 1,728,874 |
| Original Figure 3 WebP | `c4f4c650ef6c675feeac53298b3969a3af7852bf8fcef4e87d37e7e2fd44a4d1` | 1,788,820 |
| Source-panel audit | `5ec56eaf942007a146acedfadfe1def961522a8f30cc12c3f1bdde74a4da240d` | 38,951 |

Original XML and both original figures were inspected. Original figures are
packaged unchanged; the viewer changes only the displayed source viewport.
Protocol: `plans/thor-ursa-source-panel-protocol-v1.md`.
Acquisition: `research/source-data/exley-loop-2022/acquisition.json`.
Internal role review: `signals/roles/check/thor-ursa-source-panels-roles-check-2026-10-09.md`.

## Validation

- Focused Python: eight tests pass, including nine native source/dependency
  rejections and exact atlas/object scenes.
- Serialized native/WASM build: 45 Rust tests pass.
- New shipped browser: fifty date selections, two full original figures,
  atlas/object native parity, per-date source inspection, keyboard/mobile and
  nine identical native/WASM scientific rejections pass. Initial source-link
  pagination defect corrected and re-tested.
- Existing atlas browser: 84 exact source documents, eighteen loader rejections,
  100 current/140 eddy selectors, 64 cards, no direct source reads, mobile and
  optional/unavailable data pass.
- Existing object browser: twenty exact canonical imports, 42 collections, ten
  native/WASM object cases, packet/no-direct-JSON/mobile/outage checks pass.
- All 54 JavaScript modules and fourteen page validation assignments pass.
- Full offline Python suite: 1,272 tests and 923 subtests pass in 893.64 seconds.
- Eight affected browser checks pass after scoping feature-title assertions to
  the preview's direct heading. A directory reload check now waits for the
  complete 240-entry inventory instead of an arbitrary 150 ms delay. The
  monthly-width and all-dashboard-links checks, directory, inline widths,
  presentation, shared view, Black Sea and Labrador checks all pass.
- All query collection values equal the parent snapshot. 127 scoped width
  records/67 owners, 64 routes, one named footprint and physical state decisions
  are unchanged.

The full Python suite ran before the final browser-selector/timing amendments;
those changes are in standalone browser checks, and all eight were exercised
afterward. No engine, scientific data or generated artifact changed afterward.

Parent PR 78 hosted companion run `37945964061`, offline job `113872161270`,
completed with failure in `test_atlas_monthly_width_browser.py`: a broad `h3`
selector matched both Leeuwin's title and its new transport subheading. All 25
paper acquisitions, native Rust, standard-library baseline and full offline
suite passed in that run before the UI assertion. This batch fixes the title
selectors for cards with multiple evidence sections. PR 79's two hosted runs
remain in progress at the shipped-WASM step as of this receipt; their NetCDF
jobs pass. No complete hosted-pass claim follows from local checks.

## Review links

- [Ursa source viewer](http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=eddy%3Apublished%3Aursa-2021#route-atlas)
- [Thor object page](http://127.0.0.1:8788/almanac/object.html?id=eddy%3Apublished%3Athor-2020)

## Remaining core work

Review the Ursa contour convention and identity, reconcile the printed unit,
and acquire/digitize compatible dated boundary coordinates with explicit
calibration scenarios before intersecting OSW states. Continue the 89 unresolved
comparable current lengths, 28 missing route-owner candidates, 24 unassessed
current widths and remaining named-eddy footprint/seasonal evidence gaps.
