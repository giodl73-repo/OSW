# REDSOX Section 3: repeat survey and unresolved seasonal comparisons

Continuing draft PR #83 on `codex/current-measurement-gaps`. Base commit
`720135e593403fcb8d691b92531f1560bae569de`. No new PR or main merge.

## Additional observations

The original summer cruise report Figure 7 top panel (printed/PDF page 19)
identifies stations 18–29 as Plume Section 3. They correspond in source order
to all twelve winter section stations, with each original pair within 0.3 km.
The original report rendering was checked: PDF text-object extraction order
alone would have confused the transverse and along-rift panels.

The summer data cover 23 August 2001, roughly 08:00–21:00 UTC. This repeats the
geographic station context of 22–23 February, without assuming identical
positions or interpolating across dates. Both mean velocity components,
local section normals, hydrography, timestamps, exclusions and all thirty
fixed cases are retained in the new report. The winter report remains exact.

| Summer outcome | Result |
|---|---|
| Primary 20–60 m northern half-peak component span | About 3.1 km, conditional association |
| Northern 40/60% component spans | About 3.9/2.4 km |
| Northern +0.04 m/s half-peak scenario | About 3.9 km |
| Northern −0.04 m/s scenario | Peak falls below 0.2 m/s floor; span unresolved |
| Primary northern peak salinity | About 37.41 source psu; unchanged 38 psu screen fails |
| Southern branch, all layers/conventions | Unresolved: cast 22 quality treatment unverified |
| 10–50 m layer | Incomplete observed endpoint support |
| 40–80 m northern branch | Peak below component floor |

Four summer component spans are finite, 26 outcomes remain unresolved. None
passes the unchanged saline-outflow screen; the roughly 3.1 km value is not
promoted to a verified named-current width. The screen failure does not prove
the outflow is absent. Lower summer salinity was visible before declaration;
the threshold was not lowered after seeing the candidate.

## What the comparison establishes

Six same-branch, same-layer half-peak comparisons are retained, all unresolved.
Winter's supported southern spans are never paired with summer's northern
candidate to fabricate a seasonal change. The current's annual width range,
whole-current physical width and physical state joins remain unknown.
Unremoved tides and non-synoptic sampling further limit interpretation.

The figure shows both dates side by side, with identical component/salinity
axes, source gaps and excluded values marked separately. The summer negative
component minimum is fully visible; a preliminary clipped axis was corrected
before publication. All three layers retain distinct markers/line styles.
The current card adds this analysis view, a branch-separated comparison table,
the candidate's failed-screen label, source-case queries and matched positions.

## Structured measurement inventory

The shared `current_section_measurements` collection adds all 60 declared
cases from the two frozen reports to the main Rust/WASM query API. It retains
14 finite local spans and 46 unresolved outcomes, including every failed
salinity or component-quality screen. These are local section metrics; the
published scoped-width inventory and whole-current width remain unchanged.

Records have stable IDs, current-owner links, dates, branches, height layers,
thresholds, velocity offsets, source status, exact source cases and file/pointer
provenance. The current card links directly to the query table. Public values
are rounded to one decimal with failed-screen labels; exports retain numerical
readbacks. Primary conventions can be filtered without hiding other cases.
The existing Antilles-specific section table is preserved. See
`plans/current-section-measurement-records-v1.md` for the record contract.

## Reproduction

The operator declaration is
`plans/redsox-section3-repeat-survey-protocol-v1.md`. Source selection pins the
original summer PDF and frozen winter report. New calculations use the same
verified original ASCII archives. No original report imagery is redistributed.

The v1 measurement case operator is retained locally, with a regression check
proving exact identity to the frozen winter operator after station renaming.
This avoids rewriting the already published winter source/generator graph.
Changing either v1 method requires an intentional protocol revision.

```text
python analysis/build_redsox_section3_repeat.py
python analysis/build_redsox_section3_repeat_figure.py
python analysis/current_research_evidence.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis/test_redsox_section3_repeat.py analysis/test_redsox_section3_spans.py analysis/test_redsox_lower_nc_section.py -q
python -m pytest analysis/test_current_section_measurements.py -q
python analysis/test_redsox_section3_repeat_browser.py
python analysis/inspect_scientific_reproduction.py
```

The standalone browser check uses the standard `OSW_TEST_BROWSER` override
when Playwright-managed Chromium is not installed. The new report is
independent-reproduction target15. Base720135e passed all14previous reports
byte-for-byte on Linux (job118996488297, run39530964516); this does not prove
the new report's Linux result.

The clean full test process remains alive at basecefddd5 in its separate
checkout; preserve its CLI and fixtures. Previous8399af0full is terminalPASS
(1856tests/1222subtests). Keep the ongoing PR draft and report new focused,
build/browser, preservation and remote gates at their actual terminal scope.
The broader current inventory, measurement and visualization goal remains active.

## Terminal batch checks

* 29 focused checks pass, including unchanged winter/lower-channel results,
  operator parity, branch comparisons, provider rejection and all typed cases.
* 81 Rust tests pass. Locked native/WASM builds and the native atlas load pass.
* Actual native/browser WASM results match all 30 summer cases, six unresolved
  comparisons, twelve station pairs and all 60 normalized query records.
  Primary filtering returns four cases. Numeric/failed-screen table values,
  record-source and atlas links, two analysis views, export and 320px reflow
  pass, without automatic original requests or page errors.
* Source/build/index custody: 701 staged blob pins match the exact files.
* Preservation against `720135e`: all 14 prior scientific reports, 43 other
  collections, 239 other objects, 48 other diagnostics and 389 indexed
  documents remain exact. The new typed collection has 60 records; the source
  index has 393 documents. Widths155 / samples463 / reference routes76 remain
  unchanged. Catalogue subject IDs and verified flow association are distinct.

The browser test initially assumed provider order, while the documented query
engine defaults to stable ID order. Native and browser records already agreed;
the expected list now uses the engine's ID ordering and still compares all
sixty complete records exactly. No data or validation predicate was relaxed.

Current-head independent Linux target15 and the final clean full remain
separate gates. The broad program is not marked complete by this local batch.
