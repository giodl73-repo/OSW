# Jutland thesis and cited satellite widths

## Source review

Original agency-hosted DMI Scientific Report 00-15:
https://www.dmi.dk/fileadmin/Rapporter/SR/sr00-15.pdf

Mads Hvid Nielsen (2000), *Dynamisk beskrivelse og hydrografisk klassifikation
af Den Jyske Kyststrøm*, reprint of April 1999 University of Copenhagen thesis.
The original preface (PDF p3) confirms the reprint link and October 2000 issue;
only typographical corrections and summaries were added. ISBN 87-7478-425-0.

Original: 4,292,648 bytes / 144 pages, SHA256
`29e027afd56877b6acec02382a8a6a2e5b2ecce24572171c2e15c1f1ae071525`.
Selected original PDF pages 1,3,7,22,23,71,140 visually inspected. No full-report
review, image diagnosis, independently validated translation or license to
redistribute the original is claimed; PDF stays ignored.

## Three scoped descriptions

Section 2.4, printed p14 / PDF p22, attributes three widths to satellite images
and cites Aarup (1994a):

| Site | Reported width | Scope |
|---|---:|---|
| Thyborøn | 40 km | One cited image estimate; image date/threshold unresolved |
| Hanstholm | 25 km | One cited image estimate; image date/threshold unresolved |
| Hirtshals | 20–25 km | One reported span; no selected midpoint or annual extrema |

Aarup (1994a), *Satellitbilleder af danske havområder*, Havforskning 42, is
listed separately from the English series 52 thesis in the bibliography on
printed p132 / PDF p140. Its original images and methods remain unreviewed.
No sensor, pixel uncertainty, salinity threshold, velocity threshold, transect,
fixed depth slab or width occupation date has been inferred.

Section 2.4.1 discusses freshwater-influence and hydrographic-flow definitions;
neither supplies the satellite threshold. Section 2.4.2's mainly mixed-water
description and local bathymetry do not define image sampling depth. Section
7.3.3 qualitatively infers midsummer widening from German Bight-water fractions
at different coast distances; this is separate from numeric width observations.
Do not animate the three dimensions, assign them to months or pool them into
annual extrema. North/South labels remain unresolved; canonical naming unchanged.

## Later source reconciled

The DHI 2019 10–20 km Henne Strand–Skagen water-mass band remains a separate
description. Its bibliographic link to the Nielsen thesis is now established;
the exact figure was not corroborated by the inspected Nielsen width passage.
That source review state is updated on the existing card, audit and inventory.
It is not a claim that every page of the thesis lacks the phrase. Do not replace
the later report's value with 40 km or merge different sites/operators.

The unchanged DHI PDF, thesis PDF, receipts, protocols, full source rows,
comparison and naming audit are pinned. One owner now has two source audits.
The Rust registry resolves the source by the immutable reviewed record identity,
so the current owner alone cannot select or substitute the wrong source.

Coverage: **109 scoped descriptions / 58 owners / 34 unassessed**. These counts
include geographic summaries; they are not complete measured current dimensions.
105 prior non-Jutland descriptions remain unchanged. The DHI record only gains
reviewed source context, not a new scalar or seasonal support. Canonical ledger,
reference routes and naming audit stay unchanged; frames refresh only their
inventory dependency. Lossless source corpus: **130 documents**.

## Verified parent failures and fix

PR65 companion run 37904303040 reached the browser suite after successful
source acquisition, native build, standard-library and full pytest gates.
The width cards, 39 collections, dashboard, source queries and several other
browser gates passed. The run then failed in
`test_seasonal_atlas_navigation_browser.py`: it expected the West Australian
Current to have no selected phase after an unrelated Monsoon phase request.
That assertion predated its added scoped breadth record. The UI correctly
selected its own record. The updated test verifies the exact owned record,
current identity, selected option and disabled seasonal playback, preserving
the intended rejection of the unrelated phase.

PR66 push run 37906888735 failed earlier during acquisition: Geomar's Zenk
original returned HTTP403. NetCDF job passed. No source pin, fixture check or
HTTP403 behavior is loosened by this batch. These are distinct verified failures.

PR66 companion pull-request run 37906905633 also failed during acquisition,
after three Qiu/Chen NEC original-download timeouts. Its NetCDF job passed.
Neither PR66 run reached the content tests; local validation below is separate
from these remote failures.

## Regeneration

```powershell
python analysis/acquire_local_paper_fixtures.py
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest -q
$env:OSW_TEST_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python analysis/test_jutland_satellite_widths_browser.py
python analysis/test_jutland_water_mass_breadth_browser.py
python analysis/test_seasonal_atlas_navigation_browser.py
```

The new browser check is registered in the shipped WASM runner. Internal roles
review is not independent scientific admission. Original Aarup imagery and
comparable dated geometry remain required scientific work.

## Validation outcome

- Full Python suite: **1,076 tests and 918 subtests passed** in 463.51 seconds.
- Rust: **41 tests passed**; native and WASM builds succeeded.
- New satellite browser and existing DHI browser: passed scoped cards, mobile
  reflow, source/inspector/query parity and coherent native/WASM rejection.
- Seasonal navigation: **100 current links, 64 route-card links, 117 phase
  deep links and six round trips passed**, including the corrected owned-phase
  assertion, share/update/reset and mobile reflow.
- All 48 JavaScript modules passed syntax checks; all 14 page assignments passed.
- Original DMI download verified against its pinned bytes and checksum.
- Dependency comparison passed: 105 non-Jutland descriptions and other dashboard
  entries unchanged; DHI numerical support unchanged; ledger/routes/naming
  unchanged; only the seasonal-frame inventory dependency refreshed.
- Mobile four-card screenshot visually reviewed. Source corpus contains 130
  documents; query bundle is 46,382,675 bytes and WASM is 2,029,915 bytes.

Publication is a draft stack above PR66. This batch does not close a new current
owner, supply seasonal width margins, or complete the full core-data objective.
