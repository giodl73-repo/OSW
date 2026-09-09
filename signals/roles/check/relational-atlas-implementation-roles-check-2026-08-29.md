---
skill: roles-check
topic: relational-atlas-implementation
date: 2026-08-29
roles_used: 8
p1_count: 0
p2_count: 0
verdict: APPROVED
source_commit: 39f1269
plan_review_commit: ae48060
kernel_commit: 0a0b51a
---

# Native-role review — Relational Atlas implementation

## PHASE 1 — ARTIFACT IDENTIFICATION

Artifact type: implemented interactive cartography, SVG generator, browser
geometry algorithm, evidence/provenance contract, documentation, and tests.

Reviewed implementation: commits `0a0b51a` through `39f1269` on the private
`atlas-08-private-preview` branch. This is an implementation approval, not a
public Atlas promotion or owner visual acceptance.

Verification evidence:

- `node --check atlas/app.js` passed;
- `python analysis/validate_feature_geometry.py` accepted all 36 draft rows;
- 77 offline unit tests passed;
- Edge completed all six individual lenses plus All with the relationship
  fixture marked `data-smoke="passed"`;
- the fixture verified Gulf Stream/GFST, Kuroshio/KURO, Drake/FKLD, and ACC
  overlaps with ANTA and SSTC;
- 1,600-pixel Edge captures reviewed Quiet states and Fluid shapes.

## PHASE 2 — ROLE SELECTION

All eight native roles apply because the implementation combines ocean
mechanism, evidence status, cartographic hierarchy, public explanation,
accessible interaction, browser computation, repository state, and an
explicit Earth/planetary boundary.

## PHASE 3 — REVIEW

### CURRENT — physical oceanography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| C-1 | Relations are computed only from rendered geometry; catalog anchors position labels and cannot manufacture membership. | P3 | `sampledPairHit`, `featurePathSamples`, centroid-negative test | Preserve this separation in later geometry editions. |
| C-2 | Interface and CSV consistently call the result sampled schematic rendered overlap and reject transport, observed membership, and fixed-boundary interpretations. | P3 | relation panel, export, Atlas README | Keep the caveat adjacent to every future relational statistic. |
| C-3 | Coast clearance is declared as visual SVG-unit treatment, with narrow gates exempted instead of being erased. | P3 | dual SVG masks and four-item exemption registry | Require CURRENT review before changing the exemption list. |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| S-1 | The 2,016-row export identifies method, tolerances, editions, evidence class, hit method, and both exact SVG checksums. | P3 | `exportRelationMatrix` | Treat any column or ordering change as an export-version change. |
| S-2 | The future-geometry register requires provider, product, variable, version, license decision, authority/date, CRS, time/depth/baseline, transforms, and checksums. | P3 | schema and 36-row register | Keep new rows in draft until source and license review are complete. |
| S-3 | The offline validator checks catalog coverage, actual output-file checksum, license compatibility, enums, finite tolerances, and illustrative-geometry promotion. | P3 | `validate_feature_geometry.py` and rejection test | Add coordinate parsing when the first coordinate-bearing candidate arrives. |

### CHART — ocean cartography

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| CH-1 | Quiet states now leads, Ocean states preserves province reading, and Fluid shapes removes state borders/codes while retaining ghost coastlines and dark land. | P3 | three-state control and Edge captures | Preserve the same geometry beneath all three presentations. |
| CH-2 | Labels use names, deterministic bounded candidates, ocean-tested anchors, seam-side constraints, and leaders; selected labels survive the All lens. | P3 | `renderFeatureLabels` | Curate explicit short names if later catalogs make automatic shortening ambiguous. |
| CH-3 | Seven antimeridian-spanning objects carry paired continuation marks and shared selection identity. | P3 | generated `data-seam` groups and seven seam tests | Keep seam marks subordinate and explain the cut as projection-only. |

### BEACON — public-science editing

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| B-1 | The first-use disclosure gives place-first, object-first, and shape-first routes without claiming the map partitions all ocean physics. | P3 | “How to explore this fluid map” | Keep this compact route above future controls. |
| B-2 | Evidence badges explicitly describe evidence type for the named phenomenon—not footprint validation or a confidence score. | P3 | badge-adjacent note and README | Repeat this distinction anywhere badges are summarized. |
| B-3 | Stale marker/point language was removed from current catalog caveats and the source register. | P3 | `zone-catalog.csv`, `app.js`, source register | Continue using shape/extent language while geometry remains schematic. |

### HARBOR — accessibility

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| H-1 | Reciprocal results are operable buttons under headings and a polite text summary, not color-only highlights. | P3 | relation panel and keyboard handlers | Retain the button lists as the canonical equivalent route. |
| H-2 | Evidence states use text plus solid/double/dashed borders; related and near-contact states use redundant strokes. | P3 | CSS badge and relation rules | Recheck contrast after any palette revision. |
| H-3 | Feature zoom moves focus to its frame summary, Escape/reset returns focus, reduced motion is honored, and map labels hide on narrow screens in favor of the text directory. | P3 | focus handlers, media queries | Include focus restoration in every future zoom regression pass. |

### KEEL — reproducibility engineering

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| K-1 | Geometry sampling caches path and interior points and yields between province batches, keeping the UI responsive while building all 2,016 records. | P3 | async matrix builder and Edge completion | Add timing telemetry only if performance regresses; do not weaken tolerance silently. |
| K-2 | A checked-in fixture is evaluated by the real browser algorithm and exposes pass/fail state in the DOM. | P3 | `relation-smoke-fixture.js`, `data-smoke="passed"` | Regenerate and review the fixture whenever either input SVG changes materially. |
| K-3 | Structural, generator, admission, and browser-facing contracts are covered by 77 offline tests plus the optional local Edge sweep. | P3 | test suite and recorded sweep | Keep the default suite dependency-light and browser refresh explicit. |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| L-1 | The implementation has a traceable plan review, kernel commit, final source commit, and this separate post-implementation review. | P3 | front matter and git history | Cite this review if the owner later promotes the Atlas. |
| L-2 | New register, schema, validator, fixture, and methods are documented and linked from the source register. | P3 | repository-relative links | Keep ownership and license decisions inside the repository. |
| L-3 | Project history was deliberately not promoted and no remote was pushed; owner visual acceptance remains open. | P3 | clean private branch state | Do not convert this implementation approval into release approval automatically. |

### ORBIT — planetary comparison

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| O-1 | The README says the relationship engine and evidence badges describe Earth features only. | P3 | Earth-specific paragraph | Preserve this boundary in any RESONANCE cross-link. |
| O-2 | No Earth province relationship or evidence badge is exported to Jupiter or Saturn. | P3 | implementation scope | Require a separate mechanism-level correspondence contract before reuse. |
| O-3 | The implementation improves Earth-side object definitions without claiming visual similarity is causal equivalence. | P3 | truth contract and non-goals | Let CURRENT govern any later planetary mapping. |

## PHASE 4 — SYNTHESIS

```
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 0  |  P3 findings: 24

Verdict: APPROVED
```

Cross-role consensus: the Atlas has become meaningfully relational without
promoting its hand-drawn features into observed boundaries. The strongest
implementation choice is the same one requested by the plan review: geometry
creates relationships, while anchors only help readers find labels. The
strongest release constraint is unchanged: this private implementation still
needs owner visual acceptance before history, Atlas numbering, or publication
changes.

## PHASE 5 — AMEND

No unresolved P1 or P2 findings. During implementation review, three issues
were corrected before this artifact was recorded:

1. matrix construction was cached and made cooperative after Edge exposed a
   long main-thread build;
2. narrow-screen labels now yield to the complete text directory and
   shape-first hiding is enforced inside the inline SVG;
3. the admission validator now compares the registered output checksum with
   the actual geometry file, and the README states the Earth-only boundary.
