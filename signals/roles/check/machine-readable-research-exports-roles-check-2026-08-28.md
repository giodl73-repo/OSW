---
skill: roles-check
topic: machine-readable-research-exports
date: 2026-08-28
source_commit: 7d673df
roles_used: [CURRENT, SOUNDER, BEACON, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED
---

# Roles check: machine-readable research exports

## Artifact identification

- **Type:** deterministic CSV exports, generator, download routes, documentation, and regression tests.
- **Reviewed:** `research/zone-catalog.csv`, `research/claims-ledger.csv`, `analysis/export_research_tables.js`, Research Note downloads, methods, README, and review guide.
- **Scope:** researcher reuse of the private Atlas 08 contract; the exports do not elevate conceptual zones into measured features.

## Role selection

CURRENT checks physical wording; SOUNDER checks schema and provenance; BEACON checks whether tabular reuse preserves limitations; KEEL checks deterministic generation and drift detection; LOGBOOK checks status and handoff truth. CHART, HARBOR, and ORBIT are excluded because this delta adds data downloads rather than a new visual, interaction, or planetary comparison.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every zone row carries depth, persistence, physical role, summary, and an inferential boundary rather than only a name and footprint. | P3 | Zone catalog | Preserve these columns as required fields. |
| 2 | The claims table retains the separation among observed-product geometry, observed surface fields, explanatory synthesis, and model counterfactual. | P3 | Claims ledger | Do not collapse these classes into a single confidence score. |
| 3 | The Drake row rejects feasibility, uniqueness, modern ice-loss forecasting, and gateway-only causation in the downloadable artifact itself. | P3 | Claim C4 | Keep this boundary attached to any downstream copy. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Evidence class and source IDs are separate columns, allowing clean filtering without parsing display prose. | P3 | Zone schema | Preserve the separation in later JSON or database forms. |
| 2 | Every row includes a primary URL or source-register route; claims carry DOI mappings and explicit non-claims. | P3 | Both exports | Add stable claim/zone version identifiers if semantic revisions begin. |
| 3 | The zone CSV is generated from the interactive catalog, while the four-claim CSV is documented as a deliberately reviewed contract. | P3 | Generator; methods | Keep that source-of-truth distinction explicit. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Column names use plain scientific language, including `inferential_boundary` and `does_not_establish`. | P3 | CSV headers | Retain unabbreviated names for researcher handoff. |
| 2 | The C3 wording calls the taxonomy “candidate map roles,” avoiding the stronger claim that the classification is already validated. | P3 | Claim C3 | Use the same phrasing in derivative summaries. |
| 3 | Download links explain the contents and row counts rather than offering unexplained data files. | P3 | Research Note | Keep the descriptions beside the download actions. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The standard-library Node generator runs offline and reproduces byte-identical output on repeated runs. | P3 | Export generator | Keep network access out of this build step. |
| 2 | Tests compare all twelve exported ID/name pairs and ordinal numbers with the live Atlas catalog. | P3 | Export regression test | Extend the comparison if additional canonical fields move out of the catalog. |
| 3 | Tests require nonempty boundaries/sources, separated evidence/source fields, four ordered claims, and the Drake non-claim. | P3 | Export regression test | Add a CSV dialect check if consumers report interoperability problems. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, methods, Research Note, and optional review guide all expose the same two export files. | P3 | Navigation and documentation | Update these routes together if filenames change. |
| 2 | The generator command and source-of-truth distinction are documented for a fresh maintainer. | P3 | Atlas methods | Include the command in CI if these exports become release assets. |
| 3 | The exports contain no recipient identity, private-project reference, machine path, secret, or public-release claim. | P3 | Public-boundary scan | Preserve the neutral reusable contract. |

## Synthesis

```text
Roles reviewed: 5
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 15

Verdict: APPROVED

Top finding: The downloadable rows preserve the same scientific boundaries as the interface instead of exporting decontextualized names and coordinates.
Cross-role consensus: The exports are suitable for private researcher reuse because their provenance, evidence class, and non-claims survive the transition from interface to spreadsheet.
```

## Amendments applied

1. Separated evidence class from source IDs so machine filtering does not require parsing a display string.
2. Added a deterministic offline generator and regression tests tying all twelve export rows to the live Atlas catalog.
3. Added explicit, downloadable non-claims and DOI mappings for all four headline statements.
