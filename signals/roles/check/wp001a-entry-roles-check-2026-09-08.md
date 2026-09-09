---
skill: roles-check
topic: wp001a-entry
date: 2026-09-08
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — WP-OSW-001A implementation entry

**Artifact type:** bounded implementation-entry packet

**Source commit:** `da7b463a2720794bbe9baa43a55924d3be9bbb3c`

**Reviewed artifact:**
`context/waves/2026-09-08-wp001a-contract-foundation/ENTRY.md`

**Fixed-point artifact identity:**

| Artifact | SHA-256 |
|---|---|
| `context/waves/2026-09-08-wp001a-contract-foundation/ENTRY.md` | `AA1EFAE44C3C2CBC65D7AB60677B9D87F9A4B3332473D9D9B8BAF17389822AC1` |

## Role selection

All eight OSW roles were selected. Even this internal kernel controls physical
quantity names, data/support identity, map-facing states, public diagnostics,
access semantics, executable evidence, repository authority, and possible
planetary comparison identity.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Quantity vocabulary implementation could become scientific calculation or causal admission. | P2 | Decision / prohibited mutations | Limit 001-A to identity and validation shape; prohibit calculations, acquisition, and claim promotion. **Resolved.** |
| 2 | A closed vocabulary could silently assign unknown values to the nearest known physical class. | P2 | Frozen vocabulary | Require exact match or explicit bounded unknown/unavailable behavior. **Resolved.** |
| 3 | Later quantity semantics still require CURRENT veto. | P3 | Closeout | Retain CURRENT in closeout and future adapter admission. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Family scope could expand while adapters are being explored. | P2 | Entry basis / owned mutations | Freeze inventory and prohibit historical adapters until separately reviewed 001-B. **Resolved.** |
| 2 | Unknown/unavailable source meaning could be erased by constructor defaults. | P2 | Vocabulary/invariants | Make absence explicit and test that source records are never rewritten or fabricated. **Resolved.** |
| 3 | Exact entry commit, tree, Review hash, runtime, and test times are retained. | P3 | Immutable basis | Preserve these identities in closeout. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A single support enum would collapse land, missing data, and sea ice. | P2 | Vocabulary/invariants | Implement three orthogonal axes and retain subsurface-under-ice regression evidence. **Resolved.** |
| 2 | Diagnostic work could leak into renderer or atlas changes. | P2 | Owned mutations | Explicitly exclude atlas, figures, map data, and public pages. **Resolved.** |
| 3 | Map view-model implementation remains WP-OSW-003. | P3 | Prohibitions | Keep the package boundary. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Contract foundation” could sound like a finished evidence system. | P2 | Decision / result | State that target verification, Validation, and package closure remain unearned. **Resolved.** |
| 2 | Diagnostics could echo unsafe provider text or imply authority. | P2 | Invariants | Use stable codes and bounded safe context; forbid arbitrary payload echo and authority transfer. **Resolved.** |
| 3 | VTRACE language remains internal. | P3 | Scope | Preserve the visitor/process boundary. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Closed states without explicit unknown behavior can create inaccessible silent fallback later. | P2 | Frozen vocabulary | Require field-local explicit failure/unknown state that later channels can announce. **Resolved.** |
| 2 | 001-A cannot claim accessible UI merely because it defines support/state identity. | P2 | Entry result | Keep VAL-SCN-OSW-003 and all user-facing state work blocked. **Resolved.** |
| 3 | HARBOR should inspect public-semantic fields even before renderer work. | P3 | Closeout roles | Include HARBOR where affected. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Baseline evidence needs exact commit/tree/runtime/times and an honest network boundary. | P2 | Basis / L1 receipt | Record identities and distinguish ordinary offline behavior from enforced denial. **Resolved.** |
| 2 | Broad path ownership could allow 001-B/001-C behavior into the first pulse. | P2 | Owned mutations / stop | Name exact files, authorized results, negative cases, and a hard post-closeout stop. **Resolved.** |
| 3 | The failed unquoted Git-tree probe is useful reproducibility evidence. | P3 | Basis | Retain it and the corrected command outcome. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Baseline commit permission could be confused with push or broader repository mutation. | P2 | Decision | Record the local commit and keep push, merge, deployment, release, and cross-repo change unauthorized. **Resolved.** |
| 2 | Entry needs declared governance mutations as well as product paths. | P2 | Owned mutations | Include wave and role/evidence records in the mutation inventory. **Resolved.** |
| 3 | Existing status/citation/research artifacts remain outside pulse ownership. | P3 | Prohibitions | Preserve them byte-for-byte unless entry is amended. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Shared identity types might be read as authorization to register a planetary comparison. | P2 | Decision / prohibitions | Keep comparison records and WP-OSW-008 blocked. **Resolved.** |
| 2 | Planetary-specific vocabulary needs ORBIT review before entry. | P2 | Closeout roles | Require ORBIT whenever 001-A touches comparison identity. **Resolved.** |
| 3 | No planetary product file is an owned mutation. | P3 | Owned mutations | Retain this boundary. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: 001-A must encode identity and safe diagnostic shape without
silently starting adapters, admission, science, rendering, or release work.

Cross-role consensus: freeze the exact entry basis and vocabulary, name every
allowed mutation, fail unknown/unsafe states explicitly, and stop after the
single reversible pulse.
```

All 16 P2 findings are repaired in the reviewed entry packet. Remaining
conditions are implementation evidence: obey the declared paths and negative
cases, retain exact entry/closeout identities, keep target VFY and Validation
states honest, and return for a separate closeout and 001-B entry decision.

## Amendments

1. Narrowed owned paths and results to registry/identity contracts, tests,
   invented fixtures, and declared governance evidence.
2. Added exact baseline receipts, honest network/non-mutation boundaries,
   vocabulary invariants, and adversarial diagnostic cases.
3. Added explicit waiver applicability, stop/rollback rules, evidence fields,
   and non-authorization for every later effect.

Fixed-point decision: `pass_with_risk` for WP-OSW-001 pulse 001-A entry only.
Implementation may begin from baseline `da7b463`; it must stop after the pulse
for separate closeout. No push, merge, deployment, validation, release, external
contact, NASA affiliation, or cross-repository change is authorized or implied.
