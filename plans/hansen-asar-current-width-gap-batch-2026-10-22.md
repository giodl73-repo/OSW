# ASAR local surface-width evidence batch

Working branch:codex/current-measurement-gaps. Continue draft PR83; no new PR
and no main merge. This adds measurement evidence, not a completed inventory.

## Source evidence

Hansen etal(2011),doi:10.1029/2011JC007375, original13-page publication from
[IFREMER Archimer](https://archimer.ifremer.fr/doc/00056/16771/), original
file14216.pdf,3,067,007bytes,SHA256
d17a4411e92d5603c1692583a7740b1dcde0048a794617118cfa9fa606027584.
Original pages3-5 visually reviewed, including paragraphs9-12 and Figure2.
Copyright2011AGU: original PDF and rendered pages remain private and ignored.
The public receipt, factual records and independent SVG contain no original
figure or publication text. No author contact or external approval claimed.

## Added records

| Owner/location | Report | Scope |
|---|---|---|
| NwASC/P1 |60km| FWHM of the local mean surface range-Doppler profile |
| NwASC/S1 |36km| Conditional separation from NCC using the200m isobath |
| NCC/Haltenbanken-Froya |about30km| Local surface-jet description; boundary operator not explicitly restated |

All use the source's August2007-July2010 weighted mean surface field. This
is a width of a mean field, not an average of instantaneous widths or a
seasonal sequence. Broader2007-2011 acquisition dates are not substituted.
The5km output grid is distinct from10km spatial resolution; velocity RMSE
does not supply a width error. Exact occupation dates and fixed depth slabs
remain null. The200m contour is bathymetry, not the current's sampling depth.

Retain45km P2 as possibly mixed context and60km S1 as an explicitly combined
NwASC/NCC profile. Neither is admitted as an isolated current width. Do not
subtract36from60 to infer an NCC width or turn30-60into an annual envelope.
No whole-current width, geographic edges, route, seasonal playback, physical
state join or NASA identification follows. Source reference positions are
points of discussion, not interpolated current axes or boundaries.

## Integration

The previous v0.3live export remains byte unchanged. The new
research/ocean-current-measurements-asar-edition.json preserves all its prior
widths, measurements and length assessments, adding only three scoped widths
and one source. Effective totals:102accepted currents,13qualified reported
lengths,167scoped widths/84owners.89unranked lengths and18width-owner gaps
remain; this batch improves scope/reference-period coverage for known owners.

Native validation binds the complete width inventory and unchanged length
assessments, exact source rows, report/export receipts and both owner links.
NwASC now has8scoped width records; NCC has2. The earlier NwASC admission and
its6-record figure remain historical source artifacts. New atlas/object links,
accepted-card section and separate scalar figure present the ASAR additions.
Seasonal views retain manual source descriptions without enabling playback.

## Verification

36focused Python tests/4subtests passed before native ingestion. Additional
native, actual Chrome and publication receipts are recorded below when terminal.
The first bundle build revealed an absent diagnostic_ids field on a formerly
undiagnosed owner; explicit list initialization fixes that join. No source or
width guard was weakened. The whole default suite and complete browser matrix
remain separate gates; neither is claimed passed here.

```powershell
python analysis/hansen_asar_widths.py
python -m pytest analysis/test_hansen_asar_widths.py analysis/test_nwasc_working_admission.py analysis/test_current_identity_admissions.py analysis/test_north_atlantic_gate_bound.py analysis/test_canonical_working_assertions.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_hansen_asar_widths_browser.py
python analysis/inspect_scientific_reproduction.py
```

The29-report source reconstruction includes deterministic factual transcription
of this publication. It is not reproduction of the original satellite analysis.


### Terminal native and preservation checks

121Rust tests pass; native/WASM builds and the complete native atlas ingestion
pass. Native ingestion first caught a cross-owner diagnostic link, the older
NCC-only regional scope dispatcher, and missing object source IDs after the
packet builder replaced dashboard source lists. Separate owner diagnostics,
exact full-record dispatch and explicit source joins resolve these findings.
Edited values, periods, ranges, owners and layers remain rejected.

Compared with f937af1, exactly six rows are added:three widths,one source,two
diagnostics. Only the two owning object rows change. All previous collection
rows otherwise remain exact; all28previous reports and their producers remain
byte identical. All422engine dependency hashes verify. Main packet contains
51collections/59,856rows/170sources/57diagnostics,with167widths. The source
index contains439documents. The browser runner registers132checks; the complete
matrix is not claimed run. Actual scoped Chrome verification follows.


### Terminal actual-browser checks

Chrome passes four exact native/WASM comparisons:the3new widths,the full
source diagnostic and both owner objects. Both owners have the correct
source/diagnostic links and width counts8and2. The diagnostic query shows
the scalar figure plus equivalent readable descriptions. Atlas addresses for
the new report,new export and old export retain their own exact bytes.
Accepted-card links,keyboard figure navigation,320px layout,exports and
disabled slope-current animation pass. All8manual descriptions are retained,
with zero eligible playback steps. No automatic original-file requests or
page errors. The actual comparison screenshot was visually reviewed.

The first browser attempt passed all4queries and source-byte checks,then
stopped because a test expected a relative link attribute where the DOM used
an absolute URL. The final check compares the resolved destination and passes
without a product change or a weakened destination assertion.

26superseded generated packet parts were individually length/hash/containment
verified before retirement,including9published and17intermediate parts. No
research original was removed. Final packet140,010,424bytes/nine parts;
WASM54,853,269bytes. Prior complete-suite limitations remain. Fresh Linux
29-report evidence will be attributed to its actual source commit below.
