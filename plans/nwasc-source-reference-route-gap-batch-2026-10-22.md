# NwASC regional source-reference route gap batch

Date: 2026-10-22. Continuing branch `codex/current-measurement-gaps`, draft PR83.

## Admission and measurement scope

Hansen et al.2011, DOI10.1029/2011JC007375, page3 paragraph10 supplies nominal
P1(0deg30minW,62N), P2(3E,62deg40minN), S1(4deg15minE,62deg48minN).
The predeclared protocol and pinned input preserve all three coordinates.
The source was inspected before protocol declaration; this is not blinded work.
The source discusses the 2007-08 through 2010-07 weighted mean surface field.
Its reference positions do not supply an observed current axis, surveyed500m
isobath, instantaneous core, positional error or seasonal geometry. WGS84 is
our computational convention; the nominal coordinates do not imply that accuracy.

The two geodesic connections total261.604991km, publicly rounded to260km.
Nine combinations of midpoint offsets(-10/0/+10km on each leg) retain all three
anchors. The resulting261.604991-265.602838km span is displayed as260-270km.
The10km offset is an editorial sensitivity probe, not uncertainty, resolution,
width or annual variation. No scenario is suppressed. Raw and rounded exports
pass dense land checks against both the coarse mask and pinned Natural Earth
1:10M5.1.1 land. The original copyright PDF and reviewed source renders remain
private ignored fixtures; the public SVG is an original schematic.

## Data and presentation

A separate source-anchor connection class keeps this reference outside both
published whole-current ranks and the existing studied-reach ranking.
The77-row frozen catalogue and its original source address remain unchanged.
A derived runtime78-row catalogue adds the source-bound route, planning decision
and source joins. The region can be opened from the current query, global atlas,
keyboard-selectable current card, route card and full SVG. Labels and bend-probe
scope accompany the map. Seasonal playback remains disabled without eligible data.

Targets:78 routes,72 owners,30 currents without a reference card. All102 named
current records now have geographic marks; this does not establish102 observed
whole-current axes. The13 published length ranks and167 scoped widths across84
owners remain unchanged.89 unranked lengths and18 width-owner gaps remain.

## Verification and publication

Local and fresh Linux receipts will be appended after terminal results.
No new PR and no main merge. No complete-suite claim: the full local4GiB guard
is unmet, the full133-browser matrix is not run, and prior offline CI stopped
at Stramma1992 source acquisition(HTTP403) before tests. Large snapshot memory
and >50MiB WASM packaging remain open engineering limits.

### Local terminal verification

Final focused pytest:49 tests and2 subtests pass. Compileall and changed browser
JavaScript syntax pass. Engine builder:125 Rust tests pass, native and WASM builds
pass, and complete native atlas ingestion matches the generated bundle. Final
WASM54,834,640bytes; packet140,042,668bytes/nine parts.428 engine pins verify.

Actual Chrome executes five exact native/WASM comparisons: NwASC object, its
reference route, planning decision, all102 named currents, and all78 reference
routes. Every route maps to its own selectable route record; only the matching
editorial candidate is used, even for owners with several routes. Keyboard
current-to-card-to-SVG navigation, original source-byte addresses,320px reflow
and disabled seasonal playback pass. The own SVG screenshot was visually checked.
The first complete browser attempt found a test locator matching both the outer
accessible SVG and its nested map viewport. Targeting the outer role=img SVG
fixed the locator; the complete rerun passes. Earlier browser feedback exposed
the actual missing reference-route query map, now fixed and covered by Rust tests.

Preservation checks pass against4f964f6: all29 prior reports/producers and77
reference-route rows exact; all439 prior source descriptors unchanged and all441
current source hashes verify. Only the NwASC object/planning rows change; exactly
one route and one method source are added. Source index317,843,955original bytes,
48,670,398compressed bytes. No copyrighted original or source render is staged.
Fresh Linux evidence and final atlas-directory regression receipt follow below.

Atlas-directory regression passes:102 currents/140 eddies or detections, search,
map selection, keyboard, updates, shared gateways, empty results and320px reflow.
Nine superseded generated parts were individually hash/length/containment checked
and retired after all consumers finished; current parts and research originals remain.

### Fresh Linux and publication receipt

Scientific source commit31b9cd45575b07f0fee6cf0ba3a4e72e86b5c639,
run39745580870, scientific-reproduction job119713070243:SUCCESS.
All30 retained/rebuilt report SHA256 values match local exactly. This proves
reconstruction of the admitted source references, not independent reconstruction
of the original satellite observations. NetCDF job119713069984:SUCCESS.
Offline job119713070276 stops at Rotschi1972 paper-fixture acquisition:
https://horizon.documentation.ird.fr/exl-doc/pleins_textes/divers20-05/010028590.pdf
returns HTTP403 before tests. This supersedes the preceding Stramma1992 failure
as the latest acquisition blocker. No overall green/full-suite claim.

All428 raw staged engine pins and441 index-source hashes verify. GitHub accepted
the source push with a >50MB recommendation warning for the54,834,640-byte WASM.
The following receipt-only commit changes these two review documents, preserving
all source/data/engine/artifact bytes from the Linux-tested source head. Source
and receipts continue in existing draft PR83; no new PR and no main merge.
Full133-browser matrix and complete local suite remain unrun;4GiB guard unmet.
The internal seven-role review has no unresolved P1; broader suite coverage and
snapshot packaging/memory remain open P2 conditions, not external peer approval.
