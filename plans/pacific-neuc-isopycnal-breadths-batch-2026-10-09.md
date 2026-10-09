# Pacific NEUC isopycnal breadths

Parent `27e4579ff117f820837f56f886ed5fd04be87492` / draft PR78.
Branch `codex/pacific-neuc-isopycnal-widths`.
Status: locally verified and pushed as stacked draft PR79 above PR78; no
mainline publication or independent scientific admission.

PR: https://github.com/giodl73-repo/OSW/pull/79
Implementation commit: `25a0fdddef0e70c840fb009a9def110bdc2abbb7`.

## Original evidence

Li, Y., Liu, H. and Lin, P. (2018), *Interannual and decadal variability of
the North Equatorial Undercurrents in an eddy-resolving ocean model*, Scientific
Reports 8, 17112. DOI 10.1038/s41598-018-35469-2.

Complete author article JATS XML obtained from Europe PMC, 89,353 bytes,
SHA256 `2321fff1a540d19d5da1409f16218efb748968e01e29c21926f9262fd0c6efc8`.
A fresh request reproduced these exact bytes. Relevant Results/Methods,
Figure 1/2 captions and license were reviewed. The original publisher PDF
was unavailable to this client; no PDF review is claimed.

The article's CC BY 4.0 license permits retaining the archived XML and source
figures with attribution. Europe PMC supplementaryFiles supplied original
Figure 1/2 JPGs; both were visually inspected. Figure 1 is reused unchanged
with attribution, DOI and license link. No figure boundaries were digitized.
The supplemental ZIP's download identity is recorded, but individual member
byte pins are the reproducibility contract, without assuming ZIP metadata
remains immutable across future requests.

Audit SHA256:
`2edff326fd4b7bbc2c6a8cdd1ef0324bac77a62f7e85579cd8ff38753e2db9a6`.
Protocol: `plans/pacific-neuc-isopycnal-breadth-protocol-v1.md`.
Scoped Git attributes preserve original JATS response bytes on every platform
and exempt the original math-markup whitespace from code whitespace checks.
The source response is not cleaned or reformatted.

## Measurements and exclusions

Two component records on the basin-specific Pacific NEUC owner:

| Component | Author's approximate breadth | Rounded WGS84 unit conversion |
|---|---|---|
| Southern (NEUCS) | 3° latitude | 330 km |
| Northern (NEUCN) | 1° latitude | 110 km |

The middle jet (NEUCM) exists, but its numeric width remains unresolved.
These widths belong to the Argo-based absolute-geostrophic 2004–2014 mean on
the 27.0 σθ potential-density-anomaly surface. Fixed-depth bounds, numerical
width error, exact observation dates, width endpoints and fixed-section
longitude remain null. The 2000 m relative-geostrophic reference, separate
LICOM/SODA 1969–2007 fields and source velocity variability are not width
sampling, depth or uncertainty.

Conversion is WGS84 meridional distance about zero latitude, a unit origin
only, rounded to 10 km. It does not locate a jet or its edges. Source degree
values stay visible. The reported meridional breadth is not a measured
flow-normal transect for tilted jets.

There is no single-current 110–330 km width range, annual extrema, monthly
animation, footprint buffer or physical state join. No measurement is assigned
to the cross-basin generic NEUC, surface NEC or Tsuchiya countercurrents.

## Data and presentation

127 scoped width records / 67 current owners / 24 unassessed owners.
All previous 125 width records are unchanged; only the Pacific NEUC dashboard
entry changes. Route geometry and 64 reference cards remain unchanged.

One checked Rust comparison scene appears in query, atlas and seasons.
It retains both source components for filtered-query context, marks matching
or selected rows, and preserves common-axis source-degree/km labels. Tables,
original licensed source imagery and source-row inspection accompany the
comparison. The phase selector changes component selection, with playback
disabled. Native geographic envelopes are not created.

The source corpus has 154 JSON documents and 5,486,953 compressed bytes.
There are 42 query collections, 53 JavaScript modules and 14 HTML surfaces.

## Validation

Local verification:

- Source/audit/protocol/acquisition/figure pins and inventory/frame validators pass.
- Full offline Python suite: 1,264 tests and 923 subtests pass in 759.36 s.
  Previous generated scratch was safely cleared before this invocation, which
  had no disk-space failures. The final scene-order canonicalization follows
  this run and is separately checked by revised Rust and browser regressions.
- All 42 query collections pass native/WASM first/last-page, inspection and
  canonical import checks. All 240 contextual object map marks remain.
- Seasons snapshot: four exact source documents, eight loader rejections and
  100 phase plans pass. Atlas snapshot: 83 exact documents, eighteen loader
  rejections, 100 current / 140 eddy selectors and 64 cards pass.
- Existing Australian transport and DWBC browser checks pass, including their
  ten native/WASM guards each. All 240 dashboard atlas name links pass.
- 53 JavaScript modules pass syntax; 14 HTML pages retain validation assignments.
- Final serialized Rust build passes all 45 tests, including reversed-query-order
  scene equality. WASM: 2,496,894 bytes; query bundle: 46,764,917 bytes.
- The new browser check passes exact query/atlas/seasons scene equality,
  complete filtered-component context, original source image load, mobile
  reflow/readability, keyboard source inspection and all eleven native/WASM
  scope/proof rejection fixtures.

Commands:

```powershell
python analysis/check_pacific_neuc_isopycnal_breadths.py
python analysis/check_current_width_inventory.py
python analysis/check_current_seasonal_route_frames.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_pacific_neuc_isopycnal_breadths_browser.py
python analysis/test_published_section_transports_browser.py
python analysis/test_dwbc_float_composite_browser.py
python analysis/test_rust_collection_coverage_browser.py
python analysis/test_seasons_rust_snapshot_browser.py
python analysis/test_rust_atlas_snapshot_browser.py
python analysis/test_dashboard_atlas_navigation_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

One parent PR78 offline run (37945954828) stopped at three Qiu/Chen timeouts
before reaching GEOMAR mirrors or code validation; its terminal log was
inspected. The companion 37945964061 subsequently completed all original acquisitions,
native Rust tests/build, baseline and full offline suite successfully. Its
shipped-WASM browser step remained in progress at the latest observation.
Which GEOMAR URL supplied that run is not established from step status alone.
Both NetCDF jobs succeeded. No mainline coverage or fully green remote CI is claimed.

The overall goal remains active: 89 whole-current length gaps, 24 unassessed
width owners, annual dimension ranges, missing route geometry and most
named-eddy physical footprints still require work.
