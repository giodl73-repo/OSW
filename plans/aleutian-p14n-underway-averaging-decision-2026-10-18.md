# P14N underway averaging: both boundaries remain unresolved

## Decision

The declared contiguous-run operator does **not** supply a new current width.
All **54 relative-peak scenarios and 72 velocity-displacement scenarios**
lack two resolved crossings. Missing sides and endpoint separations remain
null. Do not substitute the earlier approximately 100/80 km hourly component
spans or connect across CTD stops to complete these new measurements.

This closes the question of whether these particular fixed native averaging
operators recover both boundaries without joining runs. It does not close
the physical-width gap or prove that no other justified method could do so.

## What was computed

The [declared operator](aleutian-p14n-underway-averaging-protocol-v1.md)
was written after native vectors and run support had been inspected, before
these new averaged velocities and crossings were calculated. It is
exploratory. For each fixed 1/2/3 m/s ship-speed cutoff, retain every original
run and all 30/60/150 minute bins anchored at the first ensemble start.
Overlap is integrated once, using the mean of simultaneously active source
ensemble means. Boundary analysis requires at least 80% of the full window
duration and all contributor latitudes within the unchanged branch window.

| Ship-speed cutoff (m/s) | Averaging (minutes) | Retained bins, all reach | Bins with >=80% time coverage, all reach |
|---:|---:|---:|---:|
| 1 | 30 | 128 | 95 |
| 1 | 60 | 81 | 41 |
| 1 | 150 | 53 | 16 |
| 2 | 30 | 103 | 92 |
| 2 | 60 | 57 | 39 |
| 2 | 150 | 29 | 16 |
| 3 | 30 | 96 | 85 |
| 3 | 60 | 54 | 37 |
| 3 | 150 | 27 | 15 |

Counts cover the original 40-48 N reach, not just either branch. Each
experiment separately uses northern 44-46 N and southern 41-43 N footprints.
For each branch, select the largest eligible eastward mean, preserving ties
by earliest run/bin. Retain 40/50/60% peak crossings and four separate
half-peak threshold offsets. Run ends, incomplete bins and branch-window
edges cannot stand in for measured crossings. All 126 scenarios are
unresolved under these rules; the full report retains each stopping reason.

## Visualization and numeric alternative

![Six panels compare northern and southern eastward means for fixed 30, 60 and 150 minute windows and all three ship-speed cutoffs. Horizontal bars show contributor latitude footprints. Hollow markers have less than 80 percent time coverage. All 126 scenarios remain unresolved; no physical width is admitted.](../figures/aleutian-p14n-1993-underway-averages.png)

- [Accessible SVG](../figures/aleutian-p14n-1993-underway-averages.svg)
- [All bins, source indices, clipped intervals, u/v, locations and scenarios](../research/aleutian-p14n-1993-underway-averages.json)
- [Figure provenance](../research/aleutian-p14n-1993-underway-averages-figure.json)

Mean locations summarize moving measurement footprints. Horizontal bars
are latitude support, not uncertainty or current edges. The figure neither
joins runs nor sorts observations into a continuous reconstructed transect.
Symbols distinguish cutoffs without requiring color. The SVG contains a
title and description; this table and the numeric report provide text/data
alternatives. This is a research artifact, not yet an added dashboard figure
choice or registered Rust/WASM source collection.

## Uncertainty and attribution

The native source has already undergone provider processing. No second ship
correction is applied. These are OSW temporal averages of supported nominal
100-300 m layer means, not an independent reprocessing of raw acoustic pings.
The source paper's GPS-related averaging estimates do not calibrate total
errors for these clipped, filtered means. Neither those estimates nor the
finite threshold offsets constitute a width confidence interval.

The component remains eastward, not a newly estimated flow-normal
coordinate. Same-cruise branch attribution and the possible southern eddy
remain contextual. No annual range, physical edge geometry, seasonal
playback, state intersection or inventory ranking is admitted.

Source context: [Chen and Firing (2006), section 2 paragraph 5, section 3
paragraph 7 and Figure 2](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005JC003064).

## Reproduction and verification

Run from the repository root with the pinned scientific dependencies:

```text
python analysis/build_p14n_underway_averages.py
python analysis/build_p14n_underway_average_figure.py
python -m pytest analysis/test_p14n_underway_averages.py -q
```

The focused gate passes **8 tests / 3 subtests**. It checks exact source
reconstruction, independent overlap integration, clipped interval weighting,
full-duration terminal denominators, missing-bin/coverage/window barriers,
cross-run rejection, synthetic resolved geometry, earliest-run peak ties,
source mutation rejection, admission flags, figure pins and SVG description.
The existing NumPy binary-size warning remains visible. The final PNG was
visually reviewed for labels, legend, symbol distinctions and footprint
interpretation.

The combined native metadata, native field and new averaging gate passes
**17 tests / 28 subtests in 4.65 seconds**. The seven-role review approves
this as research-only, with pending query/card registration and successor
combined validation recorded explicitly.

The separate clean **25b286e** full suite was already running when this
successor research operator was added. Its eventual result cannot certify
this later operator. All published production assets and all 155 prior
scoped width rows remain unchanged by this research-only addition.

## Next work

Do not keep tuning this operator to manufacture a two-sided result. A future
station-to-station composite would require a separate declared assumption
about temporal comparability and preserve its gaps and sensitivities.
Keep the physical-width gap open and prioritize another unresolved current
with a directly supportable measurement. Registration of this negative
result in the existing query/card source inspector is also pending.

## Registration follow-up,2026-10-18

The later registration batch completes the pending query/card source work:
`plans/aleutian-underway-averaging-registration-2026-10-18.md`. The existing
report and figure bytes are unchanged. Atlas cards, seasons source review
and diagnostic query charts now expose the native averaging figure, all nine
experiment summaries and exact source/provenance links. This supersedes the
earlier registration-status sentences, not the scientific negative result.
Physical width and annual variability remain unresolved.
