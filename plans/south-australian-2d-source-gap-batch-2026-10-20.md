# South Australian surrounding-flow evidence

Continues `codex/current-measurement-gaps`, draft PR #83. This is the next
source and interpretation batch; it does not claim another completed width.

## Actual gap

The existing 132°E, 100 m HYCOM diagnostic already resolves twelve monthly
component spans. Repeating those calculations would not resolve the missing
named-current association. Surrounding vectors are needed to examine flow
direction, continuity and possible eddy flanks. Duran et al. (2020), original
Figure 2 on PDF page 4, supplies independent regional context, not validation
of this model's daily 2012 field. That original remains excluded from Git.

## Source selection and custody

The pinned source-selection protocol requests the same GOFS 3.0 reanalysis,
every daily 00Z 2012 record, exact 100 m depth, paired native Int16 `water_u`
and `water_v`, 130–134°E and 38–32°S. Each component has shape 366×76×51.
All 55,632 scalar values from the retained 132°E section must match exactly,
including missing flags and coordinate/time association. Preserve unrounded
source coordinates, masks, metadata, clock, packing, URLs, rights and hashes.

The first acquisition completed but failed the combined geographic check.
Its original responses were lost because the initial operator saved them only
after validation. No scientific result or width was published from that
attempt. A prior declared protocol amendment permits native endpoint
representation within 0.00002°, with 0.00005° spacing tolerance; exact old
section overlap remains mandatory. This is a representation allowance, not
permission to shift indices or adopt another product. The actual endpoints
must be reported and checked before attributing that failure to rounding.

The corrected operator saves each complete response and its receipt in an
ignored staging directory before decoding. Failed validation retains originals
and an error receipt. The second response proved that the endpoints are correct,
but native longitude increments are 0.0799560546875° and 0.080078125°. Earlier
amendment wording attributed the initial rejection to decimal bounds before
the retained response proved the spacing issue; that historical inference is
superseded here. No provider floating-point implementation is inferred.

A recorded correction preserves native coordinates, requires exact agreement
with a separately requested coordinate-only response and bounds nominal
longitude deviations at 0.0001°. The second cube was reused; no third cube
download. Source verification passes: 366 dates, 1,418,616 vector positions,
**1,070,550 valid pairs**, 951 consistently unsupported cells, zero varying
paired masks and exact agreement with all 55,632 original scalar values.
The ASCII cube is 16,675,808 bytes; numerical subset is 3,023,158 bytes.
The acquisition receipt SHA is frozen in the context generator to reject
resealing a changed corpus. No scientific selection criterion changed.

## Verification and presentation

Current focused result: **26 tests and 5 subtests pass**, covering source
corruption, packing/clock/rights, precise original-section overlap, coordinate
tolerance limits, custody after failed validation, and the existing twelve
monthly component-span results, the actual retained source and all 36 context
cases, resealed-receipt rejection and described, hash-verified SVG figures.

The prepared source figure uses fixed indices 0, 182 and 365, all-date paired
availability and one all-date speed scale. Direction-only glyphs sample every
fourth native cell; they are not trajectories or current axes. Missing values
are not converted into a coastline. Both figures are rendered and visually
reviewed. Monthly-map legend/footer overlap was fixed before publication.

- [Fixed days and all-date source availability](../figures/south-australian-hycom-2d-source.svg)
- [All twelve monthly flow contexts](../figures/south-australian-hycom-2d-flow-context.svg)
- [Exact membership and support](../research/south-australian-hycom-2d-flow-context.json)

All twelve original seed peaks and monthly profiles reproduce under the
separately declared flow-context protocol. Seed directions range from 49.9°
south of east to 40.5° north of east. Nine half-peak components touch a longitude
box side; three do not. This is threshold connectivity of monthly model means,
not named-current continuity or physical width. No angle correction is applied
to the existing section spans.

Reproduce source intake explicitly:

```powershell
python analysis/acquire_south_australian_hycom_2d.py --acquire
python analysis/acquire_south_australian_hycom_2d.py
python analysis/build_south_australian_hycom_2d_figure.py
python analysis/build_south_australian_flow_context.py
python analysis/build_south_australian_flow_context_figure.py
python -m pytest analysis/test_south_australian_hycom_2d.py analysis/test_south_australian_flow_context.py analysis/test_south_australian_hycom_spans.py -q
```

Do not rerun acquisition over retained originals. The default operator verifies
offline. The clean preceding full gate at `778c791` passed **1,805 tests and
1,164 subtests in 2943.83 seconds**, covering EAC core/store and initial
transport changes. It predates the final cooldown follow-up and this batch;
the focused gate above covers this batch. A clean successor gate is required.

Required next: connect context maps and exact records to the current card and
checked Rust/WASM queries. These source-level deliverables do not establish
UI integration. Named-flow interpretation and physical-width admission still
require independent geographic/dynamical evidence and explicit review.

Existing monthly spans, canonical physical widths, ranked lengths, annual
ranges, routes, observation dates and seasonal geometry have not changed.
The full current-data inventory and required visualizations remain incomplete.
