# Agulhas source-custody and core-description batch — 2026-10-21

Continues `codex/current-measurement-gaps`, draft PR #83. No new PR or main
merge. The overall current measurement/info/visualization goal remains active.

## Source and decision

Acquired the original publisher PDF (12,585,782 bytes, SHA256
`9ca5a0854eff936d32d5fd597cd94007ea3704ddba1ebeb1aeedede09967472d`)
and XML (657,080 bytes, SHA256
`b0b6aaa4932ce5fcce1576c0cb389f106c96f56e983fc3773803a8ac53ed3f45`)
for Vinayachandran et al. (2021), doi:10.5194/bg-18-5967-2021. Preserve
the CC BY 4.0 attribution, original bytes, retrieval times and acquisition
receipt. Printed pages 5970–5971/PDF pages 4–5 were rendered and inspected.
The offline verifier binds both originals and the publication identity.

Section 2.1.1 supplies an approximately 200 km typical core description.
Admit one scoped width record with unspecified observation date, averaging
period, layer, edge cutoff, paired coordinates and error. This contextual
review cites earlier literature; it is not independent observations of the
existing 219 km ACT time-mean section result. Do not combine the values into
a range or transfer either metric to a whole-current physical envelope.

Initial research rediscovered the review's 1000 km coastal extent. That value
was already retained as a narrower source variant in the length ledger.
The original acquisition strengthens its custody; it is not a new length
discovery or rank. The broader 27–40 S geographic floor and editorial route
have different supports. Keep all length assessments and rankings unchanged.

## Data and presentation

The new report binds a typed width record, source record, original files,
protocol and OSW scalar summary. The existing publication ID is reused with
updated custody/license metadata. Native validation rejects changed values,
source/owner reassignment, removed rows, dates/layers/annual ranges and whole-
length promotion. Old snapshots without this edition remain readable.

`research/ocean-current-effective-measurements.json` appends this width to the
earlier working measurement export. The earlier export and admission remain
unchanged. The working catalogue download points to this effective export;
the new query/atlas/card/seasons summary links the exact report, width record,
original paper and citation. The figure displays two separate scalar
descriptions, without map geometry, rectangles, area or seasonal animation.
Semantic HTML repeats the image content for phone and assistive access.

The reference page previously appended only the Madagascar width. The actual
regression test exposed its missing new row. It now consumes the same native
supplemental width/decision arrays as seasons and computes counts and owner
links from those records. The final browser gate verifies the new table row.
The undated core-description phase is non-playable and its width bar is hidden.

## Verification and remaining work

- Nine focused Python tests/eight subtests pass, including independent PDF
  text readback, frozen original pins, source/width scope and append-only export.
- All 106 Rust tests pass, with native and WASM builds and atlas validation.
  All 66 top-level almanac JS files pass syntax checks.
- Actual browser checks cover native/WASM diagnostic and width equality,
  original-source links, exact report, keyboard query navigation, atlas/card/
  seasons, 158 width-table rows, 320 px reflow and non-playable undated evidence.
  Desktop/mobile scalar summaries were visually inspected.
- Native backward validation reads full snapshot `ee27a9e` and compares all
  108 atlas source documents to file bytes. Its prior normal-span scene remains
  available. Source changes do not rewrite old scientific reports: all 23
  reports and their 23 producer files remain byte-exact to that baseline.
- Preservation compares every old query row and dashboard owner. Changes are
  one appended width, one diagnostic, Agulhas owner metadata and the existing
  publication's custody record. Other owners, observation dates/time evidence,
  geometry, length assessments, canonical releases and previous widths remain
  unchanged. The new source updates Agulhas measurement/source fingerprints.
- The prior prose-admission browser regression passes, including all158 width
  rows, the unchanged Madagascar rank12 and its non-playable survey state.
  The complete local suite is still an open release gate: free disk remains
  below its 4 GiB guard. No fresh full-suite or integration-CI pass is claimed.

Current totals: 101 accepted current names, 28 proposals, 12 qualified ranked
lengths, 89 unranked names, 158 scoped widths across 83 owners, 18 owners
without scoped width. Fifty collections/59,826 rows, 55 diagnostics, 421 index
documents. The new core description does not close an uncovered owner, annual
range, uncertainty or physical-edge gap. Reference paths remain 77/71 owners.

The packet is 139,736,488 logical bytes in nine checked parts, SHA256
`fb83c295d0387739f23e51a035fb8e19de854f8dcfa60dc4dd75e7307cf857af`.
The final engine is 49,465,955 bytes. Nine superseded generated parts were
retired; all source originals remain. Full-snapshot memory loading and source
upload limits are unchanged.

## Reproduce

```powershell
python analysis/acquire_indian_upwelling_review.py --verify-only
python analysis/agulhas_reported_dimensions.py
python -m pytest analysis/test_agulhas_reported_dimensions.py analysis/test_current_measurement_admissions.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_agulhas_reported_dimensions_browser.py
python analysis/test_prose_dimensions_browser.py
```

Use the checkout server on port 8788. Build commands are sequential. Continue
the remaining current length, width, repeated-boundary and uncertainty gaps
on this same PR; do not treat the scalar source summary as physical completion.
