# REDSOX Section 3: another observed section

Continuing branch `codex/current-measurement-gaps`, existing draft PR #83.
Base commit `cefddd5261d6df7f2f63f053939a11d4d8f49716`. No new PR or main merge.

## What this fills

The original winter cruise report supplies a second, explicitly identified
cross-channel section. The twelve source-ordered casts span 22–23 February
2001. The declared experiment retains 30 outcomes, including 20 unresolved
results. Ten southern-branch local component spans have paired observed
brackets; the northern branch remains unresolved at every convention.

| Layer above bottom | Southern half-peak span | Northern half-peak span |
|---|---:|---|
| 20–60 m, primary | About 5.0 km | Unresolved |
| 10–50 m | Unresolved | Unresolved |
| 40–80 m | About 5.5 km | Unresolved |

The primary southern peak is cast 73, with mean practical salinity about
39.01 source psu. Station 74 supplies a velocity bracket but has no CTD
companion. Casts 61 and 63 have uninterpretable velocity references; cast 63
also has unresolved treatment of a rejected downcast. None is reinstated.

Primary-layer 40/50/60% spans are about 6.0/5.0/4.0 km. Uniform component
offsets of -0.03/+0.03 m/s give about 4.7/5.3 km at half peak. The deeper
layer's 40% span reaches about 12.6 km: sensitivity is substantial and is
displayed, rather than collapsed into a favorable narrow envelope.

The section bends, so each station's projected component uses a different
local normal. Both original Earth-frame components and each normal direction
remain available. Changes in projection can contribute to component changes;
the chainage span is not a verified flow-normal physical width. Sparse station
spacing, non-synoptic sampling and unremoved tides remain limitations.

## Preserved boundaries

The previous casts 7–11 lower Northern Channel experiment, its roughly 6 km
secondary-layer estimate and its unresolved primary stay unchanged. The new
5 km observation is not the published bathymetric channel breadth: it comes
from velocity-profile threshold crossings, with a separate metric and epoch.

No whole-current width, annual range, ranked physical measurement, current
axis or physical state intersection is admitted. The physical width inventory
is unchanged. The positive local observations reduce an observational gap;
they do not close the current's complete physical measurement gap.

## Reproduction and presentation

The preflight is `plans/redsox-section3-width-protocol-v1.md`.
The reviewed source receipt pins the cruise report, original LADCP README,
station extraction and protocol; original report imagery is not redistributed.
The data producer verifies both pre-existing NCEI archives and parsers.

Run, in order:

```text
python analysis/build_redsox_section3_spans.py
python analysis/build_redsox_section3_figure.py
python analysis/current_research_evidence.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
python -m pytest analysis/test_redsox_section3_spans.py analysis/test_redsox_lower_nc_section.py -q
python analysis/test_redsox_section3_browser.py
python analysis/inspect_scientific_reproduction.py
```

The Red Sea current card offers the original section view and this new
map/component/salinity/sensitivity figure through its existing analysis-view
control. All three layers and thirty cases are queryable through the source
index with the actual Rust/WASM engine. Public summaries round km to one
decimal. Machine precision is a reproducibility convention, not uncertainty.
The fact labels identify the earlier northern section separately, so its
unresolved primary cannot be confused with the new southern primary estimate.
Browser checks use the standard `OSW_TEST_BROWSER` override if the
Playwright-managed Chromium executable is not installed.

## Gate status

At preparation, 15 focused checks pass. Native/WASM rebuild, browser and
preservation results are recorded when terminal. The clean combined full
suite at base `cefddd5` continues in a separate checkout: its status must not
be relabeled as coverage of this new batch. Independent Linux reproduction
of the base passed all thirteen prior reports byte-for-byte; the new report
is added as target fourteen for the next run. Keep PR #83 draft while required
final gates remain outstanding. This document does not claim external
scientific review or completion of the broader gap-filling program.

### Terminal checks for this batch

* 18 focused checks pass, including the old lower Northern Channel tests,
  independent WGS84/normal-sign and edge readbacks, missing-data barriers,
  changed-source/figure rejection and complete research-index registration.
* 79 Rust tests pass; locked native/WASM builds and native atlas loading pass.
* The actual browser matches all 30 nested cases against native Rust, with
  all 20 unresolved outcomes retained. Keyboard figure selection, distinct
  earlier/new section labels, export and 320px reflow pass. No automatic
  original-file requests or page errors. The browser executable uses the
  documented `OSW_TEST_BROWSER` override.
* Preservation against `cefddd5`: other 43 collections, 239 objects,
  48 diagnostics and 386 indexed documents remain exact. Old REDSOX reports
  and canonical dimensions are unchanged. Widths155 / samples463 / routes76.
* Index390 documents, 281,912,254 original bytes, 45,877,683 compressed bytes.
  Main packet90,263,162 bytes; WASM16,861,364 bytes.

The base remote scientific job passed all thirteen prior reports. Its offline
job118984170297 subsequently failed during acquisition, before tests, when
the Qiu/Chen2010 original and institutional mirror both timed out after
transport retries. This is separate from the running clean local full suite
and the new fourteen-target scientific job. Neither failure nor pending work
is waived or relabeled green.
