---
skill: roles-check
topic: necc-paired-vector-source
date: 2026-10-18
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---
# NECC paired-vector evidence: source and figures

Direct use of seven installed role lenses, not independent external review. ORBIT omitted because no astronomical mechanism is involved. This review covers the source/analysis package; shared Rust/query/card integration remains required.

| Role | Finding | Severity | Resolution |
|---|---|---|---|
| CURRENT | Eastward-component extent is not automatically flow-normal width. | P2 | Added paired v and peak direction; no cosine correction or physical width admission. |
| CURRENT | Selecting an eastward peak does not verify a named current. | P2 | Current association remains false; raw regional cells retain context-only membership. |
| CURRENT | Neighbor agreement can masquerade as independent validation. | P2 | Three native columns explicitly remain one product and year. |
| SOUNDER | New source edition could invalidate an old comparison. | P2 | Metadata bytes match exactly; all 2,664 target u values/masks match bitwise after float64 decoding. |
| SOUNDER | A declaration after viewing would overstate blinding. | P2 | Prior target-u exposure disclosed; declaration commit precedes new v/neighbor acquisition, without external preregistration claim. |
| SOUNDER | Nominal depth and actual cadence need precise scope. | P2 | Nominal 15 m product context; actual Jan1-Dec26 timestamps, four six-day gaps and equal-sample means retained. |
| CHART | Component sign must be visually interpretable. | P2 | Common zero-centered velocity palettes within each component, units and signed direction from east. |
| CHART | Monthly peak markers can imply an axis. | P2 | Marker role states selected component peaks, not a current axis or physical edges. |
| CHART | Legends/captions can collide with plot labels. | P3 | Rendered both figures, corrected margins/legend placement and inspected final images. |
| BEACON | Attention guides could sound like validated scientific limits. | P2 | 15 degrees and two native cells are OSW flags, not admission or error thresholds. |
| BEACON | A full sampled year could imply complete daily coverage. | P2 | All 72 archive timestamps retained; no daily interpolation or climatology claim. |
| BEACON | Additional numbers must not turn unresolved widths green. | P2 | New width, axis, annual range, rank and physical geometry remain unadmitted. |
| HARBOR | New fields need numeric alternatives. | P2 | Raw flat source inventory and monthly profile tables retained; shared source UI integration required. |
| HARBOR | Color alone cannot distinguish native columns. | P2 | Direction/span plots combine distinct markers, labels and line colors. |
| HARBOR | Small card plots need inspectable versions. | P2 | Full SVG/PNG artifacts plus descriptive SVG metadata; source/table/card links remain an integration condition. |
| KEEL | A missing v sample must not preserve a falsely complete width. | P2 | Both monthly components become unresolved; test proves boundary search stops at the missing pair. |
| KEEL | Reconstructing old target values is a critical compatibility check. | P2 | All twelve central profiles and spans reproduce; all original source inputs pinned. |
| KEEL | New source tests must run offline. | P2 | Acquisition explicit only; frozen response reconstruction and five tests/five subtests pass offline. |
| LOGBOOK | Source package readiness is not UI completeness. | P2 | Results list Rust/index/card/seasons/query and combined-gate work as required, not complete. |
| LOGBOOK | Source licensing and production code must remain auditable. | P2 | Provider free-use/redistribution statement retained in exact metadata; original collector and validator hashes preserved. |
| LOGBOOK | User rejected PRs for individual gaps. | P2 | All source and integration commits stay on the existing workstream/PR83. |

21 findings: 0 P1, 20 P2, 1 P3. Source amendments above are implemented. Verdict conditional on shared source/query/presentation integration and a passing clean combined gate. The earlier eb16678 gate does not establish a passing result for this later package.

## Amendments
1. Preserve paired support, source identity and actual temporal sampling before measuring direction or boundaries.
2. Keep direction/neighbor sensitivity separate from physical widths, errors, independent validation and current membership.
3. Provide accessible figures and full numeric evidence through the existing shared UI, with unchanged previous data and tests.
