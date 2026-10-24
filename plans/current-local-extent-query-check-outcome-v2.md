# Dedicated local extent query engine: verified outcome

Cloud run40138158745, attempt2, job121004198936 succeeded from source
3700e9d1bb57cae00515de49a623d607f0c7b196. Its build request is disabled again.
An initial attempt was cancelled with zero jobs by the shared queue; the second
attempt ran after the queued workflows completed. Execution used one CPU,
nice15, one Cargo job and one test thread. No local build was run.

## Verified runtime

- Dedicated WASM:278034bytes, below the2MiB budget.
- Linear memory after scoped checks:7340032bytes (7MiB), below64MiB.
- The same21 query results matched both native CLIs, the dedicated WASM and
  the previous59201757-byte reference WASM.
- Two pagination-overflow refusals and three record/case lookups passed.
- Failed reload clears the scoped store; successful reload restores it.
- The835839-byte scalar snapshot is unchanged. Its72 cases and864 attempts
  remain separate research evidence, including missing outcomes.
- Null physical width matches864 attempts; numeric zero matches none.

Exact parity and source-gate reports are retained in research, alongside
`current-local-extent-query-execution-review-v2.json`. The archived binary has
SHA2565758d51eb754b14b0b0660c6d5f7c2137f0f4f56b9e8b0ea133ca5ec8c21e8cc.
Artifact12577793330 is117960bytes compressed. Only1952 range bytes were
transferred to retrieve compact metadata; the binary remains in the cloud.

All83 scientific inputs and23 frozen runtime inputs were verified. The source
corrections and three failed cases are preserved, including the shallow-history
failure fixed by checkout depth32. No physical width, rank or state join was
admitted. Full-atlas regression and browser UI behavior are not verified by
these scoped runtime checks. Installed assets and main remain unchanged.

## Next delivery stage

Connect this dedicated engine and the explicit scalar snapshot to a lightweight
worker/UI scope. Show source/case inspection, missing outcomes and the existing
monthly evidence chart. Keep physical joins and ordinary atlas workspace
controls unavailable within this research scope. Retain the ordinary atlas
engine separately. Verify actual UI behavior in one serial cloud case before
claiming the data and visualization are delivered.

After this delivery, continue the broader current and eddy measurement gaps;
the scoped EACC evidence does not establish whole-current dimensions or annual
physical ranges.
