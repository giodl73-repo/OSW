# South Australian flow context in the checked atlas

Baseline `ce3cb2c99395f66a3bfeb5837d6580462645ffc1`; continuing branch
`codex/current-measurement-gaps`, draft PR83. No new PR or main merge.

## Delivery

The current card, seasons page and diagnostic query share one monthly map.
All twelve 2012 means and three original thresholds remain selectable. The
map preserves native cell membership, source missing support, original seed,
direction samples at fixed stride four and the unchanged section span. It
draws longitude/latitude axes at local aspect 35°S; no coastline is inferred.

Playback steps through recorded monthly model means without interpolation.
Reduced motion disables automatic playback. Manual controls still work;
playback stops when the panel closes, the page hides, the panel is removed or
the user changes a control. Share links restore month and threshold. Exact
monthly membership/support, both scientific sheets, original section profiles
and method/source pins remain directly reachable. Original approximate spans
use the declared 10 km reporting rule; full numerical source precision remains
in the retained record. Colors are accompanied by textual readings and source
tables. Phone labels were enlarged after visual inspection.

## Checked data contract

`analysis/south_australian_flow_context.py` verifies the actual source and full
context report, then emits a compact 234,680-byte scene. No full source cube is
embedded in the main query store. The scene preserves all 36 cell-membership
sets, all seeds, monthly support denominators, old section endpoints, and 247
direction sample positions per month, including null unsupported samples.
The checked constant source-pair mask justifies a shared support grid.

Rust binds the exact scene, Python helper, 23 source/method/figure pins,
diagnostic record and owner join. Scope changes, deleted membership, altered
source/figure pins, erased joins, duplicate diagnostics, coherently resealed
records and attempted inventory-width promotion reject. The checked index
contains the full report and supporting JSON documents; its compiled catalog
rejects changed raw source documents. A source-level JSON query can recover
all twelve monthly records exactly.

The scene is `diagnostic:south-australian-hycom-2d-flow-context`; it remains
separate from `diagnostic:basin-south-australian-132e-100m`. Native/WASM query,
atlas and seasons snapshots expose the same scene. Queries returning several
diagnostic families retain their earlier scenes alongside the new context.

## Preservation

Against ce3cb2c, all other 239 object rows and 239 dashboard entries are
identical by value, as are all 47 older diagnostic records and every other
query collection. All 240 latest-observation dates and the width-inventory
bytes are unchanged. Widths remain 155, old width samples 463, reference routes
76, series 28. Mixed-query legacy source-review, research, filtered-width,
ASCA and EAC scene arrays compare exactly against the predecessor native
binary/packet. Only South Australian context support is added.

Generated index: 370 documents. Main query packet: 90,190,856 bytes. WASM:
16,805,377 bytes. New total: 48 diagnostics. The source is modeled flow at
100 m, not a direct observation or new physical-width measurement.

## Verification and limits

- 79 Rust unit tests and locked native/WASM builds pass; actual native atlas
  loading accepts the generated packet.
- Focused source/context/scene checks: 28 Python tests and 5 subtests pass.
  Browser-runner environment checks: 2 tests and 2 subtests pass.
- The browser matrix exercises all 36 cases in each of card, seasons and
  diagnostic views, exact native/WASM scene and full source-row parity,
  keyboard selection, reduced motion, playback, collapse-stop, share links,
  320 px reflow, seven packet corruptions and one index corruption.
  An initial exact-label failure was fixed with explicit accessible labels.
  The final visual/playback matrix passes, including seven native/actual-WASM
  packet rejections and one native/actual-WASM index rejection. Phone maps
  and their final larger labels were visually inspected.
- The normal shipped-WASM runner includes this check and retains every prior
  check. Source originals are not downloaded by normal page use.

The clean ce3cb2c full analysis run remains active in its separate verification
checkout and predates this UI batch. Its result cannot certify these edits.
The last terminal clean full pass remains 778c791, 1,805 tests / 1,164 subtests
in 2943.83 seconds. Remote ce3cb2c CI attempts stopped during old paper-fixture
acquisition (GEOMAR South Indian 403; Hawaii Qiu NEC timeout), before tests.
No source pin or scientific assertion was weakened to obtain a green check.

Reproduce:

```powershell
python analysis/south_australian_flow_context.py --check
python -m pytest analysis/test_south_australian_context_scene.py analysis/test_south_australian_flow_context.py analysis/test_south_australian_hycom_2d.py analysis/test_south_australian_hycom_spans.py -q
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_south_australian_context_browser.py
```

Further scientific work remains: independent named-flow association and
flow-normal/representative dimensions. These monthly grid components are not
current footprints, trajectories, physical width or annual physical extrema.
The full inventory, its measurement gaps and required visualizations remain
the active objective; neither this source nor its UI closes that whole task.
