# Portugal ORCA section-span preparation

Status: source-bound candidate prepared; **not registered in the product**.
Continue on `codex/current-measurement-gaps`, draft PR83. No new PR or merge.

## Result

The existing reviewed Portugal event supplies two nominal section limits.
Their WGS84 inverse-geodesic separation is115.71427424571638 km, displayed as
approximately116 km. This adds an independently reproducible candidate local
section span, with an explicit method and graphic; it adds no whole-current
dimension or annual range.

Protocol: `plans/portugal-orca-section-span-protocol-v1.md`.
Audit: `research/portugal-perez-2013-orca-section-span-scope-audit.json`.
Checker: `analysis/check_portugal_orca_section_span.py`.
Graphic: `figures/portugal-orca-2009-section-span.svg`.

## Evidence limits

Primary DOI10.1002/jgrc.20227 was reviewed as publisher HTML and institutional
PDF parsed text. All four attempted direct acquisition paths returned403;
page-image requests also failed. No original PDF bytes, PDF checksum or visual
original-page review is claimed. The unchanged local source-event file is
checksummed, and the event is matched exactly before calculation.

The two nominal geographic limits define a section span, not an observed axis,
physical boundary polygon or flow-normal whole-current width. WGS84 is an OSW
calculation assumption; source datum and coordinate uncertainty are unknown.
Cruise dates are context only; exact section days and fixed metre layer remain
unresolved. Transport error is not width error. The independent40 N component
diagnostic remains separate.

## Verification

- `python -m pytest analysis/test_portugal_orca_section_span.py -q`:
  **20 passed in0.42s**. Covers coordinate conversion and rejects current
  identity, temporal, depth, uncertainty, physical-width and provenance
  promotions, including deleted/duplicated records and a forged audit.
- Independent reverse-endpoint geodesic agrees; nominal separation is115.714 km.
  The37 N parallel arc is115.715 km, a calculation-choice difference rather
  than a physical error interval.
- Standalone640x420 SVG rendered in Chrome and visually inspected: source
  limits, calculation, time qualification and whole-width limitation visible.
  This is not a claim about integration into atlas, query or mobile cards.
- Product data, generated pages, native executable and WASM were not changed.
  The active full run47326 continues against the148-record South Atlantic
  checkpoint; its results cannot be attributed to this later candidate.

## Remaining registration work

1. Decide and preserve the dedicated calculated-section evidence type in the
   complete inventory checker and native/WASM admission rules.
2. Register source, decision, provenance and chart in existing atlas/query/card
   flows; retain the separate surface-component diagnostic.
3. Verify compiled parity, coherent invalid-input rejection, source navigation,
   mobile and reduced-motion behavior; recompute coverage only after admission.
4. Retain the raw-original recovery gap explicitly, including on the card.

## Concurrent publication state

The full148-record suite is still active; preceding147-record suite passed
1512 tests and1061 subtests. Latest remote run39083859720, head5212c8e,
fails at unchanged Qiu/SOEST acquisition with timeout, after prior remote runs
had acquired that exact pinned paper successfully. A previous run reached the
Reading VanAken source and failed there. Do not describe remote acquisition as
passing or relax either source pin to hide provider failures.
