---
skill: roles-check
topic: thor-ursa-dated-event-taxonomy
date: 2026-09-30
depth: quick
roles_used: 6
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: Thor and Ursa dated event taxonomy

Artifact: `research/named-loop-eddy-published-observations.json`, `research/ursa-2021-noaa-identity-candidate-audit.json`, the source-scoped release observations, source-use review, and screened atlas. Selected CURRENT, SOUNDER, CHART, HARBOR, KEEL, and LOGBOOK from `.roles/`.

| Role | Finding | Severity | Recommendation |
| --- | --- | --- | --- |
| CURRENT | Thor's 27 January separation is supported by SST and drifters in Thoppil et al.; the earlier Johnson Exley et al. paper also describes later reattachment and final separation. | P2 | Say “confirmed separated by date,” not “final detachment.” |
| CURRENT | Ursa has a source-reported brief detachment and later final detachment; neither date proves a continuous track or whole-eddy state footprint. | P2 | Keep stage labels and temporal limits explicit. |
| SOUNDER | The 2025 NOAA-hosted PDF has a pinned SHA-256, and a new Crossref receipt supplies DOI metadata. | P2 | Preserve both source references and the precise section/figure locators. |
| SOUNDER | The Frontiers Figure 2/3 image hashes identify the audited source bytes, but no numeric named-ring polygon was published in those panels. | P2 | Keep the figure suitability decision separate from event date evidence. |
| CHART | The eastern Gulf panels are cropped around the instrument array; bold lines depict Loop Current position and often cross the frame. | P2 | Reject full Thor/Ursa footprint extraction from these figures. |
| CHART | Five NOAA anticyclones pass the broad 8 March candidate window and four pass on 26 April, with different state joins. | P2 | Leave the named Ursa state relation unresolved; retain NOAA local IDs as independent detections. |
| HARBOR | Exact event dates and plain-language stages are available in the screened object detail. | P2 | Keep dates and stage definitions readable without a figure. |
| HARBOR | Human accessibility review of the full screened atlas remains open. | P3 | Complete a human keyboard and assistive-technology pass before publication. |
| KEEL | Incremental Crossref refresh preserves prior pinned receipts and fetches only newly used DOIs. | P2 | Keep the source queue and receipt set equal in the validator. |
| KEEL | Four new observation claims changed package and preview counts. | P2 | Verify package, screening closure, site, and browser deep links after rebuild. |
| LOGBOOK | The new factual use is attributed to a CC BY 4.0 article; the original figures are not packaged. | P2 | Keep notice, source-use review, and metadata override aligned. |
| LOGBOOK | Seventeen used external sources still have rights reviews pending and individual scientific claim review is incomplete. | P1 | Keep the public release gate closed. |

Roles reviewed: 6. P1: 1; P2: 10; P3: 1. Verdict: **NEEDS-WORK for public release; the four source-scoped event observations are suitable for internal review.** CURRENT and CHART agree that dated event stages do not establish state footprints.

Amendments: added four event-stage definitions and claim limits, recorded Frontiers figure suitability with exact image hashes, retained NOAA PDF and Crossref provenance, generated two independent NOAA contour-state snapshots with a nine-detection identity audit, updated the screened atlas, and checked the new observation rows. Remaining: obtain a dated full-ring boundary or source altimetry for Thor/Ursa state intersection, scientific review of event interpretation, human accessibility review, rights reconciliation, and owner publication decision.
