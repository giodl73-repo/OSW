# Native coastal depth curtains

Extend the retained32 coastal sections into spatial depth support using only the
original velocity and full salinity arrays. Reproduce the complete v12 admission,
including all five retained controls and all original axis/core selections, first.
No new source requests, reference rows, replacement cores or parent inheritance.

For the27 supported original cores, seed a component at that exact native column
and depth index. Accept native nodes only when both fields are finite, the original
signed component exceeds0.1m/s and practical salinity is below35 for Norwegian
Coastal or34 for East Greenland Coastal. Use four axis-adjacent native neighbors;
never connect diagonally, interpolate across missing nodes or connect separate
fresh lenses. A detour around a missing node through qualifying native neighbors
is permitted and retained explicitly. This is sampled-grid topology, not proof of
continuous physical connectivity between samples. Original velocity-frame bearings
remain north0degrees and southwest225degrees respectively.

For every original native column, retain every vertically contiguous run belonging
to the seed-connected component. Runs may reconnect through neighboring columns;
keep separate vertical runs rather than collapsing their gap to one thickness.
Each run reuses the frozen owner-specific vertical fresh/component diagnostic,
seeded at its first node solely to recover its adjacent boundaries. This diagnostic
seed is not a replacement current core. Retain native index intervals, upper/lower
boundary status, adjacent brackets and limiting criteria. The run containing the
original core must reproduce the previously admitted upper/lower boundaries exactly.

At a missing next native input or depth-domain end, retain censoring and the last
connected sample; do not infer seabed or zero depth. Surface support has no
interpolated physical top. Flag every section touching a lateral sampled edge;
the sampled span is not a complete width. Retain columns outside the seed-connected
component explicitly as no seed-connected support, not absent current. Preserve
all5 original unclassified cases without a curtain or zero-valued depth.

These conditional model section curtains add cross-current variation in depth at
the original locations and2022 quarterly instantaneous snapshots. They do not
establish full-route coverage, annual extrema, independently validated identity,
coastal-front foot depth, physical current bottom, thickness, width, cross-section
area or volume. No integration across horizontal/vertical gaps, no seasonal
interpolation and no pairing to unrelated width/length estimates.

All numerical work and tests run sequentially in cloud on one idle CPU. No new
field retrieval. Keep the existing publication/native/decoded caps; the new
component has at most150columns by40levels and6000nodes per section. Retain exact
cloud output only after all branch jobs terminate and hashes pass. Prior validated
methods, main, runtime, UI and eddy register remain unchanged.
