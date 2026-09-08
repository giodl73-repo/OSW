---
skill: roles-check
topic: architecture
date: 2026-09-06
roles_used: 8
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — OSW VTRACE Architecture

**Artifact type:** logical architecture and package-boundary allocation for an
existing static ocean-atlas and offline scientific evidence system

**Source commit:** `6285bdd3b74b8924f006e8f8e4582d2673564c95` plus reviewed working-tree changes

**Fixed-point artifact SHA-256:** `ARCHITECTURE.md`
`64d9dcca1825f8d153e01b4fdc6b254ef89597d64b28ba27a6fbde667c628569`;
`PACKAGE_BOUNDARIES.md`
`ea8d7bfb564580be298a2d2f675880efbf3c5afea599b238d2eede469ea65169`

**Reviewed artifacts:** `docs/vtrace/ARCHITECTURE.md`,
`docs/vtrace/PACKAGE_BOUNDARIES.md`, the 45-item Specification Baseline,
current `atlas/`, `analysis/`, `research/`, `figures/`, publication/governance
surfaces, and the PITFALL register

## Role selection

All eight native roles were selected. Architecture allocates authority over
physical claims, source custody, maps, public explanation, equivalent reader
state, verification, release truth, and planetary comparison; excluding any
one would leave a reverse dependency or unowned veto.

## Review findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A central admission component could accidentally overrule physical invalidity when every data/format check passes. | P2 | ADR-OSW-010; ARCH-OSW-006 | Make admission federated and preserve CURRENT's physical-claim veto. **Resolved.** |
| 2 | Client-side derivation would allow presentation choices to manufacture heat, transport, convergence, or province aggregates. | P2 | ADR-OSW-002; authority boundaries | Confine scientific transformations to the offline pipeline and make the browser consume admitted derivatives only. **Resolved.** |
| 3 | Exact zoning algorithms and thresholds remain outside Architecture while provisional borders stay constrained. | P3 | Open risks and deferred decisions | Preserve this separation through Design/Validation. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Source custody, scientific result, display derivative, and public claim must remain separate identities across the data flow. | P2 | ADR-OSW-002, 005; data flows | Allocate distinct acquisition, transformation, contract, display, and presentation boundaries with lineage between them. **Resolved.** |
| 2 | Browser access to mutable scientific providers would bypass checksums, masks, rights, and degraded-operation controls. | P2 | Dependency direction | Make acquisition the only provider-facing boundary and prohibit runtime/default-gate provider dependencies. **Resolved.** |
| 3 | Historical receipt representations need an Interfaces-stage adapter/version decision rather than an Architecture rewrite. | P3 | ARCH-RISK-OSW-002; PKG-UNK-OSW-001 | Retain source truth and defer representation. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A renderer that infers masks, evidence classes, or boundary authority could fabricate geographic meaning even from valid numeric data. | P2 | ADR-OSW-004; authority boundaries | Require typed support/classes upstream and prohibit renderer repair or inference. **Resolved.** |
| 2 | State, scene copy, and rendering concentrated in one client file risk divergent projection and text outputs. | P2 | ADR-OSW-003; ARCH-RISK-OSW-001 | Separate logical state authority from cartographic and scene projections without mandating a framework rewrite. **Resolved.** |
| 3 | Experimental projections remain candidates, not automatically admitted map families. | P3 | ARCH-OSW-004–006 | Preserve map admission ahead of display-bundle membership. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Replacing the README corridor could sever expert audit routes if public navigation and the research corpus were collapsed. | P2 | ADR-OSW-008; ARCH-OSW-001, 011 | Keep three primary routes and a complete secondary corpus as separate responsibilities. **Resolved.** |
| 2 | Scene presentation must simplify inside the admitted claim ceiling, not create a second scientific interpretation layer. | P2 | ARCH-OSW-003; authority boundaries | Bind finding, strongest limitation, evidence identity, and receipt at presentation time. **Resolved.** |
| 3 | Route success must be validated by reader outcomes rather than the existence of three links. | P3 | ARCH-RISK-OSW-007 | Carry to Validation. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Multiple state owners would let URL, visual selection, focus, announcement, and text alternatives disagree. | P2 | ADR-OSW-003; ARCH-OSW-002 | Establish one canonical accepted-state responsibility with all outputs as projections. **Resolved.** |
| 2 | Making rendering a dependency of state would turn canonical authority into a client monolith and complicate pure transition testing. | P2 | Dependency direction; PKG-OSW-002 | Let scenes/renderers consume state; state may read only accepted compatibility metadata. **Resolved.** |
| 3 | Exact viewport, zoom, contrast, target-size, and assistive-technology cases remain measured Interfaces/Validation inputs. | P3 | Deferred decisions | Do not invent thresholds in Architecture. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Read-only verification” could prohibit legitimate temporary regeneration or, conversely, hide tests that rewrite accepted artifacts. | P2 | Dependency direction; PKG-OSW-009 | Permit ephemeral outputs while forbidding repair or overwrite of accepted candidates. **Resolved.** |
| 2 | Optional scientific dependencies and provider outages must remain capability-local rather than reach the thin reader or default gate. | P2 | ADR-OSW-001, 002; FAIL-OSW-001, 006 | Contain them in acquisition/transformation and verify bounded failure offline. **Resolved.** |
| 3 | Physical splitting of `atlas/app.js` is a Design decision; Architecture correctly records coupling risk without prescribing modules. | P3 | ARCH-RISK-OSW-001, 005 | Preserve pure seams and measure the design benefit later. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Scientific admission and public release were at risk of becoming one approval state. | P2 | ADR-OSW-006; release flow | Keep domain admission, lifecycle classification, owner decision, deployment proof, and current/citation update as separate ordered authorities. **Resolved.** |
| 2 | Choosing GitHub Pages rollback mechanics here would conceal the currently unknown deployment/atomicity contract. | P2 | ARCH-OSW-010; ARCH-RISK-OSW-004 | Allocate the outcome but defer mechanism to Implementation Plan. **Resolved.** |
| 3 | VTRACE and `.roles` remain governance evidence, not browser runtime data or ocean ontology. | P3 | ADR-OSW-007; PKG-OSW-011 | Keep the negative dependency test. **Accepted.** |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A separate planetary truth system could duplicate and drift from Earth quantities, receipts, and claim ceilings. | P2 | ADR-OSW-009; ARCH-RISK-OSW-008 | Route comparisons through shared admitted identities and add only comparison-specific review. **Resolved.** |
| 2 | ORBIT review cannot rescue an unidentified or physically invalid Earth-side object. | P2 | ADR-OSW-010 | Preserve CURRENT and SOUNDER vetoes ahead of comparison acceptance. **Resolved.** |
| 3 | Comparison representation and negative fixtures remain Interfaces/Verification work, not architecture components. | P3 | Deferred decisions | Preserve stage boundary. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: authority must flow one way from receipted evidence to public
presentation, while admission remains a composition of domain vetoes rather
than a single super-gate.

Cross-role consensus: the static reader should stay thin, deterministic, and
semantically unified; science, verification, governance, and release must not
leak backward into browser state.
```

All P2 findings are resolved in the reviewed Architecture pair. Conditions
remaining for later stages are explicit rather than architectural omissions:
contract representations and URL policy belong to Interfaces; component
granularity, algorithms, and rigor profiles to Design/Code Rigor; payload
budgets and user thresholds to Validation; deployment mechanics and work order
to Implementation Plan.

## Amendments

1. Replaced a central admission authority with a federated model that preserves
   each native domain veto while using a shared registry only for identities
   and disposition composition.
2. Corrected reader dependency direction so presentation and rendering consume
   canonical accepted state, while state remains testable without importing
   the presentation/rendering layers.
3. Separated source custody, scientific transformation, display derivatives,
   admission, verification, lifecycle, and hosted release; clarified that
   verification may create ephemeral outputs but never repair accepted ones.

Fixed-point decision: `pass_with_risk` for Architecture only. All 45 controlled
specification items allocate to eleven logical boundaries; reverse dependencies
and forbidden responsibilities are explicit. Interfaces may open next but is
not opened by this review.

No implementation, framework migration, schema, deployment provider, public
release, scientific endorsement, or NASA affiliation is authorized or implied.
