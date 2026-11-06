# Full-parent rehearsal without a local atlas rebuild

The current published packet is the immutable parent for this rehearsal:
logical SHA256`5ea582e44f8fd88d736d9ddf9c46fb52fad8e9c4cdca74f6130da10d979a2345`,
187116909bytes. The preparation now stages79 new records: the previous75-row
identity/evidence/width batch plus four explicitly unresolved route decisions.
The original scientific products and historical release remain unchanged.

## Compatibility findings before publication

Inspection of the existing native code found three required integration fixes:

1. `dashboard.rs` requires `dashboard_search` to equal label plus basin. The
   prepared identities now match; abbreviations/spellings are preserved in
   `search_aliases` and the ten separate name records.
2. `current_catalogue.rs` currently applies the Southern East Madagascar
   measurement flag/width ID to generic added identities. That logic must be
   made per-current before the four new identities are loaded. Nested entity
   metadata is now present in each identity admission, but no borrowed width
   status is accepted as a substitute for the T24 admission.
3. `planning.rs` requires a remaining-current route decision for every named
   current with no published length. Four source-pinned route-gap decisions
   now describe the unresolved axis/endpoints with no coordinates/candidates.
   Native planning lookup still needs to recognize their separate worklist.

The four planning decisions are in
`research/indian-current-reference-route-planning-v1.json`, bound to the frozen
identity review. They supply unresolved work, not physical routes. Seasonal
width/source completeness and updated dashboard/taxonomy/index receipts also
remain coordinated native/publication gates. The current live packet is not
modified while those gates are incomplete.

## Cloud rehearsal

`analysis/check_current_gap_parent_rehearsal.py --full-parent`:

1. Requires explicit opt-in, at least2GiB free disk and3GiB available memory.
   The automated full-packet path reads Linux memory availability; it cannot
   silently run a full parse on this disk-constrained Windows workspace.
2. Verifies the parent manifest's pinned logical digest before packet loading;
   the existing transport then checks every part and assembled digest.
3. Hashes every prior non-object collection in canonical row order, and records
   pre-mutation hashes of physical object fields and original capabilities.
4. Applies the verified79-row batch without re-executing old scientific
   producers, then verifies every original row prefix and physical object
   field/capability. Restored source refs and metadata changes stay separate.
5. Reports actual parent/candidate inventory totals, source-count mismatches,
   admission receipt, preservation hashes and peak resident memory.
6. Publishes no data packet, index, source asset or engine. Native validation
   is explicitly not attempted: the known integration changes are outstanding.

Only the receipt is uploaded as a CI artifact. The step runs sequentially in
the existing source job after every prerequisite check passes, on one logical
CPU at reduced priority. Source originals remain outside the artifact. The
rehearsal is not an alternative to typed guards, canonical builds or UI checks.

Nine small fixture tests passed locally, covering preservation of row order,
values, physical object fields/capabilities and pre-load resource rejection.
The full parent has not been loaded locally. The first actual cloud execution
is verified below; it did not attempt native/WASM or browser validation.

Current local focused checks:37 identity/provenance,19 compatible-source and16
scoped-width checks, plus9 rehearsal fixtures:81total. The identity/evidence/
width contracts were regenerated after the metadata compatibility corrections.
The prior Linux36/19/16 results, where verified, belong to their exact earlier
source commits; they are not silently reused as proof of this revision.

## Verified actual parent application

At commit`dc42d372101fc82674e663325e7874bcb1aadbf6`,
[job120719542984](https://github.com/giodl73-repo/OSW/actions/runs/40043432722/job/120719542984)
completed the full-parent rehearsal successfully. Both its actual log and
[artifact12540720397](https://github.com/giodl73-repo/OSW/actions/runs/40043432722/artifacts/12540720397)
were retrieved and inspected. Public proof:
`research/current-gap-parent-rehearsal-proof-v1.json`.

| Inventory | Parent | Prepared candidate |
|---|---:|---:|
| Collections |55 |60 |
| Records |108445 |108524 |
| Objects |242 |246 |
| Named currents |102 |106 |
| Width-evidence records |170 |171 |

All108203 prior non-object rows across54 collections matched canonical row
hashes in the original order; all242 old physical object fields and original
capabilities were preserved. Canonical hashes verify row content/order, not
identity of outer JSON whitespace. Registered source projection corrected119
existing owner records, and the candidate has zero count/reference mismatches.
The one scoped width remains a published T24 summary, not a raw sample or
annual envelope. Peak process RSS was1117360KiB on the cloud runner.

No packet, engine, index or source asset was published. Native validation was
not attempted. The next native/dashboard/seasonal/planning gates above remain
required. This proves actual data compatibility/preservation, not live atlas
coverage, browser behavior or a complete offline-suite pass.

Follow-up correction: unchanged object content now retains its prior overall
and section fingerprints. This prevents a recomputed hash from lighting an
otherwise unchanged record. A ninth fixture and the full-parent verifier
check this explicitly. The first proof above predates that metadata correction;
a fresh cloud receipt is required for its actual full-inventory behavior.
