# Pacific NEC window and path-sampling sensitivity

## Scope

Keep all earlier centroid failures and connected-core candidates unchanged.
The latter are regional product-operator paths, not measured whole-current axes.
Five nominal months contact8N. This experiment checks dependence on latitude
selection and native-grid anchor/vertex spacing before admission.

Use the exact saved2013 OSCAR source artifact12903990715, run40887454328
attempt2,37597803bytes,SHA256
54de0d3099ca3f23ab93226a063248b34f48c176723864928ad0bbe0fb1bba7a.
Keep the original monthly parser, timestamps, nominal15m interpretation and
paired-vector completeness unchanged. No provider download or crop expansion.
The130E and240E gates remain fixed. All new quantities are numerical candidates.

## Frozen choices and counts

Use windows8–18N (preceding nominal),7–19N and9–17N. These are declared OSW
selection alternatives, not source confidence bounds or new physical edges.
Keep threshold0.025m/s, native-step penalty0.02m/s and maximum vector/path
angle60degrees. First reproduce the preceding twelve nominal paths exactly.

For both latitude and longitude anchor grids use native index strides1,2,4.
Retain every phase0..stride−1 independently on the two axes, and always include
both window boundaries and both longitudinal gates. Thus each window/month has
1+4+16=21 anchor grids, giving3×12×21=756 cases. Every failed grid remains
in the result. This is anchor/search discretization sensitivity using the same
native data, not an independent lower-resolution ocean product.

## Preserve native connectivity

Do not jump across unseen source cells when anchors are coarser. Between each
candidate pair of adjacent-column anchors, examine every intervening native
longitude column. The allowed native latitude cells are floor/ceiling of the
straight anchor segment's grid-index latitude, with exact endpoint cells fixed.
Within this narrow digital corridor apply the preceding native eligibility,
±one-latitude-cell step, orthogonal-corner, two-endpoint direction and score rules.
No missing/eastward cell or failed vector gate may be bridged.

Choose the maximum-score native witness inside each coarse leg, retaining ties.
Sum the original native-leg scores, including the original per-native-step
smoothness penalty. This holds the optimization units fixed across strides;
do not inadvertently divide the penalty or speed objective by the grid stride.
Then maximize over coarse anchor paths, permitting the same/adjacent retained
latitude anchor at the next retained longitude. Preserve a tied optimum as
ambiguous and withhold its length. The stride1 case must reproduce the original
nominal native path, including the exact vector-valued vertices and length.

Measure and distinguish (a) the complete validated native witness geodesic leg
sum and (b) its coarse-anchor geodesic leg sum. The latter is a representation
length and does not establish flow along a shortcut chord. Preserve the witness
path hash, anchor indices, source-window contacts and all failure reasons. No
coarse-anchor chord is promoted to a physical current axis.

## Separate vertex thinning from route selection

For each window/month's original native path, retain every vertex stride1,2,4
and every one-dimensional phase, always preserving both gates. This gives
3×12×(1+2+4)=252 additional geometry-only cases. Do not rerun the optimizer for
these cases. Their length differences isolate vertex-density effects on the
same path. These chords also have no independent physical-route qualification.

All lengths use WGS84 geodesic leg sums. Raw values retain calculation precision;
nominal candidate lengths round to100km. Any displayed method span is explicitly
a spread across the declared operator choices, not physical uncertainty, an
annual envelope, a probability or a confidence interval. Missing cases stay null.
Boundary contact is recorded even when the numerical path qualifies.

## Required output and visualization

Retain756 anchor-grid cases,252 vertex-thinning cases and36 native window/month
paths. Retain full scenario witnesses on cloud. Return compact metadata with
qualification, method lengths, native boundary contacts and exact witness hashes.
Report twelve-month qualification and window/phase dependence without averaging
away failures or selecting a preferred window after inspecting its length.

Render a window comparison using May (chosen before running because its earlier
nominal path had79 boundary cells), plus all twelve native monthly lengths in
all three windows. Render anchor-grid method spreads and fixed-path vertex-
thinning differences for the preceding nominal8–18N window, with failed-case
counts visible. Inspect the actual figures. Keep whole-current dimensions,
seasonal width envelopes, physical uncertainty, independent observations and
installation unadmitted. The previously reviewed source/width candidates remain
available unchanged for later Rust/query/card/atlas integration after scope review.

One cloud job on one low-priority CPU; maximum local heavy jobs0. No local field
processing, native/WASM build, browser automation, provider download, packet/index
installation or main update. The broad delivery phase remains disabled.
