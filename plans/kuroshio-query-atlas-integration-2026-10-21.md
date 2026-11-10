# Kuroshio regional model data in native/WASM queries and atlas

Base:b2b6556d2f2994edd043b038e048d71e5983b0fe. Continue the existing branch
`codex/current-measurement-gaps` and draft PR83. No new PR or main merge.
Full core-data/info/visualization objective remains active and incomplete.

## Data and contract

`current_dimension_samples` contains all6588 attempts:1098 regional-axis cases
and5490 fixed-latitude boundary spans.908 lengths and4976 spans resolve;190
and514 unresolved cases remain queryable with null values and explicit reasons.
Every row has date, source level/nominal depth, entity/source/diagnostic IDs,
case index and model evidence class. Unknown uncertainty is null on all rows;
boundary fallback occurrence is null on span rows. No zero error or known
threshold attainment is inferred. All inputs and the exact Python/Rust
projection are checksum bound by the versioned query contract.

Scientific support remains2024 only, nominal0.49/109.73/380.21m, fixed18–30N
axis gates and18.5/21.5/24.5/27.5/29.5N sections. Source30% axis-speed edges can
include unflagged search-window fallbacks;7km sampling and110km smoothing do
not establish numerical accuracy. Fixed-latitude spans can be oblique and exceed
the140km source normal-transect search length. Empirical sample ranges retain
expected/valid denominators; no physical annual extrema, confidence interval,
whole-current length/width, occupied area or physical state passage is admitted.

The scientific report's stale live-interface flag is removed. Its only other
change is the renewed producer checksum. Every numerical case, display frame,
summary, convention and source field stays exact relative tob2b6556;21 other
scientific reports remain byte-exact. Original provider bytes are unchanged.
Interface support belongs in the separate integration contract and bundle
edition, rather than a mutable flag embedded in scientific data.

## Query and visualization

Native and WASM expose the same6588 rows. The diagnostic returns a Rust-built
map scene with36 first-of-month frames at three depths, missing-vertex breaks,
daily case links and annual sample summaries. The source report is available
both as an exact atlas document and in the separate source-query index.

The global OSW map selects Kuroshio, zooms to the declared regional display
extent and overlays the selected dated axis/left/right curves. Changing date
or depth updates those paths and their label; selecting another current clears
them. A dedicated regional model map card provides map-card-return navigation.
It is not inserted into whole-current reference-route ordering:77 reference
candidates/71 owners and30 currents lacking reference cards remain unchanged.

The same component appears in the exact diagnostic query, model map card,
atlas preview and Kuroshio seasonal page. It includes date/depth controls,
manual stepping and optional twelve-snapshot playback without interpolation or
autoplay. Playback stops on selection change, visibility loss, component
removal, reduced-motion changes or year end. Reduced motion keeps manual
controls and disables playback. Sharing retains date/depth. Keyboard operation
and320px reflow are explicit gates.

Cream/pink/mint strokes with solid/dashed/dotted patterns remain legible over
the dark OSW background. Desktop maps and tables share columns when space
allows; narrow layouts stack, with a labeled scrollable table. The geographic
region, model basis, range meaning, uncertainty and source limits remain text.

Dashboard fingerprints add source/time/measurement evidence only to Kuroshio.
A new regional-model-attempts metric covers one current. Missing capability
fields on older/other rows mean zero stored attempts, preserving all other
objects and older packet compatibility. No model date is promoted to a new
observed-current position or width record.

## Preserved coverage and gates

101 accepted current names,28 pending proposals,12 ranked source-reported
lengths,31 published measurement rows,157 scoped widths across83 owners,
463 width samples and2853 existing section cases remain unchanged. There are
now165 query sources,53 diagnostics and415 indexed JSON documents. All240 other
objects and45 prior query collections are exact. All101 seasonal phase plans,
four original seasonal documents and historical release remain exact; prior
bundles load. New model maps do not enter canonical map features/state links.

Focused gates are22 Python tests and97 Rust tests, native/WASM/native atlas,
new end-to-end query/map/card/seasons/source/dashboard checks, existing general
query regression and106-source snapshot/18-corruption/optional-data regression.
Record final terminal results, visual inspection and staged pins below before
publication. These do not substitute for the full default new-head suite.

Atb2b6556, independent22-report reconstruction job119294003123 and NetCDF
job119294003437 passed; offline119294003697 failed before tests on the existing
Rotschi1972 IRD PDF HTTP403. New-head CI is separate. Last complete local Python
baseline remains774e466:1910 tests/1222 subtests; current disk guard prevents a
new complete local suite. No scientific external approval is claimed.

## Required continuation

Measure final packet size against Git's100MiB limit; do not drop cases to fit.
Partition storage before adding the remaining31 years/27 depth levels or other
large sources. Then continue actual current dimension, uncertainty, temporal,
route/card and source-qualified state-association gaps.89 current names remain
unranked and18 owners lack admitted scoped width. This batch is progress toward
the full program, not completion or permission to merge main.


## Final local publication evidence

- 22 focused Python tests pass, including the full scientific source rebuild,
  exact6588-case projection, preserved numerical data and explicit unknowns.
- 97 Rust tests pass; native/WASM builds and native atlas validation pass.
- New end-to-end browser passes exact native/WASM data,36 dated frames,
  date/depth controls/sharing, reduced-motion stop/disable, keyboard map-card
  return, overlay update/cleanup, seasonal page, exact source query,320px and
  dashboard one-owner coverage/native selection parity. No page errors.
- Existing general query regression passes. Snapshot regression passes106 exact
  atlas documents,eighteen loader rejections,native/WASM parity,101 current and
 140 eddy-record selectors,77 reference cards,mobile/optional/unavailable data.
- Final contrast/layout/link fixes rendered and visually inspected at1360x1100
  and320x1000.66 JavaScript files pass syntax;14 pages have validation
  assignments. This is not a complete14-page browser-suite claim.
- Preservation passes:45 collections,240 other objects,21 prior reports, all101
  phase plans and four raw seasonal documents exact. Kuroshio's complete
  numerical cases/frames/statistics/source/scope stay exact; only the old UI
  flag and producer checksum change. Prior bundle readable; historical release
  untouched.31 measurement rows,157 widths,463 samples,2853 old section cases.
- Final packet102819992 bytes;2037608 bytes remain below100MiB. All6588 attempts
  retained. Subsequent large datasets require partitioned storage.

The complete new-head default suite and independent22-report result remain
separate gates before merge. See recordedb2b6556 successes and403 fixture failure;
do not substitute old/focused results for those current-head gates.


Stable identity amendment: IDs now use source edition/date/depth and
metric/section/method, never extraction ordinals. Inserting or reordering source
cases preserves IDs; the UI consumes Rust-provided sample IDs. The case index
remains only a checksum-scoped source pointer. An explicit reorder/insertion
regression protects future year/depth additions.

Build recovery: a full disk interrupted formatting and one test write. Both
files were recovered from staged copies, then the stable-ID change reapplied.
Only the verified inactive Rust incremental build cache was removed. Retained
source originals were not deleted. Default engine builds now disable incremental
caches (caller override retained) and check free space before formatting. The
recovered build passes97 Rust tests/native/WASM/atlas. The earlier failed build
log remains recorded; it is not relabeled as a passing run.

Stable-ID final checks:22 focused Python tests pass, including insertion/reorder
identity stability. The final native/WASM browser also opens the exact Rust-
provided sample ID from its table. Recovered build/source-preservation gates
pass; original130603298-byte provider file SHA256 remains unchanged.

Final navigation gate passes: model map/card controls stay synchronized and
return navigation preserves both selected date and source depth. Exact sample
inspection uses the persistent Rust-provided identity. Final22 Python/97 Rust,
source-preservation, general query,106-document/eighteen-rejection snapshot,
source/dashboard/season/phone/reduced-motion gates pass.

Publication pin gate:940 staged source/input/artifact paths match their declared
bytes, including the complete source graph, original archive and final UI.
Whitespace check passes. This evidence footer is separately rechecked against
its staged bytes; it changes no source, data, executable or dependency pin.
