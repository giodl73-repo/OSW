# Loop Current: original prestorm core width

Continues PR83 from5fffc07. Adds one source-reported regional width and the
required provenance, independent visual, exact source query and atlas card.
No new PR or merge. Earlier145 widths remain unchanged.

## Source and definition

Uhlhorn, E.W. (2008), *Gulf of Mexico Loop Current Mechanical Energy and
Vorticity Response to a Tropical Cyclone*, PhD dissertation, University of Miami.
Institutional record: https://scholarship.miami.edu/esploro/outputs/doctoral/Gulf-of-Mexico-Loop-Current-Mechanical/991031447487802976

Section2.5.2 printed35-37 / downloaded PDF64-66, Figure2.28 printed38/PDF67:
about100 km for geostrophic speed at least0.4 m/s in the source-labeled
cross-stream middle-grid-row section. The width paragraph's period is
19-23September2002. General flight context18-23September is separate;2October
in-storm and4October poststorm data are not width occupations.

Velocity derives from thermal wind with zero reference at the shallower of
750 m and local bottom. Upper300 m core structure is not a uniform width slab;
exact width-evaluation depth and geographic edges are unresolved. Source calls
0.4 m/s about one e-folding from a0.75 m/s peak; their ratio is about0.53,
not exp(-1). Keep the explicitly stated fixed cutoff; no corrected boundary,
curve fit or new width inferred. Reference-flow and curvature speed biases are
not width-error margins. No100-200 km pooled range, annual extrema, whole-current
width, rank, buffered footprint or seasonal playback.

## Reproducible institutional acquisition

Repository cover responses are4,764,365 bytes, with distinct timestamps/hashes:

-14:53:17 -0400: c86e4086c9d3242abe52e11e8702aba7af59fc76975ec3d1173b2d572accca84.
-14:56:42 -0400: b1861bf6cffb0dfb9dc62fbe298a337859bc29ebb9ab2d0052355457b3727172.

All176 original thesis pages and794 transitive page/resource objects agree,
with graph SHA2566641481f87dd6dc2aedd651e00588b2aa163fdaa74d2cc9262a59e018beed4dc.
The edition contract also protects the repository cover identity except its
clock. Full PDFs remain unchanged and ignored; regenerated responses are retained
separately from the first reviewed response. Scientific content/resources,
ordering, count or retained-original changes fail; container metadata is outside
the scientific graph. Reuses the pinned pypdf6.11.0 typed object encoder.

## Integration and preservation

Totals:146 scoped widths /76 owners;263 indexed JSON sources;33 diagnostics,
24 series,44 collections and271 width samples. Seven diagnostic-only unresolved
owners remain; eight local-component diagnostic records are preserved because
Loop now also has independent published source evidence. These records remain
unadmitted as physical whole-current widths. Atlas retains their map link.

All earlier145 widths,271 samples,32 diagnostics,75 reference routes and
canonical arrays compare unchanged. Only the Loop dashboard owner changes.
No new current/eddy identity, monthly width series or physical annual dimensions.

## Reproduce

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/check_loop_uhlhorn_core_width.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
python analysis/test_loop_uhlhorn_core_width_browser.py
python analysis/test_dashboard_diagnostic_navigation_browser.py
python analysis/test_rust_collection_coverage_browser.py
python analysis/test_atlas_inline_width_browser.py
```

Downloads explicit; default tests use local originals/renditions. Never rebuild
native executable while tests use it. New source tests19 pass;47 Rust tests pass.
Dedicated browser passes atlas/seasons/inspector/source/mobile native/WASM parity, retained component links, disabled seasonal playback and nine coherent rejections. Dashboard diagnostic navigation also passes. All44 collection UI checks and100 current cards /146 scoped widths pass; the fresh full offline suite passes:1460 tests and1061 subtests in2543.79 seconds (42m23s). The first complete invocation finished with1459 tests /1061 subtests passed and one obsolete dashboard-count assertion (two retained diagnostics, now plus one published core). That assertion was corrected; the affected test passed on17October in22.54 seconds. No scientific inputs or product code changed after that complete invocation. Original width paragraph, independent figure and mobile chart visually inspected.

Fresh acquisition succeeded from an empty fixture directory. Third full response
SHA2562103155b21d0ce2fdd2df1f72cb25a3a6c213a57db33cc27a7b8aa7dba99a357
retained separately as repository-current.pdf; all176 original pages/resources
match the frozen graph. Prior-head5fffc07 PR run38617920029 failed acquiring
the older Qiu original from Hawaii (timeout), before tests; no source pin relaxed.
Remote CI is reported separately; institutional availability can fail before tests.
