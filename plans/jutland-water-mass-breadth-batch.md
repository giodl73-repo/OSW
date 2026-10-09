# Jutland coastal water-mass breadth batch

## Source and result

Skov, Mortensen and Tuhuteru (2019), DHI for the Danish Energy Agency,
*Site selection for offshore wind farms in Danish waters: Investigations of
bird distribution and abundance*, final approved 18 September 2019,
project 11823165. Original: https://ens.dk/media/5628/download/

The original is 13,249,526 bytes / 168 pages, SHA256
`4d77f9ecce0fe7c3f4760d050e1a68588fb8e86b6ed40b1d397d0bee95d0d572`.
Selected pages 1,3,26,27,28,35,36 were visually inspected. The PDF remains
ignored; the Open classification does not establish a redistribution license.

One editorial record preserves the reported **10–20 km surface-water-mass
breadth from Henne Strand to Skagen**, section 2.3, printed p15 / PDF p27.
The report cites Nielsen (1999), whose original boundary methods remain
unreviewed. No midpoint, velocity-core width, occupation dates, fixed depth
layer, uncertainty, annual extrema, ranking or seasonal map band was admitted.

Separate context stays separate:

- Almost 100 km offshore traceability and typically within 40 km core confinement
  apply to the Wadden Sea, without paired current edges.
- The roughly 40 km zone on printed p23 / PDF p35 is bird-habitat suitability;
  the 15–30 m depth zone is bathymetry.
- The nearby 20 km prose starts at Ringkøbing Fjord, a different reach; it is
  neither a preferred value nor an independent dated measurement.
- Figure 6 is a December 2018 modeled-field illustration, not width support.
- North/South Jutland alias relations remain unresolved in the existing naming
  audit, which is pinned and unchanged. No Norwegian Coastal width inheritance.
- Rydberg et al. (1996) is a retained research lead; the original was not acquired
  and no numerical record was admitted from its indexed excerpt.

## Data and display

Coverage: 106 scoped descriptions / 58 owners / 34 unassessed. These counts
include regional summaries and do not count resolved whole-current dimensions.
All 105 previous width records remain unchanged. Canonical ledgers and editorial
routes remain unchanged; the seasonal frames only refresh their width-inventory
dependency. The lossless source corpus gains the audit and acquisition receipt,
for 128 documents.

The source row is bound in the Python inventory and native/WASM trusted source
registry. The complete row, audit pointer, original PDF, provenance, convention
and naming context are pinned. Coherent receipt edits, erased context and
reassignment to another owner are rejected. Existing atlas/inspector charts
explain the water-mass scope and link to the source query. Close span-end labels
use outward alignment to retain legibility at 320 px.

## Regeneration and validation

Acquire ignored sources explicitly, then build and test:

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_jutland_water_mass_breadth_browser.py
```

The browser check is registered in the shipped WASM validation runner.
Roles review is internal editorial/software review, not independent scientific
approval. The underlying source, comparable section boundaries and seasonal
observations remain scientific gates.

## Parent remote validation

PR65 push run 37904283610 failed while downloading the checksum-pinned Qiu/Chen
NEC original: three network timeouts before native build or tests. The companion
PR run 37904303040 acquired all sources and passed native build, standard-library
and full pytest gates, then entered the browser gate. This distinguishes source
availability from the earlier PR64 missing-native-CLI failure; the build-order
fix is retained. No checksum or fixture requirement was loosened.

## Follow-up lead recovered after the extraction

DMI's author bibliography identifies the likely underlying Nielsen (1999)
source as *Dynamisk beskrivelse og hydrografisk klassifikation af Den Jyske
Kyststrøm*, University of Copenhagen master's thesis, reissued in 2000 as DMI
Scientific Report 00-15. The bibliography explicitly links the 1999 thesis to
that reissue: https://ocean.dmi.dk/staff/mhri/mhri.uk.php

Original-report candidate: https://www.dmi.dk/fileadmin/Rapporter/SR/sr00-15.pdf
and author-hosted copy https://ocean.dmi.dk/staff/mhri/Docs/Sr00-15.pdf .
This lead is not yet an inspected original or an admission of the underlying
width methods. The pinned extraction retains the source-review state when it
was made; the next source pass should verify this bibliographic join, inspect
the Danish methods and distinguish water-mass extent from velocity width.

## Validation outcome

- Full Python suite: **1,045 tests and 918 subtests passed**, 440.82 seconds.
- Native Rust: **41 tests passed**; native and WASM builds succeeded.
- Shipped Jutland browser check passed: 320 px card, disjoint numeric labels,
  inspector/source navigation, native/WASM query parity and coherent scope / owner
  mutation rejection. Screenshot inspected visually.
- Existing Baffin browser check passed after the shared label adjustment.
- Fresh explicit source acquisition verified all 13,249,526 original bytes
  against the pinned agency PDF; no fixture was added to Git.
- All engine, query and dashboard input pins passed. Previous 105 width records,
  other decisions and dashboard entries, canonical ledger, reference routes and
  Jutland naming audit are unchanged. Frames only refresh their dependency SHA.
- All 48 almanac JavaScript modules passed syntax checks; all 14 pages retain
  validation assignments. Whitespace checks passed.

Remote CI for this new batch remains pending; local results do not establish
mainline publication or independent scientific approval.
