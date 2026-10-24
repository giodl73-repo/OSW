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
   Forty small synthetic continuation checks passed locally on 2026-10-24.
   They did not contact the source or process original velocity arrays.
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

The source-review hold is still active. The new continuation workflow is
preparation, not an enabled or completed source run. No new current measurements
have been admitted by this preparation.
