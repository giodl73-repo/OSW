# Kuroshio Extension regional length series

Continuing branch `codex/current-measurement-gaps`, draftPR83. Published
baseline2abc1cb; no new PR or main merge. This scientific increment is local;
query/dashboard admission and the combined delivery build remain pending.

## Recovered evidence

Qiu, Chen and Oka2023, doi10.1029/2023GL103548, Figure2a supplies an upstream
regional pathlength graphic between141E and153E. The study's underlying SSH
period is January1993–December2022. Exact plot sampling cadence and calendar
observation dates are unresolved; graph positions remain approximate years.

The published graphic's rounded readings span **1120–4660km**, with an
editorial **+/-50km** length-reading allowance and **+/-0.1year** time-reading
allowance. These allowances cover graphics reading, not physical errors or
confidence limits. The graphic range is neither physical annual extrema nor
a seasonal envelope. Whole-current length, rank, geographic centerline and
physical width remain unresolved by this increment.

The complete factual command mirror retains1532 original line commands and
4 cubic commands in16 explicit runs. It yields1552 original graph-knot
records, including shared run endpoint instances, plus60 derived cubic graph
readings:1612 readings total. Derived cubic readings are not observations.
Two tiny source run-boundary overlaps remain exact and explicitly reported;
no points are shifted, averaged, dropped or joined to hide them.

## Source and prospective custody

Complete nine-page institutional original:5373944 bytes, SHA256
39a9f92f539ff164a6782915518bda2617b65c4fa0ba99e41bb41051bb9caa8d.
Only original pages1,3,4 were visually reviewed. The article stays private;
public products contain factual graph geometry, attribution and derived data.
The source-facts file is the retained pre-extraction snapshot; its false
red-trace-calibrated flag records that earlier phase, not current report status.

Frozen version history:

1. f323484: v1 rejected cubic operators before target calibration.
2. c82442e: v2 preserved cubics but rejected source stroke width against0.5pt.
3. 5da1cae: v3 retained0.6pt source strokes but rejected tiny boundary overlaps.
4. ef2b3b8: v4 records coordinate overlaps within the declared0.02pt tolerance.

Each producer, synthetic test, protocol and preflight was committed before
its original extraction. Every frozen version and failure is retained.
Raw graphics diagnostics, rather than calibrated length outcomes, motivated
the explicit corrections. V4 original extraction, build, byte check and
exact-original replay all pass. No frozen scientific product was edited.

## Products and local proof

- `research/source-data/ke-qiu-2023/figure2a-vector-trace-v4.json`: complete
  source commands and exact source custody.
- `research/ke-qiu-regional-plot-pathlength-v4.json`: complete readings,
  command/knot/readings counts, scope, allowances and immutable input pins.
- `figures/ke-qiu-regional-plot-pathlength-v4.svg`: all1612 readings and16
  separate run polylines, year/km axes, textual range, source and scope.

86 prospective synthetic checks pass across the retained versions. Seven
independent actual-source checks pass: complete input pins, original command
and knot accounting, Decimal calibration/rounding for every reading, cubic
readback, source overlap preservation, scope and all-point SVG accounting.
The standalone SVG was rendered with MuPDF and visually inspected; actual
browser, keyboard and phone behavior await query/card integration.

Reproduction:

```text
python analysis/ke_qiu_plot_pathlength_v4.py check
python -m pytest -q analysis/test_ke_qiu_plot_pathlength_admission.py
python analysis/ke_qiu_plot_pathlength_v4.py original --original-path ORIGINAL_PDF
```

Original replay needs PyMuPDF1.28.2 and the pinned private original. Default
report replay reads the public factual command mirror offline. Build refuses
existing products. A scientific correction requires a new version.

## Remaining delivery work

Expose complete regional series/readings and provenance in Rust/WASM query,
add chart/table/source access to the mapped KE current card, update the source
catalog, preserve all previous measurements/ranks/widths/routes, validate
complete native records before Chromium, and run focused keyboard/phone proof.
Register v4 as the39th active numerical replay target and collect fresh CI.
This is not yet counted as a delivered atlas measurement or a newly ranked
whole-current length. The current live atlas remains the verified Labrador
baseline until the combined delivery build succeeds.

Local work stays sequential at below-normal priority, one logical CPU and
one numerical/Cargo worker. No build/browser overlap. Full local regression
remains intentionally stopped until an exclusive final batch gate. Core
length, physical width, seasonal and identity/geometry gaps remain open.


## Query delivery prepared

The draft query contract exposes regional_plot_series as a partial length
evidence class. Whole-current evidence remains unmeasured, published length
and lower-bound fields stay null, and rank eligibility stays false. One
complete provenance header and1612 ordered graph-reading rows join the
working collections, alongside one scoped measurement/claim and two sources.
The mapped KE card offers chart, header, all-reading, source and assessment
links; no graph position is added to observed-date or seasonal capabilities.

The shared historical-table composition now accepts the exact KE assessment
only after complete native series/readings/dependency validation. Every other
current and all prior widths/ranks/routes remain bound. Sixteen focused
source/readback and atomic-admission checks pass. The planned serial build
is dashboard,535-document index,54-collection packet and native/WASM engine.
Expected working rows:108438, preserving106819 old rows exactly and changing
only KE assessment/card;1617 rows are added. Existing widths170, routes78
and qualified length ranks13 remain unchanged. Complete browser proof checks
all1612 readings over four pages after native CLI checks terminate.

The contract is a delivery mapping over frozen v4 products; it does not alter
the scientific calculation. Its explicit refresh happens only before any
consuming build. Native/engine/browser/preservation and fresh39-report CI
remain pending. No completed atlas-delivery or full-goal claim is made.


## Terminal local delivery (2026-10-23)

The complete serial dashboard/index/packet/engine pipeline passes. All143
Rust unit tests pass, complete native atlas validation passes before WASM
compilation, and the49108081-byte WASM engine is built. The logical packet
is186941950 bytes in12 current parts. The535-document source index preserves
all524 prior descriptors and source bytes exactly.

Preservation proves106819 old rows exact, only KE assessment/card changed,
1617 rows added and108438 total rows in54 collections. All627 prior protected
source/method inputs remain byte-identical. Two explicit native delivery files
(lib.rs and shared assessment-overlay registry) change, four generated runtime
assets are replaced, and12 superseded generated transport parts are verified
and retired. All671 current engine pins verify. Widths170, routes78 and
qualified whole-current length ranks13 are unchanged. The card changes only
its claim/source/measurement counts, IDs, fingerprints and five evidence links;
no date, geometry, route, width or seasonal capability changes.

All102 focused synthetic/source/admission checks pass. The isolated browser
proves complete native/WASM header and all1612 readings over four pages,
four individual core/source records, unchanged ranks, keyboard navigation
and320px reflow. The actual Chromium card and chart screenshots were visually
inspected. No original PDF/NetCDF/ZIP/XML download occurs. Native CLI checks
finish before Chromium starts; query and atlas workspaces are reused.
The resource monitor reapplies one-CPU/below-normal limits when a Chromium
helper resets its process settings. No heavy local job remains.

Private terminal receipts are under .pytest_cache/ke-qiu-delivery: serial-build
and serial-checks state files, preservation-result.json and browser/result.json.
The generic evidence-class rules are recorded in
plans/regional-current-length-series-admission-rules-v1.md. Staged-byte proof
and same-PR publication follow. Fresh39-report and source/UI CI remain pending
for the new delivery head; the full exclusive regression remains open.

Staged-byte proof: PASS for992 unique Git index blobs covering671 engine
pins and535 source documents. All overlapping descriptors agree; no frozen
scientific bytes differ. Same-PR publication and fresh remote CI follow.

## Verified remote follow-up for f83557e

The subsequent pushed delivery head f83557e93386f781ccfefc69ceba7d54ac58532c
has a terminal successful scientific-reproduction job 120560188175 on run
39996182669. Its downloaded log contains all 39 scientific report records,
each with exact encoded bytes. This is verified previous-head evidence, not
CI for later Caribbean source commits. Conformance and NetCDF fixture jobs
also succeeded. Offline stopped during acquisition of the original Stramma
1992 South Indian paper with HTTP 403 before tests. Front-level-atlas remained
authoritatively in progress when polled on 23 October; do not infer its result.
