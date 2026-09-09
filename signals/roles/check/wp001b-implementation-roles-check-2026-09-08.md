---
skill: roles-check
topic: wp001b-implementation
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — WP-OSW-001B implementation

**Artifact type:** Python historical-evidence adapter, strict immutable JSON
model, additive quantity identity, invented fixtures, and focused tests

**Source commit:** `762ed5c5f2ce699a1993ef16bf1d9bde8aa5aa72`
plus the reviewed 001-B candidate

**Reviewed artifact identities:**

| Artifact | SHA-256 |
|---|---|
| `analysis/osw_contracts.py` | `6EFF5CA12863369E50A8DB5A4D149C477D184F23DBD450BFC6047759659664CA` |
| `analysis/osw_adapters.py` | `0CA31ABDC346BB8E9E9AE589526ABAAC7FDBBBA45222BD294253065D649EF209` |
| `analysis/test_osw_adapters.py` | `A05AB12E40354860C797B7073243B570A42304603AEC6C6AE64E1AD12D3FD270` |
| `strict-valid.json` | `6DD0A6A0C994327B0C8A31F16ACEC40889E28546F57D16DE82D11851216EF607` |
| `invalid-duplicate.json` | `5D9CF41F8CCCACF473CE552466F315D7F1F70624BEFA382428F45F2715A8AAAB` |
| `invalid-nonfinite.json` | `2BC91A179478B20DE6EC239AE8B6FCB2FE2695C2BF4DBA15B34E0249755F6F47` |
| `family-bindings.json` | `259523C539FC7535719A6CBEF14A10C523E1F1FA83BE7C853F763F89779B5971` |

## Role selection

All eight native roles are selected for the same cross-boundary reasons as the
entry: quantity physics, custody, future map/access semantics, public claim
ceilings, deterministic proof, repository truth, and planetary non-transfer.

## Findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first candidate used area integration for a latitude-weighted grid-center mean. | P2 | D12 quantity | Use `point/sample`; do not imply exact native-area integration. **Resolved.** |
| 2 | D14's cross-system residual lacks one truthful evidence origin. | P2 | D14 unavailable fields | Preserve it in source but mark its quantity identity unavailable; prohibit closure/causation. **Resolved.** |
| 3 | Flux, storage, and horizontal advection now have distinct classes and claim ceilings. | P3 | Family definitions | Preserve this separation through 001-C. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Parsed-tree preservation alone could lose raw-byte custody. | P2 | Candidate | Retain immutable raw bytes, verify SHA-256, and independently bind the frozen tree. **Resolved.** |
| 2 | Provider/product/license/query/support fields absent from D12–D14 could appear complete. | P2 | Unavailable fields | Enumerate missing provenance, rights, acquisition, uncertainty, grid, and support fields. **Resolved.** |
| 3 | Exact source schemas, paths, hashes, references, dates, and semantic anchors are checked. | P3 | Registry/validators | Reconfirm against the implementation commit at closeout. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Aggregate arrays cannot establish cell-level ocean/land/data/ice support. | P2 | Support mapping | Mark all absent axes and grid conventions unavailable; never infer them from null/zero/map arrays. **Resolved.** |
| 2 | Preserving map-shaped arrays might look like map admission. | P2 | Candidate authority | Keep `admitted=False`; perform no rendering and leave IF-OSW-004/WP-OSW-003 pending. **Resolved.** |
| 3 | Explicit ocean + valid + sea-ice survives as an orthogonal invented fixture. | P3 | Support test | Retain this as vocabulary proof, not D12–D14 observed ice evidence. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Lossless adapter” could be repeated as “complete receipt.” | P2 | Module/candidate boundary | Name it a candidate and expose every unavailable modern field. **Resolved.** |
| 2 | Surface heat flux could be repeated as temperature change or closure. | P2 | D12 ceiling | Keep depth conversion, native closure, and causation explicitly unsupported. **Resolved.** |
| 3 | Exact historical boundary prose travels unchanged with each candidate. | P3 | `claim_boundary` | Continue binding future scene prose beneath it. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Missing support represented only by absence would be lost in later text. | P2 | `UnavailableField` | Preserve stable field path, reason, and claim restriction in deterministic order. **Resolved.** |
| 2 | Adapter tests cannot establish accessible map or reader behavior. | P2 | Evidence status | Keep UI, text-equivalence, announcements, and Validation blocked. **Resolved.** |
| 3 | Distinct exact quantity/support identities give later visual and text renderers one source. | P3 | Candidate | Preserve them in the view-model package. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Object hooks initially validated nested arrays before those arrays were frozen. | P2 | Strict parser | Detect duplicate names first, then recursively freeze the complete decoded tree. **Resolved and retested.** |
| 2 | Direct construction, huge input, recursion, or registry collision could bypass normal dispatch. | P2 | Defensive contracts | Revalidate bytes/tree/binding, cap source size, catch recursion/value errors, and enforce unique registries. **Resolved.** |
| 3 | Focused and full gates pass with no external package or default-network dependency. | P3 | Evidence | Rerun against the committed implementation before closeout. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A generic adapter could widen silently to the repository's many JSON families. | P2 | Registry | Freeze exactly three path/schema/detection identities and test the complete ordered set. **Resolved.** |
| 2 | Adapter execution could follow source references or write normalized sidecars. | P2 | Effects/tests | Accept caller bytes only; deny filesystem/network calls and keep research files unchanged. **Resolved.** |
| 3 | The implementation touches only declared code, tests, and invented fixtures. | P3 | Scope | Confirm the final tree manifest and stop before closeout. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A generic surface-flux identity could appear to validate gas-giant comparisons. | P2 | Quantity extension | Limit the result to the terrestrial D12 mapping; grant no comparison admission. **Resolved.** |
| 2 | Temperature, flux, storage, and transport remain different across planetary regimes. | P2 | Claim ceilings | Preserve non-transfer until WP-OSW-008 supplies mechanism-level evidence. **Resolved.** |
| 3 | No planetary family, value, or product surface changed. | P3 | Scope | Keep ORBIT as a veto lane at closeout. **Accepted.** |

## Synthesis

```
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: a preserved historical record remains an unadmitted evidence
candidate when modern provenance, support, uncertainty, or origin is absent.

Cross-role consensus: bind raw bytes and frozen meaning together, keep the
three quantities physically distinct, infer no cell support, and prohibit
recursive I/O, source mutation, closure, causation, display, or release claims.
```

All 16 P2 findings are repaired in the exact reviewed candidate. Remaining
conditions are commit-bound evidence: commit these bytes as one rollback unit,
rerun focused/full gates and source/tree manifests on that commit, record the
mapping and limitations, and stop for separate closeout.

## Evidence inspected

- Focused suite: 35 tests and 50 subtests pass across the adapter and 001-A
  contracts.
- Full pytest: 493 tests and 60 subtests pass.
- Independent unittest discovery: 362 tests pass.
- Python compile, JavaScript syntax, and diff hygiene pass.
- D12/D13/D14 SHA-256 identities remain exactly those frozen at entry.
- All new imports are Python standard library or local OSW contract modules.
- New functions top out at 54 physical lines; changed Python and fixture files
  have zero lines over 120 characters. Markdown review-table rows are excluded.

## Amendments

1. Added the separately reviewed `surface_heat_flux` identity and changed D12
   aggregation identity from `area` to `point/sample`.
2. Added raw-byte retention/hash revalidation, strict recursive freezing,
   source-size/error bounds, registry uniqueness, and direct-constructor checks.
3. Expanded explicit unavailable provenance/support fields and retained D14's
   cross-system residual without manufacturing a unified origin or admission.

Fixed-point decision: `pass_with_risk` for the exact 001-B implementation
candidate. It may be committed as one rollback unit and then must stop for
commit-bound closeout. No 001-C, push, merge, deployment, Validation, release,
external contact, or cross-repository change is authorized.
