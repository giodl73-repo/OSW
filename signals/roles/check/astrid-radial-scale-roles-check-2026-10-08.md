---
skill: roles-check
topic: astrid-radial-scale
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Astrid diagnostic radius review

Internal review against base 90e3f24. Seven project roles; no planetary
comparison, so ORBIT excluded. This is not independent scientific review.

| Role | Finding | Severity | Disposition |
|---|---|---|---|
| CURRENT | 120 km denotes maximum-speed radius, not outer extent. | P2 | Metric and definition recorded alongside legacy value. |
| CURRENT | 140 km is a distinct model integration limit. | P2 | Separate record, no combined interval. |
| CURRENT | Two-layer approximation does not capture all observed deep flow. | P2 | Baroclinic/model assumptions retained in each layer field. |
| SOUNDER | Numerical metadata needs original-byte provenance. | P2 | PDF hash, size, acquisition and locators validated. |
| SOUNDER | Original distribution rights are not established. | P2 | Original ignored; explicit checksum-pinned hydration only. |
| SOUNDER | Uncertainty and exact sampling support are unresolved. | P2 | Nulls retained, no numerical allowances invented. |
| CHART | Circular model symmetry could suggest an occupied geographic disk. | P2 | One-dimensional point chart; map stays a locator. |
| CHART | Radius definitions could appear as seasonal bounds. | P2 | Separate labeled rows; no connecting span or seasonal playback. |
| CHART | Source boundary coordinates would improve atlas detail. | P3 | Recover independently before footprint geometry. |
| BEACON | Legacy unqualified radius prose is ambiguous. | P2 | Replaced in inventory by defined scale chart and caption. |
| BEACON | Readers need the method next to the numbers. | P2 | Model/isotherm context, uncertainty and limits visible. |
| BEACON | Readers need a direct route to full records. | P2 | Existing source-query UI link, both records and locators returned. |
| HARBOR | Detached table row made a responsive chart unreadably small. | P2 | Explicit table-cell sizing; existing table scroll preserves reflow. |
| HARBOR | Color cannot carry scientific distinctions alone. | P2 | Labels, description and textual values supplied. |
| HARBOR | Preserve keyboard and touch use of table navigation. | P3 | Semantic query link; retained existing table navigation. |
| KEEL | Coherent receipt rewrites could promote radii to footprints. | P2 | Compiled exact audit guard and negative loader checks. |
| KEEL | Minimal synthetic atlas fixtures need scoped requirements. | P2 | Astrid audit required when Astrid exists; production omission rejected. |
| KEEL | Evidence changes should reach dashboard update fingerprints. | P2 | Audit added to measurement/source sections and object payload. |
| LOGBOOK | PR30's status changed during work. | P2 | Merge timestamp verified; newer drafts remain separate. |
| LOGBOOK | New records do not close named-eddy footprint coverage. | P2 | No footprint count inflation; unresolved geometry explicit. |
| LOGBOOK | Independent scientific admission remains needed. | P3 | Conditional status retained in source audit and plan. |

## Synthesis and amendments

21 findings: zero P1, 18 P2 addressed, three P3 next-work notes.
APPROVED-WITH-CONDITIONS: independent scientific admission and publication
of the newer batches remain separate gates.

1. Bind each radius to its original method and prevent diameter, area,
   footprint or seasonal inference.
2. Preserve copyright restrictions while making source-byte verification
   reproducible through explicit fixture acquisition.
3. Render the definitions on both eddy paths, correct inventory text sizing,
   and check source-query navigation and coherent rewrite rejection.
