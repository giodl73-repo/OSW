---
skill: roles-check
topic: aleutian-p14n-hydrography-join
date: 2026-10-18
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---
# P14N hydrography correspondence review

Direct application of installed CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL and LOGBOOK lenses on parent4267da6690a5f9d00fadd0bcf15c56a2859c4c58. Internal functional review, not independent scientific peer review. ORBIT is omitted because no planetary comparison is introduced.

| Role | Finding and evidence | Severity | Resolution / condition |
|---|---|---|---|
| CURRENT | A CTD bottom event is not a velocity observation at the same depth/time. | P2 | Actual offsets and BO semantics retained; simultaneity and independent-width validation remain false. |
| CURRENT | Temperature, salinity, pressure and depth have different physical meanings. | P2 | ITS-90 in-situ temperature, PSS-78 practical salinity and original dbar pressure are explicit; named GSW conversion tested. |
| CURRENT | Nearby water properties do not automatically establish a named branch or its edges. | P2 | Association, physical width, annual range and mapped-edge admission remain false/null. |
| SOUNDER | Edited code7 differs from missing or questionable code3. | P2 | Raw values and all flags retained; primary joint QC2 support distinguished without reclassifying other codes. |
| SOUNDER | An archive conversion date cannot resolve the historical temperature notice. | P2 | Correction remains unresolved and is not reapplied. |
| SOUNDER | Expiring redirect queries are unsuitable public provenance locations. | P2 | Original receipt retained locally; explicit public normalization preserves all source-file hashes and stable request URLs. |
| CHART | Interpolation can invent a continuous hydrographic section or boundary. | P2 | Actual cast cells plotted without interpolation; rejected primary-support cells marked by their QC distinction. |
| CHART | Pairing limits can resemble uncertainty bounds. | P2 | Three-hour/15km guides labeled selection rules; actual84offsets shown, with no error interval claim. |
| CHART | Earlier station loops and temporal gap must survive the joined view. | P2 | Original velocity section retained exactly; acquisition-order curves and long-gap break preserved. |
| BEACON | More paired observations could be read as a newly measured width. | P2 | Card keeps physical width unknown;155-record width inventory unchanged. |
| BEACON | Archive198profiles could be mistaken for198stations in the local section. | P2 | Local17casts and preserved repeat-cast identities explicit; no deduplication by latitude or station alone. |
| BEACON | A unique observed match in this source should not imply a nearest-only algorithm. | P2 | All qualifying pairs retained; synthetic ambiguous-cast test proves multiplicity is preserved. |
| HARBOR | Color cannot be the only route to property/QC meaning. | P2 | Explicit units, QC text, support counts, source tables and raw numeric inspection accompany the figure. |
| HARBOR | Readers need a clear path between original velocity and hydrography. | P2 | Existing figure selector gains a named CTD view; separate source queries for casts, pairs and original profiles. |
| HARBOR | Additional figure/links must work on keyboard and narrow screens. | P2 | Final actual browser gate must pass320px/reduced-motion, selector, source and inspector checks. |
| KEEL | Coherently rehashed scientific changes must still fail. | P2 | Joined study compiled into Rust; ten added native/WASM cases target property, QC, conversion, timing, matching and source binding. |
| KEEL | The joined record can accidentally replace or alter prior vectors. | P2 | Exact nested equality with original132profile record; old inventory/seasonal bytes,42other diagnostics andfour other scenes preserved. |
| KEEL | Field units, masks, matching boundaries and source inputs need offline tests. | P2 | Ten source/registry tests, all60Rust tests and90engine/143research working pins pass; committed pins remain a publication condition. |
| LOGBOOK | The predecessor full suite cannot certify this new join. | P2 | Its running status is separate; new clean committed-head gate required. |
| LOGBOOK | Existing remote source-host failures are not a scientific pass or a missing local original. | P2 | Record latest actual CI outcomes independently; no source pin or TLS policy weakened. |
| LOGBOOK | Source work must continue within the user's existing PR. | P2 | Same branch and draft PR#83; no additional PR or main merge. |

21 findings; zero unresolved P1 findings. APPROVED-WITH-CONDITIONS: complete the actual browser gate, committed-pin and root-delivery checks, then execute and report the clean combined suite. Source custody, matched metadata and passing software checks do not establish physical current width or annual variability.

## Amendments

1. Preserve BO semantics, source quality distinctions and the unresolved correction notice beside the new evidence.
2. Retain every qualifying pair and the complete original velocity section; show raw measured cells and actual offsets without invented geometry.
3. Bind the joined data through the shared Rust record/source store, retain old corruption cases, and distinguish predecessor, focused and successor gates.
