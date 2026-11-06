# Saved EACC coastal reference extent case v1

Status: source preparation. All132 focused synthetic checks passed in16.57s
on one BelowNormal CPU with one numerical worker. An83-path dependency freeze
and execution-disabled request are prepared but not yet committed/backed up, and
no original data have been processed with this operator. This document is the
execution contract; it does not by itself enable execution.

One synthetic map and six-profile sheet were rasterized separately after the
test process finished and actually inspected. Missing hatches and fixed map
markers were visible. The profile sheet then received explicit visible axis
units; its corrected raster was separately rendered and inspected. No original
map or ocean data were used in either synthetic inspection.

## Scientific scope

Apply the new operator specified in
`plans/coastal-reference-extent-protocol-v1.md` to the retained initial normal
profiles in completed source run40117999392, attempt2, source commit
69cddec0412ca5b1a57c8416067a3e2fd10720af. This is method development informed by
the failed2013 regional diagnostic, not independent validation of EACC widths.

The source is the already retained HYCOM2013 daily00Z monthly paired-velocity
means at15m. Preserve the original source-lineage, acquisition preflights,
missing-day/calendar-coverage flags and figure manifest. Monthly mean-field
extents are not means of instantaneous widths or a seasonal climatology. Native
cell spacing does not establish effective resolution or observational accuracy.

Keep every month, native-latitude offset-1/0/+1 and5/10km sampling step:72 cases.
Each has40/50/60% attempts for all four separately typed quantities:864 metric
slots, including every unsupported or unresolved result. No favorable fraction,
offset, step, peak, boundary or month may be selected to fill a width field.
The original five-station regional status and both original axis/half-peak flags
remain attached. No original failed gate is converted to a pass.

This case supplies no independent shoreline reference. That quantity remains
unresolved. A model support transition is not physical shore; positive normal
is not automatically offshore. Current association stays unverified. Do not
double one-sided extents, report bracket midpoints, or admit whole-current
widths, ranks, physical annual ranges, physical uncertainty or OSW state joins.

## Custody and permitted calculation

The runner pins eight original artifact members: diagnostic, monthly fields,
result, environment, original preflight, continuation preflight, source lineage
and figure manifest. Validate all byte fingerprints before parsing profiles.
Validate the exact successful source run/attempt/commit, artifact ID, name,
digest, size and non-expiry through the existing read-only identity helper.
Validate each original map SVG against its retained manifest before rendering.

Keep all62 executed source/support paths byte identical to their original
preflights, and all seven synthetic-reviewed prototype paths identical to the
preparation review. Freeze the new adapter, runner, renderer, tests, workflow,
this protocol and role review plus the complete repository import closure.
The new preflight and request bind those hashes without self-referential pins.

Permitted original read-only primitives: `Field.sample`, `Field.cell`,
`Field.supported_rectangle`, WGS84 `GEOD` and `normal_point`. They verify each
retained coordinate, native-cell index, support status, Earth-frame U/V and
locally projected q. Reconstructing this frame/support check is new numerical
work; the case is explicitly not a metadata-only projection. Do not invoke the
completed acquisition/compiler, anchor search, peak selection, `diagnose_year`
or original figure producer. Do not make provider requests.

The new extent operator uses retained rounded q/offsets, not recomputed q.
Representation guards are5.000001e-9m/s,5.000001e-7km and, for coordinate
verification,5.000001e-9degrees plus floating-point ULP allowance. Each used
normal segment carries support and the maximum WGS84 edge scale of every
native cell in the original sampler's conservative segment rectangle.
Unsupported samples remain null. No path crosses its first unsupported sample.
Unusable original peaks retain structured missing-profile outcomes.

## Evidence output

Retain full unrounded extents, compact summary, request/preflight/environment,
source run fingerprints, and a result manifest. Full report cap2MiB; compact
summary cap512KiB. Write a fresh run/attempt directory; never overwrite a prior
case. Preserve failure metadata on errors and do not automatically retry.

Produce12 geographic map derivatives,12 six-case profile sheets, corresponding
PNGs,12 semantic monthly HTML pages and an index. Use the original equirectangular
region38–44E,13–5S with an explicitly registered overlay. Geographic overlays
use the fixed primary offset0/step5 case. Missing primary data do not trigger a
replacement by a more successful sensitivity case. All six cases remain in the
profile sheet and tables, with retained rows and map-marker coordinates.

The only correction to the copied original display is explicit diagonal
hatching replacing an SVG missing-data pattern that rasterizes incorrectly.
Preserve original bytes, colors, arrows, coastline context and old paths; log
the correction count and original fingerprints. Missing support is not labeled
land. The display basemap supplies no measured shoreline reference.

Show outward-rounded0.1km brackets, no midpoint, with sampling/representation
scope beside every figure. Include signed-coordinate definitions, original
failures, all quantity outcomes and source/method links. Semantic headings,
keyboard-scrollable evidence tables and textual alternatives supplement color.
No animation or browser automation is part of this case. Actual geographic
review and public browser/accessibility verification remain later gates.

## Serial execution and activation

Keep `research/current-gap-delivery-phase.json` at source-review-only-v1 with
heavy acquisition disabled. A separate request may authorize only this saved
derived-profile calculation: `saved_derived_profile_review_only=true`,
`metadata_projection_only=false`, provider/original-producer/admission flags
false, local-heavy limit0 and cloud limit1. That narrow request does not enable
source acquisition or any other case.

1. Finish source preparation and role findings before testing.
2. Run the four focused synthetic test files in one command on one BelowNormal
   local CPU with all four numerical-worker environment variables set to1.
   No original ocean data or network is needed. Finish before rendering.
3. Separately render and inspect one small synthetic map/profile example.
4. Write the complete freeze and a request with execution false. Commit and
   source-backup to the existing working branch, preserving main and app assets.
5. After verification, activate only that request. The cloud gate requires a
   clean exact committed working branch, Linux, Python3.14.8 and the unchanged
   eight scientific dependencies in `requirements-eacc-core-v2-execution-v2.txt`.
6. The single15-minute job shares `osw-current-gap-delivery`, never cancels a
   running case, and executes tests, custody checks, artifact restoration,
   adaptation, calculation and rendering in order. Scientific commands use
   actual one-CPU affinity, nice15 and one numerical worker. No local tests,
   rendering or builds overlap it.
7. Observe the exact live run identity until authoritative terminal status.
   Timeouts do not authorize restarts. Disable the request after terminal work.
8. Retrieve compact results first, then selected small PNGs separately through
   bounded reads. Original fields, full diagnostics and full ZIP stay cloud-only.
   Review actual geography and all failures before any follow-on decision.

Focused command (only after source preparation; constrain resources externally):

```text
python -m pytest -q analysis/test_coastal_reference_extent_v1.py analysis/test_eacc_coastal_reference_extent_adapter_v1.py analysis/test_eacc_coastal_reference_extent_evidence_v1.py analysis/test_run_eacc_coastal_reference_extent_case_v1.py
```

This focused gate does not replace the full offline release suite, native/WASM
or public UI checks. Existing release/source-access gaps remain recorded. A
successful method-development case alone admits zero current measurements.
