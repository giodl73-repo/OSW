# Current gap work: sequential execution

The computer must remain usable while gap filling continues. Run one stage at a
time. Never overlap acquisition, numerical processing, builds or browser checks.

## Resource limits

- Local heavy jobs: zero during source acquisition and review.
- Cloud heavy jobs: at most one, under `osw-current-gap-delivery`.
- Small local checks: one CPU, BelowNormal priority, one numerical worker.
- Preserve user browsers and preview servers. Do not open extra automation tabs.
- Keep original arrays and large artifacts in the cloud; retrieve compact review
  metadata and selected small figures only.
- Keep the exact active run identity. Poll it; an observation timeout does not
  authorize a replacement or restart.

## Ordered queue

1. **Prepare EACC continuation.** Finish the adapter's internal review, dependency
   freeze and workflow wiring while `source-review-only-v1` remains in force.
   The focused suite passed225 checks locally on2026-10-24. A versioned startup
   correction then passed24 targeted checks, including execution of the actual
   checkout script against a tiny offline Git fixture. These checks did not
   contact the source or process original velocity arrays.
2. **Acquire EACC in one cloud job.** Validate and reuse the three saved chunks;
   request the remaining 79 sequentially. Preserve progress on failure. Keep all
   40 executed scientific inputs unchanged. Enable the execution phase only
   after preparation is complete.
3. **Review EACC.** Read compact metadata and selected geographic/profile figures.
   Source recovery alone does not admit a measurement. No local build runs in
   this stage.
4. **Deliver a reviewed cohort.** Update data and query projections together, then
   run native checks, WASM checks and browser checks separately in that order.
   Large local stages remain deferred until the resource restriction is lifted;
   use sequential cloud checks where available.
5. **Take the next current gap.** Select it after recording the EACC outcome;
   do not fan out additional acquisition jobs.

## Execution checkpoint: 2026-10-24

Stage2 completed successfully in cloud run40117999392, attempt2,
job120943453102, source commit69cddec0412ca5b1a57c8416067a3e2fd10720af.
It passed226 cloud checks and completed82 requests by reusing3 and acquiring79.
All12 months and72 diagnostic cases are retained. Preserve the completed case;
do not restart it. The versioned continuation preflight binds52 inputs,
including the unchanged40 original scientific inputs.

The preceding continuation startup run40117618572 stopped before source access
because of an unsupported Git checkout option. Its v1 artifacts are preserved;
the v2 operational correction uses `sparse-checkout set --no-cone`.

Readback uses bounded HTTP206 ranges for compact JSON and at most four selected
PNGs per call, capped at3MiB transferred per call. The reader was checked with a
tiny synthetic archive and refuses a server's whole-response fallback. It will
not request an artifact until the exact run is terminal.

Stage3 is active. Compact metadata and four January/July PNGs were retrieved and
inspected, without downloading the55MB ZIP or source arrays. No month passes
both primary five-station width diagnostics. Sixty-six cases stop at missing
seed-refinement endpoint support; the two January primary cases retain resolved
central spans but fail regional axis gates. This is unsupported method coverage,
not zero flow or current absence. A coastal-mask interaction is a hypothesis
pending a separate support inspection at this checkpoint; the completed audit
below now identifies the exact computational failure.

The compact original result and figure manifest are preserved under research;
see `research/eacc-hycom-source-resume-execution-review-v1.json`. No new current
measurements have been admitted. The source-review hold is restored, with zero
local heavy jobs. Native/WASM builds and browser checks remain deferred until
the ordered delivery stage.

The separate support inspection40122083877, attempt1, completed with35 cloud
checks. Its255635-byte audit retains all72 cases. For all66 missing-endpoint
cases, the negative40km endpoint is unsupported and the positive40km endpoint
is supported. Sixty profiles stop before the negative endpoint; six reach an
unsupported sample. Each first negative failure is missing paired-corner support
west of the seed. Physical land attribution remains distinct from that exact
computational cause. The full two-sided regional width gate remains unsupported.

The inspection request is disabled again. The bounded audit and execution
review are retained in research; all62 executed input paths remain unchanged.
Next prepare the separate coastal-extent design in
`plans/coastal-current-extent-measurement-design-v1.md`, with synthetic tests and
a new protocol/review/freeze before any further original-data calculation.

The new scalar-profile prototype and numerical protocol are now prepared under
`analysis/coastal_reference_extent_v1.py` and
`plans/coastal-reference-extent-protocol-v1.md`. All48 synthetic checks passed on
one low-priority CPU, including analytic/quantized crossings, missing segments,
shore-position gaps, native-scale changes and WGS84 normals across a longitude
seam. A small synthetic SVG and its raster were inspected. These are method
development examples; no original ocean field or new width has been processed.

Next implement and verify the separate source-bound cloud adapter, native-cell
scale footprints and actual-data evidence output. The new prototype preparation
does not permit original-data execution or measurement admission. Keep all62
executed inputs and the completed failed two-sided case unchanged.
