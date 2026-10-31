# EICC exact source-file and semantic scope custody

Status: source preparation; no execution activated and no data installed.

V6 passed all eight Rust tests, native route smoke, all24 main-query,25 source
query and two complete atlas/seasonal native/WASM comparisons. Parent/candidate
presentation preservation and index mismatch refusal passed. Manifest assembly
then stopped at an incorrect scope hash comparison. Evidence is retained in
`research/eicc-reference-delivery-failure-review-v6.json`.

The pinned v5 scope file ends in CRLF; its canonical JSON serialization ends in
LF. They decode to exactly the same scope. Preserve the original file and its
exact source digest. Verify the actual source bytes against that digest and
compare their decoded JSON with the scope passed to compiler/manifest logic.
Record the raw-source digest separately from the canonical-semantic digest.
Neither a changed source hash nor changed scope semantics may be accepted.

Use the separately versioned v7 matching-engine helper and controller. Reuse
the v5 runtime scope and v6 response policy/parity runner unchanged. Small
regressions cover LF,CRLF,formatted JSON and rejection of changed bytes,
changed semantics and invalid JSON. Preserve all134 v6 source pins and nine
historical source relocations. No runtime or scientific data changes.

Continue the full v6 requirements in one low-priority cloud job at CPU1:
disabled held workflow, then one case, exact candidate bytes, all eight Rust
tests and51 complete API comparisons, matching-engine custody and browser
checks. Disable the request after terminal before actual screenshot review or
saved-artifact installation. No local build, full packet/index load, source
velocity processing, new PR or main merge. Overall data gaps remain open.
