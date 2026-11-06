# EAC dated section-core span gap batch

Baseline: `82c290a8163e2978ff1cd1dec81073e231113273`; same continuing
branch and draft PR83. No additional PR and no main merge.

## Declared measurement and actual outcomes

The separately declared protocol uses original geographic U/V at100m,
WGS84 source-section bearings and the right-hand section-normal component.
It attempts all3770source dates at40/50/60% of each case's global positive
peak, requiring at least0.3m/s. Exact ties select the first source index.
Missing cells, excluded source-bottom cells and section ends stop crossings.
Only adjacent intact cells support linear interpolation. No alternate lobe,
gap bridge, coast extension or empirical width correction is introduced.

Central half peak resolves2883dates and leaves887unresolved:629missing dates,
142section truncations and116weak-positive-core dates. Central40% resolves2848;
60% resolves2896. The primary resolved section spans have a conditional median
of50.64km and sampled numerical extent7.21–135.51km. These statistics condition
on successful bracketing; they are **not annual physical extrema, a whole-current
width or flow-normal width**. Unequal success sets make sensitivity extrema
non-comparable as uncertainty bounds.

Two additional component scenarios add/subtract the algebraic sum of absolute
projected supplied uncertainty magnitudes. They assume no component independence
or confidence convention. Every scenario reselects its peak under the same rule
and preserves every failure. All33930attempts remain available. Boundary-cell
separation intervals describe sampling support, not measurement error or actual
instrument resolution. Five-day filtering, SOM filling and spatial mapping
remain explicit; no new independent observation or observation date is added.

The first protocol's compass description said southwestward; actual source
bearings near81degrees place the declared right-hand normal generally southward
with an eastward component. The correction and original protocol hash are
documented. All projection signs, thresholds, profiles, scenario outcomes,
geometry and summaries were verified identical after the description change.

## Required information and visualization

All3770derived profiles, original paired components at peaks, projected
components, supplied-magnitude envelopes, exact dates, crossing cells and
failure reasons are retained. Monthly summaries preserve every attempted date
and each scenario's denominator. The original source corpus stays unchanged.

The standalone SVG/PNG shows all central primary outcomes, missing periods,
monthly success denominators, threshold/magnitude sensitivity and fixed source
indices0,1885,3769. The weak final profile is not replaced by a cleaner example.
No statistical confidence band or annual-range claim is made.

Shared atlas-card, seasons and diagnostic-query UI reuses original recorded
month/day navigation. Three component scenarios and three peak thresholds expose
all nine cases, missing/domain/weak outcomes, source bracket support, local
alignment context and original/derived links. Green rings on the OSW map are
approximate within-cell sampling-section intersections, with textual crossing
alternatives; they are not geographic current edges or a current polygon.
Reduced motion, manual selection and keyboard chart scrolling remain supported.

The45.4MBprofile corpus lives in the checked source index; a0.462MBcompact
summary/contract supplies Rust scenes. The main packet is89,712,747bytes,
not a duplicate of that full corpus. New totals:47diagnostics,28series,
364indexed documents and45collections. Source time frames remain unchanged;
3770derived dated diagnostic outcomes do not become extra independent samples.

## Query-store loading and gates

Initial actual-browser attempts timed out loading the enlarged eager index.
Those failures remain recorded; no source request or interaction assertion was
relaxed. The store now authenticates each source's original SHA256, byte count,
root kind, schema and complete JSON syntax/numeric range on admission, retaining
raw bytes and deferring its Value tree until requested. Existing special source
validators still execute. A test catches the distinction between ignored JSON
numbers and invalid1e400; a lazy read preserves signed zero and nulls.

The complete EAC matrices and index support/NOAA matrices have an explicit
30minute aggregate subprocess budget in the normal runner. The previous smaller
source check exceeded its generic10minute budget; measured native admission of
all364sources takes about19seconds, before any individual view is compared.
The support matrix performs more than40such native admissions. Per-interaction
and worker-request limits remain90seconds. Every earlier browser check stays
registered in original order.
Gate status is recorded in the PR and execution receipts; a running gate is not
called passed by this document.

Preservation checks confirm239other owners, all463old width samples,
46old diagnostics,28old series,155inventory width rows/81owners,11ranked
lengths,76routes, all time-sample counts and observation dates unchanged.
The new corpus does not authorize a physical-width inventory row.

## Reproduction and remaining work

With repository test/figure/projection/observation dependencies installed:

The complete test manifest now pins h5py3.16.0, matching the existing observation
manifest and tested environment. The new offline EAC modules import the retained
acquisition operator, so a fresh CI installation needs that package even when
the large original NetCDF is not reacquired.

The remote82c290aoffline job stopped before its tests: the JCU Hiri thesis
endpoint returned HTTP429 after the existing1/3second retries. Fixture hydration
now honors numeric/date Retry-After values and uses15/45second backoff for429
without that header. Provider cooldowns longer than60seconds stop without an
early retry or mirror fallback. Byte pins, PDF limits and integrity failures
remain strict; no original paper is redistributed. Mocked transport tests cover
these paths, while remote source availability remains an external gate.

```powershell
python analysis/build_eac_section_core_spans.py --check
python analysis/build_eac_section_core_span_figure.py
python analysis/eac_core_spans.py --check
python -m pytest analysis/test_eac_section_core_spans.py analysis/test_rust_browser_runner_environment.py -q
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_engine.py
python analysis/test_eac_section_core_spans_browser.py
python analysis/test_eac_source_fields_browser.py
```

Browser checks reuse the existing verified8788checkout server and accept
`OSW_TEST_BROWSER`. Full clean analysis testing must identify its tested commit;
the live82c290arun predates this batch and cannot certify these changes.

Required next: finish actual browser/pagination/corruption checks, review and
committed-byte verification, then publish into PR83. Broader identity/geometry,
flow-normal physical-width validation, annual ranges,89length gaps and19route
owner gaps remain active work. These diagnostics do not redefine completion.
