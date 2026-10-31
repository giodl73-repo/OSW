# Resolve inherited EACC presentation dependencies

The completed v1 case failed before overlay or browser work because a workflow
path no longer held its manifest-pinned historical bytes. Keep v1 code, tests,
preflight and failed case unchanged. Its request is disabled.

Four specific source differences are now independently verified against the
installed-parent GitHub contents and the earlier source commit:

- Baffin and Davidson workflows retain manifest hashes from source commit
  `0c2f0dc67a9ba25cbf488f634702b05f30401f2f`. Current workflow bytes are later
  disabled versions. Check both exact versions; do not reactivate old workflows.
- Dashboard and query HTML gained a `Local extent evidence` navigation link.
  Their active bytes differ from stale manifest hashes by that existing link.
  Preserve active HTML. A future v2 presentation manifest must explicitly
  record and repair these two presentation pins; do not revert navigation.

The four exact earlier files are retained as non-executable `.source` files in
`research/eacc-connection-presentation-history-v2/`. The binding document records
source commit, old and active hashes, byte lengths, archive paths and roles.
The archive bytes match the actual inherited manifest hashes.

The v2 parent verifier streams every manifest entry and permits only these
four exact registered bindings. It verifies both active and archived bytes,
rejects duplicate or expanded binding paths and any compiled production
dependency rebinding, and reports all unrecognized mismatches together.
Data, WASM, current routes and scientific source tables receive ordinary exact
hash checks. No missing or mismatched pin may be discarded.

Twelve synthetic corruption cases pass on one CPU, including simultaneous
packet/WASM corruption, changed archives/current files, byte lengths, missing
archives, path traversal, wrong roles, duplicates and scope expansion.
The bounded local audit covered 473 small code/control files (4,500,230 bytes),
excluding 571 other manifest paths. It is not a full parent verification.

Next, integrate this verifier into a separately frozen v2 presentation case:
preserve every other manifest field, retain old source hashes through explicit
archive custody, repair only the two stale HTML presentation pins, add only the
new SVG and card UI, and run the complete parent verification and mobile card
check in one sequenced cloud job. No new cloud case is enabled by this plan.
