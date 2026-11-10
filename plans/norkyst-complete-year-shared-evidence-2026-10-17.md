# Complete 2024 model year: shared evidence integration

## Scope

Add the Norwegian Coastal Current regional model study to the existing shared current-card, seasons and diagnostics-query renderer. Retain twelve monthly maps, raw/low-pass mean sections and temporal variability figures, with a labelled keyboard-operated view selector and full size figure link. Source inspection exposes the complete annual report, original acquisition, declared rules and regional monthly values.

This is regional model evidence at 10 m for 2024. The 8,784 calendar hours and 191 interpolated section positions do not admit physical current width, an axis, annual width extrema, ranking or a state intersection. Original source spacing is 800 m; retained spacing is 3.2 km. Derived monthly quantiles and population standard deviations describe temporal model variability, not measurement uncertainty. The prior snapshot exposure remains disclosed.

## Generated contract

- 302 indexed JSON sources, up from 296.
- 45 query collections; 41 diagnostics, up from 40.
- Three shared research evidence scenes.
- Compiled third study uses the exact original annual report, scene, owner link and dependency pins.
- 80 engine source/artifact hashes checked.
- All 43 other query collections and all 40 earlier diagnostics preserved by value.
- Only the Norwegian Coastal Current object gains an evidence link; it is the only dashboard entry with a changed update fingerprint.
- 149 width records, 271 width samples and 75 reference routes unchanged. Width inventory, seasonal route frames and reference path source files retain exact bytes.

## Validation and publication

The engine build passed all 50 Rust tests (2.02 s). JavaScript syntax and Python compilation passed. The annual scientific reconstruction has an earlier 27-test / 20-subtest passing receipt; the repeat focused check passed all 27 tests and 20 subtests in 84.98 s. The expanded browser check and new combined offline suite are pending at candidate creation. The old 8130086 full-suite result is historical and does not cover this candidate.

Browser checks include all three owners through cards, seasons, query charts and source/record inspection; three figure views; keyboard, 320 px and reduced motion; mixed diagnostics; and native/WASM rejection of changed year hours, figures and width claims. These are required outcomes, not a claim that an unfinished run has passed.

Publication stays on codex/current-measurement-gaps and existing draft PR 83. No new PR or merge to main. Verify remote head after the original source upload finishes before claiming publication.

## Commands

```powershell
python analysis/current_research_evidence.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_current_research_evidence_browser.py
python -m pytest analysis -q
```

The standalone browser check can target an isolated local preview using OSW_RESEARCH_EVIDENCE_BASE and the installed browser using OSW_TEST_BROWSER. The mainline browser runner retains its existing documented server behavior. Ignored paper fixtures are local checksum-verified copies, not staged publisher documents.
