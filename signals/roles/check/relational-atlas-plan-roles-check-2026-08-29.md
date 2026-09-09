---
skill: roles-check
topic: relational-atlas-plan
date: 2026-08-29
roles_used: 8
p1_count: 0
verdict: APPROVED
source_commit: 9276891
artifact: plans/relational-atlas-implementation.md
---

# Native-role review — Relational Atlas implementation plan

## PHASE 1 — ARTIFACT IDENTIFICATION

Artifact type: implementation specification and staged interaction/cartography
design.

Domain signals: physical oceanography, schematic/observed evidence boundaries,
SVG geometry, cartography and projections, climate-data provenance,
accessibility, deterministic browser behavior, repository/release state, and
the possible future reuse of Earth-side geography in planetary comparison.

## PHASE 2 — ROLE SELECTION

| Role | Why selected |
|---|---|
| CURRENT | Reviews whether crossings, fronts, water masses, and gates imply unsupported physical membership. |
| SOUNDER | Reviews evidence status and the future observed-geometry admission contract. |
| CHART | Reviews intersection semantics, coastline clearance, labels, seam treatment, and map hierarchy. |
| BEACON | Reviews what readers will repeat about “crossings” and evidence status. |
| HARBOR | Reviews keyboard relations, live summaries, labels, dimming, zoom, and non-color equivalence. |
| KEEL | Reviews deterministic matrix construction, validation, fixtures, and offline gates. |
| LOGBOOK | Reviews source commit, milestone status, registry, licensing, and private/public boundaries. |
| ORBIT | Reviews whether the new Earth-side relationship vocabulary is inappropriately exported to gas giants. |

## PHASE 3 — REVIEW

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C-1 | An anchor-only fallback can create a positive crossing with no rendered overlap and weakens the otherwise strong truth contract. | P2 | 4.A1 | Remove the anchor fallback from boolean membership; use anchors only for diagnostics or label placement. |
| C-2 | Evidence status could be misread as validation of the drawn outline rather than evidence for the named phenomenon. | P2 | 8 | State beside every status that it qualifies the record, not the schematic footprint. |
| C-3 | The specification correctly separates rendered overlap from transport, membership, and observed boundaries. | P3 | 2 | Preserve this language in the interface and export. |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S-1 | The matrix export lacks checksums identifying the exact province and feature SVG inputs. | P2 | 4.A2 | Include both artifact SHA-256 values, catalog version, and method version in export metadata. |
| S-2 | The admission contract names license but not an explicit compatibility decision or decision authority. | P2 | 10 | Add license identifier, compatibility status, reviewer, and decision date fields. |
| S-3 | The plan correctly keeps observed geometry separate from the present schematic registry. | P3 | 10 | Retain the no-promotion validator rule. |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| CH-1 | A sampled boolean matrix must not be described as exact geometry intersection; narrow or tangent contacts can remain resolution-dependent. | P2 | 4.A1 | Name it a sampled rendered-overlap index, export hit method/tolerance, and mark unresolved near-contact as indeterminate rather than false. |
| CH-2 | Label displacement can push an ocean label over land or across the map seam. | P2 | 5.B2 | Constrain resolved label anchors to ocean and their original seam hemisphere; use leader lines. |
| CH-3 | Coast clearance can visually erase legitimate narrow gates and marginal-sea shapes. | P2 | 6.C1 | Maintain an explicit exemption list and test Drake, Indonesian passages, Gibraltar, and Bab el-Mandeb. |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B-1 | “True province–feature crossings” remains likely shorthand even though the body qualifies it. | P2 | 1, 4 | Use “schematic rendered overlap” in controls, summaries, exports, and release notes. |
| B-2 | Four evidence badges may falsely suggest an ordinal confidence ladder. | P2 | 8 | Explain that classes describe evidence type, not a quality score. |
| B-3 | Ten additions need a short first-use route so the map does not become self-documenting only to its authors. | P3 | 9 | Add a compact “How to explore” disclosure with place-first, object-first, and shape-only routes. |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| H-1 | Dimming unrelated objects can make keyboard focus or related context imperceptible. | P2 | 5.B1 | Never dim the focused item; retain minimum contrast and a non-color related/not-related stroke distinction. |
| H-2 | Relation summaries need an operable route to each result, not only announced counts. | P2 | 4.A2 | Render related feature/province lists as buttons with logical focus order and an accessible heading. |
| H-3 | Feature zoom needs predictable focus restoration. | P2 | 7 | Move focus to the zoom summary on entry and return it to the invoking control on reset without stealing focus during passive changes. |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K-1 | Browser SVG APIs are not covered by the existing Python structural suite. | P2 | 4.A3, 12 | Add a deterministic browser smoke harness or checked-in relation fixture generated from the same versioned algorithm. |
| K-2 | The dynamic CSV needs a schema and stable serialization rules. | P2 | 4.A2 | Define column order, boolean/indeterminate tokens, line endings, sort order, and metadata rows. |
| K-3 | Five reversible commits and offline defaults are appropriate. | P3 | 13 | Keep every stage independently passing. |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L-1 | A plan review tied to `9276891` will not by itself review later implementation commits. | P2 | 12, 13 | Run an implementation role review after the final code commit and record both hashes. |
| L-2 | New registries and exports need explicit ownership and source-register entries. | P2 | 10, 11 | Add them to the method/source register and keep all paths repository-relative. |
| L-3 | Deferring history and release promotion until owner visual approval is correct. | P3 | 9, 13 | Preserve the private-preview boundary and do not push. |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| O-1 | Earth province overlap must not be reused as a direct gas-giant geography mapping. | P2 | 3, 10 | State that the relational engine is Earth-specific unless a separate mechanism-level correspondence contract is reviewed. |
| O-2 | Evidence badges for Earth observations should not appear to qualify gas-giant analogies. | P3 | 8 | Keep planetary analogy status outside the feature evidence badge. |
| O-3 | The plan improves the Earth-side objects that any later analogy would need. | P3 | Overall | Defer planetary integration until the Earth implementation is accepted. |

## PHASE 4 — SYNTHESIS

```
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 17  |  P3 notes: 7

Verdict: APPROVED-WITH-CONDITIONS

Top finding: CH-1 — sampled display-geometry overlap must expose tolerance and
an indeterminate state rather than presenting a resolution-dependent boolean as
exact intersection.

Cross-role consensus: CURRENT, CHART, BEACON, and SOUNDER agree that relational
power must not promote schematic geometry into observational truth. HARBOR and
KEEL agree that the same relationship must be available as an operable,
deterministically testable text structure rather than only visual emphasis.
```

## PHASE 5 — AMEND

1. Amend Stage A to remove anchor-based positives; use a tri-state
   `overlap / near-contact / none` method with exported tolerance, hit method,
   SVG checksums, stable schema, and a checked-in deterministic fixture.
2. Amend focus, labels, and zoom to require operable related-object lists,
   minimum focus contrast, ocean/seam-constrained labels, and explicit focus
   restoration.
3. Amend evidence/admission/release sections to distinguish record evidence
   from outline evidence, add license-decision authority fields and Earth-only
   scope, register all new artifacts, and require a post-implementation native
   role review before any milestone or promotion.

## Post-amendment recheck

All 17 P2 conditions are resolved in
`plans/relational-atlas-implementation.md`:

| Findings | Resolution |
|---|---|
| C-1, CH-1, B-1 | Removed anchor positives; adopted named tri-state sampled rendered overlap with near-contact and tolerances. |
| C-2, B-2, O-2 | Evidence badges now qualify the named Earth phenomenon, not the footprint, confidence, or planetary analogy. |
| S-1, K-2 | Export contract now fixes schema, ordering, line endings, method metadata, and both SVG checksums. |
| S-2 | Admission records now require license identifier, compatibility decision, authority, and date. |
| CH-2 | Collision-resolved labels must remain over ocean and on their original side of the seam. |
| CH-3 | Coast-clearance exemptions explicitly cover Drake, Indonesia, Gibraltar, and Bab el-Mandeb. |
| B-3 | A compact three-route first-use guide is required. |
| H-1, H-2, H-3 | Focus contrast, operable relation lists, zoom focus entry, and reset restoration are required. |
| K-1 | A checked-in algorithm fixture and optional local browser smoke gate are required. |
| L-1, L-2 | Final code receives a new role review; new artifacts receive source-register entries. |
| O-1 | The relationship engine is explicitly Earth-only absent a new reviewed correspondence contract. |

Post-amendment verdict: **APPROVED** for implementation on the private branch.
This approves the specification, not the resulting code or an Atlas release.
