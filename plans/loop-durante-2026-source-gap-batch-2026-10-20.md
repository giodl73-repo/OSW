# Loop Current author-processed source coverage

Baseline5633d093585901fb83d9b5498b2b628f0043a7aa. Continue the same branch
`codex/current-measurement-gaps` and draft PR83. No per-gap PR or main merge.

## Source recovered

Durante2026, Zenodo22652650, DOI10.5281/zenodo.22652650, public record version0,
published8September2026. Original data.zip is14,212,662bytes, provider
MD5db5a3615a6b103ff8b2311530785e0c0 and SHA256
2594682dcaa2e007d7d46de8f17344ce5c269dcc91cf64423fabc4a2c01a8a24.
Every member CRC and declared size/path was checked. The complete ZIP remains
in ignored acquisition storage; the selected original member is retained:
`data/Figures2_4_processed.mat`,3,201,419bytes, SHA256
316daa53a45fc6b2817abfa4ba8da76344323d20c84c781bfa8705163235e073.

The retained API snapshot declares CC BY4.0. README still carries a pre-release
license-selection TODO; CITATION.cff says1.0.0 while the record says0; manuscript
DOI is a placeholder. These disagreements remain visible and no peer-reviewed
publication claim is inferred. Original metadata, dictionary and source/code
archives are preserved with hashes. MATLAB scripts were read, never executed.
Their author-local paths are not dependencies of the OSW import or derived UI.

## What the data actually supports

Twenty-five selected numerical fields preserve HDF5/MATLAB shape association,
native numeric bits and masks. Positive/negative surface speed/U/V composites
and ADT fields are source-processed configurations, not seasons, forecasts or
dated raw fields. Per-member support for the composites is unavailable here.

Two248-point coordinate means extend from the Caribbean toward Yucatan. Their
northernmost points are22.69N/23.14N, respectively, and the supplied coordinates
do not trace a complete Yucatan-to-Florida Loop path. The author averages
coordinates pointwise with omitnan; underlying daily coordinates and per-point
support are unavailable. OSW shows every supplied point without joining them.
These arrays therefore do not close the missing Loop reference-route gap.

The three distinct source clocks are preserved:

| Field | Entries | First / last finite calendar | Missing times |
|---|---:|---|---:|
| tid | 4,111 | 2011-05-11 / 2023-07-10 | 0 |
| tisp | 4,111 | 2011-05-11 / 2023-07-10 | 1 |
| htimef | 11,902 | 1993-01-01 / 2025-08-02 | 0 |

tisp has no time at zero-based OSW position3462 (MATLAB index3463). Original
phase/grid selection indices remain one-based MATLAB indices; clock-block
positions and JSON array positions are zero-based, explicitly encoded. No
index or source datum was moved to make these conventions agree.
The initial assumption that
concurrent clocks were identical failed validation. Import was corrected to
preserve the distinct arrays, matching the preflight rule; no missing time was
filled from tid. Finite paired times agree. Calendar timezone is unspecified.
The333-day calendar gap in tid and the missing tisp entry remain explicit.

area_loop and AMR_loop are retained unscaled under their source identifiers,
with their author plotting-unit evidence. No length, width or occupied-current
polygon is derived from these scalars. Source clocks are not assigned as dates
of complete current paths. Old observation dates do not change.

## Atlas delivery

The [source map and clock sheet](../figures/loop-durante-2026-source-view.svg)
uses both complete supplied grids, a common source-speed scale, fixed-stride
direction arrows, unjoined coordinate points and gap-preserving clock blocks.
No source figure is copied. Gray denotes missing source data, not coastline.
The plot is rendered and visually inspected; its exact transformed inputs,
original clock values and unscaled scalar series are in
[the source-view record](../research/loop-durante-2026-source-view.json).

The existing shared research-evidence interface exposes this on the Loop
current card, seasons page and diagnostic query, with direct source pointers.
`diagnostic:current-research:loop` remains evidence, not a width or route.
The compiled Rust registry binds the exact quality document, source/method
inputs, figure and owner join. The full source view is support-only and cannot
be used as inventory width evidence. Six JSON documents join the checked index.

The index now has376documents; research registry50documents and6scenes.
The main packet contains49diagnostics. The Loop diagnostic embeds its quality
summary; its full source matrices are available through the checked index.
Exact bundle sizes and input hashes are recorded in the engine manifest and
the local verification receipt.
Final main packet:90,258,544bytes; WASM:16,849,153bytes. Index corpus:
268,747,675original bytes /42,255,731compressed bytes.

## Preservation and checks

All48older diagnostics and five older research scenes are unchanged by value.
All other239objects/dashboard entries, every other collection and every latest
observation date are unchanged. Width-inventory bytes,155width records,
463old samples,76reference routes and28series remain unchanged.

- Source/value/view tests:15passed in1.75s. All selected source values round-trip
  their MATLAB/HDF5 storage association, including original missing values.
- Existing shared research tests:7passed/2subtests in32.96s after source-index
  registration. The initial missing-index failure is resolved; assertions stay.
- Browser-runner environment:2passed/2subtests in0.24s.
- Final combined focused run:24passed/4subtests in36.70s. A refresh helper's default
  Windows encoding initially corrupted existing captions; explicit UTF-8
  reads restore them. The exact older-diagnostic preservation check is retained.
- 79Rust tests, locked native/WASM builds and actual native atlas loading pass.
- Actual shipped-WASM browser passes all3views, keyboard/320px, complete phase,
  clock and scalar rows against native,6packet corruptions and1index corruption.
  No source originals are downloaded by normal page use.

The clean ce3cb2c full analysis gate passed1,826tests/1,164subtests in3184.08s,
finished20October2026at22:17:31UTC. It predates both the5633d09UI and this batch.
A clean successor full gate must cover the combined latest changes.

Reproduce offline:

```powershell
python analysis/acquire_loop_durante_2026.py
python analysis/build_loop_durante_source_view.py
python analysis/current_research_evidence.py
python -m pytest analysis/test_loop_durante_2026_source.py analysis/test_loop_durante_source_view.py analysis/test_current_research_evidence.py -q
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_loop_durante_source_browser.py
```

## Other lead and remaining work

Azores Countercurrent: public HAL metadata has no attached original; its
document URL returned404. NERC105943 explicitly has no full text. The existing
Alves2002access audit is unchanged. A separate Carracedo2014Figure2preflight
was recorded after overview inspection, but quantitative crossing calibration
was not executed and no measurement/failure rows are invented. That figure is
a set of boundary sections and cannot itself establish longitudinal route
geometry. No prior2009width or Azores Current value was altered.

Next scientific work can test the now-available composite ADT/velocity fields
against explicitly declared gateway-connected path methods. The author's
0.55m plotted ADT guide is not the Manta0.17m demeaned daily method or a
maximum-velocity algorithm; any proxy measurement needs its own method/scope
review. Do not use the incomplete coordinate means to fill a Loop length.
The19unconstructed route owners and broader dimension/source gaps remain
active. This source recovery and atlas integration do not complete the goal.
