---
skill: roles-check
topic: ocean-object-field-guides
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Native-role review — Ocean Object Field Guides

## Artifact identification

- **Artifact type:** public-science guide collection and repository navigation
- **Artifacts:** `guides/README.md`, seven numbered guide chapters,
  `analysis/test_guides.py`, and their README/history/source-register routes
- **Domain signals:** physical oceanography, climate data, cartography,
  accessibility, reproducibility, public communication, repository state, and
  Earth–gas-giant comparison
- **Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b`
- **Snapshot status:** review covers the named uncommitted working-tree files on
  2026-09-05; it is not a release or publication verdict
- **Validation:** `python -m pytest analysis -q` — 387 passed, 10 subtests passed

## Role selection

All eight OSW roles apply. CURRENT governs the object definitions and budgets;
SOUNDER the evidence and quantitative examples; CHART the schematic visual
grammar; BEACON the teaching path; HARBOR nonvisual access; KEEL guide
contracts; LOGBOOK repository truth; and ORBIT the planetary chapter.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The taxonomy correctly allows one parcel to belong to multiple relational objects and rejects a single universal molecule-to-state assignment. | P3 | Guide index, “One parcel, several objects” | Preserve this as the governing ontology. |
| 2 | The gate equation originally called a reference-dependent `uT` integral simply “heat transport,” without stating how the reference term cancels. | P2 | Guide 04, “From arrow to measurement” | **Fixed:** define reference dependence, volume-closure condition, and omitted native flux terms. |
| 3 | The Nordic relay explicitly separates correlation from parcel transit time and causation. | P3 | Guide 04, OSW example | Preserve the twelve-month limitation beside the result. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Literature examples link directly to current papers or operational source products, and the discovery ledger records the broader search. | P3 | All guides; literature grounding | Keep claim-level sources close to the teaching claim. |
| 2 | Conceptual diagrams and quantitative OSW examples were not governed by an explicit collection-wide evidence vocabulary. | P2 | Guide index | **Fixed:** add Concept, Reference geography, Detected state, Measured flux, and Hypothesis labels. |
| 3 | OSW numerical examples generally link to a figure, and Guide 04 also links its machine-readable receipt; some older plates do not yet have chapter-specific receipts. | P3 | Guides 01, 02, and 04 | Add receipt links when dedicated receipts exist; do not invent provenance files. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The diagrams distinguish property space, geographic space, snapshot flow, trajectories, gates, and planetary systems instead of forcing all objects onto one flat map. | P3 | Guides 01, 03, 04, and 07 | Preserve the coordinate-system distinctions. |
| 2 | Unqualified diagrams could be mistaken for detected sections or mapped boundaries. | P2 | Collection-wide diagrams | **Fixed:** the reading contract now identifies every guide diagram as an explanatory schematic. |
| 3 | The collection repeatedly states that boundaries can be illustrative, thresholded, dynamic, or material and that these meanings differ. | P3 | Guides 02, 03, and 06 | Carry these boundary classes into future interactive legends. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every chapter leads with a short contrast between easily confused objects and follows with examples and common mistakes. | P3 | All numbered guides | Retain this repeated learning rhythm. |
| 2 | Temperature, heat content, transport, transformation, and event anomaly remain separate concepts throughout. | P3 | Guides 01, 04, 05, and 06 | Cross-link the distinctions whenever new quantitative guides are added. |
| 3 | “OSW did not discover these object classes” prevents the integration contribution from becoming a priority claim. | P3 | Guide index, “Research position” | Keep the contribution framed as synthesis and visual grammar until a systematic product review supports more. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Meaning is repeated in prose and tables rather than encoded only in the ASCII line art. | P3 | All guides | Continue treating prose as the authoritative alternative. |
| 2 | The collection lacked an explicit statement that readers need not perceive diagram alignment or symbols to recover the claim. | P2 | Guide index | **Fixed:** add a collection-wide canonical-text-alternative contract. |
| 3 | Descriptive link labels identify the destination or action instead of relying on bare URLs. | P3 | Guide navigation | Retain descriptive labels and test their targets. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | An offline test verifies all seven chapters, diagrams, common-mistake sections, and local Markdown targets. | P3 | `analysis/test_guides.py` | Keep this in the default analysis suite. |
| 2 | The first test revision did not protect the new evidence vocabulary, gate caveat, or planetary falsifier. | P2 | `analysis/test_guides.py` | **Fixed:** add explicit regression assertions for all three amendments. |
| 3 | The complete offline suite passes after integration with the pre-existing Atlas contracts. | P3 | Full analysis suite | Use the same command as the merge gate. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Root navigation, project history, source register, literature signal, and guide tests expose the new work as one coherent increment. | P3 | Repository entry points | Preserve these routes together in any later commit. |
| 2 | The artifacts are uncommitted, so the review cannot truthfully cite a guide-containing source commit. | P3 | Review metadata | Record both current HEAD and working-tree scope now; replace with the eventual commit only after committing. |
| 3 | The guide index accurately describes the contribution as working integration rather than a released scientific standard. | P3 | Guide index, “Research position” | Do not call the taxonomy canonical or externally peer-reviewed. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The planetary guide compares explicit mechanisms and lists forcing, compressibility, depth, boundaries, and observation as non-equivalences. | P3 | Guide 07, correspondence and limits | Keep the transfer limit adjacent to the analogy. |
| 2 | The comparison protocol requested falsification but supplied no concrete falsifiable example. | P2 | Guide 07, comparison protocol | **Fixed:** add a Rhines-scale jet-spacing hypothesis and specific failure outcome. |
| 3 | The guide rejects cloud colour as a direct temperature or full-depth heat-transport proxy. | P3 | Guide 07, object correspondence | Preserve this caveat in every future planetary visual. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues found: 6 (6 resolved)  |  P3 notes: 18
Residual P1: 0  |  Residual P2: 0

Verdict: APPROVED
Top finding: the guide system needed a shared evidence contract separating
conceptual diagrams, detected states, measured fluxes, and hypotheses.
Cross-role consensus: CURRENT, SOUNDER, CHART, BEACON, and HARBOR all require
object labels to carry their definition, evidentiary class, scale, and limits.
```

This is a native repository review, not external scientific peer review and not
a release decision.

## Amendments completed

1. Added the collection-wide evidence vocabulary and canonical text-alternative
   contract to `guides/README.md`.
2. Qualified the heat-transport expression, reference dependence, volume
   closure, and omitted native terms in Guide 04.
3. Added a concrete, rejectable Rhines-scale comparison to Guide 07 and protected
   all three changes with offline guide-contract tests.
