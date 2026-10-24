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

Eight small fixture tests passed locally, covering preservation of row order,
values, physical object fields/capabilities and pre-load resource rejection.
The full parent has not been loaded locally. Full cloud execution and its
result must be inspected before claiming that actual79-row integration passed.

Current local focused checks:37 identity/provenance,19 compatible-source and16
scoped-width checks, plus8 rehearsal fixtures:80total. The identity/evidence/
width contracts were regenerated after the metadata compatibility corrections.
The prior Linux36/19/16 results, where verified, belong to their exact earlier
source commits; they are not silently reused as proof of this revision.
