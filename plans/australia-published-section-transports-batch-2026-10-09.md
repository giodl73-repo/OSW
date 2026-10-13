# Australian published section transports

Parent: `f52db2ed2b79e85565cd2dd83879fd03a93806dd` (draft PR77).
Branch: `codex/australia-published-section-transports`.
Status: locally verified, pushed as stacked draft PR78 above PR77; no mainline
publication or independent scientific admission.

PR: https://github.com/giodl73-repo/OSW/pull/78
Implementation commit: `39a7bbe87d493bb5e91fe85862212ce5f68191a1`.

## Evidence and extraction

Wijeratne, Pattiaratchi and Proctor (2018), *Estimates of Surface and
Subsurface Boundary Current Transport Around Australia*, JGR Oceans 123,
3444–3466, DOI 10.1029/2017JC013221.

The author institution's original is 23 pages, 3,016,059 bytes, SHA256
`1880c05374a7fb1cfed56910059a32c0884599d97ba040f532c07d28daecf0d9`.
A fresh institutional download reproduced these bytes on 2026-10-09.
The complete article is ignored because it is in copyright; no original
figures are redistributed. Acquisition metadata is tracked.

Original pages 1, 4–7 and 12–14 were rendered and visually reviewed.
Table 1(b), original p7 / printed 3450, supplies 35 model entries.
Table 1(a) supplies six paired validation entries. These are source-table
extractions, without raw model fields or observational series ingestion.
The model THREDDS endpoint timed out during an explicit acquisition attempt.

Frozen audit SHA256:
`758f18afccfee1411434d59ff9a3d0c38daf8833abf285674a33f9386ec961dd`.
Protocol SHA256:
`193ac84a9af37b5b9d4301c9990f848df6faad16238c0f5384d133d3fadfeaaf`.

## Contracts retained

- Volume transport is in Sv, independently of current length and width.
- Magnitudes retain their separate N/S/E/W directions. No global signed budget
  is inferred across different sections.
- Model entries apply to 2000–2014; paired validation means have shorter periods,
  incomplete sampling and no exact matched-month masks.
- Table 1(b)'s plus/minus notation has an unresolved statistic definition.
  It is not rendered as standard error, a confidence interval or width error.
  Table 1(a)'s explicit SD remains variability; RMSE retains its own field.
- Eastern upper-2000-m integrals retain their explicit bounds. Western
  surface/subsurface cores have no assigned numeric depth interval.
- Recirculation variants and total westward integrals are distinct source
  quantities. Overlapping entries are not summed.
- M1's observed W / simulated S discrepancy and M6's 18 source months / 17
  inclusive calendar months discrepancy are preserved without correction.
- Fifteen model entries and two validation pairs have no canonical current
  owner. Holloway, Flinders and Leeuwin Undercurrent are source labels, without
  invented canonical aliases or aggregate-family ownership.
- Source latitude/longitude guides are partial coordinate context. They do not
  establish transect endpoints, routes, widths, footprints or OSW state joins.
- Hiri, South Australian and Zeehan seasonal transport ranges remain prose
  source context. No monthly curve, width margin or animation is fabricated.
- ozROMS uses no formal data assimilation, but SST/SSS relaxation and open
  boundaries use HYCOM. A freely evolving closed-budget interpretation is invalid.

## Data and presentation

Two new query collections: `section_transports` (35) and
`transport_validations` (6). All 42 shipped collections remain available.
The frozen Rust projection validates records, source/dependency pins, owner
joins and dashboard counts before creating scenes.

Six current cards expose native Rust scenes in both atlas and seasons views:
Leeuwin (8 combined records), East Australian (10), Hiri (1), South Australian
(2), Zeehan (1), Indonesian Throughflow (2).
Dashboard coverage has a separate published-section-transport metric.
Only these six of 240 dashboard entries change. All 125 width records and all
64 reference-route cards are unchanged.

The query UI renders common-axis mean magnitude bars, complete data tables,
separate validation tables, source-discrepancy notes, OSW map context and
source-row links. Names on coordinate guides appear on hover or keyboard focus.
Narrow screens use local keyboard-accessible horizontal scroll regions and
full tables. There are 52 JavaScript modules, 14 assigned HTML surfaces and
151 indexed source documents (5,483,610 compressed bytes).

## Validation and publication

Local gates:

- Frozen original/audit/protocol/acquisition pins pass; fresh institutional
  original redownload reproduces bytes.
- Serialized native/WASM build passes 44 Rust tests. Final WASM is 2,440,378
  bytes; query bundle is 46,742,164 bytes.
- Full offline Python run: 1,252 passed and 923 subtests passed in 649.72 s.
  Two additional cases hit ENOSPC while writing temporary fixture files, without
  reaching assertions. After removing verified old generated test scratch,
  targeted rerun passes all 53 selected tests in 70.51 s, including both failed
  cases and the strengthened proof-erasure guard. No scientific assertion
  failures remain; a single wholly passing full-suite invocation is not claimed.
- New mobile/keyboard/native-WASM browser check passes with ten scope mutations.
  Source rows, six owner scenes, dashboard coverage and guide focus are checked.
- All 42 collection first/last pages and record inspection pass, including
  canonical import equality and 240 contextual object map marks.
- Seasons snapshot: four source documents, eight loader rejections and 100 phase
  plans pass. Atlas snapshot: 83 source documents, eighteen loader rejections,
  100 current / 140 eddy selectors and 64 cards pass.
- Existing dashboard parity/outage/mobile and all 240 atlas name-link regressions
  pass. These browser tests run against the checked-out shipped WASM.
- All 52 JavaScript modules pass syntax checking; all 14 HTML surfaces have
  declared validation assignments. Internal seven-role review records 21 findings.

Commands:

```powershell
python analysis/published_section_transports.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_published_section_transports_browser.py
python analysis/test_rust_collection_coverage_browser.py
python analysis/test_seasons_rust_snapshot_browser.py
python analysis/test_rust_atlas_snapshot_browser.py
python analysis/test_motion_dashboard_browser.py
python analysis/test_dashboard_atlas_navigation_browser.py
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

The independent source admission and raw-data acquisition remain outstanding.
This batch does not close the 89 whole-current length gaps, annual dimension
ranges, missing current geometry or most named-eddy physical footprints.

Parent PR77's two fresh paper jobs failed before reaching the new GEOMAR
fallback: runs 37938395659 and 37938436349 each timed out three times on
Qiu/Chen. Both NetCDF jobs passed. The GEOMAR fallback's hosted-runner
availability is untested; no green CI or mainline coverage is claimed.
