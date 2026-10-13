# Solomon / New Ireland coastal confinement batch

## Original acquisition and review

Melet, A., L. Gourdeau, W. S. Kessler, J. Verron and J.-M. Molines (2010),
*Thermocline Circulation in the Solomon Sea: A Modeling Study*, Journal of
Physical Oceanography 40(6), 1302–1319, doi:10.1175/2009JPO4264.1.

Repository original:
https://hal.science/hal-00534041v1/file/2009jpo4264_2E1.pdf

19 PDF pages: HAL cover plus 18 journal pages. The cover records deposit on
6 June 2014, distinct from article publication in June 2010. Original bytes
6,048,321; SHA256 `9d41af95d2ccbcee1e1469ea45d703d9cb1005ce6d1701896f4a94b5e8f1da3d`.
Selected original PDF pages 1–8, 13–16 and 19 visually inspected: provenance,
model/layer/period context, Figures 1/4/9/11/12 and the confinement passage.
No full-study reproduction or source velocity/axis digitization claimed.
The first journal page bears AMS copyright; HAL Authorization does not establish
a redistribution license. Original stays ignored; receipt and annotations ship.
Fresh acquisition through the registered helper reproduced the pinned bytes.

Publisher PDF endpoints returned HTTP403; Crossref's old article-PDF endpoint
returned HTTP404. HAL's actual file link and API supplied the original; none of
those errors was bypassed or accepted as a PDF.

## Source-defined records

| Canonical owner | Source relation | Evidence class | Representative width |
|---|---|---|---|
| Solomon Island Coastal Undercurrent | within 100 km of eastern coast | Original model prose | unknown |
| New Ireland Coastal Undercurrent | within 40 km of eastern coast | Original paper's citation of Butt/Lindstrom (1994) observations | unknown |

Section 5c, printed p1315 / HAL PDF p15, supplies both relations. They are
one-sided coastal confinement descriptions. No 100 km or 40 km full-width
point, zero-to-scale interval, hard upper bound, confidence interval, seasonal
range or geographic buffer is admitted. Both numerical width fields remain null.
The source's plural SICU name is retained through its citation; the canonical
singular current ID/name is unchanged.

The NICU original cruise paper, *Currents off the east coast of New Ireland,
Papua New Guinea, and their relevance to regional undercurrents in the western
equatorial Pacific Ocean*, Butt and Lindstrom (1994), JGR 99(C6), 12503–12514,
doi:10.1029/94JC00399, remains unacquired after actual publisher HTTP403.
Melet's citation is not independent review of that paper. Other accounts use
"40 km width"; their wording is not used to replace the inspected relation.

## Support distinctions

Nested NEMO/OPA 1/12-degree model, 46 z levels; 1984–2004 simulation with first
two years for adjustment and 1986–2004 climatology. Daily outputs feed the mean
and monthly transport cycle. Those periods are not width observation dates.
Thermocline sigma 24.0–26.5 varies in depth, approximately 100–400 m (printed
p1306); it is not a fixed depth slab. Model SICU core near 200 m/20 cm/s is
distinct from cited NICU core 235 m/60 cm/s and separate modeled NICU maximum
65 cm/s on sigma 25.5. The model's 154.5 E transport integration gate is not a
paired width boundary. Transport standard deviations and calendar extrema are
not width error or width seasonality. Gateway dimensions remain separate.

Figures 4, 9 and 12 establish source model geography and section meaning; no
axis, threshold contour or paired edges are digitized. Existing geographic
reference paths and earlier scope audits remain historical artifacts unchanged.
This new audit records the newly recovered original explicitly. No dated
footprint or physical OSW-state intersection is derived.

## Data / implementation

**111 scoped descriptions / 60 currents / 32 unassessed**. This assesses two
previously unassessed owners for a qualified description; full measured widths
remain unknown. All 109 prior descriptions, other decisions and dashboard
entries are unchanged. Canonical ledger, reference paths and historic scope
audits unchanged; seasonal frames refresh only the inventory dependency.

One audit covers two owners. Rust matches reviewed record identity and its
source owner before source selection, preserving the preceding Jutland case of
two audits for one owner. Known IDs cannot move owners by erasing context.
Python owner guards, complete reviewed-row comparisons and coherent native/WASM
mutation tests enforce support bounds. The generic constraint renderer now
uses the scoped accessible description and correct array pointer; existing
NGCU size and West Australian offshore-breadth descriptions retain their grammar.

Atlas and inspector cards display "Coastal confinement", source relations,
evidence class and unknown widths. No bar, paired edge locator or playback.
Source index grows to 132 documents; the browser check is registered in the
shipped WASM runner. Scientific review remains separate from editorial roles.

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
python analysis/test_solomon_coastal_confinement_browser.py
python analysis/test_jutland_satellite_widths_browser.py
python analysis/test_original_regional_widths_browser.py
python analysis/test_seasonal_atlas_navigation_browser.py
```

Validation results are recorded after completion. Draft publication is above
PR67; this batch does not complete the core-data objective or mainline release.

## Executed validation

- Full Python suite: **1,107 tests and 918 subtests passed**, 444.01 seconds.
- Rust: **41 tests passed**, native/WASM builds succeeded. Shipped WASM is
  2,044,184 bytes; query bundle 46,408,347 bytes.
- New confinement browser passed both atlas/inspector cards, 320 px reflow,
  rendered font sizes, source-query/native parity, disabled playback and coherent
  native/WASM scope rejection. Both mobile screenshots visually reviewed.
- Prior Jutland satellite browser passed the two-audits/one-owner regression.
- Original regional-width browser passed existing points/spans, Kuroshio
  Extension averaging, NGCU qualified constraint and West Australian breadth;
  mobile cards, source queries and coherent native/WASM scope guards passed.
- Seasonal navigation passed **100 current links, 64 route-card links, 119 phase
  deep links and six round trips**, plus share/update/reset and mobile reflow.
- Fresh original acquisition, all dependency comparisons and source pins passed.
- All 48 JavaScript modules passed syntax checks; all 14 pages retain validation
  assignments; Python compilation and whitespace checks passed.
- Source corpus: 132 documents / 76,435,055 original JSON bytes /
  5,451,792 compressed bytes.

Existing mixed line endings were restored per unchanged source line during
review, with an assertion that code content was unchanged. No generated source
pin changed; dependency verification passed after that preservation.

The editorial validation condition is satisfied. PR67 remote push and companion
runs 37908835254 / 37908849086 had both passed acquisition, native build,
standard-library and full offline-suite gates when inspected; both shipped
browser jobs remained running. Both NetCDF gates passed. Remote results are
separate from this batch's local checks and mainline admission.
