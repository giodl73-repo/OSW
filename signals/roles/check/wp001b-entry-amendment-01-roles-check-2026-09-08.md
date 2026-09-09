---
skill: roles-check
topic: wp001b-entry-amendment-01
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — WP-OSW-001B entry amendment 01

**Artifact type:** narrow scientific identity-contract amendment

**Source commit:** `29b7c47b` plus amendment candidate

**Reviewed amendment SHA-256:**
`ED67310838C6FA1B51DB2DEEAFBAC63BEAD937B2E2A9161FCB0FB241778D09AF`

All eight roles apply because the value will flow from scientific evidence to
future map, prose, accessible text, verification, repository, and comparison
boundaries.

## Findings

### CURRENT

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Treating surface flux as storage or transport is physically false. | P2 | Add the exact boundary-flux class only. **Resolved.** |
| 2 | Flux-to-temperature conversion depends on heat capacity and depth. | P2 | Keep converted tendencies separate with their own assumptions. **Resolved.** |
| 3 | Positive-downward sign and air–sea-boundary support are explicit. | P3 | Preserve both in D12 mapping. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | W/m² alone does not identify direction or support. | P2 | Require sign, interval, spatial support, and boundary support. **Resolved.** |
| 2 | An open-ended extension could destabilize the registry. | P2 | Authorize one exact serialized value with exact-match failure. **Resolved.** |
| 3 | The amendment does not alter historical bytes. | P3 | Confirm hashes at closeout. **Accepted.** |

### CHART

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | A future map might confuse surface W/m² with vertical-section MW/m². | P2 | Bind quantity identity and support, not units alone. **Resolved.** |
| 2 | The new class does not authorize visual scale or palette behavior. | P2 | Keep rendering in WP-OSW-003. **Resolved.** |
| 3 | Air–sea-boundary support gives later legends a truthful distinction. | P3 | Preserve it in the candidate. **Accepted.** |

### BEACON

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | “Heat flux” can be repeated as “ocean warming.” | P2 | State that temperature change needs a separate conversion. **Resolved.** |
| 2 | Numerical agreement could still be described as closure. | P2 | Retain native-closure and causation prohibitions. **Resolved.** |
| 3 | The name is plainer and more accurate than forcing it into storage. | P3 | Use `surface_heat_flux` consistently. **Accepted.** |

### HARBOR

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Later accessible text needs the sign and boundary, not a color cue. | P2 | Make both contract fields required. **Resolved.** |
| 2 | This code-only amendment cannot pass accessible-reader validation. | P2 | Keep reader and Validation claims blocked. **Resolved.** |
| 3 | A stable distinct class supports equivalent future text. | P3 | Test exact serialization. **Accepted.** |

### KEEL

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | The new value could alias through case or whitespace. | P2 | Reuse exact closed-enum parsing and negative tests. **Resolved.** |
| 2 | Existing quantity cases could drift when the enum changes. | P2 | Run focused and complete dual-runner gates. **Resolved.** |
| 3 | No new dependency is required. | P3 | Retain the 001-A tool decision. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Editing the committed entry would obscure the discovered gap. | P2 | Preserve it in this separately committed amendment. **Resolved.** |
| 2 | A vocabulary fix could be mistaken for broad implementation authority. | P2 | Retain every 001-B scope and external-effect prohibition. **Resolved.** |
| 3 | The amendment records why the extra value is necessary. | P3 | Link it in implementation evidence. **Accepted.** |

### ORBIT

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Surface heat flux in a terrestrial ocean is not automatically analogous to gas-giant flux. | P2 | Grant no planetary transfer or admission. **Resolved.** |
| 2 | Visible temperature and energy flux must remain distinct across planets. | P2 | Preserve the explicit quantity separation. **Resolved.** |
| 3 | No comparison family is touched. | P3 | Keep WP-OSW-008 blocked. **Accepted.** |

## Synthesis

```
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: D12 cannot be adapted honestly through any existing quantity
class; one exact surface-boundary heat-flux extension is necessary.

Cross-role consensus: keep flux, temperature conversion, storage, transport,
residual, and causation distinct, with no new display or release authority.
```

All P2 findings are repaired in the amendment. Implementation conditions are
exact enum serialization, required sign/support, positive/negative tests, full
gates, and later closeout confirmation.

## Amendments

1. Limited the change to one exact class and physical dimension.
2. Required boundary support, sign, and explicit conversion limits.
3. Preserved all adapter, admission, UI, Validation, planetary, and release
   gates.

Fixed-point decision: `pass_with_risk` for amendment 01 only. Commit these exact
bytes before 001-B code changes.
