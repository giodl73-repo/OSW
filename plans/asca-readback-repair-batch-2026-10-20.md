# ASCA reconstruction repair and full-suite recovery

Same continuing branch and draft PR #83. Source base `20b1017`, following the
Red Sea source/case inventory commit `dfbdbb1`.

## Two distinct validation failures

The clean full run at `cefddd5` completed all 1,890 tests: 1,881 passed, nine
failed, with 1,114 passing subtests, in 5,538.20 seconds. Every failure reported
`OSError: [Errno 28] No space left on device`. Its log and terminal receipt
remain preserved. This is a failed full gate, not a passing result or a timeout.

During the run, automatic Git geometric repacking exhausted local storage after
the data commit succeeded. Its abandoned 960,102,400-byte temporary pack was
removed only after Git was terminal. Source datasets, committed objects and
the running checkout were preserved. Unused local compiled caches were cleared;
retained failed fixtures were compressed losslessly. Repository-local automatic
maintenance/GC is suspended, with previous values recorded in the task cache,
to prevent another repack during complete validation. Source assets were not
deleted. A fresh full run requires a clean head, adequate free space and a
separate receipt; the failed run is never overwritten.

Separately, Linux baseline job 118996488516 failed on ASCA strict reconstruction,
causing related dashboard negative tests to stop at that earlier error. The new
16-target independent audit (run 39535694813, job 119011695686) established the
cause: only three computed alignment indicators differed by up to
3.552713678800501e-15 degrees. The other fifteen reports were byte-exact, and
all ASCA source/measurement/non-angle fields agreed. This is unrelated to the
local disk failure.

## Narrow representation repair

The [readback declaration](asca-alignment-indicator-readback-v1.md) fixes the
computed alignment indicator at six decimal degrees after all decisions.
`measure` remains at full precision. `verify` still requires exact report
equality; the independent gate still requires exact encoded bytes. No tolerance
or exception is added to those checks.

The rule applies consistently to all indicators: 925 of 931 stored values
change representation, with a maximum change below 0.0000005 degrees. Every
one of 2,793 threshold cases, every span/edge/bracket, all peaks/source vectors,
masks, clocks and monthly/overall summaries remain exact. The four original
frozen inputs, raw/monthly/query packets and original component protocol are
unchanged. Both scientific figure assets are byte-for-byte unchanged; only
the report/figure provenance and downstream bindings are renewed.

No physical width, new annual range, source-file completeness, corrected-axis
validation or completed 2022-corrigenda review is claimed.

Terminal preservation also confirms all 60 typed Red Sea records, 43 other
collections, 239 other objects, 48 other diagnostics and 391 indexed documents
remain exact. All series values remain exact; one Agulhas series source hash
is renewed. The source corpus still contains 393 documents. All 770 staged
source/build/index blob pins verify, now including the complete retained ASCA
byte-subset graph (65 original-input/contract pins). This is custody of the
retained subsets, not a claim that the entire remote NetCDF file was downloaded.

## Checks

* 19 focused ASCA checks pass, including every profile's unrounded measurement
  outputs and the exclusive angle readback rule.
* 81 Rust tests, locked native/WASM builds and native atlas loading pass.
* Actual-browser ASCA checks pass all 931 outcomes, three views, 27 month
  choices, source pagination, keyboard/320px, and nine native/WASM corruption
  cases, including rejection of the new readback-protocol pin mutation.
* Preserve all 60 Red Sea normalized cases and the other fifteen scientific
  reports; verify whole-source custody and strict independent Linux equality.
* Start a new clean complete run only after the earlier process is confirmed
  terminal. Use compressed private temporary directories and adequate space.

Commands:

```text
python analysis/build_asca_component_spans.py
python analysis/build_asca_component_span_figure.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis/test_asca_component_spans.py -q
python analysis/test_asca_component_spans_browser.py
python analysis/inspect_scientific_reproduction.py
python -m pytest analysis -q -o tmp_path_retention_policy=failed
```

The broader current measurement/inventory goal remains active. This repair
makes existing source-derived data reproducible; it does not make remaining
physical dimension, seasonal coverage or state-association gaps complete.
