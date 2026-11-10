# EAC section-core readback repair

Continue the same draft PR83, from16c8bb32c2030fe21b0d0ef04c3520618014a4a8.
Linux run39550912749/job119059651738 atfba615a reproduced seventeen reports
exactly and isolated the remaining EAC section-core failure:609,263 numeric
leaves differed, with zero changed other leaves. The largest distance
difference was4.831235855817795e-8m. The source-quality repair passed exactly.

## Changes

Declare final derived-field serialization in
`plans/eac-section-core-calculation-readback-v1.md`. Enumerate supported
fields in `analysis/eac_core_readback.py`. Apply readback after full-precision
geometry, projection, peak decisions, boundary interpolation and summaries.
Keep all original coordinates, depths, UCUR/VCUR, supplied uncertainty,
source times, masks, outcomes, indices, experimental fractions and integer
display spans exact. Preserve strict object and encoded-byte validation.

Renew the core report, figure, compact scene, calendar source pin, dashboard,
source index and native/WASM bindings in dependency order. Actually regenerate
both plots; do not merely rebind an old plot to the new report. Source-quality
and original source-profile products remain unchanged.

## Evidence

- Full-precision build with only final readback intercepted is exact against
  the preceding report, except the producer checksum. ASTs of geometry,
  project, edge, measure and summarize are unchanged.
- All33,930 cases retain statuses, boundary/peak indices and original peak
  components. Every numeric change equals the declared final serialization.
- All calendar values, extrema membership, counts and scope fields are exact.
- The regenerated calendar SVG/PNG are byte-exact. The core PNG differs in
  four pixels by at most one channel level; its SVG reflects regenerated
  subpixel coordinates. Both figures were visually inspected.
- All2,853 shared Agulhas/REDSOX cases, all28 time-series value arrays and
  all other query collections remain exact. Only the EAC object's source,
  measurement and time-evidence fingerprints and its core diagnostic renew.
-32 focused Python tests and4 subtests pass. All18 local scientific reports
  reconstruct byte-for-byte;81 Rust tests and native atlas validation pass.

Browser validation includes all3,770 dated profiles, all nine scenarios,
missing/domain/weak cases, actual native/WASM source parity, the two new
readback corruption gates, existing promotion/rehash guards, mobile and source
navigation. An old ambiguous test selector matched both the outcome and newer
calendar details; target the intended outcome control by its exact name.
Browser checks pass for all3,770 profiles, ten packet corruptions and two
source-index corruptions. Calendar checks pass for all twelve month and
eleven year groups, all nine cases, three views and320px layout.
Independent Linux and current-head integration gates remain separate until
their actual results are recorded. No new physical width, annual range,
climatology, association or ranking admission follows from this repair.
