---
skill: roles-check
topic: norwegian-front-source-alignment
date: 2026-10-13
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
p3_count: 21
verdict: APPROVED-WITH-CONDITIONS
---

# Norwegian front source-alignment review

Internal review of a source QA artifact, not width or identity admission.
ORBIT does not apply; no delegation or independent scientific approval.

| Role | # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- | --- |
| CURRENT | 1 | DAC is not velocity at a fixed depth | P3 | layer | Depth-average label retained; no fixed-depth width inferred. |
| CURRENT | 2 | Vehicle motion might be read as current speed | P3 | kinematics | Displacement-rate diagnostic named as glider position motion, not current velocity. |
| CURRENT | 3 | Source tracks could be read as a current axis | P3 | geography | Sampling positions only; dimensions, footprint and association remain unresolved. |
| SOUNDER | 1 | Pre-correction originals might certify corrected results | P3 | provenance | Version 1 / February 2019 creation retained; corrected-paper reproduction false. |
| SOUNDER | 2 | DAC_U descriptions disagree | P3 | variables | Both attributes retained; direction validation open, plotted magnitude invariant under component exchange. |
| SOUNDER | 3 | Timestamp display could lose original precision | P3 | time | Original numeric epoch seconds retained beside derived UTC strings. |
| CHART | 1 | Longitude/latitude axes might distort distance | P3 | map | EPSG:3413 projected coordinates in km and equal aspect. |
| CHART | 2 | Missing vectors might become zero speed | P3 | missingness | Four missing pairs retained, excluded from magnitude plot; complete counts reported. |
| CHART | 3 | Post-July data could support the paper's seasonal claims | P3 | extent | Paper endpoint marked on both time plots; all-mission source coverage explicit. |
| BEACON | 1 | Small offsets could imply true positioning accuracy | P3 | conclusion | Internal agreement only; no independent georeferencing truth. |
| BEACON | 2 | New file could imply a filled width gap | P3 | status | Source preflight only; all current dimensions and gap counts unchanged. |
| BEACON | 3 | Old 60 km headline could replace corrected 38 km | P3 | edition | Correction documented; neither headline copied into width inventory. |
| HARBOR | 1 | Colors alone could identify missions | P3 | figure | Named legend and full source JSON data alternative. |
| HARBOR | 2 | Dense figure could hide explanatory text | P3 | layout | Caption/source and July endpoint labels visually inspected. |
| HARBOR | 3 | SVG could lack accessible description | P3 | semantics | Role, title, description and exact JSON data alternative supplied. |
| KEEL | 1 | Unknown source versions could regenerate different numbers | P3 | source | Exact SHA256 source pins reject alternative originals. |
| KEEL | 2 | Audit could only compare itself | P3 | verification | Independent bisect interpolation/WGS84 check, source reconstruction and record/mask tests. |
| KEEL | 3 | Earlier green suite might imply current full coverage | P3 | gates | Four focused tests and unchanged engine/core files reported; full-suite result belongs to a130c3e. |
| LOGBOOK | 1 | Local cache could be mistaken for a distributed fixture | P3 | reproduction | Explicit download URLs, SHA pins and source-directory command; originals remain local. |
| LOGBOOK | 2 | QA could imply live atlas integration | P3 | delivery | Standalone research/figure artifact; UI wiring remains pending. |
| LOGBOOK | 3 | Another gap could create another PR | P3 | Git | Same continuing branch and PR83; no separate PR or merge. |

Seven roles; no unresolved P1/P2 issues for standalone source QA publication,
21 advisory findings. Conditional approval does not admit width measurements,
corrected-paper reproduction, canonical names or integration into atlas queries.
Cross-role CURRENT/SOUNDER/BEACON condition: retain the distinction between
internal coordinate agreement and independent scientific validation.

Amendments applied: preserve original numeric epochs; use direction-independent
magnitudes with the metadata conflict exposed; mark the source-paper date cutoff.
Direction corroboration and corrected-method width extraction remain future work.
