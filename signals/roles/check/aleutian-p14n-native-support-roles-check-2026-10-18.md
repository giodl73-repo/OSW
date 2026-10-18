---
skill: roles-check
topic: aleutian-p14n-native-support
date: 2026-10-18
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---
# Native vector and ship-motion support review

Internal application of CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL and
LOGBOOK; not independent scientific peer review. ORBIT omitted: no planetary
comparison is introduced. Approval concerns support data, not physical width.

| Role | Finding | Severity | Resolution / condition |
|---|---|---|---|
| CURRENT | Short ocean vectors already contain ship-motion correction. | P2 | Compare to long relative-water plus absolute-ship vectors; no second correction. |
| CURRENT | Motion eligibility is not independently verified ship activity. | P2 | Fixed1/2/3m/s scenarios all retained; nominal CTD-event agreement is context only. |
| CURRENT | Native sampling density does not establish accurate width or a snapshot. | P2 | No new temporal ocean averaging, width, edge or annual range; next operator must address uncertainty and temporal/spatial support. |
| SOUNDER | CODAS bit flags cannot inherit CTD WOCE meanings. | P2 | Source bits1/2/4 and flag counts retained; primary joint support requires flag0. |
| SOUNDER | Ensemble-end time and nominal depth differ from instantaneous/mapped support. | P2 | Original decimal days, actual300s duration, nominal start/end and time-dependent depth representation explicit. |
| SOUNDER | Historical header/acquisition flags must not be silently rewritten. | P2 | Earlier operators remain header-only; separate field report records arrays now inspected. |
| CHART | Station occupations can masquerade as spatial crossings. | P2 | Actual time/latitude and ship speed beside both ocean components; recorded BE–EN intervals shown. |
| CHART | A native time series can imply newly resolved edges. | P2 | Source processing/no further OSW averaging and GPS-uncertainty context adjacent; no map ribbon or edge. |
| CHART | Missing support and source time gaps must survive plots and grouping. | P2 | Unsupported means null; source-order scatter/run breaks. Ship-speed85minute gap corrected with explicit7.5minute line break; old hourly gap break retained. |
| BEACON | Whole-cruise11455records could be mistaken for the local section. | P2 | Regional1585profiles distinct from full-product metadata. |
| BEACON | A frame residual can look like measurement precision. | P2 |1e-5m/s is a representation-comparison tolerance, not instrument accuracy or width error. |
| BEACON | More profiles do not close physical-width coverage. | P2 |155width rows remain unchanged; physical width unknown and next evidence explicit. |
| HARBOR | Motion categories and native/hourly distinction need redundant encodings. | P2 | Final figure uses triangles/dots/crosses and line styles, text labels and numeric source alternatives; corrected PNG visually reviewed. |
| HARBOR | Native data need a direct inspection path. | P2 | Named figure selector and source queries for profiles, runs, events, frames and custody. |
| HARBOR | More evidence must not break small-screen/keyboard access. | P2 | Require actual all-owner browser,320px,reduced-motion, source-query and inspector gate. |
| KEEL | Missing CLI can invalidate a clean-checkout gate before data assertions. | P2 | Archive aborted attempt; locked native prerequisite built and60Rust tests pass before exact baseline attempt2. |
| KEEL | Unsupported research can be promoted through an orphan width row. | P2 | Native support-only path guard checks width presence even with owner/registry erased; isolated Rust rejection test added. |
| KEEL | Masks, duration units, run gaps and interval touching can alter scientific support. | P2 | Nine source tests/25subtests cover units, flag meanings, missing support, gap limits, multiplicity, touching and11input pins. |
| LOGBOOK | New source work belongs in the user's continuing PR. | P2 | Same branch/draft PR83; no new PR or merge. |
| LOGBOOK | Parent full/CI state cannot certify this successor. | P2 | Baseline9092076passes1703tests/1127subtests; attempt history, final focused scopes and hosted source failure remain separate; successor combined gate required. |
| LOGBOOK | Original data and derived records need public provenance without automatic bulk downloads. | P2 |59.5MB originals with source URLs/hashes; metadata and derived queries; actual browser must show no automatic NetCDF/PDF/ZIP/MAT fetch. |

21 findings, no unresolved P1 finding. Conditional on final redundant marker
encoding/visual check, source and preservation gates, actual native/WASM UI
verification, committed provenance/root delivery, and a clean successor full
suite. Passing software checks does not establish physical current boundaries.

## Freshness regression amendment

The plot-only provenance update exposed a main tile-hash omission. Research
source content now participates in the main fingerprint for allfive research
owners. Four other owners change only their main checksum during this repair;
their scientific content, source-section hashes, capabilities and observation
dates remain unchanged. A new counterfactual test passes: changing only one
native support-document hash changes Aleutian alone, including its source
section, and preserves every other entry. This implements the user's requested
data-update highlight behavior. Actual dashboard browser acceptance remains
the final rendering gate for the repair.

## Final focused acceptance

The final broad dashboard browser and diagnostic-navigation gates pass,
including real refresh highlights and retention after a failed update. The
two earlier closures are traced to DevTools'100MiB message cap; complete
fixtures are now transferred by HTTP with no assertions removed. Final native
views across card/seasons/query, two changed indexed documents and three
figure-provenance native/WASM rebindings pass. Explicit supported1993 dates
populate the time ledger; the updated provenance-only regression passes while
preserving all other entries and dates. Earlier full54case browser results,
these focused corrections and the successor combined gate remain separately
reported. No width, annual range or physical geometry admission follows.
