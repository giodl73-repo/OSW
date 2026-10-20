# South Australian HYCOM flow context v1

Declared 20 October 2026 before calculating the following two-dimensional
reductions, connectivity or direction diagnostics. Existing monthly section
profiles and peak selections have been inspected. The first surrounding cube
parsed in memory but failed geographic validation; no map or two-dimensional
scientific statistic was inspected. No blinded or independent discovery claim.

## Purpose and fixed scope

Use the independently verified surrounding 2012/100 m source subset to examine
the context of the twelve existing 132°E component peaks. Preserve all months,
three existing thresholds and failures. These diagnostics can expose problems
with named-current association; they cannot establish that association alone.
Positive eastward velocity and grid connectivity can occur on an eddy flank.

1. Require successful full source intake, exact old-section overlap and pinned
   original diagnostic. No replacement source, depth, dates or expanded box.
2. Form monthly cell means using only complete native u/v pairs. Require
   `ceil(0.8 × calendar days)` pairs, as in the existing section diagnostic.
   Average each scaled native component over those same pairs. No filling,
   smoothing, spatial averaging or replacement of masked cells by zero.
3. Compare every 132°E monthly mean and pair count against the existing profile;
   require identical support and agreement within 1e-12 m/s for arithmetic
   representation. Raw source overlap remains bit-for-bit. Do not revise the
   old profiles or peak choices to improve the new outcomes.
4. Use the exact original selected peak latitude and native 132°E cell as the
   seed, with its existing positive eastward peak value. No new peak search,
   alternative lobe, streamline seeding or manual axis placement.
5. For each existing fraction 0.4, 0.5 and 0.6, mark supported cells whose
   monthly eastward mean is at least that fraction of the original seed peak.
   Find the seed-containing component using four-neighbor native-grid
   adjacency. Missing, unsupported or sub-threshold cells are barriers. No
   diagonal bridging, interpolation across a gap or joining nearby components.
6. Record seed components, speed, `atan2(v,u)` angle in degrees north of east
   and `u/hypot(u,v)` alignment. These are local direction diagnostics. Do not
   rotate the section, multiply its span by an angle correction, or report
   cross-flow width from this information.
7. For every threshold/month record all component cell indices, component cell
   count, coordinate extrema, occupied native-longitude count, every touched
   box side, and supported/sub-threshold/missing neighbor-barrier counts.
   Retain all source support denominators. If a seed is unsupported or not
   above threshold, retain that failure; do not choose another seed.

## Interpretation and presentation

A component touching either longitude boundary is a threshold structure that
continues to a sampled domain edge. A component not touching that boundary is
not proof of absent current continuity. Native-grid coordinate bounds are not
occupied-current polygons, physical widths, trajectories or material barriers.
Monthly-mean connectivity does not prove instantaneous continuity. The twelve
monthly means from one leap year are not a climatology or annual extrema.

Show all twelve months with native support, selected seed, directions and the
three threshold outcomes, plus the unchanged section diagnostic and source
gallery. Label these as model flow-context diagnostics. Preserve exact source
and method hashes, failure statuses and machine-readable component membership.
Do not rank connectivity extent as current length or width. No new canonical
measurement, current identity, OSW-state membership, NASA match or seasonal
footprint is admitted by this protocol. A later named-flow interpretation
requires independent geographic and dynamical evidence and explicit review.
