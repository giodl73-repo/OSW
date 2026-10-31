---
skill: roles-check
topic: southern-east-madagascar-catalogue
date: 2026-10-21
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Southern East Madagascar catalogue review

Baseline b7272570901b2e0b9c8eb7dc31eb63f48b4a5a5d plus this batch.
Artifact: proposed identity and source-reported dimensions, original SVG and
source-query navigation. All seven Earth atlas lenses apply. ORBIT has no
planetary claim to assess. Internal functional review, not external peer review.

| Role / reason | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT / object identity | Southward current is distinct from northern branch and undercurrent. | P2 resolved | Qualified proposal identity and explicit exclusions; do not alias to Agulhas. |
| CURRENT | Contextual extent is not a cruise-derived axis length. | P2 resolved |650km record cites introduction paragraph2 and earlier literature; observation period and coordinates null. |
| CURRENT | Survey width does not define physical annual extrema. | P2 resolved |120km record retains April2001 and near-surface scope; no annual range or playback. |
| SOUNDER / provenance | Original PDF unavailable in this pass. | P3 open | Publisher full HTML inspected; PDF/epdf403 recorded, checksum null. Acquire and visually review before canonical admission. |
| SOUNDER | Institutional abstract is a duplicate study, not independent corroboration. | P2 resolved | Second source explicitly labeled same study; no independent count. |
| SOUNDER | Upper100m mean velocity context is not a separately verified width layer. | P2 resolved | Both context and false layer-verification flag stored; fixed width layer remains null. |
| CHART / interpretation | Combining reported length and width could imply a footprint. | P2 resolved | Independent textual callouts, no rectangle scaled by dimensions; caption prohibits area inference. |
| CHART | No supported geographic route was recovered. | P3 | No route, polygon or state join added; proposal card reached directly by fragment. |
| CHART | Figure must stand alone with scope and source. | P3 | SVG includes survey date, contextual length label, source DOI and original-PDF limit. |
| BEACON / public claim | Proposed record must not look like canonical measurement admission. | P2 resolved | Card and figure label proposal; canonical scalar and rank fields null/false. |
| BEACON | A reader needs different time supports beside the numbers. | P3 | Length details say no assigned observation period; width details say2001-04. |
| BEACON | Missing methods must be stated rather than inferred from round numbers. | P3 | Source support and details retain unspecified cutoff, uncertainty and edge coordinates. |
| HARBOR / equivalent access | Figure requires accessible equivalent details. | P3 | SVG title/description, image alt, caption and two semantic details records. |
| HARBOR | Source query must work without a pointer. | P3 | Browser gate focuses link and activates Enter; exact returned row checked. |
| HARBOR | Diagram and card must reflow at320px. | P3 | Responsive image and browser reflow gate; retain full-size SVG access through image source. |
| KEEL / source contracts | Rehashed dimension edits must not become accepted facts. | P2 resolved | Rust compares proposal to compiled source; negative tests alter value, scope and date. |
| KEEL | Coherent removal from a full bundle must fail. | P2 resolved | Full-bundle scope marker requires exactly one matching proposal; erasure test. |
| KEEL | Existing frozen scope receipts refer to the prior proposal file. | P2 resolved | Renew only proposal checksum and derived generator receipts; preservation gate checks membership/physical exclusions unchanged. |
| LOGBOOK / inventory truth | Adding one proposal does not increase canonical100. | P3 |29 proposed additions,100 canonical stations; dashboard canonical rows preserved. |
| LOGBOOK | Older28 proposals must retain all fields and values. | P3 | Append-only source edit; baseline semantic comparison required before publication. |
| LOGBOOK | Current scope and CI status remain incomplete. | P3 | Same PR83; original-source/canonical gates open; prior-head scientific CI success is not a new-head full-suite claim. |

Roles reviewed:7. Unresolved P1:0; unresolved P2:0. P3 notes:11,
including the open original-source acquisition gate. Verdict:
APPROVED-WITH-CONDITIONS for a proposed catalogue/evidence addition.
Publication requires native/WASM build, browser exact-source/keyboard/reflow
gate, baseline preservation and staged-file checksum checks. Canonical admission
remains open; this verdict does not approve a canonical width or ranked length.

Top finding: measurement identity, geographic support and time support must
remain separate. CURRENT, SOUNDER, CHART and BEACON agree.

Amendments applied: qualify southern branch identity; retain separate source
dimension records and null annual/edge fields; add exact source navigation and
checks against mutation, rank promotion and full-bundle erasure.
