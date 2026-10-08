# Equatorial branching-point scope — 2026-10-07

Status: local source-context candidate, following the basin inventory proposals in PR25. No canonical dimensions or map geometry admitted.

The source-backed audit `research/equatorial-bifurcation-endpoint-scope-audit.json` records two regional diagnostics: the Pacific NEC branching near the Philippines and the Indian SEC branching off eastern Madagascar. Values were checked against local PDF renders. The source PDFs remain in an ignored review cache; their retrieval URLs and byte checksums are recorded. The original Madagascar author link returned 404 on direct retrieval, so the same paper was retrieved from the authors' university.

## Rules for future measurements

E01–E05 in the audit supplement the existing M01–M13 workflow:

- Define the branching point and upstream connection to the current core before selecting a velocity zero.
- Keep surface, depth-specific and layer-averaged results separate, including reference level and product.
- Keep annual-cycle spans, filtered multiyear variation and estimation uncertainty as different range types.
- Keep branching-latitude motion and coastal sampling bands separate from current width and whole-current length.
- Require compatible geographic fields for longitude, axis and both endpoint gates; reported latitude windows alone do not establish monthly routes.

## Source handling

The Pacific study's own section-2 results are stored separately from the prior-work seasonal discussion in its introduction. Its annual-cycle and filtered multiyear ranges are retained as separate records. No confidence interval is inferred.

For Madagascar, surface SSH, WOD09 surface/400-m values and the upper-400-m hydrographic mean retain their different layers and methods. Figure 3 describes the model average as upper 415 m while the prose discusses upper 400 m; the audit flags this difference and does not admit a harmonised model-layer record. Source seasonal windows are timing context, not inferred routes or annual dimension extrema. The published branching-latitude amplitude is not stored as current width.

## Checked access and verification

The exact audit document is registered in the lossless Rust index corpus, increasing the local source count from 65 to 66. It is queryable at `/entries`. The 38-collection main snapshot and admitted object counts are unchanged.

```json
{"document":"research/equatorial-bifurcation-endpoint-scope-audit.json","pointer":"/entries","limit":10}
```

```powershell
python -m unittest discover -s analysis -p test_equatorial_endpoint_scope.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_rust_index_store_browser.py
python analysis/test_rust_index_page_browser.py
```

The scope test rejects stale input pins, dimensions/rank on a regional diagnostic, relabelling cycle spans as confidence intervals and promotion of seasonal timing to annual geometry. Browser checks preserve exact original source bytes and native/WASM query parity.

Next: review identities and terminology, acquire versioned layer/time-compatible fields, reproduce regional branching diagnostics, and source the upstream gates and axes. Current lengths and widths remain missing for these proposed members.
