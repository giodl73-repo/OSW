# Offshore regional lengths: retained baseline and numerical refinement

Continues the same measurement branch and draft PR #83. These are numerical
source-region candidates, not newly admitted whole-current lengths or widths.

## Fixed experiment and a necessary numerical correction

The v1 protocol fixed thirteen fields (twelve monthly means and a separate
equal-record source-period mean), the original32S maximum-v seed search,
three native seed positions,5/10/20km steps,28/36S gates and all failure guards
before any traces were calculated. All117attempts were retained.

Euler v1 produced43matching gate pairs, including four primary monthly
cases. The step comparison then exposed large numerical changes: the finer
step lost some connections, and June/August primary lengths changed by
hundreds of kilometres. Those provisional Euler numbers are retained as a
baseline, not promoted as dependable length estimates.

A separately declared v2 protocol kept the sources, seeds, gates and guards
unchanged. Classical RK4 with step doubling controls its estimated local
error to10m, with100m minimum trial steps, fully supported stages and a
separately recorded boundary closure of at most1m. All117refined cases are
retained alongside the117Euler cases. No failed case was replaced by a
different seed, lobe, month or field.

The refined run yields24matching gate pairs and two primary monthly matches:

| Source field | Primary calculated regional length | Public approximation |
| --- | ---: | ---: |
| June2013 monthly mean |2004.221319km|about2000km|
| August2013 monthly mean |2276.997724km|about2280km|

For the same central seed,5/10/20km maximum steps give2004.317292,
2004.221319,2001.549348km in June;2277.098991,2276.997724,
2276.027275km in August. These alternatives retain the same10km public
rounding. Relative spreads are reported directly, without a pass threshold
selected after results or a claim that they bound physical uncertainty.

January/September lose the primary numerical connections found by Euler.
The source-period mean remains unresolved at all nine conventions. No
annual reference route, annual physical range or mean instantaneous path
is inferred. Successful seeds can select different source-field branches;
named-current association is still unverified.

## Data and visualization

Both complete experiments retain source/protocol/operator hashes, native
anchors, seed/step conventions, full partial geometry, gate and guard outcomes,
accepted distances and all234attempts. Refined cases keep their exact Euler
counterparts, rejected-trial counts, local error estimates, closure distances
and three-step comparisons. Derived readback precision is explicit; original
monthly vectors and source-period means are not rounded as observations.

Independent comparisons show every success/failure, with the Euler points
visible behind refined results. Separate primary-path maps keep failed
traces and the source-period mean. The source-query workspace exposes exact
JSON, and the West Australian card links to comparisons, paths and all117
refined cases. No failed trace is drawn as a measured current boundary.

No new published ranked length, reference-route inventory row, width,
observed footprint, eddy identity or physical state join is admitted.
Current physical width/length and scientific association remain open.

## Verification scope

Fifteen focused numerical tests pass, including uniform meridional flow,
constant-bearing WGS84 length benchmarks, rotational return, masked/zero-weight
corners, side/opposite exits, weak speeds and computational limits. Every
retained case is rebuilt; stored polygon distances are checked independently
with an explicit endpoint-readback bound. Refined/source/baseline bindings
remain exact. The standalone figures were visually inspected.

The previous isolated full suite at8399af0 is terminal PASS:1856tests /
1222subtests in3679.83s, clean start/end, completed2026-10-21T00:52:50UTC.
Independent Linux at91c334b passed all11preceding report reconstructions,
run39523392672/job118972324832. These results predate this new measurement
method and are not presented as its full-suite or cross-platform pass.

The final focused gate passes17tests /2subtests in39.04s (fifteen numerical
tests plus the browser-runner environment checks).79Rust tests, locked native/
WASM builds and actual native atlas loading pass. The387-document index has
281,781,873original /45,860,871compressed bytes; main packet90,259,126bytes,
WASM16,856,188bytes.

The actual browser returns all234cases exactly through native Rust and browser
WASM. Both solver runs, source export, keyboard current-card navigation and
320px reflow pass, with no page errors or automatic original-source requests.
Against91c334b, all44other query collections,239other object rows and383earlier
indexed documents remain exact. Existing source fields, widths155, samples463,
routes76 and series28 are unchanged. All680inspected staged source/build blobs
match their pins, including144engine inputs and both complete figure graphs.

A new clean full-suite snapshot follows final publication, using a new receipt
and preserving the earlier terminal pass. Independent Linux now also attempts
both numerical producers, bringing its reconstruction scope to13reports; that
new-head result is tracked separately. The broader core-data goal stays active.
