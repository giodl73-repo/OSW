# EAC interpolation-fraction readback revision

Continue draft PR83 from37013974c24f7d29aae7cb4c3851d44be417777a.
Independent Linux run39557216015/job119079679024 passed seventeen of eighteen
reports exactly. The EAC report had one remaining numeric difference and no
other differences: profile3021, minus-supplied-component-magnitudes,40%
threshold, offshore `fraction_inside_to_outside`,0.24547311 vs0.24547310.
All stored distances, spans, statuses, indices and source components agreed.

Preserve the published v1 protocol and its commit unchanged. New v2 declares
seven decimal places for the final interpolation fraction; every other field
and all full-precision functions retain v1's convention. At the actual maximum
source spacing, half this fractional quantum is0.0001003623m, below the
half-millimetre distance readback. This is representation precision, not
physical uncertainty or an observation-resolution claim.

Always rebuild from the pinned original source arrays. Do not upgrade v1
serialized fractions by rounding them again: double rounding can produce a
different value from direct final readback of the full-precision calculation.

Audit against3701397 proves only47,848 final fraction representations change,
by at most5.000000003e-8; all33,930 cases retain their span values (including
nulls), edge distances/brackets, statuses, source values and other scientific fields exactly. The full-precision audit
against16c8bb3 remains exact except producer identity. Calendar values and
scope are unchanged.33 focused tests and4 subtests pass, including a regression
on both sides of the observed v1 rounding boundary.

Regenerate the source report, plot receipts/scene, calendar source binding,
dashboard, index, bundle and engine in order. Retain strict independent
encoded-byte comparisons and actual native/WASM hash-mutation checks against
the v2 protocol. Current-head browser, committed-pin and independent Linux
results remain distinct gates until their actual results are recorded.

The actual native/WASM check passes all 3,770 profiles, all nine cases,
ten packet corruptions, two source-index corruptions, source links and
320 px layouts. All 81 Rust tests pass. The standalone calendar comparison
values and plots remain unchanged from v1; its previous runtime gate retains
that tested scope. Independent current-revision Linux proof remains pending.
