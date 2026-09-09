---
skill: roles-check
topic: wp001b-entry
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — WP-OSW-001B entry

**Artifact type:** bounded implementation-entry proposal for versioned
historical-evidence adapters

**Source commit:** `1bdfbc31d14cfd1092d8c5a1216e5764d34f4392` plus the reviewed entry packet

**Reviewed entry SHA-256:**
`958AB379E42521474BB522040D75E677C9799844E8A716DB6DB18D14172A6EE5`

## Role selection

All eight native roles are selected. CURRENT and SOUNDER govern scientific
meaning and custody; CHART and HARBOR govern orthogonal support meaning that
later maps/text must share; BEACON governs claim ceilings; KEEL governs
lossless deterministic proof; LOGBOOK governs immutable scope and repository
truth; ORBIT confirms that shared contracts do not admit planetary evidence.

## Findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Adapting D12–D14 as one chain could imply a native closed heat budget. | P2 | Frozen inventory / authorized result | Preserve three quantities, model origins, supports, and cross-system ceilings; prohibit closure and causal labels. **Resolved.** |
| 2 | Structural mapping could invent sign, reference, depth, or process meaning absent upstream. | P2 | Adapter contract | Mark scientifically interpreted fields unavailable unless exactly mapped by a reviewed rule. **Resolved.** |
| 3 | The inventory selects the three records needed for event anatomy without recomputing them. | P3 | Decision | Keep scientific calculation and later challenge work outside 001-B. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A normal JSON parser can silently discard duplicate object names or accept non-finite values. | P2 | Parser contract | Reject duplicate names, non-finite numbers, invalid UTF-8, and trailing content before dispatch. **Resolved.** |
| 2 | D12–D14 reference D11 and provider/source artifacts that are not in the frozen inventory. | P2 | Frozen inventory | Preserve those references as opaque identities; do not recursively open or claim complete provenance. **Resolved.** |
| 3 | Exact paths, schemas, byte sizes, and SHA-256 identities bound the historical inputs. | P3 | Inventory | Recheck all identities at implementation closeout. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Record-level source fields cannot establish cell-level land, missingness, or sea-ice state. | P2 | Orthogonal support | Emit explicit unavailable axes instead of inferring support from numeric maps, zero, or null. **Resolved.** |
| 2 | Adapting bridge maps could be mistaken for authorizing map display. | P2 | Prohibited mutations | Keep rendering/view models in WP-OSW-003 and preserve map arrays only as source content. **Resolved.** |
| 3 | The valid-subsurface-under-ice fixture protects the three-axis model. | P3 | Fixtures | Retain it without claiming these records supply real ice classification. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “First admitted families” could make adapter success sound like scientific/public admission. | P2 | Decision / parents | Call them adapter candidates and explicitly exclude IF-OSW-010 admission. **Resolved.** |
| 2 | “Lossless bytes” could imply regenerated JSON is byte-identical despite formatting/lexeme changes. | P2 | Authorized result | Separate bound raw-byte hash from semantic parsed-tree round trip. **Resolved.** |
| 3 | The packet keeps the existing limitation text adjacent to supported mappings. | P3 | Cross-system ceiling | Preserve that claim ceiling through later scenes. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Missing support encoded only as null would be unavailable to later text/state channels. | P2 | Unavailable fields | Require explicit field path, reason, and claim restriction. **Resolved.** |
| 2 | An adapter has no user interface and cannot satisfy accessible map or announcement Validation. | P2 | Entry result | Keep reader, map, and VAL-SCN-OSW-003 evidence blocked. **Resolved.** |
| 3 | Deterministic unavailable-field order supports equivalent later rendering. | P3 | Determinism | Test stable ordering at implementation. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Semantic round trip can miss raw-byte mutation unless both identities are tested. | P2 | Adapter/fixture contract | Bind raw SHA-256 separately and compare the complete parsed tree, including unknown fields and array order. **Resolved.** |
| 2 | Tests could accidentally follow embedded paths/URLs or write sidecars. | P2 | Ambient effects | Prohibit recursive opens, network, writes, and logging/environment mutation; inspect before/after trees. **Resolved.** |
| 3 | The refreshed L1 baseline passes 477 pytest and 346 unittest tests. | P3 | Baseline receipt | Treat this only as entry evidence and rerun on the implementation commit. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A broad adapter path could silently expand into the repository's many JSON families. | P2 | Frozen inventory | Limit dispatch to three exact schema IDs and require amended entry for any additional family. **Resolved.** |
| 2 | Prior push authority could be misread as standing authority for this pulse. | P2 | Immutable basis / decision | State that implementation begins only after entry commit and that push/merge/deploy remain unauthorized. **Resolved.** |
| 3 | Existing JSON and public/status files are explicitly read-only or out of scope. | P3 | Owned mutations | Confirm their hashes and status at closeout. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Shared quantity/support contracts might be mistaken for admitting gas-giant evidence. | P2 | Controlled parents | Exclude comparison families and IF-OSW-010; retain WP-OSW-008 as blocked. **Resolved.** |
| 2 | No Earth-to-planet mechanism transfer is evaluated in this pulse. | P2 | Entry result | Do not claim planetary Validation or analogy support from adapter success. **Resolved.** |
| 3 | ORBIT remains useful here only as a scope-veto lane. | P3 | Role selection | Re-engage for any future comparison-family adapter. **Accepted.** |

## Synthesis

```
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: adapter success must preserve source meaning without becoming
scientific admission, native-budget closure, or authority to widen families.

Cross-role consensus: bind raw bytes and semantic structure separately, reject
ambiguous JSON before dispatch, preserve absent support/provenance explicitly,
and prevent recursive I/O or source mutation.
```

All 16 P2 findings are repaired in the reviewed entry packet. Remaining
conditions are implementation evidence: commit the exact entry fixed point,
obey the three-family inventory and owned paths, pass all preservation/failure
fixtures, retain every pending/blocked state, and return for closeout.

## Amendments

1. Distinguished raw-byte SHA-256 identity from semantic parsed-tree round trip
   and added strict duplicate-name/non-finite/encoding/trailing-data rejection.
2. Made referenced D11/provider/source records opaque and prohibited recursive
   file or URL access, sidecars, and inferred cell-support metadata.
3. Clarified that the three families are adapter candidates, not federated
   admissions, and preserved all reader/map/science/planetary/release gates.

Fixed-point decision: `pass_with_risk` for WP-OSW-001 pulse 001-B entry only.
Implementation may begin after this exact packet and review are committed. It
must stop for separate closeout before 001-C. No push, merge, deployment,
validation, release, external contact, or cross-repository change is authorized.
