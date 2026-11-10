# Norwegian slope branch: source-bound mean-core spans

Continues `codex/current-measurement-gaps` / draft PR83. No new PR and no main
merge. Previous turn completed publication of validated Agulhas evidence at
c01c980, updated PR83 and removed all temporary upload references.

## Gap closed by this batch

The prior slope-branch records retain a1995–1999 regional branch descriptor,
an altimetry surface scale and a2016–2017 relative-geostrophic span. This
batch adds the source's1993–2022 mean-core operator and two reported extents,
with stronger depth and threshold support. It does not resolve the ambiguous
Norwegian Current name, construct physical boundaries or supply missing
seasonal widths.

Baumann et al.2026, doi:10.5194/os-22-17-2026, original publisher PDF/XML,
CC BY4.0, acquired2026-10-22 UTC/2026-10-21 Pacific. PDF3–6/printed19–22
rendered and inspected, including Figure3 and distinct box-model assumptions.
PDF3,081,881B/SHA b7a49fcc9ff6f2f487381d9736996fd07e5cd0d2310743a88fb168e1587bae49;
XML114,882B/SHA81be4c2d2e437e1375c7063cd6f58cde79b66ea593437d6425346d0d1086b96d.
Original acquisition times, final URLs, byte lengths, type, citation and
license are retained in the new acquisition receipt.

- Svinøy: approximately50km lateral core extent at50m, comprising four CTD
  casts. The variable core reaches about460m;1500m is the horizontal domain's
  isobath constraint, not a width layer.
- Gimsøy: approximately50km horizontal extent of the variable-depth core,
  upper boundary50m and deepest point about530m. A fixed width plane is not
  supplied;2500m is the horizontal domain constraint.
- Both: absolute salinity at least35.16g/kg; fastest mean absolute-geostrophic
  velocity cells supplying50% of mean Atlantic-Water transport. Static core
  from1993–2022 mean fields, not mean instantaneous widths or seasonal samples.
  No edge coordinates, width errors or numerical threshold sensitivity range.
- The separate50km box-model width and750km section-to-section path remain
  modeling conventions, outside these widths and whole-current length ranks.
  The article's quarterly property interpolation does not date these widths.
  Public CTD data are identified, but curated study sections require author
  contact; raw reconstruction and author contact are not claimed.

## Data and interface contract

Two appended `proposed_widths` records, source-qualified variable/constant-depth
support, exact report query, independent scalar SVG and retained original.
The proposed slope card and main native/WASM typed query expose the same
records. Existing source definitions and canonical width inventory stay exact.
The new optional packet edition is checked separately so prior c01c980 packets
remain readable. Source rebinding, changed operators, erasure and transfer into
canonical widths must reject. No geographic scene or seasonal playback.

Expected totals:101 accepted current identities,28 proposals,12 ranked lengths,
89 unranked names,158 admitted scoped widths/83 owners;18 owners without scoped
width include6 currents,8 families and4 systems. Proposed-width collection
grows5→7, with five records on the slope branch and two on the front branch.
The source-index corpus gains report/receipt (421→423); main packet50
collections/59,828 rows. These expectations require final generated receipts.

## Verification and remaining work

Run source readback/field-support Python tests, serialized Rust tests/builds,
new native/WASM/card/source/keyboard/mobile browser gate, and the existing
Nordic branch navigation/width comparisons. Compare prior c01c980 typed rows,
dashboard bytes and scientific reports/producers. Preserve the source distinction
in both figure and accessible text; inspect desktop/phone renders.

Latest c01c980 Linux NetCDF job passed. Offline job119590800270/run39707477559
failed before tests on IRD Rotschi1972 HTTP403. The verified WHOI repair cleared
its earlier failure. Both original IRD URL and official host alias still return
403 locally; no source pin was changed, no restricted original redistributed
and no failed acquisition was treated as a scientific-test pass. Full current
suite remains an open gate; local disk below4GiB guard. Fresh results will be
recorded here after execution.

## Reproduce

```powershell
python analysis/nwasc_mean_core_widths.py
python -m pytest analysis/test_nwasc_mean_core_widths.py analysis/test_nordic_section_widths.py -q
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_nwasc_mean_core_widths_browser.py
python analysis/test_nordic_proposal_navigation_browser.py
python analysis/test_nordic_section_widths_browser.py
```

## Executed results

-7 Python tests/17 subtests passed for source/readback and existing Nordic
  definitions.109 Rust tests, native build, WASM release build and native atlas
  validation passed.66 top-level JavaScript modules pass syntax checks.
- New source/typed-query/card browser passed actual native/WASM equality,
  keyboard details and exact-source links, original link,320px reflow and three
  actual native/WASM mutation rejections. Desktop/mobile renders inspected.
  Existing Nordic proposal navigation passed five slope records. Existing
  Nordic comparison passed its WSC and prior Gimsøy views, inspectors, source
  links, phone layout and eight additional native/WASM rejection cases.
- All59,826 preceding typed rows remain exact; only two proposed-width rows
  append (50 collections/59,828 rows). All23 scientific reports and their23
  producer files, dashboard, proposal catalogue, admitted width inventory and
  effective measurement export remain byte-exact to c01c980. Prior full packet
  loads under the new engine; all108 prior atlas source documents remain exact.
-423 source-index documents,109 atlas sources,372 staged engine dependency
  hashes verified, including the CC BY4.0 original. Main packet139,743,073
  logical bytes/nine parts; WASM49,474,831 bytes. Report SHA256:
  7cfdbc51b3bbd7d4ab97753664969b944b905330d468522031a6ffd7b92b5966.
- Nine verified superseded generated packet parts retired; all source originals
  retained. Completed upload-prefix caches were retired after excluding all
  refs/reflogs/current source blobs; Git connectivity validation passes.
- Internal seven-role review:21 P2 findings,20 resolved/one whole-suite gate
  open; zeroP1. No external scientific approval or overall full-suite pass.

Earlier failed attempts are not gates: one Rust test initially compared the
figure's capitalization incorrectly, and the first browser attempt assumed
source-order rows instead of comparing IDs. Both were corrected; the terminal
runs above passed without changing source quantities or their scope.
