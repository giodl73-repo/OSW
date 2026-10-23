# Indian SECC retained-source boundary audit v1

Prospective audit of the existing 144 HYCOM local-normal attempts, all months,
both seed meridians, all three seed offsets and both sampling steps. Preserve
every available station and both normal directions, including successful,
unsupported, missing and profile-limit endpoints. Do not select only May.

Read the frozen serialized local-normal report and native monthly arrays.
For each station/direction, select the terminal sample in signed-offset order
and its immediate inward neighbor. Copy both complete serialized rows. Check
the terminal location against the exact native coordinate extrema; retain all
violated sides, including corner exits. Missing corners are not domain exits.
Retain every threshold case's status and that direction's edge result. Compare
the inward neighbor's serialized projected velocity with an edge's serialized
threshold using Decimal decimal-string arithmetic only when both are present.
An unresolved edge has no stored threshold: use the recorded peak times the
recorded fraction, explicitly labeled a serialized-value diagnostic, not a
replacement for the original unrounded calculation. Do not infer a crossing
from the final finite/outside pair, interpolate across it, sample new velocities,
or turn last-sample offsets into lower bounds on a physical current width.

Record native row/column indices and coordinate extrema from the retained
arrays. Validate sample columns, 144 unique attempts, all twelve months, source
quality/array binding, finite coordinate monotonicity and both source shapes.
Record every source endpoint, including all source-boundary stops that did not
cause a threshold failure. Separate these two counts. Retain station-level
axis status so the already passing axis attempts can be inspected without
discarding other cases. Current identity, physical edge, width, length, annual
ranges and map/state intersections remain unverified.

This is an audit of previously serialized samples, not a finer sampling run,
source-domain expansion or revised width operator. A last valid sample above a
threshold does not exclude an intervening crossing and return. Any future
expanded-domain or terminal-interval experiment needs its own frozen protocol,
including failed months and offsets. The actual report must reconstruct byte
exactly offline. The accompanying original visualization should expose all
twelve months and distinguish unresolved source-edge threshold cases from
other terminal stops; it must not draw any endpoint as a current boundary.
