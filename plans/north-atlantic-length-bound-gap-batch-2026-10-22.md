# North Atlantic nominal-section length evidence

Continuing `codex/current-measurement-gaps`, draft PR #83. No new PR or main
merge. Source commit before this batch: `8709da980941bcc985737f1fd42b41b1cf7c6029`.

## Increment

The working North Atlantic Current assessment advances from
`no_numeric_length` to `derived_lower_bound`. WGS84 meridional separation
between nominal 47°N and 58°N sections is **1,224.035663 km**, rounded down
to a **conditional 1,200 km geographic floor**. This fills one missing
regional numeric evidence record; it does not fill the whole-current length.

Caínzos et al. (2023), section 3.1.10 identifies the current at both sections.
Section 2 warns that actual stations deviate from nominal latitude. The
northern section combines western 53°N and eastern 58°N portions; only the
explicit eastern NAC description supplies the second gate. Different
cruises, branches and density layers do not establish one simultaneous axis.

Original CC BY 4.0 publisher XML is retained with acquisition metadata and
SHA-256. Existing source tables and original seven gate calculations remain
unchanged. The new protocol was written before calculation.

Nine independently perturbed ±0.5° gate scenarios yield
**1,112.761190–1,335.309667 km**. These are finite editorial sensitivity
scenarios, not measured source-position errors, confidence intervals,
physical lower bounds, annual extrema or seasonal variability. The 1,200 km
floor is conditional on the nominal gates; it is not robust to every scenario.

## Data and presentation

- New working `current_length_bound_admissions` collection retains the full
  calculation, nine scenarios, method, source, measurement, claim and assessment.
- Working `length_assessments`, `measurements`, `claims` and method-source
  records expose the bound through the existing Rust/WASM query interface.
- The existing North Atlantic mapped card links an accessible scalar figure,
  its working length assessment and the complete admission. No geographic
  axis is drawn from the abstract calculation meridian.
- Native validation pins the admission and dependencies and rejects changed
  owner, source, value, rank, annual range, missing rows and duplicates.
- The qualified ranking stays **12 of 101**, with **89 unranked**. Width
  counts and whole-current measurements do not increase. Historical v0.1.0
  remains immutable.

## Reproduce

```powershell
python analysis/north_atlantic_gate_bound.py
python -m pytest analysis/test_north_atlantic_gate_bound.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_north_atlantic_gate_bound_browser.py
python analysis/inspect_scientific_reproduction.py
```

## Verification receipt

Independent meridional-curvature integration agrees with PROJ to one millionth
of a kilometre for the nominal distance and all nine scenarios. Eight focused
tests pass. This arithmetic tolerance is not physical measurement precision.
All 112 Rust tests, native/WASM builds and native atlas validation pass.
Actual Chrome matches native results for the working assessment, measurement,
complete admission and all 12 ranked lengths. Keyboard disclosure/figure,
320px reflow, export availability and zero automatic original-source requests
pass; the scalar figure was visually inspected.

All 163 preservation fingerprints pass, including the frozen release and all
26 prior scientific reports and producers. Only the existing North Atlantic
assessment and dashboard-object rows change; four rows are added (method
source, claim, measurement, admission). Previous dashboard capabilities and
observation date remain unchanged. All 430 prior source-index descriptors
remain exact; all 432 current original-file hashes and all 407 engine input
hashes match. Main data: 51 collections / 59,832 rows / 166 sources / 55
diagnostics. Native atlas still has 109 sources. New packet: 139,772,306 bytes
in nine checked parts; WASM: 49,505,272 bytes. Nine verified superseded generated
parts were retired; all original research sources remain.

Fresh target-27 Linux reconstruction is pending publication. No complete-suite
or overall green CI claim is made here.

The full local suite requires at least 4 GiB free and that guard remains unmet.
The preceding remote offline job stopped during acquisition before tests;
provider 403 failures are separate from scientific reconstruction. This batch
stays in the draft PR while the complete-suite release gate remains open.

## Next

Continue the other current-length gaps in this same PR. Seek source-supported
axes or qualified published full extents. Never promote a coastline, model
viewport, plume, cruise section or illustrative route into a whole-current
length merely to reduce the unranked count.
