# Labrador described-latitude evidence increment

Continuing branch `codex/current-measurement-gaps`, draft PR83. Baseline
c5a1841; prospective method freeze b52358d precedes actual calculation.

## Measurement gap addressed

The working Labrador assessment advances from no numeric length evidence to a
conditional geographic lower bound. WGS84 meridional separation of the source's
43–60°N regional description is 1891.352935 km. Following the existing North
Atlantic method, round downward to a **1800 km conditional geographic floor**.
This is not a measured along-current axis or whole-current length. The source
supports a regional shelf/slope description with branches, not one dated path.

Nine independent ±0.5° editorial gate scenarios span1780.100119–2002.605130 km.
These are neither source position errors nor confidence intervals, annual
extrema or seasonal variability. The central1800 km floor is conditional on
the unperturbed source gates and is not below every editorial scenario.
Published length ranks remain13 of102, with89 unranked. The no-numeric-length
category decreases from70 to69; full current lengths remain unresolved there.

## Source and consistency

Thompson et al.2009, doi:10.1029/2008JC004859, section4.2 paragraph29, original
PDF pages6–7. The institutional original is572833 bytes with SHA256
1bbfdaf1c19dba0c6a274a8b06345e7dc0bd73b2980dc17e347fad985387bfdc.
Only selected pages6–7 were visually reviewed. The original remains private;
public metadata and factual transcription are pinned. Local original-file
custody is verified; default arithmetic reproduction is offline from the
retained factual inputs, with no new network acquisition gate.

The frozen North Atlantic latitude operator is reused without modification:
same WGS84 meridian, six-decimal arithmetic readback,100 km downward rounding
and nine gate scenarios. The abstract calculation meridian is never mapped.
No width, time interval, fixed measurement layer, endpoint longitude, seasonal
range, physical state intersection or connected centerline is inferred.
The old illustration-only map-arrow span and historical release are retained.

## Data and visualization

One scoped measurement and claim, an original-source record, an internal method
record and a complete admission are added. Only the Labrador working length
assessment changes. The existing North Atlantic admission remains alongside
it; its mapped-card scenario link now explicitly filters that current.
The Labrador mapped card links a scalar SVG, working assessment, all nine
scenarios and source custody. The figure link includes1800 km as text, and
complete numerical records provide an alternative to the visual. The actual
Chromium SVG rendering was inspected; it supports the embedded CSS which the
private MuPDF SVG renderer did not implement. Neither render was used to
change the frozen producer after actual calculation.

## Verification status

Twenty-one prospective source/arithmetic checks were frozen before calculation.
Seven actual-source/atomic-admission checks pass afterward:28 focused checks
in total. Three new native validation tests pass, including legacy NAC-only
compatibility and rejection of changed owner, source, value, rank, annual
range, missing dependencies/records and duplicates. Local report/figure
reproduction and exact original PDF custody checks pass.

A serial dashboard/index/packet/engine rebuild is running at below-normal
priority on one CPU, one worker. After terminal build, require preservation
against all106816 baseline rows (only Labrador assessment/object and the NAC
card-link change are intended), all522 old source documents and616 protected
old inputs. Expected additions: five rows; source index524; widths170 and
reference routes78 unchanged. Then run the focused browser check alone.
Staged-byte proof, publication and fresh38-report/UI CI remain pending.
The broad offline gate remains open; run it alone only as a final batch gate.
No main merge, overall-green or program-complete claim.

## Reproduce

```
python analysis/labrador_latitude_gate_bound_v1.py check
python -m pytest analysis/test_labrador_latitude_gate_bound_v1.py analysis/test_labrador_gate_bound_admission.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_labrador_gate_bound_browser.py
python analysis/inspect_scientific_reproduction.py
```

Optional local original custody check:
`python analysis/labrador_latitude_gate_bound_v1.py original --original-path PATH`.
Set OSW_TEST_BROWSER and run the local server for direct browser invocation.
Build refuses existing scientific outputs; retain failures and use new versions
for corrections. Width, along-current geometry and seasonal work remain open.

## Retained pipeline-order failure

The first full delivery reached native atlas validation and correctly rejected
`Changed Labrador geographic-bound length_assessments`. The older NWASC
working-admission loader replaces the assessment table after early overlays.
Moving the new Labrador overlay after all legacy imports fixes the ordering,
without changing the frozen calculation, preflight, report or figure. The
dashboard and source index do not pin the changed query builder and remain
valid; resume only packet and engine stages serially. The original failed
engine log is retained. Complete corrected delivery is still pending.

## Retained legacy-snapshot compatibility failure

The corrected packet passes the Labrador-specific record check but the older
NWASC validator binds its complete102-row historical assessment table and
rejects legitimate new overlays. A narrow native compatibility function first
validates the entire Labrador admission and every dependency, then substitutes
only that exact expected Labrador row into the old expected table. Every other
row and rank is still compared in full. The old NWASC scientific producer,
report, protocol and source inputs remain unchanged. Five targeted NWASC tests
pass, including exact new-overlay coexistence and rejection of altered
Labrador rank or another current value. One test compile error using an
unsupported Bundle.clone was corrected by mutating/restoring the test fixture.

This is one intentional native-validator compatibility update among616 prior
engine inputs;615 others must remain exact. The immutable baseline is retained.
Only the engine is rebuilding now; dashboard,524-document index and corrected
packet are reused. The previous failed engine logs remain retained.

## Shared verified-table composition

A third native gate exposed the same whole-table contract in the ASAR width
validator. A complete search found the matching contracts in the NEUC and
Aleutian width guards. All four now compose one shared expected-table function:
require the complete pinned Labrador admission and dependencies, replace only
its exact expected assessment, then compare the entire resulting table. No
width record, other length assessment or published rank is exempted. Existing
scientific reports, producers, protocols and preflights remain unchanged.

Four reviewed native guard files intentionally change among616 previous engine
inputs;612 others remain protected exactly. The immutable original baseline
is retained. A new composition test rejects incomplete proof and ambiguous
owners and preserves another current row exactly. The engine builder now runs
native atlas validation before the WASM compile, avoiding wasted later work
on invalid inputs. Corrected full native atlas validation passes; WASM build,
preservation and browser verification remain in progress.


## Terminal local delivery receipts (2026-10-23)

The corrected serial engine build passes all139 Rust unit tests and complete
native atlas validation before compiling WASM. The28 focused synthetic and
admission checks pass. The focused browser passes both complete native/WASM
admissions, four individual records, all nine Labrador scenarios, the retained
13 qualified length ranks, keyboard navigation and320px phone reflow. Native
CLI work finishes before Chromium starts; workspaces are reused.

The preservation receipt verifies106813 old rows exactly, the three declared
old-row changes and five added rows (106821 total across52 collections).
All522 previous source documents are byte-identical; the current catalog has
524 documents. All645 current engine pins match. Of616 historical protected
inputs,612 are exact and four reviewed native guard updates are explicitly
reported; the baseline and all frozen scientific products remain unchanged.
Widths170 and reference routes78 remain unchanged. The Labrador number stays
outside whole-current length ranks and seasonal data.

Private receipts: `.pytest_cache/labrador-bound-v1/preservation-result.json`,
`serial-engine-resume3/state.json`, `serial-checks-resume1/state.json` and
`browser/result.json` under that same private batch directory. Failed build
logs and the first failed packet parts remain privately archived. Only the
12 parts referenced by the current packet remain in the public parts folder.

Local conditions are satisfied. Staged-byte proof and publication to the same
PR83 follow as separate low-priority single-CPU operations. Fresh38-report
scientific replay and source/UI CI remain pending for the new head. The full
local regression remains intentionally stopped and must run alone at the
final batch gate. This batch does not close the remaining current length,
physical width, seasonal or identity/geometry gaps.

Staged-byte proof: PASS for966 unique Git index blobs comprising645 engine
pins and524 source documents, with overlapping descriptors consistent.
Publication and fresh remote CI remain pending.
