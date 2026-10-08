# Mindanao mean surface offshore extent

2026-10-08. Editorial source extraction; scientific/canonical admission pending.

## Source and scope

Schönau et al. (2015), Oceanography 28(4), 34–45,
doi:10.5670/oceanog.2015.79, reports roughly 250–300 km offshore surface
extent in the averaged glider velocity section (printed p.38, Figure 2a).
Original author-hosted PDF methods pp.36–38 and rendered Figure 2a inspected.
The local 13-page PDF is 2,560,492 bytes, SHA256
6d50cb950e266119c1fcaade1c13396182e6010c14b3dcb38fe1cef442f8c66a.
It remains an ignored local research copy; redistribution rights are restricted.

This is a one-sided author-described surface extent. No midpoint, paired width,
confidence interval, annual extrema, seasonal playback or route buffer admitted.
The source mean line is 126.61 E, 8.16 N to 130 E, 8.77 N; profiles within
80 km were projected and objectively mapped. Absolute geostrophic velocities
use the glider depth-average reference (surface to 1000 m). That reference
range does not become a fixed measurement layer for the surface extent.

The background describes repeated sections to January 2014; the methods report
deployments to July 2014. Both descriptions are retained. Neither is promoted
to exact profile dates contributing to the mean. A secondary core at 250–350 km
may be an eddy; its position, the 50 km main core position and the transport
integration limit at 300 km are not additional widths. Historical source widths
are not pooled across layers or study periods as seasonal minima/maxima.

## Implementation

Added mean_offshore_extent_range with complete audit-bound measurement and
sampling context. Protocol v1.22 defines the distinction. Validators reject
midpoint, threshold, layer, geometry, sampling-date and annual/whole-width
promotion. Audit receipts flow through dashboard, query and source index.
The atlas and seasonal explorer identify offshore extent explicitly; the latter
shows an interval chart without a full-width bar or geographic edges.

Coverage: 74 records for 38 current owners; 55 unassessed. These heterogeneous
records include dimensions and related scoped metrics, not 38 whole-current
widths. Source index: 80 documents. Query collections: 39. Dashboard: 240 objects.
All 73 older measurements and six seasonal frame records remain unchanged.
Gulf Stream and both Loop section diagnostics were regenerated after the
protocol update: only general_protocol_sha256 changed. Inventory receipts and
seasonal upstream width receipt were then rebound. Scientific samples unchanged.
The first builds correctly rejected those stale protocol receipts.

## Validation

Native/WASM build: 38 Rust tests passed. General query browser parity passed.
Expanded regional range browser check covers both Black Sea and Mindanao,
source links, no midpoint/annual/full-width inference, route navigation,
complete row parity and 320 px reflow. Initial visual review found overlapping
250/300 labels; anchors and axis padding were corrected with an overlap check.
JavaScript syntax: 39 files; page assignments: 14 (assignments are not test results).
Full local suite: 821 tests and 647 subtests passed in 236.71 seconds.
Final expanded range browser rerun passed after the label correction; its
full-page 320 px screenshot was visually inspected. General query browser
parity passed. The final UI text/label edits followed the native build; final
JavaScript syntax passes and these browser checks exercised the final UI.

Reproduction:

```powershell
python analysis/build_current_section_width_series.py
python analysis/build_loop_current_section_spans.py
python analysis/check_current_width_inventory.py
python analysis/build_motion_dashboard.py
python analysis/build_rust_query_bundle.py
python analysis/build_almanac_index_bundle.py
$env:CARGO_INCREMENTAL='0'
python analysis/build_rust_query_engine.py
python -m pytest analysis -q
python analysis/test_black_sea_regional_width_browser.py
python analysis/test_rust_query_browser.py
```

Publication remains pending. Consolidated PR30 at f0c3f40 has failed offline
checks; its earlier failure exhausted the primary Qiu/Chen PDF acquisition.
PR39 at 0b86dc0 still had two running offline jobs at this batch's status read.
No mainline completion claimed. This batch will be a dependent draft review.
