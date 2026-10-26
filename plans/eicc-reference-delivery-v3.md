# EICC admission, query and atlas integration v3

## Verified failure and source audit

Run40364739085/attempt2/job121726666243 completed with failure, then its request was
disabled at remote2e4173908a0008261c79f7ba69eaa095617a8bba. Its only compact artifact
contains `failure.json`: candidate preparation rejected the assumed original EICC
worklist. No native build, Rust planning tests, WASM build or browser verification
ran in this attempt. The earlier v1 case's two engine builds are separate history.

The actual admitted source contract is
`research/indian-current-reference-route-planning-v1.json`; the exact prior decision
is in `research/indian-current-identity-query-contract-v1.json`. The prototype reads
these small authoritative source files directly and checks both their hashes and
the complete prior decision. It does not load the installed packet.

The audit also found additional existing guards that must agree before another
cloud attempt. Bypassing one guard or rerunning v2 will not complete this integration.

## Required implementation and proof

| Area | Required change | Evidence needed |
|---|---|---|
| Planning | Validate the actual compiled admission decision, exact saved query-contract bytes and candidate bytes, and retain the exact prior decision. | Positive source-bound revision test; changed prior/source/URL/route rejects. |
| Current-gap admissions | Permit only this verified EICC editorial extension while keeping the exact earlier admission as history. Preserve all width, measurement, date, state and identity guards. | Tests accept two editorial references and reject any physical promotion or changed original record. |
| Seasonal store | Include the two verified references in complete route-inventory checks. They carry no temporal geometry, annual range or playback phase. | Store initialization and seasonal snapshot agree on complete route inventory without enabling playback. |
| Atlas store | Recognize only the two source-bound new rows through the exact query contract; preserve every earlier route/source receipt. | Complete atlas snapshot preserves old records and exposes both new references. |
| Atlas catalog | Add two cards for one current, update its worklist decision and strategy counts, keep length ordering unchanged. | Counts and selected route IDs match source/owner data; repeated projection rejected. |
| Route cards | Accept validated inline rendering reports before the legacy file loader. Inline reports retain actual source file/pointer links and are explicitly derived display data. | Both cards, images and global-map selection render; old cards still use their existing sources. |
| Map panel | Label editorial bend-probe spans correctly, with hover/focus names and source scopes retained. | Actual desktop/phone screenshots and direct selection checks. |
| Delivery | Complete source/native/Rust/WASM checks before installing browser dependencies. Keep one cloud job/CPU and source custody across phases. | Engine receipt before browser setup; bounded diagnostic logs on failure. |

`analysis/eicc_reference_projection_v3.py` specifies the source-side projection and
inline card payloads. Its small fixtures use the real prior admission record. This
is a prototype contract, not runtime approval. The corresponding Rust/UI adapters,
compiler scope, phased cloud controller and held workflow are still outstanding.

## Preservation and measurement rules

- Same installed Loop parent:189986194 bytes,108574 rows,246 objects,106 currents,
  172 scoped-width rows and601 indexed source documents.
- Intended addition remains2 reference routes,7 sampling records,6 spectral scales
  and3 source definitions:108592 candidate rows,609 source documents. Inline
  rendering reports do not add observations or invent source-file addresses.
- Keep source-table points unmapped, point G qualified as outlet context, bathymetry
  distinct from current depth, spectral scales distinct from physical widths.
- Keep the590km and630km conventions separate. Their590–600 and620–640 rounded
  bend-probe spans are editorial sensitivity, not physical extrema or uncertainty.
- Keep physical state membership unknown; an empty presentation link list represents
  no admitted links, not a claim of zero intersections. No NASA identity inferred.
- Preserve all old source strings except the dashboard projection, every prior
  measurement and every other current/eddy owner. Preserve published length ranks.
- Declare all runtime/UI source changes and archive prior source bytes, including
  the executed v2 planning implementation. Historical source preflights remain valid
  through explicit relocation checks. No unqualified checksum exceptions.

Before the next activation: implement the required adapters, run only small local
checks, prepare disabled request/held workflow, verify source custody, then run one
sequential cloud case. Add actual atlas/seasonal API checks to the existing query
and source comparisons. Disable requests after terminal outcomes; inspect actual
screenshots before exact saved-artifact installation. No local heavy jobs, new PR,
main merge or scientific release. The wider data-gap objective remains open.
