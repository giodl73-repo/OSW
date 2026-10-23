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
