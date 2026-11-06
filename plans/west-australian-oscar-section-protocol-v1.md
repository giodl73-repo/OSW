# West Australian offshore section diagnostic

Rules declared before acquisition, 2026-10-13. Extend the existing fixed
orientation component diagnostic to a northward offshore section. This is
an OSW diagnostic convention, not a published current-width measurement.

Use original OSCAR 2017.0 u/v values, nominal 15 m coordinate, for all 72
archived 2013 samples along 32 S, 60–116 E. The source-specific nominal
five-day timing includes four six-day gaps; preserve actual times. These
satellite-derived velocities are not direct measurements at 15 m.

The domain and 80–105 E peak-search window are declared editorial choices,
not physical endpoints. Average northward v only over complete finite u/v
pairs with at least five paired source samples per cell per month. Select
the largest positive northward component in the declared window, requiring
at least 0.02 m/s. Retain a search-edge flag. Independently search both ways
for the connected 40%, 50% and 60% crossings. A missing cell or unclosed
domain edge leaves the full span unresolved; do not bridge, double or close
against land. Preserve all profiles, crossings, failed scenarios and brackets.

Compute crossing separations using WGS84 shortest geodesics and round the
nominal span to 10 km. Threshold sensitivity and grid-bracket spans are
neither confidence limits nor annual current-width ranges. Flag spans
narrower than four native one-third-degree spacings. Different monthly
peaks need not track the same flow. An offshore northward component is not
proof of West Australian Current identity, continuity, origin or termination.

Keep full-current length, width, annual ranges, axis geometry and seasonal
map playback unknown. Do not inherit the historical 100–200 km cyclonic
stream or the government synthesis's >1000 km geographic breadth. Inspect
the full-domain profile figure and source support before integration into
the shipped query/UI. A standalone research diagnostic is not canonical
admission or a completed physical width.
