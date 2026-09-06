# Web grounding — first detected marine-heatwave object

**Date:** 2026-09-05  
**Question:** What operational data and identity rule can support OSW's first
observation-derived detected object without promoting a one-day anomaly into a
marine heatwave?

## Search path

- `NOAA marine heatwave daily dataset gridded download OISST 90th percentile duration product`
- `marine heatwave tracker API daily MHW category OISST netcdf`
- NOAA CRW product page, method, file archive, and NetCDF metadata
- public Marine Heatwave Tracker pipeline and canonical reference implementation

## Direct evidence

| Source | Direct support | OSW use |
|---|---|---|
| [Hobday et al. 2016 NOAA repository](https://repository.library.noaa.gov/view/noaa/63891) | Defines a marine heatwave using a seasonally varying high-percentile threshold sustained for at least five days. | Registry identity test and minimum duration. |
| [NOAA CRW Marine Heatwave Watch](https://coralreefwatch.noaa.gov/product/marine_heatwave/) | States that daily 5-km files contain categories 0–5 and documents the 1985–2012 climatology and 11-day percentile window. | Upstream category semantics and baseline. |
| [NOAA CRW daily NetCDF archive](https://www.star.nesdis.noaa.gov/pub/socd/mecb/crw/data/marine_heatwave/v1.0.1/category/nc/) | Exposes dated versioned files from 1985 to present. | Exact source URLs and raw-file SHA-256 receipts. |
| [Marine Heatwave Tracker repository](https://github.com/robwschlegel/MHWapp) | Public pipeline detects global MHW/MCS events against 1982–2011 and 1991–2020 baselines and publishes daily categories. | Independent workflow comparison; no tracker result bytes are imported. |
| [NOAA OISST product](https://www.ncei.noaa.gov/products/optimum-interpolation-sst) | Describes OISST as a daily 0.25-degree analysis combining satellite, ship, buoy, Argo, and sea-ice inputs. | Correctly labels the separate OSW anomaly field as observational analysis rather than raw observation. |
| [Xu et al. 2023](https://doi.org/10.1016/j.pocean.2022.102947) | Extends pointwise MHWs into spatially compact snapshots tracked through time and distinguishes event motion from water-mass motion. | Grounds the daily-footprint versus tracked-event distinction. |
| [Cai et al. 2024](https://doi.org/10.1175/JTECH-D-23-0126.1) | Uses spatial edge detection and three-dimensional connectivity to track MHW evolution, including splits and merges. | Grounds the need for an explicit tracking stage after daily components. |
| [Marin et al. 2026](https://doi.org/10.5194/os-22-1023-2026) | Measures daily extent from spatially connected active-MHW pixels and explicitly disclaims physical-process inference. | Supports the simple connected-pixel daily footprint and its mechanism boundary. |

## Finding

The North Atlantic pixel at 42.125°N, 49.875°W was selected from OSW's separate
2026-08-01 OISST anomaly snapshot, then tested against NOAA CRW rather than
selected from the CRW result. Thirty-two exact daily files show two qualifying
runs—19 days and seven days—separated by one category-zero day. Applying the
declared maximum two-day gap rule yields one 27-day linked event, July 23 to
August 18, with maximum category 2. An isolated category-1 day on August 20 is
not promoted into an event.

On August 1 the four-neighbor native-grid component containing the anchor is
bounded away from every global-grid edge. It contains 1,769 pixels, covers
approximately 41,025 km² using spherical cell areas, and is almost entirely
category 1 with three category-2 pixels. This earns a daily footprint but not
one tracked identity across the full 27-day point event.

Exact native-pixel inheritance answers that remaining question more narrowly
than expected. A primary branch can be followed for 21 days, July 21 through
August 10, with a 450 km centroid path and five branch-ambiguous transitions.
No active August 11 component inherits a pixel from the August 10 remnant.
Thus the pointwise gap rule and the spatial tracking rule produce different
lifetimes; reconnection would be a method choice, not an observed fact.

The post-gap bakeoff makes that choice quantitative. The August 10 and August
12 components share 122 native grid locations directly: 84.1% of the prior
footprint and 26.7% of the post-gap patch. Thus one-day bridging requires no spatial
dilation, but it still crosses a day with zero inherited threshold-active
locations. OSW records the answer as policy-dependent rather than silently
joining or splitting the shapes.

A controlled follow-up separates two policy families. Eight-neighbor adjacency
adds one corner-connected cell on three of 21 days, but four- and eight-neighbor
rules yield identical lifetimes and exact gap footprints. Minimum overlap does
not: the lineage lasts 21 days under any exact overlap or IoU at
least 0.10, 18 days under IoU at least 0.20 or 0.25, and only the seed day under
IoU at least 0.50. The moderate break occurs from August 7 to 8, when 216 exact
cells persist but simultaneous reshaping reduces IoU to 0.198.

The split/merge follow-up finds a second identity sensitivity. Largest shared
footprint, greatest IoU, and largest overlapping component reproduce the same
21 daily components. A one-sided candidate-inherited-fraction score instead
selects a 12-cell splinter on July 30 and a one-cell splinter on August 3,
because both small candidates score 100% inherited, and ends after 14 days.
This demonstrates why a branch score needs scale or two-sided overlap rather
than treating perfect containment of a fragment as sufficient identity.

Preserving every branch rather than selecting one produces a 28-node, 29-edge
exact-overlap family. The original 21-day D3 lineage remains the primary trunk.
Seven side components expose five split nodes and one merge node; five terminate
and two merge back into the trunk. This graph is a more complete representation
of the threshold topology, but it still does not establish water-parcel
genealogy or physical mechanism.

An area-pruning ladder then separates trunk stability from family topology.
All 21 primary nodes survive thresholds from zero through 1,500 km², while
side-component counts fall from seven to four, four, two, one, and zero. The
only merge disappears at 500 km². This does not invalidate small components;
it shows that branch and merge counts require an explicit, resolution-aware
minimum-scale convention.

The temporal bridge is then encoded as a different graph relation rather than
another daily edge. The strict family remains 28 nodes and 29 edges through
August 10. A conditional graph adds one dashed August 10–12 edge, the seven
post-gap primary nodes, and six ordinary post-gap edges, reaching 35 nodes and
36 edges through August 18. The bridge retains the zero-active-cell August 11
receipt and therefore does not interpolate continuity.

The separate OISST analysis adds a temperature cross-check without treating the
two NOAA products as interchangeable. From August 11 to 12 the CRW anchor
category returns from zero to one, but the nearest OISST cell cools 0.13°C.
Meanwhile the fixed 12-by-17-cell OISST neighborhood mean warms 0.160°C and its
maximum warms 0.18°C. The bridge is therefore not evidence of a simple local
temperature rebound; spatial rearrangement, distinct product processing, and
the category threshold remain live explanations pending a physical budget.

## Boundary

This source chain supports a duration-qualified event at one surface pixel, a
connected daily footprint, and policy-declared spatial lineages. It does not
support subsurface extent, heat inventory, transport, mechanism, attribution,
or biological consequence. The independent
raw-OISST threshold implementation remains coded and tested, but NOAA PSL's DAP
service did not complete the baseline extraction during this run; no incomplete
series was accepted as evidence.
