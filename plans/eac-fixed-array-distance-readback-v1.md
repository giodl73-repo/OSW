# EAC fixed-array distance readback v1

The source-quality report calculates WGS84 geodesic distances between the
124 retained fixed processing-grid positions. They describe sampling-array
geometry. They are not current length, current width, instrument resolution
or an uncertainty estimate.

Serialize cumulative distances and minimum/maximum segment lengths in metres
to three decimal places; serialize the total array length in kilometres to
six decimal places. Apply Python `round` only to these final report fields,
after computing all segment lengths and cumulative distances at full precision.
No source coordinates, depths, velocity or uncertainty arrays, missing masks,
source clocks, field counts, association gates or admission flags are rounded.
The section-core measurement operator independently uses its original full
precision geometry and is unchanged by this readback convention.

Linux reconstruction at `7a8d7dc` found 124 changed numeric leaves in exactly
these three geometry fields, with a maximum cumulative-distance difference
of 4.234607331454754e-9 metres. Every other source-quality field agreed exactly.
One millimetre is a serialization convention, not claimed measurement accuracy.
Keep exact report and checksum validation after serialization; add no tolerance
and never repair a failure by copying retained calculated values into a build.
