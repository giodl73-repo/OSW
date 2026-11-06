# EICC reference and source-table delivery

This case advances the current measurement inventory with source-qualified regional
reference routes and typed sampling/spectral evidence. It does not supply a measured
whole-current length, physical width, annual extrema or new named eddy.

## Fixed inputs and intended changes

- Installed Loop parent: logical SHA256 `b4d60a69eeea0339e06088f0b1e737ef50ec2983521615dc96341dd69d736551`,
  189986194 bytes, 108574 rows, 246 objects, 106 named currents, 172 scoped-width records.
- Add two EICC spring regional reference connections, seven published sampling
  reference records, six spectral scale records and three source definitions.
- Candidate total: 108592 rows. Preserve every earlier science record. Update only
  EICC evidence metadata and its editorial route decision; retain that exact prior
  decision in the new record.
- Extend the source index from 601 to 609 documents. The dashboard is the only
  historical source replacement; every other original source string stays exact.
- Preserve the revised Loop page and its original page/manifest archives. Historical
  preflights continue to validate the original archived page under an explicit relocation.
- Recompile native and WASM once using Rust 1.95.0, the same 98 Rust/Cargo sources,
  the same 143 noncatalog data inputs and the newly generated catalog. Validate
  compiler-emitted production dependencies; exclude all six test-only data references.

## Sequential execution

1. Commit and back up a disabled request; confirm the held workflow skips all heavy steps.
2. Enable just this case, after earlier selectors/jobs have finished. Use shared
   concurrency `osw-current-gap-delivery`, cancel-in-progress false, one CPU,
   nice15 and one worker per tool. No local packet/index loads, builds or browser.
3. Verify clean exact source checkout, active branch, source/preflight pins,
   17 earlier disabled requests, installed parent assets and historical relocations.
4. Create the candidate, verify preservation, extend the index, then compile the
   matching native CLI and WASM sequentially with offline locked dependencies.
5. Compare complete native and WASM responses for 24 main-store queries and 25
   source queries in separate fresh Node processes. Main checks cover both direct
   route selections, seven points, point G's outlet qualification, six spectral
   scales, null-versus-zero semantics, unchanged widths and legacy Loop/South Java
   evidence. Source checks cover eight root documents, all 15 source pointers and
   two legacy documents. Compare initialization metadata too.
6. Check source-index/compiled-catalog mismatch refusal in both engines. Record
   actual response sizes and hashes. Scalar output bound 131072 bytes; reference
   routes, detailed owners and source responses 2097152 bytes. Never truncate.
7. After all query processes finish, run one cloud browser: dashboard keyboard
   navigation, both exact reference-card links, fitted single-route maps and
   details, all diagnostic rows, source queries, two SVG figures and 320/390px
   evidence-page screenshots. Do not download original PDFs or data arrays.
8. Retain compact receipts/screenshots separately from the large generated files.
   Disable the request after a terminal run. Inspect actual screenshots before a
   separate installation of the exact saved artifacts on the existing branch.

## Completion evidence

Required: source/preparation receipt; actual preservation/index audit; matching
compiled dependency proof; all 49 complete native/WASM comparisons; both mismatch
guards; browser receipt; actual visual review; exact saved artifact hashes and
separate working-branch installation proof. A passing source fixture suite alone
does not establish runtime verification, visual approval or installation.

The wider data-gap goal remains open. Published whole-current length, physical
width, seasonal ranges and uncertainty remain separate evidence gates. No new PR,
main merge or scientific release is part of this case.
