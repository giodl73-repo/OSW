---
skill: roles-check
topic: ocean-geography-expansion-plan
date: 2026-08-29
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK, ORBIT]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Ocean-geography expansion plan — native-role review

Artifact: `plans/ocean-geography-expansion.md`
Research basis: `signals/discover/websearch/ocean-geography-ontology-websearch-2026-08-29.md`

## Artifact identification

- Type: implementation plan and information-architecture proposal
- Signals: water-mass classification, circulation, fronts, bathymetry,
  biogeochemistry, interactive filters, accessibility, provenance
- Selection: all eight OCEANLINES roles because the plan changes the atlas's
  primary conceptual vocabulary and machine-readable catalog

## Findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Separating WATERS, FLOWS, EDGES, FLOOR, LIFE, and EVENTS prevents fundamentally different physical objects from becoming generic blobs. | P3 | core model | Preserve the primary-lens distinction. |
| 2 | Temperature/property tags alone are insufficient to identify a water mass; source region, formation or transformation, depth, and identifying properties matter. | P2 | data model | Add a `basis` field stating how each feature is recognized and formed or maintained. |
| 3 | A representative marker can imply a localized center for basin-spanning or deep features. | P2 | scientific firewall | Call it an index point in the interface and state that it is neither centroid nor boundary. |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Deferring polygons until variable, depth, rule, period, source, and uncertainty are known is correct. | P3 | scientific firewall | Keep this release boundary. |
| 2 | Twenty-four records need source identity specific to the named feature, not a generic oceanography page. | P2 | first catalog | Register an authoritative source URL and source ID for every new record. |
| 3 | Depth, property, clock, and evidence facets need controlled values or the CSV will drift. | P2 | data and implementation | Define enumerations and test every emitted value. |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Quiet basin labels address the owner's central complaint that most water appears unnamed. | P3 | interface | Show basin labels in both conceptual emphasis variants. |
| 2 | Thirty-six simultaneous markers can obscure the map even if the default is filtered. | P2 | ALL view | Rename the view and provide collision offsets plus a text-directory route; never make it the default. |
| 3 | Category-specific shape and border are necessary because color alone cannot carry six classes. | P3 | implementation | Add a visible legend keyed to the marker grammar. |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “ALL OCEAN” contradicts the stated curated, non-exhaustive scope. | P2 | interface | Rename it `ALL FEATURES` and keep “curated first atlas” visible. |
| 2 | “Coldmass” can invite discovery while `water mass` remains the formal type. | P3 | core model | Explain the translation once, then use the scientific term. |
| 3 | The overlapping-lenses model gives readers a stronger takeaway than a larger bag of names. | P3 | purpose | Put the overlap statement beside the controls. |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Native buttons and selects are appropriate controls if labels and current state remain explicit. | P3 | interface | Use fieldsets, legends, and an `aria-live` result summary. |
| 2 | Filtering must remove unmatched markers from keyboard navigation, not merely fade them. | P2 | acceptance gates | Use `hidden`/disabled semantics as well as visual filtering. |
| 3 | A grouped text directory is the required equivalent to a crowded marker map. | P3 | directory | Keep every matching feature reachable there. |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Exact catalog cardinality and per-record boundary/source requirements are testable acceptance gates. | P3 | acceptance gates | Lock them in the offline suite. |
| 2 | Query-state and combined-filter behavior need tests beyond source-token checks. | P2 | implementation | Export or isolate a pure matcher and test representative combinations. |
| 3 | The generated CSV must remain an exact ordered projection of the application catalog. | P2 | exports | Regenerate it and validate the new fields and controlled vocabularies. |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The plan preserves previous experiments and avoids an unapproved Atlas version claim. | P3 | purpose | Describe this as an additive private-preview expansion. |
| 2 | The plan and its research evidence are versioned within OCEANLINES without private external references. | P3 | repository boundary | Keep researcher outreach outside the public repo. |
| 3 | Preview status should name the source commit and review only after implementation passes. | P3 | acceptance gates | Record the milestone in a follow-up review commit. |

### ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Deferring planetary transfer keeps Earth-side objects physically coherent first. | P3 | deliberately deferred | Preserve this separation. |
| 2 | Gyres, fronts, and water masses must not be relabeled as planetary belts by visual resemblance. | P3 | legacy studies | Keep OCEANBELTS as a separate comparison lens or guide. |
| 3 | The richer Earth taxonomy will eventually improve mechanistic comparison by distinguishing volume, flow, and boundary. | P3 | core model | Require a separate ORBIT review before any transfer. |

## Synthesis

Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 11  |  P3 notes: 13

Verdict: APPROVED-WITH-CONDITIONS

Top finding: the first catalog is scientifically defensible only if every
feature records its identifying basis and the interface describes markers as
index points rather than boundaries or centroids.

Cross-role consensus: CURRENT, SOUNDER, CHART, BEACON, HARBOR, and KEEL agree
that a larger catalog increases interpretive and interaction risk. Controlled
facets, explicit non-exhaustive language, hidden unmatched controls, a text
directory, authoritative sources, and testable query state are required.

## Amend

1. Rename `ALL OCEAN` to `ALL FEATURES`; add `basis` and controlled facet
   enumerations; require authoritative source IDs for every new record.
2. State beside the map that markers are representative index points—not
   boundaries or centroids—and keep unmatched controls out of keyboard order.
3. Add a marker legend, collision offsets, grouped text directory, live result
   summary, pure filter matcher, query-state coverage, and exact CSV parity tests.

