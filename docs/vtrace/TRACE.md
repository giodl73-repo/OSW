# OSW Trace Matrix

Status: settled at native-role fixed point, 2026-09-07

## Scope

Repo: OSW — Ocean States of the World

This matrix connects each accepted product requirement to its mission parent,
controlled specification, interface/design/rigor allocation, proposed work,
verification, validation, and present evidence state. It is a planning and
evidence index, not implementation or release authority.

## Status model

Trace never compresses progress into one optimistic label. Every row carries:

- **requirement**: accepted, changed, retired, or rejected;
- **implementation**: absent, proposed, active, implemented, or superseded;
- **verification**: baseline partial, target pending, passed, failed, or blocked;
- **validation**: blocked, active, passed, failed, or not applicable with reason.

At this fixed point all 34 requirements are accepted; all nine work packages
remain proposed; only VFY-OSW-001 current-baseline evidence passes; target
VFY-OSW-002 through VFY-OSW-020 remain pending; and all eight validation
scenarios remain blocked. No row is fully implemented, verified, or validated.

## End-to-end requirement trace

| Trace | Requirement and intent | Parent need / constraint | Specification | Interface / design | Code rigor | Work package / surface | Verification | Validation | Evidence and current status |
|---|---|---|---|---|---|---|---|---|---|
| TR-OSW-001 | REQ-OSW-001 — three entrances plus complete research index | NEED-OSW-001, NEED-OSW-005 | SPEC-OSW-001, SPEC-OSW-002, SPEC-OSW-003 | IF-OSW-001; DES-OSW-001, DES-OSW-004 | CR-OSW-003, CR-OSW-015, CR-OSW-016 | WP-OSW-002; README/atlas/research entry | VFY-OSW-007, VFY-OSW-008 | VAL-SCN-OSW-001, VAL-SCN-OSW-003 | Current link/atlas tests partial; implementation proposed; target verification pending; validation blocked. |
| TR-OSW-002 | REQ-OSW-002 — ordered heat-event-to-partial-budget journey | NEED-OSW-002, NEED-OSW-005 | SPEC-OSW-004, SPEC-OSW-005 | IF-OSW-008; DES-OSW-004, DES-OSW-005 | CR-OSW-009, CR-OSW-010, CR-OSW-017 | WP-OSW-004; guided scenes/D-series | VFY-OSW-004, VFY-OSW-008 | VAL-SCN-OSW-001, VAL-SCN-OSW-008 | D1–D14 evidence exists separately; integrated journey absent; target pending/blocked. |
| TR-OSW-003 | REQ-OSW-003 — finding, strongest limitation, receipt per scene | NEED-OSW-003, NEED-OSW-005 | SPEC-OSW-006, SPEC-OSW-007 | IF-OSW-003, IF-OSW-008; DES-OSW-004, DES-OSW-005 | CR-OSW-003, CR-OSW-010, CR-OSW-017 | WP-OSW-004; scenes/content/receipts | VFY-OSW-002, VFY-OSW-008 | VAL-SCN-OSW-001, VAL-SCN-OSW-002 | Individual evidence exists; common scene contract unimplemented; target pending/blocked. |
| TR-OSW-004 | REQ-OSW-004 — resumable province selection by all entry paths | NEED-OSW-001, NEED-OSW-004 | SPEC-OSW-008, SPEC-OSW-009 | IF-OSW-002; DES-OSW-002, DES-OSW-003 | CR-OSW-014, CR-OSW-016 | WP-OSW-002; state/navigation/controls | VFY-OSW-007, VFY-OSW-010 | VAL-SCN-OSW-003 | Current province URL/keyboard behavior partial; canonical state target pending; validation blocked. |
| TR-OSW-005 | REQ-OSW-005 — no invented province aggregation | NEED-OSW-003, CON-OSW-001 | SPEC-OSW-010 | IF-OSW-004; DES-OSW-008, DES-OSW-009 | CR-OSW-003, CR-OSW-008, CR-OSW-017 | WP-OSW-003; view model/map/text | VFY-OSW-005, VFY-OSW-009 | VAL-SCN-OSW-004 | Current atlas states “no state aggregation”; universal admission target pending; validation blocked. |
| TR-OSW-006 | REQ-OSW-006 — controlled physical quantity identity | NEED-OSW-002, CON-OSW-002, CON-OSW-003 | SPEC-OSW-011, SPEC-OSW-012 | IF-OSW-007; DES-OSW-005, DES-OSW-006 | CR-OSW-006, CR-OSW-007 | WP-OSW-001, WP-OSW-006; contracts/science | VFY-OSW-002, VFY-OSW-004 | VAL-SCN-OSW-002, VAL-SCN-OSW-008 | Rich current conventions; closed common contract pending; validation blocked. |
| TR-OSW-007 | REQ-OSW-007 — residual remains unresolved | NEED-OSW-002, CON-OSW-004 | SPEC-OSW-011, SPEC-OSW-012 | IF-OSW-007; DES-OSW-005, DES-OSW-007 | CR-OSW-009 | WP-OSW-001, WP-OSW-004, WP-OSW-006; budget claims | VFY-OSW-004, VFY-OSW-014 | VAL-SCN-OSW-001, VAL-SCN-OSW-008 | Current examples preserve partial residual; universal rejection pending; validation blocked. |
| TR-OSW-008 | REQ-OSW-008 — motion evidence cannot become delivery/closure | NEED-OSW-004, CON-OSW-003 | SPEC-OSW-011, SPEC-OSW-012 | IF-OSW-007; DES-OSW-007, DES-OSW-014 | CR-OSW-004, CR-OSW-009 | WP-OSW-001, WP-OSW-006; motion/claim admission | VFY-OSW-004, VFY-OSW-014 | VAL-SCN-OSW-002, VAL-SCN-OSW-008 | M-series limitations exist; universal claim-ceiling fixtures pending; validation blocked. |
| TR-OSW-009 | REQ-OSW-009 — physics-tested, revisable borders | NEED-OSW-007, CON-OSW-005, CON-OSW-011 | SPEC-OSW-013, SPEC-OSW-014 | IF-OSW-015; DES-OSW-007, DES-OSW-014 | CR-OSW-004, CR-OSW-019 | WP-OSW-007; scorecards/zoning map | VFY-OSW-015 | VAL-SCN-OSW-005 | Organizational regions frozen/provisional; scorecard implementation/verification pending; validation blocked. |
| TR-OSW-010 | REQ-OSW-010 — mechanism-safe planetary comparison | NEED-OSW-008, CON-OSW-012 | SPEC-OSW-015, SPEC-OSW-016 | IF-OSW-014; DES-OSW-014 | CR-OSW-003, CR-OSW-006 | WP-OSW-008; comparison record/guide | VFY-OSW-016 | VAL-SCN-OSW-007 | Guide concepts exist; admitted paired comparison absent; target pending/blocked. |
| TR-OSW-011 | REQ-OSW-011 — no forecast/navigation/intervention/endorsement authority | Mission non-goals, CON-OSW-013 | SPEC-OSW-017, SPEC-OSW-018 | IF-OSW-010, IF-OSW-013; DES-OSW-007, DES-OSW-012 | CR-OSW-003, CR-OSW-021 | WP-OSW-001, WP-OSW-008, WP-OSW-009; claims/review/release | VFY-OSW-013 | VAL-SCN-OSW-001, VAL-SCN-OSW-006, VAL-SCN-OSW-007 | Current prose bounded; executable negative admission pending; validation blocked. |
| TR-OSW-012 | REQ-OSW-012 — complete quantitative receipt | NEED-OSW-003, NEED-OSW-006 | SPEC-OSW-019, SPEC-OSW-020 | IF-OSW-003, IF-OSW-007; DES-OSW-005, DES-OSW-006 | CR-OSW-006, CR-OSW-010 | WP-OSW-001, WP-OSW-004, WP-OSW-006, WP-OSW-008; receipts | VFY-OSW-002, VFY-OSW-012 | VAL-SCN-OSW-002 | Historical receipts heterogeneous; adapter/family target pending; validation blocked. |
| TR-OSW-013 | REQ-OSW-013 — distinct source/result/display/claim identities | NEED-OSW-003, NEED-OSW-006 | SPEC-OSW-019, SPEC-OSW-020 | IF-OSW-003, IF-OSW-012; DES-OSW-005, DES-OSW-011 | CR-OSW-010, CR-OSW-013 | WP-OSW-001, WP-OSW-004, WP-OSW-006; lineage/bindings | VFY-OSW-002, VFY-OSW-008, VFY-OSW-012 | VAL-SCN-OSW-002 | Many exact current checks; registry-wide mutation enforcement pending; validation blocked. |
| TR-OSW-014 | REQ-OSW-014 — orthogonal geometry/data/surface states | CON-OSW-002, CON-OSW-006 | SPEC-OSW-021, SPEC-OSW-022 | IF-OSW-009; DES-OSW-008, DES-OSW-009 | CR-OSW-008 | WP-OSW-001, WP-OSW-003, WP-OSW-006, WP-OSW-007; support/render | VFY-OSW-005, VFY-OSW-009 | VAL-SCN-OSW-003, VAL-SCN-OSW-004 | Interface amended; implementation and cross-family proof pending; validation blocked. |
| TR-OSW-015 | REQ-OSW-015 — explicit safe acquisition; offline default | NEED-OSW-006, CON-OSW-009 | SPEC-OSW-023, SPEC-OSW-024 | IF-OSW-011; DES-OSW-011 | CR-OSW-011, CR-OSW-012 | WP-OSW-001, WP-OSW-006; acquisition/custody | VFY-OSW-006, VFY-OSW-019 | VAL-SCN-OSW-006 | Default suite uses local assets; enforced network-denial and universal fault proof pending; validation blocked. |
| TR-OSW-016 | REQ-OSW-016 — mismatch stops affected claim | CON-OSW-002, CON-OSW-004 | SPEC-OSW-022, SPEC-OSW-024 | IF-OSW-009, IF-OSW-011; DES-OSW-007, DES-OSW-011 | CR-OSW-003, CR-OSW-008, CR-OSW-011 | WP-OSW-001, WP-OSW-006; validators/acquisition | VFY-OSW-005, VFY-OSW-006 | VAL-SCN-OSW-002, VAL-SCN-OSW-008 | Artifact-specific failures exist; full mismatch matrix pending; validation blocked. |
| TR-OSW-017 | REQ-OSW-017 — complete map context | NEED-OSW-001, NEED-OSW-003, CON-OSW-006 | SPEC-OSW-025, SPEC-OSW-026 | IF-OSW-004; DES-OSW-009 | CR-OSW-017 | WP-OSW-003, WP-OSW-007, WP-OSW-008; view model/maps | VFY-OSW-009 | VAL-SCN-OSW-004 | Common atlas strong; complete family applicability/admission pending; validation blocked. |
| TR-OSW-018 | REQ-OSW-018 — masks, seam, pole, coast across families | NEED-OSW-001, NEED-OSW-004, CON-OSW-006 | SPEC-OSW-022, SPEC-OSW-025, SPEC-OSW-026 | IF-OSW-004, IF-OSW-009; DES-OSW-008, DES-OSW-009 | CR-OSW-008, CR-OSW-017 | WP-OSW-003, WP-OSW-007; maps/support | VFY-OSW-005, VFY-OSW-009 | VAL-SCN-OSW-004 | Current shared atlas partial proof; all-family target pending; validation blocked. |
| TR-OSW-019 | REQ-OSW-019 — machine/non-color boundary classes | CON-OSW-005, CON-OSW-007 | SPEC-OSW-025, SPEC-OSW-026 | IF-OSW-004, IF-OSW-015; DES-OSW-009, DES-OSW-014 | CR-OSW-016, CR-OSW-017 | WP-OSW-003, WP-OSW-007; boundary render/text | VFY-OSW-009, VFY-OSW-010, VFY-OSW-015 | VAL-SCN-OSW-003, VAL-SCN-OSW-004, VAL-SCN-OSW-005 | Current atlas classes partial; universal/non-color belief proof pending; validation blocked. |
| TR-OSW-020 | REQ-OSW-020 — prohibit unsupported projection comparisons | CON-OSW-006 | SPEC-OSW-025, SPEC-OSW-026 | IF-OSW-004; DES-OSW-009, DES-OSW-010 | CR-OSW-003, CR-OSW-017 | WP-OSW-003, WP-OSW-007; map capabilities | VFY-OSW-009 | VAL-SCN-OSW-004, VAL-SCN-OSW-005 | Some limitations exist; common capability enforcement pending; validation blocked. |
| TR-OSW-021 | REQ-OSW-021 — all public actions keyboard/touch operable | NEED-OSW-005, CON-OSW-007 | SPEC-OSW-009, SPEC-OSW-027, SPEC-OSW-028 | IF-OSW-002, IF-OSW-008; DES-OSW-002, DES-OSW-009 | CR-OSW-015, CR-OSW-016 | WP-OSW-002, WP-OSW-003, WP-OSW-004; controls/scenes/maps | VFY-OSW-007, VFY-OSW-010 | VAL-SCN-OSW-003 | Current province controls partial; complete journey/access target pending; validation blocked. |
| TR-OSW-022 | REQ-OSW-022 — URL/visual/focus/name/announcement/text agree | CON-OSW-007 | SPEC-OSW-009, SPEC-OSW-027, SPEC-OSW-028 | IF-OSW-002, IF-OSW-004; DES-OSW-002, DES-OSW-009 | CR-OSW-014, CR-OSW-017 | WP-OSW-002, WP-OSW-003, WP-OSW-004; state/view | VFY-OSW-007, VFY-OSW-009, VFY-OSW-010 | VAL-SCN-OSW-003 | Several current states agree; transactional equivalence target pending; validation blocked. |
| TR-OSW-023 | REQ-OSW-023 — no unique color/hover/motion meaning | CON-OSW-007 | SPEC-OSW-027, SPEC-OSW-028 | IF-OSW-004; DES-OSW-009 | CR-OSW-016, CR-OSW-017 | WP-OSW-002, WP-OSW-003, WP-OSW-004; UI/map/text | VFY-OSW-009, VFY-OSW-010 | VAL-SCN-OSW-003 | Non-color support partial; reduced-motion/full-journey target pending; validation blocked. |
| TR-OSW-024 | REQ-OSW-024 — usable map/finding/limit/control/receipt at reflow | NEED-OSW-005, CON-OSW-007 | SPEC-OSW-029, SPEC-OSW-030 | IF-OSW-004; DES-OSW-009 | CR-OSW-016, CR-OSW-017 | WP-OSW-003, WP-OSW-004, WP-OSW-005; responsive integration | VFY-OSW-010, VFY-OSW-011 | VAL-SCN-OSW-003 | Controlled threshold discovery/implementation/evidence blocked. |
| TR-OSW-025 | REQ-OSW-025 — measured selected-view performance budget | CON-OSW-014 | SPEC-OSW-031, SPEC-OSW-032 | IF-OSW-006, IF-OSW-012; DES-OSW-010 | CR-OSW-018 | WP-OSW-005, WP-OSW-009; manifest/measurement/release | VFY-OSW-011, VFY-OSW-012 | VAL-SCN-OSW-003, VAL-SCN-OSW-006 | Hosted baseline/budget absent; discovery and validation blocked. |
| TR-OSW-026 | REQ-OSW-026 — deterministic family regeneration/integrity | NEED-OSW-006, CON-OSW-009 | SPEC-OSW-033, SPEC-OSW-034 | IF-OSW-012; DES-OSW-006, DES-OSW-011 | CR-OSW-012, CR-OSW-013 | WP-OSW-001, WP-OSW-005, WP-OSW-006, WP-OSW-007, WP-OSW-008; generators/families | VFY-OSW-012, VFY-OSW-019, VFY-OSW-020 | VAL-SCN-OSW-002, VAL-SCN-OSW-006 | Many current generators tested; complete admitted-family proof pending; validation blocked. |
| TR-OSW-027 | REQ-OSW-027 — bounded scientific-view intake before work | NEED-OSW-003, NEED-OSW-006 | SPEC-OSW-033, SPEC-OSW-034 | IF-OSW-007, IF-OSW-012; DES-OSW-007, DES-OSW-015 | CR-OSW-004, CR-OSW-025 | WP-OSW-001, WP-OSW-006, WP-OSW-007, WP-OSW-008; intake/research | VFY-OSW-002, VFY-OSW-012, VFY-OSW-013 | VAL-SCN-OSW-002, VAL-SCN-OSW-008 | Practice exists unevenly; common intake/admission target pending; validation blocked. |
| TR-OSW-028 | REQ-OSW-028 — optional/network failures remain local/actionable | CON-OSW-009 | SPEC-OSW-023, SPEC-OSW-024, SPEC-OSW-033, SPEC-OSW-034 | IF-OSW-011, IF-OSW-012; DES-OSW-011, DES-OSW-012 | CR-OSW-003, CR-OSW-012, CR-OSW-024 | WP-OSW-001, WP-OSW-005, WP-OSW-006, WP-OSW-007, WP-OSW-008; dependency boundaries | VFY-OSW-006, VFY-OSW-019 | VAL-SCN-OSW-006 | Several localized current paths; universal isolation proof pending; validation blocked. |
| TR-OSW-029 | REQ-OSW-029 — immutable bounded external review | NEED-OSW-005 | SPEC-OSW-035, SPEC-OSW-036 | IF-OSW-013; DES-OSW-007, DES-OSW-012 | CR-OSW-010, CR-OSW-021 | WP-OSW-001, WP-OSW-008, WP-OSW-009; review records | VFY-OSW-002, VFY-OSW-013 | VAL-SCN-OSW-002, VAL-SCN-OSW-006 | Current roles reviews increasingly hashed; universal record contract pending; validation blocked. |
| TR-OSW-030 | REQ-OSW-030 — exactly one lifecycle state | CON-OSW-010 | SPEC-OSW-037, SPEC-OSW-038 | IF-OSW-005, IF-OSW-010; DES-OSW-007, DES-OSW-013 | CR-OSW-019, CR-OSW-020 | WP-OSW-009; lifecycle/reconciler | VFY-OSW-003, VFY-OSW-017 | VAL-SCN-OSW-006 | Current status surfaces drift; reconciler implementation/evidence pending; validation blocked. |
| TR-OSW-031 | REQ-OSW-031 — immutable reconciled release candidate | NEED-OSW-006, CON-OSW-010 | SPEC-OSW-037, SPEC-OSW-038 | IF-OSW-005, IF-OSW-013; DES-OSW-013 | CR-OSW-010, CR-OSW-020, CR-OSW-021 | WP-OSW-009; packet/status/citation | VFY-OSW-013, VFY-OSW-017 | VAL-SCN-OSW-006 | Current conflict recorded; pure packet/reconciliation target pending; validation blocked. |
| TR-OSW-032 | REQ-OSW-032 — hosted proof and retain/restore | CON-OSW-010 | SPEC-OSW-039, SPEC-OSW-040 | IF-OSW-005; DES-OSW-013 | CR-OSW-020 | WP-OSW-009; deploy/smoke/rollback | VFY-OSW-018 | VAL-SCN-OSW-006 | Host/proof/mechanism discovery absent; verification and validation blocked; no release readiness. |
| TR-OSW-033 | REQ-OSW-033 — versioned URL compatibility and announced fallback | NEED-OSW-004, CON-OSW-007 | SPEC-OSW-008, SPEC-OSW-009, SPEC-OSW-041, SPEC-OSW-042, SPEC-OSW-043 | IF-OSW-002; DES-OSW-002, DES-OSW-003 | CR-OSW-003, CR-OSW-014 | WP-OSW-002, WP-OSW-009; state/compatibility/release | VFY-OSW-007 | VAL-SCN-OSW-003, VAL-SCN-OSW-006 | Current query behavior partial; owner policy discovery and target proof pending; validation blocked. |
| TR-OSW-034 | REQ-OSW-034 — preserve no-account/upload/cookie/telemetry boundary | CON-OSW-014 | SPEC-OSW-044, SPEC-OSW-045 | IF-OSW-006; DES-OSW-001, DES-OSW-010 | CR-OSW-018, CR-OSW-021 | WP-OSW-002, WP-OSW-005, WP-OSW-009; browser requests/privacy | VFY-OSW-011, VFY-OSW-013 | VAL-SCN-OSW-003, VAL-SCN-OSW-006 | Static no-collection baseline observed; controlled request/release proof pending; validation blocked. |

## Evidence pointer index

The wide matrix supports completeness; these concern-first routes provide a
shorter audit path and concrete current evidence pointers.

| Concern | Trace rows | Current evidence family | Target authority |
|---|---|---|---|
| Public entrances and guided heat journey | TR-OSW-001–003 | `README.md`, `atlas/index.html`, `analysis/test_atlas.py`, `research/osw-d1-*` through `research/osw-d14-*` | WP-OSW-002/004; VFY-OSW-007/008; VAL-SCN-OSW-001 |
| Province state, map support, cartography, and access | TR-OSW-004, TR-OSW-005, TR-OSW-014, TR-OSW-017–025, TR-OSW-033, TR-OSW-034 | `atlas/`, `figures/`, `analysis/test_atlas.py` | WP-OSW-002/003/005; VFY-OSW-005/007/009–011; VAL-SCN-OSW-003/004 |
| Quantity, budget, motion, custody, and receipts | TR-OSW-006–008, TR-OSW-012, TR-OSW-013, TR-OSW-015, TR-OSW-016, TR-OSW-026–028 | `SOURCE-REGISTER.md`, `MOTION.md`, `research/ocean-object-evidence-receipts.json`, `research/osw-d*.json`, focused `analysis/test_*` modules | WP-OSW-001/006; VFY-OSW-002–006/012/014/019/020; VAL-SCN-OSW-002/006/008 |
| Transport-tested zoning | TR-OSW-009, TR-OSW-019, TR-OSW-020 | `research/osw-motion-*.json`, `research/osw-motion-*.csv`, motion/region tests | WP-OSW-007; VFY-OSW-015; VAL-SCN-OSW-005 |
| Planetary comparison | TR-OSW-010 | `guides/07-OCEANS-AND-GAS-GIANTS.md` | WP-OSW-008; VFY-OSW-016; VAL-SCN-OSW-007 |
| Authority, review, lifecycle, performance, and release | TR-OSW-011, TR-OSW-025, TR-OSW-029–032, TR-OSW-034 | `PREVIEW-STATUS.md`, `PUBLICATION-CHECKLIST.md`, `CITATION.cff`, hashed role reviews, `.github/workflows/validate.yml` | WP-OSW-005/009; VFY-OSW-011/013/017–020; VAL-SCN-OSW-006 |

Wildcards above identify families for navigation, not immutable evidence. An
executed evidence record must enumerate exact paths and hashes.

## PITFALL crosswalk

| Pitfall | Preventing trace rows | Required negative evidence |
|---|---|---|
| SI-01 | TR-OSW-005, TR-OSW-006, TR-OSW-012 | Incompatible quantity/aggregation/receipt fails admission and public claim. |
| SI-02 | TR-OSW-007 | Residual/process and near-closure fixtures fail; reader/scientist retain non-closure. |
| SI-03 | TR-OSW-008, TR-OSW-009 | Motion/path/open-section evidence cannot become delivery/convergence or border proof. |
| DN-01 | TR-OSW-006, TR-OSW-012, TR-OSW-016 | Sign/reference/unit mismatch stops the affected result with named diagnostic. |
| DN-02 | TR-OSW-014–016, TR-OSW-028 | Sampling/support/custody/dependency failures remain distinct, local, and non-destructive. |
| CA-01 | TR-OSW-014, TR-OSW-017, TR-OSW-018 | Land/seam/pole/ice/missing cases cannot create an object or valid value. |
| CA-02 | TR-OSW-005, TR-OSW-009, TR-OSW-019, TR-OSW-020 | Schematic/attractive boundary and unsupported comparison cannot gain authority from rendering. |
| DL-01 | TR-OSW-030–032 | Drift or hosted failure produces hold/retain/restore without advancing current/citation state. |
| DL-02 | TR-OSW-003, TR-OSW-012, TR-OSW-013, TR-OSW-029 | Result/receipt/review mutation invalidates dependent claim, scene, artifact, or review credit. |
| DL-03 | TR-OSW-025, TR-OSW-026, TR-OSW-028, TR-OSW-034 | Undeclared/eager payload, provider dependency, persistence, or verifier residue fails. |

## Machine-expanded coverage inventories

These lists deliberately avoid typographic ranges so structural checks can
detect orphans.

- Needs: NEED-OSW-001, NEED-OSW-002, NEED-OSW-003, NEED-OSW-004,
  NEED-OSW-005, NEED-OSW-006, NEED-OSW-007, NEED-OSW-008.
- Requirements: REQ-OSW-001, REQ-OSW-002, REQ-OSW-003, REQ-OSW-004,
  REQ-OSW-005, REQ-OSW-006, REQ-OSW-007, REQ-OSW-008, REQ-OSW-009,
  REQ-OSW-010, REQ-OSW-011, REQ-OSW-012, REQ-OSW-013, REQ-OSW-014,
  REQ-OSW-015, REQ-OSW-016, REQ-OSW-017, REQ-OSW-018, REQ-OSW-019,
  REQ-OSW-020, REQ-OSW-021, REQ-OSW-022, REQ-OSW-023, REQ-OSW-024,
  REQ-OSW-025, REQ-OSW-026, REQ-OSW-027, REQ-OSW-028, REQ-OSW-029,
  REQ-OSW-030, REQ-OSW-031, REQ-OSW-032, REQ-OSW-033, REQ-OSW-034.
- Specifications: SPEC-OSW-001, SPEC-OSW-002, SPEC-OSW-003, SPEC-OSW-004,
  SPEC-OSW-005, SPEC-OSW-006, SPEC-OSW-007, SPEC-OSW-008, SPEC-OSW-009,
  SPEC-OSW-010, SPEC-OSW-011, SPEC-OSW-012, SPEC-OSW-013, SPEC-OSW-014,
  SPEC-OSW-015, SPEC-OSW-016, SPEC-OSW-017, SPEC-OSW-018, SPEC-OSW-019,
  SPEC-OSW-020, SPEC-OSW-021, SPEC-OSW-022, SPEC-OSW-023, SPEC-OSW-024,
  SPEC-OSW-025, SPEC-OSW-026, SPEC-OSW-027, SPEC-OSW-028, SPEC-OSW-029,
  SPEC-OSW-030, SPEC-OSW-031, SPEC-OSW-032, SPEC-OSW-033, SPEC-OSW-034,
  SPEC-OSW-035, SPEC-OSW-036, SPEC-OSW-037, SPEC-OSW-038, SPEC-OSW-039,
  SPEC-OSW-040, SPEC-OSW-041, SPEC-OSW-042, SPEC-OSW-043, SPEC-OSW-044,
  SPEC-OSW-045.
- Interfaces: IF-OSW-001, IF-OSW-002, IF-OSW-003, IF-OSW-004,
  IF-OSW-005, IF-OSW-006, IF-OSW-007, IF-OSW-008, IF-OSW-009,
  IF-OSW-010, IF-OSW-011, IF-OSW-012, IF-OSW-013, IF-OSW-014,
  IF-OSW-015.
- Design: DES-OSW-001, DES-OSW-002, DES-OSW-003, DES-OSW-004,
  DES-OSW-005, DES-OSW-006, DES-OSW-007, DES-OSW-008, DES-OSW-009,
  DES-OSW-010, DES-OSW-011, DES-OSW-012, DES-OSW-013, DES-OSW-014,
  DES-OSW-015.
- Code rigor: CR-OSW-001, CR-OSW-002, CR-OSW-003, CR-OSW-004,
  CR-OSW-005, CR-OSW-006, CR-OSW-007, CR-OSW-008, CR-OSW-009,
  CR-OSW-010, CR-OSW-011, CR-OSW-012, CR-OSW-013, CR-OSW-014,
  CR-OSW-015, CR-OSW-016, CR-OSW-017, CR-OSW-018, CR-OSW-019,
  CR-OSW-020, CR-OSW-021, CR-OSW-022, CR-OSW-023, CR-OSW-024,
  CR-OSW-025.
- Work packages: WP-OSW-001, WP-OSW-002, WP-OSW-003, WP-OSW-004,
  WP-OSW-005, WP-OSW-006, WP-OSW-007, WP-OSW-008, WP-OSW-009.
- Verification: VFY-OSW-001, VFY-OSW-002, VFY-OSW-003, VFY-OSW-004,
  VFY-OSW-005, VFY-OSW-006, VFY-OSW-007, VFY-OSW-008, VFY-OSW-009,
  VFY-OSW-010, VFY-OSW-011, VFY-OSW-012, VFY-OSW-013, VFY-OSW-014,
  VFY-OSW-015, VFY-OSW-016, VFY-OSW-017, VFY-OSW-018, VFY-OSW-019,
  VFY-OSW-020.
- Validation: VAL-SCN-OSW-001, VAL-SCN-OSW-002, VAL-SCN-OSW-003,
  VAL-SCN-OSW-004, VAL-SCN-OSW-005, VAL-SCN-OSW-006,
  VAL-SCN-OSW-007, VAL-SCN-OSW-008.
- Fixtures: FIX-OSW-001, FIX-OSW-002, FIX-OSW-003, FIX-OSW-004,
  FIX-OSW-005, FIX-OSW-006, FIX-OSW-007, FIX-OSW-008, FIX-OSW-009,
  FIX-OSW-010, FIX-OSW-011, FIX-OSW-012, FIX-OSW-013, FIX-OSW-014,
  FIX-OSW-015, FIX-OSW-016, FIX-OSW-017, FIX-OSW-018, FIX-OSW-019,
  FIX-OSW-020. Fixture-to-contract/package ownership is controlled by
  `VERIFICATION.md`; all remain target pending.

## Evidence-state ledger

| Evidence class | Current state | Controlling source | Promotion rule |
|---|---|---|---|
| Left-side VTRACE artifacts | settled at native-role fixed points | `docs/vtrace/` plus hashed role reviews | Re-review when controlled parent meaning changes. |
| Current repository baseline | passed for executed default commands | EVID-VFY-OSW-001–006 | Does not satisfy a target requirement by itself. |
| Target verification | pending | EVID-VFY-OSW-007–011; VFY-OSW-002–020 | Pass only after implemented fixture/command executes against immutable candidate. |
| Validation execution | blocked | EVID-VAL-OSW-001–009 | Pass only after prerequisites and controlled human/scientific/release protocol execute. |
| Work packages | proposed / proposed-deferred | `WORK_PACKAGES.md` | Require entry criteria, applicable VFY IDs, role lanes, and explicit execution authority. |
| Public release | not authorized | IF-OSW-005; WP-OSW-009 | Requires reconciled candidate, all applicable evidence, hosted proof, and owner approval. |

## Bidirectional audit rules

- Forward: every accepted requirement must reach a specification, owning
  interface/design, work/disposition, VFY item, validation scenario or explicit
  rationale, and present evidence state.
- Backward: every work package, VFY/FIX item, validation scenario, public claim,
  and release decision must name its requirement/specification parents.
- Change impact: a parent meaning, ID, interface version, artifact identity,
  claim ceiling, verification command, validation protocol, or lifecycle change
  marks dependent trace rows stale until inspected and re-signed.
- No range-only proof: compact ranges may aid reading, but machine-expanded
  inventories control orphan checks.
- No status inheritance: a parent fixed point, current test, role review, or
  successful neighboring row never promotes a dependent implementation,
  verification, validation, or release state.
- Historical evidence remains linked when superseded; trace correction creates
  a new reviewed identity rather than silently rewriting the old record.

## Trace gaps

| Gap | Affected rows | Present control |
|---|---|---|
| URL version/window policy unknown | TR-OSW-004, TR-OSW-033 | WP-OSW-002 discovery; VFY-OSW-007 pending; VAL-SCN-OSW-003 blocked. |
| Complete artifact/map-family inventories absent | TR-OSW-012–014, TR-OSW-017–020, TR-OSW-026 | WP-OSW-001/003; VFY-OSW-002/009/012 pending. |
| Responsive/performance thresholds absent | TR-OSW-024, TR-OSW-025 | WP-OSW-005 measurement; VFY-OSW-010/011 pending; Validation blocked. |
| Network-denial/non-mutation evidence absent | TR-OSW-015, TR-OSW-026, TR-OSW-028 | VFY-OSW-019/020 pending; VAL-SCN-OSW-006 blocked. |
| Deployment host/proof/retain-restore unknown | TR-OSW-030–032 | WP-OSW-009 discovery; VFY-OSW-017/018 pending; no release readiness. |
| Human/scientific scenario evidence absent | all user/research outcome rows | EVID-VAL-OSW-001–009 remain blocked; no validation status inherited. |

## Trace gate

Decision: `pass_with_risk`

- [x] Every one of the 34 accepted requirements has an end-to-end trace row.
- [x] All 8 needs, 45 specs, 15 interfaces, 15 designs, 25 rigor constraints, 9 packages, 20 verification IDs, and 8 validation scenarios are machine-visible.
- [x] Requirement, implementation, verification, and validation states are independent.
- [x] Current baseline proof is not promoted into target evidence.
- [x] Unknowns, pending targets, blocked scenarios, and release non-authority remain explicit.
- [x] Forward, backward, change-impact, stale-evidence, and historical-record rules are defined.
- [x] All eight native roles resolve every P1/P2 trace finding.

Final Review is authorized next but remains unopened. Work packages remain
proposed and no implementation, validation execution, or release is authorized.

## Source links

- [Mission](MISSION.md)
- [Requirements](REQUIREMENTS.md)
- [Specification Baseline](SPECIFICATION_BASELINE.md)
- [Interfaces](INTERFACES.md)
- [Detailed Design](DESIGN.md)
- [Code Rigor](CODE_RIGOR.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Work Packages](WORK_PACKAGES.md)
- [Verification](VERIFICATION.md)
- [Validation](VALIDATION.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Native roles](../../.roles/ROLE.md)
- [Trace roles review](../../signals/roles/check/trace-roles-check-2026-09-07.md)
